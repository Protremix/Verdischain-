#!/usr/bin/env bash
# Definitive: which gran keys exist where, which have a LIVE signing node, duplicates.
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i $HOME/.ssh/id_ed25519"
OUT="$LOCALAPPDATA/Temp/keymap.txt"
: > "$OUT"

for ip in 185.84.224.91 195.154.80.40 213.136.78.63; do
  # primary keystores only (skip .bak / .bak2 duplicates of the same node)
  $SSH "root@$ip" 'find /data -path "*/chains/*/keystore/6772616e*" 2>/dev/null' \
    | while read -r f; do
        key=$(basename "$f" | cut -c9-)
        bp=$(echo "$f" | sed -E "s#(/data/[^/]+)/chains/.*#\1#")
        echo "$ip $key $bp"
      done >> "$OUT"
done

echo "=== raw rows: $(wc -l < "$OUT") ==="

# which base-paths have a live validator process
: > "$LOCALAPPDATA/Temp/live.txt"
for ip in 185.84.224.91 195.154.80.40 213.136.78.63; do
  $SSH "root@$ip" 'ps -eo args= | grep "[/]usr/local/bin/verdis " | grep -- "--validator" | grep -oP "(?<=--base-path=)[^ ]+"' \
    | while read -r bp; do echo "$ip $bp"; done >> "$LOCALAPPDATA/Temp/live.txt"
done
echo "=== live validator base-paths ==="
cat "$LOCALAPPDATA/Temp/live.txt"
