#!/usr/bin/env bash
# ==============================================================================
# Verdis Blockchain Backup Script
# Script Name: verdis-backup.sh
# Purpose: Performs full system, configuration, database, and keystore backup
# Domain: verdischain.com | Server: 91.98.160.145
# Token: VRS (SS58=909, 9 Decimals)
# ==============================================================================

set -euo pipefail

# --- Configuration & Constants ---
LOG_FILE="/var/log/verdis-backup.log"
BACKUP_BASE_DIR="${BACKUP_BASE_DIR:-/opt/verdis-backups/full}"
DAILY_DIR="${BACKUP_BASE_DIR}/daily"
WEEKLY_DIR="${BACKUP_BASE_DIR}/weekly"
MONTHLY_DIR="${BACKUP_BASE_DIR}/monthly"

LOCK_FILE="/var/run/verdis-backup.lock"
NODE_SERVICE="verdis-node.service"
STOP_TIMEOUT=30

NODE_DATA_DIR="/opt/verdis-chain-rust/data"
KEYSTORE_DIR="/opt/verdis-chain-rust/data/keystore"
CHAIN_SPEC_FILE="/opt/verdis-chain-rust/chain-spec.json"
NGINX_CONF_AVAILABLE="/etc/nginx/sites-available/verdischain"
NGINX_CONF_ENABLED="/etc/nginx/sites-enabled/verdischain"
SSL_CERT_DIR="/etc/letsencrypt/live/verdischain.com"
SYSTEMD_SERVICE_FILE="/etc/systemd/system/verdis-node.service"
LOGROTATE_FILE="/etc/logrotate.d/verdis"
MONITORING_PATHS=("/etc/prometheus" "/etc/grafana" "/etc/verdis")

REMOTE_DEST="${REMOTE_DEST:-backupuser@91.98.160.145:/backups/verdis/}"
SKIP_REMOTE="${SKIP_REMOTE:-false}"
DRY_RUN=false

TIMESTAMP=$(date +"%Y%m%d-%HMMSS")
DATE_DAY=$(date +"%d")
DAY_OF_WEEK=$(date +"%u") # 7 is Sunday
BACKUP_NAME="verdis-backup-${TIMESTAMP}"
TEMP_WORK_DIR="/tmp/${BACKUP_NAME}"

# State variables for exit trap
NODE_WAS_STOPPED=false

# --- Logging Helper Functions ---
log() {
    local level="$1"
    shift
    local msg="$*"
    local timestamp
    timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] [$level] $msg"
    # Ensure log file exists or attempt append safely
    if [[ -w "$(dirname "$LOG_FILE")" ]] || [[ -w "$LOG_FILE" ]]; then
        echo "[$timestamp] [$level] $msg" >> "$LOG_FILE" 2>/dev/null || true
    fi
}

log_info()    { log "INFO" "$@"; }
log_warn()    { log "WARN" "$@"; }
log_error()   { log "ERROR" "$@"; }
log_success() { log "SUCCESS" "$@"; }

# --- Clean Trap Handler ---
cleanup() {
    local exit_code=$?
    log_info "Executing cleanup procedure (exit code: $exit_code)..."

    # Always restart node if we stopped it earlier and script is terminating
    if [[ "$NODE_WAS_STOPPED" == "true" ]]; then
        log_warn "Node was previously stopped. Attempting to restart $NODE_SERVICE..."
        if command -v systemctl >/dev/null 2>&1; then
            systemctl start "$NODE_SERVICE" || log_error "Failed to restart $NODE_SERVICE!"
            if systemctl is-active --quiet "$NODE_SERVICE"; then
                log_success "$NODE_SERVICE restarted successfully."
            else
                log_error "$NODE_SERVICE is not active after restart attempt."
            fi
        fi
        NODE_WAS_STOPPED=false
    fi

    # Remove temporary directory
    if [[ -d "$TEMP_WORK_DIR" ]]; then
        log_info "Removing temporary directory $TEMP_WORK_DIR..."
        rm -rf "$TEMP_WORK_DIR"
    fi

    # Remove lock file
    if [[ -f "$LOCK_FILE" ]]; then
        rm -f "$LOCK_FILE"
    fi

    if [[ $exit_code -eq 0 ]]; then
        log_success "Backup process completed successfully."
    else
        log_error "Backup process finished with errors (exit code $exit_code)."
    fi
}

trap cleanup EXIT INT TERM

# --- Usage / Help ---
show_usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Full Backup Script for Verdis Blockchain Node (Rust + Substrate).

Options:
  --backup-dir DIR     Base target directory for backups (default: /opt/verdis-backups/full)
  --remote-dest DEST   Remote destination for rsync (default: $REMOTE_DEST)
  --skip-remote        Skip uploading backup to remote server
  --dry-run            Simulate operations without making changes
  -h, --help           Show this help message and exit

Environment Variables:
  BACKUP_BASE_DIR      Base target directory
  REMOTE_DEST          Rsync remote path
  SKIP_REMOTE          Set to 'true' to skip rsync
EOF
}

# --- Parse Arguments ---
parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --backup-dir)
                BACKUP_BASE_DIR="$2"
                DAILY_DIR="${BACKUP_BASE_DIR}/daily"
                WEEKLY_DIR="${BACKUP_BASE_DIR}/weekly"
                MONTHLY_DIR="${BACKUP_BASE_DIR}/monthly"
                shift 2
                ;;
            --remote-dest)
                REMOTE_DEST="$2"
                shift 2
                ;;
            --skip-remote)
                SKIP_REMOTE="true"
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown parameter: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# --- Pre-flight Checks ---
check_prerequisites() {
    log_info "Running pre-flight checks..."
    
    # Check root if not dry-run
    if [[ $EUID -ne 0 ]] && [[ "$DRY_RUN" == "false" ]]; then
        log_error "This script must be run as root (or via sudo)."
        exit 1
    fi

    # Check required commands
    local req_cmds=("tar" "gzip" "sha256sum" "rsync")
    for cmd in "${req_cmds[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            log_error "Required tool '$cmd' is not installed."
            exit 1
        fi
    done

    # Handle concurrent executions
    if [[ -f "$LOCK_FILE" ]]; then
        local pid
        pid=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            log_error "Another backup instance is already running (PID: $pid)."
            exit 1
        else
            log_warn "Stale lockfile found at $LOCK_FILE. Overwriting."
        fi
    fi

    if [[ "$DRY_RUN" == "false" ]]; then
        mkdir -p "$(dirname "$LOCK_FILE")"
        echo "$$" > "$LOCK_FILE"
    fi

    # Ensure output directories exist
    mkdir -p "$DAILY_DIR" "$WEEKLY_DIR" "$MONTHLY_DIR"
    mkdir -p "$(dirname "$LOG_FILE")"

    log_success "Pre-flight checks completed."
}

# --- Graceful Service Stop ---
stop_verdis_node() {
    log_info "Checking $NODE_SERVICE status..."
    if command -v systemctl >/dev/null 2>&1 && systemctl is-active --quiet "$NODE_SERVICE"; then
        log_info "Stopping $NODE_SERVICE gracefully..."
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "[DRY-RUN] Would run: systemctl stop $NODE_SERVICE"
            return 0
        fi

        systemctl stop "$NODE_SERVICE"
        NODE_WAS_STOPPED=true

        local elapsed=0
        while systemctl is-active --quiet "$NODE_SERVICE"; do
            if [[ $elapsed -ge $STOP_TIMEOUT ]]; then
                log_warn "Service did not stop within $STOP_TIMEOUT seconds. Sending SIGKILL..."
                systemctl kill -s SIGKILL "$NODE_SERVICE" || true
                break
            fi
            sleep 1
            ((elapsed++))
        done
        log_success "$NODE_SERVICE stopped successfully after ${elapsed}s."
    else
        log_info "$NODE_SERVICE is not running or systemctl is not available. Proceeding with backup."
    fi
}

# --- Data Collection ---
collect_backup_files() {
    log_info "Creating temporary workspace at $TEMP_WORK_DIR..."
    mkdir -p "$TEMP_WORK_DIR/data"
    mkdir -p "$TEMP_WORK_DIR/keystore"
    mkdir -p "$TEMP_WORK_DIR/nginx"
    mkdir -p "$TEMP_WORK_DIR/ssl"
    mkdir -p "$TEMP_WORK_DIR/systemd"
    mkdir -p "$TEMP_WORK_DIR/logrotate"
    mkdir -p "$TEMP_WORK_DIR/monitoring"

    # 1. Chain Database (RocksDB)
    if [[ -d "$NODE_DATA_DIR" ]]; then
        log_info "Backing up RocksDB chain database from $NODE_DATA_DIR..."
        if [[ "$DRY_RUN" == "false" ]]; then
            rsync -a --exclude="keystore" "$NODE_DATA_DIR/" "$TEMP_WORK_DIR/data/"
        fi
    else
        log_warn "Node data directory $NODE_DATA_DIR does not exist."
    fi

    # 2. Keystore
    if [[ -d "$KEYSTORE_DIR" ]]; then
        log_info "Backing up keystore from $KEYSTORE_DIR..."
        if [[ "$DRY_RUN" == "false" ]]; then
            rsync -a "$KEYSTORE_DIR/" "$TEMP_WORK_DIR/keystore/"
        fi
    else
        log_warn "Keystore directory $KEYSTORE_DIR does not exist."
    fi

    # 3. Chain Spec
    if [[ -f "$CHAIN_SPEC_FILE" ]]; then
        log_info "Backing up chain specification $CHAIN_SPEC_FILE..."
        if [[ "$DRY_RUN" == "false" ]]; then
            cp -a "$CHAIN_SPEC_FILE" "$TEMP_WORK_DIR/chain-spec.json"
        fi
    else
        log_warn "Chain spec $CHAIN_SPEC_FILE not found."
    fi

    # 4. Nginx Configuration
    if [[ -f "$NGINX_CONF_AVAILABLE" ]]; then
        log_info "Backing up Nginx configuration from $NGINX_CONF_AVAILABLE..."
        if [[ "$DRY_RUN" == "false" ]]; then
            cp -a "$NGINX_CONF_AVAILABLE" "$TEMP_WORK_DIR/nginx/verdischain.conf"
            if [[ -f "$NGINX_CONF_ENABLED" ]]; then
                cp -a "$NGINX_CONF_ENABLED" "$TEMP_WORK_DIR/nginx/verdischain-enabled.conf" 2>/dev/null || true
            fi
        fi
    else
        log_warn "Nginx config $NGINX_CONF_AVAILABLE not found."
    fi

    # 5. SSL Certificates
    if [[ -d "$SSL_CERT_DIR" ]]; then
        log_info "Backing up SSL certificates from $SSL_CERT_DIR..."
        if [[ "$DRY_RUN" == "false" ]]; then
            rsync -aL "$SSL_CERT_DIR/" "$TEMP_WORK_DIR/ssl/"
        fi
    else
        log_warn "SSL certificate directory $SSL_CERT_DIR not found."
    fi

    # 6. Systemd Service
    if [[ -f "$SYSTEMD_SERVICE_FILE" ]]; then
        log_info "Backing up Systemd service file from $SYSTEMD_SERVICE_FILE..."
        if [[ "$DRY_RUN" == "false" ]]; then
            cp -a "$SYSTEMD_SERVICE_FILE" "$TEMP_WORK_DIR/systemd/verdis-node.service"
        fi
    else
        log_warn "Systemd service file $SYSTEMD_SERVICE_FILE not found."
    fi

    # 7. Logrotate Config
    if [[ -f "$LOGROTATE_FILE" ]]; then
        log_info "Backing up Logrotate config from $LOGROTATE_FILE..."
        if [[ "$DRY_RUN" == "false" ]]; then
            cp -a "$LOGROTATE_FILE" "$TEMP_WORK_DIR/logrotate/verdis"
        fi
    else
        log_warn "Logrotate file $LOGROTATE_FILE not found."
    fi

    # 8. Monitoring Configs
    for m_path in "${MONITORING_PATHS[@]}"; do
        if [[ -d "$m_path" ]]; then
            log_info "Backing up monitoring configuration from $m_path..."
            if [[ "$DRY_RUN" == "false" ]]; then
                m_name=$(basename "$m_path")
                mkdir -p "$TEMP_WORK_DIR/monitoring/$m_name"
                rsync -a "$m_path/" "$TEMP_WORK_DIR/monitoring/$m_name/"
            fi
        fi
    done

    # 9. Create Metadata
    if [[ "$DRY_RUN" == "false" ]]; then
        cat << EOF > "$TEMP_WORK_DIR/metadata.json"
{
  "timestamp": "$TIMESTAMP",
  "hostname": "$(hostname -f 2>/dev/null || hostname)",
  "ip": "91.98.160.145",
  "domain": "verdischain.com",
  "token_symbol": "VRS",
  "ss58_format": 909,
  "decimals": 9,
  "total_supply": "100000000000",
  "block_time": "6s",
  "epoch_blocks": 600,
  "created_by": "verdis-backup.sh"
}
EOF
    fi

    log_success "All backup files collected in $TEMP_WORK_DIR."
}

# --- Checksum Creation & Archive Packaging ---
package_backup() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would create checksums and package archive ${BACKUP_NAME}.tar.gz"
        return 0
    fi

    log_info "Generating internal checksums (SHA-256) for collected backup files..."
    (
        cd "$TEMP_WORK_DIR"
        find . -type f ! -name "SHA256SUMS" -print0 | xargs -0 sha256sum > SHA256SUMS
    )
    log_success "Internal checksum manifest created."

    local target_archive="${DAILY_DIR}/${BACKUP_NAME}.tar.gz"
    log_info "Compressing backup payload into $target_archive..."
    tar -czf "$target_archive" -C "$TEMP_WORK_DIR" .
    
    # Calculate checksum for tar.gz archive
    sha256sum "$target_archive" > "${target_archive}.sha256"
    log_success "Archive compressed and signed: $target_archive"

    # Maintain latest link
    ln -sf "$target_archive" "${BACKUP_BASE_DIR}/verdis-latest.tar.gz"
    ln -sf "${target_archive}.sha256" "${BACKUP_BASE_DIR}/verdis-latest.tar.gz.sha256"

    # Tier copy to weekly/monthly
    if [[ "$DAY_OF_WEEK" -eq 7 ]]; then
        log_info "Today is Sunday. Archiving weekly backup copy to $WEEKLY_DIR..."
        cp -a "$target_archive" "${WEEKLY_DIR}/${BACKUP_NAME}.tar.gz"
        cp -a "${target_archive}.sha256" "${WEEKLY_DIR}/${BACKUP_NAME}.tar.gz.sha256"
    fi

    if [[ "$DATE_DAY" == "01" ]]; then
        log_info "Today is the 1st of the month. Archiving monthly backup copy to $MONTHLY_DIR..."
        cp -a "$target_archive" "${MONTHLY_DIR}/${BACKUP_NAME}.tar.gz"
        cp -a "${target_archive}.sha256" "${MONTHLY_DIR}/${BACKUP_NAME}.tar.gz.sha256"
    fi
}

# --- Remote Sync ---
sync_remote() {
    if [[ "$SKIP_REMOTE" == "true" ]]; then
        log_info "Remote sync skipped as requested."
        return 0
    fi

    log_info "Uploading backup archive to remote destination: $REMOTE_DEST..."
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would run: rsync -avz ${DAILY_DIR}/${BACKUP_NAME}.tar* $REMOTE_DEST"
        return 0
    fi

    local target_archive="${DAILY_DIR}/${BACKUP_NAME}.tar.gz"
    if rsync -avz "$target_archive" "${target_archive}.sha256" "$REMOTE_DEST" 2>/dev/null; then
        log_success "Remote upload to $REMOTE_DEST completed successfully."
    else
        log_warn "Remote sync failed or remote host unreachable. Local backup remains valid."
    fi
}

# --- Retention Policy Cleanup ---
# Retention rules: keep last 7 daily, 4 weekly, 12 monthly
apply_retention_policy() {
    log_info "Applying retention policy (Daily: 7, Weekly: 4, Monthly: 12)..."
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Skipping retention purge."
        return 0
    fi

    prune_directory "$DAILY_DIR" 7
    prune_directory "$WEEKLY_DIR" 4
    prune_directory "$MONTHLY_DIR" 12
}

prune_directory() {
    local dir="$1"
    local keep="$2"

    if [[ ! -d "$dir" ]]; then
        return 0
    fi

    # Find archives sorted by modification time (newest first)
    local archives=()
    while IFS= read -r file; do
        archives+=("$file")
    done < <(find "$dir" -maxdepth 1 -name "verdis-backup-*.tar.gz" -type f | sort -r)

    local count=${#archives[@]}
    log_info "Directory $dir has $count backup archive(s). Threshold: $keep."

    if [[ $count -gt $keep ]]; then
        for ((i=keep; i<count; i++)); do
            local archive_to_remove="${archives[$i]}"
            local sha_to_remove="${archive_to_remove}.sha256"
            log_info "Pruning old backup: $archive_to_remove"
            rm -f "$archive_to_remove" "$sha_to_remove"
        done
    fi
}

# --- Main Execution Flow ---
main() {
    log_info "================================================================="
    log_info "Starting Verdis Blockchain Full Backup ($BACKUP_NAME)"
    log_info "================================================================="

    parse_args "$@"
    check_prerequisites
    stop_verdis_node
    collect_backup_files

    # Restart node as soon as data snapshotting is completed
    if [[ "$NODE_WAS_STOPPED" == "true" ]]; then
        log_info "Data collection complete. Restarting $NODE_SERVICE immediately..."
        systemctl start "$NODE_SERVICE"
        if systemctl is-active --quiet "$NODE_SERVICE"; then
            log_success "$NODE_SERVICE is running."
        else
            log_error "$NODE_SERVICE failed to start after data collection."
        fi
        NODE_WAS_STOPPED=false
    fi

    package_backup
    sync_remote
    apply_retention_policy

    log_info "================================================================="
    log_success "Verdis Full Backup operation completed successfully."
    log_info "================================================================="
}

main "$@"
