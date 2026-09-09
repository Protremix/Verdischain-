#!/usr/bin/env bash
# Seed node4's database from node6 (already at chain head, identical genesis+spec).
# Rationale: node4 requests blocks correctly but EVERY peer answers RequestFailure::Refused,
# so it can never sync over p2p. Copying a synced DB bypasses the broken request path.
# Safety notes:
#  - db/ holds chain data + GRANDPA aux state. It does NOT hold the node key
#    (--node-key flag) or the session keys (--dave / --ferdie flag), so node4 keeps its
#    own Dave identity after the copy.
#  - Dave inheriting Ferdie's "round already completed" markers cannot cause equivocation:
#    stored votes are Ferdie-signed; Dave simply skips voting in those rounds.
#  - node6 must be stopped for a consistent RocksDB copy. That drops voters 5 -> 4,
#    below the threshold of 5, so finality pauses for the duration.

set -euo pipefail

SRC_DB=/opt/verdis-node6-data-v6/chains/verdis-testnet/db
DST_DB=/opt/verdis-node4-data-v6/chains/verdis-testnet/db

say() { echo "== $*"; }
cb() { curl -s -m 6 -H 'Content-Type: application/json' \
        -d '{"jsonrpc":"2.0","id":1,"method":"system_syncState","params":[]}' \
        "http://localhost:$1" 2>/dev/null | grep -oP '"currentBlock":\K[0-9]+'; }

say "BEFORE"
echo "  node4 (9936): $(cb 9936)"
echo "  node6 (9938): $(cb 9938)"
echo "  disk free: $(df -h / | tail -1 | awk '{print $4}')"

say "stopping node4 + node6 for consistent copy"
systemctl stop verdis-node4 verdis-node6
sleep 4

say "source size"
du -sh "$SRC_DB"

say "replacing node4 db"
rm -rf "$DST_DB"
cp -a "$SRC_DB" "$DST_DB"
du -sh "$DST_DB"

say "restarting node6 first, then node4"
systemctl start verdis-node6
sleep 6
systemctl start verdis-node4

say "waiting 80s for both to rejoin"
sleep 80

say "AFTER - all six nodes"
for p in 9933 9934 9935 9936 9937 9938; do
  printf "  rpc:%s currentBlock=%s\n" "$p" "$(cb "$p")"
done

say "node4 recent log"
journalctl -u verdis-node4 -n 4 --no-pager | tail -4

say "node6 recent log"
journalctl -u verdis-node6 -n 2 --no-pager | tail -2

say "service states"
for u in verdis-node verdis-node2 verdis-node3 verdis-node4 verdis-node5 verdis-node6; do
  printf "  %s: %s\n" "$u" "$(systemctl is-active $u)"
done

say "disk free: $(df -h / | tail -1 | awk '{print $4}')"
