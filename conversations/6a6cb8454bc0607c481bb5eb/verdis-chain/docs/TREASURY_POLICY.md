# VERDIS CHAIN — TREASURY POLICY

**Created:** 2026-08-14
**Updated:** 2026-08-14
**Status:** SPECIFICATION (implementation pending key ceremony)

---

## TREASURY OVERVIEW

| Parameter | Value |
|---|---|
| Allocation | 20,000,000,000 VRDX (20% of 100B supply) |
| Account | PalletId(*b"verdist0") — pallet-controlled |
| Decimals | 9 (20B VRDX = 20,000,000,000,000,000,000 units) |
| Burn rate | 0% (no burn — preserves 100B total supply) |
| Spend period | 600 blocks |

---

## ACCESS CONTROL

### Current (Testnet)

- Treasury spend origin: Council 2/3 majority (`EnsureCouncilSpend`)
- No direct dispatchable spending
- All spending through governance proposals

### Mainnet Target

- **3-of-5 multisignature authorization** (per Rojs Gordons' specification)
- No single signer can independently authorize a Treasury transfer
- 5 signer keys independently generated on air-gapped machine
- Each key stored under separate physical custody
- Treasury spend requires: Council 2/3 approval + 3-of-5 multisig authorization

See `docs/TREASURY_SECURITY_SPEC.md` for full technical specification.

---

## ALLOWED USES

1. Ecosystem grants and developer programs
2. Validator incentives and staking rewards (supplementary)
3. Community initiatives and partnerships
4. Emergency security responses
5. Infrastructure and operational costs

---

## PROHIBITED USES

1. Direct team enrichment (team allocation is separate)
2. Market manipulation or price support
3. Unauthorized loans or lending
4. Any transfer not approved by 3-of-5 multisig (mainnet)

---

## SPEND APPROVAL FLOW (MAINNET)

```
1. Treasury spend proposal submitted
2. Council reviews and approves (2/3 majority)
3. 3-of-5 multisig signers independently review
4. Minimum 3 signers approve (each signs on their own device)
5. Transfer executes on-chain
```

All approvals are transparent and recorded on-chain.
