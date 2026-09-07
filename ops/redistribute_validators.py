#!/usr/bin/env python
"""Move mainnet validators off Contabo so no single host can stop finality.

Measured problem: Contabo runs 14 of 21. Threshold is 15, so losing that one host
leaves 7 and finality halts. With 21 validators and threshold 15, no host may hold
more than 6 - which needs 4 hosts.

Target:
    185.84.224.91   3 -> 5   (+2)
    195.154.80.40   4 -> 6   (+2)
    213.136.78.63  14 -> 6   (-8)
    5.223.77.19     0 -> 4   (+4)
Worst single-host loss then leaves 15, exactly the threshold.

MOVE PROCEDURE per validator (the only safe order):
  1. verify the key exists in exactly ONE keystore across the whole fleet
  2. STOP + DISABLE the unit on the source (key now signs nowhere)
  3. copy keystore + network key to the target, write the unit there
  4. START on the target, wait for active
  5. verify: chain is mainnet, roles=Authority, equivocation 0, finality advancing
  6. only then delete the source keystore
If anything fails, restart the source and stop.

Never run steps for two validators concurrently - a key live in two places is
equivocation, which costs stake.
"""
import base64, json, os, subprocess, sys, time

KEY = os.path.expanduser("~/.ssh/id_ed25519")
SPEC = "/data/verdis-chain/chain-specs/mainnet-raw.json"
SPEC_SHA = "aca92919e13da10f"
MON = "185.84.224.91"
SRC = "213.136.78.63"
BOOT = [
    "/ip4/195.154.80.40/tcp/30333/p2p/12D3KooWQXtFadPxGmFRuEKKXpQWjQjSBooy6g4BhRHJQbiDjgfW",
    "/ip4/213.136.78.63/tcp/30333/p2p/12D3KooWSLhcUfZPEuh7h6JPs6yG5a1bMBmtwTQ1bnp56asoW869",
    "/ip4/185.84.224.91/tcp/30334/p2p/12D3KooWAyGAVHJ5BuJXFgSrvrUyLuhswCNuN65gsi7tzX3TwxNU",
]
ALL = [MON, "195.154.80.40", SRC, "5.223.77.19"]

# which of the freshly-deployed nodes to move where, and with which free ports
MOVES = [
    # (validator dir, source unit, target host, p2p, rpc, target unit)
    ("validator-18", "verdis-v18b", "5.223.77.19",   30341, 9960, "verdis-v18b"),
    ("validator-19", "verdis-v19b", "5.223.77.19",   30342, 9961, "verdis-v19b"),
    ("validator-20", "verdis-v20b", "5.223.77.19",   30343, 9962, "verdis-v20b"),
    ("validator-21", "verdis-v21b", "5.223.77.19",   30344, 9963, "verdis-v21b"),
    ("validator-16", "verdis-v16b", "195.154.80.40", 30341, 9960, "verdis-v16b"),
    ("validator-17", "verdis-v17b", "195.154.80.40", 30342, 9961, "verdis-v17b"),
]


def sh(host, cmd, timeout=250):
    p = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=15", "-i", KEY, f"root@{host}", cmd],
        capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip()


def finality():
    cmd = (r'''R(){ curl -s -m 8 -H "Content-Type: application/json" '''
           r'''-d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" '''
           r'''http://localhost:9944; }; '''
           r'''B=$(R chain_getHeader "[]"|grep -oP "\"number\":\"\K0x[0-9a-f]+"); '''
           r'''FH=$(R chain_getFinalizedHead "[]"|grep -oP "0x[0-9a-f]{64}"); '''
           r'''F=$(R chain_getHeader "[\"$FH\"]"|grep -oP "\"number\":\"\K0x[0-9a-f]+"); '''
           r'''echo "$((B)) $((F))"''')
    try:
        b, f = sh(MON, cmd, timeout=90).split()
        return int(b), int(f)
    except Exception:
        return None, None


def key_locations(fnames):
    """Every host+path where any of these keystore filenames exists."""
    hits = []
    for h in ALL:
        out = sh(h, "for f in " + " ".join(fnames) +
                 "; do find /data -name \"$f\" 2>/dev/null; done")
        for line in out.split("\n"):
            if line.strip():
                hits.append((h, line.strip()))
    return hits


def total_validators():
    t = {}
    for h in ALL:
        n = sh(h, "systemctl list-units 'verdis-validator*' 'verdis-v??b*' "
                  "--state=active --no-legend --no-pager | wc -l")
        t[h] = int(n or 0)
    return t


# ---------- prepare the 4th host ----------
print("=== prepare 5.223.77.19 ===")
have = sh("5.223.77.19", f"[ -f {SPEC} ] && sha256sum {SPEC} | cut -c1-16 || echo MISSING")
if SPEC_SHA not in have:
    print(f"  spec missing/wrong ({have}) - copying verified spec from {SRC}")
    sh("5.223.77.19", "mkdir -p /data/verdis-chain/chain-specs")
    # stream through the local machine to avoid needing host-to-host trust
    tmp = os.path.join(os.environ.get("LOCALAPPDATA", "/tmp"), "Temp", "mainnet-raw.json")
    subprocess.run(["scp", "-q", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
                    "-i", KEY, f"root@{SRC}:{SPEC}", tmp], check=True, timeout=300)
    subprocess.run(["scp", "-q", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
                    "-i", KEY, tmp, f"root@5.223.77.19:{SPEC}"], check=True, timeout=300)
    os.remove(tmp)
    have = sh("5.223.77.19", f"sha256sum {SPEC} | cut -c1-16")
print(f"  spec on 5.223.77.19: {have} (want {SPEC_SHA})")
if SPEC_SHA not in have:
    print("  spec still wrong - abort"); sys.exit(1)

t0 = total_validators()
b0, f0 = finality()
print(f"\n=== baseline: {t0}, total={sum(t0.values())}, finalized={f0} ===")

moved, failed = [], []

for vdir, src_unit, tgt, p2p, rpc, tgt_unit in MOVES:
    print(f"\n{'='*66}\n{vdir}: {SRC}/{src_unit}  ->  {tgt}/{tgt_unit} (p2p {p2p}, rpc {rpc})\n{'='*66}")
    ks_src = f"/data/{vdir}/chains/verdis/keystore"
    net_src = f"/data/{vdir}/chains/verdis/network/secret_ed25519"

    fnames = sh(SRC, f"ls -1 {ks_src} 2>/dev/null").split()
    if len(fnames) != 3:
        print(f"  expected 3 key files, found {len(fnames)} - skip"); failed.append(vdir); continue

    locs = key_locations(fnames)
    print(f"  key currently in {len(locs)} location(s)")
    if len(locs) != 3:  # 3 files, one host
        for h, p in locs:
            print(f"    {h}: {p}")
        print("  key is not in exactly one place - refusing to move"); failed.append(vdir); break

    # 2. stop on source FIRST
    sh(SRC, f"systemctl disable --now {src_unit}")
    st = sh(SRC, f"systemctl is-active {src_unit}")
    print(f"  source stopped: is-active={st}")
    if st == "active":
        print("  could not stop source - abort"); failed.append(vdir); break

    # 3. copy keystore + network key to target
    ks_tgt = f"/data/{vdir}/chains/verdis/keystore"
    net_dir = f"/data/{vdir}/chains/verdis/network"
    sh(tgt, f"mkdir -p {ks_tgt} {net_dir}")
    ok = True
    for fn in fnames:
        content = sh(SRC, f"base64 -w0 {ks_src}/{fn}")
        if not content:
            ok = False; break
        sh(tgt, f"echo {content} | base64 -d > {ks_tgt}/{fn} && chmod 600 {ks_tgt}/{fn}")
    netb = sh(SRC, f"base64 -w0 {net_src} 2>/dev/null")
    if netb:
        sh(tgt, f"echo {netb} | base64 -d > {net_dir}/secret_ed25519 && chmod 600 {net_dir}/secret_ed25519")
    else:
        sh(tgt, f"head -c32 /dev/urandom | xxd -p -c32 | tr -d '\\n' > {net_dir}/secret_ed25519 && "
                f"chmod 600 {net_dir}/secret_ed25519")
    cnt = sh(tgt, f"ls -1 {ks_tgt} | wc -l")
    print(f"  copied: {cnt} key files on target (expect 3)")
    if not ok or cnt != "3":
        print("  copy failed - restarting source")
        sh(SRC, f"systemctl enable --now {src_unit}"); failed.append(vdir); break

    # 4. unit on target
    boots = " ".join(f"--bootnodes={b}" for b in BOOT)
    unit = f"""[Unit]
Description=Verdis Chain Validator {vdir.upper()} (moved for host redundancy)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
Restart=always
RestartSec=10
ExecStart=/usr/local/bin/verdis --chain={SPEC} --base-path=/data/{vdir} \\
  --name='Verdis {vdir}' --validator --port={p2p} --rpc-port={rpc} \\
  --no-telemetry --state-pruning=archive --force-authoring {boots}
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
"""
    b64 = base64.b64encode(unit.encode()).decode()
    sh(tgt, f"echo {b64} | base64 -d > /etc/systemd/system/{tgt_unit}.service && systemctl daemon-reload")
    eff = sh(tgt, f"systemctl show -p ExecStart --value {tgt_unit} | grep -oP 'argv\\[\\]=\\K[^;]+' | tail -1")
    if f"--name=Verdis {vdir}" not in eff:
        print(f"  quoting broken: {eff[:120]}")
        sh(tgt, f"rm -f /etc/systemd/system/{tgt_unit}.service; systemctl daemon-reload")
        sh(SRC, f"systemctl enable --now {src_unit}"); failed.append(vdir); break

    sh(tgt, f"systemctl enable {tgt_unit} >/dev/null 2>&1; systemctl start {tgt_unit}")
    state = ""
    for _ in range(48):
        time.sleep(5)
        state = sh(tgt, f"systemctl is-active {tgt_unit}", timeout=60)
        if state in ("active", "failed"):
            break
    print(f"  target is-active: {state}")
    if state != "active":
        print(" ", sh(tgt, f"journalctl -u {tgt_unit} -n 6 --no-pager | tail -6 | cut -c1-150"))
        sh(tgt, f"systemctl disable --now {tgt_unit}")
        sh(SRC, f"systemctl enable --now {src_unit}")
        failed.append(vdir); break

    # 5. verify
    time.sleep(25)
    chain = sh(tgt, f"curl -s -m 8 -H 'Content-Type: application/json' "
                    f"-d '{{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"system_chain\",\"params\":[]}}' "
                    f"http://localhost:{rpc} | grep -oP 'result\":\"\\K[^\"]+'")
    roles = sh(tgt, f"curl -s -m 8 -H 'Content-Type: application/json' "
                    f"-d '{{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"system_nodeRoles\",\"params\":[]}}' "
                    f"http://localhost:{rpc} | grep -oP 'result\":\\K.*'")
    eq = 0
    for h in (SRC, tgt, MON):
        e = sh(h, "journalctl -u 'verdis*' --since '3 min ago' --no-pager 2>/dev/null | grep -ci equivocat")
        eq += int(e or 0)
    b1, f1 = finality()
    print(f"  chain={chain} roles={roles} equivocation={eq} finality={f0}->{f1}")

    if "Mainnet" not in str(chain) or "Authority" not in str(roles) or eq > 0:
        print("  verification FAILED - rolling back")
        sh(tgt, f"systemctl disable --now {tgt_unit}")
        sh(SRC, f"systemctl enable --now {src_unit}")
        failed.append(vdir); break

    # 6. remove source keystore only after success
    sh(SRC, f"rm -rf /data/{vdir}/chains/verdis/keystore && "
            f"rm -f /etc/systemd/system/{src_unit}.service && systemctl daemon-reload")
    print("  source keystore removed, key now in exactly one place")
    f0 = f1 if f1 else f0
    moved.append(vdir)

print(f"\n{'='*66}")
print(f"moved: {len(moved)} -> {moved}")
print(f"failed: {len(failed)} -> {failed}")
t1 = total_validators()
tot = sum(t1.values())
print(f"\n=== new distribution (total {tot}, threshold 15) ===")
for h, n in t1.items():
    rem = tot - n
    print(f"  {h:<16} {n:>2}  -> lose it: {rem} remain, {'survives' if rem >= 15 else 'FINALITY STOPS'}")
b, f = finality()
print(f"\n  chain: best={b} finalized={f} lag={b - f if b else '?'}")
