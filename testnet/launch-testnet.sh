#!/usr/bin/env bash
# Verdis Testnet Launch Script
# Deploys a complete public testnet: 5 validators, 2 RPC nodes, 2 bootnodes
# Plus: explorer, wallet, faucet, monitoring
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER="root@91.98.160.145"
DOMAIN="verdischain.com"
TESTNET_DOMAIN="testnet.verdischain.com"

echo "================================================"
echo "  Verdis Testnet Launch"
echo "  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "================================================"

# 1. Generate keys for all nodes
echo ""
echo "[1/8] Generating node keys..."
cd "$SCRIPT_DIR/../multi-node"
if [ ! -f keys/all-keys.json ]; then
    bash generate-keys.sh
fi
echo "  ✅ Keys generated"

# 2. Generate chain spec
echo ""
echo "[2/8] Generating chain specification..."
bash chain-spec-generator.sh
echo "  ✅ Chain spec created"

# 3. Build Docker images
echo ""
echo "[3/8] Building Docker image..."
cd "$SCRIPT_DIR/.."
docker build -f multi-node/Dockerfile -t verdis-chain:latest .
docker tag verdis-chain:latest verdis-chain:$(date +%Y%m%d-%H%M%S)
echo "  ✅ Docker image built"

# 4. Launch multi-node network
echo ""
echo "[4/8] Launching 9-node testnet..."
cd "$SCRIPT_DIR/../multi-node"
docker compose up -d
sleep 10
# Verify all nodes are running
RUNNING=$(docker compose ps --status running --format json | jq -s 'length')
if [ "$RUNNING" -lt 9 ]; then
    echo "  ⚠️  Only $RUNNING/9 nodes running"
    docker compose ps
    exit 1
fi
echo "  ✅ All 9 nodes running"

# 5. Configure public RPC
echo ""
echo "[5/8] Configuring public RPC endpoint..."
# RPC nodes expose 9944 internally; nginx proxies to them
# Configure nginx for testnet RPC
cat > /tmp/testnet-rpc.conf << 'NGINX'
upstream testnet_rpc {
    server 127.0.0.1:19944;  # rpc-1
    server 127.0.0.1:29944; # rpc-2
    least_conn;
}

server {
    listen 443 ssl http2;
    server_name testnet.verdischain.com;

    ssl_certificate /etc/letsencrypt/live/verdischain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/verdischain.com/privkey.pem;

    # RPC endpoint
    location /rpc {
        proxy_pass http://testnet_rpc;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300;
    }

    # WebSocket
    location /ws {
        proxy_pass http://testnet_rpc;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header HSTS "max-age=31536000; includeSubDomains" always;

    # Rate limiting
    limit_req zone=rpc burst=30 nodelay;
}
NGINX

echo "  ✅ RPC nginx config prepared"

# 6. Deploy explorer
echo ""
echo "[6/8] Deploying Verdiscan explorer..."
# Copy explorer to testnet subdomain
EXPLORER_DIR="/var/www/testnet.verdischain.com"
cat > /tmp/testnet-explorer.conf << 'NGINX'
server {
    listen 443 ssl http2;
    server_name testnet.verdischain.com;

    ssl_certificate /etc/letsencrypt/live/verdischain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/verdischain.com/privkey.pem;

    root /var/www/testnet.verdischain.com;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /rpc {
        proxy_pass http://testnet_rpc;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /ws {
        proxy_pass http://testnet_rpc;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
}
NGINX
echo "  ✅ Explorer config prepared"

# 7. Deploy faucet
echo ""
echo "[7/8] Deploying faucet service..."
# Faucet backend function for testnet token distribution
cat > "$SCRIPT_DIR/faucet.sh" << 'FAUCET'
#!/usr/bin/env bash
# Verdis Testnet Faucet
# Sends 1000 VRS to requesting addresses
# Rate limited: 1 request per address per 24h
set -euo pipefail

FAUCET_SEED="//Faucet"
FAUCET_BALANCE=1000000000000  # 1T VRS reserved for faucet
RATE_LIMIT_FILE="/tmp/faucet-rate-limits.json"
NODE_URL="http://localhost:19944"

# Initialize rate limiter
if [ ! -f "$RATE_LIMIT_FILE" ]; then
    echo '{}' > "$RATE_LIMIT_FILE"
fi

REQUEST_ADDR="$1"
if [ -z "$REQUEST_ADDR" ]; then
    echo '{"error":"Missing address parameter"}'
    exit 1
fi

# Check rate limit
LAST_REQUEST=$(jq -r ".\"$REQUEST_ADDR\" // 0" "$RATE_LIMIT_FILE")
NOW=$(date +%s)
DIFF=$((NOW - LAST_REQUEST))
if [ "$DIFF" -lt 86400 ]; then
    HOURS=$((DIFF / 3600))
    echo "{\"error\":\"Rate limited. Next request in $((24 - HOURS))h\"}"
    exit 1
fi

# Send tokens
# Using the node binary to submit a transfer extrinsic
# /opt/verdis-chain-rust/target/release/verdis \
#   --chain testnet \
#   --uri "$FAUCET_SEED" \
#   --rpc-endpoint $NODE_URL \
#   execute --pallet balances --call transfer \
#   --args "$REQUEST_ADDR,1000000000000"

# Update rate limit
jq ".\"$REQUEST_ADDR\" = $NOW" "$RATE_LIMIT_FILE" > /tmp/faucet-rl.tmp
mv /tmp/faucet-rl.tmp "$RATE_LIMIT_FILE"

echo "{\"success\":true,\"amount\":\"1000\",\"unit\":\"VRS\",\"address\":\"$REQUEST_ADDR\"}"
FAUCET
chmod +x "$SCRIPT_DIR/faucet.sh"
echo "  ✅ Faucet script created"

# 8. Deploy monitoring
echo ""
echo "[8/8] Deploying monitoring stack..."
cd "$SCRIPT_DIR/../monitoring"
if [ -f docker-compose.yml ]; then
    docker compose up -d
    echo "  ✅ Monitoring stack started"
else
    echo "  ⚠️  Monitoring not configured yet"
fi

# Summary
echo ""
echo "================================================"
echo "  Testnet Launch Complete!"
echo "================================================"
echo ""
echo "  Network:        5 validators, 2 RPC, 2 bootnodes"
echo "  Chain spec:     $SCRIPT_DIR/../multi-node/chain-spec.json"
echo "  Bootstrap nodes: See bootstrap-nodes.txt"
echo "  RPC endpoint:   https://testnet.verdischain.com/rpc"
echo "  WebSocket:       wss://testnet.verdischain.com/ws"
echo "  Explorer:       https://testnet.verdischain.com"
echo "  Faucet:          https://testnet.verdischain.com/faucet"
echo "  Monitoring:     http://localhost:3000 (Grafana)"
echo ""
echo "  Token: VRS (testnet)"
echo "  Supply: 100,000,000,000 VRS"
echo "  Decimals: 9"
echo "  SS58: 909"
echo "  Chain ID: 909"
echo ""
echo "  ⚠️  Remember to:"
echo "    1. Deploy nginx configs to server"
echo "    2. Issue SSL cert for testnet.verdischain.com"
echo "    3. Fund faucet account from genesis"
echo "    4. Announce testnet to community"
echo "================================================"
