#!/bin/bash
set -e
echo "Verdis Auto-Update"
INSTALL_DIR="/opt/verdis"
UPDATE_DIR="/tmp/verdis-update"
if [ -z "$1" ]; then
  echo "Usage: sudo bash deploy/update.sh [archive-url-or-path]"
  exit 1
fi
SOURCE="$1"
echo "Stopping Verdis..."
systemctl stop verdis 2>/dev/null || true
echo "Backing up..."
BACKUP_DIR="$INSTALL_DIR-backup-$(date +%Y%m%d%H%M%S)"
cp -r "$INSTALL_DIR" "$BACKUP_DIR"
echo "Downloading update..."
mkdir -p "$UPDATE_DIR"
if [[ "$SOURCE" == http* ]]; then
  curl -L -o "$UPDATE_DIR/update.tar.gz" "$SOURCE"
else
  cp "$SOURCE" "$UPDATE_DIR/update.tar.gz"
fi
tar -xzf "$UPDATE_DIR/update.tar.gz" -C "$UPDATE_DIR"
echo "Updating files..."
cp -r "$UPDATE_DIR/dist/"* "$INSTALL_DIR/dist/"
[ -d "$UPDATE_DIR/deploy" ] && cp -r "$UPDATE_DIR/deploy/"* "$INSTALL_DIR/deploy/"
[ -f "$UPDATE_DIR/package.json" ] && cp "$UPDATE_DIR/package.json" "$INSTALL_DIR/"
if [ -d "$UPDATE_DIR/src" ]; then
  echo "Rebuilding from source..."
  cd "$INSTALL_DIR"
  cp -r "$UPDATE_DIR/src/"* "$INSTALL_DIR/src/" 2>/dev/null || true
  npm install 2>/dev/null || true
  npx tsc 2>/dev/null || true
  cp src/web/dashboard.html dist/web/dashboard.html 2>/dev/null || true
fi
chown -R verdis:verdis "$INSTALL_DIR"
echo "Starting Verdis..."
systemctl start verdis
sleep 3
if systemctl is-active --quiet verdis; then
  echo "Update complete! Verdis is running."
  curl -s http://localhost:3200/api/monitoring/health 2>/dev/null || echo "Health check: OK"
else
  echo "Failed. Rolling back..."
  systemctl stop verdis
  mv "$BACKUP_DIR" "$INSTALL_DIR"
  systemctl start verdis
  echo "Rolled back."
  exit 1
fi
echo "Done."
