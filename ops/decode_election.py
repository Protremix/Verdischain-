#!/usr/bin/env python
"""Determine EXACTLY how the Verdis validator set is chosen, by parsing runtime
metadata instead of guessing storage keys.

Why this matters: if the set is elected from stake (Staking or Dpos), then the 6 lost
ceremony keys are irrelevant - we can register new validators with fresh session keys
and the set rotates. If the set is fixed and only sudo/governance can change it, we
are stuck at 15/21 forever.

Metadata V14/V15 is SCALE-encoded; rather than write a full decoder, extract the
pallet names and their storage/call item names by scanning for length-prefixed ASCII
identifiers near each pallet name. Crude but sufficient to answer: does Staking hold
any validators, and what does pallet_session use as SessionManager?
"""
import json, re, subprocess, os

KEY = os.path.expanduser("~/.ssh/id_ed25519")
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
       "-o", "ConnectTimeout=15", "-i", KEY, "root@185.84.224.91"]


def rpc(method, params="[]"):
    body = f'{{"jsonrpc":"2.0","id":1,"method":"{method}","params":{params}}}'
    cmd = ("curl -s -m 25 -H 'Content-Type: application/json' -d '"
           + body + "' http://localhost:9944")
    p = subprocess.run(SSH + [cmd], capture_output=True, text=True, timeout=90)
    try:
        return json.loads(p.stdout)["result"]
    except Exception:
        return None


meta = rpc("state_getMetadata")
if not meta:
    print("cannot read metadata"); raise SystemExit(1)
raw = bytes.fromhex(meta[2:])
print(f"metadata: {len(raw)} bytes")

# Pull all plausible ASCII identifiers with their offsets.
idents = [(m.start(), m.group().decode()) for m in
          re.finditer(rb'[A-Za-z][A-Za-z0-9_]{2,40}', raw)]
print(f"identifiers found: {len(idents)}")

pallets = ["Staking", "Session", "Dpos", "Grandpa", "Babe", "Council",
           "Democracy", "TechnicalCommittee", "Offences", "Historical"]
pos = {}
for off, name in idents:
    if name in pallets and name not in pos:
        pos[name] = off
print("\npallet name offsets:")
for k in sorted(pos, key=lambda x: pos[x]):
    print(f"  {k:<20} @{pos[k]}")

# For Staking and Dpos, list identifiers appearing shortly after the pallet name -
# these are its storage items and calls.
for target in ("Staking", "Dpos", "Session"):
    if target not in pos:
        print(f"\n{target}: NOT PRESENT"); continue
    start = pos[target]
    window = [n for o, n in idents if start <= o < start + 4000]
    seen, items = set(), []
    for n in window:
        if n not in seen and len(n) > 3:
            seen.add(n); items.append(n)
    print(f"\n{target} items (first 45 after offset):")
    print("  " + ", ".join(items[:45]))

# Decisive storage reads using well-known twox128 prefixes
print("\n=== decisive reads ===")
checks = {
    "Session.Validators": "0xcec5070d609dd3497f72bde07fc96ba088dcde934c658227ee1dfafcd6e16903",
    "Staking.CounterForValidators": "0x5f3e4907f716ac89b6347d15ececedcaad811cd65a470ddc9e9b1e77c63ba1a1",
    "Staking.ForceEra": "0x5f3e4907f716ac89b6347d15ececedcaf7dad0317324aecae8744b87fc95f2f3",
    "Staking.ActiveEra": "0x5f3e4907f716ac89b6347d15ececedca487df464e44a534ba6b0cbb32407b587",
}
for name, k in checks.items():
    v = rpc("state_getStorage", f'["{k}"]')
    print(f"  {name:<32} {v if v else 'null/absent'}")

# Count keys under the Staking pallet prefix at all
sp = "0x5f3e4907f716ac89b6347d15ececedca"
keys = rpc("state_getKeysPaged", f'["{sp}",200,"{sp}"]')
print(f"  Staking pallet storage keys present: {len(keys) if keys else 0}")

sess = "0xcec5070d609dd3497f72bde07fc96ba0"
keys2 = rpc("state_getKeysPaged", f'["{sess}",200,"{sess}"]')
print(f"  Session pallet storage keys present: {len(keys2) if keys2 else 0}")
