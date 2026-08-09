#!/usr/bin/env bash
# ==============================================================================
# Verdis Blockchain Hourly Configuration Backup Script
# Script Name: verdis-config-backup.sh
# Purpose: Lightweight hourly backup of node configs, chain spec, & system setup
# Domain: verdischain.com | Server: 91.98.160.145
# ==============================================================================

set -euo pipefail

# --- Configuration & Constants ---
LOG_FILE="/var/log/verdis-config-backup.log"
CONFIG_BACKUP_DIR="${CONFIG_BACKUP_DIR:-/opt/verdis-backups/config}"
RETENTION_COUNT=24

NGINX_CONF_AVAILABLE="/etc/nginx/sites-available/verdischain"
NGINX_CONF_ENABLED="/etc/nginx/sites-enabled/verdischain"
SYSTEMD_SERVICE_FILE="/etc/systemd/system/verdis-node.service"
CHAIN_SPEC_FILE="/opt/verdis-chain-rust/chain-spec.json"
LOGROTATE_FILE="/etc/logrotate.d/verdis"
MONITORING_PATHS=("/etc/prometheus" "/etc/grafana" "/etc/verdis")

TIMESTAMP=$(date +"%Y%m%d-%HMMSS")
BACKUP_NAME="verdis-config-${TIMESTAMP}"
TEMP_WORK_DIR="/tmp/${BACKUP_NAME}"

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
    if [[ -d "$TEMP_WORK_DIR" ]]; then
        rm -rf "$TEMP_WORK_DIR"
    fi

    if [[ $exit_code -eq 0 ]]; then
        log_success "Configuration backup finished successfully."
    else
        log_error "Configuration backup failed with exit code $exit_code."
    fi
}

trap cleanup EXIT INT TERM

# --- Pre-flight Checks ---
check_prerequisites() {
    if [[ $EUID -ne 0 ]]; then
        log_warn "Running as non-root user ($USER). Some system files may be unreadable."
    fi

    mkdir -p "$CONFIG_BACKUP_DIR"
    mkdir -p "$(dirname "$LOG_FILE")"
}

# --- Collect Configurations ---
collect_configs() {
    log_info "Creating temporary configuration staging directory at $TEMP_WORK_DIR..."
    mkdir -p "$TEMP_WORK_DIR/nginx"
    mkdir -p "$TEMP_WORK_DIR/systemd"
    mkdir -p "$TEMP_WORK_DIR/logrotate"
    mkdir -p "$TEMP_WORK_DIR/monitoring"

    # 1. Nginx Config
    if [[ -f "$NGINX_CONF_AVAILABLE" ]]; then
        cp -a "$NGINX_CONF_AVAILABLE" "$TEMP_WORK_DIR/nginx/verdischain.conf"
        if [[ -f "$NGINX_CONF_ENABLED" ]]; then
            cp -a "$NGINX_CONF_ENABLED" "$TEMP_WORK_DIR/nginx/verdischain-enabled.conf" 2>/dev/null || true
        fi
        log_info "Collected Nginx configuration."
    else
        log_warn "Nginx configuration $NGINX_CONF_AVAILABLE not found."
    fi

    # 2. Systemd Service File
    if [[ -f "$SYSTEMD_SERVICE_FILE" ]]; then
        cp -a "$SYSTEMD_SERVICE_FILE" "$TEMP_WORK_DIR/systemd/verdis-node.service"
        log_info "Collected Systemd service file."
    else
        log_warn "Systemd service $SYSTEMD_SERVICE_FILE not found."
    fi

    # 3. Chain Spec File
    if [[ -f "$CHAIN_SPEC_FILE" ]]; then
        cp -a "$CHAIN_SPEC_FILE" "$TEMP_WORK_DIR/chain-spec.json"
        log_info "Collected Chain Specification file."
    else
        log_warn "Chain spec $CHAIN_SPEC_FILE not found."
    fi

    # 4. Logrotate Config
    if [[ -f "$LOGROTATE_FILE" ]]; then
        cp -a "$LOGROTATE_FILE" "$TEMP_WORK_DIR/logrotate/verdis"
        log_info "Collected Logrotate configuration."
    else
        log_warn "Logrotate configuration $LOGROTATE_FILE not found."
    fi

    # 5. Monitoring Configs
    for m_path in "${MONITORING_PATHS[@]}"; do
        if [[ -d "$m_path" ]]; then
            m_name=$(basename "$m_path")
            mkdir -p "$TEMP_WORK_DIR/monitoring/$m_name"
            rsync -a "$m_path/" "$TEMP_WORK_DIR/monitoring/$m_name/" 2>/dev/null || cp -a "$m_path/." "$TEMP_WORK_DIR/monitoring/$m_name/" 2>/dev/null || true
            log_info "Collected monitoring config from $m_path."
        fi
    done

    # 6. Metadata Manifest
    cat << EOF > "$TEMP_WORK_DIR/manifest.json"
{
  "backup_type": "config-only",
  "timestamp": "$TIMESTAMP",
  "hostname": "$(hostname -f 2>/dev/null || hostname)",
  "ip": "91.98.160.145",
  "domain": "verdischain.com",
  "token": "VRS",
  "ss58": 909
}
EOF
}

# --- Package Archive ---
package_config() {
    log_info "Generating file checksums for configuration archive..."
    (
        cd "$TEMP_WORK_DIR"
        find . -type f ! -name "SHA256SUMS" -print0 | xargs -0 sha256sum > SHA256SUMS
    )

    local target_archive="${CONFIG_BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
    log_info "Packaging configurations into $target_archive..."
    tar -czf "$target_archive" -C "$TEMP_WORK_DIR" .
    sha256sum "$target_archive" > "${target_archive}.sha256"

    # Maintain latest symlink
    ln -sf "$target_archive" "${CONFIG_BACKUP_DIR}/verdis-config-latest.tar.gz"
    ln -sf "${target_archive}.sha256" "${CONFIG_BACKUP_DIR}/verdis-config-latest.tar.gz.sha256"

    log_success "Configuration archive created: $target_archive"
}

# --- Prune Retention (Keep last 24 hourly backups) ---
prune_old_configs() {
    log_info "Applying retention policy (keeping last $RETENTION_COUNT hourly config backups)..."

    local archives=()
    while IFS= read -r file; do
        archives+=("$file")
    done < <(find "$CONFIG_BACKUP_DIR" -maxdepth 1 -name "verdis-config-*.tar.gz" -type f | sort -r)

    local count=${#archives[@]}
    log_info "Found $count configuration archive(s) in $CONFIG_BACKUP_DIR."

    if [[ $count -gt $RETENTION_COUNT ]]; then
        for ((i=RETENTION_COUNT; i<count; i++)); do
            local archive_to_remove="${archives[$i]}"
            local sha_to_remove="${archive_to_remove}.sha256"
            log_info "Pruning old config backup: $archive_to_remove"
            rm -f "$archive_to_remove" "$sha_to_remove"
        done
    fi
}

# --- Main Execution ---
main() {
    log_info "Starting hourly Verdis configuration backup..."
    check_prerequisites
    collect_configs
    package_config
    prune_old_configs
    log_success "Hourly configuration backup completed successfully."
}

main "$@"
