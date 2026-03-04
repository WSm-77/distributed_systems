package client;

import java.io.ObjectInputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.net.Socket;

import messages.Message;
import messages.MessagesType;

public class Client {
    private static final int PORT = 12345;
    private final Socket clientSocket;
    private final ObjectOutputStream out;
    private final ObjectInputStream in;
    private final String name;

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

    public static void main(String[] args) {
        String name = args.length > 0 ? args[0] : "Client";

        try {
            Client client = new Client("127.0.0.1", Client.PORT, name);
            client.setUpConnection();

            client.closeConnection();
        } catch (IOException e) {
            System.out.println("Error in client: " + e.getMessage());
        }
    }
}
