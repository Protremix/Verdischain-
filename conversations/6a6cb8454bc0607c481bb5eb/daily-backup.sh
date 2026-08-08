#!/bin/bash
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
BACKUP_DIR="/var/backups/verdis-chain"
mkdir -p "$BACKUP_DIR"

echo "[$TIMESTAMP] Starting daily backup..."

# Full backup tarball
tar -czf "$BACKUP_DIR/full-backup-$TIMESTAMP.tar.gz" \
  /opt/verdis-data/ \
  /var/www/verdiscan/ \
  /opt/verdis-api/ \
  /etc/systemd/system/verdis-*.service \
  /etc/nginx/sites-enabled/ \
  /etc/nginx/nginx.conf \
  /opt/verdis-chain-rust/node-service/chain-spec.json \
  /opt/verdis-chain-rust/sdk/ \
  /opt/verdis-chain-rust/docs/ \
  --exclude="/opt/verdis-api/venv" \
  --exclude="/opt/verdis-api/__pycache__" \
  2>/dev/null

# Git repo backup
cd /tmp/verdischain-repo
git bundle create "$BACKUP_DIR/git-repo-$TIMESTAMP.bundle" --all 2>/dev/null

# Chain state exports
for method in chain_getHeader system_properties system_health dpos_allValidators amm_getAllPools; do
  curl -s -X POST http://localhost:9933 -H "Content-Type: application/json" \
    -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$method\",\"params\":[]}" \
    > "$BACKUP_DIR/${method}-$TIMESTAMP.json" 2>/dev/null
done

# Cleanup: keep only the 7 most recent full backups
ls -t "$BACKUP_DIR"/full-backup-*.tar.gz 2>/dev/null | tail -n +8 | xargs rm -f 2>/dev/null
ls -t "$BACKUP_DIR"/git-repo-*.bundle 2>/dev/null | tail -n +8 | xargs rm -f 2>/dev/null

# Cleanup old state files (keep 7 days)
find "$BACKUP_DIR" -name "*.json" -mtime +7 -delete 2>/dev/null

echo "[$TIMESTAMP] Backup complete: $(du -sh "$BACKUP_DIR/full-backup-$TIMESTAMP.tar.gz" | cut -f1)"
