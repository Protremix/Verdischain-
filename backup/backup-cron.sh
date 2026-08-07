#!/usr/bin/env bash
# ==============================================================================
# Verdis Backup Cron Installation & Management Script
# Script Name: backup-cron.sh
# Purpose: Configures crontab entries and logrotate rules for automated backups
# Domain: verdischain.com | Server: 91.98.160.145
# ==============================================================================

set -euo pipefail

# --- Configuration & Constants ---
TOOL_DIR="${TOOL_DIR:-/opt/verdis-backup-tools}"
LOG_ROTATE_FILE="/etc/logrotate.d/verdis-backup"
CRON_MARKER="# --- Verdis Blockchain Backup System ---"
GPG_RECIPIENT="${GPG_RECIPIENT:-admin@verdischain.com}"
ACTION="install"

# --- Logging Helper Functions ---
log_info()    { echo "[INFO]    $*"; }
log_warn()    { echo "[WARN]    $*"; }
log_error()   { echo "[ERROR]   $*"; }
log_success() { echo "[SUCCESS] $*"; }

# --- Usage Message ---
show_usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Installs, removes, or checks status of Verdis backup cron jobs and log rotation.

Options:
  --install               Install backup cron jobs and logrotate configuration (default)
  --uninstall             Remove backup cron jobs and logrotate configuration
  --status                Display current status of installed backup cron jobs
  --gpg-recipient EMAIL   Set GPG recipient email/ID for weekly key backup (default: $GPG_RECIPIENT)
  --tool-dir DIR          Set destination directory for backup tools (default: $TOOL_DIR)
  -h, --help              Show this help message and exit
EOF
}

# --- Parse Arguments ---
parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --install)
                ACTION="install"
                shift
                ;;
            --uninstall)
                ACTION="uninstall"
                shift
                ;;
            --status)
                ACTION="status"
                shift
                ;;
            --gpg-recipient)
                GPG_RECIPIENT="$2"
                shift 2
                ;;
            --tool-dir)
                TOOL_DIR="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# --- Check Root Privileges ---
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (or via sudo)."
        exit 1
    fi
}

# --- Deploy Tools to TOOL_DIR ---
deploy_tools() {
    log_info "Deploying backup tools to $TOOL_DIR..."
    mkdir -p "$TOOL_DIR"

    # Copy current workspace scripts to TOOL_DIR if running from source
    local current_dir
    current_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

    local scripts=("verdis-backup.sh" "verdis-restore.sh" "verdis-config-backup.sh" "verdis-key-backup.sh" "verify-backup.sh" "recovery-test.sh")

    for script in "${scripts[@]}"; do
        if [[ -f "${current_dir}/${script}" ]]; then
            cp -a "${current_dir}/${script}" "${TOOL_DIR}/${script}"
            chmod +x "${TOOL_DIR}/${script}"
            log_info "Installed ${script} -> ${TOOL_DIR}/${script}"
        fi
    done
}

# --- Install Crontab ---
install_cron() {
    log_info "Installing crontab schedules..."

    # Ensure tool scripts are executable in TOOL_DIR
    deploy_tools

    # Get current crontab without existing Verdis entries
    local temp_cron
    temp_cron=$(mktemp /tmp/verdis-cron-XXXXXX)
    crontab -l 2>/dev/null | grep -v "verdis-" | grep -v "$CRON_MARKER" > "$temp_cron" || true

    # Append new cron entries
    cat << EOF >> "$temp_cron"
$CRON_MARKER
# Daily Full Backup at 02:00 AM
0 2 * * * $TOOL_DIR/verdis-backup.sh >> /var/log/verdis-backup-cron.log 2>&1
# Hourly Configuration Backup
0 * * * * $TOOL_DIR/verdis-config-backup.sh >> /var/log/verdis-backup-cron.log 2>&1
# Weekly Key Backup (Sunday at 03:00 AM)
0 3 * * 0 $TOOL_DIR/verdis-key-backup.sh "$GPG_RECIPIENT" >> /var/log/verdis-backup-cron.log 2>&1
# Daily Automated Backup Verification at 04:00 AM
0 4 * * * $TOOL_DIR/verify-backup.sh /opt/verdis-backups/full/verdis-latest.tar.gz >> /var/log/verdis-backup-cron.log 2>&1
# Weekly Recovery Test (Monday at 04:30 AM)
30 4 * * 1 $TOOL_DIR/recovery-test.sh >> /var/log/verdis-backup-cron.log 2>&1
$CRON_MARKER
EOF

    crontab "$temp_cron"
    rm -f "$temp_cron"
    log_success "Crontab entries successfully installed."

    # Install logrotate configuration for backup logs
    log_info "Configuring log rotation for backup logs at $LOG_ROTATE_FILE..."
    cat << EOF > "$LOG_ROTATE_FILE"
/var/log/verdis-backup*.log /var/log/verdis-restore.log /var/log/verdis-verify.log /var/log/verdis-recovery-test.log {
    weekly
    rotate 8
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
}
EOF
    log_success "Logrotate rule created at $LOG_ROTATE_FILE."
}

# --- Uninstall Crontab ---
uninstall_cron() {
    log_info "Removing Verdis backup crontab entries..."

    local temp_cron
    temp_cron=$(mktemp /tmp/verdis-cron-XXXXXX)
    crontab -l 2>/dev/null | grep -v "verdis-" | grep -v "$CRON_MARKER" > "$temp_cron" || true

    crontab "$temp_cron"
    rm -f "$temp_cron"
    log_success "Crontab entries removed."

    if [[ -f "$LOG_ROTATE_FILE" ]]; then
        rm -f "$LOG_ROTATE_FILE"
        log_success "Removed $LOG_ROTATE_FILE."
    fi
}

# --- Check Status ---
show_status() {
    log_info "================================================================="
    log_info "Verdis Backup Cron & Tools Status"
    log_info "================================================================="

    echo "Tool Directory: $TOOL_DIR"
    if [[ -d "$TOOL_DIR" ]]; then
        echo "Installed Scripts:"
        ls -la "$TOOL_DIR"
    else
        echo "Tool directory $TOOL_DIR does not exist."
    fi

    echo ""
    echo "Active Crontab Entries:"
    crontab -l 2>/dev/null | grep -A 8 "$CRON_MARKER" || echo "No Verdis crontab entries found."

    echo ""
    echo "Logrotate Rule ($LOG_ROTATE_FILE):"
    if [[ -f "$LOG_ROTATE_FILE" ]]; then
        cat "$LOG_ROTATE_FILE"
    else
        echo "Logrotate rule not installed."
    fi
}

# --- Main Execution ---
main() {
    parse_args "$@"

    case "$ACTION" in
        install)
            check_root
            install_cron
            ;;
        uninstall)
            check_root
            uninstall_cron
            ;;
        status)
            show_status
            ;;
    esac
}

main "$@"
