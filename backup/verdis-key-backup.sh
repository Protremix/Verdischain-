#!/usr/bin/env bash
# ==============================================================================
# Verdis Blockchain Key Backup Script
# Script Name: verdis-key-backup.sh
# Purpose: Encrypts and backs up validator node keystore (session, BABE, GRANDPA keys)
# Domain: verdischain.com | Server: 91.98.160.145
# ==============================================================================

set -euo pipefail

# --- Configuration & Constants ---
LOG_FILE="/var/log/verdis-key-backup.log"
KEY_BACKUP_DIR="${KEY_BACKUP_DIR:-/opt/verdis-backups/keys}"
KEYSTORE_DIR="/opt/verdis-chain-rust/data/keystore"
RETENTION_COUNT=5

GPG_RECIPIENT=""
TIMESTAMP=$(date +"%Y%m%d-%HMMSS")
BACKUP_NAME="verdis-keys-${TIMESTAMP}"
TEMP_WORK_DIR=""

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
    if [[ -n "$TEMP_WORK_DIR" ]] && [[ -d "$TEMP_WORK_DIR" ]]; then
        rm -rf "$TEMP_WORK_DIR"
    fi

    if [[ $exit_code -eq 0 ]]; then
        log_success "Key backup finished successfully."
    else
        log_error "Key backup failed with exit code $exit_code."
    fi
}

trap cleanup EXIT INT TERM

# --- Usage Message ---
show_usage() {
    cat << EOF
Usage: $(basename "$0") <gpg-recipient-email-or-keyid> [OPTIONS]
   OR: $(basename "$0") --recipient <gpg-recipient-email-or-keyid>

Safely archives and encrypts the Verdis validator keystore using GPG.

Arguments:
  <recipient>             GPG key ID or email address of recipient

Options:
  -r, --recipient RECPT   Specify GPG recipient
  -h, --help              Show this help message and exit
EOF
}

# --- Parse Arguments ---
parse_args() {
    if [[ $# -eq 0 ]]; then
        log_error "Missing GPG recipient argument."
        show_usage
        exit 1
    fi

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -r|--recipient)
                GPG_RECIPIENT="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                if [[ -z "$GPG_RECIPIENT" ]] && [[ "$1" != -* ]]; then
                    GPG_RECIPIENT="$1"
                    shift
                else
                    log_error "Unknown or duplicate parameter: $1"
                    show_usage
                    exit 1
                fi
                ;;
        esac
    done

    if [[ -z "$GPG_RECIPIENT" ]]; then
        log_error "GPG recipient is required."
        show_usage
        exit 1
    fi
}

# --- Pre-flight Checks ---
check_prerequisites() {
    log_info "Running pre-flight checks..."

    if [[ $EUID -ne 0 ]]; then
        log_warn "Running as non-root user ($USER). Permissions on $KEYSTORE_DIR must be readable."
    fi

    if ! command -v gpg >/dev/null 2>&1; then
        log_error "GPG command 'gpg' is not installed."
        exit 1
    fi

    if [[ ! -d "$KEYSTORE_DIR" ]]; then
        log_error "Keystore directory $KEYSTORE_DIR does not exist!"
        exit 1
    fi

    mkdir -p "$KEY_BACKUP_DIR"
    mkdir -p "$(dirname "$LOG_FILE")"

    # Verify recipient key exists in gpg keyring (optional check, fallback if key import required)
    if ! gpg --list-keys "$GPG_RECIPIENT" >/dev/null 2>&1; then
        log_warn "GPG recipient '$GPG_RECIPIENT' not found in local keyring. Attempting encryption anyway (or ensure public key is imported)."
    fi

    log_success "Pre-flight checks passed."
}

# --- Perform Encrypted Key Backup ---
backup_and_encrypt() {
    TEMP_WORK_DIR=$(mktemp -d /tmp/verdis-key-backup-XXXXXX)
    log_info "Staging keystore from $KEYSTORE_DIR..."

    mkdir -p "$TEMP_WORK_DIR/keystore"
    rsync -a "$KEYSTORE_DIR/" "$TEMP_WORK_DIR/keystore/"

    # Add key backup metadata
    cat << EOF > "$TEMP_WORK_DIR/key-manifest.json"
{
  "backup_type": "keystore-encrypted",
  "timestamp": "$TIMESTAMP",
  "keystore_path": "$KEYSTORE_DIR",
  "gpg_recipient": "$GPG_RECIPIENT",
  "key_count": $(find "$KEYSTORE_DIR" -type f | wc -l)
}
EOF

    local unencrypted_tar="$TEMP_WORK_DIR/${BACKUP_NAME}.tar"
    local encrypted_target="${KEY_BACKUP_DIR}/${BACKUP_NAME}.tar.gz.gpg"

    log_info "Creating unencrypted tarball in temporary directory..."
    tar -czf "$unencrypted_tar" -C "$TEMP_WORK_DIR" keystore key-manifest.json

    log_info "Encrypting key archive for GPG recipient: $GPG_RECIPIENT..."
    if gpg --batch --yes --trust-model always --encrypt --recipient "$GPG_RECIPIENT" --output "$encrypted_target" "$unencrypted_tar"; then
        log_success "Keystore successfully encrypted to $encrypted_target"
    else
        log_error "GPG encryption failed!"
        exit 1
    fi

    # Set strict permissions (600) on encrypted file
    chmod 600 "$encrypted_target"

    # Calculate SHA-256 for the encrypted output
    sha256sum "$encrypted_target" > "${encrypted_target}.sha256"
    chmod 600 "${encrypted_target}.sha256"

    # Maintain latest symlinks
    ln -sf "$encrypted_target" "${KEY_BACKUP_DIR}/verdis-keys-latest.tar.gz.gpg"
    ln -sf "${encrypted_target}.sha256" "${KEY_BACKUP_DIR}/verdis-keys-latest.tar.gz.gpg.sha256"

    log_success "Encrypted key backup complete: $encrypted_target"
}

# --- Retention Policy Cleanup (Keep last 5) ---
prune_old_key_backups() {
    log_info "Applying key backup retention policy (keeping last $RETENTION_COUNT backups)..."

    local archives=()
    while IFS= read -r file; do
        archives+=("$file")
    done < <(find "$KEY_BACKUP_DIR" -maxdepth 1 -name "verdis-keys-*.tar.gz.gpg" -type f | sort -r)

    local count=${#archives[@]}
    log_info "Found $count encrypted key archive(s) in $KEY_BACKUP_DIR."

    if [[ $count -gt $RETENTION_COUNT ]]; then
        for ((i=RETENTION_COUNT; i<count; i++)); do
            local archive_to_remove="${archives[$i]}"
            local sha_to_remove="${archive_to_remove}.sha256"
            log_info "Pruning old key backup: $archive_to_remove"
            rm -f "$archive_to_remove" "$sha_to_remove"
        done
    fi
}

# --- Main Execution ---
main() {
    log_info "Starting Verdis Validator Key Backup Procedure..."
    parse_args "$@"
    check_prerequisites
    backup_and_encrypt
    prune_old_key_backups
    log_success "Verdis Key Backup Procedure completed successfully."
}

main "$@"
