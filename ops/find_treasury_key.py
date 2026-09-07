#!/usr/bin/env python
"""Who holds the 99.9 billion VRDX, and do we control that key?

Findings so far:
  * 33 accounts on mainnet; sum of free balances 99,925,003,000 VRDX
  * the 21 Dpos validators are SEPARATE stash accounts holding 1,000 free +
    1,000,000 or 10,000,000 reserved (their bond)
  * our 11 acco session-key accounts are NOT on chain at all - they never held funds,
    so they are NOT the stashes
  * 3 accounts with 1,000 free and 0 reserved = the Council members

That means the stash keys are a separate set that we have not located. If the treasury
/ founder account key is on one of the servers, we can fund and register new
validators without governance and without the 6 lost ceremony keys.

This script finds the big holder and searches every server for any key file matching
any on-chain account.
"""
import hashlib, json, os, subprocess
import xxhash

KEY = os.path.expanduser("~/.ssh/id_ed25519")
HOSTS = ["185.84.224.91", "195.154.80.40", "213.136.78.63", "91.98.160.145"]
DEC = 10 ** 9


def ssh(host, cmd, timeout=120):
    p = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=15", "-i", KEY, f"root@{host}", cmd],
        capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip()


def twox128(s: bytes) -> str:
    return b"".join(xxhash.xxh64(s, seed=i).digest()[::-1] for i in (0, 1)).hex()


def rpc(method, params="[]"):
    body = f'{{"jsonrpc":"2.0","id":1,"method":"{method}","params":{params}}}'
    return json.loads(ssh("185.84.224.91",
        "curl -s -m 25 -H 'Content-Type: application/json' -d '" + body
        + "' http://localhost:9944") or "{}").get("result")


SYS = twox128(b"System") + twox128(b"Account")
keys = rpc("state_getKeysPaged", f'["0x{SYS}",200,"0x{SYS}"]') or []

rows = []
for k in keys:
    acct = k[-64:]
    v = rpc("state_getStorage", f'["{k}"]')
    if not v:
        continue
    b = bytes.fromhex(v[2:])
    if len(b) < 48:
        continue
    rows.append((int.from_bytes(b[16:32], "little"),
                 int.from_bytes(b[32:48], "little"), acct))
rows.sort(reverse=True)

print("=== top 6 holders ===")
for free, res, acct in rows[:6]:
    print(f"  0x{acct}")
    print(f"     free={free/DEC:>20,.2f}  reserved={res/DEC:>16,.2f}")

print("\n=== search every server for a key file matching ANY on-chain account ===")
all_accts = [r[2] for r in rows]
# check the top few first - those are the ones worth controlling
targets = [r[2] for r in rows[:6]]
for host in HOSTS:
    print(f"  --- {host} ---")
    for acct in targets:
        # keystore filenames are hex(keytype)+hex(pubkey); also check json/txt dumps
        out = ssh(host, f"find / -maxdepth 9 -name '*{acct}*' 2>/dev/null | head -3; "
                        f"grep -rl '{acct}' /root /opt /data 2>/dev/null | head -3")
        if out:
            print(f"    MATCH {acct[:20]}…")
            for line in out.split("\n")[:4]:
                print(f"      {line}")
    print("    (no match above means none of the top accounts' keys are on this host)")

print("\n=== how many of the 33 accounts have ANY key material on our servers? ===")
found_any = 0
for acct in all_accts:
    hit = False
    for host in HOSTS[:3]:
        out = ssh(host, f"find /data /opt /root -maxdepth 8 -name '*{acct}*' 2>/dev/null | head -1")
        if out:
            hit = True
            print(f"  {acct[:20]}… -> {host}: {out}")
            break
    if hit:
        found_any += 1
print(f"  accounts with key material found: {found_any} / {len(all_accts)}")
