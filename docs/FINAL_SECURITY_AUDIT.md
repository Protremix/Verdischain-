# Verdis Chain — Final Security Audit & Mainnet Readiness Assessment

> **Audit Date:** 2026-08-17  
> **Release Candidate:** Commit `51cdb5e3346f2f26c843096c44f678e716fd5d1c`  
> **Runtime:** v2.0.0 (spec_version 14)  
> **Node:** verdis-node 2.0.0  
> **Auditors:** Arlo (AI) + 10 parallel sub-agent audits  
> **Methodology:** Full source code review via SSH, 16 pallets, runtime, chain specs, RPC, P2P, genesis  

---

## EXECUTIVE SUMMARY

**VERDICT: 🔴 NOT MAINNET-READY — 8 CRITICAL, 16 HIGH, 30+ MEDIUM findings**

The Verdis Chain codebase has a solid Substrate foundation with good arithmetic safety and a well-structured DEX for native tokens. However, there are **8 release-blocking CRITICAL issues** and **16 HIGH severity findings** that must be resolved before mainnet launch.

The most severe issues are:
1. Dev keyrings (Alice-Ferdie) with publicly known private keys in the mainnet chain spec
2. Sudo pallet with Alice's key in the mainnet chain spec — anyone can seize the chain
3. Equivocation reporting completely broken — no slashing for double-signing
4. IBC pallet has no authentication — anyone can permanently lock bridge funds
5. No minimum validator count enforced — chain can run with 1 validator
6. No downtime detection — offline validators keep their slots indefinitely
7. RPC exposes unsafe methods on 0.0.0.0 with predictable node keys
8. ZK compression verify_proof always returns true — rubber-stamp verification

---

## FINDING SUMMARY TABLE

| # | Sev | Area | Finding | File |
|---|-----|------|---------|------|
| C1 | CRITICAL | Genesis | Dev keyrings (Alice-Ferdie) in mainnet chain spec | chain-specs/mainnet-raw.json |
| C2 | CRITICAL | Genesis | Sudo pallet with Alice key in mainnet spec | chain-specs/mainnet-plain.json |
| C3 | CRITICAL | Consensus | Equivocation reporting broken (generate_key_ownership_proof returns None) | runtime/src/lib.rs:1715,1734 |
| C4 | CRITICAL | Consensus | No minimum validator count enforced | runtime/src/lib.rs:585 |
| C5 | CRITICAL | Consensus | No downtime/inactive validator detection | pallets/dpos/src/lib.rs:690 |
| C6 | CRITICAL | IBC | acknowledge_packet has no auth — permanent token locking | pallets/ibc/src/lib.rs:432-448 |
| C7 | CRITICAL | IBC | recv_packet is a no-op — incoming transfers never credited | pallets/ibc/src/lib.rs:401 |
| C8 | CRITICAL | RPC | Unsafe RPC exposed on 0.0.0.0 (author_rotateKeys accessible) | nodes 4/5/6 config |
| H1 | HIGH | DPoS | Green score manipulation (user-supplied, no bounds) | pallets/dpos/src/lib.rs:register_validator |
| H2 | HIGH | DPoS | Reactivation cooldown bypassed (LastSlashedBlock not written) | pallets/dpos/src/lib.rs:654-715 |
| H3 | HIGH | DPoS | Slashing breaks VoteRecord.amount accounting | pallets/dpos/src/lib.rs:884-906 |
| H4 | HIGH | DPoS | TotalStaked double-reduced after slash | pallets/dpos/src/lib.rs:835-906 |
| H5 | HIGH | DEX | add_liquidity missing min_lp_minted (sandwich attack) | pallets/amm-dex/src/lib.rs:467 |
| H6 | HIGH | DEX | add_token_liquidity missing min_lp_minted + no deadline | pallets/amm-dex/src/lib.rs:870 |
| H7 | HIGH | Cross-Module | Presale↔Vesting: vesting not cleaned on refund (future funds frozen) | pallets/presale/src/lib.rs:713-773 |
| H8 | HIGH | IBC | acknowledge_packet doesn't release escrow | pallets/ibc/src/lib.rs:445 |
| H9 | HIGH | RPC | All 6 nodes use predictable node keys (0001-0006) | node service configs |
| H10 | HIGH | RPC | Nodes run as root — RPC vuln = root server access | systemd service files |
| H11 | HIGH | RPC | WebSocket bypasses RPC method filtering | nginx config |
| H12 | HIGH | Genesis | Dev keyrings in testnet-canonical spec | chain-specs/testnet-canonical-raw.json |
| H13 | HIGH | Runtime | Malicious runtime can permanently brick network | systemic |
| H14 | HIGH | ZK | verify_proof always returns true (rubber-stamp) | pallets/zk-compression/src/lib.rs:86-100 |
| H15 | HIGH | ZK | create_tree generates fake Merkle root | pallets/zk-compression/src/lib.rs:74-82 |
| H16 | HIGH | Gulf Stream | ForwardedTxs unbounded growth (storage DoS) | pallets/gulf-stream/src/lib.rs:89-90,161 |

---

## DETAILED FINDINGS

### C1 — CRITICAL: Dev Keyrings in Mainnet Chain Spec
**File:** chain-specs/mainnet-raw.json, chain-specs/mainnet-plain.json  
**Impact:** All 6 well-known Substrate dev accounts (Alice-Ferdie) appear as validators, council members, and session key holders in the stored mainnet chain spec. Their private keys are publicly known across the entire Substrate ecosystem.  
**Attack:** Anyone can impersonate validators, vote on governance, and control the council.  
**Fix:** Regenerate chain-specs/mainnet-raw.json from current code (which correctly uses //MAINNET_VALIDATOR_N placeholders). Verify zero dev keyring hex patterns in regenerated files.  

### C2 — CRITICAL: Sudo Pallet with Alice Key in Mainnet Spec
**File:** chain-specs/mainnet-plain.json → patch.sudo  
**Impact:** The stored mainnet spec includes sudo configuration setting Alice as root key. Alice's private key is publicly known.  
**Attack:** Anyone can call sudo(set_code_without_checks(malicious_wasm)) to instantly upgrade the runtime with zero delay — full chain takeover.  
**Fix:** Regenerate mainnet spec from current codebase (pallet_sudo removed from runtime). Verify no sudo section exists.  

### C3 — CRITICAL: Equivocation Reporting Broken
**File:** runtime/src/lib.rs:1715, 1734  
**Impact:** Both BabeApi::generate_key_ownership_proof and GrandpaApi::generate_key_ownership_proof return None. Without key-ownership proofs, no equivocation reports can be submitted. Automated BABE/GRANDPA slashing is dead.  
**Attack:** A validator can double-sign or double-vote with zero economic penalty.  
**Fix:** Implement generate_key_ownership_proof to return actual ownership proofs for registered validators.  

### C4 — CRITICAL: No Minimum Validator Count
**File:** runtime/src/lib.rs:585 (MinimumValidatorCount=4 declared but never used)  
**Impact:** new_session returns whatever active validators exist, even a single one. The chain can operate with 1 validator.  
**Fix:** Enforce MinimumValidatorCount in new_session — return None (halt) if below threshold.  

### C5 — CRITICAL: No Downtime Detection
**File:** pallets/dpos/src/lib.rs:690 (on_initialize is empty)  
**Impact:** Offline validators keep their active-set membership indefinitely. No missed-block tracking, no auto-removal, no chill.  
**Fix:** Implement on_initialize with missed-block tracking and automatic deactivation after threshold.  

### C6 — CRITICAL: IBC acknowledge_packet Has No Authentication
**File:** pallets/ibc/src/lib.rs:432-448  
**Impact:** Any signed account can call acknowledge_packet for any IBC packet, removing it from storage. The original sender cannot call timeout_packet (returns PacketNotFound). Escrowed tokens are permanently locked.  
**Attack:** Alice transfers 10,000 VRDX cross-chain → Mallory calls acknowledge_packet → tokens locked forever.  
**Fix:** Add relayer authorization. Verify acknowledgement proof from destination chain.  

### C7 — CRITICAL: IBC recv_packet Is a No-Op
**File:** pallets/ibc/src/lib.rs:401  
**Impact:** recv_packet only increments a sequence counter and emits an event. No tokens are minted/credited to recipients. IBC token transfers are fundamentally non-functional.  
**Fix:** Implement recv_packet to parse packet data and mint/credit tokens to recipients.  

### C8 — CRITICAL: Unsafe RPC Exposed
**File:** Node service configs (nodes 4/5/6)  
**Impact:** Nodes 4/5/6 expose unsafe RPC methods on 0.0.0.0. author_rotateKeys confirmed working remotely. Currently firewalled by UFW but any misconfiguration = total compromise.  
**Fix:** Bind RPC to localhost only. Remove --unsafe-rpc-external and --rpc-methods=unsafe flags.  

### H1 — HIGH: Green Score Manipulation
**File:** pallets/dpos/src/lib.rs:register_validator  
**Impact:** register_validator accepts green_score from user with no bounds check. A validator can set green_score=255 for 26.5x voting weight boost.  
**Fix:** Set green_score via ensure_root or validated oracle, not user-supplied. Add bounds check (0-10 range).  

### H2 — HIGH: Reactivation Cooldown Bypassed
**File:** pallets/dpos/src/lib.rs:654-715  
**Impact:** slash_validator (governance path) never writes LastSlashedBlock. Only do_slash writes it. After governance slash, cooldown is measured from block 0 → zero cooldown.  
**Fix:** Write LastSlashedBlock in slash_validator.  

### H3 — HIGH: Slashing Breaks VoteRecord Accounting
**File:** pallets/dpos/src/lib.rs:884-906  
**Impact:** do_slash slashes delegators' reserved funds but never updates VoteRecord.amount in storage. Stored amounts become stale and higher than actual reserved balances.  
**Fix:** Update VoteRecord.amount for each delegator during do_slash.  

### H4 — HIGH: TotalStaked Double-Reduced
**File:** pallets/dpos/src/lib.rs:835-906  
**Impact:** do_slash reduces TotalStaked for each delegator's slash AND for the validator's slash, but only reduces total_votes by the validator portion. TotalStaked ≠ sum(total_votes) permanently after any slash.  
**Fix:** Fix accounting to reduce TotalStaked exactly once per unit slashed.  

### H5-H6 — HIGH: DEX Missing Slippage Protection
**File:** pallets/amm-dex/src/lib.rs:467, 870  
**Impact:** add_liquidity and add_token_liquidity have no min_lp_minted parameter. Sandwich attackers can front-run LP deposits. add_token_liquidity also has no deadline.  
**Fix:** Add min_lp_minted parameter to both functions. Add deadline to add_token_liquidity.  

### H7 — HIGH: Vesting Not Cleaned Up on Presale Refund
**File:** pallets/presale/src/lib.rs:713-773  
**Impact:** When users claim presale refunds, vesting schedules are never removed. All future incoming funds are frozen for the vesting duration.  
**Fix:** Add vesting cleanup to claim_refund. Add remove_vesting function to vesting pallet.  

### H8 — HIGH: IBC acknowledge_packet Doesn't Release Escrow
**File:** pallets/ibc/src/lib.rs:445  
**Impact:** acknowledge_packet removes packet from storage but doesn't handle escrowed tokens. Combined with C6, escrow is permanent if anyone calls acknowledge prematurely.  
**Fix:** Complete the IBC lifecycle — release escrow on proper acknowledgement, refund on timeout.  

### H9-H11 — HIGH: RPC/P2P Security Issues
**Files:** Node service configs, nginx config  
**Impact:** Predictable node keys (0001-0006) enable impersonation. Nodes run as root. WebSocket bypasses RPC filter.  
**Fix:** Generate random node keys. Run nodes as non-root user. Add WS filtering to nginx.  

### H12 — HIGH: Dev Keyrings in Testnet Spec
**File:** chain-specs/testnet-canonical-raw.json  
**Impact:** All 6 dev keyrings as validators, council, and tech committee on testnet. Anyone can control governance and fast-track upgrades.  
**Fix:** Replace with randomly generated test keys for public testnet.  

### H13 — HIGH: Malicious Runtime Can Brick Network
**Impact:** If root is compromised, set_code_without_checks uploads malicious WASM with no validation. No on-chain recovery mechanism.  
**Fix:** Add time-lock for upgrades. Disable InstantAllowed or raise threshold.  

### H14 — HIGH: ZK verify_proof Always Returns True
**File:** pallets/zk-compression/src/lib.rs:86-100  
**Impact:** verify_proof unconditionally returns verified:true. No actual ZK proof verification. If any pallet trusts ProofVerified events, it's a trust boundary violation.  
**Fix:** Implement actual ZK proof verification or remove the pallet.  

### H15 — HIGH: ZK create_tree Generates Fake Merkle Root
**File:** pallets/zk-compression/src/lib.rs:74-82  
**Impact:** Merkle root is just blake2_256(who.encode()) — not a real Merkle root. Deterministic per-account.  
**Fix:** Implement actual Merkle tree construction or remove.  

### H16 — HIGH: Gulf Stream Unbounded Storage Growth
**File:** pallets/gulf-stream/src/lib.rs:89-90, 161  
**Impact:** ForwardedTxs Vec grows without bound. Permissionless forward_transaction enables storage DoS.  
**Fix:** Enforce MaxPendingForwards. Add pruning. Restrict to active validators only.  

---

## MEDIUM FINDINGS (30+)

### DPoS
- Commission is dead code — validators keep 100% of rewards, delegators get nothing
- Unvoted delegators can front-run slashes by calling unvote
- No delegator reward distribution exists — undermines DPoS economic model
- refill_reward_pool says "governance only" but uses ensure_signed

### Vesting
- Block-number-based with hardcoded 5s assumption — validators can manipulate cadence
- Genesis doesn't validate schedule params — vesting_days=0 causes div-by-zero panic (DoS)

### Presale
- Refunds broken for all vested rounds
- Unsold VRDX stranded in escrow forever (no sweep)
- Deactivation = cancel (pause and cancel share one bit)

### DEX (Token path)
- swap_token CEI violation (transfers before state update)
- remove_token_liquidity CEI violation
- create_pool missing MinimumLiquidity lock
- Token functions lack deadline parameters
- swap_token missing k-invariant check
- Token functions significantly less hardened than native functions

### Arithmetic
- dpos:961 raw epoch increment (potential overflow)
- sealevel:140 raw multiplication in running average
- amm-dex fee denominator not zero-validated at genesis

### Cross-Module
- Delegator VoteRecords not updated after slash (TotalStaked drifts)
- Hardcoded 5% slash ignores governance-configured fraction
- set_storage not blocked by call filter (arbitrary storage manipulation)
- release_distribution updates supply counter without token transfer

### RPC/P2P
- All bootnodes on single server (SPOF)
- --rpc-cors all
- No --no-private-ipv4
- CORS wildcard on RPC
- 400 max peers (excessive)

### Runtime Upgrade
- set_code_without_checks/set_storage/kill_storage not blocked by call filter
- InstantAllowed=true with Council 1/1 = zero-delay upgrade if council compromised
- Circuit Breaker only covers 8 pallets (missing 16+)
- Circuit Breaker root-only with no timelock

### Parallel Execution Pallets (Solana-inspired)
- 6 of 7 pallets are scaffolding/statistics only — not functional
- Gulf Stream: forward_transaction permissionless, timestamp hardcoded to 0
- Turbine: register_shard permissionless, no validation
- Sealevel: all extrinsics permissionless, has_conflicts caller-supplied
- ZK: compress_account doesn't compress, create_tree permissionless
- Storage: register_provider permissionless with no deposit, verify_storage permissionless
- Address Lookup Tables: don't store actual addresses

---

## TOKEN SUPPLY MODEL

**100B VRDX cap is enforced by convention (genesis-only pre-mint), NOT by runtime code.**

- All 100B pre-minted at genesis to PalletId-controlled pools ✅
- No active mint path for native VRDX ✅ (inflation and block rewards are dead code)
- No burn path for native VRDX (TreasuryBurn = 0%) ✅
- All post-genesis token movement is transfers, not minting ✅
- BUT: no runtime-level supply guard — a future runtime upgrade adding mint_into could exceed 100B with no rejection ⚠️
- Staking rewards (if activated) come from pre-funded 20B pool, not minting ✅
- Treasury cannot spend beyond balance (PayFromAccount enforces) ✅

---

## POSITIVE FINDINGS

- **Arithmetic safety**: DPoS, AMM-DEX, and vesting pallets predominantly use checked/saturating arithmetic ✅
- **DEX native path**: swap function well-hardened — k-invariant, slippage, deadline, CEI, circuit breaker ✅
- **remove_liquidity**: Clean CEI, division-by-zero protection, proportional withdrawal ✅
- **Token supply**: All pre-minted at genesis, no inflation in production ✅
- **Treasury**: Cannot overspend, Council 2/3 or 3-of-5 multisig, max 1B per proposal ✅
- **Transaction validation**: Standard Substrate validation (nonce, spec version, genesis, mortality, weight, fees) ✅
- **Failed extrinsics**: Atomic rollback guaranteed by Substrate FRAME ✅
- **Deterministic execution**: No non-deterministic primitives found ✅
- **Circuit Breaker**: Fully functional and wired into CallFilter with recursive Utility/Scheduler checks ✅

---

## MAINNET READINESS ASSESSMENT

| Category | Status | Blockers |
|----------|--------|----------|
| Consensus | 🔴 FAIL | C3 (equivocation), C4 (min validators), C5 (downtime) |
| Genesis/Privileged | 🔴 FAIL | C1 (dev keys), C2 (sudo) |
| IBC/Bridge | 🔴 FAIL | C6 (no auth), C7 (no-op), H8 (escrow) |
| DPoS/Staking | 🔴 FAIL | H1-H4 (accounting, green score, cooldown) |
| DEX | 🟡 PARTIAL | H5-H6 (slippage), token path less hardened |
| RPC/P2P | 🔴 FAIL | C8 (unsafe RPC), H9-H11 (keys, root, WS) |
| Token Supply | 🟢 PASS | No active mint, all pre-minted |
| Arithmetic | 🟢 PASS | Generally well-guarded |
| Presale/Vesting | 🟡 PARTIAL | H7 (vesting cleanup), vesting_days=0 panic |
| Runtime Upgrade | 🟡 PARTIAL | set_storage unblocked, InstantAllowed |
| Parallel Execution | 🟡 INFO | 6/7 pallets are scaffolding (not blocking) |
| ZK Compression | 🔴 FAIL | H14-H15 (rubber-stamp, fake roots) |

**Overall: 🔴 NOT MAINNET-READY**

---

## REMEDIATION PRIORITY

### P0 — Must fix before mainnet (blocking):
1. Regenerate mainnet chain spec — remove dev keys and sudo (C1, C2)
2. Implement equivocation reporting (C3)
3. Enforce minimum validator count (C4)
4. Implement downtime detection (C5)
5. Fix IBC authentication — add relayer auth, complete recv_packet (C6, C7, H8)
6. Secure RPC — bind to localhost, remove unsafe flags, random node keys (C8, H9-H11)
7. Fix DPoS accounting — VoteRecord, TotalStaked, LastSlashedBlock (H2-H4)
8. Bound green_score at registration (H1)
9. Add min_lp_minted to DEX liquidity functions (H5-H6)
10. Fix vesting cleanup on presale refund (H7)
11. Remove or properly implement ZK compression (H14-H15)
12. Fix Gulf Stream unbounded storage (H16)

### P1 — Should fix before mainnet:
13. Block set_storage/kill_storage in call filter
14. Disable InstantAllowed or raise threshold
15. Expand Circuit Breaker coverage to all pallets
16. Add timelock to Circuit Breaker
17. Backport DEX security features from native to token path
18. Add genesis validation for vesting params (vesting_days > 0)
19. Replace testnet dev keys with random test keys
20. Run nodes as non-root user

### P2 — Post-mainnet improvements:
21. Implement actual block reward distribution (currently dead code)
22. Implement delegator reward distribution
23. Remove or properly implement Solana-inspired pallets (6/7 are scaffolding)
24. Add runtime-level supply cap guard
25. Add protocol fee routing from DEX to Treasury

---

## REPRODUCTION

```bash
# Verify release candidate
cd /opt/verdis-chain-rust
git rev-parse HEAD  # Should be 51cdb5e3346f2f26c843096c44f678e716fd5d1c

# Check for dev keys in mainnet spec
grep -c "d43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d" chain-specs/mainnet-raw.json  # Should be 0

# Check for sudo in mainnet spec
python3 -c "import json; d=json.load(open('chain-specs/mainnet-plain.json')); print(d.get('genesis',{}).get('runtimeGenesis',{}).get('patch',{}).get('sudo','NOT FOUND'))"

# Check equivocation reporting
grep -n "generate_key_ownership_proof" runtime/src/lib.rs  # Should NOT return None

# Check minimum validator count enforcement
grep -n "MinimumValidatorCount" pallets/dpos/src/lib.rs runtime/src/lib.rs

# Check IBC authentication
grep -n "ensure_signed\|ensure_root" pallets/ibc/src/lib.rs | head -10

# Check node keys
systemctl cat verdis-node.service | grep node-key  # Should NOT be 0000...0001
```

---

**Audit completed by Arlo (AI representative of Verdis Chain) + 10 parallel sub-agent audits.**  
**All findings verified against actual source code at commit 51cdb5e.**  
**No findings marked as fixed without verifying the actual code path.**
