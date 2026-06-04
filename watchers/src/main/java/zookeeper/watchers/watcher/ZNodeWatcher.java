package zookeeper.watchers.watcher;

import org.apache.zookeeper.*;
import org.apache.zookeeper.data.Stat;
import zookeeper.watchers.gui.ChildrenCountDialog;
import zookeeper.watchers.gui.MainControlPanel;
import zookeeper.watchers.gui.TreeViewDialog;

import java.io.IOException;
import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.CountDownLatch;

public class ZNodeWatcher implements Watcher {

    private static final String WATCHED_NODE = "/a";
    private static final int    SESSION_TIMEOUT_MS = 5_000;

    private final String connectString;
    private final String externalAppCommand;

    private ZooKeeper zk;
    private Process   externalProcess;

    private MainControlPanel controlPanel;

    private final CountDownLatch connectedLatch = new CountDownLatch(1);

    public ZNodeWatcher(String connectString, String externalAppCommand) {
        this.connectString      = connectString;
        this.externalAppCommand = externalAppCommand;
    }


    public void start() {
        connectToZooKeeper();

        controlPanel = new MainControlPanel(this);
        controlPanel.show();

        checkNodeExists();

        try {
            Thread.currentThread().join();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    public void close() {
        if (zk != null) {
            try {
                zk.close();
            } catch (InterruptedException ignored) {

            }
        }
        stopExternalApp();
    }

    private void connectToZooKeeper() {
        try {
            System.out.println("[ZK] Connecting to: " + connectString);
            zk = new ZooKeeper(connectString, SESSION_TIMEOUT_MS, this);
            connectedLatch.await();
            System.out.println("[ZK] Session established.");
        } catch (IOException | InterruptedException e) {
            throw new RuntimeException("Cannot connect to ZooKeeper: " + e.getMessage(), e);
        }
    }

    @Override
    public void process(WatchedEvent event) {
        System.out.println("[Watch] " + event.getType() + " | state=" + event.getState()
                           + " | path=" + event.getPath());

        if (event.getType() == Event.EventType.None) {
            handleStateChange(event.getState());
            return;
        }

        String path = event.getPath();

        switch (event.getType()) {
            case NodeCreated:
                if (WATCHED_NODE.equals(path)) {
                    onNodeACreated();
                }
                break;

            case NodeDeleted:
                if (WATCHED_NODE.equals(path)) {
                    onNodeADeleted();
                } else if (path != null && path.startsWith(WATCHED_NODE + "/")) {
                    watchChildrenOfA();
                }
                break;

            case NodeChildrenChanged:
                if (WATCHED_NODE.equals(path)) {
                    onChildrenChanged();
                }
                break;

            case NodeDataChanged:
                watchNodeData();
                break;

            default:
                break;
        }
    }

    private void handleStateChange(Event.KeeperState state) {
        switch (state) {
            case SyncConnected:
                System.out.println("[ZK] SyncConnected");
                connectedLatch.countDown();
                checkNodeExists();
                break;

            case Disconnected:
                System.out.println("[ZK] Disconnected - watches will be re-registered on reconnect");
                break;

            case Expired:
                System.out.println("[ZK] Session expired - reconnecting...");
                reconnect();
                break;

            case AuthFailed:
                System.err.println("[ZK] Auth failed!");
                break;

            default:
                break;
        }
    }

    private void reconnect() {
        try {
            zk.close();
        } catch (InterruptedException ignored) {

        }
        connectToZooKeeper();
    }

    public void checkNodeExists() {
        try {
            if (stat != null) {
                System.out.println("[ZK] /a already exists - registering children watch");
                watchChildrenOfA();
                watchNodeData();
            } else {
                System.out.println("[ZK] /a does not exist - waiting for NodeCreated");
            }
        } catch (KeeperException | InterruptedException e) {
            System.err.println("[ZK] Error in checkNodeExists: " + e.getMessage());
        }
    }

    private void watchChildrenOfA() {
        try {
            List<String> children = zk.getChildren(WATCHED_NODE, this);
            System.out.println("[ZK] Children of /a (currently " + children.size() + "): " + children);
        } catch (KeeperException.NoNodeException e) {
            System.out.println("[ZK] /a no longer exists - skipping children watch");
        } catch (KeeperException | InterruptedException e) {
            System.err.println("[ZK] Error watching children: " + e.getMessage());
        }
    }

    private void watchNodeData() {
        try {
            zk.getData(WATCHED_NODE, this, null);
        } catch (KeeperException.NoNodeException e) {
        } catch (KeeperException | InterruptedException e) {
            System.err.println("[ZK] Error watching data: " + e.getMessage());
        }
    }

    private void onNodeACreated() {
        System.out.println("[Event] /a CREATED - launching external app");
        launchExternalApp();
        watchChildrenOfA();
        watchNodeData();
        checkNodeExists();
    }

    private void onNodeADeleted() {
        System.out.println("[Event] /a DELETED - stopping external app");
        stopExternalApp();
        checkNodeExists();
    }

    private void onChildrenChanged() {
        try {
            List<String> children = zk.getChildren(WATCHED_NODE, this);
            int count = children.size();
            System.out.println("[Event] Children of /a changed - count=" + count + " " + children);
            ChildrenCountDialog.show(count, children);
            zk.exists(WATCHED_NODE, this);
        } catch (KeeperException.NoNodeException e) {
            System.out.println("[ZK] /a deleted while processing children change");
        } catch (KeeperException | InterruptedException e) {
            System.err.println("[ZK] Error in onChildrenChanged: " + e.getMessage());
        }
    }

    private void launchExternalApp() {
        if (externalProcess != null && externalProcess.isAlive()) {
            System.out.println("[App] External app is already running - skipping launch");
            return;
        }
        try {
            String[] cmdArray = externalAppCommand.split("\\s+");
            ProcessBuilder pb = new ProcessBuilder(cmdArray);
            pb.inheritIO();
            externalProcess = pb.start();
            System.out.println("[App] Launched: " + externalAppCommand
                               + " (PID=" + externalProcess.pid() + ")");
        } catch (IOException e) {
            System.err.println("[App] Failed to launch '" + externalAppCommand + "': " + e.getMessage());
        }
    }

    private void stopExternalApp() {
        if (externalProcess != null && externalProcess.isAlive()) {
            System.out.println("[App] Stopping external app (PID=" + externalProcess.pid() + ")");
            externalProcess.destroy();
            externalProcess = null;
        }
    }

    public void showTreeView() {
        try {
            Stat stat = zk.exists(WATCHED_NODE, false);
            if (stat == null) {
                javax.swing.JOptionPane.showMessageDialog(
                    null,
                    "Node /a does not exist.",
                    "ZooKeeper Tree",
                    javax.swing.JOptionPane.WARNING_MESSAGE
                );
                return;
            }
            TreeNode root = buildTree(WATCHED_NODE);
            TreeViewDialog.show(root);
        } catch (KeeperException | InterruptedException e) {
            System.err.println("[Tree] Error fetching tree: " + e.getMessage());
        }
    }

    private TreeNode buildTree(String path) throws KeeperException, InterruptedException {
        byte[] data;
        try {
            data = zk.getData(path, false, null);
        } catch (KeeperException.NoNodeException e) {
            return new TreeNode(path, null, List.of());
        }
        String dataStr = (data != null && data.length > 0) ? new String(data) : null;

        List<String> childNames;
        try {
            childNames = zk.getChildren(path, false);
        } catch (KeeperException.NoNodeException e) {
            childNames = List.of();
        }

        List<TreeNode> childNodes = new ArrayList<>();
        for (String child : childNames) {
            String childPath = path + "/" + child;
            childNodes.add(buildTree(childPath));
        }
        return new TreeNode(path, dataStr, childNodes);
    }

    public boolean isExternalAppRunning() {
        return externalProcess != null && externalProcess.isAlive();
    }

    public String getConnectString() {
        return connectString;
    }

    public String getExternalAppCommand() {
        return externalAppCommand;
    }
}
