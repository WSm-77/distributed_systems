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
                    watchDescendantsOf(path);
                }
                break;

            case NodeChildrenChanged:
                System.out.println("[Watch] Children changed for path: " + path);
                if (path != null && (WATCHED_NODE.equals(path) || path.startsWith(WATCHED_NODE + "/"))) {
                    onChildrenChanged(path);
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
        try {
            controlPanel.onRefresh();
        } catch (Exception e) {
            System.err.println("[UI] Error refreshing UI on state change: " + e.getMessage());
        }

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
            if (this.isNodeAExists()) {
                System.out.println("[ZK] /a already exists - registering children watch");
                watchDescendantsOf(WATCHED_NODE);
                watchNodeData();
            } else {
                System.out.println("[ZK] /a does not exist - waiting for NodeCreated");
            }
        } catch (Exception e) {
            System.err.println("[ZK] Error in checkNodeExists: " + e.getMessage());
        }
    }

    private void watchDescendantsOf(String path) {
        try {
            List<String> children = zk.getChildren(path, this);
            for (String child : children) {
                watchDescendantsOf(path + "/" + child);
            }
        } catch (KeeperException.NoNodeException e) {

        } catch (KeeperException | InterruptedException e) {
            System.err.println("[ZK] Error watching descendants of " + path + ": " + e.getMessage());
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
        watchDescendantsOf(WATCHED_NODE);
        watchNodeData();
        checkNodeExists();
    }

    private void onNodeADeleted() {
        System.out.println("[Event] /a DELETED - stopping external app");
        stopExternalApp();
        checkNodeExists();
    }

    private void onChildrenChanged(String path) {
        try {
            watchDescendantsOf(path);

            List<String> allDescendants = new ArrayList<>();
            collectDescendants(WATCHED_NODE, allDescendants);
            int count = allDescendants.size();
            System.out.println("[Event] Descendants of /a changed - count=" + count + " " + allDescendants);
            ChildrenCountDialog.show(count, allDescendants);

            zk.exists(WATCHED_NODE, this);
        } catch (KeeperException.NoNodeException e) {
            System.out.println("[ZK] Node deleted while processing children change: " + path);
        } catch (KeeperException | InterruptedException e) {
            System.err.println("[ZK] Error in onChildrenChanged: " + e.getMessage());
        }
    }

    private void collectDescendants(String path, List<String> result)
            throws KeeperException, InterruptedException {
        List<String> children;
        try {
            children = zk.getChildren(path, false);
        } catch (KeeperException.NoNodeException e) {
            return;
        }
        for (String child : children) {
            String childPath = path + "/" + child;
            result.add(childPath);
            collectDescendants(childPath, result);
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

    public boolean isNodeAExists() {
        try {
            return zk.exists(WATCHED_NODE, this) != null;
        } catch (KeeperException | InterruptedException e) {
            System.err.println("[Node] Error checking node existence: " + e.getMessage());
            return false;
        }
    }

    public String getConnectString() {
        return connectString;
    }

    public String getExternalAppCommand() {
        return externalAppCommand;
    }
}
