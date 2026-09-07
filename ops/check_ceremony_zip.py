#!/usr/bin/env python
"""Check the ceremony key archive against the 6 authorities that have no key on any
server. This decides whether headroom can be restored.

The 6 idle GRANDPA authority pubkeys (from the on-chain set, measured today):
  c684b6445815fe73b22b70e6...  2d78d9baa868f09e1167a6ec...  866979f9f431a08fed738db3...
  1d1b56d9c8ffd65ac29154c9...  89bd2c69f05d4e83041262dd...  ab97b020d2cab53fbde3c794...

SECURITY: never print private key material, seeds, or mnemonics. Only public keys,
counts, and match/no-match verdicts. The archive stays where it is; nothing is copied
to a server in this script.
"""
import json, os, zipfile

ZIP = os.path.join(os.environ["LOCALAPPDATA"], "hermes", "profiles", "verdis",
                   "attachments", "ceremony-keys-20260901.zip")

# full 64-hex gran pubkeys of the 6 authorities with no key on our servers
MISSING_PREFIX = [
    "c684b6445815fe73b22b70e6", "2d78d9baa868f09e1167a6ec",
    "866979f9f431a08fed738db3", "1d1b56d9c8ffd65ac29154c9",
    "89bd2c69f05d4e83041262dd", "ab97b020d2cab53fbde3c794",
]
# the 15 gran pubkeys we already hold (prefixes), to identify overlap
HELD_PREFIX = [
    "a978cfff64dcddcf", "ffc8578a222dd7b7", "9480dd38bbebc220", "67cace71102f996c",
    "12004cf1f3337995", "283f3ca9ae981582", "5c4fa7a418f59dd1", "938eeebdb0d1d8da",
    "cd6e40b9c9efbb5b", "d9ae5710ce8d7678", "ead9387b1fceba7a", "fe079402f98caad2",
    "ff2a16b559abed82",
]

z = zipfile.ZipFile(ZIP)
names = z.namelist()
print(f"archive: {os.path.basename(ZIP)}  {os.path.getsize(ZIP)} bytes")
print(f"entries: {len(names)}")

dirs = sorted({n.split("/")[1] for n in names if n.count("/") >= 2 and n.split("/")[1]})
print(f"top-level groups: {dirs}")

validators = sorted({n.split("/")[2] for n in names
                     if "/validators/" in n and n.count("/") >= 3 and n.split("/")[2]})
print(f"validator folders: {len(validators)} -> {validators[0]} … {validators[-1]}")

others = [n for n in names if "/validators/" not in n and n.endswith(".json")]
print(f"non-validator json files: {len(others)}")
for o in others[:20]:
    print(f"   {o}")


def pub_of(entry):
    """Extract only the PUBLIC key from a keyfile, never the secret."""
    try:
        d = json.loads(z.read(entry).decode())
    except Exception as e:
        return None, f"unparsable ({type(e).__name__})"
    if not isinstance(d, dict):
        return None, "not an object"
    # common field names across subkey / polkadot-js outputs
    for k in ("publicKey", "public_key", "pubkey", "public", "ss58PublicKey"):
        if k in d and isinstance(d[k], str):
            return d[k].removeprefix("0x").lower(), sorted(d.keys())
    if "address" in d:
        return None, sorted(d.keys())
    return None, sorted(d.keys())


print("\n=== structure of one keyfile (field NAMES only) ===")
sample = f"ceremony-keys-20260901/validators/{validators[0]}/grandpa.json"
p, fields = pub_of(sample)
print(f"  {sample}")
print(f"  fields: {fields}")
print(f"  public key readable: {'yes' if p else 'no'}")

print("\n=== gran public keys in the archive vs the 6 missing authorities ===")
found_missing, all_gran = [], {}
for v in validators:
    entry = f"ceremony-keys-20260901/validators/{v}/grandpa.json"
    if entry not in names:
        continue
    pub, _ = pub_of(entry)
    if not pub:
        continue
    all_gran[v] = pub
    for m in MISSING_PREFIX:
        if pub.startswith(m):
            found_missing.append((v, m))

print(f"  gran pubkeys extracted: {len(all_gran)} / {len(validators)}")
for v, pub in sorted(all_gran.items()):
    tag = ""
    if any(pub.startswith(m) for m in MISSING_PREFIX):
        tag = "  *** ONE OF THE 6 MISSING ***"
    elif any(pub.startswith(h) for h in HELD_PREFIX):
        tag = "  (already held)"
    print(f"    {v:<14} 0x{pub[:24]}…{tag}")

print(f"\n=== VERDICT ===")
print(f"  missing authorities found in archive: {len(found_missing)} / 6")
for v, m in found_missing:
    print(f"    {v} -> 0x{m}…")
if len(found_missing) == 6:
    print("  ALL SIX RECOVERED - headroom can be restored to 6")
elif found_missing:
    print(f"  PARTIAL - {len(found_missing)} of 6 recoverable")
else:
    print("  none of the 6 are in this archive")
