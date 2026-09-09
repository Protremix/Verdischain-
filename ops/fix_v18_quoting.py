#!/usr/bin/env python
"""Fix verdis-validator-v18 on 185.84.224.91: my 95-bootnodes.conf drop-in lost the
quotes around --name=Verdis Validator V18, so systemd split it and the node has been
crash-looping (`the subcommand 'Validator' cannot be used with --chain`).

This is the SAME mistake I already made once today on V15 and wrote into the skill.
The bootnodes script quoted nothing; only remove_unsafe_flags.py used shlex. Rewrite
the drop-in properly, with shlex quoting and a pre-flight shlex.split assertion, then
confirm the node reaches active and finality resumes.
"""
import os, re, shlex, subprocess, sys, time

KEY = os.path.expanduser("~/.ssh/id_ed25519")
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
       "-o", "ConnectTimeout=15", "-i", KEY, "root@185.84.224.91"]
UNIT = "verdis-validator-v18.service"
CONF = f"/etc/systemd/system/{UNIT}.d/95-bootnodes.conf"

B = ["/ip4/195.154.80.40/tcp/30333/p2p/12D3KooWQXtFadPxGmFRuEKKXpQWjQjSBooy6g4BhRHJQbiDjgfW",
     "/ip4/213.136.78.63/tcp/30333/p2p/12D3KooWSLhcUfZPEuh7h6JPs6yG5a1bMBmtwTQ1bnp56asoW869"]


def run(cmd, timeout=180):
    p = subprocess.run(SSH + [cmd], capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip()


def fin():
    cmd = (r'''R(){ curl -s -m 8 -H "Content-Type: application/json" '''
           r'''-d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" '''
           r'''http://localhost:9945; }; '''
           r'''B=$(R chain_getHeader "[]"|grep -oP "\"number\":\"\K0x[0-9a-f]+"); '''
           r'''FH=$(R chain_getFinalizedHead "[]"|grep -oP "0x[0-9a-f]{64}"); '''
           r'''F=$(R chain_getHeader "[\"$FH\"]"|grep -oP "\"number\":\"\K0x[0-9a-f]+"); '''
           r'''echo "$((B)) $((F))"''')
    out = run(cmd, timeout=90)
    try:
        b, f = out.split()
        return int(b), int(f)
    except Exception:
        return None, None


print("=== stop the crash loop first ===")
print(" ", run(f"systemctl stop {UNIT}; systemctl reset-failed {UNIT}; "
               f"echo stopped=$(systemctl is-active {UNIT})"))

# Rebuild the ExecStart from the base unit (no drop-ins) so we start from clean args.
print("\n=== base unit ExecStart (drop-ins removed from consideration) ===")
run(f"mv {CONF} {CONF}.broken 2>/dev/null; systemctl daemon-reload")
argv = run(f"systemctl show -p ExecStart --value {UNIT} | grep -oP 'argv\\[\\]=\\K[^;]+' | tail -1")
print(" ", argv[:200])

if "--validator" not in argv:
    print("  cannot read a sane ExecStart - aborting"); sys.exit(1)

# strip old bootnodes, keep everything else, then re-quote properly
cleaned = re.sub(r"--bootnodes=\S+", "", argv)
cleaned = re.sub(r"\s+", " ", cleaned).strip()

toks, cur = [], ""
for piece in cleaned.split(" "):
    if piece.startswith("--") or piece.startswith("/"):
        if cur:
            toks.append(cur)
        cur = piece
    else:
        cur += " " + piece
if cur:
    toks.append(cur)

quoted = []
for t in toks:
    if "=" in t and " " in t.split("=", 1)[1]:
        k, v = t.split("=", 1)
        quoted.append(f"{k}={shlex.quote(v)}")
    else:
        quoted.append(t)
line = " ".join(quoted) + "".join(f" --bootnodes={b}" for b in B)

# PRE-FLIGHT: systemd splits like a shell, so shlex must give back the exact --name
parts = shlex.split(line)
name = [p for p in parts if p.startswith("--name")]
print(f"\n=== pre-flight ===")
print(f"  --name after split: {name}")
assert name == ["--name=Verdis Validator V18"], f"quoting still wrong: {name}"
assert "--validator" in parts and any(p.startswith("--chain=") for p in parts)
assert sum(1 for p in parts if p.startswith("--bootnodes=")) == 2
print("  quoting verified OK")

body = "[Service]\nExecStart=\nExecStart=" + line + "\n"
b64 = __import__("base64").b64encode(body.encode()).decode()
run(f"mkdir -p /etc/systemd/system/{UNIT}.d && echo {b64} | base64 -d > {CONF} "
    f"&& rm -f {CONF}.broken && systemctl daemon-reload")

eff = run(f"systemctl show -p ExecStart --value {UNIT} | grep -oP 'argv\\[\\]=\\K[^;]+' | tail -1")
print(f"\n=== effective ExecStart ===\n  {eff[:220]}")

print("\n=== starting ===")
run(f"systemctl start {UNIT}")
state = ""
for _ in range(30):
    time.sleep(6)
    state = run(f"systemctl is-active {UNIT}", timeout=60)
    if state == "active":
        break
    if state == "failed":
        break
print(f"  is-active: {state}")
if state != "active":
    print(" ", run(f"journalctl -u {UNIT} -n 6 --no-pager | tail -6 | cut -c1-160"))
    sys.exit(1)

print("\n=== finality recovery ===")
for i in range(12):
    b, f = fin()
    if b:
        print(f"  [{time.strftime('%H:%M:%S')}] best={b} finalized={f} lag={b - f}")
        if b - f < 15:
            print("  finality caught up")
            break
    time.sleep(20)

print("\n=== all validators ===")
tot = 0
for ip in ("185.84.224.91", "195.154.80.40", "213.136.78.63"):
    n = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=15", "-i", KEY, f"root@{ip}",
         "systemctl list-units 'verdis-validator*' --state=active --no-legend --no-pager | wc -l"],
        capture_output=True, text=True, timeout=90).stdout.strip()
    try:
        tot += int(n)
    except Exception:
        pass
    print(f"  {ip}: {n}")
print(f"  TOTAL: {tot} / 15")
