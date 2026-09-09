#!/usr/bin/env bash
#
# Verdis Chain — Multi-Location Server Deployment Script
#
# PURPOSE: Deploy Verdis Chain validator nodes across 3 geographic locations
#          to achieve 21-validator mainnet configuration with fault tolerance.
#
# TARGETS:
#   Server 1: Hostkey Netherlands (NL)   — 7 validators (ports 30340-30346)
#   Server 2: Hostkey USA               — 7 validators (ports 30340-30346)
#   Server 3: Hetzner Helsinki (FI)     — 7 validators (ports 30340-30346)
#   Boot Node: Hetzner current (91.98.160.145) — explorer + API (no change)
#
# FAULT TOLERANCE: 1 server failure = 14/21 survive (67%) — consensus continues
#
# USAGE:
#   ./deploy_3_servers.sh --server nl    # Deploy to Netherlands
#   ./deploy_3_servers.sh --server usa   # Deploy to USA
#   ./deploy_3_servers.sh --server fi    # Deploy to Helsinki
#   ./deploy_3_servers.sh --all          # Deploy to all 3
#   ./deploy_3_servers.sh --verify       # Verify all 3 are operational
#
# PREREQUISITES:
#   1. Servers provisioned (see docs/infrastructure/SERVER_PROCUREMENT.md)
#   2. SSH access configured for each server
#   3. Validator keys generated (see scripts/air-gapped-key-ceremony.sh)
#   4. Mainnet chain spec built and distributed
#   5. Rust toolchain installed on each server
#
# SECURITY:
#   - This script does NOT handle private keys. Keys must be manually
#     deployed via air-gapped USB transfer per the key ceremony protocol.
#   - This script sets up the node software, systemd services, monitoring.
#   - Private key injection is a MANUAL step performed by the operator.
#
# ============================================================================

set -euo pipefail

# --- Configuration ----------------------------------------------------------

REPO_URL="https://github.com/verdischain/verdis-chain-rust.git"
REPO_DIR="/opt/verdis-chain-rust"
CHAIN_SPEC="/opt/verdis-chain-rust/chain-specs/mainnet-raw.json"
BOOT_NODE_IP="91.98.160.145"
BOOT_NODE_P2P_PORT=30333
VALIDATORS_PER_SERVER=7
BASE_P2P_PORT=30340
BASE_RPC_PORT=9940
BASE_WS_PORT=9950

# Server definitions
declare -A SERVERS
SERVERS[nl]="HOSTKEY_NL"
SERVERS[usa]="HOSTKEY_USA"
SERVERS[fi]="HETZNER_HELSINKI"

declare -A SERVER_IPS
# These must be filled in after server procurement
SERVER_IPS[nl]="__NL_SERVER_IP__"
SERVER_IPS[usa]="__USA_SERVER_IP__"
SERVER_IPS[fi]="__FI_SERVER_IP__"

declare -A SERVER_NAMES
SERVER_NAMES[nl]="Hostkey Netherlands"
SERVER_NAMES[usa]="Hostkey USA"
SERVER_NAMES[fi]="Hetzner Helsinki"

# --- Functions --------------------------------------------------------------

log() {
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] $1"
}

error() {
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] ERROR: $1" >&2
    exit 1
}

warn() {
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] WARNING: $1"
}

success() {
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] OK: $1"
}

check_root() {
    [ "$(id -u)" -eq 0 ] || error "This script must be run as root"
}

check_prerequisites() {
    log "Checking prerequisites..."

    # Check if repo exists
    if [ ! -d "$REPO_DIR" ]; then
        log "Cloning Verdis Chain repository..."
        git clone "$REPO_URL" "$REPO_DIR"
    fi

    # Check if chain spec exists
    if [ ! -f "$CHAIN_SPEC" ]; then
        error "Mainnet chain spec not found at $CHAIN_SPEC. Build it before deploying."
    fi

    # Check if Rust is installed
    if ! command -v cargo &>/dev/null; then
        log "Installing Rust toolchain..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        source "$HOME/.cargo/env"
    fi

    # Check if verdis binary exists
    if [ ! -f "$REPO_DIR/target/release/verdis" ]; then
        log "Building verdis-node (release)... This will take 10-20 minutes."
        cd "$REPO_DIR"
        cargo build --release
    fi

    success "Prerequisites verified"
}

install_dependencies() {
    log "Installing system dependencies..."

    apt-get update -qq
    apt-get install -y -qq \
        build-essential \
        pkg-config \
        libssl-dev \
        curl \
        git \
        ufw \
        fail2ban \
        prometheus-node-exporter \
        chrony

    success "System dependencies installed"
}

configure_firewall() {
    log "Configuring UFW firewall..."

    # Default deny incoming
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing

    # Allow SSH (from boot node IP only for management)
    ufw allow from "$BOOT_NODE_IP" to any port 22 proto tcp

    # Allow P2P ports for 7 validators
    for i in $(seq 0 $((VALIDATORS_PER_SERVER - 1))); do
        port=$((BASE_P2P_PORT + i))
        ufw allow "$port"/tcp comment "Verdis validator $i P2P"
    done

    # Allow Prometheus monitoring (from boot node only)
    ufw allow from "$BOOT_NODE_IP" to any port 9100 proto tcp comment "Prometheus node exporter"

    ufw --force enable
    success "Firewall configured — P2P ports $(BASE_P2P_PORT)-$((BASE_P2P_PORT + VALIDATORS_PER_SERVER - 1)), SSH restricted to boot node"
}

configure_time_sync() {
    log "Configuring time synchronization (chrony)..."

    systemctl stop systemd-timesyncd 2>/dev/null || true
    systemctl disable systemd-timesyncd 2>/dev/null || true

    cat > /etc/chrony/chrony.conf << 'CHRONYEOF'
server 0.pool.ntp.org iburst
server 1.pool.ntp.org iburst
server 2.pool.ntp.org iburst
server 3.pool.ntp.org iburst
makestep 1 3
rtcsync
logdir /var/log/chrony
CHRONYEOF

    systemctl enable chrony
    systemctl restart chrony
    success "Time sync configured (chrony)"
}

create_validator_directories() {
    log "Creating validator data directories..."

    for i in $(seq 0 $((VALIDATORS_PER_SERVER - 1))); do
        local p2p_port=$((BASE_P2P_PORT + i))
        local data_dir="/opt/verdis-data/validator-$i"

        mkdir -p "$data_dir/keystore"
        mkdir -p "$data_dir/network"
        chown -R root:root "$data_dir"
        chmod 700 "$data_dir/keystore"

        log "  Validator $i: data_dir=$data_dir p2p_port=$p2p_port"
    done

    success "Validator directories created"
}

create_systemd_services() {
    log "Creating systemd service files for $VALIDATORS_PER_SERVER validators..."

    for i in $(seq 0 $((VALIDATORS_PER_SERVER - 1))); do
        local p2p_port=$((BASE_P2P_PORT + i))
        local rpc_port=$((BASE_RPC_PORT + i))
        local ws_port=$((BASE_WS_PORT + i))
        local data_dir="/opt/verdis-data/validator-$i"
        local service_file="/etc/systemd/system/verdis-validator-$i.service"

        cat > "$service_file" << SVCEOF
[Unit]
Description=Verdis Chain Validator Node #$i
After=network.target chrony.service
StartLimitIntervalSec=0

[Service]
ExecStart=$REPO_DIR/target/release/verdis \\
  --chain $CHAIN_SPEC \\
  --base-path $data_dir \\
  --validator \\
  --port $p2p_port \\
  --rpc-port $rpc_port \\
  --ws-port $ws_port \\
  --rpc-external \\
  --ws-external \\
  --rpc-methods unsafe \\
  --rpc-cors all \\
  --keystore $data_dir/keystore \\
  --bootnodes /dns/bootnode.verdischain.com/tcp/$BOOT_NODE_P2P_PORT/p2p/__BOOT_NODE_PEER_ID__
Restart=always
RestartSec=10
User=root
StandardOutput=append:/var/log/verdis-validator-$i.log
StandardError=append:/var/log/verdis-validator-$i.log

[Install]
WantedBy=multi-user.target
SVCEOF

        log "  Created: $service_file (P2P:$p2p_port RPC:$rpc_port WS:$ws_port)"
    done

    systemctl daemon-reload
    success "Systemd service files created for $VALIDATORS_PER_SERVER validators"
}

setup_monitoring() {
    log "Setting up monitoring..."

    # Prometheus node exporter is already installed
    systemctl enable prometheus-node-exporter
    systemctl start prometheus-node-exporter

    # Create health check script
    cat > /opt/verdis-data/health-check.sh << 'HEALTHEOF'
#!/usr/bin/env bash
# Verdis Chain — Validator Health Check
# Reports: block height, peer count, validator count, sync status

RPC="http://localhost:9940"

BLOCK=$(curl -s -m5 -H "Content-Type: application/json" \
  -d '{"id":1,"jsonrpc":"2.0","method":"chain_getHeader","params":[]}' \
  "$RPC" | python3 -c "import sys,json; print(int(json.load(sys.stdin)['result']['number'],16))" 2>/dev/null || echo "ERROR")

PEERS=$(curl -s -m5 -H "Content-Type: application/json" \
  -d '{"id":1,"jsonrpc":"2.0","method":"system_health","params":[]}' \
  "$RPC" | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['peers'])" 2>/dev/null || echo "ERROR")

SYNCING=$(curl -s -m5 -H "Content-Type: application/json" \
  -d '{"id":1,"jsonrpc":"2.0","method":"system_health","params":[]}' \
  "$RPC" | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['isSyncing'])" 2>/dev/null || echo "ERROR")

echo "BLOCK:$BLOCK PEERS:$PEERS SYNCING:$SYNCING"

if [ "$BLOCK" = "ERROR" ] || [ "$PEERS" = "ERROR" ]; then
    echo "HEALTH_CHECK_FAILED"
    exit 1
fi
echo "HEALTH_CHECK_OK"
HEALTHEOF

    chmod +x /opt/verdis-data/health-check.sh

    # Create cron entry for health check every 5 minutes
    (crontab -l 2>/dev/null | grep -v health-check; echo "*/5 * * * * /opt/verdis-data/health-check.sh >> /var/log/verdis-health.log") | crontab -

    success "Monitoring configured — health check every 5 minutes"
}

setup_log_rotation() {
    log "Setting up log rotation..."

    cat > /etc/logrotate.d/verdis-validator << 'LOGEOF'
/var/log/verdis-validator-*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
}
LOGEOF

    success "Log rotation configured (daily, 30 days retention)"
}

verify_deployment() {
    log "Verifying deployment..."

    local all_ok=true

    for i in $(seq 0 $((VALIDATORS_PER_SERVER - 1))); do
        local service="verdis-validator-$i"

        if systemctl is-active --quiet "$service"; then
            local rpc_port=$((BASE_RPC_PORT + i))
            local block=$(curl -s -m3 -H "Content-Type: application/json" \
                -d '{"id":1,"jsonrpc":"2.0","method":"chain_getHeader","params":[]}' \
                "http://localhost:$rpc_port" | python3 -c "import sys,json; print(int(json.load(sys.stdin)['result']['number'],16))" 2>/dev/null || echo "FAIL")

            if [ "$block" != "FAIL" ]; then
                success "  Validator $i: RUNNING (block #$block)"
            else
                warn "  Validator $i: RUNNING but RPC unreachable"
                all_ok=false
            fi
        else
            warn "  Validator $i: NOT RUNNING"
            all_ok=false
        fi
    done

    if $all_ok; then
        success "All $VALIDATORS_PER_SERVER validators operational"
    else
        warn "Some validators not fully operational — check logs in /var/log/verdis-validator-*.log"
    fi
}

# --- Main Deployment Logic --------------------------------------------------

deploy_to_server() {
    local server_key="$1"
    local server_name="${SERVER_NAMES[$server_key]:-UNKNOWN}"

    log "=========================================="
    log "DEPLOYING TO: $server_name"
    log "=========================================="

    check_root
    install_dependencies
    configure_firewall
    configure_time_sync
    check_prerequisites
    create_validator_directories
    create_systemd_services
    setup_monitoring
    setup_log_rotation

    log ""
    log "=========================================="
    log "DEPLOYMENT COMPLETE: $server_name"
    log "=========================================="
    log ""
    log "MANUAL STEPS REQUIRED:"
    log "  1. Copy validator private keys (from USB) to each validator keystore:"
    log "     /opt/verdis-data/validator-0/keystore/"
    log "     /opt/verdis-data/validator-1/keystore/"
    log "     ... (7 validators)"
    log ""
    log "  2. Update __BOOT_NODE_PEER_ID__ in systemd files with actual peer ID"
    log "     from the boot node (91.98.160.145)"
    log ""
    log "  3. Insert session keys for each validator via RPC:"
    log "     curl -H 'Content-Type: application/json' \\"
    log "       -d '{\"id\":1,\"jsonrpc\":\"2.0\",\"method\":\"author_insertKey\",\"params\":[\"babe!\",\"0x<SEED>\",\"0x<PUBKEY>\"]}' \\"
    log "       http://localhost:$((BASE_RPC_PORT + 0))"
    log ""
    log "  4. Start validators:"
    log "     systemctl start verdis-validator-0"
    log "     systemctl start verdis-validator-1"
    log "     ... (7 validators)"
    log ""
    log "  5. Verify with: $0 --verify"
    log ""
}

# --- Argument Parsing -------------------------------------------------------

case "${1:-}" in
    --server)
        [ -z "${2:-}" ] && error "Usage: $0 --server <nl|usa|fi>"
        [ -z "${SERVERS[$2]:-}" ] && error "Unknown server: $2. Use: nl, usa, fi"
        deploy_to_server "$2"
        ;;
    --all)
        log "WARNING: --all deploys to the CURRENT machine only."
        log "To deploy to all 3 servers, run this script ON each server with --server <location>"
        log "Run: ssh root@<NL_IP> '$0 --server nl'"
        log "Run: ssh root@<USA_IP> '$0 --server usa'"
        log "Run: ssh root@<FI_IP> '$0 --server fi'"
        exit 0
        ;;
    --verify)
        verify_deployment
        ;;
    *)
        echo "Verdis Chain — Multi-Location Server Deployment"
        echo ""
        echo "Usage:"
        echo "  $0 --server nl     Deploy 7 validators to Netherlands server"
        echo "  $0 --server usa    Deploy 7 validators to USA server"
        echo "  $0 --server fi     Deploy 7 validators to Helsinki server"
        echo "  $0 --verify        Verify all validators on this machine"
        echo ""
        echo "Targets:"
        echo "  nl  = Hostkey Netherlands  (7 validators, ports 30340-30346)"
        echo "  usa = Hostkey USA          (7 validators, ports 30340-30346)"
        echo "  fi  = Hetzner Helsinki     (7 validators, ports 30340-30346)"
        echo "  Boot node = Hetzner current (91.98.160.145) — unchanged"
        echo ""
        echo "Prerequisites:"
        echo "  - Server provisioned and SSH accessible"
        echo "  - Validator keys generated (air-gapped ceremony)"
        echo "  - Mainnet chain spec built"
        echo ""
        echo "Before running:"
        echo "  - Update SERVER_IPS in this script with actual IPs"
        echo "  - Update __BOOT_NODE_PEER_ID__ with actual boot node peer ID"
        echo ""
        exit 0
        ;;
esac
