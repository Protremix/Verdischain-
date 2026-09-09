# =============================================================================
# Stage 1: Build Environment
# =============================================================================
FROM rust:1.78-slim AS builder

LABEL maintainer="Verdis Network Engineers <devops@verdischain.com>"
LABEL description="Multi-stage build container for Verdis Substrate blockchain node"

ENV DEBIAN_FRONTEND=noninteractive
ENV CARGO_HOME=/usr/local/cargo

# Install required build dependencies for Substrate Rust compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    clang \
    libssl-dev \
    pkg-config \
    build-essential \
    git \
    protobuf-compiler \
    cmake \
    curl \
    lld \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/verdis

# Copy Rust source tree
COPY . .

# Build release binary for the Verdis node
RUN cargo build --release --locked || cargo build --release

# =============================================================================
# Stage 2: Runtime Environment
# =============================================================================
FROM debian:bookworm-slim AS runtime

LABEL maintainer="Verdis Network Engineers <devops@verdischain.com>"
LABEL org.opencontainers.image.title="Verdis Blockchain Node"
LABEL org.opencontainers.image.description="Production Substrate node for Verdis Network (VRS, Chain ID 909)"

ENV DEBIAN_FRONTEND=noninteractive

# Install essential runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libssl3 \
    curl \
    jq \
    iputils-ping \
    libstdc++6 \
    libc6 \
    netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root user and group
RUN groupadd -g 1000 verdis \
 && useradd -u 1000 -g verdis -m -s /bin/bash verdis

# Create data directories and binary output path matching project spec
RUN mkdir -p /data /etc/verdis /opt/verdis-chain-rust/target/release \
 && chown -R verdis:verdis /data /etc/verdis /opt/verdis-chain-rust

# Copy binary from builder
COPY --from=builder --chown=verdis:verdis /usr/src/verdis/target/release/verdis /usr/local/bin/verdis

# Symlink to /opt/verdis-chain-rust/target/release/verdis per specification
RUN ln -sf /usr/local/bin/verdis /opt/verdis-chain-rust/target/release/verdis

# Expose P2P (30333), RPC (9944), WebSocket (9933), Prometheus (9615)
EXPOSE 30333 9944 9933 9615

USER verdis
WORKDIR /data

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f -s -H 'Content-Type: application/json' -d '{"id":1,"jsonrpc":"2.0","method":"system_health","params":[]}' http://localhost:9944 || exit 1

ENTRYPOINT ["/usr/local/bin/verdis"]
CMD ["--help"]
