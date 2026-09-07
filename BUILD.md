# Building Verdis Chain

Verified on Ubuntu 22.04 and 26.04, `rustc 1.98.0`, commit `f7fc4e2`.

A clean clone fails without the native dependencies below. This is the exact list —
each entry is here because its absence produces a real, observed build failure.

## 1. Native dependencies

```bash
apt-get update
apt-get install -y \
    clang libclang-dev \
    protobuf-compiler \
    pkg-config libssl-dev \
    build-essential git curl
```

Why each one:

- **clang / libclang-dev** — `rocksdb` uses bindgen. Without it the build dies with
  `couldn't find any valid shared libraries matching libclang.so`, which does not name
  the missing package and is the single most common first-build failure.
- **protobuf-compiler** — required by the networking crates.
- **pkg-config / libssl-dev** — TLS for the RPC and telemetry layers.

If clang is installed but not found, point the build at it explicitly (adjust the LLVM
version to what is installed):

```bash
export LIBCLANG_PATH=/usr/lib/llvm-21/lib
export LLVM_CONFIG_PATH=/usr/lib/llvm-21/bin/llvm-config
export PROTOC=/usr/bin/protoc
```

## 2. Rust toolchain

The toolchain is pinned in `rust-toolchain.toml`, so `rustup` selects it automatically:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
cd verdis-chain
rustc --version        # must print 1.98.0
```

Do not override the channel. A different rustc produces a different WASM blob, and the
runtime hash is what an auditor and every validator compare.

## 3. Build

```bash
cargo build --release              # node binary -> target/release/verdis
cargo test  --workspace            # 734 tests
```

Expected: **734 passed, 0 failed.**

If a pallet's tests fail to *compile* with `error[E0046]: not all trait items
implemented, missing: AdminOrigin`, a `Config` trait gained an associated type and the
`impl Config for Test` block in that pallet's `mock.rs`/`tests.rs` was not updated.
Add `type AdminOrigin = EnsureRoot<AccountId32>;` to match the other pallets. This
condition silently prevented six crates from running any tests at all, while the
project still looked green — always run the suite from a **clean clone**, never from a
long-lived working copy.

## 4. Lints

Keep lints separate from tests, so a lint failure and a test failure stay
distinguishable:

```bash
cargo clippy --workspace --all-targets
```

Do **not** set `RUSTFLAGS="-D warnings"` for the test run — it turns upstream dependency
warnings into build failures and tells you nothing about this codebase.

## 5. Long builds on validator hosts

Several hosts carry live mainnet authorities. A full build will starve them and can cost
finality. Always constrain the build and run it detached from the SSH connection
(`nohup ... &` inside `ssh -c` dies with the connection):

```bash
systemd-run --unit=verdis-build --collect \
  --property=WorkingDirectory=/root/verdis-chain \
  --property=Nice=15 --property=CPUQuota=1000% \
  --property=StandardOutput=append:/root/build.log \
  --setenv=LIBCLANG_PATH=/usr/lib/llvm-21/lib \
  /root/.cargo/bin/cargo build --release
```

Verify the host's validator count is unchanged before and after.

## 6. Runtime facts

```
chain      Verdis Mainnet
genesis    0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e
runtime    verdis-chain, specVersion 16, transactionVersion 3
token      VRDX, 9 decimals, ss58Format 909
pallets    36 in construct_runtime!
consensus  BABE + GRANDPA, 21 authorities, threshold 15
```
