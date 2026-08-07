#!/bin/bash
# Verdis Chain — Web Deployment Script
# Run this on the production server (91.98.160.145) to deploy all 8 pages
# Usage: bash deploy-verdis-web.sh

set -e

REPO_URL="https://github.com/Protremix/Verdischain-.git"
WEB_DIR="/opt/verdis-repo/dist/web"
TEMP_DIR="/tmp/verdis-deploy"

echo "🟢 Verdis Chain Web Deployment"
echo "=============================="

# Clone or pull latest
if [ -d "$TEMP_DIR" ]; then
  cd "$TEMP_DIR" && git pull origin master
else
  git clone --depth 1 "$REPO_URL" "$TEMP_DIR"
fi

# Backup current web files
if [ -d "$WEB_DIR" ]; then
  cp -r "$WEB_DIR" "${WEB_DIR}.backup.$(date +%Y%m%d%H%M%S)"
  echo "✓ Backed up current web files"
fi

# Create web directory if needed
mkdir -p "$WEB_DIR"

# Copy all HTML files
cp "$TEMP_DIR"/web/*.html "$WEB_DIR/"
echo "✓ Copied HTML files: $(ls "$WEB_DIR"/*.html | wc -l) pages"

# Copy any assets
if [ -d "$TEMP_DIR/web/assets" ]; then
  cp -r "$TEMP_DIR/web/assets" "$WEB_DIR/"
  echo "✓ Copied assets"
fi

# Copy favicon
if [ -f "$TEMP_DIR/web/favicon-32.png" ]; then
  cp "$TEMP_DIR/web/favicon-32.png" "$WEB_DIR/"
  echo "✓ Copied favicon"
fi

# Copy nginx config
if [ -f "$TEMP_DIR/deploy/nginx.conf" ]; then
  cp "$TEMP_DIR/deploy/nginx.conf" /etc/nginx/nginx.conf
  echo "✓ Updated nginx.conf"
fi

# Test nginx config
nginx -t && echo "✓ nginx config valid"

# Reload nginx
systemctl reload nginx
echo "✓ nginx reloaded"

# List deployed files
echo ""
echo "Deployed pages:"
ls -la "$WEB_DIR"/*.html | awk '{print "  " $NF " (" $5 " bytes)"}'
echo ""
echo "🟢 Deployment complete!"
echo "   Visit: https://verdischain.com"
