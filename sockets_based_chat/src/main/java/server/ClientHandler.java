package server;

import java.io.ObjectInputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.net.Socket;
import java.util.ArrayList;
import java.util.List;

import messages.Message;

public class ClientHandler implements Runnable {
    private static final List<Socket> clients = new ArrayList<>();
    private final Socket clientSocket;
    private final ObjectOutputStream out;
    private final ObjectInputStream in;

    public ClientHandler(Socket clientSocket) {
        this.clientSocket = clientSocket;
        try {
            this.in = new ObjectInputStream(clientSocket.getInputStream());
            this.out = new ObjectOutputStream(clientSocket.getOutputStream());
        } catch (IOException e) {
            System.out.println("Error initializing client handler: " + e.getMessage());
            throw new RuntimeException(e);
        }
    }

    private void setupConnection() {
        System.out.println("Handling client: " + clientSocket.getRemoteSocketAddress());

        Message clientName = this.receiveFromClient();

        System.out.println("Client name: " + clientName.getContent());

        clients.add(this.clientSocket);
        System.out.println("Client added to list. Total clients: " + clients.size());
        this.sendToClient("Welcome " + clientName.getContent() + "!");
    }

    private void sendToClient(String message) {
        try {
            Message messageObject = new Message(messages.MessagesType.MESSAGE, message);
            this.out.writeObject(messageObject);
            this.out.flush();
        } catch (IOException e) {
            System.out.println("Error sending message to client: " + e.getMessage());
        }
    }

    private Message receiveFromClient() {
        try {
            Object obj = this.in.readObject();
            if (obj instanceof Message) {
                Message message = (Message) obj;
                return message;
            }
        } catch (IOException | ClassNotFoundException e) {
            System.out.println(String.format("Couldn't receive message: %s", e.getMessage()));
        }

        return null;
    }

    private void closeConnection() {
        try {
            this.in.close();
            this.out.close();
            this.clientSocket.close();
        } catch (IOException e) {
            System.out.println("Error closing connection: " + e.getMessage());
        }
    }

    @Override
    public void run() {
        this.setupConnection();

        try {
            // TODO: implement message broadcasting to all clients
        } catch (Exception e) {
            throw new RuntimeException(e.getMessage());
        } finally {
            this.closeConnection();
        }
    }

}
