#!/bin/bash
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
BACKUP_DIR="/var/backups/verdis-chain"
mkdir -p "$BACKUP_DIR"

echo "[$TIMESTAMP] Starting daily backup..."

# Full backup tarball — node data, web files, configs, SDK
tar -czf "$BACKUP_DIR/full-backup-$TIMESTAMP.tar.gz" \
  /opt/verdis-node1-data-v5/ \
  /opt/verdis-node2-data-v5/ \
  /opt/verdis-node3-data-v5/ \
  /opt/verdis-repo/dist/web/ \
  /opt/verdis-chain-rust/verdis-dev-raw.json \
  /opt/verdis-chain-rust/sdk/ \
  /opt/verdis-chain-rust/docs/ \
  /opt/verdis-wallet/mobile/lib/ \
  /etc/systemd/system/verdis-*.service \
  /etc/nginx/sites-enabled/ \
  /etc/nginx/nginx.conf \
  --exclude="*/chains/" \
  --exclude="*/network/" \
  2>/dev/null

# Git repo backup
cd /tmp/verdischain-repo
git bundle create "$BACKUP_DIR/git-repo-$TIMESTAMP.bundle" --all 2>/dev/null

# Chain state exports via RPC
for method in chain_getHeader system_properties system_health system_peers dpos_allValidators amm_dex_getAllPools eco_getGreenScore; do
  curl -s -X POST http://localhost:9933 -H "Content-Type: application/json" \
    -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$method\",\"params\":[]}" \
    > "$BACKUP_DIR/${method}-$TIMESTAMP.json" 2>/dev/null
done

# Cleanup: keep only 7 most recent full backups and git bundles
ls -t "$BACKUP_DIR"/full-backup-*.tar.gz 2>/dev/null | tail -n +8 | xargs rm -f 2>/dev/null
ls -t "$BACKUP_DIR"/git-repo-*.bundle 2>/dev/null | tail -n +8 | xargs rm -f 2>/dev/null

# Cleanup old state files (keep 7 days)
find "$BACKUP_DIR" -name "*.json" -mtime +7 -delete 2>/dev/null

echo "[$TIMESTAMP] Backup complete: $(du -sh "$BACKUP_DIR/full-backup-$TIMESTAMP.tar.gz" 2>/dev/null | cut -f1)"
echo "[$TIMESTAMP] Total backups: $(ls "$BACKUP_DIR"/full-backup-*.tar.gz 2>/dev/null | wc -l)"
echo "[$TIMESTAMP] Disk usage: $(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)"
