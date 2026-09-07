#!/usr/bin/env bash
# Issue a SEPARATE Let's Encrypt certificate for blog.verdischain.com only.
#
# Why separate: --expand on the 14-name verdischain.com cert fails because
# several of those names (status, validators, wallet, ws) serve from different
# webroots or proxy to apps, so their ACME challenges 404/426. Expanding is
# all-or-nothing, so one bad name blocks blog. A dedicated single-name cert
# avoids touching the working cert entirely.
#
# The existing 14-name cert is left untouched. Verified before and after.

set -uo pipefail
DOMAIN=blog.verdischain.com
WEBROOT=/var/www/verdiscan
CONF=/etc/nginx/sites-enabled/blog-verdischain-com.conf
EMAIL=$(grep -rhoP '(?<=^email = ).*' /etc/letsencrypt/renewal/*.conf 2>/dev/null | head -1)

echo "== main cert BEFORE (must stay 14 names, untouched)"
certbot certificates 2>/dev/null | grep -A2 "Certificate Name: verdischain.com" | grep -E 'Domains|Expiry' | head -2

echo
echo "== confirm ACME path works for $DOMAIN"
mkdir -p "$WEBROOT/.well-known/acme-challenge"
T="arlo-$(date +%s)"
echo "$T" > "$WEBROOT/.well-known/acme-challenge/$T"
GOT=$(curl -s -m 10 "http://$DOMAIN/.well-known/acme-challenge/$T" 2>/dev/null)
rm -f "$WEBROOT/.well-known/acme-challenge/$T"
if [ "$GOT" = "$T" ]; then
  echo "   OK - challenge served"
else
  echo "!! challenge not served (got '${GOT:0:50}') - aborting"
  exit 1
fi

echo
echo "== requesting dedicated cert for $DOMAIN"
certbot certonly --webroot -w "$WEBROOT" \
  --cert-name "$DOMAIN" -d "$DOMAIN" \
  --non-interactive --agree-tos \
  ${EMAIL:+--email "$EMAIL"} 2>&1 | tail -12

NEWCERT="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
if [ ! -f "$NEWCERT" ]; then
  echo "!! cert was not issued - leaving nginx untouched"
  exit 1
fi
echo "   cert issued: $NEWCERT"

echo
echo "== pointing the blog vhost at its own cert"
cp -a "$CONF" "$CONF.bak-cert-$(date +%s)"
sed -i \
  -e "s#ssl_certificate /etc/letsencrypt/live/verdischain.com/fullchain.pem;#ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;#" \
  -e "s#ssl_certificate_key /etc/letsencrypt/live/verdischain.com/privkey.pem;#ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;#" \
  "$CONF"
grep -n 'ssl_certificate' "$CONF" | sed 's/^/   /'

nginx -t 2>&1 | tail -1
if ! nginx -t >/dev/null 2>&1; then
  echo "!! nginx config broken - restoring backup"
  cp -a "$(ls -t $CONF.bak-cert-* | head -1)" "$CONF"
  nginx -t 2>&1 | tail -1
  exit 1
fi
systemctl reload nginx && echo "   nginx reloaded"

echo
echo "== EXTERNAL verification"
sleep 4
for d in blog.verdischain.com verdischain.com explorer.verdischain.com \
         wallet.verdischain.com faucet.verdischain.com dex.verdischain.com \
         api.verdischain.com rpc.verdischain.com docs.verdischain.com \
         validators.verdischain.com developers.verdischain.com ws.verdischain.com; do
  printf "  %-32s %s\n" "$d" "$(curl -s -o /dev/null -w '%{http_code}' -m 12 "https://$d" 2>&1)"
done

echo
echo "== main cert AFTER (must be unchanged)"
certbot certificates 2>/dev/null | grep -A2 "Certificate Name: verdischain.com" | grep -E 'Domains|Expiry' | head -2

echo
echo "== auto-renewal covers the new cert"
certbot renew --dry-run 2>&1 | grep -iE "$DOMAIN|Congratulations|no renewals|simulating" | head -5
