#!/usr/bin/env bash
#
# Verdis Chain — Air-Gapped Validator Key Generation Ceremony
#
# PURPOSE: Generate 21 production validator keypairs + 5 cold-storage multisig keys
#          in a fully air-gapped environment. No network connections. No internet.
#
# PREREQUISITES:
#   1. A dedicated air-gapped machine (no WiFi, no Ethernet, no Bluetooth)
#   2. Substrate keyring utility installed (subkey) OR the verdis-node binary
#   3. Two USB drives (one for input verification, one for output keys)
#   4. This script copied to the air-gapped machine via USB
#   5. A printer or secure display for mnemonic phrases
#
# SECURITY:
#   - All keys are generated locally, never transmitted
#   - Mnemonic phrases are displayed once and must be written down physically
#   - Public keys are saved to USB for import into the chain spec
#   - Private keys / mnemonics NEVER leave the air-gapped machine
#
# OUTPUT:
#   - /output/validator-keys.json: 21 validator public keys (for chain spec)
#   - /output/multisig-keys.json: 5 cold-storage public keys + computed multisig address
#   - /output/ceremony-log.txt: Audit log (no secrets)
#   - Physical paper backups of all mnemonic phrases (operator responsibility)
#
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/output"
LOG_FILE="${OUTPUT_DIR}/ceremony-log.txt"

mkdir -p "$OUTPUT_DIR"

header() {
    echo ""
    echo "================================================================"
    echo " $1"
    echo "================================================================"
    echo ""
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] STEP: $1" | tee -a "$LOG_FILE"
}

warning() {
    echo "WARNING: $1"
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] WARNING: $1" | tee -a "$LOG_FILE"
}

success() {
    echo "OK: $1"
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] SUCCESS: $1" | tee -a "$LOG_FILE"
}

error() {
    echo "ERROR: $1"
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] ERROR: $1" | tee -a "$LOG_FILE"
    exit 1
}

# ============================================================================

header "VERDIS CHAIN — AIR-GAPPED KEY CEREMONY"

# Verify air-gapped
echo "Verifying air-gapped environment..."
if ip link 2>/dev/null | grep -E "state (UP|UNKNOWN)" | grep -v "lo:" | grep -q .; then
    warning "Network interface detected! This machine may not be air-gapped."
    echo "Disable all network interfaces before continuing."
    read -p "Type 'I-UNDERSTAND' to proceed anyway: " confirm
    [ "$confirm" = "I-UNDERSTAND" ] || error "Aborted by operator"
else
    success "No active network interfaces detected — air-gapped confirmed"
fi

# Check for subkey or node binary
SUBKEY=""
if command -v subkey &>/dev/null; then
    SUBKEY="subkey"
    success "Found subkey utility"
elif [ -f "/usr/local/bin/verdis-node" ]; then
    SUBKEY="/usr/local/bin/verdis-node key"
    success "Found verdis-node binary"
elif [ -f "$SCRIPT_DIR/../target/release/verdis-node" ]; then
    SUBKEY="$SCRIPT_DIR/../target/release/verdis-node key"
    success "Found verdis-node in build directory"
else
    error "Neither subkey nor verdis-node found. Install subkey: cargo install subkey --locked"
fi

# ============================================================================

header "STEP 1: GENERATE 21 PRODUCTION VALIDATOR KEYS"

VALIDATOR_KEYS_FILE="$OUTPUT_DIR/validator-keys.json"
echo "[" > "$VALIDATOR_KEYS_FILE"

for i in $(seq 1 21); do
    echo ""
    echo "--- Validator $i of 21 ---"
    echo ""

    # Generate sr25519 keypair (for Babe/Session)
    SR_OUTPUT=$($SUBKEY generate --scheme sr25519 --network 42 2>&1)
    SR_SECRET=$(echo "$SR_OUTPUT" | grep "Secret seed:" | awk '{print $3}')
    SR_PUBLIC=$(echo "$SR_OUTPUT" | grep "Public key (hex):" | awk '{print $4}')
    SR_ADDRESS=$(echo "$SR_OUTPUT" | grep "SS58 Address:" | awk '{print $3}')
    SR_MNEMONIC=$(echo "$SR_OUTPUT" | grep "Secret phrase:" | sed 's/Secret phrase: *//')

    # Generate ed25519 keypair (for Grandpa)
    ED_OUTPUT=$($SUBKEY generate --scheme ed25519 --network 42 2>&1)
    ED_SECRET=$(echo "$ED_OUTPUT" | grep "Secret seed:" | awk '{print $3}')
    ED_PUBLIC=$(echo "$ED_OUTPUT" | grep "Public key (hex):" | awk '{print $4}')
    ED_ADDRESS=$(echo "$ED_OUTPUT" | grep "SS58 Address:" | awk '{print $3}')
    ED_MNEMONIC=$(echo "$ED_OUTPUT" | grep "Secret phrase:" | sed 's/Secret phrase: *//')

    # Display mnemonics for physical backup
    echo "  Validator $i:"
    echo "    sr25519 (Babe/Session):"
    echo "      Address: $SR_ADDRESS"
    echo "      Mnemonic: $SR_MNEMONIC"
    echo ""
    echo "    ed25519 (Grandpa):"
    echo "      Address: $ED_ADDRESS"
    echo "      Mnemonic: $ED_MNEMONIC"
    echo ""
    warning "Write down BOTH mnemonics on paper. Store in separate secure locations."
    read -p "  Press ENTER after backing up validator $i mnemonics..."

    # Save public keys to JSON (no secrets!)
    COMMA=$([ $i -lt 21 ] && echo "," || echo "")
    cat >> "$VALIDATOR_KEYS_FILE" <<EOF
  {
    "validator_id": $i,
    "sr25519": {
      "address": "$SR_ADDRESS",
      "public_key_hex": "$SR_PUBLIC"
    },
    "ed25519": {
      "address": "$ED_ADDRESS",
      "public_key_hex": "$ED_PUBLIC"
    }
  }$COMMA
EOF

    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Generated validator $i: sr25519=$SR_ADDRESS ed25519=$ED_ADDRESS" | tee -a "$LOG_FILE"
    success "Validator $i keys generated and backed up"
done

echo "]" >> "$VALIDATOR_KEYS_FILE"
success "All 21 validator keys generated"

# ============================================================================

header "STEP 2: GENERATE 5 COLD-STORAGE MULTISIG KEYS"

MULTISIG_KEYS_FILE="$OUTPUT_DIR/multisig-keys.json"
echo "[" > "$MULTISIG_KEYS_FILE"

for i in $(seq 1 5); do
    echo ""
    echo "--- Cold Storage Key $i of 5 ---"
    echo ""

    CS_OUTPUT=$($SUBKEY generate --scheme sr25519 --network 42 2>&1)
    CS_PUBLIC=$(echo "$CS_OUTPUT" | grep "Public key (hex):" | awk '{print $4}')
    CS_ADDRESS=$(echo "$CS_OUTPUT" | grep "SS58 Address:" | awk '{print $3}')
    CS_MNEMONIC=$(echo "$CS_OUTPUT" | grep "Secret phrase:" | sed 's/Secret phrase: *//')

    echo "  Cold Storage Key $i:"
    echo "    Address: $CS_ADDRESS"
    echo "    Mnemonic: $CS_MNEMONIC"
    echo ""
    warning "Write down this mnemonic on paper. Store in a separate secure location."
    warning "This is one of 5 keys that control the team treasury (3-of-5 required)."
    read -p "  Press ENTER after backing up cold storage key $i..."

    COMMA=$([ $i -lt 5 ] && echo "," || echo "")
    cat >> "$MULTISIG_KEYS_FILE" <<EOF
  {
    "key_id": $i,
    "address": "$CS_ADDRESS",
    "public_key_hex": "$CS_PUBLIC"
  }$COMMA
EOF

    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Generated cold storage key $i: $CS_ADDRESS" | tee -a "$LOG_FILE"
    success "Cold storage key $i generated and backed up"
done

echo "]" >> "$MULTISIG_KEYS_FILE"
success "All 5 cold storage keys generated"

# ============================================================================

header "STEP 3: COMPUTE 3-OF-5 MULTISIG ADDRESS"

echo "Computing 3-of-5 multisig address from cold storage public keys..."
echo ""
echo "The multisig address will be computed when importing keys into the chain spec."
echo "Use the following formula with pallet-multisig:"
echo "  multisig_address = AccountId32(blake2_256(threshold ++ sorted_signatories))"
echo ""
echo "Or use the verdis-node utility (if available):"
echo "  verdis-node key multisig --threshold 3 --signatories <addr1>,<addr2>,<addr3>,<addr4>,<addr5>"
echo ""
warning "The multisig address replaces PalletId(*b'verdistm') in the mainnet chain spec."
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Multisig address computation deferred to chain spec import" | tee -a "$LOG_FILE"

# ============================================================================

header "STEP 4: GENERATE CHECKSUMS"

CHECKSUM_FILE="$OUTPUT_DIR/ceremony-checksums.txt"
cd "$OUTPUT_DIR"
sha256sum validator-keys.json multisig-keys.json > "$CHECKSUM_FILE"
cd "$SCRIPT_DIR"
success "Checksums generated: $CHECKSUM_FILE"

# ============================================================================

header "CEREMONY COMPLETE"

echo ""
echo "Output files in: $OUTPUT_DIR/"
echo "  - validator-keys.json    (21 validator public keys — NO SECRETS)"
echo "  - multisig-keys.json     (5 cold-storage public keys — NO SECRETS)"
echo "  - ceremony-checksums.txt (SHA-256 checksums for verification)"
echo "  - ceremony-log.txt       (Audit log — NO SECRETS)"
echo ""
warning "IMPORTANT: All mnemonic phrases must be on physical paper only."
warning "Do NOT save mnemonics electronically. Do NOT connect USB drives to internet-connected machines."
warning "Distribute paper backups to 5 separate secure locations."
echo ""
echo "Next steps:"
echo "  1. Copy output/ to USB drive"
echo "  2. Import validator-keys.json into chain spec (replace placeholder keys)"
echo "  3. Import multisig-keys.json into chain spec (replace PalletId team account)"
echo "  4. Build the chain spec and verify genesis hash"
echo "  5. Distribute chain spec to all 21 validator operators"
echo ""
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Ceremony completed successfully" | tee -a "$LOG_FILE"
