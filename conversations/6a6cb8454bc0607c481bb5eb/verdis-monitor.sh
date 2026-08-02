#!/bin/bash
# ============================================================
# VERDIS BLOCKCHAIN MONITORING & AUTO-REPAIR DAEMON
# Runs every 60 seconds via systemd timer
# ============================================================

LOG_FILE="/var/log/verdis-monitor.log"
ALERT_FILE="/opt/verdis/data/monitor-alerts.json"
API_URL="http://localhost:3200"
MAX_BLOCK_STALENESS=30  # seconds without a new block before alert
SERVICE_NAME="verdis"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

send_alert() {
  local severity="$1"
  local message="$2"
  local details="$3"
  
  log "🚨 ALERT [$severity]: $message — $details"
  
  # Write alert to file for the workflow to pick up
  local alert_json=$(cat <<EOF
{
  "timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "severity": "$severity",
  "message": "$message",
  "details": "$details",
  "hostname": "$(hostname)",
  "service": "verdis"
}
EOF
)
  echo "$alert_json" >> "$ALERT_FILE"
  
  # Also send to a simple webhook endpoint on the blockchain API
  curl -s -X POST "$API_URL/api/monitor/alert" \
    -H "Content-Type: application/json" \
    -d "$alert_json" > /dev/null 2>&1
}

# ============================================================
# CHECK 1: Is the verdis service running?
# ============================================================
if ! systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
  log "❌ Service $SERVICE_NAME is DOWN — attempting restart..."
  systemctl restart "$SERVICE_NAME"
  sleep 5
  
  if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    send_alert "CRITICAL" "Blockchain service was down and has been RESTARTED" "Service auto-restarted successfully after being detected as down"
    log "✅ Service restarted successfully"
  else
    send_alert "CRITICAL" "Blockchain service is DOWN and auto-restart FAILED" "Manual intervention required — service could not be restarted automatically"
    log "❌ Auto-restart failed — service still down"
    exit 1
  fi
fi

# ============================================================
# CHECK 2: Is the API responding?
# ============================================================
API_RESPONSE=$(curl -s -m 10 "$API_URL/api/blockchain/info" 2>/dev/null)

if [ -z "$API_RESPONSE" ] || [ $? -ne 0 ]; then
  send_alert "WARNING" "Blockchain API is not responding" "API at $API_URL/api/blockchain/info returned empty or failed"
  log "⚠️ API not responding — checking if process is alive..."
  
  # Check if the process is consuming too much memory (potential OOM)
  MEM_USAGE=$(systemctl show "$SERVICE_NAME" --property=MemoryCurrent 2>/dev/null | cut -d= -f2)
  if [ -n "$MEM_USAGE" ] && [ "$MEM_USAGE" -gt 268435456 ]; then
    log "🔄 High memory usage (${MEM_USAGE} bytes) — restarting service..."
    systemctl restart "$SERVICE_NAME"
    sleep 5
    send_alert "WARNING" "Blockchain restarted due to high memory usage" "Memory was ${MEM_USAGE} bytes (>256MB), service restarted"
  fi
  exit 0
fi

# ============================================================
# CHECK 3: Is block production happening?
# ============================================================
BLOCK_HEIGHT=$(echo "$API_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('height',0))" 2>/dev/null)
CHAIN_VALID=$(echo "$API_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('chainValid',False))" 2>/dev/null)
MEMPOOL_SIZE=$(echo "$API_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('mempoolSize',0))" 2>/dev/null)

# Check block staleness via the health endpoint
HEALTH_RESPONSE=$(curl -s -m 10 "$API_URL/api/health" 2>/dev/null)
LAST_BLOCK_TIME=$(echo "$HEALTH_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('blockStalenessMs',999999))" 2>/dev/null)

if [ -z "$BLOCK_HEIGHT" ] || [ "$BLOCK_HEIGHT" = "0" ]; then
  send_alert "CRITICAL" "Block height is 0 or unreadable" "API returned height=$BLOCK_HEIGHT"
  exit 0
fi

if [ "$CHAIN_VALID" = "False" ]; then
  send_alert "CRITICAL" "Chain validation FAILED" "Blockchain reports chainValid=false — possible tampering or corruption"
  log "❌ Chain invalid — this is critical and requires manual investigation"
  exit 0
fi

# Check block staleness (in ms)
if [ -n "$LAST_BLOCK_TIME" ] && [ "$LAST_BLOCK_TIME" -gt $((MAX_BLOCK_STALENESS * 1000)) ]; then
  STALE_SEC=$((LAST_BLOCK_TIME / 1000))
  log "⚠️ Block production stalled — last block ${STALE_SEC}s ago"
  
  # Auto-repair: restart the service if blocks are stalled
  if [ "$STALE_SEC" -gt 60 ]; then
    log "🔄 Block stall >60s — restarting service..."
    systemctl restart "$SERVICE_NAME"
    sleep 8
    send_alert "WARNING" "Block production stalled — service restarted" "Last block was ${STALE_SEC}s old, service auto-restarted"
    
    # Verify restart fixed it
    NEW_HEALTH=$(curl -s -m 10 "$API_URL/api/health" 2>/dev/null)
    NEW_STALE=$(echo "$NEW_HEALTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('blockStalenessMs',999999))" 2>/dev/null)
    if [ -n "$NEW_STALE" ] && [ "$NEW_STALE" -lt 15000 ]; then
      log "✅ Service restarted — block production resumed (${NEW_STALE}ms staleness)"
    else
      send_alert "CRITICAL" "Block production still stalled after restart" "Restart did not fix the issue — manual investigation needed"
    fi
  else
    send_alert "WARNING" "Block production is slow" "Last block was ${STALE_SEC}s ago (threshold: ${MAX_BLOCK_STALENESS}s)"
  fi
fi

# ============================================================
# CHECK 4: Mempool overflow
# ============================================================
if [ -n "$MEMPOOL_SIZE" ] && [ "$MEMPOOL_SIZE" -gt 900 ]; then
  log "⚠️ Mempool overflow: $MEMPOOL_SIZE transactions (limit 1000)"
  send_alert "WARNING" "Mempool near capacity" "$MEMPOOL_SIZE/1000 transactions in mempool — may need manual cleanup"
fi

# ============================================================
# CHECK 5: Disk space
# ============================================================
DISK_USAGE=$(df /opt/verdis | tail -1 | awk '{print $5}' | tr -d '%')
if [ -n "$DISK_USAGE" ] && [ "$DISK_USAGE" -gt 85 ]; then
  send_alert "WARNING" "Disk space low" "Disk usage at ${DISK_USAGE}% on /opt/verdis partition"
  log "⚠️ Disk usage at ${DISK_USAGE}%"
  
  # Auto-repair: clean old backup files
  find /opt/verdis/app/dist-backup-* -type d -mtime +7 -exec rm -rf {} \; 2>/dev/null
  find /opt/verdis -name "*.bak" -mtime +7 -exec rm -f {} \; 2>/dev/null
  log "🧹 Cleaned old backup files"
fi

# ============================================================
# CHECK 6: State file integrity
# ============================================================
STATE_FILE="/opt/verdis/app/data/blockchain-state.json"
if [ -f "$STATE_FILE" ]; then
  STATE_SIZE=$(stat -c%s "$STATE_FILE" 2>/dev/null)
  if [ -n "$STATE_SIZE" ] && [ "$STATE_SIZE" -lt 100 ]; then
    send_alert "CRITICAL" "State file may be corrupted" "blockchain-state.json is only ${STATE_SIZE} bytes — possible corruption"
  fi
fi

# ============================================================
# SUMMARY LOG (every 10 minutes)
# ============================================================
MINUTE=$(date '+%M')
if [ "$((MINUTE % 10))" -eq 0 ]; then
  log "✅ Health check passed — Block: $BLOCK_HEIGHT | Chain valid: $CHAIN_VALID | Mempool: $MEMPOOL_SIZE | Staleness: ${LAST_BLOCK_TIME}ms"
fi
