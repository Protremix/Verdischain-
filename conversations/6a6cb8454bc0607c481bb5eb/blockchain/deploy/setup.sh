#!/bin/bash
set -e
echo "╔══════════════════════════════════════════════════╗"
echo "║  🌿 Verdis Blockchain — Deployment Setup          ║"
echo "╚══════════════════════════════════════════════════╝"
INSTALL_DIR="/opt/verdis"
USER_NAME="verdis"
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root: sudo bash deploy/setup.sh"
  exit 1
fi
if ! id -u $USER_NAME &>/dev/null; then
  useradd -r -m -d $INSTALL_DIR -s /bin/bash $USER_NAME
fi
mkdir -p $INSTALL_DIR $INSTALL_DIR/data
cp -r dist/ $INSTALL_DIR/dist/
cp -r node_modules/ $INSTALL_DIR/node_modules/
cp package*.json $INSTALL_DIR/
chown -R $USER_NAME:$USER_NAME $INSTALL_DIR
cp deploy/verdis.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable verdis
systemctl start verdis
sleep 3
if systemctl is-active --quiet verdis; then
  echo "✅ Verdis is running at http://localhost:3200"
  echo "   RPC: http://localhost:3200/rpc | Chain ID: 909 | Symbol: VRS"
  echo "   systemctl status verdis | journalctl -u verdis -f"
else
  echo "❌ Failed to start. Check: journalctl -u verdis"
  exit 1
fi
