# Verdis CI/CD Pipeline

Complete continuous integration and deployment pipeline for the Verdis blockchain.

## Pipeline Overview

```
Push to main → CI (fmt, clippy, test, build, docker)
Tag v*.*.*  → Release (binaries, Docker, checksums, signatures)
Release     → Deploy (staging → integration tests → production)
```

## GitHub Actions Workflows

| Workflow | Trigger | Description |
|----------|---------|-------------|
| `ci.yml` | Push/PR | fmt check, clippy, test, build, Docker build, security audit |
| `release.yml` | Tag v*.*.* | Release binaries, Docker push, checksums, GPG signing |
| `deploy.yml` | Release published | Deploy to staging, integration tests, production approval |

## Quick Start

```bash
# Copy workflows to your repo
cp -r .github /path/to/verdis-chain-rust/

# Run integration tests against a running node
./integration-tests.sh http://localhost:9944

# Generate release artifacts
./release-artifacts.sh

# Generate checksums
./checksums.sh dist/

# Publish Docker image
./docker-publish.sh
```

## CI Checks

### 1. Format Check
```bash
cargo fmt --all -- --check
```

### 2. Clippy (lint)
```bash
cargo clippy --all-targets -- -D warnings
```

### 3. Tests
```bash
cargo test --all --release
```

### 4. Build (with WASM)
```bash
cargo build --release
```

### 5. Security Audit
```bash
cargo audit
```

## Release Artifacts

The release pipeline produces:
- Stripped Linux binary (`verdis-linux-amd64`)
- Docker image (`verdis-chain:latest`, `verdis-chain:v*.*.*`)
- SHA-256 and MD5 checksums
- GPG signatures (if key available)
- Release tarball (binary + chain spec + docs)

## Docker

### Build
```bash
docker build -f Dockerfile -t verdis-chain:latest .
```

### Run
```bash
docker run -d \
  -p 9944:9944 \
  -p 30333:30333 \
  -v verdis-data:/data \
  verdis-chain:latest \
  --chain testnet --validator
```

### Publish
```bash
# To Docker Hub
docker tag verdis-chain:latest verdischain/verdis-chain:latest
docker push verdischain/verdis-chain:latest

# To GHCR
docker tag verdis-chain:latest ghcr.io/verdischain/verdis-chain:latest
docker push ghcr.io/verdischain/verdis-chain:latest
```

## Integration Tests

```bash
# Start node first
./target/release/verdis --chain dev --validator

# Run tests
./integration-tests.sh http://localhost:9944
```

Tests cover:
- Node health (system_health)
- Block production (chain_getHeader over 7s)
- GRANDPA finality lag (≤ 10 blocks)
- RPC endpoints (system_version, chain, name, properties)
- Runtime version
- Token supply storage
- Peer information
- GRANDPA round state
- Epoch transition tracking
- WebSocket endpoint

## Deployment

### Staging
1. Deploy to staging server
2. Run integration tests
3. Verify block production and finality

### Production
1. Manual approval gate
2. SSH to production server
3. Pull latest code
4. Rebuild binary
5. Restart systemd service
6. Health check
7. Auto-rollback on failure

## File Structure

```
ci-cd/
├── .github/workflows/
│   ├── ci.yml              # CI pipeline
│   ├── release.yml         # Release pipeline
│   └── deploy.yml          # Deployment pipeline
├── Dockerfile              # Production Docker image
├── docker-publish.sh       # Docker publishing script
├── release-artifacts.sh    # Binary + checksums + tarball
├── checksums.sh            # SHA-256 + MD5 generation
├── integration-tests.sh    # Full integration test suite
└── README.md               # This file
```
