# Verdis Chain Testnet Known Limitations

**Last Updated:** 2026-08-14 15:07 UTC

## Critical Limitations (Block Mainnet)

### 1. Dev/Test Keys in Use
- **Description:** Well-known Substrate development keys (Alice, Bob, Charlie, Dave, Eve, Ferdie) are used as validators.
- **Impact:** Not secure for production. Anyone knows these private keys.
- **Mitigation:** Air-gapped key ceremony required to generate production keys.
- **Status:** BLOCKER for mainnet

### 2. Treasury Multisig Not Implemented
- **Description:** Treasury uses a PalletId placeholder (`verdistm`) instead of the specified 3-of-5 multisig.
- **Impact:** Treasury spending is controlled by Council (2/3 majority), not the designed 3-of-5 cold storage multisig.
- **Mitigation:** Implement multisig pallet integration after key ceremony.
- **Status:** BLOCKER for mainnet

### 3. No Independent Security Audit
- **Description:** Only internal AI audits (Claude + GPT-4o) have been performed. No independent third-party audit.
- **Impact:** Unknown vulnerabilities may exist.
- **Mitigation:** Engage professional security audit firm before mainnet.
- **Status:** BLOCKER for mainnet

### 4. 14-Day Soak Test Not Completed
- **Description:** Chain was restarted on 2026-08-14. No continuous 14-day operation has been demonstrated.
- **Impact:** Long-term stability is unproven.
- **Mitigation:** Run soak test for minimum 14 days with monitoring.
- **Status:** BLOCKER for mainnet

### 5. Smart Contract E2E Flow Unverified
- **Description:** The Sealevel smart contract pallet exists with tests, but the complete flow (upload → instantiate → call → state change) has not been verified on testnet.
- **Impact:** Smart contracts advertised as a feature may not work.
- **Mitigation:** Deploy and test a sample contract on testnet.
- **Status:** BLOCKER for mainnet

## Non-Critical Limitations

### 6. Only 3 of 6 Validators Active
- **Description:** Only 3 validators (Alice, Bob, Charlie) are active with running nodes. The other 3 (Dave, Eve, Ferdie) are registered but have no running nodes.
- **Impact:** Lower decentralization. GRANDPA finality requires all 3 active nodes.
- **Mitigation:** Start additional validator nodes or reduce registered validator count.
- **Status:** Acceptable for testnet

### 7. Weights Are Placeholders
- **Description:** Pallet weights are not based on actual benchmarks. They use default/placeholder values.
- **Impact:** Transaction costs and block capacity may be inaccurate.
- **Mitigation:** Run benchmarks for each pallet and update weights.
- **Status:** Non-blocking for testnet, required for mainnet

### 8. No Chaos Testing
- **Description:** No chaos tests (network partition, random crashes, RPC overload) have been performed.
- **Impact:** Network resilience under adverse conditions is unproven.
- **Mitigation:** Perform chaos tests on dedicated environment.
- **Status:** Non-blocking for testnet, required for mainnet

### 9. No Try-Runtime Tests
- **Description:** While a try-runtime CI workflow exists, no actual try-runtime tests have been run.
- **Impact:** Runtime upgrade safety is unproven.
- **Mitigation:** Run try-runtime tests before any runtime upgrade.
- **Status:** Non-blocking for testnet, required for mainnet

### 10. Explorer Has Mock Data Reference
- **Description:** One file in the explorer contains a reference to "mock/fake/dummy" data.
- **Impact:** May display non-live data in some edge cases.
- **Mitigation:** Audit and remove any mock data references.
- **Status:** Low priority
