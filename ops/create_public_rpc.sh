#!/usr/bin/env bash
# Give the mainnet a PUBLIC read-only RPC endpoint so the website can finally talk to
# the real chain instead of the testnet.
#
# Discovered: rpc.verdischain.com and verdischain.com/rpc both return genesis
# 0xf72f1241... (testnet). Everything a visitor sees comes from a chain secured by
# public dev keys. The mainnet has no public endpoint at all.
#
# Approach - a FULL NODE, not a validator:
#   * no --validator flag, EMPTY keystore -> it can never sign or equivocate, so it
#     adds zero risk to the 15/15 authority situation
#   * --rpc-methods=safe -> author_*/system_addReservedPeer are not exposed
#   * runs on 185.84.224.91 (our most idle mainnet host: load 0.50, 811G free)
#   * binds RPC to 127.0.0.1 only; the web host reaches it through an SSH tunnel,
#     so no new port is opened to the internet
#
# This script only ADDS a node. It does not touch any existing validator.

set -uo pipefail
KEY=$HOME/.ssh/id_ed25519
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i $KEY"
H=185.84.224.91

echo "=== baseline: do not disturb the 15 ==="
$SSH root@$H 'R(){ curl -s -m 8 -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" http://localhost:9944; }
B=$(R chain_getHeader "[]"|grep -oP "\"number\":\"\K0x[0-9a-f]+")
FH=$(R chain_getFinalizedHead "[]"|grep -oP "0x[0-9a-f]{64}")
F=$(R chain_getHeader "[\"$FH\"]"|grep -oP "\"number\":\"\K0x[0-9a-f]+")
echo "  best=$((B)) final=$((F)) lag=$(( $((B)) - $((F)) ))"
echo "  validators active: $(systemctl list-units "verdis*" --state=active --no-legend --no-pager | grep -c validator)"'

echo
echo "=== creating mainnet public full node (no keys, safe RPC) ==="
$SSH root@$H 'bash -s' <<'REMOTE' 2>&1
set -uo pipefail

# pick a free RPC port and p2p port
RPC=9955; P2P=30350
for p in $RPC $P2P; do
  if ss -tln | grep -q ":$p "; then echo "  port $p already in use - aborting"; exit 1; fi
done

SPEC=/data/verdis-chain/chain-specs/mainnet-raw.json
[ -f "$SPEC" ] || { echo "  spec not found at $SPEC"; exit 1; }
echo "  spec: $SPEC ($(stat -c%s "$SPEC") bytes)"

BASE=/data/mainnet-public-rpc
mkdir -p "$BASE"

# bootnodes: our three known-good peer identities
B1=/ip4/195.154.80.40/tcp/30333/p2p/12D3KooWQXtFadPxGmFRuEKKXpQWjQjSBooy6g4BhRHJQbiDjgfW
B2=/ip4/213.136.78.63/tcp/30333/p2p/12D3KooWSLhcUfZPEuh7h6JPs6yG5a1bMBmtwTQ1bnp56asoW869
B3=/ip4/185.84.224.91/tcp/30334/p2p/12D3KooWAyGAVHJ5BuJXFgSrvrUyLuhswCNuN65gsi7tzX3TwxNU

cat > /etc/systemd/system/verdis-public-rpc.service <<UNIT
[Unit]
Description=Verdis Mainnet Public RPC (full node, no validator keys)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
Restart=always
RestartSec=10
# NOTE: no --validator, no keys inserted. This node can never sign a block or vote,
# so it cannot cause equivocation and cannot affect the 15/21 authority threshold.
ExecStart=/usr/local/bin/verdis \\
  --chain=$SPEC \\
  --base-path=$BASE \\
  --name='Verdis Public RPC' \\
  --port=$P2P \\
  --rpc-port=$RPC \\
  --rpc-external=false \\
  --rpc-methods=safe \\
  --rpc-cors=all \\
  --no-telemetry \\
  --state-pruning=archive \\
  --bootnodes=$B1 \\
  --bootnodes=$B2 \\
  --bootnodes=$B3
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable verdis-public-rpc >/dev/null 2>&1
systemctl start verdis-public-rpc
echo "  started, waiting for it to come up..."

for i in $(seq 1 24); do
  sleep 5
  st=$(systemctl is-active verdis-public-rpc)
  [ "$st" = "active" ] && break
  [ "$st" = "failed" ] && break
done
echo "  is-active: $(systemctl is-active verdis-public-rpc)"

if [ "$(systemctl is-active verdis-public-rpc)" != "active" ]; then
  echo "  --- last log lines ---"
  journalctl -u verdis-public-rpc -n 12 --no-pager | tail -12 | cut -c1-170
  exit 1
fi

# verify it is on the MAINNET and has no keys
sleep 20
echo "  --- verification ---"
C=$(curl -s -m 8 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"system_chain","params":[]}' http://localhost:$RPC | grep -oP 'result":"\K[^"]+')
G=$(curl -s -m 8 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}' http://localhost:$RPC | grep -oP 'result":"\K[^"]+')
ROLE=$(curl -s -m 8 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"system_nodeRoles","params":[]}' http://localhost:$RPC | grep -oP 'result":\K.*' | head -c 30)
echo "    chain:   $C"
echo "    genesis: $G"
echo "    roles:   $ROLE   (must be Full, NOT Authority)"
echo "    keystore files: $(find $BASE -type d -name keystore -exec sh -c 'find "$1" -type f | wc -l' _ {} \; 2>/dev/null | paste -sd+ | bc 2>/dev/null || echo 0)  (must be 0)"
# unsafe methods must be rejected
U=$(curl -s -m 8 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"author_rotateKeys","params":[]}' http://localhost:$RPC | head -c 120)
echo "    author_rotateKeys -> $U"
echo "    peers: $(curl -s -m 8 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"system_health","params":[]}' http://localhost:$RPC | grep -oP '"peers":\K[0-9]+')"
echo "    syncing: $(curl -s -m 8 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"system_health","params":[]}' http://localhost:$RPC | grep -oP '"isSyncing":\K(true|false)')"
REMOTE

echo
echo "=== the 15 validators must be untouched ==="
$SSH root@$H 'echo "  validators active: $(systemctl list-units "verdis*" --state=active --no-legend --no-pager | grep -c "validator")"
R(){ curl -s -m 8 -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" http://localhost:9944; }
B=$(R chain_getHeader "[]"|grep -oP "\"number\":\"\K0x[0-9a-f]+")
FH=$(R chain_getFinalizedHead "[]"|grep -oP "0x[0-9a-f]{64}")
F=$(R chain_getHeader "[\"$FH\"]"|grep -oP "\"number\":\"\K0x[0-9a-f]+")
echo "  best=$((B)) final=$((F)) lag=$(( $((B)) - $((F)) ))"'
