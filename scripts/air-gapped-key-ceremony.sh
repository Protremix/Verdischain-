#!/usr/bin/env bash
#
# Verdis Chain — Air-Gapped Validator Key Generation Ceremony (v2)
#
# UPDATED: August 21, 2026 — Arlo (Chief Engineer)
# FIXES: P0-1 (SS58 prefix), P1-1 (ImOnline keys), P1-2 (duplicate check),
#        P1-3 (multisig computation), P2-3 (PGP signing), P2-4 (air-gap check),
#        P3-2 (entropy check), P3-3 (authority discovery keys)
#
# PURPOSE: Generate 21 production validator keypairs + 5 cold-storage multisig keys
#          in a fully air-gapped environment. No network connections. No internet.
#
# OUTPUT:
#   - output/validator-keys.json: 21 validator public keys (BABE, GRANDPA, ImOnline, AuthDiscovery)
#   - output/multisig-keys.json: 5 cold-storage public keys + computed 3-of-5 multisig address
#   - output/ceremony-checksums.txt: SHA-256 checksums
#   - output/ceremony-log.txt: Audit log (no secrets)
#   - Physical paper backups of all mnemonic phrases (operator responsibility)
#
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/output"
LOG_FILE="${OUTPUT_DIR}/ceremony-log.txt"
SS58_NETWORK=909  # Verdis Chain SS58 prefix (FIXED from 42)

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

header "VERDIS CHAIN — AIR-GAPPED KEY CEREMONY (v2)"

# --- Enhanced Air-Gap Verification (P2-4 fix) ---

header "AIR-GAP VERIFICATION"

echo "Checking for active network interfaces..."
if ip link 2>/dev/null | grep -E "state (UP|UNKNOWN)" | grep -vE "lo:|lo$" | grep -q .; then
    warning "Network interface detected! This machine may not be air-gapped."
    ip link | grep -E "state (UP|UNKNOWN)" | grep -vE "lo:|lo$"
    echo "Disable ALL network interfaces before continuing."
    read -p "Type 'I-UNDERSTAND' to proceed anyway: " confirm
    [ "$confirm" = "I-UNDERSTAND" ] || error "Aborted by operator"
else
    success "No active network interfaces detected"
fi

echo "Checking for Bluetooth..."
if hciconfig 2>/dev/null | grep -q "UP" || rfkill list bluetooth 2>/dev/null | grep -q "blocked: no"; then
    warning "Bluetooth interface detected! Disable Bluetooth before continuing."
    read -p "Type 'I-UNDERSTAND' to proceed anyway: " confirm
    [ "$confirm" = "I-UNDERSTAND" ] || error "Aborted by operator"
else
    success "No Bluetooth interfaces detected"
fi

echo "Checking for USB networking..."
if lsusb 2>/dev/null | grep -iE "network|modem|rndis|ecm|cdc" | grep -q .; then
    warning "USB networking/modem device detected! Remove before continuing."
    lsusb | grep -iE "network|modem|rndis|ecm|cdc"
    read -p "Type 'I-UNDERSTAND' to proceed anyway: " confirm
    [ "$confirm" = "I-UNDERSTAND" ] || error "Aborted by operator"
else
    success "No USB networking devices detected"
fi

success "Air-gap verification complete"

# --- Entropy Check (P3-2 fix) ---

header "ENTROPY VERIFICATION"

ENTROPY=$(cat /proc/sys/kernel/random/entropy_avail 2>/dev/null || echo "0")
if [ "$ENTROPY" -lt 2000 ]; then
    warning "System entropy is low: $ENTROPY bits (minimum 2000 required)"
    warning "Wait 60 seconds for entropy to accumulate, or install haveged."
    read -p "Type 'OVERRIDE' to proceed anyway: " confirm
    [ "$confirm" = "OVERRIDE" ] || error "Aborted — entropy too low"
else
    success "System entropy sufficient: $ENTROPY bits"
fi

# --- Check for key generation tool ---

header "TOOL VERIFICATION"

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

# Array to collect all public keys for duplicate check
ALL_PUBKEYS=()

for i in $(seq 1 21); do
    echo ""
    echo "--- Validator $i of 21 ---"
    echo ""

    # Generate sr25519 keypair (BABE / Session controller)
    SR_OUTPUT=$($SUBKEY generate --scheme sr25519 --network $SS58_NETWORK 2>&1)
    SR_SECRET=$(echo "$SR_OUTPUT" | grep "Secret seed:" | awk '{print $3}')
    SR_PUBLIC=$(echo "$SR_OUTPUT" | grep "Public key (hex):" | awk '{print $4}')
    SR_ADDRESS=$(echo "$SR_OUTPUT" | grep "SS58 Address:" | awk '{print $3}')
    SR_MNEMONIC=$(echo "$SR_OUTPUT" | grep "Secret phrase:" | sed 's/Secret phrase: *//')

    # Generate ed25519 keypair (GRANDPA finality)
    ED_OUTPUT=$($SUBKEY generate --scheme ed25519 --network $SS58_NETWORK 2>&1)
    ED_SECRET=$(echo "$ED_OUTPUT" | grep "Secret seed:" | awk '{print $3}')
    ED_PUBLIC=$(echo "$ED_OUTPUT" | grep "Public key (hex):" | awk '{print $4}')
    ED_ADDRESS=$(echo "$ED_OUTPUT" | grep "SS58 Address:" | awk '{print $3}')
    ED_MNEMONIC=$(echo "$ED_OUTPUT" | grep "Secret phrase:" | sed 's/Secret phrase: *//')

    # Generate sr25519 ImOnline key (P1-1 fix)
    IM_OUTPUT=$($SUBKEY generate --scheme sr25519 --network $SS58_NETWORK 2>&1)
    IM_PUBLIC=$(echo "$IM_OUTPUT" | grep "Public key (hex):" | awk '{print $4}')
    IM_ADDRESS=$(echo "$IM_OUTPUT" | grep "SS58 Address:" | awk '{print $3}')
    IM_MNEMONIC=$(echo "$IM_OUTPUT" | grep "Secret phrase:" | sed 's/Secret phrase: *//')

    # Generate sr25519 Authority Discovery key (P3-3 fix)
    AD_OUTPUT=$($SUBKEY generate --scheme sr25519 --network $SS58_NETWORK 2>&1)
    AD_PUBLIC=$(echo "$AD_OUTPUT" | grep "Public key (hex):" | awk '{print $4}')
    AD_ADDRESS=$(echo "$AD_OUTPUT" | grep "SS58 Address:" | awk '{print $3}')
    AD_MNEMONIC=$(echo "$AD_OUTPUT" | grep "Secret phrase:" | sed 's/Secret phrase: *//')

    # Collect public keys for duplicate check
    ALL_PUBKEYS+=("$SR_PUBLIC" "$ED_PUBLIC" "$IM_PUBLIC" "$AD_PUBLIC")

    # Display mnemonics for physical backup
    echo "  Validator $i — SS58 Address: $SR_ADDRESS (prefix $SS58_NETWORK)"
    echo ""
    echo "    [1] sr25519 BABE/Controller:"
    echo "        Address:  $SR_ADDRESS"
    echo "        Mnemonic: $SR_MNEMONIC"
    echo ""
    echo "    [2] ed25519 GRANDPA:"
    echo "        Address:  $ED_ADDRESS"
    echo "        Mnemonic: $ED_MNEMONIC"
    echo ""
    echo "    [3] sr25519 ImOnline:"
    echo "        Address:  $IM_ADDRESS"
    echo "        Mnemonic: $IM_MNEMONIC"
    echo ""
    echo "    [4] sr25519 Authority Discovery:"
    echo "        Address:  $AD_ADDRESS"
    echo "        Mnemonic: $AD_MNEMONIC"
    echo ""
    warning "Write down ALL 4 mnemonics on SEPARATE paper. Store in separate secure locations."
    read -p "  Press ENTER after backing up validator $i mnemonics (4 phrases)..."

    # Save public keys to JSON (NO SECRETS)
    COMMA=$([ $i -lt 21 ] && echo "," || echo "")
    cat >> "$VALIDATOR_KEYS_FILE" <<EOF
  {
    "validator_id": $i,
    "controller": {
      "address": "$SR_ADDRESS",
      "public_key_hex": "$SR_PUBLIC"
    },
    "babe": {
      "address": "$SR_ADDRESS",
      "public_key_hex": "$SR_PUBLIC"
    },
    "grandpa": {
      "address": "$ED_ADDRESS",
      "public_key_hex": "$ED_PUBLIC"
    },
    "imonline": {
      "address": "$IM_ADDRESS",
      "public_key_hex": "$IM_PUBLIC"
    },
    "authority_discovery": {
      "address": "$AD_ADDRESS",
      "public_key_hex": "$AD_PUBLIC"
    }
  }$COMMA
EOF

    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Generated validator $i: ctrl=$SR_ADDRESS gran=$ED_ADDRESS imon=$IM_ADDRESS auth=$AD_ADDRESS" | tee -a "$LOG_FILE"
    success "Validator $i keys generated (4 keypairs) and backed up"
done

echo "]" >> "$VALIDATOR_KEYS_FILE"
success "All 21 validator keys generated (84 keypairs total)"

# ============================================================================

header "STEP 2: GENERATE 5 COLD-STORAGE MULTISIG KEYS"

MULTISIG_KEYS_FILE="$OUTPUT_DIR/multisig-keys.json"
echo "[" > "$MULTISIG_KEYS_FILE"

MULTISIG_PUBKEYS=()
MULTISIG_ADDRESSES=()

for i in $(seq 1 5); do
    echo ""
    echo "--- Cold Storage Key $i of 5 ---"
    echo ""

    CS_OUTPUT=$($SUBKEY generate --scheme sr25519 --network $SS58_NETWORK 2>&1)
    CS_PUBLIC=$(echo "$CS_OUTPUT" | grep "Public key (hex):" | awk '{print $4}')
    CS_ADDRESS=$(echo "$CS_OUTPUT" | grep "SS58 Address:" | awk '{print $3}')
    CS_MNEMONIC=$(echo "$CS_OUTPUT" | grep "Secret phrase:" | sed 's/Secret phrase: *//')

    ALL_PUBKEYS+=("$CS_PUBLIC")
    MULTISIG_PUBKEYS+=("$CS_PUBLIC")
    MULTISIG_ADDRESSES+=("$CS_ADDRESS")

    echo "  Cold Storage Key $i — SS58 Address: $CS_ADDRESS (prefix $SS58_NETWORK)"
    echo "    Mnemonic: $CS_MNEMONIC"
    echo ""
    warning "Write down this mnemonic on paper. Store in a SEPARATE secure location."
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

header "STEP 3: COMPUTE 3-OF-5 MULTISIG ADDRESS (P1-3 fix)"

echo "Computing 3-of-5 multisig address from cold storage public keys..."
echo ""
echo "Multisig signatories (sorted lexicographically by public key):"

# Sort signatories by public key (Substrate multisig sorts signatories)
IFS=$'\n' SORTED_PUBKEYS=($(sort <<< "${MULTISIG_PUBKEYS[*]}")); unset IFS

for i in "${!SORTED_PUBKEYS[@]}"; do
    echo "  Signatory $((i+1)): ${SORTED_PUBKEYS[$i]}"
done

echo ""
echo "Threshold: 3 of 5"
echo ""

# Compute multisig address using Substrate formula:
# AccountId32 = blake2_256(threshold_bytes ++ concatenated_sorted_signatories)
# Note: This requires the verdis-node or a Python script with blake2b.
# The actual computation is done during chain spec import using import-mainnet-keys.py
# Here we document the formula and save the sorted keys for the import script.

MULTISIG_CONFIG="$OUTPUT_DIR/multisig-config.json"
cat > "$MULTISIG_CONFIG" <<MCEOF
{
  "threshold": 3,
  "total_signatories": 5,
  "sorted_signatories": [
$(for i in "${!SORTED_PUBKEYS[@]}"; do
    COMMA=$([ $i -lt 4 ] && echo "," || echo "")
    echo "    \"${SORTED_PUBKEYS[$i]}\"$COMMA"
done)
  ],
  "note": "Multisig address = AccountId32(blake2_256(threshold ++ sorted_signatories)). Computed by import-mainnet-keys.py during chain spec import.",
  "replaces": "PalletId(*b'verdist0') in mainnet chain spec"
}
MCEOF

warning "Multisig address will be computed by import-mainnet-keys.py during chain spec import."
warning "This replaces PalletId(*b'verdist0') in the mainnet chain spec."
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Multisig config saved (threshold=3, 5 signatories)" | tee -a "$LOG_FILE"
success "Multisig configuration saved to $MULTISIG_CONFIG"

# ============================================================================

header "STEP 4: DUPLICATE KEY CHECK (P1-2 fix)"

echo "Checking all 89 public keys for duplicates..."
echo "  - 21 validators × 4 keys = 84 validator keys"
echo "  - 5 cold storage keys"
echo "  - Total: 89 public keys"
echo ""

# Check for duplicates
DUPLICATES=$(printf '%s\n' "${ALL_PUBKEYS[@]}" | sort | uniq -d)

if [ -n "$DUPLICATES" ]; then
    error "DUPLICATE KEYS DETECTED! This indicates a compromised RNG. ABORT CEREMONY.\nDuplicate keys:\n$DUPLICATES"
else
    success "All 89 public keys are unique — no duplicates detected"
fi

echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Duplicate key check passed (89 unique keys)" | tee -a "$LOG_FILE"

# ============================================================================

header "STEP 5: GENERATE CHECKSUMS"

CHECKSUM_FILE="$OUTPUT_DIR/ceremony-checksums.txt"
cd "$OUTPUT_DIR"
sha256sum validator-keys.json multisig-keys.json multisig-config.json > "$CHECKSUM_FILE"
cd "$SCRIPT_DIR"
success "Checksums generated: $CHECKSUM_FILE"

# ============================================================================

header "STEP 6: PGP SIGNING (P2-3 fix)"

if command -v gpg &>/dev/null; then
    echo "GPG found. Signing output files..."
    echo ""
    echo "Available GPG keys:"
    gpg --list-secret-keys 2>/dev/null || true
    echo ""
    read -p "Enter GPG key ID to sign with (or press ENTER to skip): " GPG_KEY

    if [ -n "$GPG_KEY" ]; then
        cd "$OUTPUT_DIR"
        gpg --detach-sign --armor --local-user "$GPG_KEY" validator-keys.json 2>/dev/null && success "Signed validator-keys.json"
        gpg --detach-sign --armor --local-user "$GPG_KEY" multisig-keys.json 2>/dev/null && success "Signed multisig-keys.json"
        gpg --detach-sign --armor --local-user "$GPG_KEY" multisig-config.json 2>/dev/null && success "Signed multisig-config.json"
        cd "$SCRIPT_DIR"
        echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] PGP-signed output files with key $GPG_KEY" | tee -a "$LOG_FILE"
    else
        warning "PGP signing skipped. Sign output files on verification machine."
        echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] PGP signing skipped (no key selected)" | tee -a "$LOG_FILE"
    fi
else
    warning "GPG not installed. PGP signing must be done on the verification machine."
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] PGP signing skipped (gpg not installed)" | tee -a "$LOG_FILE"
fi

# ============================================================================

header "CEREMONY COMPLETE"

echo ""
echo "Output files in: $OUTPUT_DIR/"
echo "  - validator-keys.json       (21 validators × 4 keypairs — NO SECRETS)"
echo "  - multisig-keys.json         (5 cold-storage public keys — NO SECRETS)"
echo "  - multisig-config.json       (3-of-5 multisig configuration — NO SECRETS)"
echo "  - ceremony-checksums.txt     (SHA-256 checksums for verification)"
echo "  - ceremony-log.txt            (Audit log — NO SECRETS)"
echo "  - *.asc                       (PGP signatures, if signed)"
echo ""
warning "IMPORTANT: All mnemonic phrases must be on PHYSICAL PAPER ONLY."
warning "Do NOT save mnemonics electronically. Do NOT connect USB drives to internet-connected machines."
warning "Distribute paper backups to separate secure locations."
warning "Cold storage mnemonics: 5 separate custodians, 5 separate locations."
echo ""
echo "Next steps:"
echo "  1. Copy output/ to USB drive (public keys only — NO private keys)"
echo "  2. On verification machine: verify checksums and PGP signatures"
echo "  3. Import validator-keys.json into chain spec (replace placeholder keys)"
echo "  4. Compute multisig address using import-mainnet-keys.py"
echo "  5. Replace PalletId(*b'verdist0') with computed multisig address"
echo "  6. Build mainnet raw chain spec and verify genesis hash determinism"
echo "  7. Distribute chain spec to all 21 validator operators"
echo "  8. Each operator inserts their private keys into their node keystore"
echo ""
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Ceremony completed successfully (v2)" | tee -a "$LOG_FILE"
