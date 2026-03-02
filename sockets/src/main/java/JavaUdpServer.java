import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
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
                int number = ByteBuffer
                    .wrap(receivePacket.getData())
                    .order(ByteOrder.LITTLE_ENDIAN)
                    .getInt();

                System.out.println(String.format("received number: %d", number));

                // Send response

                int sendNumber = number + 1;
                sendBuffer = ByteBuffer.allocate(4)
                    .order(ByteOrder.LITTLE_ENDIAN)
                    .putInt(sendNumber)
                    .array();

                InetAddress senderAddress = receivePacket.getAddress();
                int senderPort = receivePacket.getPort();

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
