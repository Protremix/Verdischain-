#!/bin/bash
# Verdis Chain Recovery Script
# Usage: ./recover.sh <backup-tarball>

if [ -z "$1" ]; then
    echo "Usage: $0 <backup-tarball>"
    echo "Available backups:"
    ls -lt /var/backups/verdis-chain/*.tar.gz 2>/dev/null | head -10
    exit 1
fi

BACKUP="$1"
TMP_DIR=$(mktemp -d)

echo "[$(date -u)] Starting recovery from $BACKUP"

# Extract backup
tar xzf "$BACKUP" -C "$TMP_DIR"
BACKUP_CONTENTS=$(ls "$TMP_DIR")

# 1. Restore nginx config
if [ -f "$TMP_DIR/$BACKUP_CONTENTS/nginx-config.tar.gz" ]; then
    echo "  Restoring nginx config..."
    tar xzf "$TMP_DIR/$BACKUP_CONTENTS/nginx-config.tar.gz" -C /
    nginx -t && systemctl reload nginx
fi

# 2. Restore systemd services
if [ -f "$TMP_DIR/$BACKUP_CONTENTS/systemd.tar.gz" ]; then
    echo "  Restoring systemd services..."
    tar xzf "$TMP_DIR/$BACKUP_CONTENTS/systemd.tar.gz" -C /
    systemctl daemon-reload
fi

# 3. Restore web assets
if [ -f "$TMP_DIR/$BACKUP_CONTENTS/web-assets.tar.gz" ]; then
    echo "  Restoring web assets..."
    tar xzf "$TMP_DIR/$BACKUP_CONTENTS/web-assets.tar.gz" -C /
fi

# 4. Restore Prometheus config
if [ -f "$TMP_DIR/$BACKUP_CONTENTS/prometheus.tar.gz" ]; then
    echo "  Restoring Prometheus config..."
    tar xzf "$TMP_DIR/$BACKUP_CONTENTS/prometheus.tar.gz" -C /
    systemctl restart prometheus
fi

# 5. Restore Grafana config
if [ -f "$TMP_DIR/$BACKUP_CONTENTS/grafana.tar.gz" ]; then
    echo "  Restoring Grafana config..."
    tar xzf "$TMP_DIR/$BACKUP_CONTENTS/grafana.tar.gz" -C /
    systemctl restart grafana-server
fi

# 6. Restart blockchain services
echo "  Restarting blockchain services..."
for svc in verdis-rpc-1 verdis-rpc-2 verdis-val-1 verdis-val-2 verdis-val-3 verdis-val-4 verdis-val-5 verdis-boot-1 verdis-boot-2; do
    systemctl restart "$svc" 2>/dev/null
    sleep 2
done

# 7. Restart support services
systemctl restart verdis-faucet verdis-tx-bot verdis-rpc-filter verdis-health-monitor 2>/dev/null

# 8. Cleanup
find "$TMP_DIR" -type f -delete 2>/dev/null
find "$TMP_DIR" -type d -empty -delete 2>/dev/null

echo "[$(date -u)] Recovery complete"
echo "Verify: systemctl list-units | grep verdis"
echo "Verify: curl -X POST http://localhost:9948 -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"method\":\"chain_getHeader\",\"params\":[],\"id\":1}'"
