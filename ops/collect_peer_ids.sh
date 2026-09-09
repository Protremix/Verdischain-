#!/usr/bin/env bash
# Collect the libp2p peer identity of every mainnet validator so we can build a
# multi-bootnode list. Right now every unit points at ONE bootnode
# (/ip4/195.154.80.40/tcp/30333/p2p/12D3KooWQXtFadPx...) which is a single point
# of failure: if that host is down during a restart, nodes cannot join the network.
#
# Read-only. Uses the local RPC (system_localPeerId) on each node's own rpc-port.

KEY=$HOME/.ssh/id_ed25519
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=12 -i $KEY"

for ip in 185.84.224.91 195.154.80.40 213.136.78.63; do
  echo "=== $ip ==="
  $SSH "root@$ip" 'bash -s' <<'REMOTE' 2>&1
for u in $(systemctl list-units 'verdis*' --state=active --no-legend --no-pager 2>/dev/null | awk '{print $1}' | grep '\.service$'); do
  E=$(systemctl show -p ExecStart --value "$u" 2>/dev/null)
  echo "$E" | grep -q -- '--validator' || continue
  spec=$(echo "$E" | grep -oP '(?<=--chain[= ])[^ ]+' | head -1)
  case "$(basename "${spec:-x}")" in mainnet*) ;; *) continue ;; esac
  rpc=$(echo "$E" | grep -oP '(?<=--rpc-port[= ])[0-9]+' | head -1)
  p2p=$(echo "$E" | grep -oP '(?<=--port[= ])[0-9]+' | head -1)
  [ -z "$rpc" ] && rpc=9933
  pid=$(curl -s -m 6 -H 'Content-Type: application/json' \
        -d '{"jsonrpc":"2.0","id":1,"method":"system_localPeerId","params":[]}' \
        "http://localhost:$rpc" 2>/dev/null | grep -oP 'result":"\K[^"]+')
  printf "  %-28s p2p=%-6s rpc=%-6s peer=%s\n" "$u" "${p2p:-?}" "$rpc" "${pid:-UNREADABLE}"
done
REMOTE
  echo
done
