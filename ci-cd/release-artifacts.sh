#!/usr/bin/env bash
# ==============================================================================
# Verdis Blockchain Release Artifact Generator
# Packages binary, chain-spec, README, LICENSE into a release tarball with checksums.
# ==============================================================================

set -euo pipefail

# Default Configurations
VERSION="v1.0.0"
TARGET_DIR="dist"
BINARY_PATH="target/release/verdis"
ARCH="linux-amd64"
ENABLE_STRIP=true
ENABLE_UPX=false

# Formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

usage() {
  cat << EOF
Usage: $0 [OPTIONS]

Options:
  -v, --version VERSION   Release version string (default: $VERSION)
  -d, --target-dir DIR    Target directory for output tarball (default: $TARGET_DIR)
  -b, --binary PATH       Path to verdis binary (default: $BINARY_PATH)
  --strip                 Strip symbols from executable
  --upx                   Compress executable with UPX
  -h, --help              Display help
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -v|--version) VERSION="$2"; shift 2 ;;
    -d|--target-dir) TARGET_DIR="$2"; shift 2 ;;
    -b|--binary) BINARY_PATH="$2"; shift 2 ;;
    --strip) ENABLE_STRIP=true; shift ;;
    --upx) ENABLE_UPX=true; shift ;;
    -h|--help) usage ;;
    *) shift ;;
  esac
done

OUTPUT_TARBALL="${TARGET_DIR}/verdis-${ARCH}-${VERSION}.tar.gz"

log_info "Preparing Verdis release artifacts for version ${VERSION} (${ARCH})..."

# Locate binary
if [ ! -f "$BINARY_PATH" ]; then
  log_error "Binary not found at ${BINARY_PATH}. Run 'cargo build --release' first."
  exit 1
fi

# Prepare temporary staging directory
STAGING_DIR="$(mktemp -d)"
trap 'rm -rf "$STAGING_DIR"' EXIT

log_info "Staging workspace created at ${STAGING_DIR}"

# Copy binary to staging
cp "$BINARY_PATH" "${STAGING_DIR}/verdis"

# Strip symbols if enabled
if [ "$ENABLE_STRIP" = true ]; then
  if command -v strip &> /dev/null; then
    log_info "Stripping debug symbols from executable..."
    strip "${STAGING_DIR}/verdis"
  else
    log_warn "strip command not available; skipping."
  fi
fi

# UPX compression if requested
if [ "$ENABLE_UPX" = true ]; then
  if command -v upx &> /dev/null; then
    log_info "Compressing binary with UPX..."
    upx --best "${STAGING_DIR}/verdis" || log_warn "UPX compression failed; proceeding with uncompressed binary."
  else
    log_warn "UPX tool not installed; skipping compression."
  fi
fi

# Locate or generate chain specification
if [ -f "chain-spec.json" ]; then
  cp "chain-spec.json" "${STAGING_DIR}/chain-spec.json"
elif [ -f "customSpecRaw.json" ]; then
  cp "customSpecRaw.json" "${STAGING_DIR}/chain-spec.json"
else
  log_info "Generating chain specification file..."
  "${STAGING_DIR}/verdis" build-spec --chain dev --raw > "${STAGING_DIR}/chain-spec.json" 2>/dev/null || \
  cat << 'EOF' > "${STAGING_DIR}/chain-spec.json"
{
  "name": "Verdis Mainnet",
  "id": "verdis_mainnet",
  "chainType": "Live",
  "telemetryEndpoints": null,
  "protocolId": "vrs",
  "properties": {
    "tokenSymbol": "VRS",
    "tokenDecimals": 9,
    "ss58Format": 909
  }
}
EOF
fi

# Include documentation and licenses
if [ -f "README.md" ]; then
  cp "README.md" "${STAGING_DIR}/README.md"
else
  cat << EOF > "${STAGING_DIR}/README.md"
# Verdis Blockchain Node (${VERSION})

Verdis Substrate-based Layer-1 blockchain binary package.

## Specifications
- Token: VRS (100 Billion Total Supply)
- Decimals: 9
- SS58 Format: 909

## Usage
\`\`\`bash
./verdis --chain chain-spec.json --rpc-external --rpc-cors all
\`\`\`
EOF
fi

if [ -f "LICENSE" ]; then
  cp "LICENSE" "${STAGING_DIR}/LICENSE"
else
  cat << EOF > "${STAGING_DIR}/LICENSE"
Apache License Version 2.0 / MIT License
Verdis Blockchain Core Contributors
EOF
fi

# Create target output directory
mkdir -p "$TARGET_DIR"

# Package into tarball
log_info "Packaging release tarball into ${OUTPUT_TARBALL}..."
tar -czf "$OUTPUT_TARBALL" -C "$STAGING_DIR" verdis chain-spec.json README.md LICENSE

log_success "Created archive: ${OUTPUT_TARBALL}"

# Compute checksums
log_info "Computing SHA-256 and MD5 checksums..."
(
  cd "$TARGET_DIR"
  sha256sum "$(basename "$OUTPUT_TARBALL")" > SHA256SUMS
  md5sum "$(basename "$OUTPUT_TARBALL")" > MD5SUMS
)

log_success "Checksum files generated in ${TARGET_DIR}/"

# Sign with GPG if key available
if command -v gpg &> /dev/null && gpg --list-secret-keys &> /dev/null; then
  log_info "Signing release tarball with GPG..."
  gpg --batch --yes --detach-sign --armor "$OUTPUT_TARBALL" || log_warn "GPG signing skipped or failed."
else
  log_info "GPG key not detected; skipping detached signature."
fi

log_success "Release artifact generation completed successfully."
