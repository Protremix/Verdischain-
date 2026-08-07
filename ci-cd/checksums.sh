#!/usr/bin/env bash
# Verdis Checksum Generation Script
# Generates SHA-256 and MD5 checksums for release artifacts
set -euo pipefail

ARTIFACTS_DIR="${1:-dist}"
CHECKSUMS_DIR="${2:-.}"

echo "================================================"
echo "  Verdis Checksum Generation"
echo "  Artifacts: $ARTIFACTS_DIR"
echo "  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "================================================"

if [ ! -d "$ARTIFACTS_DIR" ]; then
    echo "  ❌ Artifacts directory not found: $ARTIFACTS_DIR"
    exit 1
fi

SHA256_FILE="$CHECKSUMS_DIR/SHA256SUMS"
MD5_FILE="$CHECKSUMS_DIR/MD5SUMS"

# Clear existing
> "$SHA256_FILE"
> "$MD5_FILE"

# Generate checksums for all artifacts
echo ""
echo "Generating checksums..."
COUNT=0
for file in "$ARTIFACTS_DIR"/*; do
    if [ -f "$file" ]; then
        FILENAME=$(basename "$file")
        
        # SHA-256
        SHA256=$(sha256sum "$file" | awk '{print $1}')
        echo "$SHA256  $FILENAME" >> "$SHA256_FILE"
        
        # MD5
        MD5=$(md5sum "$file" | awk '{print $1}')
        echo "$MD5  $FILENAME" >> "$MD5_FILE"
        
        echo "  ✅ $FILENAME"
        echo "     SHA-256: $SHA256"
        echo "     MD5:     $MD5"
        COUNT=$((COUNT + 1))
    fi
done

# Sign with GPG if key available
if command -v gpg &>/dev/null && gpg --list-secret-keys &>/dev/null 2>&1; then
    echo ""
    echo "Signing checksums with GPG..."
    gpg --detach-sign --armor "$SHA256_FILE" 2>/dev/null && echo "  ✅ SHA256SUMS.asc signed" || echo "  ⚠️  GPG signing failed"
    gpg --detach-sign --armor "$MD5_FILE" 2>/dev/null && echo "  ✅ MD5SUMS.asc signed" || echo "  ⚠️  GPG signing failed"
else
    echo ""
    echo "  ⚠️  No GPG key available, skipping signature"
fi

echo ""
echo "================================================"
echo "  Checksums generated for $COUNT files"
echo "  SHA-256: $SHA256_FILE"
echo "  MD5:     $MD5_FILE"
echo "================================================"
