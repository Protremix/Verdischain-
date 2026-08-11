import json, xxhash

def twox128(data):
    h1 = xxhash.xxh64(data.encode(), seed=0).intdigest()
    h2 = xxhash.xxh64(data.encode(), seed=1).intdigest()
    return h1.to_bytes(8, "little").hex() + h2.to_bytes(8, "little").hex()

with open("/opt/verdis-chain-rust/verdis-testnet-raw-fixed.json") as f:
    spec = json.load(f)

raw = spec.get("genesis", {}).get("raw", {}).get("top", {})
print("=== VERDIS TESTNET RAW SPEC VERIFICATION ===")
print("Name:", spec.get("name"))
print("ID:", spec.get("id"))
print("ChainType:", spec.get("chainType"))
print("Total keys:", len(raw))

# Check Sudo
sudo_prefix = "0x" + twox128("Sudo")
has_sudo = any(k.startswith(sudo_prefix) for k in raw)
print("\nHas Sudo:", has_sudo)

# DPOS ValidatorList count
dpos_vl_key = "0x" + twox128("Dpos") + twox128("ValidatorList")
for k, v in raw.items():
    if k.lower().startswith(dpos_vl_key.lower()):
        n = bytes.fromhex(v[2:])[0] >> 2
        print("DPOS ValidatorList:", n)
        break

# DPOS ActiveValidators count
dpos_av_key = "0x" + twox128("Dpos") + twox128("ActiveValidators")
for k, v in raw.items():
    if k.lower().startswith(dpos_av_key.lower()):
        n = bytes.fromhex(v[2:])[0] >> 2
        print("DPOS ActiveValidators:", n)
        # Decode the active validators
        raw_b = bytes.fromhex(v[2:])
        offset = 1
        for i in range(n):
            acct = raw_b[offset:offset+32]
            print("  %d. 0x%s" % (i+1, acct.hex()))
            offset += 32
        break

# Session validators
sv_key = "0x" + twox128("Session") + twox128("Validators")
for k, v in raw.items():
    if k.lower().startswith(sv_key.lower()):
        n = bytes.fromhex(v[2:])[0] >> 2
        print("Session::Validators:", n)
        break

# BABE authorities
babe_key = "0x" + twox128("Babe") + twox128("Authorities")
for k, v in raw.items():
    if k.lower().startswith(babe_key.lower()):
        n = bytes.fromhex(v[2:])[0] >> 2
        print("BABE::Authorities:", n)
        break

# GRANDPA authorities
gpa_key = "0x" + twox128("Grandpa") + twox128("Authorities")
for k, v in raw.items():
    if k.lower().startswith(gpa_key.lower()):
        n = bytes.fromhex(v[2:])[0] >> 2
        print("GRANDPA::Authorities:", n)
        break

# Token supply: sum System::Account free + reserved
sys_acct_prefix = "0x" + twox128("System") + twox128("Account")
total_free = 0
total_reserved = 0
acct_count = 0
for k, v in raw.items():
    if k.lower().startswith(sys_acct_prefix.lower()):
        acct_count += 1
        raw_b = bytes.fromhex(v[2:])
        if len(raw_b) >= 48:  # 4*u32 + 2*u128
            offset = 16  # skip nonce + consumers + providers + sufficients
            free = int.from_bytes(raw_b[offset:offset+16], "little")
            reserved = int.from_bytes(raw_b[offset+16:offset+32], "little")
            total_free += free
            total_reserved += reserved

grand_total = total_free + total_reserved
target = 100_000_000_000 * 10**9
print("\n=== TOKEN SUPPLY ===")
print("Accounts:", acct_count)
print("Total free: %.0f VRDX" % (total_free / 1e9))
print("Total reserved: %.0f VRDX" % (total_reserved / 1e9))
print("Grand total: %.0f VRDX" % (grand_total / 1e9))
print("Target: %.0f VRDX" % (target / 1e9))
print("Difference: %.0f VRDX" % ((grand_total - target) / 1e9))
print("Match:", grand_total == target)

# Also check TotalIssuance
ti_key = "0x" + twox128("Balances") + twox128("TotalIssuance")
for k, v in raw.items():
    if k.lower().startswith(ti_key.lower()):
        raw_b = bytes.fromhex(v[2:])
        if len(raw_b) >= 16:
            ti = int.from_bytes(raw_b[0:16], "little")
            print("TotalIssuance: %.0f VRDX" % (ti / 1e9))
            print("TotalIssuance match:", ti == target)
        break
