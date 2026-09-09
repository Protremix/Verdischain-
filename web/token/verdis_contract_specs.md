# VERDIS Token Contract Specification

## Overview
The VERDIS token is the native token of the Verdis Blockchain, implemented as a Substrate pallet (not an ERC-20). This document specifies the on-chain logic for token supply, transfers, staking, and governance.

## Native Token Properties
- **Name**: VERDIS
- **Symbol**: VRDX
- **Decimals**: 9 (smallest unit: 1 nano-VRDX)
- **Maximum Supply**: 100,000,000,000 VERDIS (100B)
- **SS58 Prefix**: 909
- **Cryptographic Curve**: sr25519 (Schnorrkel/Ristretto)

## Implemented Pallets (15)

### 1. pallet-tokens (Native Token)
- Functions: `transfer`, `transfer_keep_alive`, `set_balance` (root only)
- Storage: `TotalIssuance`, `Account` (balance per account)
- Events: `Transfer`, `BalanceSet`, `TransferEvent`
- Tests: 14 passing

### 2. pallet-dpos (Delegated Proof of Stake)
- Functions: `bond`, `unbond`, `nominate`, `chill`, `set_validator_name`, `update_green_score` (root only)
- Storage: `Validators`, `Stashes`, `ValidatorNames`, `GreenScores`
- RPC: `dpos_allValidators`, `dpos_validatorStake`, `dpos_validatorName`
- Staking Pool: 20B VERDIS (10-year emission at 2B/year)
- Unbonding Period: 28 days (2,519,200 blocks at 6-second blocks)
- Slashing: 10% for double-sign, 5% for downtime
- Minimum Stake: 100,000 VRDX (delegator), 500,000,000 VRDX (validator)
- Commission: 10% default (configurable per-validator)
- Tests: 34 passing

### 3. pallet-amm-dex (AMM DEX)
- Functions: `create_pool`, `add_liquidity`, `remove_liquidity`, `swap`
- Storage: `Pools`, `LiquidityProviders`, `PoolReserves`
- RPC: `amm_dex_getAllPools`, `amm_dex_getPool`
- Fee: 0.3% per swap
- Arithmetic: Checked (overflow/underflow protection)
- Liquidity Tokens: LP tokens with provider accounting
- Tests: 25 passing

### 4. pallet-eco (Eco-Features)
- Functions: `mint_carbon_credit` (root), `create_reforest_project` (root), `update_green_score` (root)
- Storage: `CarbonCredits`, `ReforestProjects`, `GreenScores`
- RPC: `eco_getGreenScore`, `eco_getAllGreenValidators`, `eco_getCarbonCredits`, `eco_getReforestProjects`
- Tests: 33 passing

### 5. pallet-tokenomics (Token Supply Management)
- Functions: `mint` (root), `burn` (root), `set_allocation`
- Storage: `Allocations`, `VestingSchedules`, `TotalMinted`
- Tests: 23 passing

### 6. pallet-vesting (Vesting Schedules)
- Functions: `vest`, `vest_other`, `create_vesting_schedule` (root)
- Storage: `VestingInfo`, `VestingSchedules`
- Supports: Linear vesting with cliff
- Tests: 10 passing

### 7. pallet-evm (EVM Compatibility)
- Chain ID: 909
- Max Code Size: 24,576 bytes
- 142 Opcodes (including Cancun: TLOAD, TSTORE, MCOPY, BLOBHASH, BLOBBASEFEE)
- Tests: 102 passing

### 8-15. Solana-Inspired Pallets
- pallet-poh (Proof of History): 8 tests
- pallet-gulf-stream: 6 tests
- pallet-turbine: 6 tests
- pallet-zk-compression: 6 tests
- pallet-alt (Account Lookup Table): 6 tests
- pallet-sealevel: 6 tests
- pallet-cloudbreak: Storage sharding (13 references)
- pallet-priority-fees: Tokenomics integration (20 references)

## Pending Contract Implementations

### Presale Contract (Specification)
```
Contract: PresaleContract
Functions:
  - buy(amount: Balance) -> Result<()>
  - claim() -> Result<Balance>
  - addWhitelist(address: AccountId) -> Result<()> (admin)
  - removeWhitelist(address: AccountId) -> Result<()> (admin)
  - setPrice(price: Balance) -> Result<()> (admin)
  - pause() -> Result<()> (admin)
  - unpause() -> Result<()> (admin)
  - emergencyWithdraw() -> Result<()> (admin)
Storage:
  - participants: Map<AccountId, ParticipantInfo>
  - totalRaised: Balance
  - hardCap: Balance
  - softCap: Balance
  - price: Balance
  - startTime: BlockNumber
  - endTime: BlockNumber
  - paused: bool
  - whitelisted: Set<AccountId>
Access Control:
  - buy(): Requires KYC verification, whitelist, within time window, not paused
  - claim(): Requires vesting period elapsed
  - admin functions: Requires ROOT or council approval
Constraints:
  - minPurchase: $100 equivalent
  - maxPurchase: $25,000 equivalent
  - maxPerWallet: 0.1% of presale allocation (2M VERDIS)
Security:
  - Pausable
  - Reentrancy guard
  - Overflow protection (checked math)
  - Whitelist enforcement
  - Time-locked admin functions
```

### Vesting Contract (Specification)
```
Contract: VestingContract
Functions:
  - createSchedule(beneficiary: AccountId, amount: Balance, cliff: BlockNumber, duration: BlockNumber) -> Result<()> (admin)
  - vestedAmount(beneficiary: AccountId) -> Balance (view)
  - releasableAmount(beneficiary: AccountId) -> Balance (view)
  - release() -> Result<Balance>
  - revokeSchedule(beneficiary: AccountId) -> Result<()> (admin)
Storage:
  - schedules: Map<AccountId, VestingSchedule>
  - released: Map<AccountId, Balance>
VestingSchedule:
  - beneficiary: AccountId
  - totalAmount: Balance
  - cliffEnd: BlockNumber
  - vestingEnd: BlockNumber
  - tgeUnlock: Balance (unlocked at TGE)
  - revoked: bool
Access Control:
  - createSchedule: ROOT only
  - release: Beneficiary only
  - revoke: ROOT + governance approval
Security:
  - Immutable schedules (cannot be modified after creation)
  - Reentrancy guard
  - Event emission for all state changes
  - Emergency pause mechanism
```

### Staking Contract (Already Implemented)
See pallet-dpos above. Key parameters:
- Validator count: 21 (launch) → 200+ (expansion)
- Commission: 10% default
- Unbonding: 28 days
- Slashing: 10% double-sign, 5% downtime
- Emission: 2B VERDIS/year for 10 years

### Treasury Architecture (Specification)
```
Contract: TreasuryMultiSig
Functions:
  - submitProposal(target: AccountId, amount: Balance, description: String) -> Result<ProposalId>
  - approveProposal(proposalId: ProposalId) -> Result<()>
  - executeProposal(proposalId: ProposalId) -> Result<()>
  - cancelProposal(proposalId: ProposalId) -> Result<()>
  - addSigner(signer: AccountId) -> Result<()> (governance)
  - removeSigner(signer: AccountId) -> Result<()> (governance)
  - setThreshold(threshold: u32) -> Result<()> (governance)
Storage:
  - signers: Set<AccountId>
  - threshold: u32 (default: 5 of 7)
  - proposals: Map<ProposalId, Proposal>
  - spendingLimit: Balance (max 10% of balance per month)
  - monthlySpent: Map<Month, Balance>
Proposal:
  - id: ProposalId
  - target: AccountId
  - amount: Balance
  - description: String
  - approvals: Set<AccountId>
  - executed: bool
  - cancelled: bool
Access Control:
  - submitProposal: Any signer
  - approveProposal: Signer only
  - executeProposal: Any signer (after threshold met)
  - addSigner/removeSigner: Governance vote
  - setThreshold: Governance vote
Constraints:
  - Max 10% of treasury balance per month
  - Monthly reset on block number modulo
  - Public proposal visibility
  - 7-day timelock before execution
Security:
  - Multisig (5-of-7)
  - Timelock (7 days)
  - Spending limit (10% monthly)
  - Public audit log
  - Emergency freeze (governance vote)
```

## Test Requirements (Pre-Deployment)
1. Unit tests for every contract function
2. Integration tests for contract interactions
3. Fuzz tests for:
   - Overflow/underflow in arithmetic
   - Reentrancy attacks
   - Access control bypass
   - Vesting schedule manipulation
4. Access control tests
5. Vesting schedule tests
6. Presale contract tests
7. Staking contract tests
8. Treasury multisig tests
9. Emergency mechanism tests
10. Economic attack simulations
11. Independent security audit

## Deployment Checklist
- [ ] All unit tests passing (currently: 137)
- [ ] Integration tests written and passing
- [ ] Fuzz tests written and passing
- [ ] Access control audit
- [ ] Vesting contract implemented
- [ ] Presale contract implemented
- [ ] Treasury multisig implemented
- [ ] Independent security audit completed
- [ ] All critical findings resolved
- [ ] Mainnet chain spec finalized
- [ ] Genesis allocation configured
- [ ] Validator set configured
- [ ] NO real-money deployment before above items complete
