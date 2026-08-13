# Verdis Blockchain Release and Operations Makefile
# Version: 2.0.0

.PHONY: all build test docker-build docker-run docker-stop release-package checksums verify-checksums clean help

IMAGE_NAME ?= verdis:v2.0.0
CONTAINER_NAME ?= verdis-node
RELEASE_VERSION ?= 2.0.0
BUILD_DIR ?= target/release
ARCH ?= x86_64-unknown-linux-gnu
PACKAGE_NAME ?= verdis-v$(RELEASE_VERSION)-$(ARCH)

all: help

help:
	@echo "Verdis Chain v2.0.0 Deployment Makefile"
	@echo "========================================"
	@echo "Available targets:"
	@echo "  make build           - Build Rust release binary (cargo build --release)"
	@echo "  make test            - Execute full test suite (cargo test --all)"
	@echo "  make docker-build    - Build production Docker image ($(IMAGE_NAME))"
	@echo "  make docker-run      - Run single-node validator using docker-compose"
	@echo "  make docker-multi    - Run 5-node testnet cluster using docker-compose.multi.yml"
	@echo "  make docker-stop     - Stop and remove running docker-compose containers"
	@echo "  make release-package - Create release archive tarball with artifacts"
	@echo "  make checksums       - Generate SHA256 checksums for release files"
	@echo "  make verify-checksums- Verify SHA256 checksums against manifest"
	@echo "  make clean           - Clean Cargo target and release package artifacts"

build:
	@echo "Building Verdis Chain v$(RELEASE_VERSION) release binary..."
	RUSTFLAGS="-C link-arg=-Wl,--allow-undefined" cargo build --release

test:
	@echo "Running unit and integration tests..."
	cargo test --all

docker-build:
	@echo "Building Docker image $(IMAGE_NAME)..."
	docker build -f Dockerfile -t $(IMAGE_NAME) ..

docker-run:
	@echo "Starting single-node validator service..."
	docker-compose -f docker-compose.yml up -d

docker-multi:
	@echo "Starting 5-node validator cluster..."
	docker-compose -f docker-compose.multi.yml up -d

docker-stop:
	@echo "Stopping Docker containers..."
	docker-compose -f docker-compose.yml down
	docker-compose -f docker-compose.multi.yml down 2>/dev/null || true

release-package: build checksums
	@echo "Packaging production release $(PACKAGE_NAME).tar.gz..."
	mkdir -p dist/$(PACKAGE_NAME)
	cp -r Dockerfile docker-compose.yml docker-compose.multi.yml RELEASE.md version-manifest.json checksums.sh SHA256SUMS dist/$(PACKAGE_NAME)/
	if [ -f "../$(BUILD_DIR)/verdis" ]; then cp "../$(BUILD_DIR)/verdis" dist/$(PACKAGE_NAME)/; fi
	if [ -f "../verdis" ]; then cp "../verdis" dist/$(PACKAGE_NAME)/; fi
	tar -czvf $(PACKAGE_NAME).tar.gz -C dist $(PACKAGE_NAME)
	@echo "Release archive created: $(PACKAGE_NAME).tar.gz"

checksums:
	@echo "Generating SHA256 checksums..."
	./checksums.sh

verify-checksums:
	@echo "Verifying SHA256 checksums..."
	./checksums.sh --verify

clean:
	@echo "Cleaning workspace build artifacts..."
	cargo clean 2>/dev/null || true
	rm -rf dist $(PACKAGE_NAME).tar.gz SHA256SUMS
