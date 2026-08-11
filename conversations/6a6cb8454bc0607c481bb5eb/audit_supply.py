import json, xxhash

def twox128(data):
    h1 = xxhash.xxh64(data.encode(), seed=0).intdigest()
    h2 = xxhash.xxh64(data.encode(), seed=1).intdigest()
    return h1.to_bytes(8, "little").hex() + h2.to_bytes(8, "little").hex()

# Testnet spec
with open("/opt/verdis-chain-rust/verdis-dev-raw-6val.json") as f:
    spec = json.load(f)

raw = spec.get("genesis", {}).get("raw", {}).get("top", {})

acct_prefix = "0x" + twox128("Balances") + twox128("Account")
print("Account prefix:", acct_prefix)

total = 0
count = 0
for k, v in raw.items():
    if k.lower().startswith(acct_prefix.lower()):
        count += 1
        raw_b = bytes.fromhex(v[2:])
        if len(raw_b) >= 16:
            free = int.from_bytes(raw_b[0:16], "little")
            total += free
            if count <= 10:
                key_bytes = bytes.fromhex(k[2:])
                acct_start = len(acct_prefix) // 2 + 16
                acct_id = key_bytes[acct_start:acct_start+32]
                acct_hex = acct_id.hex()[:16]
                free_v = free / 1e9
                print("  %d. account=0x%s... free=%.1fM VRDX" % (count, acct_hex, free_v / 1e6))

print("Total accounts: %d" % count)
print("Total free balance: %.0f VRDX" % (total / 1e9))
target = 100_000_000_000 * 10**9
print("Target: %.0f VRDX" % (target / 1e9))
print("Match: %s" % (total == target))
print("Difference: %.0f VRDX" % ((total - target) / 1e9))

# Also check mainnet spec
print("\n--- Mainnet Spec ---")
with open("/opt/verdis-chain-rust/chain-spec-mainnet-raw.json") as f:
    mspec = json.load(f)

mraw = mspec.get("genesis", {}).get("raw", {}).get("top", {})
mtotal = 0
mcount = 0
for k, v in mraw.items():
    if k.lower().startswith(acct_prefix.lower()):
        mcount += 1
        raw_b = bytes.fromhex(v[2:])
        if len(raw_b) >= 16:
            free = int.from_bytes(raw_b[0:16], "little")
            mtotal += free

print("Mainnet accounts: %d" % mcount)
print("Mainnet total free: %.0f VRDX" % (mtotal / 1e9))
print("Mainnet match: %s" % (mtotal == target))

# Check for dev identities in mainnet
alice_hex = "d43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d"
has_alice = any(alice_hex in v for v in mraw.values())
print("Mainnet has Alice: %s" % has_alice)

# Check sudo
sudo_prefix = "0x" + twox128("Sudo")
has_sudo = any(k.startswith(sudo_prefix) for k in mraw)
print("Mainnet has Sudo: %s" % has_sudo)
