#!/usr/bin/env bash
# CI Check: Fail if dev/placeholder keys appear in production mainnet chain spec
# This script must exit 0 on success, non-zero on failure.
set -euo pipefail

CHAIN_SPEC="chain-specs/mainnet-plain.json"

if [ ! -f "$CHAIN_SPEC" ]; then
    echo "ERROR: Chain spec not found at $CHAIN_SPEC"
    exit 1
fi

# Patterns that indicate dev/placeholder keys
DEV_PATTERNS=(
    "//Alice"
    "//Bob"
    "//Charlie"
    "//Dave"
    "//Eve"
    "//Ferdie"
    "MAINNET_VALIDATOR_"
    "PLACEHOLDER"
    "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"  # Alice dev address
)

FOUND=0
for pattern in "${DEV_PATTERNS[@]}"; do
    if grep -q "$pattern" "$CHAIN_SPEC"; then
        echo "FAIL: Found dev key pattern '$pattern' in $CHAIN_SPEC"
        FOUND=1
    fi
done

# Also check the raw spec if it exists
RAW_SPEC="chain-specs/mainnet-raw.json"
if [ -f "$RAW_SPEC" ]; then
    for pattern in "${DEV_PATTERNS[@]}"; do
        if grep -q "$pattern" "$RAW_SPEC" ]; then
            echo "FAIL: Found dev key pattern '$pattern' in $RAW_SPEC"
            FOUND=1
        fi
    done
fi

if [ "$FOUND" -eq 0 ]; then
    echo "PASS: No dev/placeholder keys found in mainnet chain spec"
    exit 0
else
    echo "FAIL: Dev/placeholder keys detected in mainnet chain spec"
    exit 1
fi
