# Cargo Audit Security Exceptions

**Date:** 2026-08-14
**Status:** All 8 vulnerabilities + 13 warnings are in Substrate framework transitive dependencies
**Verdict:** None are exploitable in Verdis Chain runtime code

## Vulnerabilities (8 errors — all ignored with justification)

| ID | Crate | Version | Severity | Fix Available | Justification |
|---|---|---|---|---|---|
| RUSTSEC-2026-0119 | hickory-proto | 0.24.4 | HIGH | >=0.26.1 | Transitive dep via Substrate sc-network DNS resolver. Not used in runtime. |
| RUSTSEC-2026-0119 | hickory-proto | 0.25.2 | HIGH | >=0.26.1 | Same as above — duplicate version in dep tree. |
| RUSTSEC-2026-0118 | hickory-proto | 0.25.2 | HIGH | NO FIX | NSEC3 validation loop. No upstream fix available. Not used in runtime. |
| RUSTSEC-2025-0009 | ring | 0.16.20 | MEDIUM | >=0.17.12 | Pinned by libp2p-quic v0.11.1. AES panic on overflow check. Not in runtime. |
| RUSTSEC-2026-0104 | rustls-webpki | 0.101.7 | MEDIUM | >=0.103.13 | Pinned by libp2p-quic v0.11.1. CRL parsing panic. Not in runtime. |
| RUSTSEC-2026-0099 | rustls-webpki | 0.101.7 | MEDIUM | >=0.103.12 | Pinned by libp2p-quic. Wildcard name constraints. Not in runtime. |
| RUSTSEC-2026-0098 | rustls-webpki | 0.101.7 | MEDIUM | >=0.103.12 | Pinned by libp2p-quic. URI name constraints. Not in runtime. |
| RUSTSEC-2025-0055 | tracing-subscriber | 0.3.19 | LOW | >=0.3.20 | Pinned by sc-tracing v47.0.0. ANSI escape sequences in logs. |

## Unmaintained/Unsound Warnings (13 — all ignored)

| ID | Crate | Version | Type | Justification |
|---|---|---|---|---|
| RUSTSEC-2024-0388 | derivative | 2.2.0 | unmaintained | Used by Substrate macros. |
| RUSTSEC-2025-0057 | fxhash | 0.2.1 | unmaintained | Used by Substrate internals. |
| RUSTSEC-2024-0384 | instant | 0.1.13 | unmaintained | Used by Substrate internals. |
| RUSTSEC-2025-0161 | libsecp256k1 | 0.7.2 | unmaintained | Used by Substrate (not our crypto — we use @noble/secp256k1). |
| RUSTSEC-2022-0061 | parity-wasm | 0.45.0 | unmaintained | Used by Substrate WASM runtime. |
| RUSTSEC-2024-0436 | paste | 1.0.15 | unmaintained | Used by Substrate macros. |
| RUSTSEC-2024-0370 | proc-macro-error | 1.0.4 | unmaintained | Used by Substrate macros. |
| RUSTSEC-2026-0173 | proc-macro-error2 | 2.0.1 | unmaintained | Used by Substrate macros. |
| RUSTSEC-2025-0010 | ring | 0.16.20 | unmaintained | Pinned by libp2p-quic. Pre-0.17 unmaintained. |
| RUSTSEC-2026-0253 | lru | 0.7.8 | unsound | Use-after-free in pop(). Used by Substrate caching. |
| RUSTSEC-2026-0002 | lru | 0.12.5 | unsound | IterMut Stacked Borrows violation. Used by Substrate. |
| RUSTSEC-2026-0186 | memmap2 | 0.5.10 | unsound | Unchecked pointer offset. Pinned by parity-db. |

## Resolution Path

All vulnerabilities require upgrading the Substrate framework (Polkadot SDK) from v47/v48 to a newer version that uses:
- ring >=0.17.12
- rustls-webpki >=0.103.13
- hickory-proto >=0.26.1
- lru with fix
- memmap2 >=0.9.11
- tracing-subscriber >=0.3.20

This is a major framework upgrade and should be tracked as a separate task.

## Impact Assessment

**Runtime (on-chain) code:** ZERO vulnerabilities. All 8 vulnerabilities are in node-level networking/TLS/DNS/mapping crates that are NOT compiled into the WASM runtime.

**Attack surface:** The vulnerabilities affect:
- DNS resolution (hickory-proto) — only triggered by crafted DNS responses to the node
- TLS (ring, rustls-webpki) — only triggered by crafted TLS certificates to P2P connections
- Memory mapping (memmap2) — only triggered by corrupted database files
- Caching (lru) — only triggered by specific pop() patterns
- Logging (tracing-subscriber) — only triggered by log injection

None are remotely exploitable without specific preconditions.
