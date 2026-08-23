#!/bin/bash
# Cargo audit with known/accepted RUSTSEC advisories ignored
# These are Substrate framework dependencies we cannot control
# New (non-ignored) vulnerabilities WILL fail CI.

cargo audit \
  --ignore RUSTSEC-2026-0118 \
  --ignore RUSTSEC-2026-0119 \
  --ignore RUSTSEC-2025-0009 \
  --ignore RUSTSEC-2025-0010 \
  --ignore RUSTSEC-2026-0098 \
  --ignore RUSTSEC-2026-0099 \
  --ignore RUSTSEC-2026-0104 \
  --ignore RUSTSEC-2025-0055 \
  --ignore RUSTSEC-2026-0186

# Exit with cargo audit's actual exit code
# (0 = no new vulns, 1 = new vulns found)
