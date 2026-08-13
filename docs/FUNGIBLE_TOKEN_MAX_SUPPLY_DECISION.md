# Fungible-Token Max Supply Design Decision

## Date: August 13, 2026
## SHA: 477470943cb45aec05781ebc777d8fcf668ce7c5
## Status: IMPLEMENTED

## Decision

**max_supply is a one-way ratchet — it can only decrease, never increase after token creation.**

## Rationale

1. **Token Holder Protection**: Allowing token owners to increase max_supply after creation enables dilution attacks. An owner could mint unlimited tokens, devaluing all existing holdings.

2. **Economic Integrity**: For VRDX (native token with fixed 100B supply), max_supply immutability is a core promise to investors. User-created tokens via the fungible-tokens pallet must offer the same guarantee.

3. **Uniswap/ERC-20 Standard**: Standard ERC-20 tokens with capped supply do not allow increasing the cap. Solana's Token-2022 also enforces immutable supply caps.

4. **Flexibility Preserved**: Decreasing the cap is still allowed (e.g., to lock in a final supply or reduce from u128::MAX to a specific cap). This covers legitimate use cases like "set the real cap after creation" without enabling inflation.

## Implementation

### Before (vulnerable):
```rust
// Could increase OR decrease - no protection against inflation
ensure!(max_supply >= token.total_supply, Error::MaxBalanceExceeded);
token.max_supply = max_supply;
```

### After (fixed):
```rust
// One-way ratchet: can only decrease, never increase
ensure!(max_supply <= token.max_supply, Error::MaxSupplyCannotIncrease);
ensure!(max_supply >= token.total_supply, Error::MaxBalanceExceeded);
token.max_supply = max_supply;
```

### New Error: `MaxSupplyCannotIncrease`
Emitted when `max_supply > token.max_supply`.

## Regression Tests (4 new tests)

1. `set_max_supply_decrease_succeeds` — Verify decreasing max_supply works
2. `set_max_supply_increase_fails` — Verify increasing max_supply fails with `MaxSupplyCannotIncrease`
3. `set_max_supply_below_total_supply_fails` — Verify can't set below current total_supply
4. `set_max_supply_non_owner_fails` — Verify only owner can change max_supply

## Test Results: 27 tests pass, 0 failures (was 23 tests, added 4 regression tests)
