#!/usr/bin/env bash
# Add /api/v2 to the APEX vhost.
#
# Earlier mistake: the block went into api-verdischain-com.conf, which serves
# api.verdischain.com - not the apex. verdischain.com/api/v1 is served by
# verdischain-com.conf, which has its own `location /api/v1/` proxying to :4400.
# That is why verdischain.com/api/v2/status returned text/html: no v2 location existed
# there, so the request fell through to the static SPA.
#
# The apex matters because the explorer frontend hardcodes API = 'https://verdischain.com/api'.
# Insert v2 directly after the existing v1 block so both live in the same server context.
set -u
K=~/.ssh/id_ed25519
H=root@91.98.160.145
S() { timeout 280 ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i "$K" "$H" "$@"; }
TS=$(date +%Y%m%d-%H%M%S)
P=/etc/nginx/sites-enabled/verdischain-com.conf

echo "=== текущий /api/v1 в apex ==="
S "grep -n -A3 'location /api/v1/' $P | head -8 | sed 's/^/  /'"

if S "grep -c 'location /api/v2/' $P" | grep -qv '^0$'; then
  echo "  v2 уже есть"
else
  cat > /tmp/v2apex.conf <<'CONF'

    # Index-backed API (PostgreSQL). The explorer frontend hardcodes
    # API = 'https://verdischain.com/api', so v2 must exist on the APEX vhost, not only
    # on explorer.verdischain.com. /api/v1 above is untouched.
    location /api/v2/ {
        proxy_pass http://127.0.0.1:4500;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
        proxy_connect_timeout 5s;
        proxy_cache verdis_api_cache;
        proxy_cache_valid 200 5s;
        proxy_cache_use_stale error timeout updating;
        add_header X-Cache-Status $upstream_cache_status always;
    }
CONF
  scp -q -o BatchMode=yes -o StrictHostKeyChecking=no -i "$K" /tmp/v2apex.conf "$H:/tmp/v2apex.conf"
  S "cp $P $P.bak-v2apex-$TS"
  # find the end of the existing /api/v1/ block: its closing brace
  LN=$(S "awk '/location \/api\/v1\// {f=1} f && /^\s*}\s*$/ {print NR; exit}' $P")
  echo "  конец блока /api/v1 на строке: $LN"
  [ -z "$LN" ] && { echo "  не найден — прерываю"; exit 1; }
  S "sed -i '${LN}r /tmp/v2apex.conf' $P"
  echo "  вставлено после строки $LN"
fi

echo
echo "=== nginx -t ==="
if S 'nginx -t 2>&1 | grep -c successful' | grep -q 1; then
  S 'systemctl reload nginx'; echo "  ok"
else
  echo "  ОШИБКА — откат"
  S "cp $P.bak-v2apex-$TS $P && nginx -t && systemctl reload nginx"
  exit 1
fi

echo
echo "=== проверка ==="
for u in "https://verdischain.com/api/v2/status" \
         "https://verdischain.com/api/v2/stats" \
         "https://verdischain.com/api/v2/producers?limit=3" \
         "https://verdischain.com/api/v1/networks" \
         "https://verdischain.com" ; do
  R=$(timeout 20 curl -s -o /dev/null -m 15 -w '%{http_code} %{content_type}' "$u" 2>/dev/null)
  printf "  %-52s %s\n" "${u#https://}" "$R"
done
