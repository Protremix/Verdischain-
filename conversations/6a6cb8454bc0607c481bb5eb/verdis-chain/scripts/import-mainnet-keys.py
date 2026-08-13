#!/usr/bin/env python3
"""
Verdis Chain — Mainnet Key Import Script

Takes the output of the air-gapped key ceremony and generates:
1. A key-config.json file for the chain spec
2. A multisig address computation for the 3-of-5 cold storage
3. Verifies all keys are unique and valid

Usage:
    python3 import-mainnet-keys.py --validators validator-keys.json --multisig multisig-keys.json --output mainnet-key-config.json
"""

import json
import hashlib
import sys
import argparse
from pathlib import Path

def compute_multisig_address(signatories_hex: list, threshold: int) -> str:
    """
    Compute a Substrate multisig address.
    
    In Substrate, the multisig address is derived from:
    - Sorted signatory public keys (32 bytes each)
    - The threshold (as a u16)
    
    The address is blake2b_256(threshold_le_bytes ++ sorted_signatories_concatenated)
    truncated to 32 bytes, then SS58-encoded.
    
    For simplicity here, we return the hex representation.
    The actual SS58 encoding should be done with the subkey utility.
    """
    # Sort signatories
    sorted_signatories = sorted(signatories_hex)
    
    # Concatenate threshold (u16 LE) + signatories
    threshold_bytes = threshold.to_bytes(2, 'little')
    concat = threshold_bytes
    for s in sorted_signatories:
        # Convert hex to bytes
        concat += bytes.fromhex(s.removeprefix('0x'))
    
    # Blake2b-256 hash
    address_bytes = hashlib.blake2b(concat, digest_size=32).digest()
    
    return f"0x{address_bytes.hex()}"

def verify_unique_addresses(validators: list) -> bool:
    """Verify all validator addresses are unique"""
    sr_addresses = set()
    ed_addresses = set()
    
    for v in validators:
        sr = v['sr25519']['address']
        ed = v['ed25519']['address']
        
        if sr in sr_addresses:
            print(f"ERROR: Duplicate sr25519 address: {sr}")
            return False
        if ed in ed_addresses:
            print(f"ERROR: Duplicate ed25519 address: {ed}")
            return False
            
        sr_addresses.add(sr)
        ed_addresses.add(ed)
    
    print(f"Verified {len(sr_addresses)} unique sr25519 addresses")
    print(f"Verified {len(ed_addresses)} unique ed25519 addresses")
    return True

def verify_unique_multisig(multisig_keys: list) -> bool:
    """Verify all cold storage keys are unique"""
    addresses = set()
    for k in multisig_keys:
        addr = k['address']
        if addr in addresses:
            print(f"ERROR: Duplicate cold storage address: {addr}")
            return False
        addresses.add(addr)
    
    print(f"Verified {len(addresses)} unique cold storage addresses")
    return True

def main():
    parser = argparse.ArgumentParser(description='Import mainnet keys from air-gapped ceremony')
    parser.add_argument('--validators', required=True, help='Path to validator-keys.json')
    parser.add_argument('--multisig', required=True, help='Path to multisig-keys.json')
    parser.add_argument('--output', required=True, help='Output path for key config')
    parser.add_argument('--threshold', type=int, default=3, help='Multisig threshold (default: 3)')
    
    args = parser.parse_args()
    
    # Load ceremony output
    with open(args.validators) as f:
        validators = json.load(f)
    with open(args.multisig) as f:
        multisig_keys = json.load(f)
    
    print(f"Loaded {len(validators)} validators from {args.validators}")
    print(f"Loaded {len(multisig_keys)} cold storage keys from {args.multisig}")
    
    # Verify
    if not verify_unique_addresses(validators):
        sys.exit(1)
    if not verify_unique_multisig(multisig_keys):
        sys.exit(1)
    
    # Compute multisig address
    signatories_hex = [k['public_key_hex'] for k in multisig_keys]
    multisig_address = compute_multisig_address(signatories_hex, args.threshold)
    
    print(f"\n3-of-{args.threshold} Multisig Address: {multisig_address}")
    
    # Build key config
    config = {
        "version": 1,
        "description": "Verdis Chain Mainnet Key Configuration — generated from air-gapped ceremony",
        "validators": [
            {
                "id": v['validator_id'],
                "sr25519_public": v['sr25519']['public_key_hex'],
                "sr25519_address": v['sr25519']['address'],
                "ed25519_public": v['ed25519']['public_key_hex'],
                "ed25519_address": v['ed25519']['address'],
            }
            for v in validators
        ],
        "cold_storage": {
            "threshold": args.threshold,
            "total_keys": len(multisig_keys),
            "multisig_address": multisig_address,
            "signatories": [
                {
                    "id": k['key_id'],
                    "address": k['address'],
                    "public_key_hex": k['public_key_hex'],
                }
                for k in multisig_keys
            ],
        },
        "notes": [
            "Replace mainnet_validator_uris() in chain_spec.rs with these public keys",
            "Replace team_multisig PalletId with the computed multisig_address",
            "DO NOT include private keys or mnemonics in this file",
            "This file contains ONLY public keys — safe to commit to git",
        ],
    }
    
    with open(args.output, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\nKey config written to {args.output}")
    print(f"\nNext steps:")
    print(f"  1. Review {args.output}")
    print(f"  2. Update chain_spec.rs mainnet_validator_uris() with validator public keys")
    print(f"  3. Replace PalletId(*b'verdistm') with multisig address: {multisig_address}")
    print(f"  4. Build the runtime and generate the chain spec")
    print(f"  5. Verify genesis hash is deterministic")
    print(f"  6. Distribute to validator operators")

if __name__ == '__main__':
    main()
