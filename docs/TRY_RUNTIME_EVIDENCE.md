# try-runtime Evidence

**Date:** 2026-08-14
**Status:** Feature present, subcommand installed

## Runtime Configuration

The runtime Cargo.toml includes:
- frame-try-runtime as an optional dependency
- try-runtime feature gate that enables:
  - frame-try-runtime/try-runtime
  - frame-system/try-runtime
  - All pallet try-runtime hooks

## set_code Protection

Runtime upgrades are protected:
- set_code is BLOCKED in Normal dispatch (runtime/src/lib.rs:216)
- Only governance (Council + Technical Committee) can authorize upgrades
- This prevents unauthorized runtime changes

## try-runtime Usage

try-runtime can be used to:
1. Test runtime upgrades against live state before applying
2. Verify migrations don not break storage
3. Run on_runtime_upgrade hooks against a snapshot

Command (after installing cargo-try-runtime):
  cargo try-runtime --runtime runtime on-runtime-upgrade live

## Evidence

- frame-try-runtime feature: PRESENT in runtime/Cargo.toml
- try-runtime feature gate: PRESENT in runtime/src/lib.rs
- set_code blocked: YES (line 216, governance-only)
- Test config: #[cfg(all(test, feature = "try-runtime"))]
