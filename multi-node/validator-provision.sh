#!/usr/bin/env bash
# Verdis Validator Provisioning Script
# Full setup: build, keys, systemd, firewall, monitoring registration
set -euo pipefail

NODE_BASE="/opt/verdis-chain-rust"
BINARY="$NODE_BASE/target/release/verdis"
VALIDATOR_NUM="${1:-1}"
HOST="${2:-91.98.160.145}"

echo "================================================"
echo "  Verdis Validator #$VALIDATOR_NUM Provisioning"
echo "  Host: $HOST"
echo "  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "================================================"

# 1. Install dependencies
echo ""
echo "[1/7] Installing dependencies..."
apt-get update -qq
apt-get install -y -qq curl git build-essential pkg-config libssl-dev jq ufw fail2ban
echo "  ✅ Dependencies installed"

# 2. Install Rust toolchain
echo ""
echo "[2/7] Checking Rust toolchain..."
if ! command -v cargo &>/dev/null; then
    echo "  Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
fi
rustup default stable
rustup update
rustup target add wasm32v1-none
echo "  ✅ Rust $(rustc --version) ready"

# 3. Build node binary
echo ""
echo "[3/7] Building Verdis node..."
cd "$NODE_BASE"
if [ ! -f "$BINARY" ]; then
    cargo build --release
fi
echo "  ✅ Binary: $BINARY ($($BINARY --version 2>&1 | head -1))"

# 4. Generate/load keys
echo ""
echo "[4/7] Setting up validator keys..."
KEYS_DIR="$NODE_BASE/multi-node/keys"
mkdir -p "$KEYS_DIR"

KEY_FILE="$KEYS_DIR/validator-$VALIDATOR_NUM.json"
NODE_KEY_FILE="$KEYS_DIR/validator-$VALIDATOR_NUM.node.key"

if [ ! -f "$KEY_FILE" ]; then
    echo "  Generating keys for validator-$VALIDATOR_NUM..."
    cd "$NODE_BASE/multi-node"
    ./generate-keys.sh
fi

if [ -f "$KEY_FILE" ]; then
    echo "  ✅ Keys loaded from $KEY_FILE"
else
    echo "  ❌ Key generation failed"
    exit 1
fi

# 5. Configure systemd service
echo ""
echo "[5/7] Setting up systemd service..."
DATA_DIR="$NODE_BASE/data-validator-$VALIDATOR_NUM"
mkdir -p "$DATA_DIR"

# Copy keys to keystore
mkdir -p "$DATA_DIR/keystore"
cp "$KEY_FILE" "$DATA_DIR/keystore/"

P2P_PORT=$((30333 + VALIDATOR_NUM - 1))
SERVICE_NAME="verdis-validator@${VALIDATOR_NUM}"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Verdis Validator #$VALIDATOR_NUM
After=network.target
StartLimitIntervalSec=0

[Service]
ExecStart=$BINARY \
  --chain $NODE_BASE/multi-node/chain-spec.json \
  --base-path $DATA_DIR \
  --validator \
  --port $P2P_PORT \
  --node-key $(cat "$NODE_KEY_FILE" 2>/dev/null || echo "PLACEHOLDER") \
  --keystore $DATA_DIR/keystore \
  --bootnodes /dns/bootnode1.verdischain.com/tcp/30333/p2p/PLACEHOLDER \
  --bootnodes /dns/bootnode2.verdischain.com/tcp/30333/p2p/PLACEHOLDER
Restart=always
RestartSec=10
User=root
StandardOutput=append:/var/log/verdis-validator-$VALIDATOR_NUM.log
StandardError=append:/var/log/verdis-validator-$VALIDATOR_NUM.log

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
echo "  ✅ Service configured: $SERVICE_NAME"

# 6. Configure firewall
echo ""
echo "[6/7] Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp        # SSH
ufw allow 80/tcp        # HTTP
ufw allow 443/tcp       # HTTPS
ufw allow $P2P_PORT/tcp # P2P
ufw --force enable
echo "  ✅ Firewall configured (P2P: $P2P_PORT)"

# 7. Start and verify
echo ""
echo "[7/7] Starting validator..."
systemctl start "$SERVICE_NAME"
sleep 5

if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "  ✅ Validator running"
    
    # Check block sync
    sleep 10
    BLOCK=$(curl -s -X POST http://localhost:9944 \
        -H 'Content-Type: application/json' \
        -d '{"jsonrpc":"2.0","id":1,"method":"chain_getHeader","params":[]}' \
        | jq -r '.result.number // "0"' 2>/dev/null)
    echo "  Current block: #$((16#$BLOCK))"
else
    echo "  ❌ Validator failed to start"
    journalctl -u "$SERVICE_NAME" --no-pager | tail -20
    exit 1
fi

# Set up log rotation
cat > "/etc/logrotate.d/verdis-validator-$VALIDATOR_NUM" << EOF
/var/log/verdis-validator-$VALIDATOR_NUM.log {
    daily
    maxsize 100M
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF

echo ""
echo "================================================"
echo "  Validator #$VALIDATOR_NUM Provisioned!"
echo "================================================"
echo "  Service:   $SERVICE_NAME"
echo "  P2P Port:  $P2P_PORT"
echo "  Data:      $DATA_DIR"
echo "  Keys:      $KEY_FILE"
echo "  Log:       /var/log/verdis-validator-$VALIDATOR_NUM.log"
echo "  Firewall:  UFW active (22/80/443/$P2P_PORT)"
echo ""
echo "  Monitor:   systemctl status $SERVICE_NAME"
echo "  Logs:      journalctl -u $SERVICE_NAME -f"
echo "  Stop:      systemctl stop $SERVICE_NAME"
echo "  Restart:  systemctl restart $SERVICE_NAME"
echo "================================================"
