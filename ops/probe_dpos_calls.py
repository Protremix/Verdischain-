#!/usr/bin/env python
"""Find the extrinsics pallet_dpos exposes. If it has a self-registration call
(register_validator / join / bond+validate) then adding a 22nd validator - or
replacing an idle authority - needs NO governance and NONE of the 6 lost keys.

Dpos.Validators is a MAP with 21 entries, so membership is stored per-account, not as
a fixed genesis vector. That strongly suggests registration is possible.

Method: dump the metadata region around the Dpos pallet definition and read the call
variant names directly. Also check what a registered validator's entry looks like, to
see what a new one would have to provide (bond amount, session keys, etc).
"""
import json, os, re, subprocess
import xxhash

KEY = os.path.expanduser("~/.ssh/id_ed25519")
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
       "-o", "ConnectTimeout=15", "-i", KEY, "root@185.84.224.91"]


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


meta = rpc("state_getMetadata")
raw = bytes.fromhex(meta[2:])
print(f"metadata {len(raw)} bytes")

# Candidate call names for DPoS-style pallets
CANDIDATES = [
    "register_validator", "register_as_validator", "join_candidates", "join",
    "add_validator", "remove_validator", "bond", "bond_more", "bond_extra",
    "unbond", "validate", "chill", "nominate", "delegate", "undelegate",
    "set_validator_count", "set_max_validators", "force_new_round",
    "leave_candidates", "candidate_bond_more", "go_offline", "go_online",
    "set_commission", "claim_rewards", "withdraw_unbonded", "stake", "unstake",
    "increase_stake", "decrease_stake", "activate", "deactivate",
]
print("\n=== call names present anywhere in metadata ===")
present = []
for c in CANDIDATES:
    if c.encode() in raw:
        present.append(c)
        print(f"  {c}")
if not present:
    print("  none of the candidate names found")

# Locate the Dpos pallet region and list identifiers inside it
idx = raw.find(b"pallet_dpos")
print(f"\npallet_dpos marker at offset {idx}")
if idx > 0:
    lo, hi = max(0, idx - 6000), idx + 2000
    region = raw[lo:hi]
    ids = [m.group().decode() for m in re.finditer(rb'[a-z][a-z0-9_]{3,40}', region)]
    seen, ordered = set(), []
    for i in ids:
        if i not in seen:
            seen.add(i); ordered.append(i)
    print("snake_case identifiers near pallet_dpos (likely its calls/fields):")
    print("  " + ", ".join(ordered[:70]))

# What does an existing validator entry contain?
dp = twox128(b"Dpos")
prefix = "0x" + dp + twox128(b"Validators")
keys = rpc("state_getKeysPaged", f'["{prefix}",30,"{prefix}"]')
print(f"\n=== Dpos.Validators map: {len(keys) if keys else 0} entries ===")
if keys:
    for k in keys[:3]:
        v = rpc("state_getStorage", f'["{k}"]')
        acct = k[-64:]
        print(f"  account 0x{acct[:24]}…")
        print(f"    value: {v}")

# Is there a bond/minimum constant we must meet?
print("\n=== constants mentioning bond/stake/validator ===")
for word in [b"MinValidatorBond", b"MinCandidateStk", b"MinimumValidatorBond",
             b"MaxValidators", b"MinValidators", b"NominationDeposit",
             b"ValidatorBond", b"MinStake"]:
    if word in raw:
        print(f"  {word.decode()}")
