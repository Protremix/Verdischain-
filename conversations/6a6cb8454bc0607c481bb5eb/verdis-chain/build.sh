#!/bin/bash
set -e
source /root/.cargo/env
cd /opt/verdis-chain-rust

echo 'Building Verdis Chain (Rust + Substrate)...'
echo 'Note: Using --import-undefined for WASM linker compatibility'

# Clean WASM build artifacts for fresh build
rm -rf target/release/wbuild

# Build with WASM_BUILD_RUSTFLAGS including --import-undefined
WASM_BUILD_RUSTFLAGS="-C link-arg=--import-undefined" cargo build --release --bin verdis

# Run tests
echo 'Running tests...'
cargo test --release --workspace --lib 2>&1 | grep 'test result'

echo 'Build complete!'
