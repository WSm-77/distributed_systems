# ZooKeeper Watcher Application

A Java Swing application that monitors the `/a` ZooKeeper znode using the **Watches** mechanism (ZooKeeper 3.8.4 API). Designed to run against a **Replicated ZooKeeper** ensemble (3-node, quorum-based).

---

## Overview

The application reacts to changes in the ZooKeeper tree in real time:

| Event | Reaction |
|---|---|
| `/a` is **created** | Launches an external GUI application specified on the command line |
| `/a` is **deleted** | Kills the external application |
| A **descendant is added** to `/a` | Shows a graphical pop-up with the current total descendant count |
| "Show Tree" button clicked | Displays the full `/a` subtree in a modal dialog |

Since ZooKeeper watches are **one-shot**, the application re-registers every watch immediately after it fires. On session expiry (`KeeperState.Expired`) a new session is created and all watches are restored automatically.

---

## Project Structure

```
.
├── pom.xml
├── README.md
├── demo.sh                                # automated demo script
├── docker/
│   └── docker-compose.yml              # 3-node ZooKeeper 3.8.4 ensemble
└── src/main/java/zookeeper/watchers/
    ├── ZooKeeperWatcherApp.java         # Entry point - parses CLI args
    ├── watcher/
    │   ├── ZNodeWatcher.java            # Core watch logic + ZK session management
    │   └── TreeNode.java                # Immutable snapshot of a ZK node
    └── gui/
        ├── MainControlPanel.java        # Always-visible control panel + event log
        ├── ChildrenCountDialog.java     # Pop-up shown on every descendant addition
        └── TreeViewDialog.java          # Full /a subtree rendered as JTree
```

---

## Prerequisites

- **Java 15+** — verify with `java -version`
- **Maven 3.6+** — verify with `mvn -version`
- **Docker + Docker Compose** — verify with `docker -v`
- **netcat** (`nc`) — for health-checking ZooKeeper nodes

---

## Step 1 — Start the Replicated ZooKeeper Ensemble

```bash
docker compose -f docker/docker-compose.yml up -d
```

Wait a few seconds for leader election to complete, then verify all three nodes respond:

```bash
echo ruok | nc localhost 2181   # expected: imok
echo ruok | nc localhost 2182   # expected: imok
echo ruok | nc localhost 2183   # expected: imok
```

Confirm which node is the leader:

```bash
echo srvr | nc localhost 2181 | grep Mode
echo srvr | nc localhost 2182 | grep Mode
echo srvr | nc localhost 2183 | grep Mode
```

One node will print `Mode: leader`, the other two `Mode: follower`.

---

## Step 2 — Build the Application

```bash
mvn clean package
```

This produces a fat JAR with all dependencies bundled:

```
target/watchers.jar
```

---

## Step 3 — Run the Application

```bash
java -jar target/watchers.jar \
     "localhost:2181,localhost:2182,localhost:2183" \
     "gnome-calculator"
```

### Arguments

| # | Argument | Description | Example |
|---|---|---|---|
| 1 | `connect-string` | ZooKeeper connection string (comma-separated `host:port` pairs) | `localhost:2181,localhost:2182,localhost:2183` |
| 2 | `external-app` | Command to launch when `/a` is created | `gnome-calculator`, `xterm`, `gedit`, `xcalc` |

The external app command may contain spaces — all arguments after the connect string are joined:

```bash
java -jar target/watchers.jar "localhost:2181,localhost:2182,localhost:2183" "gnome-calculator --new-window"
```

On startup the main control panel appears showing connection info, node status, external app status, and a live event log.

---

## Step 4 — Test the Watches

Open two terminal windows, one connected to each ZooKeeper node:

**Terminal A — zoo1:**

```bash
docker exec -it zoo1 zkCli.sh
```

**Terminal B — zoo2:**

```bash
docker exec -it zoo2 zkCli.sh
```

Then run the following commands in order and observe the application reacting after each one:

**Terminal A (zoo1):**

```bash
# 1. Create /a  ->  the external app (e.g. gnome-calculator) is launched
create /a "hello"

# 2. Add two children via zoo1  ->  a pop-up appears after each, showing the updated count
create /a/child1 "data1"
create /a/child2 "data2"
```

**Terminal B (zoo2):**
```bash
# 3. Add one child via zoo2  ->  demonstrates that watches fire regardless of which node the write goes to
create /a/child3 "data3"
```

**Terminal A (zoo1):**
```bash
# 4. Add descendants under child1  ->  pop-up shows all descendants of /a, not just direct children
create /a/child1/descendant11 "desc1"
create /a/child1/descendant12 "desc2"

# 5. In the control panel click "Show Tree"
#    ->  a dialog opens displaying the full subtree:
#       /a
#       ├── child1  (data1)
#       │   ├── descendant11  (desc1)
#       │   └── descendant12  (desc2)
#       ├── child2  (data2)
#       └── child3  (data3)
```

**Terminal B (zoo2):**
```bash
# 6. Delete child3 via zoo2  ->  pop-up shows updated descendant count
delete /a/child3
```

**Terminal A (zoo1):**
```bash
# 7. Delete /a and all remaining descendants  ->  the external app is killed
deleteall /a
```

---

## Step 5 — Stop Everything

```bash
# Stop the Java application
Ctrl+C   # or click the "Exit" button in the GUI

# Stop and remove the ZooKeeper containers
docker compose -f docker/docker-compose.yml down

# To also remove persisted data volumes
docker compose -f docker/docker-compose.yml down -v
```

---

## Automated Demo

To run the entire scenario automatically use the provided `demo.sh` script:

```bash
chmod +x demo.sh
./demo.sh                  # uses gnome-calculator by default
./demo.sh xterm            # or any other GUI app
```

The script starts the ensemble, builds the project, launches the application, executes all the ZooKeeper operations with pauses between them so you can observe the GUI reactions, and shuts everything down at the end.

---

## Troubleshooting

**`echo ruok | nc localhost 2182` returns nothing**

The ZooKeeper ensemble may still be electing a leader. Wait 3-5 seconds and retry. If the problem persists, check that the `docker-compose.yml` in use has `ZOO_SERVERS` with `;2181` (the internal container port) for all three nodes — not `;2182` / `;2183`.

**External app does not launch**

Make sure the command is available on your `PATH`:

```bash
which gnome-calculator   # or: which xterm
```

Install if missing, e.g. `sudo apt install gnome-calculator`.
