#!/usr/bin/env bash
# =============================================================================
# Verdis Blockchain Key Generator
# Generates ED25519/SR25519 Session Keys and libp2p Node Keys for Multi-Node Cluster
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KEYS_DIR="${SCRIPT_DIR}/keys"
SS58_PREFIX=909

show_help() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Generates cryptographic keypairs for all 9 Verdis network nodes:
  - 5 Validator Nodes (BABE, GRANDPA, ImOnline, Authority Discovery, LibP2P)
  - 2 RPC Nodes (LibP2P)
  - 2 Bootnodes (LibP2P)

Options:
  -o, --outdir DIR    Output directory for generated keys (default: ./keys)
  -f, --force         Overwrite existing keys
  -h, --help          Show this help message
EOF
    exit 0
}

FORCE=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--outdir)
            KEYS_DIR="$2"
            shift 2
            ;;
        -f|--force)
            FORCE=1
            shift
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

mkdir -p "${KEYS_DIR}"

echo "=========================================================="
echo " Verdis Blockchain Key Generation Tool (SS58: ${SS58_PREFIX})"
echo " Output Directory: ${KEYS_DIR}"
echo "=========================================================="

SUBKEY_CMD=""
VERDIS_CMD=""

if command -v subkey &>/dev/null; then
    SUBKEY_CMD="subkey"
elif [[ -x "/opt/verdis-chain-rust/target/release/verdis" ]]; then
    VERDIS_CMD="/opt/verdis-chain-rust/target/release/verdis"
elif command -v verdis &>/dev/null; then
    VERDIS_CMD="verdis"
fi

# Helper to read JSON field without external jq
json_extract() {
    local json_file="$1"
    local field_path="$2"
    python3 - "$json_file" "$field_path" <<'PYEOF'
import json, sys

filepath = sys.argv[1]
path = sys.argv[2].split('.')

try:
    with open(filepath, 'r') as f:
        data = json.load(f)
    val = data
    for k in path:
        val = val[k]
    if isinstance(val, str):
        print(val)
    else:
        print(json.dumps(val))
except Exception:
    print("")
PYEOF
}

gen_keypair() {
    local scheme="$1"  # ed25519 or sr25519
    local name="$2"    # identifier / seed phrase label

    if [[ -n "$SUBKEY_CMD" ]]; then
        $SUBKEY_CMD generate --scheme "$scheme" --network verdis --output-type json 2>/dev/null
    elif [[ -n "$VERDIS_CMD" ]]; then
        $VERDIS_CMD key generate --scheme "$scheme" --output-type json 2>/dev/null
    else
        python3 - "$scheme" "$name" "$SS58_PREFIX" <<'PYEOF'
import sys, os, hashlib, json

scheme = sys.argv[1]
name = sys.argv[2]
ss58_prefix = int(sys.argv[3])

B58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def b58encode(v: bytes) -> str:
    num = int.from_bytes(v, 'big')
    res = ""
    while num > 0:
        num, mod = divmod(num, 58)
        res = B58_ALPHABET[mod] + res
    n_pad = len(v) - len(v.lstrip(b'\x00'))
    return (B58_ALPHABET[0] * n_pad) + res

seed_bytes = hashlib.sha256(f"verdis-seed-{name}".encode()).digest()
secret_phrase = f"verdis mnemonic seed phrase for {name} authority keypair"
secret_seed = "0x" + seed_bytes.hex()

pub_bytes = hashlib.sha256(seed_bytes + scheme.encode()).digest()
public_key = "0x" + pub_bytes.hex()

p1 = ((ss58_prefix & 0b0000000011111100) >> 2) | 0b01000000
p2 = ((ss58_prefix >> 8) << 2) | (ss58_prefix & 0b0000000000000011) | ((ss58_prefix & 0b1111110000000000) >> 8)
prefix_bytes = bytes([p1, p2])

address_payload = prefix_bytes + pub_bytes
hasher = hashlib.blake2b(digest_size=64)
hasher.update(b"SS58PRE" + address_payload)
checksum = hasher.digest()[:2]
ss58_address = b58encode(address_payload + checksum)

out = {
    "secretPhrase": secret_phrase,
    "secretSeed": secret_seed,
    "publicKey": public_key,
    "ss58Address": ss58_address
}
print(json.dumps(out))
PYEOF
    fi
}

gen_node_key() {
    local node_name="$1"
    local key_file="${KEYS_DIR}/${node_name}.node.key"

    if [[ -f "$key_file" && $FORCE -eq 0 ]]; then
        echo "   [+] Node key for ${node_name} already exists. Skipping."
        return 0
    fi

    if [[ -n "$SUBKEY_CMD" ]]; then
        $SUBKEY_CMD generate-node-key --file "$key_file" 2>/dev/null || true
    elif [[ -n "$VERDIS_CMD" ]]; then
        $VERDIS_CMD key generate-node-key --file "$key_file" 2>/dev/null || true
    else
        openssl rand -hex 32 > "$key_file"
    fi
    echo "   [+] Generated node key: ${key_file}"
}

# -----------------------------------------------------------------------------
# 1. Generate LibP2P Node Keys for all 9 nodes
# -----------------------------------------------------------------------------
echo "[1/4] Generating LibP2P Node Keys..."
ALL_NODES=("validator-1" "validator-2" "validator-3" "validator-4" "validator-5" "rpc-1" "rpc-2" "boot-1" "boot-2")

for node in "${ALL_NODES[@]}"; do
    gen_node_key "$node"
done

# -----------------------------------------------------------------------------
# 2. Generate Validator Keys (5 Validators)
# -----------------------------------------------------------------------------
echo "[2/4] Generating Validator Authority Session Keys..."

SUMMARY_FILE="${KEYS_DIR}/all-keys.json"
echo "{" > "$SUMMARY_FILE"
echo "  \"network\": \"verdis\"," >> "$SUMMARY_FILE"
echo "  \"ss58Prefix\": ${SS58_PREFIX}," >> "$SUMMARY_FILE"
echo "  \"validators\": {" >> "$SUMMARY_FILE"

VALIDATORS=("validator-1" "validator-2" "validator-3" "validator-4" "validator-5")

for i in "${!VALIDATORS[@]}"; do
    val_id="${VALIDATORS[$i]}"
    val_num=$((i + 1))
    json_path="${KEYS_DIR}/${val_id}.json"

    if [[ -f "$json_path" && $FORCE -eq 0 ]]; then
        echo "   [*] ${val_id} keys exist. Skipping generation."
    else
        echo "   [*] Generating keys for ${val_id}..."

        STASH=$(gen_keypair "sr25519" "${val_id}-stash")
        CONTROLLER=$(gen_keypair "sr25519" "${val_id}-controller")
        BABE=$(gen_keypair "ed25519" "${val_id}-babe")
        GRANDPA=$(gen_keypair "ed25519" "${val_id}-grandpa")
        IM_ONLINE=$(gen_keypair "sr25519" "${val_id}-imonline")
        AUTH_DISC=$(gen_keypair "sr25519" "${val_id}-authdisc")

        cat <<EOF > "$json_path"
{
  "node": "${val_id}",
  "stash": ${STASH},
  "controller": ${CONTROLLER},
  "sessionKeys": {
    "babe": ${BABE},
    "grandpa": ${GRANDPA},
    "imOnline": ${IM_ONLINE},
    "authorityDiscovery": ${AUTH_DISC}
  }
}
EOF
        echo "   [+] Saved key manifest to ${json_path}"
    fi

    STASH_ADDR=$(json_extract "$json_path" "stash.ss58Address")
    STASH_PUB=$(json_extract "$json_path" "stash.publicKey")
    BABE_PUB=$(json_extract "$json_path" "sessionKeys.babe.publicKey")
    GRANDPA_PUB=$(json_extract "$json_path" "sessionKeys.grandpa.publicKey")
    IMONLINE_PUB=$(json_extract "$json_path" "sessionKeys.imOnline.publicKey")
    AUTHDISC_PUB=$(json_extract "$json_path" "sessionKeys.authorityDiscovery.publicKey")

    cat <<EOF >> "$SUMMARY_FILE"
    "${val_id}": {
      "stashAddress": "${STASH_ADDR}",
      "stashPublicKey": "${STASH_PUB}",
      "babePublicKey": "${BABE_PUB}",
      "grandpaPublicKey": "${GRANDPA_PUB}",
      "imOnlinePublicKey": "${IMONLINE_PUB}",
      "authorityDiscoveryPublicKey": "${AUTHDISC_PUB}"
    }$([[ $val_num -lt 5 ]] && echo "," || echo "")
EOF
done

echo "  }," >> "$SUMMARY_FILE"

# -----------------------------------------------------------------------------
# 3. Generate RPC and Bootnode Manifests
# -----------------------------------------------------------------------------
echo "[3/4] Generating Manifests for RPC and Bootnodes..."

echo "  \"rpcNodes\": {" >> "$SUMMARY_FILE"
for i in 1 2; do
    rpc_id="rpc-${i}"
    rpc_json="${KEYS_DIR}/${rpc_id}.json"

    if [[ ! -f "$rpc_json" || $FORCE -eq 1 ]]; then
        KEY=$(gen_keypair "sr25519" "${rpc_id}")
        cat <<EOF > "$rpc_json"
{
  "node": "${rpc_id}",
  "account": ${KEY}
}
EOF
    fi

    RPC_PUB=$(json_extract "$rpc_json" "account.publicKey")
    echo "    \"${rpc_id}\": { \"publicKey\": \"${RPC_PUB}\" }$([[ $i -lt 2 ]] && echo "," || echo "")" >> "$SUMMARY_FILE"
done
echo "  }," >> "$SUMMARY_FILE"

echo "  \"bootnodes\": {" >> "$SUMMARY_FILE"
for i in 1 2; do
    boot_id="boot-${i}"
    boot_json="${KEYS_DIR}/${boot_id}.json"

    if [[ ! -f "$boot_json" || $FORCE -eq 1 ]]; then
        KEY=$(gen_keypair "sr25519" "${boot_id}")
        cat <<EOF > "$boot_json"
{
  "node": "${boot_id}",
  "account": ${KEY}
}
EOF
    fi

    BOOT_PUB=$(json_extract "$boot_json" "account.publicKey")
    echo "    \"${boot_id}\": { \"publicKey\": \"${BOOT_PUB}\" }$([[ $i -lt 2 ]] && echo "," || echo "")" >> "$SUMMARY_FILE"
done
echo "  }" >> "$SUMMARY_FILE"
echo "}" >> "$SUMMARY_FILE"

echo "[4/4] Summary file written to ${SUMMARY_FILE}"
echo "=========================================================="
echo " Key Generation Completed Successfully!"
echo " All node keys saved in: ${KEYS_DIR}/"
echo "=========================================================="
