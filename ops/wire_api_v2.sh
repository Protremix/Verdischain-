#!/usr/bin/env bash
# Expose /api/v2 (index-backed) through nginx, and check indexer progress.
#
# /api/v1 stays exactly as it is - it reads the node and serves the current UI. v2 is
# additive, so the frontend can migrate endpoint by endpoint with no flag day.
#
# Cache policy differs from v1 deliberately: v2 answers are computed from an index that
# only changes when a new block is indexed (~6s), so a 5s micro-cache absorbs bursts
# without ever showing stale-looking data.
set -u
K=~/.ssh/id_ed25519
H=root@91.98.160.145
S() { timeout 280 ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i "$K" "$H" "$@"; }
TS=$(date +%Y%m%d-%H%M%S)

echo "=== прогресс индексации ==="
S 'set -a; . /etc/verdis/indexer.env; set +a; PGPASSWORD="$PGPASSWORD" psql -h 127.0.0.1 -U verdis_idx -d verdis -tAc "SELECT E'\''  блоков: '\''||(SELECT count(*) FROM blocks)||E'\''\n  последний: '\''||last_indexed_block||E'\''\n  tip: '\''||coalesce(chain_tip,0)||E'\''\n  отставание: '\''||(coalesce(chain_tip,0)-last_indexed_block) FROM indexer_state"'

echo
echo "=== вставляю location /api/v2 в оба vhost ==="
cat > /tmp/v2block.conf <<'CONF'
    # Index-backed explorer API (PostgreSQL). Serves the queries a node cannot answer:
    # address history, holder rankings, search, activity charts. /api/v1 is unchanged.
    location /api/v2/ {
        proxy_pass http://127.0.0.1:4500;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
        proxy_connect_timeout 5s;
        # the index only advances when a block is indexed (~6s), so 5s costs nothing
        proxy_cache verdis_api_cache;
        proxy_cache_valid 200 5s;
        proxy_cache_use_stale error timeout updating;
        add_header X-Cache-Status $upstream_cache_status always;
    }
CONF
scp -q -o BatchMode=yes -o StrictHostKeyChecking=no -i "$K" /tmp/v2block.conf "$H:/tmp/v2block.conf"

for C in explorer-verdischain-com.conf api-verdischain-com.conf; do
  P="/etc/nginx/sites-enabled/$C"
  if ! S "test -f $P && echo y" | grep -q y; then echo "  $C: нет файла"; continue; fi
  if S "grep -c 'location /api/v2/' $P" | grep -qv '^0$'; then echo "  $C: уже есть"; continue; fi
  S "cp $P $P.bak-v2-$TS"
  LN=$(S "grep -n 'location / {' $P | tail -1 | cut -d: -f1")
  if [ -z "$LN" ]; then echo "  $C: не найден location / {"; continue; fi
  S "sed -i '$((LN-1))r /tmp/v2block.conf' $P"
  echo "  $C: вставлено перед строкой $LN"
done

echo
echo "=== nginx -t ==="
if S 'nginx -t 2>&1 | grep -c "successful"' | grep -q 1; then
  S 'systemctl reload nginx'
  echo "  ok, перезагружен"
else
  echo "  ОШИБКА КОНФИГА — откат"
  S "for C in explorer-verdischain-com.conf api-verdischain-com.conf; do P=/etc/nginx/sites-enabled/\$C; [ -f \$P.bak-v2-$TS ] && cp \$P.bak-v2-$TS \$P; done; nginx -t && systemctl reload nginx"
  exit 1
fi

echo
echo "=== проверка ИЗ ИНТЕРНЕТА ==="
for u in "https://explorer.verdischain.com/api/v2/status" \
         "https://explorer.verdischain.com/api/v2/stats" \
         "https://explorer.verdischain.com/api/v2/blocks?limit=2" \
         "https://explorer.verdischain.com/api/v2/producers?limit=3" \
         "https://verdischain.com/api/v2/status" ; do
  R=$(timeout 20 curl -s -o /dev/null -m 15 -w '%{http_code} %{content_type}' "$u" 2>/dev/null)
  printf "  %-58s %s\n" "${u#https://}" "$R"
done
echo
echo "=== /api/v1 не сломан? ==="
for u in "https://verdischain.com/api/v1/networks" "https://explorer.verdischain.com/api/v1/block/last"; do
  R=$(timeout 20 curl -s -o /dev/null -m 15 -w '%{http_code} %{content_type}' "$u" 2>/dev/null)
  printf "  %-58s %s\n" "${u#https://}" "$R"
done
