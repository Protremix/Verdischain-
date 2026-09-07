#!/usr/bin/env bash
# Exercise every /api/v2 endpoint against the live index.
set -u
K=~/.ssh/id_ed25519
H=root@91.98.160.145
S() { timeout 200 ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i "$K" "$H" "$@"; }

echo "=== endpoints ==="
for p in \
  "/api/v2/health" \
  "/api/v2/stats" \
  "/api/v2/blocks?limit=3" \
  "/api/v2/block/1000" \
  "/api/v2/extrinsics?limit=3" \
  "/api/v2/transfers?limit=3" \
  "/api/v2/producers?limit=5" \
  "/api/v2/activity?days=5" \
  "/api/v2/holders?limit=3" \
  "/api/v2/search?q=1000"
do
  code=$(S "curl -s -o /dev/null -m 15 -w '%{http_code}' 'http://127.0.0.1:4500$p'")
  printf "  %-34s %s\n" "$p" "$code"
done

echo
echo "=== producers (реальное участие валидаторов) ==="
S "curl -s -m 15 'http://127.0.0.1:4500/api/v2/producers?limit=6'" | python -c "
import json,sys
d=json.load(sys.stdin)
print(f\"  блоков учтено: {d['blocks_counted']}, авторов: {d['count']}\")
for p in d['data']:
    print(f\"   {p['rank']}. {p['author'][:22]} {p['blocks']:>5} блоков  {p['share_percent']}%\")
"
echo
echo "=== stats ==="
S "curl -s -m 15 'http://127.0.0.1:4500/api/v2/stats'" | python -c "
import json,sys
d=json.load(sys.stdin)['data']
for k,v in d.items():
    print(f'  {k:<20} {v if not isinstance(v,dict) else v.get(\"amount\")}')
"
echo
echo "=== activity (график) ==="
S "curl -s -m 15 'http://127.0.0.1:4500/api/v2/activity?days=6'" | python -c "
import json,sys
for r in json.load(sys.stdin)['data']:
    print(f\"  {r['day']}  блоков={r['blocks']:<6} extrinsics={r['extrinsics']}\")
"
