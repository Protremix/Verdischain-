#!/usr/bin/env bash
# ==============================================================================
# Verdis Blockchain Restore Script
# Script Name: verdis-restore.sh
# Purpose: Restores Verdis node database, keystore, chain spec, & configs
# Domain: verdischain.com | Server: 91.98.160.145
# ==============================================================================

set -euo pipefail

# --- Configuration & Constants ---
LOG_FILE="/var/log/verdis-restore.log"
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

BACKUP_FILE=""
FORCE=false
SKIP_SSL=false
TEMP_EXTRACT_DIR=""

TIMESTAMP=$(date +"%Y%m%d-%HMMSS")
SAFETY_BACKUP_DIR="/opt/verdis-backups/pre-restore-safety-${TIMESTAMP}"

# --- Logging Helper Functions ---
log() {
    local level="$1"
    shift
    local msg="$*"
    local timestamp
    timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] [$level] $msg"
    if [[ -w "$(dirname "$LOG_FILE")" ]] || [[ -w "$LOG_FILE" ]]; then
        echo "[$timestamp] [$level] $msg" >> "$LOG_FILE" 2>/dev/null || true
    fi
}

log_info()    { log "INFO" "$@"; }
log_warn()    { log "WARN" "$@"; }
log_error()   { log "ERROR" "$@"; }
log_success() { log "SUCCESS" "$@"; }

# --- Cleanup Trap ---
cleanup() {
    local exit_code=$?
    if [[ -n "$TEMP_EXTRACT_DIR" ]] && [[ -d "$TEMP_EXTRACT_DIR" ]]; then
        log_info "Cleaning up temporary extraction workspace..."
        rm -rf "$TEMP_EXTRACT_DIR"
    fi

    if [[ $exit_code -eq 0 ]]; then
        log_success "Restore script completed successfully."
    else
        log_error "Restore script terminated with error (exit code $exit_code)."
    fi
}

trap cleanup EXIT INT TERM

# --- Usage Message ---
show_usage() {
    cat << EOF
Usage: $(basename "$0") <path-to-backup.tar.gz> [OPTIONS]

Restores Verdis Blockchain full state from a tar.gz backup archive.

Arguments:
  <path-to-backup.tar.gz>   Path to the .tar.gz backup file to restore

Options:
  -f, --force               Skip interactive confirmation prompt
  --skip-ssl                Skip restoring SSL certificates
  -h, --help                Show this help message and exit
EOF
}

# --- Argument Parsing ---
parse_args() {
    if [[ $# -lt 1 ]]; then
        log_error "Missing backup file argument."
        show_usage
        exit 1
    fi

    BACKUP_FILE="$1"
    shift

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -f|--force)
                FORCE=true
                shift
                ;;
            --skip-ssl)
                SKIP_SSL=true
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

    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (or via sudo)."
        exit 1
    fi

    if [[ ! -f "$BACKUP_FILE" ]]; then
        log_error "Backup archive file not found: $BACKUP_FILE"
        exit 1
    fi

    mkdir -p "$(dirname "$LOG_FILE")"

    # Verify sha256sum file if present
    local sha_file="${BACKUP_FILE}.sha256"
    if [[ -f "$sha_file" ]]; then
        log_info "Verifying archive SHA-256 checksum against $sha_file..."
        if sha256sum -c "$sha_file" >/dev/null 2>&1; then
            log_success "Archive SHA-256 checksum verified."
        else
            log_error "Archive SHA-256 checksum mismatch! Archive may be corrupted."
            exit 1
        fi
    else
        log_warn "Archive checksum file $sha_file not found. Proceeding with inline integrity check."
    fi

    # Test tar archive integrity
    log_info "Testing archive tar structure..."
    if ! tar -tzf "$BACKUP_FILE" >/dev/null 2>&1; then
        log_error "Archive file is corrupted or not a valid gzipped tar file."
        exit 1
    fi
    log_success "Archive integrity verified."
}

# --- Extract and Validate Backup ---
extract_and_validate() {
    TEMP_EXTRACT_DIR=$(mktemp -d /tmp/verdis-restore-XXXXXX)
    log_info "Extracting backup to temporary directory $TEMP_EXTRACT_DIR..."
    tar -xzf "$BACKUP_FILE" -C "$TEMP_EXTRACT_DIR"

    if [[ -f "$TEMP_EXTRACT_DIR/SHA256SUMS" ]]; then
        log_info "Verifying internal file checksums (SHA256SUMS)..."
        (
            cd "$TEMP_EXTRACT_DIR"
            if sha256sum -c SHA256SUMS >/dev/null 2>&1; then
                log_success "All internal files matched SHA256SUMS manifest."
            else
                log_error "Internal file checksum verification failed!"
                exit 1
            fi
        )
    else
        log_warn "No SHA256SUMS manifest found inside archive."
    fi

    if [[ -f "$TEMP_EXTRACT_DIR/metadata.json" ]]; then
        log_info "Backup metadata summary:"
        cat "$TEMP_EXTRACT_DIR/metadata.json" | grep -E '"(timestamp|hostname|token_symbol|ss58_format)"' || true
    fi
}

# --- Confirmation Prompt ---
confirm_restore() {
    if [[ "$FORCE" == "true" ]]; then
        return 0
    fi

    echo ""
    log_warn "======================= ATTENTION ======================="
    log_warn "This operation will overwrite the current node state:"
    log_warn "  Data dir:     $NODE_DATA_DIR"
    log_warn "  Keystore:     $KEYSTORE_DIR"
    log_warn "  Chain spec:   $CHAIN_SPEC_FILE"
    log_warn "  Nginx conf:   $NGINX_CONF_AVAILABLE"
    log_warn "========================================================="
    read -p "Are you sure you want to proceed with restore? [y/N]: " -r reply
    echo ""

    if [[ ! "$reply" =~ ^[Yy]$ ]]; then
        log_info "Restore operation cancelled by user."
        exit 0
    fi
}

# --- Create Safety Backup ---
create_safety_backup() {
    log_info "Creating pre-restore safety snapshot in $SAFETY_BACKUP_DIR..."
    mkdir -p "$SAFETY_BACKUP_DIR"

    if [[ -d "$NODE_DATA_DIR" ]]; then
        rsync -a "$NODE_DATA_DIR" "$SAFETY_BACKUP_DIR/" 2>/dev/null || true
    fi
    if [[ -f "$CHAIN_SPEC_FILE" ]]; then
        cp -a "$CHAIN_SPEC_FILE" "$SAFETY_BACKUP_DIR/" 2>/dev/null || true
    fi
    if [[ -f "$NGINX_CONF_AVAILABLE" ]]; then
        cp -a "$NGINX_CONF_AVAILABLE" "$SAFETY_BACKUP_DIR/" 2>/dev/null || true
    fi
    log_success "Safety backup created at $SAFETY_BACKUP_DIR."
}

# --- Stop Service ---
stop_node() {
    if command -v systemctl >/dev/null 2>&1 && systemctl is-active --quiet "$NODE_SERVICE"; then
        log_info "Stopping service $NODE_SERVICE..."
        systemctl stop "$NODE_SERVICE"

        local elapsed=0
        while systemctl is-active --quiet "$NODE_SERVICE"; do
            if [[ $elapsed -ge $STOP_TIMEOUT ]]; then
                log_warn "Service did not stop in $STOP_TIMEOUTs. Sending SIGKILL..."
                systemctl kill -s SIGKILL "$NODE_SERVICE" || true
                break
            fi
            sleep 1
            ((elapsed++))
        done
        log_success "$NODE_SERVICE stopped."
    fi
}

# --- Execute Restoration ---
perform_restoration() {
    log_info "Restoring files from extracted archive..."

    # 1. Restore Chain Spec
    if [[ -f "$TEMP_EXTRACT_DIR/chain-spec.json" ]]; then
        log_info "Restoring chain specification to $CHAIN_SPEC_FILE..."
        mkdir -p "$(dirname "$CHAIN_SPEC_FILE")"
        cp -a "$TEMP_EXTRACT_DIR/chain-spec.json" "$CHAIN_SPEC_FILE"
    fi

    # 2. Restore Database and Keystore
    if [[ -d "$TEMP_EXTRACT_DIR/data" ]]; then
        log_info "Restoring node database to $NODE_DATA_DIR..."
        mkdir -p "$NODE_DATA_DIR"
        rsync -a --delete "$TEMP_EXTRACT_DIR/data/" "$NODE_DATA_DIR/"
    fi

    if [[ -d "$TEMP_EXTRACT_DIR/keystore" ]]; then
        log_info "Restoring keystore to $KEYSTORE_DIR..."
        mkdir -p "$KEYSTORE_DIR"
        rsync -a "$TEMP_EXTRACT_DIR/keystore/" "$KEYSTORE_DIR/"
        chmod 700 "$KEYSTORE_DIR" 2>/dev/null || true
        chmod 600 "$KEYSTORE_DIR"/* 2>/dev/null || true
    fi

    # 3. Restore Nginx Configuration
    if [[ -f "$TEMP_EXTRACT_DIR/nginx/verdischain.conf" ]]; then
        log_info "Restoring Nginx config to $NGINX_CONF_AVAILABLE..."
        mkdir -p "$(dirname "$NGINX_CONF_AVAILABLE")"
        cp -a "$TEMP_EXTRACT_DIR/nginx/verdischain.conf" "$NGINX_CONF_AVAILABLE"
        
        if [[ -d "/etc/nginx/sites-enabled" ]]; then
            ln -sf "$NGINX_CONF_AVAILABLE" "$NGINX_CONF_ENABLED"
        fi
        if command -v nginx >/dev/null 2>&1; then
            nginx -t 2>/dev/null && systemctl reload nginx 2>/dev/null || log_warn "Nginx reload skipped or config check failed."
        fi
    fi

    # 4. Restore SSL Certificates
    if [[ "$SKIP_SSL" == "false" ]] && [[ -d "$TEMP_EXTRACT_DIR/ssl" ]]; then
        log_info "Restoring SSL certificates to $SSL_CERT_DIR..."
        mkdir -p "$SSL_CERT_DIR"
        rsync -a "$TEMP_EXTRACT_DIR/ssl/" "$SSL_CERT_DIR/"
    fi

    # 5. Restore Systemd Service
    if [[ -f "$TEMP_EXTRACT_DIR/systemd/verdis-node.service" ]]; then
        log_info "Restoring Systemd service to $SYSTEMD_SERVICE_FILE..."
        mkdir -p "$(dirname "$SYSTEMD_SERVICE_FILE")"
        cp -a "$TEMP_EXTRACT_DIR/systemd/verdis-node.service" "$SYSTEMD_SERVICE_FILE"
        if command -v systemctl >/dev/null 2>&1; then
            systemctl daemon-reload
        fi
    fi

    # 6. Restore Logrotate Config
    if [[ -f "$TEMP_EXTRACT_DIR/logrotate/verdis" ]]; then
        log_info "Restoring Logrotate configuration to $LOGROTATE_FILE..."
        mkdir -p "$(dirname "$LOGROTATE_FILE")"
        cp -a "$TEMP_EXTRACT_DIR/logrotate/verdis" "$LOGROTATE_FILE"
    fi

    log_success "All requested files restored successfully."
}

# --- Start Service and Health Check ---
start_and_verify() {
    if command -v systemctl >/dev/null 2>&1 && [[ -f "$SYSTEMD_SERVICE_FILE" ]]; then
        log_info "Starting $NODE_SERVICE..."
        systemctl start "$NODE_SERVICE"

        log_info "Verifying $NODE_SERVICE status..."
        sleep 3
        if systemctl is-active --quiet "$NODE_SERVICE"; then
            log_success "$NODE_SERVICE is active and running."
        else
            log_error "$NODE_SERVICE failed to start! Check systemctl status or journalctl -u $NODE_SERVICE."
            exit 1
        fi
    else
        log_warn "Systemctl or $SYSTEMD_SERVICE_FILE not available. Service start skipped."
    fi
}

# --- Main Logic ---
main() {
    log_info "================================================================="
    log_info "Starting Verdis Blockchain Restore Procedure"
    log_info "================================================================="

    parse_args "$@"
    check_prerequisites
    extract_and_validate
    confirm_restore
    create_safety_backup
    stop_node
    perform_restoration
    start_and_verify

    log_info "================================================================="
    log_success "Verdis Restoration process completed successfully."
    log_info "================================================================="
}

main "$@"
