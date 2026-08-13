# GPT-4o Architecture Review — Aug 4, 2026

## Recommendations

### 1. Slashing (CRITICAL)
Uncomment VerdisOffenceHandler slashing logic:
- Slash 5% of stake per offence
- Call Dpos::slash_validator() directly
- Optionally jail the validator

### 2. dpos_activeValidators Empty
Check: genesis config, storage key prefixes, RPC registration

### 3. Remove Sudo Before Mainnet
- Use fast-track governance for emergency upgrades
- Ensure Council + Democracy are fully operational first

### 4. DEX Circuit Breaker
- 5% price deviation threshold per swap
- Error::PriceDeviationTooHigh

### 5. Smart Contract Pre-requisites
- Verify Contracts pallet config (storage deposits, gas/weight limits)
- Confirm WASM runtime supports ink! contracts
- Security audit of Contracts pallet

### 6. Validator Stake Caps
- 10% of total stake
- Enforce in register_validator

### 7. Hybrid DPoS
- pallet_staking for economics
- Custom DPoS for eco/green scoring
