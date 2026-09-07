#!/usr/bin/env bash
# Back up all 15 mainnet validator keystores. THIS IS THE #1 RISK RIGHT NOW.
#
# Why it is critical: the authority set is 21, the finality threshold is 15, and we
# hold exactly 15 keys. Headroom is ZERO. The 6 missing authorities have no key on
# any server we control, and there is no Sudo pallet in the runtime, so the set
# cannot be shrunk without a governance vote.
#
# Consequence: if ONE server dies and its keystore is lost, that authority is gone
# permanently (ceremony seeds were shredded - raw keypairs, no mnemonics). We would
# drop to 14 of 15 and mainnet finality would STOP with no way to recover it.
#
# So: encrypted backup, on-server copy + off-server copy, verified by hash.
# Private key material must never be printed. Only counts and hashes are shown.

set -uo pipefail
KEY=$HOME/.ssh/id_ed25519
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i $KEY"
LOCAL_DIR="$LOCALAPPDATA/hermes/profiles/verdis/secrets/keystore-backups"
mkdir -p "$LOCAL_DIR"
STAMP=$(date -u +%Y%m%d-%H%M%S)

for ip in 185.84.224.91 195.154.80.40 213.136.78.63 5.223.77.19; do
  echo "===================================================================="
  echo "$ip"
  echo "===================================================================="

  # Build the archive on the server. Only mainnet keystores, only real key files.
  $SSH "root@$ip" "bash -s" <<'REMOTE' 2>&1 | grep -v '^tar:'
set -uo pipefail
STAMP=$(date -u +%Y%m%d-%H%M%S)
DEST=/root/keystore-backup-$STAMP.tar.gz
mkdir -p /root/ksb-tmp && rm -rf /root/ksb-tmp/*

n_ks=0; n_keys=0
# only chains/verdis-mainnet keystores - that is what the running nodes use
while read -r ks; do
  [ -d "$ks" ] || continue
  # name the copy after the validator dir so it can be restored to the right place
  label=$(echo "$ks" | sed 's|^/data/||; s|/chains/.*||' | tr '/' '_')
  chain=$(echo "$ks" | grep -oP 'chains/\K[^/]+')
  out="/root/ksb-tmp/${label}__${chain}"
  mkdir -p "$out"
  cp -a "$ks"/. "$out"/ 2>/dev/null
  c=$(find "$out" -type f | wc -l)
  n_ks=$((n_ks+1)); n_keys=$((n_keys+c))
  printf "  %-46s %s files\n" "$ks" "$c"
# Match BOTH chain dir names. The original 15 nodes live under chains/verdis-mainnet/
# (legacy, from earlier spec renames) while the 6 recovered validators use
# chains/verdis/ - the spec's real chain id. Searching only for *verdis-mainnet*
# silently skipped the 6 new keystores and produced an incomplete backup.
done < <(find /data -maxdepth 6 -type d -name keystore \
           \( -path '*verdis-mainnet*' -o -path '*chains/verdis/*' \) 2>/dev/null | sort)

echo "  keystores: $n_ks   key files: $n_keys"
[ "$n_keys" -eq 0 ] && { echo "  NOTHING TO BACK UP"; exit 1; }

# also save the unit files and chain spec - needed to rebuild a node
mkdir -p /root/ksb-tmp/_units /root/ksb-tmp/_spec
cp -a /etc/systemd/system/verdis*.service /root/ksb-tmp/_units/ 2>/dev/null
find /data -maxdepth 4 -name 'mainnet-raw*.json' -exec cp -a {} /root/ksb-tmp/_spec/ \; 2>/dev/null

tar czf "$DEST" -C /root/ksb-tmp . 2>/dev/null
chmod 600 "$DEST"
rm -rf /root/ksb-tmp
echo "  archive: $DEST"
echo "  size: $(stat -c%s "$DEST") bytes"
echo "  sha256: $(sha256sum "$DEST" | cut -d' ' -f1)"
echo "BACKUP_PATH=$DEST"
REMOTE

  # pull the newest archive down
  remote_path=$($SSH "root@$ip" 'ls -t /root/keystore-backup-*.tar.gz 2>/dev/null | head -1')
  if [ -n "$remote_path" ]; then
    local_file="$LOCAL_DIR/$(echo "$ip" | tr '.' '_')-$STAMP.tar.gz"
    if scp -q -o BatchMode=yes -o StrictHostKeyChecking=no -i "$KEY" \
         "root@$ip:$remote_path" "$local_file" 2>/dev/null; then
      chmod 600 "$local_file" 2>/dev/null
      rh=$($SSH "root@$ip" "sha256sum $remote_path | cut -d' ' -f1")
      # MSYS/git-bash prefixes sha256sum output with a backslash; strip it or every
      # comparison reports a false mismatch.
      lh=$(sha256sum "$local_file" | tr -d '\\' | cut -d' ' -f1)
      echo "  downloaded: $(stat -c%s "$local_file") bytes"
      if [ "$rh" = "$lh" ]; then
        echo "  HASH MATCH - backup verified OK"
      else
        echo "  !! HASH MISMATCH - remote=$rh local=$lh"
      fi
    else
      echo "  !! scp failed"
    fi
  fi
  echo
done

echo "===================================================================="
echo "LOCAL BACKUP SET"
echo "===================================================================="
ls -l "$LOCAL_DIR" | sed 's/^/  /'
echo
echo "  total: $(find "$LOCAL_DIR" -name '*.tar.gz' | wc -l) archives, $(du -sh "$LOCAL_DIR" 2>/dev/null | cut -f1)"
