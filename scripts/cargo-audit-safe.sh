#!/bin/bash
# cargo audit with documented exceptions for Substrate transitive deps
# See docs/SECURITY_EXCEPTIONS.md for full justification
cargo audit \
  --ignore RUSTSEC-2026-0119 \
  --ignore RUSTSEC-2026-0118 \
  --ignore RUSTSEC-2025-0009 \
  --ignore RUSTSEC-2026-0104 \
  --ignore RUSTSEC-2026-0099 \
  --ignore RUSTSEC-2026-0098 \
  --ignore RUSTSEC-2025-0055 \
  --ignore RUSTSEC-2024-0388 \
  --ignore RUSTSEC-2025-0057 \
  --ignore RUSTSEC-2024-0384 \
  --ignore RUSTSEC-2025-0161 \
  --ignore RUSTSEC-2022-0061 \
  --ignore RUSTSEC-2024-0436 \
  --ignore RUSTSEC-2024-0370 \
  --ignore RUSTSEC-2026-0173 \
  --ignore RUSTSEC-2025-0010 \
  --ignore RUSTSEC-2026-0253 \
  --ignore RUSTSEC-2026-0002 \
  --ignore RUSTSEC-2026-0186
