#!/usr/bin/env bash
# Deploy the Verdiscan API to the live server.
# Run on the server: bash scripts/deploy-verdiscan-api.sh
set -euo pipefail

REPO_DIR=$(find /opt /root /home /srv -maxdepth 4 -name "verdiscan_api.py" -path "*/web/api/*" 2>/dev/null | head -1 | xargs -r dirname 2>/dev/null | xargs -r dirname 2>/dev/null)
echo "REPO_DIR=$REPO_DIR"
if [ -z "$REPO_DIR" ]; then echo "verdiscan_api.py not found"; exit 1; fi

cd "$REPO_DIR"
git pull origin master

if sudo systemctl restart verdiscan-api 2>/dev/null; then
  echo "restarted verdiscan-api"
elif sudo systemctl restart verdis-api 2>/dev/null; then
  echo "restarted verdis-api"
else
  pkill -f verdiscan_api.py 2>/dev/null || true
  cd web/api && nohup python3 verdiscan_api.py > /var/log/verdiscan-api.log 2>&1 &
  echo "manual restart issued"
fi

sleep 3
curl -s -o /dev/null -w "stats_status=%{http_code}\n" http://127.0.0.1:4400/api/v1/stats || echo "probe failed"
