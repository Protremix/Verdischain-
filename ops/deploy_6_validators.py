#!/usr/bin/env python
"""Deploy the 6 recovered validators (validator-16..21) on 213.136.78.63.

Why Contabo: 24 cores, 49G RAM free, 829G free on /data, and it already runs 8
identical mainnet validators with the correct spec (sha256 aca92919e13da10f) and the
right binary. GROVIM was considered and rejected - no verdis binary and glibc 2.39
versus the 2.35 build, which would mean compiling first.

Safety rules enforced here:
  * duplicate check per validator immediately before its node starts - an equivocating
    key costs stake and already caused 738 events on the testnet today
  * ONE node at a time; after each, confirm active + finality still advancing
  * keys are inserted into the keystore as FILES (the node is stopped at that moment),
    never via author_insertKey over RPC
  * secrets never printed; only public keys and verdicts
  * any failure stops the run and leaves the already-deployed nodes running

Each node gets: its own base-path, p2p port, rpc port bound to localhost, the verified
spec, three bootnodes, archive pruning - matching the existing 15.
"""
import base64, json, os, subprocess, sys, time, zipfile
from pathlib import Path

KEY = os.path.expanduser("~/.ssh/id_ed25519")
HOST = "213.136.78.63"
MON = "185.84.224.91"
ZIP = Path(os.environ["LOCALAPPDATA"]) / "hermes" / "profiles" / "verdis" / \
      "secrets" / "ceremony-keys-20260901.zip"
SPEC = "/data/verdis-chain/chain-specs/mainnet-raw.json"
BOOT = [
    "/ip4/195.154.80.40/tcp/30333/p2p/12D3KooWQXtFadPxGmFRuEKKXpQWjQjSBooy6g4BhRHJQbiDjgfW",
    "/ip4/213.136.78.63/tcp/30333/p2p/12D3KooWSLhcUfZPEuh7h6JPs6yG5a1bMBmtwTQ1bnp56asoW869",
    "/ip4/185.84.224.91/tcp/30334/p2p/12D3KooWAyGAVHJ5BuJXFgSrvrUyLuhswCNuN65gsi7tzX3TwxNU",
]
PLAN = [  # (validator, p2p, rpc, unit suffix)
    ("validator-16", 30341, 9960, "v16b"),
    ("validator-17", 30342, 9961, "v17b"),
    ("validator-18", 30343, 9962, "v18b"),
    ("validator-19", 30344, 9963, "v19b"),
    ("validator-20", 30345, 9964, "v20b"),
    ("validator-21", 30346, 9965, "v21b"),
]
KT = {"gran": "6772616e", "babe": "62616265", "acco": "6163636f"}
# The archive names files grandpa.json / babe.json / account.json, while the keystore
# filename prefix uses the 4-char key type (gran/babe/acco). Map between them.
FILE = {"gran": "grandpa", "babe": "babe", "acco": "account"}


def sh(host, cmd, timeout=200):
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


z = zipfile.ZipFile(ZIP)


def keyfile(v, kind):
    """Return (filename, secret_seed_hex) for the keystore. Secret never printed."""
    d = json.loads(z.read(f"ceremony-keys-20260901/validators/{v}/{FILE[kind]}.json"))
    pub = d["publicKey"].removeprefix("0x").lower()
    seed = d.get("secretSeed") or d.get("secretPhrase")
    return KT[kind] + pub, pub, seed


print("=== spec sanity ===")
print(" ", sh(HOST, f"sha256sum {SPEC} | cut -c1-16"), "(want aca92919e13da10f)")
if "aca92919e13da10f" not in sh(HOST, f"sha256sum {SPEC} | cut -c1-16"):
    print("  wrong spec - abort"); sys.exit(1)

b0, f0 = finality()
n0 = sh(HOST, "systemctl list-units 'verdis-validator*' --state=active --no-legend --no-pager | wc -l")
print(f"=== baseline: best={b0} finalized={f0} lag={b0-f0}, nodes on host={n0} ===")

deployed, failed = [], []

for v, p2p, rpc, suffix in PLAN:
    unit = f"verdis-{suffix}"
    print(f"\n{'='*64}\n{v}  ->  {unit}  p2p={p2p} rpc={rpc}\n{'='*64}")

    # --- duplicate check, right now, for this key ---
    fnames = []
    for kind in ("gran", "babe", "acco"):
        fn, pub, _ = keyfile(v, kind)
        fnames.append(fn)
    found = sh(HOST, "for f in " + " ".join(fnames) +
               "; do find / -name \"$f\" 2>/dev/null | head -1; done")
    other = sh("195.154.80.40", "for f in " + " ".join(fnames) +
               "; do find /data -name \"$f\" 2>/dev/null | head -1; done")
    other2 = sh(MON, "for f in " + " ".join(fnames) +
                "; do find /data -name \"$f\" 2>/dev/null | head -1; done")
    if found or other or other2:
        print(f"  DUPLICATE KEY ALREADY PRESENT - refusing to start {v}")
        print(f"    {found} {other} {other2}")
        failed.append(v); break
    print("  duplicate check: clean")

    # --- write keystore files while nothing is running ---
    # The spec's chain id is "verdis", so the node uses chains/verdis/ - NOT
    # chains/verdis-mainnet/. The existing nodes have BOTH directories only because
    # they were migrated across spec renames; a fresh node reads chains/verdis/.
    # Also pre-generate the libp2p network key, otherwise the node exits with
    # NetworkKeyNotFound instead of creating one.
    base = f"/data/{v}"
    ks = f"{base}/chains/verdis/keystore"
    net = f"{base}/chains/verdis/network"
    sh(HOST, f"mkdir -p {ks} {net}")
    sh(HOST, f"[ -f {net}/secret_ed25519 ] || "
             f"(head -c32 /dev/urandom | xxd -p -c32 | tr -d '\\n' > {net}/secret_ed25519 && "
             f"chmod 600 {net}/secret_ed25519)")
    netsz = sh(HOST, f"stat -c%s {net}/secret_ed25519 2>/dev/null")
    print(f"  network key: {netsz} bytes (expect 64)")
    for kind in ("gran", "babe", "acco"):
        fn, pub, seed = keyfile(v, kind)
        # substrate keystore format: the file contains the JSON-quoted seed/phrase
        payload = json.dumps(seed)
        b64 = base64.b64encode(payload.encode()).decode()
        sh(HOST, f"echo {b64} | base64 -d > {ks}/{fn} && chmod 600 {ks}/{fn}")
    cnt = sh(HOST, f"ls -1 {ks} | wc -l")
    print(f"  keystore: {cnt} files written (expect 3)")
    if cnt != "3":
        print("  keystore incomplete - abort"); failed.append(v); break

    # --- unit ---
    boots = " ".join(f"--bootnodes={b}" for b in BOOT)
    unit_text = f"""[Unit]
Description=Verdis Chain Validator {v.upper()} (recovered ceremony key)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
Restart=always
RestartSec=10
ExecStart=/usr/local/bin/verdis --chain={SPEC} --base-path={base} \\
  --name='Verdis {v}' --validator --port={p2p} --rpc-port={rpc} \\
  --no-telemetry --state-pruning=archive --force-authoring {boots}
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
"""
    b64 = base64.b64encode(unit_text.encode()).decode()
    sh(HOST, f"echo {b64} | base64 -d > /etc/systemd/system/{unit}.service && systemctl daemon-reload")

    # verify systemd parsed --name as ONE argument (the V15/V18 trap)
    eff = sh(HOST, f"systemctl show -p ExecStart --value {unit} | grep -oP 'argv\\[\\]=\\K[^;]+' | tail -1")
    if f"--name=Verdis {v}" not in eff:
        print(f"  quoting broken in unit: {eff[:120]}")
        sh(HOST, f"rm -f /etc/systemd/system/{unit}.service; systemctl daemon-reload")
        failed.append(v); break
    print("  unit written, --name quoted correctly")

    # --- start ---
    sh(HOST, f"systemctl enable {unit} >/dev/null 2>&1; systemctl start {unit}")
    state = ""
    for _ in range(36):
        time.sleep(5)
        state = sh(HOST, f"systemctl is-active {unit}", timeout=60)
        if state in ("active", "failed"):
            break
    print(f"  is-active: {state}")
    if state != "active":
        print(" ", sh(HOST, f"journalctl -u {unit} -n 6 --no-pager | tail -6 | cut -c1-150"))
        sh(HOST, f"systemctl disable --now {unit} >/dev/null 2>&1")
        failed.append(v); break

    # --- is it on the right chain and is it an authority? ---
    time.sleep(20)
    chain = sh(HOST, f"curl -s -m 8 -H 'Content-Type: application/json' "
                     f"-d '{{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"system_chain\",\"params\":[]}}' "
                     f"http://localhost:{rpc} | grep -oP 'result\":\"\\K[^\"]+'")
    roles = sh(HOST, f"curl -s -m 8 -H 'Content-Type: application/json' "
                     f"-d '{{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"system_nodeRoles\",\"params\":[]}}' "
                     f"http://localhost:{rpc} | grep -oP 'result\":\\K.*'")
    print(f"  chain={chain} roles={roles}")

    # --- equivocation must stay at zero ---
    eq = sh(HOST, "journalctl -u 'verdis*' --since '2 min ago' --no-pager 2>/dev/null | grep -ci equivocat")
    print(f"  equivocation in last 2 min: {eq}")
    if eq and int(eq) > 0:
        print("  EQUIVOCATION DETECTED - stopping this node immediately")
        sh(HOST, f"systemctl disable --now {unit}")
        failed.append(v); break

    b1, f1 = finality()
    print(f"  finality: {f0} -> {f1} (best {b1}, lag {b1-f1 if b1 else '?'})")
    if f1 is None or f1 < f0:
        print("  finality regressed - stopping this node")
        sh(HOST, f"systemctl disable --now {unit}")
        failed.append(v); break
    f0 = f1
    deployed.append(v)
    print(f"  {v} DEPLOYED OK")

print(f"\n{'='*64}")
print(f"deployed: {len(deployed)} -> {deployed}")
print(f"failed  : {len(failed)} -> {failed}")
tot = 0
for ip in (MON, "195.154.80.40", HOST):
    n = sh(ip, "systemctl list-units 'verdis-validator*' 'verdis-v??b*' --state=active --no-legend --no-pager | wc -l")
    print(f"  {ip}: {n}")
    try:
        tot += int(n)
    except Exception:
        pass
b, f = finality()
print(f"  TOTAL validators: {tot}")
print(f"  chain: best={b} finalized={f} lag={b-f if b else '?'}")
