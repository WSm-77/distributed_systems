package server;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.util.Set;

import client.ClientInfo;

public class UDPChannelHandler implements Runnable {
    private final DatagramSocket datagramSocket;

    public UDPChannelHandler(int port) throws IOException {
        this.datagramSocket = new DatagramSocket(port);
    }

    private void handleUDPChannel() {
        byte[] receiveBuffer = new byte[1024];

        while (true) {
            try {
                DatagramPacket receivePacket = new DatagramPacket(receiveBuffer, receiveBuffer.length);
                datagramSocket.receive(receivePacket);

                String receivedMessage = new String(receiveBuffer, 0, receivePacket.getLength());
                System.out.println("Received UDP message: " + receivedMessage);

                Set<ClientInfo> clientsInfo = ClientHandler.getClientsInfo();
                ClientInfo senderInfo = new ClientInfo(receivePacket.getAddress(), receivePacket.getPort());

                System.out.println("Sender info: " + senderInfo);

                clientsInfo.remove(senderInfo);

                for (ClientInfo clientInfo : clientsInfo) {
                    System.out.println("Forwarding UDP message to: " + clientInfo);


                    byte[] sendBuffer = receivedMessage.getBytes();
                    DatagramPacket sendPacket = new DatagramPacket(sendBuffer, sendBuffer.length, clientInfo.address(),
                        clientInfo.port());
                    datagramSocket.send(sendPacket);
                }

            } catch (IOException e) {
                System.out.println("Error receiving UDP message: " + e.getMessage());
            }
        }
    }

    public void stop() {
        this.datagramSocket.close();
    }

    @Override
    public void run() {
        this.handleUDPChannel();
    }
}
