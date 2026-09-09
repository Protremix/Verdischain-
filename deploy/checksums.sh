#!/usr/bin/env bash
# Verdis Blockchain Deployment Artifacts - Checksum Generator and Verifier
# Copyright (c) 2026 Verdis Chain Foundation
# License: Apache-2.0

set -euo pipefail

# Locate script directory to ensure relative paths resolve properly
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
CHECKSUM_FILE="$SCRIPT_DIR/SHA256SUMS"

# Colors for output logging
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

generate_checksums() {
    log_info "Generating SHA256 checksums for Verdis deployment artifacts..."
    
    # List of files to include in the checksum, relative to script directory
    declare -a FILES=(
        "Dockerfile"
        "docker-compose.yml"
        "docker-compose.multi.yml"
        "RELEASE.md"
        "version-manifest.json"
        "Makefile"
        "checksums.sh"
    )

    # Optional paths to compiled binary and WASM blobs if they exist
    declare -a OPTIONAL_FILES=(
        "../target/release/verdis"
        "../verdis"
        "../verdis_runtime.wasm"
        "../verdis_runtime.compact.compressed.wasm"
    )

    # Clear/create the checksum file
    true > "$CHECKSUM_FILE"

    # Hash mandatory artifacts
    for file in "${FILES[@]}"; do
        if [ -f "$SCRIPT_DIR/$file" ]; then
            cd "$SCRIPT_DIR"
            sha256sum "$file" >> "$CHECKSUM_FILE"
            log_info "Hashed: $file"
        else
            log_warn "Mandatory file not found: $file"
        fi
    done

    # Hash optional artifacts if available
    for file in "${OPTIONAL_FILES[@]}"; do
        # Absolute or relative to script dir
        local full_path
        full_path="$(cd "$SCRIPT_DIR" && realpath -m "$file")"
        if [ -f "$full_path" ]; then
            local rel_path
            rel_path="$(cd "$SCRIPT_DIR" && realpath --relative-to="$SCRIPT_DIR" "$full_path")"
            cd "$SCRIPT_DIR"
            sha256sum "$rel_path" >> "$CHECKSUM_FILE"
            log_info "Hashed optional: $rel_path"
        fi
    done

    log_success "Checksums successfully written to: $CHECKSUM_FILE"
    echo "--------------------------------------------------------"
    cat "$CHECKSUM_FILE"
    echo "--------------------------------------------------------"
}

verify_checksums() {
    if [ ! -f "$CHECKSUM_FILE" ]; then
        log_error "Checksum file not found: $CHECKSUM_FILE. Please generate it first."
        exit 1
    fi

    log_info "Verifying SHA256 checksums from $CHECKSUM_FILE..."
    cd "$SCRIPT_DIR"
    
    if sha256sum -c --strict "$CHECKSUM_FILE"; then
        log_success "All artifact checksums VERIFIED successfully!"
    else
        log_error "Artifact checksum verification FAILED! Integrity compromised."
        exit 1
    fi
}

# Main routing logic
if [ "${1:-}" = "--verify" ] || [ "${1:-}" = "-c" ]; then
    verify_checksums
else
    generate_checksums
fi
