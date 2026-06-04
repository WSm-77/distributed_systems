package zookeeper.watchers.watcher;

import org.apache.zookeeper.*;
import org.apache.zookeeper.data.Stat;
import zookeeper.watchers.gui.ChildrenCountDialog;
import zookeeper.watchers.gui.MainControlPanel;
import zookeeper.watchers.gui.TreeViewDialog;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.CountDownLatch;

/**
 * Core watcher component.
 *
 * Responsibilities:
 *  1. Maintain ZooKeeper session (auto-reconnect on session expiry).
 *  2. Watch /a for creation and deletion.
 *  3. Watch /a's children list for additions.
 *  4. Manage the lifecycle of the external GUI process.
 *  5. Show a children-count dialog on every child addition.
 *  6. Provide tree-view on demand.
 */
public class ZNodeWatcher implements Watcher {

    private static final String WATCHED_NODE = "/a";
    private static final int    SESSION_TIMEOUT_MS = 5_000;

    private final String connectString;
    private final String externalAppCommand;

    private ZooKeeper zk;
    private Process   externalProcess;

    /** Main control panel (always visible while app runs). */
    private MainControlPanel controlPanel;

    /** Latch released once the ZK session is established. */
    private final CountDownLatch connectedLatch = new CountDownLatch(1);

    public ZNodeWatcher(String connectString, String externalAppCommand) {
        this.connectString      = connectString;
        this.externalAppCommand = externalAppCommand;
    }

    // -------------------------------------------------------------------------
    // Lifecycle
    // -------------------------------------------------------------------------

    /** Connect to ZooKeeper, open the control panel, and keep running. */
    public void start() {
        connectToZooKeeper();

        // Open the main control panel
        controlPanel = new MainControlPanel(this);
        controlPanel.show();

        // Perform an initial check: /a may already exist
        checkNodeExists();

        // Block the main thread – the app is event-driven from here on
        try {
            Thread.currentThread().join();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    public void close() {
        if (zk != null) {
            try { zk.close(); } catch (InterruptedException ignored) {}
        }
        stopExternalApp();
    }

    // -------------------------------------------------------------------------
    // ZooKeeper connection
    // -------------------------------------------------------------------------

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

    // -------------------------------------------------------------------------
    // Watcher callback – called for EVERY event on watched znodes
    // -------------------------------------------------------------------------

    @Override
    public void process(WatchedEvent event) {
        System.out.println("[Watch] " + event.getType() + " | state=" + event.getState()
                           + " | path=" + event.getPath());

        // --- Session state events ---
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
                    // A child was deleted – refresh children count watch
                    watchChildrenOf_A();
                }
                break;

            case NodeChildrenChanged:
                if (WATCHED_NODE.equals(path)) {
                    onChildrenChanged();
                }
                break;

            case NodeDataChanged:
                // Re-register data watch if needed (not used functionally here)
                watchNodeData();
                break;

            default:
                break;
        }
    }

    // -------------------------------------------------------------------------
    // Session state handling
    // -------------------------------------------------------------------------

    private void handleStateChange(Event.KeeperState state) {
        switch (state) {
            case SyncConnected:
                System.out.println("[ZK] SyncConnected");
                connectedLatch.countDown();
                // Re-register all watches after reconnect
                checkNodeExists();
                break;

            case Disconnected:
                System.out.println("[ZK] Disconnected – watches will be re-registered on reconnect");
                break;

            case Expired:
                System.out.println("[ZK] Session expired – reconnecting...");
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
        try { zk.close(); } catch (InterruptedException ignored) {}
        connectToZooKeeper();
    }

    // -------------------------------------------------------------------------
    // Initial check + watch registration
    // -------------------------------------------------------------------------

    /**
     * Check whether /a exists and register the appropriate watches.
     * Called on startup and after session reconnect.
     */
    public void checkNodeExists() {
        try {
            Stat stat = zk.exists(WATCHED_NODE, this);   // watch for NodeCreated / NodeDeleted
            if (stat != null) {
                System.out.println("[ZK] /a already exists – registering children watch");
                watchChildrenOf_A();
                watchNodeData();
            } else {
                System.out.println("[ZK] /a does not exist – waiting for NodeCreated");
            }
        } catch (KeeperException | InterruptedException e) {
            System.err.println("[ZK] Error in checkNodeExists: " + e.getMessage());
        }
    }

    // -------------------------------------------------------------------------
    // Watch helpers
    // -------------------------------------------------------------------------

    /**
     * Register a children watch on /a so we get NodeChildrenChanged events.
     * Must be re-registered after every event (ZK watches are one-shot).
     */
    private void watchChildrenOf_A() {
        try {
            List<String> children = zk.getChildren(WATCHED_NODE, this);
            System.out.println("[ZK] Children of /a (currently " + children.size() + "): " + children);
        } catch (KeeperException.NoNodeException e) {
            System.out.println("[ZK] /a no longer exists – skipping children watch");
        } catch (KeeperException | InterruptedException e) {
            System.err.println("[ZK] Error watching children: " + e.getMessage());
        }
    }

    /** Register a data watch on /a (re-registers on NodeDataChanged). */
    private void watchNodeData() {
        try {
            zk.getData(WATCHED_NODE, this, null);
        } catch (KeeperException.NoNodeException e) {
            // /a gone, nothing to do
        } catch (KeeperException | InterruptedException e) {
            System.err.println("[ZK] Error watching data: " + e.getMessage());
        }
    }

    // -------------------------------------------------------------------------
    // Business logic callbacks
    // -------------------------------------------------------------------------

    /** Called when /a is created. */
    private void onNodeACreated() {
        System.out.println("[Event] /a CREATED – launching external app");
        launchExternalApp();
        // Now register children + data watches on /a
        watchChildrenOf_A();
        watchNodeData();
        // Re-register existence watch for future deletion
        checkNodeExists();
    }

    /** Called when /a is deleted. */
    private void onNodeADeleted() {
        System.out.println("[Event] /a DELETED – stopping external app");
        stopExternalApp();
        // Re-register existence watch to catch next creation
        checkNodeExists();
    }

    /** Called when /a's children list changes (child added or removed). */
    private void onChildrenChanged() {
        try {
            // getChildren with a new watch to keep monitoring
            List<String> children = zk.getChildren(WATCHED_NODE, this);
            int count = children.size();
            System.out.println("[Event] Children of /a changed – count=" + count + " " + children);
            ChildrenCountDialog.show(count, children);
            // Re-register existence watch to detect deletion
            zk.exists(WATCHED_NODE, this);
        } catch (KeeperException.NoNodeException e) {
            System.out.println("[ZK] /a deleted while processing children change");
        } catch (KeeperException | InterruptedException e) {
            System.err.println("[ZK] Error in onChildrenChanged: " + e.getMessage());
        }
    }

    // -------------------------------------------------------------------------
    // External process management
    // -------------------------------------------------------------------------

    private void launchExternalApp() {
        if (externalProcess != null && externalProcess.isAlive()) {
            System.out.println("[App] External app is already running – skipping launch");
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

    // -------------------------------------------------------------------------
    // Public tree-view API (called by GUI)
    // -------------------------------------------------------------------------

    /**
     * Retrieve and display the full subtree rooted at /a.
     * Called when the user clicks "Show Tree" in the control panel.
     */
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

    /**
     * Recursively build a tree from ZooKeeper starting at {@code path}.
     */
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

        java.util.List<TreeNode> childNodes = new java.util.ArrayList<>();
        for (String child : childNames) {
            String childPath = path + "/" + child;
            childNodes.add(buildTree(childPath));
        }
        return new TreeNode(path, dataStr, childNodes);
    }

    // -------------------------------------------------------------------------
    // Status helpers
    // -------------------------------------------------------------------------

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
