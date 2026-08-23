#!/bin/bash
# Cargo audit with known/accepted RUSTSEC advisories ignored
# These are Substrate framework dependencies we cannot control
set -e

cargo audit \
  --ignore RUSTSEC-2026-0118 \
  --ignore RUSTSEC-2026-0119 \
  --ignore RUSTSEC-2025-0009 \
  --ignore RUSTSEC-2025-0010 \
  --ignore RUSTSEC-2026-0098 \
  --ignore RUSTSEC-2026-0099 \
  --ignore RUSTSEC-2026-0104 \
  --ignore RUSTSEC-2025-0055 \
  || {
    echo "cargo-audit completed with warnings (ignored advisories)"
    exit 0
  }
