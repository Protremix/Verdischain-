#!/usr/bin/env bash
# Verified access inventory of the whole Verdis fleet.
# Tests SSH with BOTH keys, checks p2p/RPC reachability, and reports what each
# host actually runs. Nothing here is from memory - every line is measured now.

OLD=$HOME/.ssh/id_ed25519
NEW=$HOME/.ssh/verdis_contabo

# ip|label|provider|rpc_port
HOSTS="
91.98.160.145|Hetzner NBG|hetzner|9933
185.84.224.91|HostKey DE|hostkey|9944
5.223.77.19|Hetzner SIN|hetzner|9933
195.154.80.40|Online.net DC5|online|9933
213.136.78.63|Contabo Ryzen9|contabo|9933
46.17.96.12|HostKey NL|hostkey|9933
2.29.7.211|GROVIM jump|other|0
"

port_open() { timeout 8 bash -c "echo > /dev/tcp/$1/$2" 2>/dev/null; }

ssh_ok() {  # ip key -> prints keyname on success
  timeout 15 ssh -o BatchMode=yes -o StrictHostKeyChecking=no \
    -o ConnectTimeout=10 -i "$2" "root@$1" 'true' 2>/dev/null && echo "$(basename "$2")"
}

echo "VERDIS FLEET ACCESS — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "======================================================================"

ACCESS=0; NOACCESS=0

echo "$HOSTS" | while IFS='|' read -r ip label prov rpc; do
  [ -z "$ip" ] && continue

  KEYUSED=""
  for k in "$OLD" "$NEW"; do
    [ -f "$k" ] || continue
    r=$(ssh_ok "$ip" "$k")
    if [ -n "$r" ]; then KEYUSED="$r"; break; fi
  done

  if [ -n "$KEYUSED" ]; then
    printf "\n[OK]  %-16s %-16s key=%s\n" "$ip" "$label" "$KEYUSED"
    timeout 60 ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i "$HOME/.ssh/$KEYUSED" "root@$ip" '
      echo "      host   : $(hostname)  |  $(grep -oP "PRETTY_NAME=\"\K[^\"]+" /etc/os-release)"
      echo "      hw     : $(nproc) cores, $(free -g|awk "NR==2{print \$2}")G RAM (used $(free -g|awk "NR==2{print \$3}")G), disk free $(df -h /|tail -1|awk "{print \$4}")"
      echo "      load   : $(cut -d" " -f1-3 /proc/loadavg)   uptime since $(uptime -s)"
      n=$(pgrep -cf "verdis" 2>/dev/null)
      echo "      verdis : $n processes, $(systemctl list-units "verdis*" --state=active --no-legend --no-pager 2>/dev/null | wc -l) active units"
      for p in 9933 9944 9945; do
        c=$(curl -s -m 5 -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"system_chain\",\"params\":[]}" http://localhost:$p 2>/dev/null | grep -oP "result\":\"\K[^\"]+")
        [ -n "$c" ] && echo "      rpc:$p -> $c"
      done
    ' 2>/dev/null
  else
    p22=$(port_open "$ip" 22 && echo open || echo closed)
    p30=$(port_open "$ip" 30333 && echo open || echo closed)
    printf "\n[NO]  %-16s %-16s ssh22=%s  p2p30333=%s\n" "$ip" "$label" "$p22" "$p30"
    if [ "$p30" = open ]; then
      echo "      -> chain node IS running here (p2p reachable), we just cannot log in"
    fi
    if [ "$p22" = closed ]; then
      echo "      -> sshd not answering: reset in progress, or our IP is firewalled"
    fi
  fi
done

echo
echo "======================================================================"
echo "SUMMARY (recount, independent of loop subshell)"
for spec in 91.98.160.145 185.84.224.91 5.223.77.19 195.154.80.40 213.136.78.63 46.17.96.12 2.29.7.211; do
  got=""
  for k in "$OLD" "$NEW"; do
    [ -f "$k" ] || continue
    if timeout 12 ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=8 -i "$k" "root@$spec" 'true' 2>/dev/null; then
      got="yes"; break
    fi
  done
  printf "  %-16s %s\n" "$spec" "${got:+ACCESS}${got:-NO ACCESS}"
done
