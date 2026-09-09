#!/usr/bin/env python
"""Remove unsafe RPC exposure from ONE live Verdis mainnet validator.

Why Python: the ExecStart contains --name=Verdis Validator V19 (spaces).
Rebuilding that line with shell string munging loses the quoting and the node
dies with "the subcommand 'Validator' cannot be used with --chain". systemd
reports argv as a proper list, so we edit the list and re-quote correctly.

Safety: verifies chain health before, polls until the RPC answers after, and
rolls the drop-in back automatically if the node does not come up.
Rollback by hand: rm the drop-in, systemctl daemon-reload, systemctl restart <unit>.
"""
import json
import re
import shlex
import subprocess
import sys
import time

UNIT = sys.argv[1]
PORT = sys.argv[2]
DROPIN = f"/etc/systemd/system/{UNIT}.service.d/90-safe-rpc.conf"
DROP = {"--unsafe-rpc-external", "--rpc-external", "--rpc-methods=unsafe", "--rpc-cors=all"}


def sh(cmd, check=False):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and r.returncode != 0:
        print(f"!! command failed: {cmd}\n{r.stderr}")
        sys.exit(1)
    return r.stdout.strip()


def rpc(method, port=9944, params="[]"):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": json.loads(params)})
    out = sh(f"curl -s -m 8 -H 'Content-Type: application/json' "
             f"-d {shlex.quote(body)} http://localhost:{port}")
    try:
        return json.loads(out)
    except Exception:
        return {}


def chain_state():
    b = rpc("chain_getHeader").get("result", {}).get("number")
    fh = rpc("chain_getFinalizedHead").get("result")
    f = None
    if fh:
        f = rpc("chain_getHeader", params=json.dumps([fh])).get("result", {}).get("number")
    bi = int(b, 16) if b else None
    fi = int(f, 16) if f else None
    return bi, fi


# --- read current argv exactly as systemd holds it -------------------------
raw = sh(f"systemctl show -p ExecStart --value {UNIT}")
m = re.search(r"argv\[\]=(.*?) ; ignore_errors", raw)
if not m:
    print("!! could not parse ExecStart argv")
    print(raw[:500])
    sys.exit(1)

argv_str = m.group(1)
parts = argv_str.split()
binary, args = parts[0], parts[1:]

# Re-group tokens: an element that does not start with "-" and follows a
# "--flag=value" belongs to that value (systemd flattened the spaces).
grouped = []
for tok in args:
    if tok.startswith("--") or not grouped:
        grouped.append(tok)
    else:
        grouped[-1] += " " + tok

print(f"== unit    : {UNIT}")
print(f"== binary  : {binary}")
removing = [g for g in grouped if g.split("=")[0] in {d.split('=')[0] for d in DROP} and
            (g in DROP or g.split("=")[0] in {"--unsafe-rpc-external", "--rpc-external"})]
print("== removing:", removing or "(nothing found)")

kept = [g for g in grouped if g not in DROP]
still = [k for k in kept if k in DROP]
if still:
    print("!! unsafe flag survived:", still)
    sys.exit(1)

# quote any arg containing whitespace so systemd/clap see one token
def q(a):
    if " " in a:
        if "=" in a:
            k, v = a.split("=", 1)
            return f'{k}="{v}"'
        return f'"{a}"'
    return a


new_exec = binary + " " + " ".join(q(a) for a in kept)
print("== new ExecStart:")
print("   " + new_exec)

b0, f0 = chain_state()
print(f"== chain before: best={b0} finalized={f0} lag={(b0 - f0) if b0 and f0 else 'NA'}")
print(f"== peers before: {json.dumps(rpc('system_health').get('result'))}")

sh(f"mkdir -p {shlex.quote(DROPIN.rsplit('/', 1)[0])}", check=True)
conf = (
    f"# Written by Arlo {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
    f"# Removes unsafe RPC exposure from a live mainnet authority.\n"
    f"# Rollback: rm {DROPIN} && systemctl daemon-reload && systemctl restart {UNIT}\n"
    f"[Service]\n"
    f"ExecStart=\n"
    f"ExecStart={new_exec}\n"
)
with open(DROPIN, "w") as fh:
    fh.write(conf)

sh("systemctl daemon-reload", check=True)
print("== drop-in written, restarting")
sh(f"systemctl restart {UNIT}")

ok = False
for i in range(1, 21):
    time.sleep(6)
    st = sh(f"systemctl is-active {UNIT}")
    ans = rpc("system_chain", port=PORT).get("result", "")
    if "Verdis" in str(ans):
        print(f"== poll {i}: state={st}, RPC -> {ans}  healthy")
        ok = True
        break
    print(f"== poll {i}: state={st}, RPC silent")

if not ok:
    print("!! not healthy - rolling back")
    print(sh(f"journalctl -u {UNIT} -n 12 --no-pager | tail -12"))
    sh(f"rm -f {DROPIN}")
    sh("systemctl daemon-reload")
    sh(f"systemctl restart {UNIT}")
    time.sleep(20)
    print("   after rollback:", sh(f"systemctl is-active {UNIT}"))
    sys.exit(1)

print("== effective flags now:")
eff = sh(f"systemctl show -p ExecStart --value {UNIT}")
print("   unsafe present:", "YES" if ("unsafe" in eff or "rpc-cors=all" in eff) else "NO")

print("== waiting 60s to confirm finality advances")
time.sleep(60)
b1, f1 = chain_state()
print(f"== chain after : best={b1} finalized={f1} lag={(b1 - f1) if b1 and f1 else 'NA'}")
print(f"== peers after : {json.dumps(rpc('system_health').get('result'))}")
if f0 and f1:
    print(f"== finality {f0} -> {f1} (+{f1 - f0})", "OK" if f1 > f0 else "STALLED")

print(f"== listener on {PORT} (must be loopback only):")
print(sh(f"ss -tlnp | grep ':{PORT}' || echo '   not listening'"))
