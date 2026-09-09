#!/usr/bin/env bash
# ==============================================================================
# Verdis Blockchain Monitoring Stack Installation & Setup Script
# Target Host: 91.98.160.145 (verdischain.com)
# Stack: Prometheus (9090), Grafana (3000), Alertmanager (9093), Node Exporter (9100)
# Substrate Target: localhost:9615
# ==============================================================================

set -euo pipefail

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

INSTALL_DIR="/opt/verdis-monitoring"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BOLD}${BLUE}====================================================${NC}"
echo -e "${BOLD}${BLUE}   Verdis Blockchain Monitoring Stack Installer    ${NC}"
echo -e "${BOLD}${BLUE}====================================================${NC}"

# Check for root / sudo permissions
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}[!] Warning: Script is not running as root. Requesting elevated privileges...${NC}"
    exec sudo bash "$0" "$@"
fi

# 1. Install Docker & Docker Compose if missing
echo -e "\n${BOLD}[1/7] Checking Docker and Docker Compose prerequisites...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}[+] Docker not found. Installing Docker CE...${NC}"
    apt-get update -qq
    apt-get install -y -qq apt-transport-https ca-certificates curl gnupg lsb-release
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
    systemctl enable --now docker
    echo -e "${GREEN}[✓] Docker installed successfully.${NC}"
else
    echo -e "${GREEN}[✓] Docker is already installed: $(docker --version)${NC}"
fi

# Check Docker Compose plugin or standalone binary
COMPOSE_CMD=""
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo -e "${YELLOW}[+] Installing docker-compose-plugin...${NC}"
    apt-get update -qq && apt-get install -y -qq docker-compose-plugin
    COMPOSE_CMD="docker compose"
fi
echo -e "${GREEN}[✓] Docker Compose command: ${COMPOSE_CMD}${NC}"

# 2. Copy configurations to target directory
echo -e "\n${BOLD}[2/7] Deploying configuration files to ${INSTALL_DIR}...${NC}"
mkdir -p "${INSTALL_DIR}"
cp -r "${SCRIPT_DIR}/"* "${INSTALL_DIR}/"
cd "${INSTALL_DIR}"

# 3. Setup Grafana Admin Credentials Environment File
echo -e "\n${BOLD}[3/7] Setting up environment configuration...${NC}"
GRAFANA_ADMIN_USER="admin"
GRAFANA_ADMIN_PASS="${GRAFANA_ADMIN_PASSWORD:-VerdisSecurePass2026!}"

cat <<EOF > "${INSTALL_DIR}/.env"
GRAFANA_ADMIN_USER=${GRAFANA_ADMIN_USER}
GRAFANA_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASS}
EOF
chmod 600 "${INSTALL_DIR}/.env"
echo -e "${GREEN}[✓] Environment file created with Grafana admin password.${NC}"

# 4. Configure Firewall (UFW)
echo -e "\n${BOLD}[4/7] Configuring UFW Firewall...${NC}"
if command -v ufw &> /dev/null && ufw status | grep -q "Status: active"; then
    echo -e "${YELLOW}[+] UFW is active. Opening monitoring ports (9090, 3000, 9093)...${NC}"
    ufw allow 9090/tcp comment 'Verdis Prometheus'
    ufw allow 3000/tcp comment 'Verdis Grafana'
    ufw allow 9093/tcp comment 'Verdis Alertmanager'
    ufw reload
    echo -e "${GREEN}[✓] Firewall rules updated successfully.${NC}"
else
    echo -e "${YELLOW}[!] UFW is either not installed or inactive. Skipping UFW configuration.${NC}"
fi

# 5. Start Docker Monitoring Stack
echo -e "\n${BOLD}[5/7] Starting Verdis Monitoring Stack via Docker Compose...${NC}"
${COMPOSE_CMD} down --remove-orphans || true
${COMPOSE_CMD} up -d

# 6. Verify Service Status & Health
echo -e "\n${BOLD}[6/7] Verifying running services and health checks...${NC}"
echo "Waiting 5 seconds for services to initialize..."
sleep 5

${COMPOSE_CMD} ps

# Function to check HTTP endpoint health
check_health() {
    local name="$1"
    local url="$2"
    local expected_code="${3:-200}"

    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_code"; then
        echo -e "${GREEN}[✓] ${name} is responding at ${url}${NC}"
    else
        echo -e "${YELLOW}[!] Warning: ${name} at ${url} did not return HTTP ${expected_code} yet.${NC}"
    fi
}

check_health "Prometheus" "http://localhost:9090/-/healthy"
check_health "Grafana" "http://localhost:3000/api/health"
check_health "Alertmanager" "http://localhost:9093/-/healthy"
check_health "Node Exporter" "http://localhost:9100/metrics"

# Check Substrate node metrics availability on host
if curl -s http://localhost:9615/metrics | grep -q "substrate_block_height"; then
    echo -e "${GREEN}[✓] Substrate Node Prometheus endpoint detected at http://localhost:9615/metrics${NC}"
else
    echo -e "${YELLOW}[!] Note: Substrate Node exporter not responding on localhost:9615 yet.${NC}"
    echo -e "${YELLOW}    Ensure verdis-node.service is running with '--prometheus-external' or '--prometheus-port 9615'.${NC}"
fi

# 7. Configure Optional Nginx Reverse Proxy for Grafana
echo -e "\n${BOLD}[7/7] Configuring Optional Nginx Reverse Proxy...${NC}"
if command -v nginx &> /dev/null; then
    NGINX_CONF="/etc/nginx/sites-available/grafana.verdischain.com"
    echo -e "${YELLOW}[+] Creating Nginx site configuration at ${NGINX_CONF}...${NC}"

    cat <<'EOF' > "${NGINX_CONF}"
server {
    listen 80;
    server_name grafana.verdischain.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

    if [ -d "/etc/nginx/sites-enabled" ]; then
        ln -sf "${NGINX_CONF}" /etc/nginx/sites-enabled/
        nginx -t && systemctl reload nginx || echo -e "${YELLOW}[!] Nginx reload failed. Please check configuration manually.${NC}"
        echo -e "${GREEN}[✓] Nginx proxy set up for grafana.verdischain.com -> http://127.0.0.1:3000${NC}"
        echo -e "${BLUE}[i] To enable HTTPS, run: certbot --nginx -d grafana.verdischain.com${NC}"
    fi
else
    echo -e "${YELLOW}[!] Nginx not detected. Skipping reverse proxy setup.${NC}"
fi

echo -e "\n${BOLD}${GREEN}====================================================${NC}"
echo -e "${BOLD}${GREEN}   Verdis Monitoring Stack Successfully Installed!  ${NC}"
echo -e "${BOLD}${GREEN}====================================================${NC}"
echo -e "Access Endpoints:"
echo -e "  - Prometheus:    http://91.98.160.145:9090"
echo -e "  - Grafana:       http://91.98.160.145:3000 (or http://grafana.verdischain.com)"
echo -e "  - Alertmanager:  http://91.98.160.145:9093"
echo -e "  - Node Exporter: http://91.98.160.145:9100"
echo -e "\nGrafana Credentials:"
echo -e "  - Username: ${GRAFANA_ADMIN_USER}"
echo -e "  - Password: ${GRAFANA_ADMIN_PASS}"
echo -e "===================================================="
