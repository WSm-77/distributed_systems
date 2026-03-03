package server;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.InputStreamReader;
import java.net.Socket;
import java.nio.Buffer;
import java.util.ArrayList;
import java.util.List;

import javax.management.RuntimeErrorException;

public class ClientHandler implements Runnable {
    private static final List<Socket> clients = new ArrayList<>();
    private final Socket clientSocket;
    private final PrintWriter out;
    private final BufferedReader in;

    public ClientHandler(Socket clientSocket) {
        this.clientSocket = clientSocket;
        try {
            this.in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
            this.out = new PrintWriter(clientSocket.getOutputStream(), true);
        } catch (IOException e) {
            System.out.println("Error initializing client handler: " + e.getMessage());
            throw new RuntimeException(e);
        }
    }

    private void sendToClient(String messsage) {
        this.out.println(messsage);
    }

    private String receiveFromClient() {
        try {
            String message = this.in.readLine();
            return message;
        } catch (IOException e) {
            System.out.println(String.format("Couldn't receive message: %s", e.getMessage()));
        }

        return "";
    }

    @Override
    public void run() {
        System.out.println("Handling client: " + clientSocket.getRemoteSocketAddress());

        try {
            String message = this.receiveFromClient();
            System.out.println("received message: " + message);

            this.sendToClient("response from Server");
        } catch (Exception e) {
            throw new RuntimeException(e.getMessage());
        }
    }

}
