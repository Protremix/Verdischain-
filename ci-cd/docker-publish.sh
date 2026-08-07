#!/usr/bin/env bash
# ==============================================================================
# Verdis Blockchain Docker Publish & Signing Script
# Handles building, tagging, pushing, SBOM generation, and cosign signing.
# ==============================================================================

set -euo pipefail

# Default configuration
REGISTRY="${REGISTRY:-ghcr.io/verdischain}"
IMAGE_NAME="${IMAGE_NAME:-verdis-chain}"
VERSION="${VERSION:-1.0.0}"
COMMIT_SHA="$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")"
DOCKERFILE="${DOCKERFILE:-ci-cd/Dockerfile}"
PUSH=false
SIGN=true
GENERATE_SBOM=true

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
  -r, --registry REGISTRY   Container registry (default: $REGISTRY)
  -n, --name NAME           Image name (default: $IMAGE_NAME)
  -v, --version VERSION     Version tag (default: $VERSION)
  -f, --file DOCKERFILE     Path to Dockerfile (default: $DOCKERFILE)
  -p, --push                Push image to registry after building
  --no-sign                 Skip cosign image signing
  --no-sbom                 Skip SBOM generation
  -h, --help                Display this help message

Example:
  ./ci-cd/docker-publish.sh --registry ghcr.io/verdischain --version v1.0.0 --push
EOF
  exit 0
}

# Parse parameters
while [[ $# -gt 0 ]]; do
  case "$1" in
    -r|--registry) REGISTRY="$2"; shift 2 ;;
    -n|--name) IMAGE_NAME="$2"; shift 2 ;;
    -v|--version) VERSION="$2"; shift 2 ;;
    -f|--file) DOCKERFILE="$2"; shift 2 ;;
    -p|--push) PUSH=true; shift ;;
    --no-sign) SIGN=false; shift ;;
    --no-sbom) GENERATE_SBOM=false; shift ;;
    -h|--help) usage ;;
    *) log_error "Unknown parameter $1"; usage ;;
  esac
done

FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}"
TAG_LATEST="${FULL_IMAGE}:latest"
TAG_VERSION="${FULL_IMAGE}:${VERSION}"
TAG_SHA="${FULL_IMAGE}:${COMMIT_SHA}"

log_info "Starting Docker Image Build Process"
log_info "Target Image Tags:"
log_info "  - ${TAG_LATEST}"
log_info "  - ${TAG_VERSION}"
log_info "  - ${TAG_SHA}"

if [ ! -f "$DOCKERFILE" ]; then
  log_error "Dockerfile not found at path: $DOCKERFILE"
  exit 1
fi

# Build Image
log_info "Building Docker image..."
docker build \
  -f "$DOCKERFILE" \
  -t "$TAG_LATEST" \
  -t "$TAG_VERSION" \
  -t "$TAG_SHA" \
  --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
  --build-arg VCS_REF="$COMMIT_SHA" \
  .

log_success "Docker image built successfully!"

# Generate SBOM
if [ "$GENERATE_SBOM" = true ]; then
  log_info "Generating Software Bill of Materials (SBOM)..."
  mkdir -p build/sbom
  if command -v syft &> /dev/null; then
    syft "$TAG_VERSION" -o spdx-json > "build/sbom/verdis-sbom-${VERSION}.spdx.json"
    log_success "SBOM generated using syft: build/sbom/verdis-sbom-${VERSION}.spdx.json"
  elif docker buildx sbom --help &> /dev/null; then
    docker buildx bake --sbom || true
    log_info "Docker buildx SBOM created"
  elif command -v trivy &> /dev/null; then
    trivy image --format spdx-json -o "build/sbom/verdis-sbom-${VERSION}.spdx.json" "$TAG_VERSION"
    log_success "SBOM generated using trivy: build/sbom/verdis-sbom-${VERSION}.spdx.json"
  else
    log_warn "Neither syft nor trivy installed; writing basic JSON SBOM manifest."
    cat << EOF > "build/sbom/verdis-sbom-${VERSION}.json"
{
  "spdxVersion": "SPDX-2.3",
  "dataLicense": "CC0-1.0",
  "name": "verdis-chain",
  "version": "${VERSION}",
  "gitCommit": "${COMMIT_SHA}",
  "created": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
}
EOF
    log_success "Created basic SBOM file build/sbom/verdis-sbom-${VERSION}.json"
  fi
fi

# Push to Registry
if [ "$PUSH" = true ]; then
  log_info "Pushing tags to registry ${REGISTRY}..."
  docker push "$TAG_LATEST"
  docker push "$TAG_VERSION"
  docker push "$TAG_SHA"
  log_success "All image tags pushed successfully."

  # Sign image if cosign available
  if [ "$SIGN" = true ]; then
    if command -v cosign &> /dev/null; then
      log_info "Signing container image with Cosign..."
      cosign sign --yes "$TAG_VERSION" || log_warn "Cosign signing failed or key not configured."
    else
      log_warn "Cosign utility not found in PATH; skipping image signing."
    fi
  fi
else
  log_info "Push skipped. Use --push to push images to remote registry."
fi

log_success "Docker publish script completed successfully."
