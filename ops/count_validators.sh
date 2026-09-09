#!/usr/bin/env bash
# Count REAL mainnet validators across all three hosts now that we have SSH on all.
# Rojs wants 12 validators; we need to know what is actually running before changing anything.
# Mainnet = chain "Verdis Mainnet", genesis 0x2284393d..., spec mainnet-raw.json
# Testnet = chain "Verdis Testnet", genesis 0xf72f1241...  (different chain, ignore)

KEY=$HOME/.ssh/id_ed25519
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=12 -i $KEY"

for spec in "185.84.224.91|HostKey DE" "195.154.80.40|Online.net" "213.136.78.63|Contabo"; do
  ip="${spec%%|*}"; label="${spec##*|}"
  echo "===================================================================="
  echo "$ip   $label"
  echo "===================================================================="
  timeout 120 $SSH "root@$ip" 'bash -s' <<'REMOTE' 2>&1
mainnet=0; testnet=0; other=0
for u in $(systemctl list-units 'verdis*' --state=active --no-legend --no-pager 2>/dev/null | awk '{print $1}' | grep -E '\.service$'); do
  E=$(systemctl show -p ExecStart --value "$u" 2>/dev/null)
  spec=$(echo "$E" | grep -oP '(?<=--chain[= ])[^ ]+' | head -1)
  base=$(basename "${spec:-none}")
  isval=$(echo "$E" | grep -c -- '--validator')
  port=$(echo "$E" | grep -oP '(?<=--port[= ])[0-9]+' | head -1)
  rpc=$(echo "$E" | grep -oP '(?<=--rpc-port[= ])[0-9]+' | head -1)
  name=$(echo "$E" | grep -oP '(?<=--name[= ])"?[^"]*' | head -1)
  case "$base" in
    mainnet*) tag=MAINNET; mainnet=$((mainnet+1)) ;;
    testnet*) tag=testnet; testnet=$((testnet+1)) ;;
    *)        tag=other;   other=$((other+1)) ;;
  esac
  printf "  %-26s %-8s val=%s p2p=%-6s rpc=%-6s %s\n" "$u" "$tag" "$isval" "${port:-?}" "${rpc:-?}" "$name"
done
echo
echo "  TOTALS: mainnet_validators=$mainnet testnet=$testnet other=$other"
echo "  verdis processes running: $(pgrep -cf verdis)"
REMOTE
  echo
done

echo "===================================================================="
echo "ON-CHAIN AUTHORITY SET (from HostKey DE)"
echo "===================================================================="
timeout 90 $SSH root@185.84.224.91 'bash -s' <<'REMOTE' 2>&1
R() { curl -s -m 8 -H 'Content-Type: application/json' \
        -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" http://localhost:9944; }
A=$(R state_call '["GrandpaApi_grandpa_authorities","0x"]' | grep -oP 'result":"0x\K[0-9a-f]+')
N=$(( ${#A} / 80 ))
echo "  GRANDPA authorities in the set: $N"
echo "  threshold to finalize: $(( N * 2 / 3 + 1 ))"
B=$(R chain_getHeader '[]' | grep -oP '"number":"\K0x[0-9a-f]+')
FH=$(R chain_getFinalizedHead '[]' | grep -oP '0x[0-9a-f]{64}')
F=$(R chain_getHeader "[\"$FH\"]" | grep -oP '"number":"\K0x[0-9a-f]+')
echo "  best=$((B)) finalized=$((F)) lag=$(( $((B)) - $((F)) ))"
echo "  peers=$(R system_health '[]' | grep -oP '"peers":\K[0-9]+')"
REMOTE
