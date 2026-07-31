#!/bin/bash
set -e
echo "=== Verdis Domain Setup: verdischain.com ==="

DOMAIN="verdischain.com"

echo "Installing nginx and certbot..."
apt update -qq
apt install -y nginx certbot python3-certbot-nginx

echo "Installing nginx config..."
cp deploy/nginx-verdischain.conf /etc/nginx/sites-available/verdischain
ln -sf /etc/nginx/sites-available/verdischain /etc/nginx/sites-enabled/verdischain
rm -f /etc/nginx/sites-enabled/default

echo "Testing nginx config..."
nginx -t
systemctl reload nginx

echo "Requesting SSL certificate..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN -d rpc.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

systemctl reload nginx

echo ""
echo "=== Setup Complete! ==="
echo "  Website:   https://verdischain.com"
echo "  Dashboard: https://verdischain.com/dashboard"
echo "  RPC:       https://verdischain.com/rpc"
echo "  RPC sub:   https://rpc.verdischain.com"
echo "  Chain ID:  909 | Symbol: VRS"
echo ""

sleep 2
curl -s https://$DOMAIN/api/monitoring/health | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'  Health: {d[\"status\"]}')
print(f'  Height: {d[\"chain\"][\"height\"]}')
" 2>/dev/null || echo "  (DNS may still be propagating)"
