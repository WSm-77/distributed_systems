package server;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class Server {
    public static final int PORT = 12345;
    public static final String ADDRESS = "127.0.0.1";
    private final ServerSocket serverSocket;
    private final ExecutorService threadPool;
    private final UDPChannelHandler udpChannelHandler;

    public Server(int portNumber, int poolSize) throws Exception {
        this.serverSocket = new ServerSocket(portNumber, 50, null);
        this.udpChannelHandler = new UDPChannelHandler(portNumber);
        this.threadPool = Executors.newFixedThreadPool(poolSize);
    }

    public void start() throws IOException {
        System.out.println(String.format("Starting server on port %d", serverSocket.getLocalPort()));

        this.threadPool.execute(this.udpChannelHandler);

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
        this.udpChannelHandler.stop();
        this.threadPool.shutdown();
    }

    public static void main(String[] args) {
        try {
            Server server = new Server(Server.PORT, 10);
            server.start();
        } catch (Exception e) {
            System.out.println("Error starting server: " + e.getMessage());
        }
    }
}
