#!/usr/bin/env python
"""Read the real free balances of our accounts, and find who holds the 100 billion
VRDX issuance. This decides whether registering a new validator is affordable.

MinStake looks like 100,000,000 VRDX (100e6 * 1e9 planck = 1e17), while existing
validators bonded 1,000,000-10,000,000 VRDX. Those are BELOW that figure, so either
MinStake is lower than my read, or genesis validators bypassed the check. Measure
balances first, then test the bound empirically if needed.

The System.Account layout must be parsed carefully: AccountInfo is
  nonce: u32, consumers: u32, providers: u32, sufficients: u32,
  data: { free: u128, reserved: u128, frozen: u128, flags: u128 }
= 16 + 64 = 80 bytes.
"""
import hashlib, json, os, subprocess
import xxhash

KEY = os.path.expanduser("~/.ssh/id_ed25519")
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
       "-o", "ConnectTimeout=15", "-i", KEY, "root@185.84.224.91"]
DEC = 10 ** 9


def twox128(s: bytes) -> str:
    return b"".join(xxhash.xxh64(s, seed=i).digest()[::-1] for i in (0, 1)).hex()


def rpc(method, params="[]"):
    body = f'{{"jsonrpc":"2.0","id":1,"method":"{method}","params":{params}}}'
    cmd = ("curl -s -m 25 -H 'Content-Type: application/json' -d '"
           + body + "' http://localhost:9944")
    p = subprocess.run(SSH + [cmd], capture_output=True, text=True, timeout=90)
    try:
        return json.loads(p.stdout).get("result")
    except Exception:
        return None


SYS = twox128(b"System") + twox128(b"Account")


def bal(acct_hex):
    h = bytes.fromhex(acct_hex)
    k = "0x" + SYS + hashlib.blake2b(h, digest_size=16).hexdigest() + acct_hex
    v = rpc("state_getStorage", f'["{k}"]')
    if not v:
        return None
    b = bytes.fromhex(v[2:])
    if len(b) < 48:
        return None
    return {
        "free": int.from_bytes(b[16:32], "little"),
        "reserved": int.from_bytes(b[32:48], "little"),
    }


print("=== all accounts on mainnet, sorted by balance ===")
keys = rpc("state_getKeysPaged", f'["0x{SYS}",200,"0x{SYS}"]')
print(f"  System.Account entries: {len(keys) if keys else 0}")

rows = []
for k in (keys or []):
    acct = k[-64:]
    b = bal(acct)
    if b:
        rows.append((b["free"], b["reserved"], acct))
rows.sort(reverse=True)

total = 0
for free, res, acct in rows:
    total += free
    if free > 0:
        print(f"  0x{acct[:20]}…  free={free/DEC:>20,.2f}  reserved={res/DEC:>16,.2f}")
print(f"\n  accounts with balance: {sum(1 for r in rows if r[0] > 0)} / {len(rows)}")
print(f"  sum of free balances: {total/DEC:,.2f} VRDX")

print("\n=== our 15 validator (acco) accounts ===")
ours = {
    "V18": "4c30c4404ef1891bab461d12cdcee69ee216fd8935dbf9bf4bf7c518f8e61421",
    "V19": "0454e42abc5c7f17bdad14e4cd77e62f4a0cfc9d0e90db1b671d82b209f8565e",
    "DE":  "7ce93e417b211fff3fe2b681ed2f4554cd1d4a133a3e84a7038c55192d23a250",
    "V15": "e4f38bb5ed50dda55ffc1cdeae75e2457aff82aa2fe336a5dfc7df77a0f42959",
    "V16": "ce0c6462482597beccc128f693ce13d436e1ba7d91b00da45c18508415da6c55",
    "V17": "9428d5bf690606a7a5bb04e1fece81aae5820b6bab8c499cd7a372b9ec2fb251",
    "NL":  "50f44232ad9377046b3e9de7734bf0b6c4e2970d3abf363b3b29b2415f4da631",
    "V9":  "4adad7e0c587c0b0130373dd13861eb902a66e515362ed8ef923982ebce0f451",
    "V10": "1ec5c2ed9739f4d67915172d787ec69a9d6ca05c04a4a1e1e793e59c941e6e52",
    "V20": "7253bd213e4e32d410e3a0160c0a6becda29d3d3f82ffff82b5b84f5e15bed7e",
    "CB":  "ae4bc6f378235050c56a3946041543611c91dc318b163cfc670639828434595f",
}
onchain = {r[2] for r in rows}
have = 0
for label, acct in ours.items():
    b = bal(acct)
    if b is None:
        print(f"  {label:<5} 0x{acct[:16]}…  NOT ON CHAIN (never received funds)")
    else:
        have += b["free"]
        print(f"  {label:<5} free={b['free']/DEC:>18,.2f}  reserved={b['reserved']/DEC:>14,.2f}")
print(f"\n  total we control: {have/DEC:,.2f} VRDX")

print("\n=== are the Dpos validator accounts the same as our acco keys? ===")
dp = twox128(b"Dpos") + twox128(b"Validators")
dkeys = rpc("state_getKeysPaged", f'["0x{dp}",30,"0x{dp}"]')
dset = {k[-64:] for k in (dkeys or [])}
print(f"  Dpos.Validators accounts: {len(dset)}")
match = dset & set(ours.values())
print(f"  overlap with our acco keys: {len(match)}")
if match:
    for m in list(match)[:5]:
        lbl = [k for k, v in ours.items() if v == m][0]
        print(f"    {lbl} 0x{m[:20]}…")
