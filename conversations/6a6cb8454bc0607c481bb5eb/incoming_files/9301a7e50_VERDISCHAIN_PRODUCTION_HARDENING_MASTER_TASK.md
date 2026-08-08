VERDISCHAIN — PRODUCTION HARDENING & MAINNET READINESS
MASTER TASK FOR ALL DEVELOPMENT AGENTS

Repository: Protremix/Verdischain-
Target: Production-ready Verdis Blockchain
Token: VERDIS
Maximum Supply: 100,000,000,000 VERDIS
Priority: CRITICAL

1. MISSION

Bring the existing Verdischain implementation from its current development state to a production-ready, secure, internally consistent blockchain.

Do not rebuild Verdischain from scratch.

First audit the existing implementation, identify inconsistencies, then fix and test them.

The final implementation must have one consistent source of truth across:
- Runtime
- Genesis
- Tokenomics
- Balances
- PoS/DPoS
- Validators
- Staking
- Rewards
- Slashing
- Vesting
- Presale
- DEX
- Fungible tokens
- Governance
- RPC
- Node/network
- Tests
- Documentation

2. CRITICAL RULE

Do not mark anything as DONE simply because it compiles.

Every change must be verified through:
1. Code review
2. Unit tests
3. Integration tests
4. Economic invariant tests
5. Genesis validation
6. Runtime validation
7. Security testing
8. Documentation synchronization

If an assumption is not supported by the existing code, do not invent an implementation. Mark it as a blocker and explain what decision is required.

3. FINAL VERDIS TOKENOMICS

Replace the current tokenomics with this approved working model:

Ecosystem & Developer Grants: 25% / 25B
PoS Staking Rewards: 20% / 20B
Treasury: 15% / 15B
Development: 10% / 10B
Liquidity: 10% / 10B
Community: 5% / 5B
Seed / Strategic: 3% / 3B
Public Presale: 2% / 2B
Team & Advisors: 5% / 5B
TOTAL: 100% / 100B

Verify:
25B + 20B + 15B + 10B + 10B + 5B + 3B + 2B + 5B = 100B VERDIS

Create automated tests proving this.

4. SUPPLY RULES

Maximum Supply = 100,000,000,000 VERDIS
Decimals = 9

No undocumented mechanism may create additional VERDIS.

Every mint/emission mechanism must be explicitly identified.

Create supply invariants proving:
total_supply <= 100B
sum(all tracked allocations) <= 100B

5. GENESIS AUDIT AND REWRITE

Completely reconcile genesis with final tokenomics.

Create deterministic accounts for:
- Ecosystem
- Staking
- Treasury
- Development
- Liquidity
- Community
- Seed
- Public Presale
- Team

The sum of all genesis allocations must equal exactly 100,000,000,000 VERDIS.

Do not rely on comments claiming genesis equals 100B.

The code must mathematically prove it.

Ensure tokenomics state, balances, staking pools, DEX reserves and vesting allocations do not accidentally count the same tokens twice.

6. TGE / CIRCULATING SUPPLY

Target approximately 8B VERDIS circulating at TGE.

Do not simply hardcode 8B.

Implement an explicit calculation showing exactly which allocations are circulating at TGE.

Prove:
TGE circulating supply <= total supply
TGE circulating supply ≈ 8B

Document the final TGE breakdown.

7. DPOS / VALIDATOR ARCHITECTURE

Target mainnet model:
21 Validators -> 31 Validators -> 51 Validators -> 100+

Initial mainnet target: 21 active validators.

Support:
- validator registration
- minimum stake
- delegation
- validator ranking
- activation/deactivation
- epoch rotation
- validator replacement
- inactive validator handling
- slashed validator handling
- validator rewards
- validator commission

8. STAKING

Implement sustainable PoS staking.

Calculate and test:
- validator rewards
- delegator rewards
- staking APR
- validator commission
- minimum stake
- unbonding
- slashing
- staking participation

Test staking participation at:
10%, 20%, 30%, 40%, 50%, 60%, 70%, 80%.

9. BLOCK REWARDS

Audit the existing block reward mechanism.

Prove:
Block Produced -> Validator Identified -> Reward Calculated -> Reward Source Debited -> Validator/Delegator Credited -> Event Emitted -> Accounting Updated

Run integration tests across at least 1,000 blocks.

If rewards are pre-funded, prove block rewards do not accidentally increase maximum supply.

10. SLASHING

After a slash, keep consistent:
- validator stake
- reserved balance
- total staked
- treasury balance
- reward calculations

Test:
- 1% slash
- 5% slash
- 100% slash
- repeated slash
- inactive validator
- already-slashed validator
- slash larger than stake
- overflow
- underflow

11. VESTING

Remove hardcoded time assumptions that conflict with actual block time.

Seed:
Allocation 3B
TGE unlock 0%
Cliff 6 months
Vesting 18 months

Team:
Allocation 5B
TGE unlock 0%
Cliff 12 months
Vesting 36 months

Development, ecosystem and other allocations must receive controlled release schedules.

Invariant:
vested + unvested = original allocation

12. PRESALE

Treat current presale implementation as not production-ready until payment flow is fully verified.

Implement:
- Create Sale
- Configure
- Open
- Purchase
- Claim
- Finalize

Support:
- hard cap
- wallet cap
- sale start/end
- price
- allocation remaining
- vesting
- claim
- pause
- emergency handling
- refund where required

Do not invent the payment asset. If undefined, report a blocker.

13. SEED / STRATEGIC ROUND

Allocation: 3B VERDIS.

Support:
- token price
- allocation
- capital raised
- discount to TGE
- cliff
- vesting
- unlock schedule

No Seed tokens should be immediately liquid unless explicitly approved.

14. PUBLIC PRESALE

Allocation: 2B VERDIS.

Implement:
- allocation limits
- wallet limits
- purchase limits
- vesting
- TGE unlock
- claim mechanism
- anti-concentration controls

15. DEX SECURITY AUDIT

The pool must have real custody accounting:
DEX Pool -> Pool Account -> Actual Token Balances

Prove actual custody balances equal recorded pool reserves, or document the exact invariant.

Test:
- pool creation
- first liquidity
- add/remove liquidity
- swaps
- fees
- slippage
- price impact
- zero amounts
- overflow/underflow
- rounding
- empty pools
- donation attacks
- malicious tokens
- pool poisoning
- repeated swaps

Add property-based tests and fuzzing.

16. FUNGIBLE TOKEN SYSTEM

Audit:
- create
- mint
- burn
- transfer
- approve
- transfer_from
- freeze
- destroy
- metadata
- permissions

Invariant:
sum(all token balances) == token total supply

Test all authorization boundaries.

17. GOVERNANCE

Audit:
- Sudo
- Council
- Democracy
- Treasury
- Multisig
- Proxy
- privileged runtime calls

Development privileges must not accidentally survive into production.

There must be no undocumented founder backdoor.

If emergency Sudo is retained temporarily, define scope, controlled authority, audit logging and removal plan.

18. MAINNET CHAIN SPECIFICATION

Create separate configurations:
- Development
- Local
- Testnet
- Mainnet

Mainnet must have:
- unique chain ID
- deterministic genesis
- production bootnodes
- production protocol ID
- production validator configuration
- no development accounts
- no test balances
- no development-only assumptions

Do not allow mainnet commands to silently load development chain specifications.

19. SEED / BOOTSTRAP INFRASTRUCTURE

Initial target: 5–7 independent seed/bootstrap nodes.

Support:
- multiple bootstrap endpoints
- peer discovery
- peer exchange
- health checks
- fallback peers
- automatic peer replacement

Loss of one or more seed nodes must not prevent a new node from joining the network.

20. RPC AND API

Audit all RPC endpoints.

Verify:
- invalid input
- missing data
- large input
- large responses
- deterministic behavior
- error handling
- state consistency
- DoS resistance
- pagination

Create a stable production API version and document every public endpoint.

21. SECURITY TESTING

Create:
- unit tests for every pallet
- integration tests
- property tests
- fuzzing

Full integration flow:
Genesis -> Validator -> Block -> Reward -> Staking -> Slash -> Vesting -> DEX -> Token -> Governance

22. ECONOMIC INVARIANTS

Create economic_invariants.rs.

Mandatory checks:
TOTAL_SUPPLY == 100B
sum(genesis allocations) == 100B
circulating_supply <= total_supply
vested + unvested == allocation
validator stake == expected reserved funds
reward pool accounting is exact
DEX reserves == custody balances
custom token balances == token supply

Run these tests in CI.

23. CI/CD

Project must pass:
cargo fmt --check
cargo check
cargo test
cargo test --workspace
cargo clippy
cargo build --release
cargo build --release --target wasm32-unknown-unknown

Run runtime validation tools where applicable.

No production release with failing tests.

24. DOCUMENTATION

Synchronize:
- README
- Tokenomics
- Staking
- Validators
- Presale
- Seed
- Vesting
- DEX
- Governance
- RPC
- Mainnet
- Testnet
- Node setup

Documentation must never hide code inconsistencies.

25. AGENT RESPONSIBILITIES

Agent 1 — Tokenomics & Genesis
Own tokenomics, supply, allocations, TGE, genesis, balances and supply invariants.

Agent 2 — DPoS & Staking
Own validators, staking, rewards, epochs, delegation and slashing.

Agent 3 — Vesting
Own Seed, Team, Development vesting, cliffs, unlocks and time calculations.

Agent 4 — Presale
Own sale lifecycle, payment, purchase, caps, claims, refunds and vesting integration.
If payment asset is undefined, report a blocker.

Agent 5 — DEX Security
Own AMM, liquidity, custody, reserves, LP accounting, swaps, fees and economic attack testing.

Agent 6 — Fungible Tokens
Own mint, burn, transfer, approvals, freeze, destroy, permissions and supply invariants.

Agent 7 — Governance & Security
Own Sudo, Council, Democracy, Treasury, Multisig, Proxy and privileged operations.

Agent 8 — Node & Mainnet
Own node, chain specification, networking, bootnodes, seed nodes, testnet and mainnet.

Agent 9 — RPC/API
Own RPC, API, errors, validation, pagination, security and documentation.

Agent 10 — QA / Final Security Auditor
Independently review all work.
Do not assume other agents are correct.

Create:
AUDIT_REPORT.md

Classify every finding:
BLOCKER
CRITICAL
HIGH
MEDIUM
LOW
WARNING
PASS

26. DEFINITION OF DONE

The project is NOT DONE until:

[ ] 100B maximum supply verified
[ ] 9 decimals verified
[ ] Final tokenomics implemented
[ ] Genesis matches tokenomics
[ ] Genesis totals exactly 100B
[ ] TGE circulating supply verified
[ ] 21 validators configured
[ ] Validator lifecycle tested
[ ] Staking tested
[ ] Rewards tested
[ ] Slashing tested
[ ] Vesting timing corrected
[ ] Seed vesting implemented
[ ] Team vesting implemented
[ ] Presale secured
[ ] DEX custody verified
[ ] DEX invariants tested
[ ] Fungible-token invariants tested
[ ] Governance audited
[ ] No undocumented privileged backdoor
[ ] Mainnet chain specification implemented
[ ] Testnet chain specification implemented
[ ] Seed/bootstrap infrastructure implemented
[ ] RPC audited
[ ] Integration tests passing
[ ] Property tests passing
[ ] Fuzz tests completed
[ ] Economic invariant suite passing
[ ] Release build passing
[ ] WASM build passing
[ ] Documentation synchronized
[ ] Final security audit completed
[ ] All BLOCKER and CRITICAL findings resolved

FINAL DIRECTIVE

Do not optimize for “it compiles.”

Optimize for:
Correctness -> Security -> Economic consistency -> Decentralization -> Testability -> Production reliability.

Do not rebuild existing Verdischain unnecessarily.

Audit first. Fix second. Refactor only when necessary. Test every change.

The final result must be a Verdis Blockchain where runtime, genesis, tokenomics, staking, validators, vesting, presale, DEX, governance, RPC and documentation all describe and implement the same system.
