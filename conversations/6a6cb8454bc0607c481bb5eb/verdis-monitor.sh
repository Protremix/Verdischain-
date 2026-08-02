#!/bin/bash
# ============================================================
# VERDIS BLOCKCHAIN MONITORING & AUTO-REPAIR DAEMON v2
# Runs every 60 seconds via systemd timer
# ============================================================

LOG_FILE="/var/log/verdis-monitor.log"
ALERT_FILE="/opt/verdis/data/monitor-alerts.json"
API_URL="http://127.0.0.1:3200"
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
  
  # Write alert to file
  echo "{\"timestamp\":\"$(date -u '+%Y-%m-%dT%H:%M:%SZ')\",\"severity\":\"$severity\",\"message\":\"$message\",\"details\":\"$details\",\"hostname\":\"$(hostname)\",\"service\":\"verdis\"}" >> "$ALERT_FILE"
  
  # Also send to the blockchain API
  curl -s -X POST "$API_URL/api/monitor/alert" \
    -H "Content-Type: application/json" \
    -d "{\"severity\":\"$severity\",\"message\":\"$message\",\"details\":\"$details\"}" > /dev/null 2>&1
}

# ============================================================
# CHECK 1: Is the verdis service running?
# ============================================================
if ! systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
  log "❌ Service $SERVICE_NAME is DOWN — attempting restart..."
  systemctl restart "$SERVICE_NAME"
  sleep 5
  
  if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    send_alert "CRITICAL" "Blockchain service was DOWN — auto-restarted successfully" "Service was detected as down and restarted"
    log "✅ Service restarted successfully"
  else
    send_alert "CRITICAL" "Blockchain service is DOWN — auto-restart FAILED" "Manual intervention required"
    log "❌ Auto-restart failed — service still down"
    exit 1
  fi
fi

# ============================================================
# CHECK 2: Is the API responding?
# ============================================================
API_RESPONSE=$(curl -s -m 10 "$API_URL/api/blockchain/info" 2>/dev/null)
CURL_EXIT=$?

if [ $CURL_EXIT -ne 0 ] || [ -z "$API_RESPONSE" ]; then
  send_alert "WARNING" "Blockchain API is not responding" "curl exit=$CURL_EXIT, response empty"
  log "⚠️ API not responding (curl exit=$CURL_EXIT) — checking memory..."
  
  MEM_USAGE=$(systemctl show "$SERVICE_NAME" --property=MemoryCurrent 2>/dev/null | cut -d= -f2)
  if [ -n "$MEM_USAGE" ] && [ "$MEM_USAGE" -gt 268435456 ]; then
    log "🔄 High memory (${MEM_USAGE} bytes) — restarting service..."
    systemctl restart "$SERVICE_NAME"
    sleep 5
    send_alert "WARNING" "Service restarted due to high memory" "Memory was ${MEM_USAGE} bytes (>256MB)"
  fi
  exit 0
fi

# Parse JSON response
BLOCK_HEIGHT=$(echo "$API_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('height',0))" 2>/dev/null)
CHAIN_VALID=$(echo "$API_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('chainValid',False))" 2>/dev/null)
MEMPOOL_SIZE=$(echo "$API_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('mempoolSize',0))" 2>/dev/null)

# ============================================================
# CHECK 3: Block height and chain validity
# ============================================================
if [ -z "$BLOCK_HEIGHT" ] || [ "$BLOCK_HEIGHT" = "0" ]; then
  send_alert "CRITICAL" "Block height is 0 or unreadable" "API returned: $API_RESPONSE"
  exit 0
fi

if [ "$CHAIN_VALID" = "False" ]; then
  send_alert "CRITICAL" "Chain validation FAILED" "chainValid=false — possible tampering or corruption"
  log "❌ Chain invalid — requires manual investigation"
  exit 0
fi

# ============================================================
# CHECK 4: Block production staleness
# ============================================================
HEALTH_RESPONSE=$(curl -s -m 10 "$API_URL/api/health" 2>/dev/null)
if [ -n "$HEALTH_RESPONSE" ]; then
  LAST_BLOCK_MS=$(echo "$HEALTH_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('blockStalenessMs',999999))" 2>/dev/null)
  
  if [ -n "$LAST_BLOCK_MS" ] && [ "$LAST_BLOCK_MS" -gt $((MAX_BLOCK_STALENESS * 1000)) ]; then
    STALE_SEC=$((LAST_BLOCK_MS / 1000))
    log "⚠️ Block production stalled — last block ${STALE_SEC}s ago"
    
    if [ "$STALE_SEC" -gt 60 ]; then
      log "🔄 Block stall >60s — restarting service..."
      systemctl restart "$SERVICE_NAME"
      sleep 8
      send_alert "WARNING" "Block production stalled — service auto-restarted" "Last block was ${STALE_SEC}s old"
      
      NEW_HEALTH=$(curl -s -m 10 "$API_URL/api/health" 2>/dev/null)
      NEW_STALE=$(echo "$NEW_HEALTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('blockStalenessMs',999999))" 2>/dev/null)
      if [ -n "$NEW_STALE" ] && [ "$NEW_STALE" -lt 15000 ]; then
        log "✅ Service restarted — block production resumed (${NEW_STALE}ms)"
      else
        send_alert "CRITICAL" "Block production still stalled after restart" "Manual investigation needed"
      fi
    else
      send_alert "WARNING" "Block production is slow" "Last block ${STALE_SEC}s ago (threshold: ${MAX_BLOCK_STALENESS}s)"
    fi
  fi
fi

# ============================================================
# CHECK 5: Mempool overflow
# ============================================================
if [ -n "$MEMPOOL_SIZE" ] && [ "$MEMPOOL_SIZE" -gt 900 ]; then
  send_alert "WARNING" "Mempool near capacity" "$MEMPOOL_SIZE/1000 transactions"
fi

# ============================================================
# CHECK 6: Disk space
# ============================================================
DISK_USAGE=$(df /opt/verdis 2>/dev/null | tail -1 | awk '{print $5}' | tr -d '%')
if [ -n "$DISK_USAGE" ] && [ "$DISK_USAGE" -gt 85 ]; then
  send_alert "WARNING" "Disk space low" "Disk at ${DISK_USAGE}% on /opt/verdis"
  find /opt/verdis -name "*.bak" -mtime +7 -exec rm -f {} \; 2>/dev/null
  log "🧹 Cleaned old backup files"
fi

# ============================================================
# CHECK 7: State file integrity
# ============================================================
STATE_FILE="/opt/verdis/app/data/blockchain-state.json"
if [ -f "$STATE_FILE" ]; then
  STATE_SIZE=$(stat -c%s "$STATE_FILE" 2>/dev/null)
  if [ -n "$STATE_SIZE" ] && [ "$STATE_SIZE" -lt 100 ]; then
    send_alert "CRITICAL" "State file may be corrupted" "blockchain-state.json is only ${STATE_SIZE} bytes"
  fi
fi

# ============================================================
# PERIODIC HEALTH LOG (every 10 minutes)
# ============================================================
MINUTE=$(date '+%M')
if [ "$((MINUTE % 10))" -eq 0 ]; then
  log "✅ Health OK — Block: $BLOCK_HEIGHT | Chain valid: $CHAIN_VALID | Mempool: $MEMPOOL_SIZE"
fi
