package client;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;

public class Client {
    private final Socket clientSocket;
    private final PrintWriter out;
    private final BufferedReader in;

    public Client(String ip, int port) throws IOException {
        this.clientSocket = new Socket(ip, port);
        this.out = new PrintWriter(clientSocket.getOutputStream(), true);
        this.in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
    }

    public String sendMessage(String msg) throws IOException {
        out.println(msg);
        String resp = in.readLine();
        return resp;
    }

    public void stopConnection() throws IOException {
        in.close();
        out.close();
        clientSocket.close();
    }

    public static void main(String[] args) {
        try {
            Client client = new Client("127.0.0.1", 12345);
            String response = client.sendMessage("Hello Server");
            System.out.println("Response from server: " + response);
            client.stopConnection();
        } catch (IOException e) {
            System.out.println("Error in client: " + e.getMessage());
        }
    }
}
