# Multi-Stage Dockerfile for Verdis Chain Node v2.0.0
FROM rust:1.75-slim-bookworm as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    clang \
    libclang-dev \
    llvm \
    pkg-config \
    libssl-dev \
    protobuf-compiler \
    make \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Add WASM compilation target
RUN rustup target add wasm32-unknown-unknown

WORKDIR /build

# Copy source files
COPY Cargo.toml Cargo.lock ./
COPY node ./node
COPY runtime ./runtime
COPY pallets ./pallets

# Build release binary
ENV RUSTFLAGS="-C link-arg=--allow-undefined"
ENV WASM_BUILD_TOOLCHAIN="stable"
RUN cargo build --release

# Production Runtime Stage
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 -s /bin/bash verdis

WORKDIR /home/verdis

COPY --from=builder /build/target/release/verdis /usr/local/bin/verdis

USER verdis

EXPOSE 9944 9933 30333 9615

ENTRYPOINT ["verdis"]
CMD ["--rpc-cors=all"]
