package zookeeper.watchers.gui;

import zookeeper.watchers.watcher.ZNodeWatcher;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;

public class MainControlPanel {

    private static final Color COLOR_BG        = new Color(30, 32, 40);
    private static final Color COLOR_HEADER     = new Color(20, 22, 30);
    private static final Color COLOR_ACCENT     = new Color(97, 175, 239);
    private static final Color COLOR_GREEN      = new Color(152, 195, 121);
    private static final Color COLOR_RED        = new Color(224, 108, 117);
    private static final Color COLOR_YELLOW     = new Color(229, 192,  123);
    private static final Color COLOR_TEXT       = new Color(220, 223, 228);
    private static final Color COLOR_MUTED      = new Color(130, 137, 151);
    private static final Color COLOR_LOG_BG     = new Color(20, 22, 28);
    private static final Font  FONT_MONO        = new Font("JetBrains Mono", Font.PLAIN, 12);
    private static final Font  FONT_MONO_BOLD   = new Font("JetBrains Mono", Font.BOLD, 12);
    private static final Font  FONT_TITLE       = new Font("Segoe UI", Font.BOLD, 16);
    private static final Font  FONT_LABEL       = new Font("Segoe UI", Font.PLAIN, 12);
    private static final Font  FONT_LABEL_BOLD  = new Font("Segoe UI", Font.BOLD, 12);
    private static final DateTimeFormatter TIME_FMT = DateTimeFormatter.ofPattern("HH:mm:ss");

    private final ZNodeWatcher watcher;

    private JFrame     frame;
    private JLabel     statusNodeLabel;
    private JLabel     statusAppLabel;
    private JTextArea  logArea;

    public MainControlPanel(ZNodeWatcher watcher) {
        this.watcher = watcher;
    }

    public void show() {
        SwingUtilities.invokeLater(() -> {
            frame = new JFrame("ZooKeeper Watcher");
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setSize(680, 560);
            frame.setLocationRelativeTo(null);
            frame.getContentPane().setBackground(COLOR_BG);
            frame.setLayout(new BorderLayout(0, 0));

            frame.add(buildHeader(),  BorderLayout.NORTH);
            frame.add(buildCenter(),  BorderLayout.CENTER);
            frame.add(buildFooter(),  BorderLayout.SOUTH);

            frame.setVisible(true);

            appendLog("Application started. Watching /a on " + watcher.getConnectString());
        });
    }

    private JPanel buildHeader() {
        JPanel panel = new JPanel(new BorderLayout());
        panel.setBackground(COLOR_HEADER);
        panel.setBorder(new EmptyBorder(16, 20, 16, 20));

        JLabel title = new JLabel("ZooKeeper Watcher");
        title.setFont(FONT_TITLE);
        title.setForeground(COLOR_ACCENT);

        JLabel subtitle = new JLabel("Monitoring node  /a  on  " + watcher.getConnectString());
        subtitle.setFont(FONT_LABEL);
        subtitle.setForeground(COLOR_MUTED);

        JPanel text = new JPanel(new GridLayout(2, 1, 0, 2));
        text.setOpaque(false);
        text.add(title);
        text.add(subtitle);

        panel.add(text, BorderLayout.CENTER);
        return panel;
    }

    private JPanel buildCenter() {
        JPanel panel = new JPanel(new BorderLayout(0, 0));
        panel.setBackground(COLOR_BG);

        panel.add(buildStatusPanel(), BorderLayout.NORTH);
        panel.add(buildLogPanel(),    BorderLayout.CENTER);

        return panel;
    }

    private JPanel buildStatusPanel() {
        JPanel panel = new JPanel(new GridLayout(1, 2, 12, 0));
        panel.setBackground(COLOR_BG);
        panel.setBorder(new EmptyBorder(16, 20, 12, 20));

        statusNodeLabel = new JLabel("⬜  /a  UNKNOWN", SwingConstants.CENTER);
        statusNodeLabel.setFont(FONT_LABEL_BOLD);
        statusNodeLabel.setForeground(COLOR_MUTED);
        panel.add(buildCard("ZNode Status", statusNodeLabel));

        statusAppLabel = new JLabel("⬜  Not running", SwingConstants.CENTER);
        statusAppLabel.setFont(FONT_LABEL_BOLD);
        statusAppLabel.setForeground(COLOR_MUTED);
        panel.add(buildCard("External App", statusAppLabel));

        return panel;
    }

    private JPanel buildCard(String title, JLabel content) {
        JPanel card = new JPanel(new BorderLayout(0, 6));
        card.setBackground(new Color(38, 40, 50));
        card.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLineBorder(new Color(55, 58, 70), 1),
            new EmptyBorder(12, 12, 12, 12)
        ));

        JLabel titleLabel = new JLabel(title);
        titleLabel.setFont(FONT_LABEL);
        titleLabel.setForeground(COLOR_MUTED);

        card.add(titleLabel, BorderLayout.NORTH);
        card.add(content,    BorderLayout.CENTER);
        return card;
    }

    private JPanel buildLogPanel() {
        JPanel panel = new JPanel(new BorderLayout(0, 6));
        panel.setBackground(COLOR_BG);
        panel.setBorder(new EmptyBorder(0, 20, 0, 20));

        JLabel header = new JLabel("Event Log");
        header.setFont(FONT_LABEL_BOLD);
        header.setForeground(COLOR_MUTED);
        panel.add(header, BorderLayout.NORTH);

        logArea = new JTextArea();
        logArea.setEditable(false);
        logArea.setBackground(COLOR_LOG_BG);
        logArea.setForeground(COLOR_TEXT);
        logArea.setFont(FONT_MONO);
        logArea.setLineWrap(false);
        logArea.setBorder(new EmptyBorder(8, 10, 8, 10));

        JScrollPane scroll = new JScrollPane(logArea);
        scroll.setBorder(BorderFactory.createLineBorder(new Color(55, 58, 70), 1));
        scroll.getViewport().setBackground(COLOR_LOG_BG);

        panel.add(scroll, BorderLayout.CENTER);
        return panel;
    }

    private JPanel buildFooter() {
        JPanel panel = new JPanel(new FlowLayout(FlowLayout.RIGHT, 12, 12));
        panel.setBackground(COLOR_HEADER);
        panel.setBorder(new EmptyBorder(4, 20, 4, 20));

        JButton treeBtn    = buildButton("🌲  Show Tree",       COLOR_GREEN,  e -> onShowTree());
        JButton refreshBtn = buildButton("🔄  Refresh Status",  COLOR_ACCENT, e -> onRefresh());
        JButton exitBtn    = buildButton("✖  Exit",            COLOR_RED,    e -> System.exit(0));

        panel.add(refreshBtn);
        panel.add(treeBtn);
        panel.add(exitBtn);
        return panel;
    }

    private JButton buildButton(String text, Color color, java.awt.event.ActionListener listener) {
        JButton btn = new JButton(text);
        btn.setFont(FONT_LABEL_BOLD);
        btn.setForeground(Color.WHITE);
        btn.setBackground(color.darker());
        btn.setFocusPainted(false);
        btn.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLineBorder(color, 1),
            new EmptyBorder(8, 16, 8, 16)
        ));
        btn.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
        btn.addActionListener(listener);

        btn.addMouseListener(new java.awt.event.MouseAdapter() {
            @Override public void mouseEntered(java.awt.event.MouseEvent e) {
                btn.setBackground(color);
            }
            @Override public void mouseExited(java.awt.event.MouseEvent e) {
                btn.setBackground(color.darker());
            }
        });
        return btn;
    }

    private void onShowTree() {
        appendLog("User requested tree view of /a");
        watcher.showTreeView();
    }

    private void onRefresh() {
        appendLog("Manual status refresh");
        watcher.checkNodeExists();
        updateNodeStatus(watcher.isExternalAppRunning());
    }

    public void setNodeExists(boolean exists) {
        SwingUtilities.invokeLater(() -> {
            if (exists) {
                statusNodeLabel.setText("🟢  /a  EXISTS");
                statusNodeLabel.setForeground(COLOR_GREEN);
            } else {
                statusNodeLabel.setText("🔴  /a  ABSENT");
                statusNodeLabel.setForeground(COLOR_RED);
            }
        });
    }

    public void updateNodeStatus(boolean appRunning) {
        SwingUtilities.invokeLater(() -> {
            if (appRunning) {
                statusAppLabel.setText("🟢  Running");
                statusAppLabel.setForeground(COLOR_GREEN);
            } else {
                statusAppLabel.setText("🔴  Stopped");
                statusAppLabel.setForeground(COLOR_RED);
            }
        });
    }

    public void appendLog(String message) {
        SwingUtilities.invokeLater(() -> {
            String ts   = LocalTime.now().format(TIME_FMT);
            String line = "[" + ts + "] " + message + "\n";
            logArea.append(line);

            logArea.setCaretPosition(logArea.getDocument().getLength());
        });
    }
}
