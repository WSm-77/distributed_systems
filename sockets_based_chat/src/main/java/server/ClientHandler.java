package server;

import java.io.ObjectInputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.net.Socket;
import java.util.Collections;
import java.util.HashSet;
import java.util.Set;
import java.util.Optional;

import messages.Message;

public class ClientHandler implements Runnable {
    private static final Set<ClientHandler> clients = Collections.synchronizedSet(new HashSet<>());
    private final Socket clientSocket;
    private final ObjectOutputStream out;
    private final ObjectInputStream in;
    private Optional<String> clientName = Optional.empty();

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

    private static void addClient(ClientHandler clientHandler) {
        ClientHandler.clients.add(clientHandler);
        System.out.println("Client added to list. Total clients: " + ClientHandler.clients.size());

    }

    private static void removeClient(ClientHandler clientHandler) {
        ClientHandler.clients.remove(clientHandler);
        System.out.println(String.format("Client removed. Total clients: %d", ClientHandler.clients.size()));
    }

    private void setUpConnection(String clientName) {
        System.out.println("Handling client: " + clientSocket.getRemoteSocketAddress());

        this.clientName = Optional.of(clientName);

        System.out.println("Client name: " + this.clientName.get());

        ClientHandler.addClient(this);

        this.sendToClient("Welcome " + clientName + "!");
    }

    private void sendToClient(String message) {
        try {
            Message messageObject = new Message(messages.MessageType.MESSAGE, message);
            this.out.writeObject(messageObject);
            this.out.flush();
        } catch (IOException e) {
            System.out.println(String.format("Could not send message: %s", message));
            System.out.println(String.format("Error while sending message to client: %s", e.getMessage()));
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
        System.out.println(String.format("Closing connection for client: %s", this.getClientName()));

        try {
            this.in.close();
            this.out.close();
            this.clientSocket.close();

            ClientHandler.removeClient(this);

            System.out.println(String.format("Connection closed successfully for client: %s", this.getClientName()));
        } catch (IOException e) {
            System.out.println("Error closing connection: " + e.getMessage());
        }
    }

    private void handleMessage(Message message) {
        if (message == null) {
            System.out.println("Received null message, ignoring.");
            return;
        }

        System.out.println("Received message: " + message);

        switch (message.getType()) {
            case REGISTER_CLIENT -> this.setUpConnection(message.getContent());
            case UNREGISTER_CLIENT -> this.closeConnection();
            case MESSAGE -> this.passMessageToAllClients(message.getContent());
        }
    }

    private void passMessageToAllClients(String content) {
        for (ClientHandler client : ClientHandler.clients) {
            if (!client.equals(this)) {
                client.sendToClient(String.format("[%s]: %s", this.getClientName(), content));
            }
        }
    }

    private String getClientName() {
        return this.clientName.orElse("unknown");
    }

    @Override
    public void run() {
        while (!this.clientSocket.isClosed() && this.clientSocket.isConnected()) {
            Message message = this.receiveFromClient();
            this.handleMessage(message);
        }
    }

    @Override
    public boolean equals(Object other) {
        if (this == other)
            return true;
        if (other == null || getClass() != other.getClass())
            return false;

        ClientHandler that = (ClientHandler)other;

        return clientSocket.equals(that.clientSocket);
    }

    @Override
    public int hashCode() {
        return clientSocket.hashCode();
    }
}
