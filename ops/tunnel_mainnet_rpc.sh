#!/usr/bin/env bash
# Point the public website at the MAINNET instead of the testnet.
#
# Established:
#   * rpc.verdischain.com and verdischain.com/rpc served genesis 0xf72f1241 (testnet)
#   * a synced mainnet full node now runs on 185.84.224.91:9955 (genesis 0x2284393d,
#     roles ["Full"], no keys, rpc-methods=safe, best == mainnet best)
#
# Transport: an autossh-style systemd tunnel from the web host (91.98.160.145) to
# 185.84.224.91:9955, exposed locally as 127.0.0.1:9960. No new internet-facing port
# on the validator host - nginx talks to a loopback address as it does today.
#
# Change is nginx-upstream only and fully reversible: the old upstream line is kept
# commented, and a backup of upstreams.conf is written before editing.
#
# NOT changed here: the JS bundles keep calling https://verdischain.com/rpc and
# wss://verdischain.com/ws, so no frontend rebuild is needed - the same URLs simply
# resolve to the real chain.

set -uo pipefail
KEY=$HOME/.ssh/id_ed25519
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i $KEY"
WEB=91.98.160.145
MAIN_GEN=0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e

echo "=== 1. does the web host have a key to reach the validator host? ==="
$SSH "root@$WEB" 'ls -1 /root/.ssh/ 2>/dev/null | grep -v known_hosts | sed "s/^/  /"'

echo
echo "=== 2. install a dedicated tunnel key if needed ==="
$SSH "root@$WEB" 'bash -s' <<'REMOTE' 2>&1
if [ ! -f /root/.ssh/verdis_tunnel ]; then
  ssh-keygen -t ed25519 -N '' -C 'verdis-rpc-tunnel' -f /root/.ssh/verdis_tunnel >/dev/null 2>&1
  echo "  generated /root/.ssh/verdis_tunnel"
else
  echo "  tunnel key already present"
fi
chmod 600 /root/.ssh/verdis_tunnel
echo "  PUBKEY:$(cat /root/.ssh/verdis_tunnel.pub)"
REMOTE

PUB=$($SSH "root@$WEB" 'cat /root/.ssh/verdis_tunnel.pub')
echo "  pubkey: ${PUB:0:60}..."

echo
echo "=== 3. authorise that key on 185.84.224.91, restricted to port-forwarding only ==="
$SSH root@185.84.224.91 "PUB='$PUB' bash -s" <<'REMOTE' 2>&1
set -uo pipefail
cp -a /root/.ssh/authorized_keys "/root/.ssh/authorized_keys.bak-$(date -u +%Y%m%d-%H%M%S)"
# restrict: no shell, no agent/x11, only the one forward we need
LINE="restrict,port-forwarding,permitopen=\"127.0.0.1:9955\" $PUB"
if grep -qF "$PUB" /root/.ssh/authorized_keys 2>/dev/null; then
  echo "  key already authorised"
else
  echo "$LINE" >> /root/.ssh/authorized_keys
  echo "  appended restricted key"
fi
chmod 600 /root/.ssh/authorized_keys
echo "  authorized_keys now: $(grep -c '^' /root/.ssh/authorized_keys) lines"
REMOTE

echo
echo "=== 4. create the tunnel service on the web host ==="
$SSH "root@$WEB" 'bash -s' <<'REMOTE' 2>&1
set -uo pipefail
cat > /etc/systemd/system/verdis-mainnet-tunnel.service <<'UNIT'
[Unit]
Description=SSH tunnel to Verdis mainnet public RPC (185.84.224.91:9955)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
Restart=always
RestartSec=10
ExecStart=/usr/bin/ssh -NT -o BatchMode=yes -o StrictHostKeyChecking=no \
  -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=3 \
  -i /root/.ssh/verdis_tunnel \
  -L 127.0.0.1:9960:127.0.0.1:9955 root@185.84.224.91

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable verdis-mainnet-tunnel >/dev/null 2>&1
systemctl restart verdis-mainnet-tunnel
sleep 8
echo "  tunnel: $(systemctl is-active verdis-mainnet-tunnel)"
if [ "$(systemctl is-active verdis-mainnet-tunnel)" != "active" ]; then
  journalctl -u verdis-mainnet-tunnel -n 6 --no-pager | tail -6 | cut -c1-160
  exit 1
fi
echo "  --- what answers on 127.0.0.1:9960 ---"
echo "    chain:   $(curl -s -m 8 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"system_chain","params":[]}' http://127.0.0.1:9960 | grep -oP 'result":"\K[^"]+')"
echo "    genesis: $(curl -s -m 8 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}' http://127.0.0.1:9960 | grep -oP 'result":"\K[^"]+')"
REMOTE

echo
echo "=== 5. expected: $MAIN_GEN ==="
