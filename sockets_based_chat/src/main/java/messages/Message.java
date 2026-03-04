package messages;

import java.io.Serializable;

public class Message implements Serializable {
    private MessageType type;
    private String content;

    public Message(MessageType type, String content) {
        this.type = type;
        this.content = content;
    }

    public MessageType getType() {
        return type;
    }

    public String getContent() {
        return content;
    }

    @Override
    public String toString() {
        return String.format("Message{type=%s, content='%s'}", type, content);
    }
}
