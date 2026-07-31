#!/bin/bash
# ╔══════════════════════════════════════════════════════════════╗
# ║  Verdis Blockchain — One-Command VPS Installer                ║
# ║  Usage: curl -sL https://verdischain.com/install.sh | bash   ║
# ║  Or:   bash install.sh                                       ║
# ╚══════════════════════════════════════════════════════════════╝

set -e

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_banner() {
  echo -e "${CYAN}"
  echo "╔══════════════════════════════════════════════════╗"
  echo "║                                                  ║"
  echo "║         🌿 Verdis Blockchain Installer            ║"
  echo "║         The Eco-Friendly Blockchain               ║"
  echo "║                                                  ║"
  echo "╚══════════════════════════════════════════════════╝"
  echo -e "${NC}"
}

print_banner

# Check root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Please run as root: sudo bash install.sh${NC}"
  exit 1
fi

# Check OS
if [ -f /etc/os-release ]; then
  . /etc/os-release
  OS=$ID
else
  echo -e "${RED}Cannot detect OS. Supported: Ubuntu, Debian, CentOS.${NC}"
  exit 1
fi

echo -e "${YELLOW}Detected OS: $OS ${NC}"

# === STEP 1: Install Node.js ===
echo -e "\n${CYAN}[1/7] Installing Node.js 20...${NC}"

if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y nodejs git
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ] || [ "$OS" = "fedora" ] || [ "$OS" = "rocky" ]; then
  curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
  yum install -y nodejs git
else
  echo -e "${YELLOW}Unknown OS, trying apt...${NC}"
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y nodejs git
fi

NODE_VERSION=$(node -v)
echo -e "${GREEN}✅ Node.js installed: $NODE_VERSION${NC}"

# === STEP 2: Create verdis user ===
echo -e "\n${CYAN}[2/7] Creating verdis user...${NC}"
if ! id -u verdis &>/dev/null; then
  useradd -r -m -d /opt/verdis -s /bin/bash verdis
  echo -e "${GREEN}✅ User 'verdis' created${NC}"
else
  echo -e "${YELLOW}User 'verdis' already exists${NC}"
fi

# === STEP 3: Download and install Verdis ===
echo -e "\n${CYAN}[3/7] Downloading Verdis...${NC}"

INSTALL_DIR="/opt/verdis"
APP_DIR="$INSTALL_DIR/app"

# Ask for archive URL or use local
ARCHIVE_URL="${1:-}"
if [ -z "$ARCHIVE_URL" ]; then
  # Check if archive exists locally
  if [ -f "verdis-full.tar.gz" ]; then
    echo -e "${YELLOW}Using local verdis-full.tar.gz${NC}"
    ARCHIVE_URL="verdis-full.tar.gz"
  elif [ -f "verdis-deploy.tar.gz" ]; then
    echo -e "${YELLOW}Using local verdis-deploy.tar.gz${NC}"
    ARCHIVE_URL="verdis-deploy.tar.gz"
  else
    echo -e "${YELLOW}No archive found locally.${NC}"
    echo -e "To install, provide the archive URL:"
    echo -e "  bash install.sh https://your-url/verdis-full.tar.gz"
    echo -e "  bash install.sh https://your-url/verdis-deploy.tar.gz"
    echo -e "\nOr upload the archive to this server first."
    exit 1
  fi
fi

mkdir -p "$APP_DIR"
TEMP_DIR="/tmp/verdis-install"
mkdir -p "$TEMP_DIR"

if [[ "$ARCHIVE_URL" == http* ]]; then
  echo "Downloading from $ARCHIVE_URL..."
  curl -L -o "$TEMP_DIR/verdis.tar.gz" "$ARCHIVE_URL"
else
  cp "$ARCHIVE_URL" "$TEMP_DIR/verdis.tar.gz"
fi

echo "Extracting..."
tar -xzf "$TEMP_DIR/verdis.tar.gz" -C "$TEMP_DIR"

# Copy files
if [ -d "$TEMP_DIR/dist" ]; then
  cp -r "$TEMP_DIR/dist" "$APP_DIR/"
fi
if [ -d "$TEMP_DIR/src" ]; then
  cp -r "$TEMP_DIR/src" "$APP_DIR/"
fi
if [ -d "$TEMP_DIR/deploy" ]; then
  cp -r "$TEMP_DIR/deploy" "$APP_DIR/"
fi
if [ -f "$TEMP_DIR/package.json" ]; then
  cp "$TEMP_DIR/package.json" "$APP_DIR/"
fi
if [ -f "$TEMP_DIR/tsconfig.json" ]; then
  cp "$TEMP_DIR/tsconfig.json" "$APP_DIR/"
fi

# Create data directory for persistence
mkdir -p "$APP_DIR/data"
chown -R verdis:verdis "$APP_DIR"

echo -e "${GREEN}✅ Verdis installed to $APP_DIR${NC}"

# === STEP 4: Install dependencies ===
echo -e "\n${CYAN}[4/7] Installing dependencies...${NC}"
cd "$APP_DIR"
npm install --production 2>/dev/null || npm install 2>/dev/null || true

# If source exists, compile TypeScript
if [ -d "$APP_DIR/src" ] && [ -f "$APP_DIR/tsconfig.json" ]; then
  echo "Compiling TypeScript..."
  npx tsc 2>/dev/null || true
  cp src/web/*.html dist/web/ 2>/dev/null || true
fi

chown -R verdis:verdis "$APP_DIR"
echo -e "${GREEN}✅ Dependencies installed${NC}"

# === STEP 5: Create systemd service ===
echo -e "\n${CYAN}[5/7] Creating systemd service...${NC}"

cat > /etc/systemd/system/verdis.service << SVCEOF
[Unit]
Description=Verdis Blockchain Node
After=network.target

[Service]
Type=simple
User=verdis
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/node $APP_DIR/dist/index.js
Restart=always
RestartSec=5
Environment=NODE_ENV=production
Environment=PORT=3200
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable verdis
systemctl start verdis
sleep 3

if systemctl is-active --quiet verdis; then
  echo -e "${GREEN}✅ Verdis service running${NC}"
else
  echo -e "${RED}❌ Verdis failed to start. Check: journalctl -u verdis -f${NC}"
  exit 1
fi

# === STEP 6: Test the node ===
echo -e "\n${CYAN}[6/7] Verifying node...${NC}"
sleep 3

HEALTH=$(curl -s http://localhost:3200/api/monitoring/health 2>/dev/null)
if [ -n "$HEALTH" ]; then
  HEIGHT=$(echo "$HEALTH" | python3 -c "import sys,json; print(json.load(sys.stdin)['chain']['height'])" 2>/dev/null)
  STATUS=$(echo "$HEALTH" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])" 2>/dev/null)
  echo -e "${GREEN}✅ Node healthy — Status: $STATUS, Height: $HEIGHT${NC}"
else
  echo -e "${YELLOW}⚠️  Node starting up, give it a few seconds...${NC}"
  sleep 5
  curl -s http://localhost:3200/api/blockchain/info | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Height: {d[\"height\"]}')" 2>/dev/null
fi

# === STEP 7: Domain + SSL (optional) ===
echo -e "\n${CYAN}[7/7] Domain setup (optional)...${NC}"

DOMAIN="verdischain.com"

read -p "Configure domain $DOMAIN with SSL? (y/n): " SETUP_DOMAIN
if [ "$SETUP_DOMAIN" = "y" ] || [ "$SETUP_DOMAIN" = "Y" ]; then
  echo "Installing nginx and certbot..."

  if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt-get install -y nginx certbot python3-certbot-nginx 2>/dev/null || true
  else
    yum install -y nginx certbot python3-certbot-nginx 2>/dev/null || true
  fi

  # Install nginx config
  if [ -f "$APP_DIR/deploy/nginx-verdischain.conf" ]; then
    cp "$APP_DIR/deploy/nginx-verdischain.conf" /etc/nginx/sites-available/verdischain
    ln -sf /etc/nginx/sites-available/verdischain /etc/nginx/sites-enabled/verdischain
  else
    # Create inline config
    cat > /etc/nginx/sites-available/verdischain << NGINXCONF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:3200;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /rpc {
        proxy_pass http://127.0.0.1:3200/rpc;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
        if (\$request_method = OPTIONS) { return 204; }
    }
}

server {
    listen 80;
    server_name rpc.$DOMAIN;
    location / {
        proxy_pass http://127.0.0.1:3200/rpc;
        proxy_set_header Host \$host;
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
        if (\$request_method = OPTIONS) { return 204; }
    }
}
NGINXCONF
    ln -sf /etc/nginx/sites-available/verdischain /etc/nginx/sites-enabled/verdischain
  fi

  rm -f /etc/nginx/sites-enabled/default 2>/dev/null
  nginx -t && systemctl reload nginx
  echo -e "${GREEN}✅ Nginx configured${NC}"

  echo "Requesting SSL certificate..."
  read -p "Enter your email for SSL certificate: " SSL_EMAIL
  certbot --nginx -d $DOMAIN -d www.$DOMAIN -d rpc.$DOMAIN \
    --non-interactive --agree-tos --email "$SSL_EMAIL" 2>/dev/null || \
  echo -e "${YELLOW}⚠️  SSL failed. Make sure DNS A record points to this server first.${NC}"

  systemctl reload nginx
  echo -e "${GREEN}✅ SSL configured${NC}"
else
  echo -e "${YELLOW}Skipping domain setup. You can run it later:${NC}"
  echo "  sudo bash $APP_DIR/deploy/setup-domain.sh"
fi

# Cleanup
rm -rf "$TEMP_DIR"

# === DONE ===
VPS_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗"
echo -e "║  🌿 VERDIS BLOCKCHAIN — INSTALLED!                    ║"
echo -e "╠══════════════════════════════════════════════════════╣"
echo -e "║                                                      ║"
echo -e "║  Node running on: http://$VPS_IP:3200"
echo -e "║  Health check:   http://$VPS_IP:3200/api/monitoring/health"
echo -e "║  Dashboard:       http://$VPS_IP:3200/dashboard"
echo -e "║  Landing page:    http://$VPS_IP:3200"
echo -e "║  JSON-RPC:        http://$VPS_IP:3200/rpc"
echo -e "║  Chain ID:        909"
echo -e "║  Symbol:         VRS"
echo -e "║                                                      ║"
if [ "$SETUP_DOMAIN" = "y" ] || [ "$SETUP_DOMAIN" = "Y" ]; then
echo -e "║  🌐 With domain:                                       ║"
echo -e "║  https://$DOMAIN"
echo -e "║  https://$DOMAIN/dashboard"
echo -e "║  https://$DOMAIN/rpc"
echo -e "║                                                      ║"
fi
echo -e "║  Manage the service:                                  ║"
echo -e "║  systemctl status verdis                              ║"
echo -e "║  systemctl restart verdis                            ║"
echo -e "║  journalctl -u verdis -f                             ║"
echo -e "║                                                      ║"
echo -e "║  Auto-restart on reboot: ENABLED                      ║"
echo -e "║  State persistence: ENABLED (saves every 30s)         ║"
echo -e "║                                                      ║"
echo -e "╚══════════════════════════════════════════════════════╝${NC}"
