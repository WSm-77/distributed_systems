package messages;

import java.io.Serializable;

public class Message implements Serializable {
    private MessagesType type;
    private String content;

    public Message(MessagesType type, String content) {
        this.type = type;
        this.content = content;
    }

    public MessagesType getType() {
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
