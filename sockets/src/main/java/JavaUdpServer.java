import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.util.Arrays;

public class JavaUdpServer {

    public static void main(String args[])
    {
        System.out.println("JAVA UDP SERVER");
        DatagramSocket socket = null;
        int portNumber = 9008;

        try{
            socket = new DatagramSocket(portNumber);
            byte[] receiveBuffer = new byte[1024];
            byte[] sendBuffer = new byte[1024];

            while(true) {
                Arrays.fill(receiveBuffer, (byte)0);
                DatagramPacket receivePacket = new DatagramPacket(receiveBuffer, receiveBuffer.length);
                socket.receive(receivePacket);
                String msg = new String(receivePacket.getData());

                System.out.println("received msg: " + msg);

                // Send response

                InetAddress senderAddress = receivePacket.getAddress();
                int senderPort = receivePacket.getPort();

                sendBuffer = String.format("Response form server to host: %s", senderAddress.toString()).getBytes();

                DatagramPacket datagramPacket = new DatagramPacket(sendBuffer, sendBuffer.length, senderAddress,
                    senderPort);

                socket.send(datagramPacket);

            }
        }
        catch(Exception e){
            e.printStackTrace();
        }
        finally {
            if (socket != null) {
                socket.close();
            }
        }
    }
}
