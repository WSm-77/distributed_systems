package zookeeper.watchers.gui;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.util.List;
import java.util.stream.Collectors;

public class ChildrenCountDialog {

    private static final Color COLOR_BG     = new Color(30, 32, 40);
    private static final Color COLOR_BORDER = new Color(97, 175, 239);
    private static final Color COLOR_COUNT  = new Color(97, 175, 239);
    private static final Color COLOR_TEXT   = new Color(220, 223, 228);
    private static final Color COLOR_MUTED  = new Color(130, 137, 151);
    private static final Color COLOR_CHILD  = new Color(152, 195, 121);

    public static void show(int count, List<String> children) {
        SwingUtilities.invokeLater(() -> buildAndShow(count, children));
    }

    private static void buildAndShow(int count, List<String> children) {
        JWindow window = new JWindow();
        window.setAlwaysOnTop(true);
        window.setBackground(new Color(0, 0, 0, 0));

        JPanel root = new JPanel(new BorderLayout(0, 0));
        root.setBackground(COLOR_BG);
        root.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLineBorder(COLOR_BORDER, 2),
            new EmptyBorder(20, 28, 20, 28)
        ));

        JLabel titleLabel = new JLabel("Children of  /a", SwingConstants.CENTER);
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 13));
        titleLabel.setForeground(COLOR_MUTED);

        JLabel countLabel = new JLabel(String.valueOf(count), SwingConstants.CENTER);
        countLabel.setFont(new Font("Segoe UI", Font.BOLD, 72));
        countLabel.setForeground(COLOR_COUNT);

        String childText = children.isEmpty()
            ? "(no children)"
            : children.stream().map(c -> "  • " + c).collect(Collectors.joining("\n"));
        JTextArea childArea = new JTextArea(childText);
        childArea.setEditable(false);
        childArea.setOpaque(false);
        childArea.setForeground(COLOR_CHILD);
        childArea.setFont(new Font("JetBrains Mono", Font.PLAIN, 12));
        childArea.setBorder(null);

        JLabel hint = new JLabel("(click to dismiss)", SwingConstants.CENTER);
        hint.setFont(new Font("Segoe UI", Font.ITALIC, 10));
        hint.setForeground(COLOR_MUTED);

        JPanel body = new JPanel();
        body.setOpaque(false);
        body.setLayout(new BoxLayout(body, BoxLayout.Y_AXIS));
        titleLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        countLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        childArea.setAlignmentX(Component.CENTER_ALIGNMENT);
        hint.setAlignmentX(Component.CENTER_ALIGNMENT);

        body.add(titleLabel);
        body.add(Box.createVerticalStrut(4));
        body.add(countLabel);
        body.add(Box.createVerticalStrut(8));
        body.add(new JSeparator());
        body.add(Box.createVerticalStrut(8));
        body.add(childArea);
        body.add(Box.createVerticalStrut(12));
        body.add(hint);

        root.add(body, BorderLayout.CENTER);
        window.add(root);
        window.pack();

        Dimension screen = Toolkit.getDefaultToolkit().getScreenSize();
        window.setLocation(
            screen.width  - window.getWidth()  - 20,
            screen.height - window.getHeight() - 50
        );

        root.addMouseListener(new java.awt.event.MouseAdapter() {
            @Override
            public void mouseClicked(java.awt.event.MouseEvent e) {
                window.dispose();
            }
        });

        window.setVisible(true);

        Timer timer = new Timer(4_000, e -> window.dispose());
        timer.setRepeats(false);
        timer.start();
    }
}
