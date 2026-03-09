package messages;

public enum MessageType {
    // TCP
    REGISTER_CLIENT,
    UNREGISTER_CLIENT,
    MESSAGE,

    // UDP
    UDP_REGISTER_CLIENT,
    UDP_UNREGISTER_CLIENT,
    UDP_MESSAGE
}
