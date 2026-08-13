#!/usr/bin/env bash
# Verdis Bootstrap Node Setup Script
# Bootstraps a new node (validator, RPC, or bootnode) for the Verdis network
set -euo pipefail

NODE_TYPE="${1:-validator}"
NODE_NUM="${2:-1}"
NODE_BASE="/opt/verdis-chain-rust"
BINARY="$NODE_BASE/target/release/verdis"
DATA_BASE="$NODE_BASE/data-$NODE_TYPE-$NODE_NUM"
KEYS_DIR="$NODE_BASE/multi-node/keys"
CHAIN_SPEC="$NODE_BASE/multi-node/chain-spec.json"
BOOTNODE1="PLACEHOLDER_BOOT1"
BOOTNODE2="PLACEHOLDER_BOOT2"
P2P_PORT=$((30333 + NODE_NUM - 1))
RPC_PORT=$((19944 + (NODE_NUM - 1) * 10000))
WS_PORT=$((9944 + (NODE_NUM - 1) * 10000))

echo "============================================"
echo "  Verdis Bootstrap: $NODE_TYPE-$NODE_NUM"
echo "============================================"

# Load node key
NODE_KEY_FILE="$KEYS_DIR/$NODE_TYPE-$NODE_NUM.node.key"
if [ -f "$NODE_KEY_FILE" ]; then
    NODE_KEY=$(cat "$NODE_KEY_FILE")
    echo "  Loaded node key from $NODE_KEY_FILE"
else
    echo "  ⚠️  No node key found, generating new one..."
    NODE_KEY=$($BINARY key generate-node-key 2>/dev/null || echo "")
    if [ -n "$NODE_KEY" ]; then
        echo "$NODE_KEY" > "$NODE_KEY_FILE"
    fi
fi

# Create data directory
mkdir -p "$DATA_BASE"

# Build command based on node type
CMD="$BINARY --chain $CHAIN_SPEC --base-path $DATA_BASE"
CMD="$CMD --port $P2P_PORT --node-key $NODE_KEY"
CMD="$CMD --bootnodes /dns/bootnode1.verdischain.com/tcp/30333/p2p/$BOOTNODE1"
CMD="$CMD --bootnodes /dns/bootnode2.verdischain.com/tcp/30333/p2p/$BOOTNODE2"

case "$NODE_TYPE" in
    validator)
        CMD="$CMD --validator"
        # Load validator keys
        KEY_FILE="$KEYS_DIR/validator-$NODE_NUM.json"
        if [ -f "$KEY_FILE" ]; then
            CMD="$CMD --keystore $DATA_BASE/keystore"
            cp "$KEY_FILE" "$DATA_BASE/keystore/" 2>/dev/null || true
        fi
        echo "  Role: Validator (port $P2P_PORT)"
        ;;
    rpc)
        CMD="$CMD --rpc-external --rpc-cors all --rpc-methods Safe"
        CMD="$CMD --rpc-port $RPC_PORT --ws-external --ws-port $WS_PORT"
        echo "  Role: RPC Node (RPC $RPC_PORT, WS $WS_PORT, P2P $P2P_PORT)"
        ;;
    bootnode)
        CMD="$CMD --no-telemetry"
        echo "  Role: Bootnode (P2P $P2P_PORT)"
        ;;
    *)
        echo "  ❌ Unknown node type: $NODE_TYPE"
        exit 1
        ;;
esac

# Set up systemd service
SERVICE_NAME="verdis-${NODE_TYPE}@${NODE_NUM}"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Verdis $NODE_TYPE Node #$NODE_NUM
After=network.target
StartLimitIntervalSec=0

[Service]
ExecStart=$CMD
Restart=always
RestartSec=10
User=root
Group=root
StandardOutput=append:/var/log/verdis-${NODE_TYPE}-${NODE_NUM}.log
StandardError=append:/var/log/verdis-${NODE_TYPE}-${NODE_NUM}.log

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

sleep 3
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "  ✅ $SERVICE_NAME started successfully"
else
    echo "  ❌ $SERVICE_NAME failed to start"
    journalctl -u "$SERVICE_NAME" --no-pager | tail -20
    exit 1
fi

# Verify peer connection (for non-validators)
if [ "$NODE_TYPE" != "validator" ]; then
    sleep 5
    PEERS=$(curl -s -X POST http://localhost:$RPC_PORT -H 'Content-Type: application/json' \
        -d '{"jsonrpc":"2.0","id":1,"method":"system_health","params":[]}' \
        | jq -r '.result.peers // 0' 2>/dev/null || echo 0)
    echo "  Peers connected: $PEERS"
fi

echo "  ✅ Bootstrap complete"
echo "  P2P: /ip4/91.98.160.145/tcp/$P2P_PORT/p2p/12D3KooW${NODE_KEY:0:40}"
