# Verdis Blockchain Deployment

## Option A: Docker (Recommended)
docker-compose up -d
curl http://localhost:3200/api/blockchain/info

## Option B: Systemd (Linux VPS)
sudo bash deploy/setup.sh
systemctl status verdis

## Option C: Direct
npm install && npx tsc && cp src/web/dashboard.html dist/web/ && node dist/index.js

## Public URL Options
1. Nginx + Let's Encrypt (your domain) — see deploy/nginx.conf
2. Serveo tunnel: ssh -R 80:localhost:3200 serveo.net
3. Any reverse proxy (Caddy, Traefik, etc.)

## Network Config
Chain ID: 909 | Symbol: VRS | Port: 3200 | Block Time: 5s | DPoS (27 validators)
