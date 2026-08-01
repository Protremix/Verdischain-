#!/bin/bash
while true; do
  ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -R 80:localhost:3200 serveo.net 2>&1
  echo "Tunnel dropped, reconnecting in 3s..."
  sleep 3
done
