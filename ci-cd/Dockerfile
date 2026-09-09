# ==========================================
# Stage 1: Build Environment
# ==========================================
FROM rust:1.78-bookworm AS builder

LABEL maintainer="Verdis Chain Core Team <dev@verdischain.com>"
LABEL description="Builder image for Verdis Substrate Blockchain Node"

# Install system compilation dependencies for Substrate & WASM
RUN apt-get update && apt-get install -y --no-install-recommends \
    clang \
    libclang-dev \
    pkg-config \
    libssl-dev \
    protobuf-compiler \
    build-essential \
    git \
    cmake \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Add WebAssembly compilation target
RUN rustup target add wasm32-unknown-unknown

WORKDIR /sources/verdis-chain

# Copy source workspace
COPY . .

# Build release binary
RUN cargo build --release --workspace

# Strip binary to reduce container layer size
RUN strip /sources/verdis-chain/target/release/verdis

# ==========================================
# Stage 2: Production Runtime
# ==========================================
FROM debian:bookworm-slim AS runtime

LABEL maintainer="Verdis Chain Core Team <dev@verdischain.com>"
LABEL version="1.0.0"
LABEL description="Verdis Blockchain Production Node (VRS Token, SS58=909, 100B Supply)"

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    libssl3 \
    jq \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user and group (verdis, UID 1000)
RUN groupadd -g 1000 verdis && \
    useradd -u 1000 -g verdis -m -s /bin/bash verdis

# Create data and configuration directories
RUN mkdir -p /data /var/lib/verdis /etc/verdis && \
    chown -R verdis:verdis /data /var/lib/verdis /etc/verdis

# Copy compiled executable from builder stage
COPY --from=builder /sources/verdis-chain/target/release/verdis /usr/local/bin/verdis

# Set binary permissions
RUN chmod +x /usr/local/bin/verdis && chown verdis:verdis /usr/local/bin/verdis

# Expose network ports:
# 30333 - P2P Libp2p port
# 9933  - HTTP RPC port
# 9944  - WebSocket RPC port
EXPOSE 30333 9933 9944

# Switch to non-root user
USER verdis
WORKDIR /data

# Health check endpoint querying system_health via RPC
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -s -f -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"system_health","params":[],"id":1}' \
    http://127.0.0.1:9933/ || exit 1

# Default runtime entrypoint
ENTRYPOINT ["/usr/local/bin/verdis"]
CMD ["--base-path", "/data", "--rpc-external", "--rpc-cors", "all", "--rpc-methods", "safe"]
