#!/usr/bin/env python
"""Final step: get Contabo from 8 down to 6 so NO single host can stop finality.

After the first redistribution:
    185.84.224.91   3  -> lose it: 18 remain, survives
    195.154.80.40   6  -> lose it: 15 remain, survives
    213.136.78.63   8  -> lose it: 13 remain, FINALITY STOPS   <- still the problem
    5.223.77.19     4  -> lose it: 17 remain, survives

Move 2 more off Contabo to 185.84.224.91 (which has the most spare capacity: 3 nodes,
811G free, load 0.12). Result:
    185.84.224.91   5  -> 16 remain, survives
    195.154.80.40   6  -> 15 remain, survives
    213.136.78.63   6  -> 15 remain, survives
    5.223.77.19     4  -> 17 remain, survives

These are ORIGINAL validators (V9..V14, V20, Contabo), not the ones just deployed, so
their keystores live under chains/verdis-mainnet/ AND chains/verdis/ - both must move,
and the unit name/ports differ. Pick two whose data is smallest to keep the copy short.

Same safety rules: one at a time, stop source before starting target, verify the key
exists in exactly one place, check equivocation and finality, roll back on any failure.
"""
import base64, json, os, subprocess, sys, time

KEY = os.path.expanduser("~/.ssh/id_ed25519")
SPEC = "/data/verdis-chain/chain-specs/mainnet-raw.json"
MON = "185.84.224.91"
SRC = "213.136.78.63"
TGT = "185.84.224.91"
ALL = [MON, "195.154.80.40", SRC, "5.223.77.19"]
BOOT = [
    "/ip4/195.154.80.40/tcp/30333/p2p/12D3KooWQXtFadPxGmFRuEKKXpQWjQjSBooy6g4BhRHJQbiDjgfW",
    "/ip4/213.136.78.63/tcp/30333/p2p/12D3KooWSLhcUfZPEuh7h6JPs6yG5a1bMBmtwTQ1bnp56asoW869",
    "/ip4/185.84.224.91/tcp/30334/p2p/12D3KooWAyGAVHJ5BuJXFgSrvrUyLuhswCNuN65gsi7tzX3TwxNU",
]
# (data dir on source, source unit, target p2p, target rpc, target unit)
MOVES = [
    ("validator-V13", "verdis-validator-v13", 30341, 9960, "verdis-v13m"),
    ("validator-V14", "verdis-validator-v14", 30342, 9961, "verdis-v14m"),
]


def sh(host, cmd, timeout=400):
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


def counts():
    t = {}
    for h in ALL:
        n = sh(h, "systemctl list-units 'verdis-validator*' 'verdis-v??[bm]*' "
                  "--state=active --no-legend --no-pager | wc -l", timeout=120)
        t[h] = int(n or 0)
    return t


t0 = counts()
b0, f0 = finality()
print(f"=== baseline {t0} total={sum(t0.values())} finalized={f0} ===")

moved, failed = [], []

for vdir, src_unit, p2p, rpc, tgt_unit in MOVES:
    print(f"\n{'='*66}\n{vdir}: {SRC}/{src_unit} -> {TGT}/{tgt_unit}\n{'='*66}")

    # find every keystore this validator owns (both chain dir variants)
    ks_dirs = sh(SRC, f"find /data/{vdir} -type d -name keystore 2>/dev/null").split()
    print(f"  keystores on source: {len(ks_dirs)}")
    for d in ks_dirs:
        print(f"    {d} ({sh(SRC, f'ls -1 {d} | wc -l')} files)")
    if not ks_dirs:
        print("  no keystore found - skip"); failed.append(vdir); continue

    fnames = sorted(set(sh(SRC, f"cat /dev/null; for d in {' '.join(ks_dirs)}; do ls -1 $d; done").split()))
    print(f"  unique key files: {len(fnames)}")

    # the key must exist only on the source right now
    hosts_with = []
    for h in ALL:
        out = sh(h, "for f in " + " ".join(fnames) +
                 "; do find /data -name \"$f\" 2>/dev/null | head -1; done", timeout=200)
        if out.strip():
            hosts_with.append(h)
    print(f"  key present on hosts: {hosts_with}")
    if hosts_with != [SRC]:
        print("  key is not exclusively on the source - refusing"); failed.append(vdir); break

    # stop source
    sh(SRC, f"systemctl disable --now {src_unit}")
    if sh(SRC, f"systemctl is-active {src_unit}") == "active":
        print("  cannot stop source - abort"); failed.append(vdir); break
    print("  source stopped")

    # copy every keystore dir + network key
    ok = True
    for d in ks_dirs:
        rel = d.replace(f"/data/{vdir}/", "")
        sh(TGT, f"mkdir -p /data/{vdir}/{rel}")
        for fn in sh(SRC, f"ls -1 {d}").split():
            c = sh(SRC, f"base64 -w0 {d}/{fn}")
            if not c:
                ok = False; break
            sh(TGT, f"echo {c} | base64 -d > /data/{vdir}/{rel}/{fn} && chmod 600 /data/{vdir}/{rel}/{fn}")
        if not ok:
            break
    for chain_dir in ("verdis", "verdis-mainnet"):
        nb = sh(SRC, f"base64 -w0 /data/{vdir}/chains/{chain_dir}/network/secret_ed25519 2>/dev/null")
        if nb:
            sh(TGT, f"mkdir -p /data/{vdir}/chains/{chain_dir}/network && "
                    f"echo {nb} | base64 -d > /data/{vdir}/chains/{chain_dir}/network/secret_ed25519 && "
                    f"chmod 600 /data/{vdir}/chains/{chain_dir}/network/secret_ed25519")
    tot_copied = sh(TGT, f"find /data/{vdir} -type f -path '*keystore*' | wc -l")
    print(f"  copied key files on target: {tot_copied} (source had {len(fnames)} unique)")
    if not ok or int(tot_copied or 0) < 3:
        print("  copy failed - restarting source")
        sh(SRC, f"systemctl enable --now {src_unit}"); failed.append(vdir); break

    # unit
    boots = " ".join(f"--bootnodes={b}" for b in BOOT)
    unit = f"""[Unit]
Description=Verdis Chain Validator {vdir} (moved for host redundancy)
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
    sh(TGT, f"echo {b64} | base64 -d > /etc/systemd/system/{tgt_unit}.service && systemctl daemon-reload")
    eff = sh(TGT, f"systemctl show -p ExecStart --value {tgt_unit} | grep -oP 'argv\\[\\]=\\K[^;]+' | tail -1")
    if f"--name=Verdis {vdir}" not in eff:
        print("  quoting broken - rollback")
        sh(TGT, f"rm -f /etc/systemd/system/{tgt_unit}.service; systemctl daemon-reload")
        sh(SRC, f"systemctl enable --now {src_unit}"); failed.append(vdir); break

    sh(TGT, f"systemctl enable {tgt_unit} >/dev/null 2>&1; systemctl start {tgt_unit}")
    state = ""
    for _ in range(48):
        time.sleep(5)
        state = sh(TGT, f"systemctl is-active {tgt_unit}", timeout=60)
        if state in ("active", "failed"):
            break
    print(f"  target is-active: {state}")
    if state != "active":
        print(" ", sh(TGT, f"journalctl -u {tgt_unit} -n 6 --no-pager | tail -6 | cut -c1-150"))
        sh(TGT, f"systemctl disable --now {tgt_unit}")
        sh(SRC, f"systemctl enable --now {src_unit}")
        failed.append(vdir); break

    time.sleep(25)
    chain = sh(TGT, f"curl -s -m 8 -H 'Content-Type: application/json' "
                    f"-d '{{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"system_chain\",\"params\":[]}}' "
                    f"http://localhost:{rpc} | grep -oP 'result\":\"\\K[^\"]+'")
    roles = sh(TGT, f"curl -s -m 8 -H 'Content-Type: application/json' "
                    f"-d '{{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"system_nodeRoles\",\"params\":[]}}' "
                    f"http://localhost:{rpc} | grep -oP 'result\":\\K.*'")
    eq = sum(int(sh(h, "journalctl -u 'verdis*' --since '3 min ago' --no-pager 2>/dev/null "
                      "| grep -ci equivocat") or 0) for h in (SRC, TGT))
    b1, f1 = finality()
    print(f"  chain={chain} roles={roles} equivocation={eq} finality={f0}->{f1}")
    if "Mainnet" not in str(chain) or "Authority" not in str(roles) or eq > 0:
        print("  verification failed - rollback")
        sh(TGT, f"systemctl disable --now {tgt_unit}")
        sh(SRC, f"systemctl enable --now {src_unit}")
        failed.append(vdir); break

    sh(SRC, f"find /data/{vdir} -type d -name keystore -exec rm -rf {{}} + 2>/dev/null; "
            f"rm -f /etc/systemd/system/{src_unit}.service; systemctl daemon-reload")
    print("  source keystore removed")
    f0 = f1 or f0
    moved.append(vdir)

print(f"\n{'='*66}")
print(f"moved: {moved}   failed: {failed}")
t1 = counts()
tot = sum(t1.values())
print(f"\n=== distribution (total {tot}, threshold 15) ===")
worst_ok = True
for h, n in t1.items():
    rem = tot - n
    ok = rem >= 15
    worst_ok &= ok
    print(f"  {h:<16} {n:>2}  -> lose it: {rem} remain, {'survives' if ok else 'FINALITY STOPS'}")
b, f = finality()
print(f"\n  chain: best={b} finalized={f} lag={b - f if b else '?'}")
print(f"  ANY single host can fail without halting finality: {'YES' if worst_ok else 'NO'}")
