#!/usr/bin/env python
"""Final piece: can we actually register a NEW validator with pallet_dpos?

Confirmed so far:
  * pallet_dpos drives the set (Staking has 0 storage keys, Dpos has 54)
  * Dpos.Validators is a MAP with 21 entries -> membership is per-account state,
    not a frozen genesis vector
  * the runtime exposes register_validator, bond, unbond, stake, unstake, delegate,
    activate, deactivate
  * existing validators show a bonded stake of 1,000,000 to 10,000,000 VRDX

Remaining unknowns, all measurable:
  1. what is MinStake?
  2. what is MaxValidators? (if it is 21, a 22nd cannot join)
  3. do any of OUR 15 accounts hold a free balance big enough to bond?

If MaxValidators > 21 and we can fund an account, we can add validators WITHOUT the
6 lost keys and WITHOUT Council - which removes the zero-headroom problem entirely.
"""
import json, os, re, subprocess
import xxhash

KEY = os.path.expanduser("~/.ssh/id_ed25519")
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
       "-o", "ConnectTimeout=15", "-i", KEY, "root@185.84.224.91"]


def twox128(s: bytes) -> str:
    return b"".join(xxhash.xxh64(s, seed=i).digest()[::-1] for i in (0, 1)).hex()


def blake2_128_concat(data: bytes) -> str:
    import hashlib
    return hashlib.blake2b(data, digest_size=16).hexdigest() + data.hex()


def rpc(method, params="[]"):
    body = f'{{"jsonrpc":"2.0","id":1,"method":"{method}","params":{params}}}'
    cmd = ("curl -s -m 25 -H 'Content-Type: application/json' -d '"
           + body + "' http://localhost:9944")
    p = subprocess.run(SSH + [cmd], capture_output=True, text=True, timeout=90)
    try:
        return json.loads(p.stdout).get("result")
    except Exception:
        return None


meta = rpc("state_getMetadata")
raw = bytes.fromhex(meta[2:])

print("=== 1. constants: find MinStake / MaxValidators values in metadata ===")
# Constants are stored as name + SCALE-encoded value + type id. Search around the name.
for name in (b"MinStake", b"MaxValidators", b"MaxNominators", b"SessionsPerEra"):
    i = raw.find(name)
    if i < 0:
        print(f"  {name.decode():<16} not found"); continue
    window = raw[i + len(name): i + len(name) + 40]
    print(f"  {name.decode():<16} @{i} raw-after: {window[:24].hex()}")
    # a u128 constant is length-prefixed (0x41 = 16 bytes compact) then 16 LE bytes
    for off in range(0, 12):
        chunk = window[off:off + 16]
        if len(chunk) == 16:
            v = int.from_bytes(chunk, "little")
            if 0 < v <= 10**30:
                print(f"      offset {off:2d} -> {v:,} = {v/10**9:,.4f} VRDX")
                break
    # a u32 constant
    for off in range(0, 12):
        chunk = window[off:off + 4]
        if len(chunk) == 4:
            v = int.from_bytes(chunk, "little")
            if 0 < v < 100000:
                print(f"      offset {off:2d} -> u32 {v}")
                break

print("\n=== 2. our 15 validator accounts: free balance ===")
accounts = {
    "V18": "4c30c4404ef1891bab461d12cdcee69ee216fd8935dbf9bf4bf7c518f8e61421",
    "V19": "0454e42abc5c7f17bdad14e4cd77e62f4a0cfc9d0e90db1b671d82b209f8565e",
    "DE":  "7ce93e417b211fff3fe2b681ed2f4554cd1d4a133a3e84a7038c55192d23a250",
    "V15": "e4f38bb5ed50dda55ffc1cdeae75e2457aff82aa2fe336a5dfc7df77a0f42959",
    "V9":  "4adad7e0c587c0b0130373dd13861eb902a66e515362ed8ef923982ebce0f451",
}
sysp = twox128(b"System")
acctp = twox128(b"Account")
total_free = 0
for label, acct in accounts.items():
    k = "0x" + sysp + acctp + blake2_128_concat(bytes.fromhex(acct))
    v = rpc("state_getStorage", f'["{k}"]')
    if not v:
        print(f"  {label:<5} no account data"); continue
    b = bytes.fromhex(v[2:])
    # AccountInfo: nonce u32, consumers u32, providers u32, sufficients u32, then AccountData
    off = 16
    free = int.from_bytes(b[off:off + 16], "little")
    reserved = int.from_bytes(b[off + 16:off + 32], "little")
    total_free += free
    print(f"  {label:<5} free={free/10**9:>18,.2f} VRDX  reserved={reserved/10**9:>15,.2f}")
print(f"  {'TOTAL':<5} free={total_free/10**9:>18,.2f} VRDX")

print("\n=== 3. how many validators does Dpos allow? ===")
dp = twox128(b"Dpos")
for item in ("ValidatorCount", "TotalValidators", "MaxValidatorCount",
             "SelectedValidators", "ActiveValidatorCount", "Round", "TotalStaked"):
    k = "0x" + dp + twox128(item.encode())
    v = rpc("state_getStorage", f'["{k}"]')
    if v:
        b = bytes.fromhex(v[2:])
        n = int.from_bytes(b[:min(len(b), 16)], "little") if len(b) <= 16 else None
        print(f"  {item:<22} {v[:50]}" + (f"  -> {n:,}" if n is not None else ""))

print("\n=== 4. total issuance vs what we hold ===")
bp = twox128(b"Balances")
ti = rpc("state_getStorage", f'["0x{bp + twox128(b"TotalIssuance")}"]')
if ti:
    v = int.from_bytes(bytes.fromhex(ti[2:]), "little")
    print(f"  TotalIssuance: {v/10**9:,.0f} VRDX")
