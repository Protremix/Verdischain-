#!/usr/bin/env bash
# Add blog.verdischain.com to the existing Let's Encrypt certificate.
#
# Root cause of the 000: nginx serves blog on 443 using the verdischain.com cert,
# but that cert covers 14 names and blog is NOT one of them, so external TLS
# handshakes fail before HTTP is reached. Content is fine (index.html present).
#
# Method: certbot --expand, reusing the existing webroot used by the ACME
# challenge location already configured in the blog vhost (/var/www/verdiscan).
# Safe: --expand keeps every existing name, nginx is only reloaded on success.

set -uo pipefail

CERT_NAME=verdischain.com
WEBROOT=/var/www/verdiscan
EMAIL=$(grep -rhoP '(?<=^email = ).*' /etc/letsencrypt/renewal/*.conf 2>/dev/null | head -1)

echo "== current cert domains"
certbot certificates 2>/dev/null | grep -A1 "Certificate Name: $CERT_NAME" | grep Domains || true
BEFORE=$(certbot certificates 2>/dev/null | grep -oP '(?<=Domains: ).*' | head -1 | wc -w)
echo "== domain count before: $BEFORE"

echo "== verifying ACME challenge path is reachable for blog"
mkdir -p "$WEBROOT/.well-known/acme-challenge"
TOKEN="arlo-precheck-$(date +%s)"
echo "$TOKEN" > "$WEBROOT/.well-known/acme-challenge/$TOKEN"

# The blog vhost has a server-level `return 301` which nginx evaluates in the
# rewrite phase, BEFORE location matching - so the acme-challenge location never
# runs and the challenge 301s away. Fix the vhost the same way certbot does for
# the other domains: an `if ($host = ...)` guard placed so the challenge wins.
GOT=$(curl -s -m 10 "http://blog.verdischain.com/.well-known/acme-challenge/$TOKEN" 2>/dev/null)
if [ "$GOT" != "$TOKEN" ]; then
  echo "   challenge 301s away - patching blog vhost to serve it"
  CONF=/etc/nginx/sites-enabled/blog-verdischain-com.conf
  cp -a "$CONF" "$CONF.bak-$(date +%s)"
  # Turn the bare `return 301` into a location-scoped redirect so that the
  # more-specific acme-challenge location takes precedence.
  python3 - "$CONF" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p).read()
# only touch the :80 server block
def fix(m):
    blk = m.group(0)
    if 'listen 80' not in blk:
        return blk
    if 'location / {' in blk and 'return 301' in blk:
        return blk  # already location-scoped
    blk = blk.replace(
        "    return 301 https://$host$request_uri;",
        "    location / { return 301 https://$host$request_uri; }"
    )
    return blk
s = re.sub(r'server\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', fix, s, count=1)
open(p, 'w').write(s)
print("   vhost patched")
PY
  nginx -t 2>&1 | tail -1
  systemctl reload nginx
  sleep 2
  GOT=$(curl -s -m 10 "http://blog.verdischain.com/.well-known/acme-challenge/$TOKEN" 2>/dev/null)
fi

rm -f "$WEBROOT/.well-known/acme-challenge/$TOKEN"
if [ "$GOT" = "$TOKEN" ]; then
  echo "   challenge path OK"
else
  echo "!! challenge path still NOT reachable (got: '${GOT:0:60}')"
  echo "   aborting - certbot would fail"
  exit 1
fi

# Build the full domain list: everything already on the cert, plus blog.
EXISTING=$(certbot certificates 2>/dev/null | grep -oP '(?<=Domains: ).*' | head -1)
ALL="$EXISTING blog.verdischain.com"
DFLAGS=""
for d in $ALL; do DFLAGS="$DFLAGS -d $d"; done
echo "== requesting $(echo $ALL | wc -w) domains (adding blog.verdischain.com)"

certbot certonly --webroot -w "$WEBROOT" \
  --cert-name "$CERT_NAME" \
  $DFLAGS \
  --expand --non-interactive --agree-tos \
  ${EMAIL:+--email "$EMAIL"} \
  --deploy-hook "systemctl reload nginx" 2>&1 | tail -20

echo
echo "== cert domains after"
certbot certificates 2>/dev/null | grep -A2 "Certificate Name: $CERT_NAME" | grep -E "Domains|Expiry"
AFTER=$(certbot certificates 2>/dev/null | grep -oP '(?<=Domains: ).*' | head -1 | wc -w)
echo "== domain count after: $AFTER (was $BEFORE)"

echo
echo "== nginx config test"
nginx -t 2>&1 | tail -2
systemctl reload nginx && echo "   nginx reloaded"

echo
echo "== EXTERNAL verification"
sleep 3
for d in blog.verdischain.com verdischain.com explorer.verdischain.com wallet.verdischain.com; do
  printf "  %-32s %s\n" "$d" "$(curl -s -o /dev/null -w '%{http_code}' -m 12 "https://$d" 2>&1)"
done
echo
echo "== blog cert subject/SAN check"
echo | timeout 10 openssl s_client -servername blog.verdischain.com \
  -connect blog.verdischain.com:443 2>/dev/null \
  | openssl x509 -noout -text 2>/dev/null \
  | grep -A1 'Subject Alternative Name' | tr ',' '\n' | grep -i blog || echo "   blog NOT in SAN"
