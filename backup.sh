#!/bin/bash
# Verdis Chain Backup Script
# Backs up: chain data, nginx, systemd, web assets, prometheus, grafana, node keys
BACKUP_DIR="/var/backups/verdis-chain"
TS=$(date +%Y%m%d-%H%M%S)
BACKUP_PATH="$BACKUP_DIR/$TS"
MAX_BACKUPS=7

mkdir -p "$BACKUP_PATH"
echo "[$(date -u)] Starting backup to $BACKUP_PATH"

# 1. Chain data
tar czf "$BACKUP_PATH/chain-data.tar.gz" /opt/verdis-chain-rust/chain-spec-raw.json /opt/verdis-chain-rust/*.json 2>/dev/null
echo "  chain-data: done"

# 2. Nginx config
tar czf "$BACKUP_PATH/nginx-config.tar.gz" /etc/nginx/sites-enabled/ /etc/nginx/nginx.conf 2>/dev/null
echo "  nginx-config: done"

# 3. Systemd services
tar czf "$BACKUP_PATH/systemd.tar.gz" /etc/systemd/system/verdis-*.service /etc/systemd/system/verdis-health-monitor.service /etc/systemd/system/node-exporter.service /etc/systemd/system/prometheus.service 2>/dev/null
echo "  systemd-services: done"

# 4. Web assets
tar czf "$BACKUP_PATH/web-assets.tar.gz" /var/www/verdiscan/ 2>/dev/null
echo "  web-assets: done"

# 5. Prometheus config
tar czf "$BACKUP_PATH/prometheus.tar.gz" /etc/prometheus/ 2>/dev/null
echo "  prometheus-config: done"

# 6. Grafana config
tar czf "$BACKUP_PATH/grafana.tar.gz" /etc/grafana/grafana.ini 2>/dev/null
echo "  grafana-config: done"

# 7. Node keys
tar czf "$BACKUP_PATH/node-keys.tar.gz" /opt/verdis-chain-rust/node-*/chains 2>/dev/null
echo "  node-keys: done"

# 8. Manifest
BLOCK=$(curl -sf -X POST http://localhost:9948 -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"chain_getHeader","params":[],"id":1}' 2>/dev/null | python3 -c "import sys,json; print('#'+str(int(json.load(sys.stdin)['result']['number'],16)))" 2>/dev/null || echo "unknown")
cat > "$BACKUP_PATH/MANIFEST.txt" << MANIFEST
Verdis Chain Backup
Date: $TS
Block: $BLOCK
Services: $(systemctl list-units --type=service --state=running | grep -c verdis)
MANIFEST

# Compress
tar czf "$BACKUP_PATH.tar.gz" -C "$BACKUP_DIR" "$TS"
find "$BACKUP_PATH" -type f -delete 2>/dev/null
find "$BACKUP_PATH" -type d -empty -delete 2>/dev/null

# Clean old backups (keep last 7)
cd "$BACKUP_DIR"
COUNT=$(ls -t *.tar.gz 2>/dev/null | wc -l)
if [ "$COUNT" -gt "$MAX_BACKUPS" ]; then
    ls -t *.tar.gz 2>/dev/null | tail -n +$((MAX_BACKUPS+1)) | xargs rm -f 2>/dev/null
fi

SIZE=$(du -sh "$BACKUP_PATH.tar.gz" 2>/dev/null | awk '{print $1}')
echo "[$(date -u)] Backup complete: $BACKUP_PATH.tar.gz ($SIZE)"
echo "$(date -u) backup=$TS size=$SIZE block=$BLOCK" >> /var/log/verdis-backup.log
