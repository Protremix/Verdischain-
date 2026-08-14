# Protremix Stake Policy (ARCH-020)

**Status:** Draft — requires approval from governance

---

## 1. Principle

Protremix (the commercial development company) and the Verdis Foundation must not hold majority stake in the network. This prevents company/foundation control of consensus.

## 2. Targets

| Metric | Mainnet Launch | 6 Months | 12 Months |
|--------|---------------|---------|-----------|
| Protremix + Foundation combined stake | <= 33% | <= 25% | <= 20% |
| Protremix-controlled validators | <= 7 of 21 | <= 10 of 50 | <= 15 of 100 |
| Foundation-controlled validators | <= 2 of 21 | <= 3 of 50 | <= 5 of 100 |

## 3. Measurement

- Stake is measured as on-chain VRDX staked to validators controlled by Protremix or Foundation entities
- "Controlled" means Protremix/Foundation operates the validator node or holds the session keys
- Measurement is via on-chain stake data (dpos_allValidators + dpos_validatorStake RPC)
- Nakamoto coefficient (minimum entities to disrupt consensus) must be >= 7 at mainnet

## 4. Enforcement

- No automatic on-chain enforcement (not possible without protocol changes)
- Self-enforced via internal policy
- Publicly auditable via on-chain data
- Reported on the status page (ARCH-062)

## 5. Sunset Clause

This policy remains in effect until:
- 100+ independent validators are active
- Nakamoto coefficient >= 21
- Top-10 stake concentration < 33%

At which point the policy is reviewed by governance.
