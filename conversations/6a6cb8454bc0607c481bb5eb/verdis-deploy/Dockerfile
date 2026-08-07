# Verdis Chain Node — Multi-stage Docker Build
# Stage 1: Rust Builder
FROM paritytech/ci-linux:production as builder

WORKDIR /verdis

# Copy workspace
COPY Cargo.toml Cargo.lock ./
COPY node/ ./node/
COPY runtime/ ./runtime/
COPY pallets/ ./pallets/

# Build the node binary (release mode)
RUN cargo build --release -p verdis-node

# Stage 2: Runtime Image
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /verdis

# Copy the compiled binary
COPY --from=builder /verdis/target/release/verdis-node /usr/local/bin/verdis-node

# Copy chain spec
COPY chain-spec.json /verdis/chain-spec.json

# Expose ports: 9944 (RPC+WS), 30333 (P2P)
EXPOSE 9944 30333

# Volume for chain data
VOLUME ["/verdis/data"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -sf http://localhost:9944 -X POST -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":1,"method":"system_health","params":[]}' || exit 1

# Start the node
CMD ["verdis-node", \
  "--chain=verdis", \
  "--base-path=/verdis/data", \
  "--rpc-external", \
  "--ws-external", \
  "--rpc-methods=safe", \
  "--rpc-cors=all", \
  "--port=30333", \
  "--rpc-port=9944", \
  "--no-telemetry", \
  "--validator"]
