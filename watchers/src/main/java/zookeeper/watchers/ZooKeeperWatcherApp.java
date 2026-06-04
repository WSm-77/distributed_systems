package zookeeper.watchers;

import zookeeper.watchers.watcher.ZNodeWatcher;

import javax.swing.*;

public class ZooKeeperWatcherApp {

    public static void main(String[] args) {
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception ignored) {}

        if (args.length < 2) {
            showUsageAndExit();
        }

        String connectString = args[0];
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
        String usage ="""
                ZooKeeper Watcher Application


                        Usage:
                          java -jar zookeeper-watcher.jar <connect-string> <external-app>

                        Arguments:
                          connect-string   ZooKeeper connection string
                                           Single:     localhost:2181
                                           Replicated: zoo1:2181,zoo2:2181,zoo3:2181
                          external-app     Command to launch when /a znode is created
                                           Examples: gnome-calculator, gedit, notepad

                        Examples:
                          java -jar zookeeper-watcher.jar localhost:2181 xterm
                          java -jar zookeeper-watcher.jar zoo1:2181,zoo2:2181,zoo3:2181 gedit

                        Behavior:
                          - /a created    - launches <external-app>
                          - /a deleted    - kills  <external-app>
                          - /a/* added    - shows children count dialog
                          - Menu button   - displays full /a subtree
                        """;

        System.err.println(usage);

        JOptionPane.showMessageDialog(
                null,
                usage,
                "ZooKeeper Watcher - Usage",
                JOptionPane.INFORMATION_MESSAGE
        );
        System.exit(1);
    }
}
