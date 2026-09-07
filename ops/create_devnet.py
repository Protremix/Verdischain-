#!/usr/bin/env python
"""Stand up a real devnet node so the network selector has three working chains.

Why a devnet at all: the selector currently reports devnet as "no endpoint configured".
Rather than leave a dead option in the UI, run an actual isolated dev chain.

Design decisions, all audit-relevant:
  * `--dev` uses the well-known Alice/Bob development keys. That is fine for a DEVNET and
    ONLY for a devnet - it must never be reachable as if it were a real network. So:
      - RPC binds to 127.0.0.1 only; nginx exposes it read-only behind /api/v1
      - the selector labels it Devnet, and the API reports its genesis separately
      - it uses --tmp so state is discarded on restart; nothing of value accumulates
  * Separate ports from every existing chain (p2p 30399, rpc 9970) so it cannot be
    confused with mainnet (9960) or testnet (9934), and cannot peer with them: a dev
    chain has its own genesis, so gossip is rejected by protocol anyway.
  * Runs as its own systemd unit with the same hardening as the API service, memory
    capped, so a runaway dev chain cannot starve the web host or the tunnel that the
    public mainnet RPC depends on.

Explicitly NOT touched: mainnet validators, the tunnel, the testnet nodes.
"""
import base64
import os
import subprocess
import sys
import time

HOST = "91.98.160.145"
KEY = os.path.expanduser("~/.ssh/id_ed25519")
BIN = "/opt/verdis-chain-rust/target/release/verdis"
RPC_PORT = 9970
P2P_PORT = 30399
UNIT = "verdis-devnet"


def ssh(cmd, timeout=280):
    p = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=15", "-i", KEY, f"root@{HOST}", cmd],
        capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip()


print("=== preflight ===")
print(f"  binary : {ssh(f'test -x {BIN} && {BIN} --version 2>/dev/null | head -1')}")
print(f"  :{RPC_PORT} free : {'no' if ssh(f'ss -tln | grep -c :{RPC_PORT}') != '0' else 'yes'}")
print(f"  :{P2P_PORT} free: {'no' if ssh(f'ss -tln | grep -c :{P2P_PORT}') != '0' else 'yes'}")

# does this binary accept --dev?
helptext = ssh(f"{BIN} --help 2>&1 | grep -cE '^\\s+--dev\\b'")
print(f"  --dev supported: {'yes' if helptext != '0' else 'NO'}")
if helptext == "0":
    print("  binary has no --dev flag; refusing to guess at a chain spec")
    sys.exit(1)

unit = f"""[Unit]
Description=Verdis Devnet (isolated dev chain, ephemeral state)
Documentation=https://github.com/Protremix/Verdischain-/blob/master/services/README.md
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
# --dev uses the well-known Alice/Bob development keys. Acceptable ONLY because this is
# an isolated dev chain: RPC is bound to loopback, state is ephemeral (--tmp), and its
# genesis differs from mainnet/testnet so it cannot peer with them.
ExecStart={BIN} \\
  --dev \\
  --tmp \\
  --name "Verdis Devnet" \\
  --rpc-port {RPC_PORT} \\
  --port {P2P_PORT} \\
  --rpc-methods safe \\
  --rpc-cors all \\
  --no-telemetry \\
  --no-prometheus \\
  -l error
Restart=always
RestartSec=10
User=root
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ProtectKernelTunables=true
ProtectKernelModules=true
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX
# a dev chain must never be able to starve the host that carries the public mainnet RPC
MemoryMax=3G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
"""

print("\n=== installing unit ===")
ssh(f"echo {base64.b64encode(unit.encode()).decode()} | base64 -d > /etc/systemd/system/{UNIT}.service")
ssh("systemctl daemon-reload")
ssh(f"systemctl enable --now {UNIT} 2>&1 | tail -1")
time.sleep(14)
state = ssh(f"systemctl is-active {UNIT}")
print(f"  state: {state}")
if state != "active":
    print(ssh(f"journalctl -u {UNIT} -n 25 --no-pager | tail -25"))
    sys.exit(1)

print("\n=== devnet responding? ===")
for attempt in range(6):
    chain = ssh(f"""curl -s -m 10 -H 'Content-Type: application/json' """
                f"""-d '{{"jsonrpc":"2.0","id":1,"method":"system_chain","params":[]}}' """
                f"""http://127.0.0.1:{RPC_PORT} | grep -oP 'result":"\\K[^"]+'""")
    if chain:
        break
    time.sleep(5)
gen = ssh(f"""curl -s -m 10 -H 'Content-Type: application/json' """
          f"""-d '{{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}}' """
          f"""http://127.0.0.1:{RPC_PORT} | grep -oP 'result":"\\K[^"]+'""")
hdr = ssh(f"""curl -s -m 10 -H 'Content-Type: application/json' """
          f"""-d '{{"jsonrpc":"2.0","id":1,"method":"chain_getHeader","params":[]}}' """
          f"""http://127.0.0.1:{RPC_PORT} | grep -oP 'number":"0x\\K[0-9a-f]+'""")
print(f"  chain  : {chain}")
print(f"  genesis: {gen}")
print(f"  block  : {int(hdr, 16) if hdr else '?'}")

if not gen:
    print("  devnet did not answer - leaving the unit stopped")
    ssh(f"systemctl disable --now {UNIT}")
    sys.exit(1)

# sanity: devnet genesis must differ from the other two chains
for other, port in (("mainnet", 9960), ("testnet", 9934)):
    g = ssh(f"""curl -s -m 10 -H 'Content-Type: application/json' """
            f"""-d '{{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}}' """
            f"""http://127.0.0.1:{port} | grep -oP 'result":"\\K[^"]+'""")
    print(f"  distinct from {other}: {'yes' if g != gen else 'NO - ABORT'}")
    if g == gen:
        ssh(f"systemctl disable --now {UNIT}")
        sys.exit(1)

print(f"\nDEVNET_GENESIS={gen}")
print(f"DEVNET_RPC=http://127.0.0.1:{RPC_PORT}")
