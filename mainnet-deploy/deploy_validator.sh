#!/usr/bin/env bash
# ==============================================================================
# Verdis Chain Mainnet Validator Deployment Script
# ==============================================================================
# Usage:
#   ./deploy_validator.sh <SERVER_IP> <SSH_KEY_PATH> <VALIDATOR_NAME> <VALIDATOR_INDEX>
#
# Parameters:
#   SERVER_IP       : IP address of the target deployment host
#   SSH_KEY_PATH    : Local path to the SSH private key for root/sudo access
#   VALIDATOR_NAME  : Human-readable moniker for the validator node (e.g. verdis-val-nl-0)
#   VALIDATOR_INDEX : Numeric index (0 to 20) assigned to this validator instance
# ==============================================================================

set -euo pipefail

# Color definitions for console output
RED='\030[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ------------------------------------------------------------------------------
# Argument Validation & Helper Function
# ------------------------------------------------------------------------------
usage() {
    echo -e "Usage: $0 <SERVER_IP> <SSH_KEY_PATH> <VALIDATOR_NAME> <VALIDATOR_INDEX>"
    echo -e "Example: $0 185.220.101.5 ~/.ssh/verdis_mainnet verdis-val-nl-0 0"
    exit 1
}

if [ "$#" -ne 4 ]; then
    log_error "Invalid number of arguments."
    usage
fi

SERVER_IP="$1"
SSH_KEY_PATH="$2"
VALIDATOR_NAME="$3"
VALIDATOR_INDEX="$4"

# Validate index is integer between 0 and 20
if ! [[ "$VALIDATOR_INDEX" =~ ^[0-9]+$ ]] || [ "$VALIDATOR_INDEX" -lt 0 ] || [ "$VALIDATOR_INDEX" -gt 20 ]; then
    log_error "VALIDATOR_INDEX must be an integer between 0 and 20."
    exit 1
fi

if [ ! -f "$SSH_KEY_PATH" ]; then
    log_error "SSH key file not found at path: $SSH_KEY_PATH"
    exit 1
fi

# Calculate dynamic ports based on VALIDATOR_INDEX
BASE_P2P_PORT=30333
BASE_RPC_PORT=9944
BASE_PROM_PORT=9615

P2P_PORT=$((BASE_P2P_PORT + VALIDATOR_INDEX))
RPC_PORT=$((BASE_RPC_PORT + VALIDATOR_INDEX))
PROM_PORT=$((BASE_PROM_PORT + VALIDATOR_INDEX))

REPO_URL="https://github.com/Protremix/Verdischain-.git"
TARGET_DIR="/opt/verdis-chain-rust"
BOOTNODE_ADDR="/ip4/91.98.160.145/tcp/30333/p2p/12D3KooWBootNodeTestnetServerVerdisChainMainnet"

SSH_CMD="ssh -i $SSH_KEY_PATH -o StrictHostKeyChecking=no -o ConnectTimeout=10 root@$SERVER_IP"

log_info "------------------------------------------------------------"
log_info "Initiating deployment for Validator #${VALIDATOR_INDEX} (${VALIDATOR_NAME})"
log_info "Target Server IP   : ${SERVER_IP}"
log_info "Assigned P2P Port  : ${P2P_PORT}"
log_info "Assigned RPC Port  : ${RPC_PORT}"
log_info "Assigned Prom Port : ${PROM_PORT}"
log_info "------------------------------------------------------------"

# ------------------------------------------------------------------------------
# Step 1: Connectivity Check
# ------------------------------------------------------------------------------
log_info "Step 1: Testing SSH connection to ${SERVER_IP}..."
if ! $SSH_CMD "echo 'SSH Connection Established'" > /dev/null 2>&1; then
    log_error "Failed to connect to root@${SERVER_IP} using key ${SSH_KEY_PATH}."
    exit 1
fi
log_success "SSH Connection verified."

# ------------------------------------------------------------------------------
# Step 2: System Dependencies & Rust Toolchain Installation
# ------------------------------------------------------------------------------
log_info "Step 2: Installing system dependencies and Rust toolchain on target server..."
$SSH_CMD << 'EOF'
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y --no-install-recommends \
    build-essential \
    clang \
    cmake \
    pkg-config \
    libssl-dev \
    git \
    curl \
    jq \
    protobuf-compiler \
    ufw \
    ca-certificates

if ! command -v rustc &> /dev/null; then
    echo "Installing Rust toolchain..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
    source $HOME/.cargo/env
else
    echo "Rust is already installed: $(rustc --version)"
fi

source $HOME/.cargo/env
rustup update stable
rustup target add wasm32-unknown-unknown --toolchain stable
EOF
log_success "Dependencies and Rust toolchain configured."

# ------------------------------------------------------------------------------
# Step 3: Repository Setup & Code Compilation
# ------------------------------------------------------------------------------
log_info "Step 3: Synchronizing repository and building node binary (cargo build --release -p verdis-chain)..."
$SSH_CMD << EOF
set -euo pipefail
source \$HOME/.cargo/env

if [ ! -d "${TARGET_DIR}" ]; then
    echo "Cloning repository from ${REPO_URL} into ${TARGET_DIR}..."
    git clone ${REPO_URL} ${TARGET_DIR}
else
    echo "Updating repository in ${TARGET_DIR}..."
    cd ${TARGET_DIR}
    git fetch --all
    git reset --hard origin/main || git reset --hard origin/master
fi

cd ${TARGET_DIR}
echo "Compiling verdis-chain release binary..."
cargo build --release -p verdis-chain
EOF
log_success "Node binary compiled successfully."

# ------------------------------------------------------------------------------
# Step 4: Chain Spec Setup
# ------------------------------------------------------------------------------
log_info "Step 4: Ensuring mainnet chain specification is present..."
$SSH_CMD << EOF
set -euo pipefail
mkdir -p ${TARGET_DIR}/chain-specs
if [ ! -f "${TARGET_DIR}/chain-specs/mainnet-raw.json" ]; then
    if [ -f "${TARGET_DIR}/chain-specs/mainnet.json" ]; then
        echo "Building raw chain spec from mainnet.json..."
        ${TARGET_DIR}/target/release/verdis-chain build-spec --chain=${TARGET_DIR}/chain-specs/mainnet.json --raw > ${TARGET_DIR}/chain-specs/mainnet-raw.json
    elif [ -f "${TARGET_DIR}/chain-specs/testnet.json" ]; then
        echo "Warning: mainnet.json not found, backing up testnet spec as fallback mainnet-raw.json template..."
        cp ${TARGET_DIR}/chain-specs/testnet.json ${TARGET_DIR}/chain-specs/mainnet-raw.json
    else
        echo "Error: No valid chain spec template found in ${TARGET_DIR}/chain-specs"
        exit 1
    fi
fi
EOF
log_success "Chain specification initialized."

# ------------------------------------------------------------------------------
# Step 5: Service Configuration & Sandboxed Environment Setup
# ------------------------------------------------------------------------------
log_info "Step 5: Configuring systemd service, verdis user, and directory structure..."

# Copy service file template
LOCAL_SERVICE_FILE="$(dirname "$0")/verdis-validator@.service"
if [ -f "$LOCAL_SERVICE_FILE" ]; then
    scp -i "$SSH_KEY_PATH" "$LOCAL_SERVICE_FILE" root@"$SERVER_IP":/etc/systemd/system/verdis-validator@.service
else
    log_warn "Local service file ${LOCAL_SERVICE_FILE} not found; generating on host."
fi

$SSH_CMD << EOF
set -euo pipefail

# Create dedicated unprivileged system user if not existing
if ! id -u verdis >/dev/null 2>&1; then
    useradd -rs /bin/false verdis
fi

# Prepare environment directory
mkdir -p /etc/verdis-validator
mkdir -p /var/lib/verdis-chain/validator-${VALIDATOR_INDEX}
chown -R verdis:verdis /var/lib/verdis-chain/validator-${VALIDATOR_INDEX}

# Write environment file for this validator instance
cat << ENVFILE > /etc/verdis-validator/validator-${VALIDATOR_INDEX}.env
VALIDATOR_NAME="${VALIDATOR_NAME}"
VALIDATOR_INDEX="${VALIDATOR_INDEX}"
P2P_PORT="${P2P_PORT}"
RPC_PORT="${RPC_PORT}"
PROM_PORT="${PROM_PORT}"
CHAIN_SPEC="${TARGET_DIR}/chain-specs/mainnet-raw.json"
BASE_PATH="/var/lib/verdis-chain/validator-${VALIDATOR_INDEX}"
BOOTNODES="${BOOTNODE_ADDR}"
ENVFILE

chmod 600 /etc/verdis-validator/validator-${VALIDATOR_INDEX}.env
chown verdis:verdis /etc/verdis-validator/validator-${VALIDATOR_INDEX}.env

# UFW Firewall configuration
ufw allow ${P2P_PORT}/tcp comment "Verdis Validator #${VALIDATOR_INDEX} P2P"
ufw --force enable || true

systemctl daemon-reload
EOF
log_success "Environment and service definitions deployed."

# ------------------------------------------------------------------------------
# Step 6: Service Start & RPC Readiness Check
# ------------------------------------------------------------------------------
log_info "Step 6: Starting verdis-validator@${VALIDATOR_INDEX} service..."
$SSH_CMD << EOF
set -euo pipefail
systemctl enable verdis-validator@${VALIDATOR_INDEX}
systemctl restart verdis-validator@${VALIDATOR_INDEX}

echo "Waiting for RPC endpoint (127.0.0.1:${RPC_PORT}) to respond..."
MAX_ATTEMPTS=30
ATTEMPT=0
while [ \$ATTEMPT -lt \$MAX_ATTEMPTS ]; do
    if curl -s -H "Content-Type: application/json" -d '{"id":1, "jsonrpc":"2.0", "method":"system_health", "params":[]}' http://127.0.0.1:${RPC_PORT} > /dev/null 2>&1; then
        echo "RPC Endpoint is live and healthy."
        break
    fi
    ATTEMPT=\$((ATTEMPT + 1))
    sleep 2
done

if [ \$ATTEMPT -eq \$MAX_ATTEMPTS ]; then
    echo "Error: Validator service failed to start or RPC timed out."
    journalctl -u verdis-validator@${VALIDATOR_INDEX} --no-pager -n 30
    exit 1
fi
EOF
log_success "Validator node #${VALIDATOR_INDEX} is active and responding on RPC."

# ------------------------------------------------------------------------------
# Step 7: Session Key Generation (author_rotateKeys)
# ------------------------------------------------------------------------------
log_info "Step 7: Executing author_rotateKeys RPC call to generate session keys..."
SESSION_KEYS_OUTPUT=$($SSH_CMD << EOF
set -euo pipefail
ROTATION_RESPONSE=\$(curl -s -H "Content-Type: application/json" \
    --data '{"id":1, "jsonrpc":"2.0", "method":"author_rotateKeys", "params":[]}' \
    http://127.0.0.1:${RPC_PORT})

KEYS=\$(echo "\$ROTATION_RESPONSE" | jq -r '.result // empty')

if [ -z "\$KEYS" ] || [ "\$KEYS" == "null" ]; then
    echo "ERROR: Failed to rotate keys. Response: \$ROTATION_RESPONSE"
    exit 1
fi

echo "\$KEYS" > /etc/verdis-validator/session-key-${VALIDATOR_INDEX}.pub
chown verdis:verdis /etc/verdis-validator/session-key-${VALIDATOR_INDEX}.pub
echo "\$KEYS"
EOF
)

log_success "Session keys generated successfully!"
echo "================================================================================"
echo "                      VALIDATOR DEPLOYMENT SUMMARY                              "
echo "================================================================================"
echo " Server IP        : ${SERVER_IP}"
echo " Validator Moniker: ${VALIDATOR_NAME}"
echo " Validator Index  : ${VALIDATOR_INDEX}"
echo " P2P Port         : ${P2P_PORT}"
echo " RPC Port         : ${RPC_PORT}"
echo " Prometheus Port  : ${PROM_PORT}"
echo " Generated Keys   : ${SESSION_KEYS_OUTPUT}"
echo " Key File Path    : /etc/verdis-validator/session-key-${VALIDATOR_INDEX}.pub"
echo "================================================================================"
echo "IMPORTANT: Submit the generated session keys above to the Key Ceremony Master"
echo "for inclusion in the genesis spec or set_keys transaction."
echo "================================================================================"
