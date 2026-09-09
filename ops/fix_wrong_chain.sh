#!/usr/bin/env bash
# v13m and v14m on 185.84.224.91 started on the WRONG CHAIN.
#
# Their log shows: best #28, finalized #0 (0x6048…898b) - that is the bogus genesis
# 0x60488cb4… produced by /data/verdis-chain/chain-specs/mainnet-raw.json ON THIS HOST,
# which is a DIFFERENT FILE from the same path on Contabo (sha256 084ca473 vs aca92919).
# I already hit this trap once today with the public RPC node and even wrote it into
# the skill - then reused the bare path in the move script anyway.
#
# So those two validators are isolated on a private fork with 1 peer, contributing
# nothing to mainnet finality. That is why the fleet count read 19 instead of 21.
#
# Fix: point both units at the VERIFIED spec (mainnet-raw-v13-verified.json, sha256
# aca92919e13da10f, already present on this host), wipe their wrong-genesis DB but KEEP
# the keystore, restart, and confirm they join the real chain as authorities.

set -uo pipefail
KEY=$HOME/.ssh/id_ed25519
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i $KEY"
H=185.84.224.91
GOOD=/data/verdis-chain/chain-specs/mainnet-raw-v13-verified.json
WANT_GEN=0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e

echo "=== spec files on $H ==="
$SSH root@$H "for f in /data/verdis-chain/chain-specs/mainnet-raw.json $GOOD; do \
  [ -f \$f ] && echo \"  \$(sha256sum \$f | cut -c1-16) \$f\"; done"
echo "  want: aca92919e13da10f"

$SSH root@$H "bash -s" <<REMOTE 2>&1
set -uo pipefail
GOOD=$GOOD
if ! sha256sum \$GOOD | cut -c1-16 | grep -q aca92919e13da10f; then
  echo "  verified spec missing or wrong - abort"; exit 1
fi

for u in verdis-v13m verdis-v14m; do
  echo "  --- \$u ---"
  vdir=\$(systemctl show -p ExecStart --value \$u | grep -oP '(?<=--base-path=)[^ ]+' | head -1)
  echo "    base-path: \$vdir"
  systemctl stop \$u

  # keep keys, drop the wrong-genesis chain data
  keep=\$(mktemp -d)
  for ks in \$(find \$vdir -type d -name keystore 2>/dev/null); do
    rel=\$(echo \$ks | sed "s|\$vdir/||")
    mkdir -p \$keep/\$rel && cp -a \$ks/. \$keep/\$rel/ 2>/dev/null
  done
  n=\$(find \$keep -type f | wc -l)
  echo "    keystore files preserved: \$n"
  [ "\$n" -lt 3 ] && { echo "    refusing to wipe without keys"; systemctl start \$u; continue; }

  rm -rf \$vdir/chains
  # restore keystores under the chain id the spec actually declares: verdis
  mkdir -p \$vdir/chains/verdis/keystore \$vdir/chains/verdis/network
  find \$keep -type f -exec cp -a {} \$vdir/chains/verdis/keystore/ \\;
  chmod 600 \$vdir/chains/verdis/keystore/* 2>/dev/null
  head -c32 /dev/urandom | xxd -p -c32 | tr -d '\n' > \$vdir/chains/verdis/network/secret_ed25519
  chmod 600 \$vdir/chains/verdis/network/secret_ed25519
  rm -rf \$keep
  echo "    restored: \$(ls -1 \$vdir/chains/verdis/keystore | wc -l) key files"

  # repoint the unit at the verified spec
  sed -i "s|--chain=/data/verdis-chain/chain-specs/mainnet-raw.json|--chain=\$GOOD|" \
    /etc/systemd/system/\$u.service
  grep -c "mainnet-raw-v13-verified" /etc/systemd/system/\$u.service | \
    xargs -I{} echo "    spec lines updated: {}"
  systemctl daemon-reload
  systemctl reset-failed \$u 2>/dev/null
  systemctl start \$u
done

echo
echo "  waiting for both to sync onto the real chain…"
for i in \$(seq 1 40); do
  sleep 10
  ok=0
  for p in 9960 9961; do
    g=\$(curl -s -m 6 -H 'Content-Type: application/json' \
        -d '{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}' \
        http://localhost:\$p 2>/dev/null | grep -oP 'result":"\K[^"]+')
    [ "\$g" = "$WANT_GEN" ] && ok=\$((ok+1))
  done
  [ "\$ok" -eq 2 ] && break
done

for p in 9960 9961; do
  g=\$(curl -s -m 6 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}' http://localhost:\$p 2>/dev/null | grep -oP 'result":"\K[^"]+')
  b=\$(curl -s -m 6 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"chain_getHeader","params":[]}' http://localhost:\$p 2>/dev/null | grep -oP '"number":"\K0x[0-9a-f]+')
  hh=\$(curl -s -m 6 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"system_health","params":[]}' http://localhost:\$p 2>/dev/null)
  r=\$(curl -s -m 6 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"system_nodeRoles","params":[]}' http://localhost:\$p 2>/dev/null | grep -oP 'result":\K.*')
  echo "  :\$p genesis=\${g:0:18}… best=\$((b)) peers=\$(echo \$hh|grep -oP '"peers":\K[0-9]+') syncing=\$(echo \$hh|grep -oP '"isSyncing":\K(true|false)') roles=\$r"
done

echo
echo "  units: \$(systemctl list-units 'verdis-validator*' 'verdis-v??[bm]*' --state=active --no-legend --no-pager | wc -l) active on this host"
echo "  equivocation last 3 min: \$(journalctl -u 'verdis*' --since '3 min ago' --no-pager 2>/dev/null | grep -ci equivocat)"
REMOTE

echo
echo "=== want genesis: $WANT_GEN ==="
