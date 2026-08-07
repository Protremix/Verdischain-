#!/usr/bin/env bash
# Verdis Chain Transaction Bot Script
# Continuously sends system.remark extrinsics to the Verdis node every 10-25 seconds.
# Server: 91.98.160.145

LOG_FILE="/var/log/verdis-txbot.log"
VERDIS_CLI="/usr/local/bin/verdis"
RPC_URL="http://127.0.0.1:9933"

# Ensure log file directory exists
mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null || true

log() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp=$(date -u "+%Y-%m-%d %H:%M:%S UTC")
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE" 2>/dev/null || echo "[$timestamp] [$level] $message"
}

# Signal handling for clean exit under systemd
cleanup() {
    log "INFO" "Verdis TX Bot received termination signal. Shutting down gracefully..."
    exit 0
}
trap cleanup SIGINT SIGTERM

log "INFO" "=================================================="
log "INFO" "Starting Verdis Chain Transaction Bot"
log "INFO" "Target Node RPC: $RPC_URL"
log "INFO" "Verdis CLI Path: $VERDIS_CLI"
log "INFO" "Log File: $LOG_FILE"
log "INFO" "=================================================="

# Random message generator sources
PHRASES=(
    "Verdis activity heartbeat"
    "Automated transaction payload"
    "System remark state update"
    "Block generation activity ping"
    "Verdis chain remark extrinsic"
    "DPoS validator activity marker"
    "Network pulse check"
)

counter=1

while true; do
    # Generate random message string
    rand_index=$((RANDOM % ${#PHRASES[@]}))
    phrase="${PHRASES[$rand_index]}"
    rand_hex=$(head -c 8 /dev/urandom 2>/dev/null | xxd -p 2>/dev/null || printf "%08x" "$RANDOM")
    msg="$phrase #$counter ($rand_hex)"

    log "INFO" "Submitting system.remark extrinsic #$counter: '$msg'"

    success=false

    # Method 1: Use Verdis node CLI
    if [ -x "$VERDIS_CLI" ] || command -v "$VERDIS_CLI" >/dev/null 2>&1; then
        output=$("$VERDIS_CLI" submit-extrinsic --alice --port 9933 system remark "$msg" 2>&1)
        exit_code=$?
        if [ $exit_code -eq 0 ]; then
            log "SUCCESS" "Extrinsic submitted successfully via Verdis CLI: $output"
            success=true
        else
            log "WARN" "Verdis CLI command failed (exit code $exit_code): $output"
        fi
    else
        log "WARN" "Verdis CLI binary not found at $VERDIS_CLI or not executable"
    fi

    # Method 2: RPC Fallback if CLI failed or missing
    if [ "$success" = false ]; then
        log "INFO" "Attempting fallback submission via RPC endpoint ($RPC_URL)..."
        
        # Hex-encode the remark message
        msg_hex=$(printf '%s' "$msg" | xxd -p 2>/dev/null | tr -d '\n')
        if [ -z "$msg_hex" ]; then
            msg_hex=$(printf '%s' "$msg" | od -An -tx1 | tr -d ' \n')
        fi

        rpc_payload="{\"jsonrpc\":\"2.0\",\"method\":\"author_submitExtrinsic\",\"params\":[\"0x$msg_hex\"],\"id\":$counter}"
        
        rpc_response=$(curl -s -m 10 -X POST "$RPC_URL" \
            -H 'Content-Type: application/json' \
            -d "$rpc_payload" 2>&1)
        curl_exit=$?

        if [ $curl_exit -eq 0 ] && [ -n "$rpc_response" ]; then
            if echo "$rpc_response" | grep -q '"error"'; then
                log "ERROR" "RPC response returned error: $rpc_response"
            else
                log "SUCCESS" "Extrinsic submitted successfully via RPC: $rpc_response"
                success=true
            fi
        else
            log "ERROR" "Failed to connect to node RPC at $RPC_URL (curl exit: $curl_exit, response: $rpc_response)"
        fi
    fi

    counter=$((counter + 1))

    # Calculate random interval between 10 and 25 seconds
    interval=$((10 + RANDOM % 16))
    log "INFO" "Waiting ${interval} seconds before sending next transaction..."
    
    sleep "$interval"
done
