package client;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.ObjectInputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.Socket;
import java.util.Scanner;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import messages.Message;
import messages.MessageType;
import server.Server;

public class Client {
    private static final int PORT = 12345;
    private static final int BUFFER_SIZE = 4096;
    private final Socket clientSocket;
    private final DatagramSocket udpSocket;
    private final ObjectOutputStream out;
    private final ObjectInputStream in;
    private final String name;
    private volatile boolean running = true;
    private final ExecutorService threadPool = Executors.newFixedThreadPool(3);

    public Client(String ip, int port, String name) throws IOException {
        this.clientSocket = new Socket(ip, port);
        this.udpSocket = new DatagramSocket();
        this.out = new ObjectOutputStream(clientSocket.getOutputStream());
        this.in = new ObjectInputStream(clientSocket.getInputStream());
        this.name = name;
    }

    private byte[] toBytes(Message message) throws IOException {
        try (ByteArrayOutputStream bos = new ByteArrayOutputStream();
            ObjectOutputStream oos = new ObjectOutputStream(bos)) {
            oos.writeObject(message);
            oos.flush();
            return bos.toByteArray();
        }
    }

    private Message fromPacket(DatagramPacket packet) throws IOException {
        try (ByteArrayInputStream bis = new ByteArrayInputStream(packet.getData(), 0, packet.getLength());
            ObjectInputStream ois = new ObjectInputStream(bis)) {
            Object obj = ois.readObject();
            if (obj instanceof Message message) {
                return message;
            }
        } catch (ClassNotFoundException e) {
            System.out.println("Error decoding UDP message: " + e.getMessage());
        }

        return null;
    }

    private void sendUDPProtocolMessage(Message message) throws IOException {
        byte[] sendBuffer = this.toBytes(message);
        InetAddress serverAddr = InetAddress.getByName(Server.ADDRESS);
        DatagramPacket sendPacket = new DatagramPacket(sendBuffer, sendBuffer.length, serverAddr, Server.PORT);
        this.udpSocket.send(sendPacket);
    }

    private void sendUDPRegister() throws IOException {
        this.sendUDPProtocolMessage(new Message(MessageType.UDP_REGISTER_CLIENT, this.name));
    }

    private void sendUDPUnregister() throws IOException {
        this.sendUDPProtocolMessage(new Message(MessageType.UDP_UNREGISTER_CLIENT, this.name));
    }

    public void sendMessage(Message msg) throws IOException {
        out.writeObject(msg);
        out.flush();
    }

    public Message receiveMessage() throws IOException {
        try {
            Object obj = in.readObject();
            if (obj instanceof Message) {
                return (Message) obj;
            }
        } catch (ClassNotFoundException e) {
            System.out.println("Error reading object: " + e.getMessage());
        }

        return null;
    }

    public void sendToChat(String msg) throws IOException {
        System.out.println(String.format("[ME]: %s", msg));
        this.sendMessage(new Message(MessageType.MESSAGE, msg));
    }

    private void sendUDPMessage(String udpMessage) throws IOException {
        System.out.println(String.format("[ME]: %s", udpMessage));
        String formatted = String.format("[%s][UDP]: %s", this.name, udpMessage);
        this.sendUDPProtocolMessage(new Message(MessageType.UDP_MESSAGE, formatted));
    }

    public void closeConnection() throws IOException {
        try {
            this.sendUDPUnregister();
        } catch (IOException e) {
            System.out.println("Error sending UDP unregister: " + e.getMessage());
        }

        Message unregisterMessage = new Message(MessageType.UNREGISTER_CLIENT, this.name);
        this.sendMessage(unregisterMessage);

        if (!udpSocket.isClosed()) {
            udpSocket.close();
        }
        if (!in.equals(null)) {
            in.close();
        }
        if (!out.equals(null)) {
            out.close();
        }
        if (!clientSocket.isClosed()) {
            clientSocket.close();
        }
    }

    public void setUpConnection() throws IOException {
        Message registerMessage = new Message(MessageType.REGISTER_CLIENT, this.name);
        this.sendMessage(registerMessage);
        Message response = this.receiveMessage();

        System.out.println("Response from server: " + response);
        this.sendUDPRegister();
    }

    private void handleReceivingMessages() {
        while (this.running) {
            try {
                Message message = this.receiveMessage();
                if (message != null) {
                    System.out.println(message.getContent());
                }
            } catch (IOException e) {
                if (this.running) {
                    System.out.println("Error receiving message: " + e.getMessage());
                }
            }
        }
    }

    private void handleReceivingUDPMessages() {
        while (this.running && !udpSocket.isClosed()) {
            try {
                byte[] receiveBuffer = new byte[BUFFER_SIZE];
                DatagramPacket receivePacket = new DatagramPacket(receiveBuffer, receiveBuffer.length);
                udpSocket.receive(receivePacket);

                Message message = this.fromPacket(receivePacket);
                if (message != null && message.getType() == MessageType.UDP_MESSAGE) {
                    System.out.println(message.getContent());
                }
            } catch (IOException e) {
                if (this.running && !udpSocket.isClosed()) {
                    System.out.println("Error receiving UDP message: " + e.getMessage());
                } else {
                    break;
                }
            }
        }
    }

    private void handleSendingMessages() {
        try (Scanner scanner = new Scanner(System.in)) {
            while (this.running) {
                String input = scanner.nextLine();

                if ("exit".equalsIgnoreCase(input)) {
                    this.stop();
                    break;
                } else if (input.startsWith("U ")) {
                    String udpMessage = input.substring(2);
                    this.sendUDPMessage(udpMessage);
                } else {
                    this.sendToChat(input);
                }
            }
        } catch (IOException e) {
            System.out.println("Error sending message: " + e.getMessage());
        }
    }

    public void start() throws IOException {
        this.setUpConnection();

        Thread receivingThread = new Thread(this::handleReceivingMessages);
        Thread sendingThread = new Thread(this::handleSendingMessages);
        Thread udpReceivingThread = new Thread(this::handleReceivingUDPMessages);

        this.threadPool.execute(sendingThread);
        this.threadPool.execute(receivingThread);
        this.threadPool.execute(udpReceivingThread);
    }

    public void stop() throws IOException {
        this.running = false;
        this.threadPool.shutdownNow();
        this.closeConnection();
    }

    public static void main(String[] args) {
        String name = args.length > 0 ? args[0] : "Derek";

        try {
            Client client = new Client(Server.ADDRESS, Client.PORT, name);
            client.start();
        } catch (IOException e) {
            System.out.println("Error in client: " + e.getMessage());
        }
    }
}
