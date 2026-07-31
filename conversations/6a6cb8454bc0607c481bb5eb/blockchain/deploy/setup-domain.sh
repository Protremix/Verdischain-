#!/bin/bash
set -e
echo "=== Verdis Domain Setup: verdis.eco ==="

DOMAIN="verdis.eco"

echo "Installing nginx and certbot..."
apt update -qq
apt install -y nginx certbot python3-certbot-nginx

echo "Installing nginx config..."
cp deploy/nginx-verdis.eco.conf /etc/nginx/sites-available/verdis.eco
ln -sf /etc/nginx/sites-available/verdis.eco /etc/nginx/sites-enabled/verdis.eco
rm -f /etc/nginx/sites-enabled/default

echo "Testing nginx config..."
nginx -t

echo "Reloading nginx..."
systemctl reload nginx

echo "Requesting SSL certificate..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN -d rpc.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

echo "Reloading nginx with SSL..."
systemctl reload nginx

echo ""
echo "=== Setup Complete! ==="
echo "  Website:   https://verdis.eco"
echo "  Dashboard: https://verdis.eco/dashboard"
echo "  RPC:       https://verdis.eco/rpc (or https://rpc.verdis.eco)"
echo "  Chain ID:  909"
echo "  Symbol:    VRS"
echo ""

# Verify
echo "Testing..."
sleep 2
curl -s https://$DOMAIN/api/monitoring/health | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'  Health: {d[\"status\"]}')
print(f'  Height: {d[\"chain\"][\"height\"]}')
print(f'  Uptime: {d[\"uptime\"][\"human\"]}')
" 2>/dev/null || echo "  (DNS may still be propagating — try again in a few minutes)"

