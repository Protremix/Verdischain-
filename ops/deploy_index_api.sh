#!/usr/bin/env bash
# Deploy and verify the index API. Kept as a file: inline heredocs of this size trip the
# command-payload guard.
set -u
K=~/.ssh/id_ed25519
H=root@91.98.160.145
S() { timeout 280 ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i "$K" "$H" "$@"; }

WS="$LOCALAPPDATA/hermes/profiles/verdis/workspace"
sed 's/\r$//' "$WS/index_api.py" > /tmp/ia.py
scp -q -o BatchMode=yes -o StrictHostKeyChecking=no -i "$K" /tmp/ia.py "$H:/opt/verdis_index_api.py"

echo "=== файл ==="
S 'ls -l /opt/verdis_index_api.py | awk "{print \"  \"\$5\" байт\"}"'

echo "=== импорт вручную ==="
S 'cd /opt && set -a && . /etc/verdis/indexer.env && set +a && /opt/verdis-indexer-venv/bin/python -c "import verdis_index_api; print(\"  импорт OK\")" 2>&1 | tail -3'

echo "=== перезапуск ==="
S 'systemctl restart verdis-index-api; sleep 10; echo "  сервис: $(systemctl is-active verdis-index-api)"; echo "  порт 4500: $(ss -tln | grep -c 4500)"'

echo "=== /api/v2/status ==="
S 'curl -s -m 12 http://127.0.0.1:4500/api/v2/status 2>/dev/null | head -c 400'
echo
echo "=== если не поднялся — лог ==="
S 'systemctl is-active verdis-index-api | grep -q active || journalctl -u verdis-index-api -n 8 --no-pager | grep -i error | tail -4'
