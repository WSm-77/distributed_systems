package client;

import java.io.ObjectInputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.net.Socket;
import java.util.Scanner;
import java.util.concurrent.Executor;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ThreadPoolExecutor;

import messages.Message;
import messages.MessagesType;

public class Client {
    private static final int PORT = 12345;
    private final Socket clientSocket;
    private final ObjectOutputStream out;
    private final ObjectInputStream in;
    private final String name;
    private volatile boolean running = true;
    private ExecutorService threadPool = Executors.newFixedThreadPool(2);

    public Client(String ip, int port, String name) throws IOException {
        this.clientSocket = new Socket(ip, port);
        this.out = new ObjectOutputStream(clientSocket.getOutputStream());
        this.in = new ObjectInputStream(clientSocket.getInputStream());
        this.name = name;
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
        this.sendMessage(new Message(MessagesType.MESSAGE, msg));
    }

    public void closeConnection() throws IOException {
        Message unregisterMessage = new Message(MessagesType.UNREGISTER_CLIENT, this.name);
        this.sendMessage(unregisterMessage);
        in.close();
        out.close();
        clientSocket.close();
    }

    public void setUpConnection() throws IOException {
        Message registerMessage = new Message(MessagesType.REGISTER_CLIENT, this.name);
        this.sendMessage(registerMessage);
        Message response = this.receiveMessage();

        System.out.println("Response from server: " + response);
    }

    private void handleReceivingMessages() {
        while (this.running) {
            try {
                Message message = this.receiveMessage();
                System.out.println(String.format("[SERVER]: %s", message.getContent()));
            } catch (IOException e) {
                if (this.running) {
                    System.out.println("Error receiving message: " + e.getMessage());
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
                }

                this.sendToChat(input);
            }
        } catch (IOException e) {
            System.out.println("Error sending message: " + e.getMessage());
        }
    }

    public void start() throws IOException {
        this.setUpConnection();

        Thread receivingThread = new Thread(this::handleReceivingMessages);
        Thread sendingThread = new Thread(this::handleSendingMessages);

        this.threadPool.execute(sendingThread);
        this.threadPool.execute(receivingThread);
    }

    public void stop() throws IOException {
        this.running = false;
        this.threadPool.shutdownNow();
        this.closeConnection();
    }

    public static void main(String[] args) {
        String name = args.length > 0 ? args[0] : "Client";

        try {
            Client client = new Client("127.0.0.1", Client.PORT, name);
            client.start();
        } catch (IOException e) {
            System.out.println("Error in client: " + e.getMessage());
        }
    }
}
