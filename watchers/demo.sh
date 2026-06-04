#!/usr/bin/env bash
# =============================================================================
#  ZooKeeper Watcher - Demo Script
# =============================================================================
set -euo pipefail

# ── Configuration ─────────────────────────────────────────────────────────────
COMPOSE_FILE="docker/docker-compose.yml"
JAR="target/watchers.jar"
ZK_CONNECT="localhost:2181,localhost:2182,localhost:2183"
EXTERNAL_APP="${1:-gnome-calculator}"          # pass a different app as $1, default: gnome-calculator
STEP_DELAY=3                        # seconds to pause between steps

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# ── Helpers ───────────────────────────────────────────────────────────────────
step() {
    echo ""
    echo -e "${CYAN}${BOLD}══════════════════════════════════════════════${RESET}"
    echo -e "${CYAN}${BOLD}  STEP $1: $2${RESET}"
    echo -e "${CYAN}${BOLD}══════════════════════════════════════════════${RESET}"
}

info()    { echo -e "  ${GREEN}▶${RESET}  $*"; }
warn()    { echo -e "  ${YELLOW}⚠${RESET}   $*"; }
die()     { echo -e "  ${RED}✖${RESET}  $*" >&2; exit 1; }

pause() {
    info "Waiting ${STEP_DELAY}s so you can observe the GUI reaction..."
    sleep "$STEP_DELAY"
}

zk_cmd() {
    # $1 = container (zoo1 or zoo2), remaining = zkCli command string
    local container="$1"; shift
    docker exec "$container" zkCli.sh -server localhost:2181 "$@" 2>/dev/null || true
}

zk_create() {
    local container="$1"
    local path="$2"
    local data="${3:-demo}"
    info "[$container] create $path \"$data\""
    docker exec "$container" zkCli.sh -server localhost:2181 \
        create "$path" "$data" 2>/dev/null || warn "Node $path may already exist, skipping"
    pause
}

zk_delete() {
    local container="$1"
    local path="$2"
    local flag="${3:-}"          # pass "-R" for recursive (ZK 3.8+: deleteall)
    if [[ "$flag" == "-R" ]]; then
        info "[$container] deleteall $path (recursive)"
        docker exec "$container" zkCli.sh -server localhost:2181 \
            deleteall "$path" 2>/dev/null || warn "Could not delete $path"
    else
        info "[$container] delete $path"
        docker exec "$container" zkCli.sh -server localhost:2181 \
            delete "$path" 2>/dev/null || warn "Could not delete $path"
    fi
    pause
}

wait_for_zk() {
    local port="$1"
    local retries=20
    info "Waiting for ZooKeeper on port $port..."
    until echo ruok | nc -q1 localhost "$port" 2>/dev/null | grep -q imok; do
        retries=$((retries - 1))
        [[ $retries -eq 0 ]] && die "ZooKeeper on port $port did not become ready in time"
        sleep 1
    done
    echo -e "  ${GREEN}✔${RESET}  ZooKeeper :$port is ready"
}

cleanup() {
    echo ""
    warn "Interrupt received - cleaning up..."
    kill "$APP_PID" 2>/dev/null && info "Java app stopped" || true
    docker compose -f "$COMPOSE_FILE" down 2>/dev/null && info "Docker containers stopped" || true
    exit 1
}
trap cleanup INT TERM

APP_PID=""

# =============================================================================
#  STEP 1 - Start Docker ensemble
# =============================================================================
step 1 "Starting replicated ZooKeeper ensemble (3 nodes)"

if ! docker compose -f "$COMPOSE_FILE" ps --quiet 2>/dev/null | grep -q .; then
    docker compose -f "$COMPOSE_FILE" up -d
    info "Containers started"
else
    info "Containers already running - skipping"
fi

wait_for_zk 2181
wait_for_zk 2182
wait_for_zk 2183
info "All 3 ZooKeeper nodes are healthy ✔"

# =============================================================================
#  STEP 2 - Build Maven project
# =============================================================================
step 2 "Building Maven project"

mvn clean package -q
[[ -f "$JAR" ]] || die "Build succeeded but JAR not found at: $JAR"
info "Build successful → $JAR"

# =============================================================================
#  STEP 3 - Launch Java application (background)
# =============================================================================
step 3 "Launching ZooKeeper Watcher application"
info "External app : $EXTERNAL_APP"
info "Connect string: $ZK_CONNECT"

java -jar "$JAR" "$ZK_CONNECT" "$EXTERNAL_APP" &
APP_PID=$!
info "Application started (PID=$APP_PID)"
info "Waiting 3s for the GUI to initialize..."
sleep 3

if ! kill -0 "$APP_PID" 2>/dev/null; then
    die "Java application exited prematurely - check the logs above"
fi

# =============================================================================
#  STEP 4 - Create /a  (triggers external app launch)
# =============================================================================
step 4 "Creating root node /a on zoo1  →  external app should launch"
zk_create zoo1 /a "root-data"

# =============================================================================
#  STEP 5 - Create /a/child1 and /a/child2 via zoo1
# =============================================================================
step 5 "Creating /a/child1 and /a/child2 on zoo1  →  children count dialog x2"
zk_create zoo1 /a/child1 "child1-data"
zk_create zoo1 /a/child2 "child2-data"

# =============================================================================
#  STEP 6 - Create /a/child3 via zoo2
# =============================================================================
step 6 "Creating /a/child3 on zoo2  →  children count dialog"
zk_create zoo2 /a/child3 "child3-data"

# =============================================================================
#  STEP 7 - Create descendants under /a/child1
# =============================================================================
step 7 "Creating descendants /a/child1/descendant11 and /a/child1/descendant12  →  descendant count dialog x2"
zk_create zoo1 /a/child1/descendant11 "desc11-data"
zk_create zoo1 /a/child1/descendant12 "desc12-data"

# =============================================================================
#  STEP 8 - Delete /a/child3
# =============================================================================
step 8 "Deleting /a/child3  →  descendant count dialog"
zk_delete zoo2 /a/child3

# =============================================================================
#  STEP 9 - Delete /a root node (with all remaining descendants)
# =============================================================================
step 9 "Deleting /a root node  →  external app should be killed"
zk_delete zoo1 /a -R

# =============================================================================
#  STEP 10 - Stop Docker containers
# =============================================================================
step 10 "Stopping Docker containers"
info "Stopping Java application (PID=$APP_PID)..."
kill "$APP_PID" 2>/dev/null && wait "$APP_PID" 2>/dev/null || true
info "Java application stopped"

docker compose -f "$COMPOSE_FILE" down
info "Docker containers stopped"

echo ""
echo -e "${GREEN}${BOLD}  Demo completed successfully ✔${RESET}"
echo ""
