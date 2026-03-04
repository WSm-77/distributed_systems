package server;

import java.io.IOException;
import java.net.DatagramSocket;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class Server {
    private final ServerSocket serverSocket;
    private final ExecutorService threadPool;

    public Server(int portNumber, int poolSize) throws Exception {
        this.serverSocket = new ServerSocket(portNumber, 50, null);
        this.threadPool = Executors.newFixedThreadPool(poolSize);
    }


    public void start() throws IOException {
        System.out.println(String.format("Starting server on port %d", serverSocket.getLocalPort()));

        while (true) {
            try {
                Socket clientSocket = serverSocket.accept();
                System.out.println("Client connected: " + clientSocket.getRemoteSocketAddress());

                ClientHandler clientHandler = new ClientHandler(clientSocket);
                this.threadPool.execute(clientHandler);
            } catch (Exception e) {
                break;
            }
        }

        this.close();
    }

    private void close() throws IOException {
        this.serverSocket.close();
        this.threadPool.shutdown();
    }

    public static void main(String[] args) {
        try {
            Server server = new Server(12345, 10);
            server.start();
        } catch (Exception e) {
            System.out.println("Error starting server: " + e.getMessage());
        }
    }
}
