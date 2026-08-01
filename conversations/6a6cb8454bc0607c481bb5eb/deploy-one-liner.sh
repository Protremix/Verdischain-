#!/bin/bash
# Verdis Blockchain - One-line deployment update
# Downloads and installs all 7 redesigned pages + TPS endpoint
cd /opt/verdis && curl -L -o /tmp/verdis-update.tar.gz "https://base44.app/api/apps/6a6cb8410d1dcb778817254f/files/mp/public/6a6cb8410d1dcb778817254f/79341b8ea_verdis-updatetar.gz" && tar -xzf /tmp/verdis-update.tar.gz -C /tmp/verdis-update-dir --one-top-level 2>/dev/null || (mkdir -p /tmp/verdis-update-dir && cd /tmp/verdis-update-dir && tar -xzf /tmp/verdis-update.tar.gz) && cp -r /tmp/verdis-update-dir/dist/web/* /opt/verdis/dist/web/ && cp /tmp/verdis-update-dir/dist/api/server.js /opt/verdis/dist/api/server.js && systemctl restart verdis && sleep 2 && curl -s http://localhost:3200/status | head -5 && echo "✅ DEPLOYMENT SUCCESSFUL - All new pages live!"
