#!/usr/bin/env bash
# ==============================================================================
# Verdis Backup Verification Script
# Script Name: verify-backup.sh
# Purpose: Validates archive integrity, file presence, and SHA-256 checksums
# Domain: verdischain.com | Server: 91.98.160.145
# ==============================================================================

set -euo pipefail

# --- Configuration & Constants ---
LOG_FILE="/var/log/verdis-verify.log"
BACKUP_FILE=""
TEMP_EXTRACT_DIR=""

FAILED_CHECKS=0
TOTAL_CHECKS=0

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

# --- Reporting Helper ---
report_check() {
    local name="$1"
    local status="$2" # PASS or FAIL
    local details="${3:-}"

    ((TOTAL_CHECKS++))
    if [[ "$status" == "PASS" ]]; then
        printf "  [✓] PASS: %-35s %s\n" "$name" "$details"
    else
        printf "  [✗] FAIL: %-35s %s\n" "$name" "$details"
        ((FAILED_CHECKS++))
    fi
}

# --- Cleanup Trap ---
cleanup() {
    if [[ -n "$TEMP_EXTRACT_DIR" ]] && [[ -d "$TEMP_EXTRACT_DIR" ]]; then
        rm -rf "$TEMP_EXTRACT_DIR"
    fi
}

trap cleanup EXIT INT TERM

# --- Usage Message ---
show_usage() {
    cat << EOF
Usage: $(basename "$0") <path-to-backup.tar.gz> [OPTIONS]

Verifies the integrity, structure, and file checksums of a Verdis backup archive.

Arguments:
  <path-to-backup.tar.gz>   Path to the backup file (.tar.gz)

Options:
  -h, --help                Show this help message and exit
EOF
}

# --- Parse Arguments ---
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

# --- Check Archive File ---
verify_archive_file() {
    log_info "Verifying archive file existence and outer checksum..."

    if [[ ! -f "$BACKUP_FILE" ]]; then
        report_check "Backup File Existence" "FAIL" "File does not exist: $BACKUP_FILE"
        exit 1
    else
        report_check "Backup File Existence" "PASS" "Found $BACKUP_FILE"
    fi

    # Check companion .sha256 file
    local sha_file="${BACKUP_FILE}.sha256"
    if [[ -f "$sha_file" ]]; then
        if sha256sum -c "$sha_file" >/dev/null 2>&1; then
            report_check "Archive SHA-256 Signature" "PASS" "Companion checksum valid"
        else
            report_check "Archive SHA-256 Signature" "FAIL" "Companion checksum mismatch"
        fi
    else
        report_check "Archive SHA-256 Signature" "WARN" "No companion .sha256 file found"
    fi

    # Check gzip tar structure
    if tar -tzf "$BACKUP_FILE" >/dev/null 2>&1; then
        report_check "Tar Archive Structure" "PASS" "Valid gzip tar archive"
    else
        report_check "Tar Archive Structure" "FAIL" "Archive corrupted or invalid format"
        exit 1
    fi
}

# --- Unpack and Check Contents ---
verify_extracted_contents() {
    TEMP_EXTRACT_DIR=$(mktemp -d /tmp/verdis-verify-XXXXXX)
    log_info "Unpacking backup into temporary workspace for inspection..."
    tar -xzf "$BACKUP_FILE" -C "$TEMP_EXTRACT_DIR"

    log_info "Checking required file components..."

    # 1. Chain Spec
    if [[ -f "$TEMP_EXTRACT_DIR/chain-spec.json" ]]; then
        report_check "Component: Chain Spec" "PASS" "chain-spec.json present"
    else
        report_check "Component: Chain Spec" "FAIL" "chain-spec.json missing"
    fi

    # 2. Database Directory
    if [[ -d "$TEMP_EXTRACT_DIR/data" ]] && [[ $(find "$TEMP_EXTRACT_DIR/data" -type f | wc -l) -gt 0 ]]; then
        local db_files
        db_files=$(find "$TEMP_EXTRACT_DIR/data" -type f | wc -l)
        report_check "Component: Database (RocksDB)" "PASS" "data/ directory present ($db_files files)"
    else
        report_check "Component: Database (RocksDB)" "FAIL" "data/ directory missing or empty"
    fi

    # 3. Keystore Directory
    if [[ -d "$TEMP_EXTRACT_DIR/keystore" ]]; then
        local key_files
        key_files=$(find "$TEMP_EXTRACT_DIR/keystore" -type f | wc -l)
        report_check "Component: Keystore" "PASS" "keystore/ present ($key_files keys)"
    else
        report_check "Component: Keystore" "FAIL" "keystore/ directory missing"
    fi

    # 4. Nginx Config
    if [[ -f "$TEMP_EXTRACT_DIR/nginx/verdischain.conf" ]]; then
        report_check "Component: Nginx Config" "PASS" "nginx/verdischain.conf present"
    else
        report_check "Component: Nginx Config" "FAIL" "nginx/verdischain.conf missing"
    fi

    # 5. Systemd Service
    if [[ -f "$TEMP_EXTRACT_DIR/systemd/verdis-node.service" ]]; then
        report_check "Component: Systemd Service" "PASS" "systemd/verdis-node.service present"
    else
        report_check "Component: Systemd Service" "FAIL" "systemd/verdis-node.service missing"
    fi

    # 6. Logrotate
    if [[ -f "$TEMP_EXTRACT_DIR/logrotate/verdis" ]]; then
        report_check "Component: Logrotate Config" "PASS" "logrotate/verdis present"
    else
        report_check "Component: Logrotate Config" "FAIL" "logrotate/verdis missing"
    fi

    # 7. Metadata Manifest
    if [[ -f "$TEMP_EXTRACT_DIR/metadata.json" ]]; then
        report_check "Component: Metadata Manifest" "PASS" "metadata.json present"
    else
        report_check "Component: Metadata Manifest" "WARN" "metadata.json missing"
    fi

    # 8. Check internal SHA256SUMS manifest
    if [[ -f "$TEMP_EXTRACT_DIR/SHA256SUMS" ]]; then
        log_info "Verifying internal SHA256SUMS file integrity..."
        (
            cd "$TEMP_EXTRACT_DIR"
            if sha256sum -c SHA256SUMS >/dev/null 2>&1; then
                report_check "Internal SHA256 Manifest" "PASS" "All internal files matched SHA256SUMS"
            else
                report_check "Internal SHA256 Manifest" "FAIL" "One or more internal files failed SHA256 verification"
            fi
        )
    else
        report_check "Internal SHA256 Manifest" "FAIL" "SHA256SUMS manifest file missing inside archive"
    fi
}

# --- Main Execution ---
main() {
    mkdir -p "$(dirname "$LOG_FILE")"
    parse_args "$@"

    echo "================================================================="
    log_info "Starting Verification of Verdis Backup: $BACKUP_FILE"
    echo "================================================================="

    verify_archive_file
    verify_extracted_contents

    echo "================================================================="
    echo "VERIFICATION SUMMARY:"
    echo "  Total Checks Performed: $TOTAL_CHECKS"
    echo "  Failed Checks:          $FAILED_CHECKS"
    echo "================================================================="

    if [[ $FAILED_CHECKS -eq 0 ]]; then
        log_success "Backup Verification Status: PASSED (All checks passed)."
        exit 0
    else
        log_error "Backup Verification Status: FAILED ($FAILED_CHECKS check(s) failed)."
        exit 1
    fi
}

main "$@"
