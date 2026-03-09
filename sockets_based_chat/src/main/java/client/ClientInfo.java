package client;

import java.net.InetAddress;

public record ClientInfo(InetAddress address, int port) {}
