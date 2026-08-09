#!/usr/bin/env python3
"""
Validates docs/data-manifest.md against runtime/src/lib.rs and node/src/chain_spec.rs.
Exits non-zero on any mismatch.
"""
import re
import sys
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNTIME = os.path.join(REPO_ROOT, "runtime/src/lib.rs")
CHAIN_SPEC = os.path.join(REPO_ROOT, "node/src/chain_spec.rs")
MANIFEST = os.path.join(REPO_ROOT, "docs/data-manifest.md")

errors = []

def read_file(path):
    with open(path) as f:
        return f.read()

def get_line(path, lineno):
    with open(path) as f:
        lines = f.readlines()
    if 0 < lineno <= len(lines):
        return lines[lineno - 1].strip()
    return ""

runtime = read_file(RUNTIME)
chain_spec = read_file(CHAIN_SPEC)
manifest = read_file(MANIFEST)

# Define expected values with source locations
checks = [
    # (name, expected_value, source_file, source_line, extract_pattern)
    ("UNITS", "1_000_000_000", RUNTIME, 130, r"UNITS.*?=\s*(\d[\d_]*)"),
    ("TOTAL_SUPPLY", "100_000_000_000", RUNTIME, 131, r"TOTAL_SUPPLY.*?=\s*(\d[\d_]*)"),
    ("CIRCULATING_SUPPLY", "17_000_000_000", RUNTIME, 132, r"CIRCULATING_SUPPLY.*?=\s*(\d[\d_]*)"),
    ("SS58Prefix", "909", RUNTIME, 141, r"SS58Prefix.*?=\s*(\d+)"),
    ("BLOCK_TIME", "6000", RUNTIME, 133, r"BLOCK_TIME.*?=\s*(\d+)"),
    ("EpochDuration", "50", RUNTIME, 216, r"EpochDuration.*?ConstU64<(\d+)>"),
    ("BlockReward", "16", RUNTIME, 510, r"BlockReward.*?=\s*(\d+)"),
    ("ExistentialDeposit", "UNITS", RUNTIME, 385, r"ExistentialDeposit.*?=\s*(\w+)"),
    ("ValidatorCount", "3", RUNTIME, 509, r"ValidatorCount.*?=\s*(\d+)"),
    ("MaxValidators", "1000", RUNTIME, 508, r"MaxValidators.*?=\s*(\d+)"),
    ("MaxValidatorsPerNode", "16", RUNTIME, 1023, r"MaxValidatorsPerNode.*?=\s*(\d+)"),
    ("MinValidatorStake", "10_000", RUNTIME, 507, r"MinValidatorStake.*?=\s*(\d[\d_]*)"),
    ("MaxStakePerValidator", "10_000_000_000", RUNTIME, 506, r"MaxStakePerValidator.*?=\s*(\d[\d_]*)"),
    ("chain_name", '"Verdis"', CHAIN_SPEC, 36, r'with_name\("([^"]+)"\)'),
    ("chain_id", '"verdis"', CHAIN_SPEC, 37, r'with_id\("([^"]+)"\)'),
    ("tokenSymbol", '"VRDX"', CHAIN_SPEC, 41, r'tokenSymbol.*?"([A-Z]+)"'),
    ("tokenDecimals", "9", CHAIN_SPEC, 42, r'tokenDecimals.*?(\d+)'),
]

for name, expected, src_file, src_line, pattern in checks:
    actual_line = get_line(src_file, src_line)
    match = re.search(pattern, actual_line)
    if not match:
        errors.append(f"[{name}] Could not extract from {os.path.basename(src_file)}:{src_line}: '{actual_line}'")
        continue
    actual = match.group(1)
    # Normalize for comparison
    exp_norm = str(expected).replace('"', '').replace('_', '')
    act_norm = str(actual).replace('"', '').replace('_', '')
    if exp_norm != act_norm:
        errors.append(f"[{name}] Mismatch: manifest expects {expected}, source has {actual} at {os.path.basename(src_file)}:{src_line}")

# Check manifest contains key numbers
manifest_checks = [
    ("100,000,000,000", "Total supply 100B"),
    ("25,000,000,000", "Ecosystem 25B"),
    ("20,000,000,000", "Staking 20B"),
    ("15,000,000,000", "Treasury 15B"),
    ("10,000,000,000", "Development 10B"),
    ("5,000,000,000", "Community 5B"),
    ("3,000,000,000", "Seed 3B"),
    ("2,000,000,000", "Presale 2B"),
    ("VRDX", "Token symbol"),
    ("909", "SS58 prefix"),
    ("9", "Decimals"),
    ("6000", "Block time ms"),
    ("16 VRDX", "Block reward"),
    ("36", "Pallet count"),
    ("144", "Test count"),
]

for value, desc in manifest_checks:
    if value not in manifest:
        errors.append(f"[manifest] Missing {desc}: '{value}'")

if errors:
    print(f"FAIL: {len(errors)} mismatch(es) found:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print(f"OK: All {len(checks)} source checks + {len(manifest_checks)} manifest checks passed.")
    sys.exit(0)
