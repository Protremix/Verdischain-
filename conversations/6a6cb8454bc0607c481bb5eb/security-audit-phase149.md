# Verdis Chain Security Audit — Phase 149
**Date:** August 8, 2026
**Auditor:** EvolvixOS Automated Security Scanner
**Scope:** Full codebase (pallets, runtime, node, web, nginx, Docker, SSH)

## Overall Score: 88/100

---

## Findings by Severity

### CRITICAL (0)
None found.

### HIGH (1) — FIXED ✅

**H1: dpos::update_green_score self-scoring vulnerability**
- **File:** `pallets/dpos/src/lib.rs:575`
- **Description:** The `update_green_score` extrinsic in the DPoS pallet used `ensure_signed(origin)`, allowing ANY validator to set their OWN green score to any value (0-255). This undermines the entire green validator scoring system — validators could self-assign maximum scores to earn higher rewards without actually being eco-friendly.
- **Remediation:** Changed signature to `(origin, validator: T::AccountId, score: u8)` and switched to `ensure_root(origin)`. Now only root (governance) can update green scores, matching the eco pallet's implementation.
- **Status:** Fixed. All 16 dpos tests pass with new signature.

### MEDIUM (3)

**M1: Dependency vulnerabilities (cargo audit)**
- **Crate:** hickory-proto 0.24.4/0.25.2 — RUSTSEC-2026-0119 (CPU exhaustion), RUSTSEC-2026-0118 (NSEC3 unbounded loop)
- **Crate:** ring 0.16.20 — RUSTSEC-2025-0009 (AES panic)
- **Crate:** rustls-webpki 0.101.7 — CRL parsing panic
- **Description:** Transitive Substrate dependencies with known vulnerabilities.
- **Remediation:** These require a Substrate framework upgrade. Monitor for upstream patches.
- **Status:** Accepted risk (Substrate-managed dependencies).

**M2: Unbounded Vec<u8> in storage parameters**
- **Files:** `pallets/amm-dex/src/lib.rs`, `pallets/dpos/src/lib.rs`, `pallets/eco/src/lib.rs`
- **Description:** Several extrinsics accept unbounded `Vec<u8>` parameters (token identifiers, project names, locations, reason strings). An attacker could submit very large vectors to bloat storage.
- **Remediation:** Replace `Vec<u8>` with `BoundedVec<u8, T::MaxLen>` in future refactor. Current impact is limited by extrinsic weight and fee mechanisms.
- **Status:** Logged for future hardening.

**M3: Integer overflow risk in type casts**
- **Files:** `pallets/dpos/src/lib.rs`, `pallets/address-lookup-tables/src/lib.rs`
- **Description:** Several `as u32` and `as u64` casts that could theoretically overflow on extremely large values (e.g., validator count > u32::MAX).
- **Remediation:** Use `try_into()` or `TryFrom` for safe conversions. Most are bounded by config parameters, so practical risk is low.
- **Status:** Logged for future hardening.

### LOW (1)

**L1: Missing Docker container security hardening**
- **File:** `docker-compose.yml`
- **Description:** Docker containers not configured with `user`, `readonly`, `cap_drop`, or `no-new-privileges`.
- **Remediation:** Add `security_opt: ["no-new-privileges:true"]` and `read_only: true` to container definitions.
- **Status:** Logged for future hardening.

---

## Passed Checks ✅

1. **No hardcoded secrets** — Scanned all Rust source, TOML, and web files. Zero API keys, passwords, or private keys found.
2. **Origin checks on sensitive extrinsics:**
   - `eco::mint_carbon_credit` → `ensure_root` ✅
   - `eco::create_reforest_project` → `ensure_root` ✅
   - `eco::update_green_score` → `ensure_root` ✅
   - `eco::verify_carbon_credit` → `ensure_root` ✅
   - `eco::verify_reforest_project` → `ensure_root` ✅
   - `dpos::register_validator` → `ensure_signed` ✅
   - `dpos::unregister_validator` → `ensure_signed` ✅
   - `dpos::vote` → `ensure_signed` ✅
   - `dpos::slash_validator` → `ensure_root` ✅
   - `dpos::update_green_score` → `ensure_root` ✅ (FIXED)
   - `amm-dex::create_pool` → `ensure_signed` ✅
   - `amm-dex::add_liquidity` → `ensure_signed` ✅
   - `amm-dex::swap` → `ensure_signed` ✅
   - `amm-dex::remove_liquidity` → `ensure_signed` ✅
3. **SSH hardening** — PasswordAuthentication: no, PermitRootLogin: prohibit-password, key-only auth ✅
4. **Nginx security headers** — X-Frame-Options, X-Content-Type-Options, HSTS, X-XSS-Protection, CSP all present ✅ (HSTS, XSS, CSP added in this audit)
5. **RPC ports** — All bound to localhost (not exposed externally) ✅
6. **No self-scoring** — Both eco and dpos green score updates now require root ✅ (FIXED)
7. **No XSS vectors** — Web files use proper input sanitization, no inline event handlers on user input ✅

---

## Summary

| Severity | Count | Fixed | Accepted |
|----------|-------|-------|----------|
| Critical | 0 | 0 | 0 |
| High | 1 | 1 | 0 |
| Medium | 3 | 0 | 3 |
| Low | 1 | 0 | 1 |
| **Total** | **5** | **1** | **4** |

**Previous audit (Phase 130):** 72/100 → **This audit:** 88/100 (+16 points)

Key improvement: Fixed the dpos self-scoring vulnerability that was missed in Phase 145. Added HSTS, CSP, and X-XSS-Protection headers. All sensitive extrinsics now properly require root or signed origins.
