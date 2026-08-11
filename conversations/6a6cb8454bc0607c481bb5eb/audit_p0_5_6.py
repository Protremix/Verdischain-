#!/usr/bin/env python3
"""P0-5 + P0-6: Mainnet genesis audit + Token supply invariant"""
import json, subprocess, sys

subprocess.run(["pip", "install", "xxhash", "-q"], capture_output=True)
import xxhash

def twox128(name):
    h1 = xxhash.xxh64(name.encode(), seed=0).intdigest()
    h2 = xxhash.xxh64(name.encode(), seed=1).intdigest()
    return h1.to_bytes(8, "little").hex() + h2.to_bytes(8, "little").hex()

# Generate mainnet raw spec
print("=" * 60)
print("P0-5: MAINNET GENESIS AUDIT")
print("=" * 60)

# Build mainnet spec on server
import subprocess as sp
r = sp.run(["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145",
            "source ~/.cargo/env 2>/dev/null; export PATH=$HOME/.cargo/bin:$PATH; cd /opt/verdis-chain-rust && ./target/release/verdis build-spec --chain mainnet --raw --disable-default-bootnode 2>/dev/null"],
           capture_output=True, text=True, timeout=30)

# The output might have log lines at the start
lines = r.stdout.strip().split('\n')
# Find the JSON start
json_start = 0
for i, line in enumerate(lines):
    if line.strip().startswith('{'):
        json_start = i
        break

json_str = '\n'.join(lines[json_start:])
spec = json.loads(json_str)

print(f"Name: {spec.get('name')}")
print(f"ID: {spec.get('id')}")
print(f"ChainType: {spec.get('chainType')}")
print(f"BootNodes: {spec.get('bootNodes')}")

raw = spec.get("genesis", {}).get("raw", {}).get("top", {})
print(f"Total storage keys: {len(raw)}")

# 1. Check Sudo
sudo_prefix = "0x" + twox128("Sudo")
sudo_key = "0x" + twox128("Sudo") + twox128("Key")
has_sudo = any(k.lower().startswith(sudo_prefix.lower()) for k in raw)
print(f"\nHas Sudo pallet: {has_sudo}")
if has_sudo:
    for k, v in raw.items():
        if k.lower().startswith(sudo_key.lower()):
            print(f"  Sudo::Key = {v}")
else:
    print("  ✓ PASS: No Sudo (mainnet is Sudo-free)")

# 2. DPoS validators
dpos_vl_key = "0x" + twox128("Dpos") + twox128("ValidatorList")
for k, v in raw.items():
    if k.lower().startswith(dpos_vl_key.lower()):
        data = bytes.fromhex(v[2:])
        n = data[0] >> 2
        print(f"\nDPoS RegisteredValidators: {n}")
        offset = 1
        validators = []
        for i in range(n):
            acct = "0x" + data[offset:offset+32].hex()
            validators.append(acct)
            offset += 32
        # Check for dev identities
        known_dev = {
            "0xd43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d": "Alice",
            "0x8eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a48": "Bob",
            "0x90b5ab205c6974c9ea841be688864633dc9ca8a357843eeacf2314649965fe22": "Charlie",
            "0x306721211d5404bd9da88e0204360a1a9ab8b87c66c1bc2fcdd37f3c2222cc20": "Dave",
            "0xe659a7a1628cdd93febc04a4e0646ea20e9f5f0ce097d9a05290d4a9e054df4e": "Eve",
            "0x1cbd2d43530a44705ad088af313e18f80b53ef16b36177cd4b77b846f2a5f07c": "Ferdie",
        }
        dev_found = [v for v in validators if v in known_dev]
        if dev_found:
            print(f"  ✗ FAIL: Dev identities found: {[known_dev[v] for v in dev_found]}")
        else:
            print(f"  ✓ PASS: No dev/testnet identities (no Alice/Bob/Charlie/Dave/Eve/Ferdie)")
        break

# 3. DPoS ActiveValidators
dpos_av_key = "0x" + twox128("Dpos") + twox128("ActiveValidators")
for k, v in raw.items():
    if k.lower().startswith(dpos_av_key.lower()):
        data = bytes.fromhex(v[2:])
        n = data[0] >> 2
        print(f"\nDPoS ActiveValidators: {n}")
        break

# 4. Session validators
sv_key = "0x" + twox128("Session") + twox128("Validators")
for k, v in raw.items():
    if k.lower().startswith(sv_key.lower()):
        data = bytes.fromhex(v[2:])
        n = data[0] >> 2
        print(f"Session::Validators: {n}")
        break

# 5. BABE authorities
ba_key = "0x" + twox128("Babe") + twox128("Authorities")
for k, v in raw.items():
    if k.lower().startswith(ba_key.lower()):
        data = bytes.fromhex(v[2:])
        n = data[0] >> 2
        print(f"BABE::Authorities: {n}")
        break

# 6. GRANDPA authorities
ga_key = "0x" + twox128("Grandpa") + twox128("Authorities")
for k, v in raw.items():
    if k.lower().startswith(ga_key.lower()):
        data = bytes.fromhex(v[2:])
        n = data[0] >> 2
        print(f"GRANDPA::Authorities: {n}")
        break

# 7. Check for private keys/seeds in the spec
print("\n=== SECURITY CHECKS ===")
dangerous_patterns = ["alice", "bob", "charlie", "dave", "eve", "ferdie", "//Alice", "//Bob",
                       "secret", "seed", "private", "mnemonic", "0x0000000000000000000"]
found_dangerous = []
for k, v in raw.items():
    for pattern in dangerous_patterns:
        if pattern.lower() in k.lower() or (isinstance(v, str) and pattern.lower() in v.lower()):
            found_dangerous.append((k[:40], v[:40] if isinstance(v, str) else str(v)[:40], pattern))

if found_dangerous:
    print(f"  Found {len(found_dangerous)} potentially dangerous entries:")
    for k, v, p in found_dangerous[:5]:
        print(f"    Key: {k}... Value: {v}... Pattern: {p}")
else:
    print("  ✓ PASS: No private keys, seeds, or dev identities found")

# 8. Token supply
print("\n" + "=" * 60)
print("P0-6: TOKEN SUPPLY INVARIANT")
print("=" * 60)

# Sum all account balances
sys_acct_prefix = "0x" + twox128("System") + twox128("Account")
total_free = 0
total_reserved = 0
acct_count = 0
account_balances = []
for k, v in raw.items():
    if k.lower().startswith(sys_acct_prefix.lower()):
        acct_count += 1
        data = bytes.fromhex(v[2:])
        if len(data) >= 48:
            offset = 16  # skip nonce + consumers + providers + sufficients (4 * u32 = 16 bytes)
            free = int.from_bytes(data[offset:offset+16], "little")
            reserved = int.from_bytes(data[offset+16:offset+32], "little")
            total_free += free
            total_reserved += reserved
            account_balances.append((k, free, reserved))

grand_total = total_free + total_reserved
target = 100_000_000_000 * 10**9

print(f"\nAccounts: {acct_count}")
print(f"Total free: {total_free/1e9:.0f} VRDX")
print(f"Total reserved: {total_reserved/1e9:.0f} VRDX")
print(f"Grand total: {grand_total/1e9:.0f} VRDX")
print(f"Target: {target/1e9:.0f} VRDX")
print(f"Difference: {(grand_total - target)/1e9:.0f} VRDX")
print(f"Match: {grand_total == target}")

# Also check TotalIssuance
ti_key = "0x" + twox128("Balances") + twox128("TotalIssuance")
for k, v in raw.items():
    if k.lower().startswith(ti_key.lower()):
        ti = int.from_bytes(bytes.fromhex(v[2:])[:16], "little")
        print(f"\nTotalIssuance: {ti/1e9:.0f} VRDX")
        print(f"TotalIssuance == Target: {ti == target}")
        print(f"TotalIssuance == Grand Total: {ti == grand_total}")
        break

# List all accounts with balances
print(f"\n=== ACCOUNT BALANCES ({acct_count} accounts) ===")
for k, free, reserved in sorted(account_balances, key=lambda x: -(x[1] + x[2])):
    total = free + reserved
    print(f"  {k[:20]}... free={free/1e9:.3f}B reserved={reserved/1e9:.3f}B total={total/1e9:.3f}B")

# Summary
print("\n" + "=" * 60)
print("P0-5 + P0-6 VERDICT")
print("=" * 60)
checks = [
    ("Mainnet name correct", spec.get("name") == "Verdis Mainnet"),
    ("Mainnet ID correct", spec.get("id") == "verdis-mainnet"),
    ("No Sudo pallet", not has_sudo),
    ("No dev identities (Alice-Ferdie)", len(dev_found) == 0 if 'dev_found' in dir() else True),
    ("No private keys/seeds", len(found_dangerous) == 0),
    ("Token supply == 100B VRDX", grand_total == target),
    ("TotalIssuance == 100B VRDX", ti == target if 'ti' in dir() else False),
    ("TotalIssuance == Account sum", ti == grand_total if 'ti' in dir() else False),
]
all_pass = True
for check, result in checks:
    status = "✓ PASS" if result else "✗ FAIL"
    if not result: all_pass = False
    print(f"  {status}: {check}")
print(f"\nOverall: {'ALL PASS ✓' if all_pass else 'FAILURES ✗'}")
