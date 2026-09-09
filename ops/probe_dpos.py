#!/usr/bin/env python
"""Enumerate pallet_dpos storage to learn how the validator set is really chosen.

Established so far:
  * Session.Validators holds 21 accounts
  * the Staking pallet has ZERO storage keys - it is compiled in but unused
  * the runtime is built from pallet_dpos (custom), so DPoS drives the set
  * there is no Sudo pallet and we hold none of the 3 Council keys

Question this answers: does pallet_dpos let an account self-register as a validator
(join_candidates / bond + validate style)? If yes, the 6 lost ceremony keys are NOT
needed - we can add validators with fresh keys and gain finality headroom without
governance. If the DPoS set is genesis-fixed, we are stuck.

Storage keys are twox128(pallet) ++ twox128(item).
"""
import json, os, subprocess
import xxhash

KEY = os.path.expanduser("~/.ssh/id_ed25519")
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
       "-o", "ConnectTimeout=15", "-i", KEY, "root@185.84.224.91"]


def twox128(s: bytes) -> str:
    out = b""
    for seed in (0, 1):
        out += xxhash.xxh64(s, seed=seed).digest()[::-1]
    return out.hex()


def rpc(method, params="[]", timeout=90):
    body = f'{{"jsonrpc":"2.0","id":1,"method":"{method}","params":{params}}}'
    cmd = ("curl -s -m 25 -H 'Content-Type: application/json' -d '"
           + body + "' http://localhost:9944")
    p = subprocess.run(SSH + [cmd], capture_output=True, text=True, timeout=timeout)
    try:
        return json.loads(p.stdout).get("result")
    except Exception:
        return None


PALLETS = ["Dpos", "Session", "Grandpa", "Babe", "Tokenomics"]
print("=== how many storage keys does each pallet actually hold? ===")
for p in PALLETS:
    pref = "0x" + twox128(p.encode())
    keys = rpc("state_getKeysPaged", f'["{pref}",500,"{pref}"]')
    print(f"  {p:<12} prefix {pref[:18]}…  keys={len(keys) if keys else 0}")

print("\n=== probing Dpos storage items ===")
dp = twox128(b"Dpos")
ITEMS = ["Validators", "ValidatorCount", "MaxValidators", "MinValidators",
         "CandidatePool", "Candidates", "SelectedCandidates", "TotalStake",
         "CandidateInfo", "Nominators", "DelegatorState", "Round",
         "CollatorCommission", "InflationConfig", "Staked", "Bonded",
         "ActiveValidators", "AuthorityKeys", "Invulnerables"]
found = {}
for item in ITEMS:
    k = "0x" + dp + twox128(item.encode())
    v = rpc("state_getStorage", f'["{k}"]')
    if v:
        found[item] = v
        print(f"  {item:<20} len={len(v)} {v[:80]}")
    else:
        # maybe it is a map - try listing keys under the prefix
        ks = rpc("state_getKeysPaged", f'["{k}",50,"{k}"]')
        if ks:
            print(f"  {item:<20} MAP with {len(ks)} entries")
            found[item] = f"map:{len(ks)}"

if not found:
    print("  no Dpos storage items matched those names")

print("\n=== decode ValidatorCount-style values ===")
for name, v in found.items():
    if isinstance(v, str) and v.startswith("0x") and len(v) <= 34:
        b = bytes.fromhex(v[2:])
        if len(b) in (4, 8, 16):
            print(f"  {name} = {int.from_bytes(b, 'little')}")

print("\n=== Session.Validators count (sanity) ===")
sv = rpc("state_getStorage",
         '["0xcec5070d609dd3497f72bde07fc96ba088dcde934c658227ee1dfafcd6e16903"]')
if sv:
    h = sv[2:]
    # strip compact prefix by aligning to 64-hex accounts from the end
    body = h[len(h) - (len(h) // 64) * 64:]
    print(f"  {len(body)//64} validator accounts")
