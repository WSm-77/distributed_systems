package server;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import client.ClientInfo;
import messages.Message;

public class UDPChannelHandler implements Runnable {
    private static final int BUFFER_SIZE = 4096;

    private final DatagramSocket datagramSocket;
    private final Map<String, ClientInfo> udpClients = new ConcurrentHashMap<>();
    private volatile boolean running = true;

    public UDPChannelHandler(int port) throws IOException {
        this.datagramSocket = new DatagramSocket(port);
    }

    private void addClient(String clientName, ClientInfo senderInfo) {
        udpClients.put(clientName, senderInfo);
        System.out.println("UDP registered: " + clientName + " -> " + senderInfo);
    }

    private void removeClient(String clientName) {
        udpClients.remove(clientName);
        System.out.println("UDP unregistered: " + clientName);
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

    private void passMessageToAllClients(Message message, ClientInfo senderInfo) throws IOException {
        byte[] sendBuffer = this.toBytes(message);

        for (ClientInfo clientInfo : udpClients.values()) {
            boolean isSender = clientInfo.address().equals(senderInfo.address()) && clientInfo.port() == senderInfo.port();
            if (isSender) {
                continue;
            }

            DatagramPacket sendPacket = new DatagramPacket(sendBuffer, sendBuffer.length, clientInfo.address(),
                clientInfo.port());
            datagramSocket.send(sendPacket);
        }
    }

    private void handleMessage(Message message, ClientInfo senderInfo) throws IOException {
        switch (message.getType()) {
            case UDP_REGISTER_CLIENT -> this.addClient(message.getContent(), senderInfo);
            case UDP_UNREGISTER_CLIENT -> this.removeClient(message.getContent());
            case UDP_MESSAGE -> this.passMessageToAllClients(message, senderInfo);
            default -> System.out.println("Unhandled UDP message of type: " + message.getType());
        }
    }

    private void handleUDPChannel() {
        while (running && !datagramSocket.isClosed()) {
            try {
                byte[] receiveBuffer = new byte[BUFFER_SIZE];
                DatagramPacket receivePacket = new DatagramPacket(receiveBuffer, receiveBuffer.length);
                datagramSocket.receive(receivePacket);

                ClientInfo senderInfo = new ClientInfo(receivePacket.getAddress(), receivePacket.getPort());
                Message message = this.fromPacket(receivePacket);

                if (message == null) {
                    continue;
                }

                this.handleMessage(message, senderInfo);

            } catch (IOException e) {
                if (running && !datagramSocket.isClosed()) {
                    System.out.println("Error receiving UDP message: " + e.getMessage());
                } else {
                    break;
                }
            }
        }
    }

    public void stop() {
        running = false;
        this.datagramSocket.close();
    }

    @Override
    public void run() {
        this.handleUDPChannel();
    }
}
