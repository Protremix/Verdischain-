#!/usr/bin/env bash
# =============================================================================
# Verdis Custom Chain Spec Generator
# Configures BABE + GRANDPA Consensus, 600-block Epochs, 100B VRS Token Supply
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KEYS_FILE="${SCRIPT_DIR}/keys/all-keys.json"
OUTPUT_SPEC="${SCRIPT_DIR}/chain-spec.json"
OUTPUT_RAW_SPEC="${SCRIPT_DIR}/chain-spec-raw.json"

show_help() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Generates a custom Verdis chain specification for multi-node production deployment.

Options:
  -k, --keys-file FILE   Path to generated all-keys.json (default: ./keys/all-keys.json)
  -o, --output FILE      Path to output chain spec (default: ./chain-spec.json)
  -h, --help             Show this help message
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -k|--keys-file)
            KEYS_FILE="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_SPEC="$2"
            shift 2
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

# Ensure keys exist
if [[ ! -f "$KEYS_FILE" ]]; then
    echo "[!] Keys summary file not found at ${KEYS_FILE}. Running generate-keys.sh first..."
    "${SCRIPT_DIR}/generate-keys.sh"
fi

echo "=========================================================="
echo " Generating Custom Chain Spec for Verdis Network"
echo " Inputs: ${KEYS_FILE}"
echo " Output: ${OUTPUT_SPEC}"
echo "=========================================================="

python3 - "$KEYS_FILE" "$OUTPUT_SPEC" "$OUTPUT_RAW_SPEC" <<'PYEOF'
import sys, json, os

keys_file = sys.argv[1]
out_spec = sys.argv[2]
out_raw_spec = sys.argv[3]

with open(keys_file, 'r') as f:
    keys_data = json.load(f)

validators = keys_data.get("validators", {})

# Token details per specification:
# Token: VRS, 100B supply, 9 decimals, SS58=909, Chain ID 909
TOKEN_SYMBOL = "VRS"
TOKEN_DECIMALS = 9
SS58_FORMAT = 909
CHAIN_ID = "verdis_909"
CHAIN_NAME = "Verdis Mainnet"
TOTAL_SUPPLY_UNITS = 100_000_000_000 * (10 ** TOKEN_DECIMALS) # 100 Billion VRS in 1e-9 base units

# Epoch & Session parameters per spec:
# 6-second block time, 600-block epochs (1 hour per epoch)
EPOCH_DURATION_BLOCKS = 600
SESSION_PERIOD_BLOCKS = 600

# Prepare Session Keys & Authorities
babe_authorities = []
grandpa_authorities = []
session_keys = []
balances = []

num_vals = len(validators)
val_allocation = (10_000_000_000 * (10 ** TOKEN_DECIMALS)) # 10B VRS per validator (5 * 10B = 50B)
treasury_allocation = (30_000_000_000 * (10 ** TOKEN_DECIMALS)) # 30B VRS
founder_allocation = (20_000_000_000 * (10 ** TOKEN_DECIMALS)) # 20B VRS

sudo_account = None

for val_name, vdata in validators.items():
    stash_pub = vdata["stashPublicKey"]
    stash_addr = vdata.get("stashAddress", stash_pub)
    babe_pub = vdata["babePublicKey"]
    grandpa_pub = vdata["grandpaPublicKey"]
    imonline_pub = vdata["imOnlinePublicKey"]
    authdisc_pub = vdata["authorityDiscoveryPublicKey"]

    if not sudo_account:
        sudo_account = stash_pub

    # BABE authority entry [pubkey, weight]
    babe_authorities.append([babe_pub, 1])

    # GRANDPA authority entry [pubkey, weight]
    grandpa_authorities.append([grandpa_pub, 1])

    # Session Key mapping: [validator_stash, validator_controller, { babe, grandpa, im_online, authority_discovery }]
    session_keys.append([
        stash_pub,
        stash_pub,
        {
            "babe": babe_pub,
            "grandpa": grandpa_pub,
            "im_online": imonline_pub,
            "authority_discovery": authdisc_pub
        }
    ])

    # Balance allocation
    balances.append([stash_pub, str(val_allocation)])

# Add Sudo / Treasury allocations
treasury_account = "0x" + "11" * 32
founder_account = "0x" + "99" * 32

balances.append([treasury_account, str(treasury_allocation)])
balances.append([founder_account, str(founder_allocation)])

# Construct Chain Spec JSON
chain_spec = {
    "name": CHAIN_NAME,
    "id": CHAIN_ID,
    "chainType": "Live",
    "bootNodes": [
        "/dns/verdis-boot-1/tcp/30333/p2p/12D3KooWBoot111111111111111111111111111111111111111",
        "/dns/verdis-boot-2/tcp/30333/p2p/12D3KooWBoot222222222222222222222222222222222222222"
    ],
    "telemetryEndpoints": [
        ["wss://telemetry.verdischain.com/submit/", 0]
    ],
    "protocolId": "verdis",
    "properties": {
        "tokenSymbol": TOKEN_SYMBOL,
        "tokenDecimals": TOKEN_DECIMALS,
        "ss58Format": SS58_FORMAT,
        "tokenSupply": "100000000000"
    },
    "genesis": {
        "runtime": {
            "system": {
                "code": "0x"
            },
            "babe": {
                "epochConfig": {
                    "c": [1, 4],
                    "allowed_slots": "PrimaryAndSecondaryPlainSlots"
                },
                "authorities": babe_authorities,
                "epochDuration": EPOCH_DURATION_BLOCKS
            },
            "grandpa": {
                "authorities": grandpa_authorities
            },
            "session": {
                "keys": session_keys,
                "period": SESSION_PERIOD_BLOCKS
            },
            "balances": {
                "balances": balances
            },
            "sudo": {
                "key": sudo_account or "0x" + "00"*32
            }
        }
    }
}

with open(out_spec, 'w') as f:
    json.dump(chain_spec, f, indent=2)

with open(out_raw_spec, 'w') as f:
    json.dump(chain_spec, f)

print(f"[+] Successfully generated chain spec: {out_spec}")
print(f"[+] Total Initial Token Allocations: {sum(int(b[1]) for b in balances) / 10**TOKEN_DECIMALS:,.0f} VRS")
print(f"[+] Active Authorities: {len(babe_authorities)}")
print(f"[+] Epoch Duration: {EPOCH_DURATION_BLOCKS} blocks (600 blocks = 1 hour at 6s/block)")
PYEOF

echo "=========================================================="
echo " Chain Spec Generation Complete!"
echo " Raw and human-readable chain specs ready in multi-node/"
echo "=========================================================="
