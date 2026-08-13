# Kimi Security Audit - Attack Vector Analysis
## Date: August 13, 2026

## DPoS Pallet Findings

### CRITICAL
- **C1**: Double-spend of voting stake - vote + delegate with same tokens, no unified lock
- **C2**: unregister_validator evades slashing - no unbonding/era delay before slash applies

### HIGH
- **H1**: Sybil takeover of 21-slot active set - no minimum self-bond or identity requirement
- **H2**: Register/unregister churn griefs consensus - no deposit or cooldown
- **H3**: Delegation accounting allows stake theft - delegated tokens not locked in-place

### MEDIUM
- **M1**: Slashing not propagated to voters/delegators
- **M2**: Integer overflow/underflow in stake aggregation - use checked_add
- **M3**: unregister_validator permission/cleanup bugs

### LOW
- **L1**: Reentrancy via external hooks (low risk in pure Substrate)
- **L2**: update_green_score root-gating is centralization point

## AMM-DEX Pallet Findings

### CRITICAL
- **C1**: Donation attack - first-deposit with tiny liquidity, donate to inflate reserves, drain
- **C5**: Zero-reserve pool creation trap - no minimum initial deposit
- **C7**: remove_liquidity overpayment if rounding/formula bug exists

### HIGH
- **H2**: Sandwich attack - no min_amount_out / deadline parameters
- **H6**: Missing slippage protection on swap/add/remove liquidity

## Presale Pallet Findings

### CRITICAL
- **C1**: Double claim - no Claimed flag set after claim
- **C2**: Refund after claim - no mutual exclusion between claim and refund
- **C3**: Double refund - contribution not zeroed after refund

### HIGH
- **H4**: Min/max per-user bypass - per-call not cumulative
- **H5**: Phase manipulation - set_phase may be callable by non-root
- **H6**: Vesting schedule bypass - start=0, duration=0 possible

## Vesting Pallet Findings

### CRITICAL
- **V1**: Vesting bypass via schedule params - start=0, duration=0
- **V2**: release() ignores time/cliff check
- **V5**: Claim another user's vested tokens - release(target, recipient)

### HIGH
- **V3**: Repeated admin_force_release
- **V4**: Admin bypasses all cliffs by design

## Eco Pallet Findings

### CRITICAL
- **E1**: mint_carbon_credit without root (VERIFY - may be fixed)
- **E3**: Retire credits not owned - no ownership check
- **E4**: Double retire same credit - no Retired set

### HIGH
- **E5**: Green score self-reported (VERIFY - may be fixed to root)
- **E2**: Duplicate/non-unique credit IDs

## Fungible-Tokens Pallet Findings

### CRITICAL
- **F1**: Mint beyond max_supply (VERIFY - may be fixed with checked_add)
- **F5**: Unrestricted minting - not owner-only

### HIGH
- **F2**: set_max_supply abuse - can raise to u128::MAX
- **F3**: Freeze bypass - transfer doesn't check frozen status

## Overall Security Scores (Kimi estimates)
- DPoS: ~65/100 (missing unbonding, Sybil protections)
- DEX: ~55/100 (missing slippage, donation protection)
- Presale: ~60/100 (missing state exclusivity)
- Vesting: ~50/100 (time bypass, unauthorized release)
- Eco: ~70/100 (auth fixes applied, ownership gaps)
- Fungible-Tokens: ~65/100 (max_supply may be fixed)
