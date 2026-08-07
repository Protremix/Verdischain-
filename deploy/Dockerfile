# Stage 1: Build stage
FROM rust:1.78-bookworm AS builder

# Set build environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    CARGO_TERM_COLOR=always \
    WASM_BUILD_TOOLCHAIN=stable \
    RUSTFLAGS="-C link-arg=-Wl,--allow-undefined"

# Install system dependencies required for Rust + Substrate build
RUN apt-get update && apt-get install -y --no-install-recommends \
    clang \
    libclang-dev \
    llvm \
    pkg-config \
    libssl-dev \
    cmake \
    git \
    protobuf-compiler \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Add WASM target for Substrate runtime build
RUN rustup target add wasm32-unknown-unknown

WORKDIR /opt/verdis-chain-rust

# Copy source code into builder container
COPY . .

# Build release binary
RUN cargo build --release --locked || cargo build --release

# Stage 2: Minimal runtime stage
FROM debian:bookworm-slim AS runtime

# Set environment variables
ENV RUST_LOG=info \
    DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies and healthcheck utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libssl3 \
    curl \
    jq \
    tini \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root user and group for security
RUN groupadd -g 10001 verdis \
    && useradd -u 10001 -g verdis -m -d /opt/verdis-chain-rust -s /bin/false verdis

WORKDIR /opt/verdis-chain-rust

# Create persistent chain data directory and assign ownership
RUN mkdir -p /opt/verdis-chain-rust/data && \
    chown -R verdis:verdis /opt/verdis-chain-rust

# Copy release binary from builder
COPY --from=builder /opt/verdis-chain-rust/target/release/verdis /usr/local/bin/verdis
RUN chmod +x /usr/local/bin/verdis && chown verdis:verdis /usr/local/bin/verdis

# Expose P2P port and RPC port
# 30333: P2P communication (public)
# 9944: RPC API (bound internally, host mapping controls public vs localhost access)
EXPOSE 30333 9944

# Configure container healthcheck against Substrate RPC system_health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f -H "Content-Type: application/json" \
      -d '{"id":1, "jsonrpc":"2.0", "method":"system_health", "params":[]}' \
      http://127.0.0.1:9944/ || exit 1

# Switch to non-root user
USER verdis

# Use tini as init system to handle signals and zombie processes
ENTRYPOINT ["/usr/bin/tini", "--", "verdis"]

# Default node startup arguments
CMD [ \
  "--chain", "dev", \
  "--base-path", "/opt/verdis-chain-rust/data", \
  "--rpc-port", "9944", \
  "--port", "30333", \
  "--rpc-methods", "Safe", \
  "--validator", \
  "--alice", \
  "--rpc-cors", "all", \
  "--unsafe-rpc-external" \
]
