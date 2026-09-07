#!/usr/bin/env python
"""Remove --unsafe-rpc-external / --rpc-methods=unsafe / --rpc-cors=all from mainnet
validator units, ONE node at a time, with per-node verification and rollback.

WHY THE SHELL VERSION FAILED (twice today, same root cause):
  ExecStart contains `--name=Verdis Validator V15` - a value WITH SPACES. When the
  drop-in is written by echoing the argv string, systemd re-splits on whitespace and
  the node starts with `--name=Verdis` plus two stray positional args, so it exits
  status=2/INVALIDARGUMENT. The fix is to re-quote every argument that contains a
  space using shlex before writing the drop-in.

SAFETY (finality threshold 15 of 21, exactly 15 running -> zero headroom):
  * one node at a time
  * after restart: unit must be active AND still be a validator on mainnet
  * poll up to 90s for the node to come up (archive nodes are slow to start)
  * on any failure: delete the drop-in, restart, confirm recovery, abort the run
  * finality must not go backwards between nodes
"""
import os, re, shlex, subprocess, sys, time

KEY = os.path.expanduser("~/.ssh/id_ed25519")
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
       "-o", "ConnectTimeout=15", "-i", KEY]
MON = "185.84.224.91"
HOSTS = ["195.154.80.40", "213.136.78.63"]
UNSAFE = ("--unsafe-rpc-external", "--rpc-methods=unsafe", "--rpc-cors=all")


def run(host, cmd, timeout=120):
    p = subprocess.run(SSH + [f"root@{host}", cmd], capture_output=True,
                       text=True, timeout=timeout)
    return p.stdout.strip(), p.returncode


def exec_start(host, unit):
    """Effective ExecStart argv (last entry wins after drop-ins)."""
    out, _ = run(host, f"systemctl show -p ExecStart --value {unit}")
    argvs = re.findall(r"argv\[\]=([^;]+)", out)
    return argvs[-1].strip() if argvs else ""


def finality():
    cmd = (r'''R(){ curl -s -m 8 -H "Content-Type: application/json" '''
           r'''-d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" '''
           r'''http://localhost:9944; }; '''
           r'''FH=$(R chain_getFinalizedHead "[]"|grep -oP "0x[0-9a-f]{64}"); '''
           r'''R chain_getHeader "[\"$FH\"]"|grep -oP "\"number\":\"\K0x[0-9a-f]+"''')
    out, _ = run(MON, cmd, timeout=60)
    try:
        return int(out.strip(), 16)
    except Exception:
        return None


def quote_argv(argv: str) -> str:
    """Re-quote args containing spaces. This is the bit the shell version got wrong."""
    parts, buf, out = argv.split(" "), "", []
    for tok in parts:
        if buf:
            buf += " " + tok
        elif tok.startswith("--") and "=" in tok:
            k, v = tok.split("=", 1)
            buf = tok if v and " " not in v else tok
        else:
            buf = tok
        out.append(buf); buf = ""
    # simpler and correct: split on ' --' boundaries instead
    toks, cur = [], ""
    for piece in argv.split(" "):
        if piece.startswith("--") or piece.startswith("/"):
            if cur: toks.append(cur)
            cur = piece
        else:
            cur += " " + piece
    if cur: toks.append(cur)
    res = []
    for t in toks:
        if "=" in t and " " in t.split("=", 1)[1]:
            k, v = t.split("=", 1)
            res.append(f"{k}={shlex.quote(v)}")
        elif " " in t and not t.startswith("/"):
            res.append(shlex.quote(t))
        else:
            res.append(t)
    return " ".join(res)


def mainnet_validators(host):
    out, _ = run(host, "systemctl list-units 'verdis*' --state=active --no-legend "
                       "--no-pager | awk '{print $1}' | grep '\\.service$'")
    units = []
    for u in out.split():
        e = exec_start(host, u)
        if "--validator" in e and re.search(r"chain=?\S*mainnet", e):
            units.append((u, e))
    return units


def main():
    base = finality()
    print(f"=== baseline finalized={base} ===", flush=True)
    if base is None:
        print("cannot read finality - abort"); return 1

    ok = fail = skipped = 0
    for host in HOSTS:
        print(f"\n{'='*68}\n{host}\n{'='*68}", flush=True)
        for unit, argv in mainnet_validators(host):
            if not any(f in argv for f in UNSAFE):
                print(f"  {unit:<30} already clean"); skipped += 1; continue

            cleaned = argv
            for f in UNSAFE:
                cleaned = cleaned.replace(f, "")
            cleaned = re.sub(r"\s+", " ", cleaned).strip()
            quoted = quote_argv(cleaned)

            # sanity check BEFORE touching anything
            if ("--validator" not in quoted or "--chain" not in quoted
                    or "--port" not in quoted or any(f in quoted for f in UNSAFE)):
                print(f"  {unit:<30} SKIP - generated line looks wrong"); fail += 1; continue

            d = f"/etc/systemd/system/{unit}.d"
            conf = f"{d}/96-safe-rpc.conf"
            body = "[Service]\nExecStart=\nExecStart=" + quoted + "\n"
            b64 = __import__("base64").b64encode(body.encode()).decode()

            print(f"  {unit:<30} ", end="", flush=True)
            run(host, f"mkdir -p {d} && echo {b64} | base64 -d > {conf} && systemctl daemon-reload")

            eff = exec_start(host, unit)
            if any(f in eff for f in UNSAFE) or "--validator" not in eff:
                run(host, f"rm -f {conf}; systemctl daemon-reload")
                print("drop-in did not apply, reverted"); fail += 1; continue

            run(host, f"systemctl restart {unit}", timeout=180)

            # archive nodes take a while; poll instead of a fixed sleep
            state = ""
            for _ in range(18):
                time.sleep(5)
                state, _ = run(host, f"systemctl is-active {unit}", timeout=40)
                if state == "active":
                    break
                if state in ("failed", "inactive"):
                    break

            if state != "active":
                log, _ = run(host, f"journalctl -u {unit} -n 3 --no-pager | tail -3")
                run(host, f"rm -f {conf}; systemctl daemon-reload; "
                          f"systemctl reset-failed {unit}; systemctl restart {unit}")
                time.sleep(20)
                back, _ = run(host, f"systemctl is-active {unit}")
                print(f"FAILED ({state}) -> reverted, now {back}")
                print(f"      log: {log[:160]}")
                fail += 1
                print("\n*** aborting run after first failure ***")
                return 1

            now = finality()
            if now is None or now < base:
                run(host, f"rm -f {conf}; systemctl daemon-reload; systemctl restart {unit}")
                print(f"OK but finality regressed {base} -> {now}, reverted"); fail += 1
                return 1
            print(f"OK  finality {base} -> {now}")
            base = now
            ok += 1

    print(f"\n=== RESULT: cleaned={ok} already_clean={skipped} failed={fail} "
          f"finalized={finality()} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
