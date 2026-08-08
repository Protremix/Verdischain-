# Multi-stage build for Verdis Substrate blockchain node

# Stage 1: Builder stage
FROM rust:1.78-bookworm AS builder

WORKDIR /usr/src/app

# Install build dependencies
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
    && apt-get clean && find /var/lib/apt/lists/ -type f -delete

# Add WASM target for Substrate runtime build
RUN rustup target add wasm32-unknown-unknown

# Copy source code
COPY . .

# Build release binary
RUN WASM_BUILD_RUSTFLAGS="-C link-arg=--import-undefined" cargo build --release --bin verdis || cargo build --release

# Stage 2: Minimal runtime stage
FROM ubuntu:22.04

LABEL maintainer="Verdis Core Team <dev@verdis.network>"

ENV DEBIAN_FRONTEND=noninteractive

# Install minimal runtime dependencies and clean apt cache
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && apt-get clean && find /var/lib/apt/lists/ -type f -delete

# Create non-root user verdis with UID 1000
RUN groupadd -g 1000 verdis && \
    useradd -u 1000 -g verdis -m -d /data -s /bin/false verdis

# Copy release binary from builder
COPY --from=builder /usr/src/app/target/release/verdis /usr/local/bin/verdis
RUN chmod +x /usr/local/bin/verdis && chown verdis:verdis /usr/local/bin/verdis

# Create persistent data directory with permissions
RUN mkdir -p /data && chown -R verdis:verdis /data

WORKDIR /data

# Expose only P2P port publicly
EXPOSE 30333

STOPSIGNAL SIGTERM

VOLUME ["/data"]

USER verdis

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -f http://localhost:9944/ || exit 1

ENTRYPOINT ["/usr/local/bin/verdis"]
CMD ["--chain", "dev", "--base-path", "/data", "--port", "30333", "--rpc-port", "9944", "--prometheus-port", "9615"]
