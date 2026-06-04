package zookeeper.watchers;

import zookeeper.watchers.watcher.ZNodeWatcher;

import javax.swing.*;

/**
 * Entry point for the ZooKeeper Watcher Application.
 *
 * Usage:
 *   java -jar zookeeper-watcher.jar <zookeeper-connect-string> <external-app-command>
 *
 * Example (replicated ensemble):
 *   java -jar zookeeper-watcher.jar "zoo1:2181,zoo2:2181,zoo3:2181" "gedit"
 *   java -jar zookeeper-watcher.jar "localhost:2181,localhost:2182,localhost:2183" "xterm"
 */
public class ZooKeeperWatcherApp {

    public static void main(String[] args) {
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception ignored) {}

        if (args.length < 2) {
            showUsageAndExit();
        }

        String connectString = args[0];
        // Join remaining args as the external command (supports commands with spaces)
        StringBuilder cmdBuilder = new StringBuilder();
        for (int i = 1; i < args.length; i++) {
            if (i > 1) cmdBuilder.append(" ");
            cmdBuilder.append(args[i]);
        }
        String externalApp = cmdBuilder.toString();

        System.out.println("=================================================");
        System.out.println("  ZooKeeper Watcher Application");
        System.out.println("=================================================");
        System.out.println("  Connect string : " + connectString);
        System.out.println("  External app   : " + externalApp);
        System.out.println("  Watching node  : /a");
        System.out.println("=================================================");

        ZNodeWatcher watcher = new ZNodeWatcher(connectString, externalApp);

        // Shutdown hook for clean disconnect
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("\n[Shutdown] Closing ZooKeeper connection...");
            watcher.close();
        }));

        watcher.start();
    }

    private static void showUsageAndExit() {
        String usage =
                "ZooKeeper Watcher Application\n\n" +
                        "Usage:\n" +
                        "  java -jar zookeeper-watcher.jar <connect-string> <external-app>\n\n" +
                        "Arguments:\n" +
                        "  connect-string   ZooKeeper connection string\n" +
                        "                   Single:     localhost:2181\n" +
                        "                   Replicated: zoo1:2181,zoo2:2181,zoo3:2181\n" +
                        "  external-app     Command to launch when /a znode is created\n" +
                        "                   Examples: xterm, gedit, xcalc, notepad\n\n" +
                        "Examples:\n" +
                        "  java -jar zookeeper-watcher.jar localhost:2181 xterm\n" +
                        "  java -jar zookeeper-watcher.jar zoo1:2181,zoo2:2181,zoo3:2181 gedit\n\n" +
                        "Behavior:\n" +
                        "  - /a created   → launches <external-app>\n" +
                        "  - /a deleted   → kills  <external-app>\n" +
                        "  - /a/* added   → shows children count dialog\n" +
                        "  - Menu button  → displays full /a subtree";

        System.err.println(usage);

        JOptionPane.showMessageDialog(
                null,
                usage,
                "ZooKeeper Watcher – Usage",
                JOptionPane.INFORMATION_MESSAGE
        );
        System.exit(1);
    }
}
