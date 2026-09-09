# Verdis Chain Data Manifest
version: 0.1.0
status: testnet-ratified
last_updated: 2026-08-09

> This file is the single source of truth for all chain, runtime, tokenomics, and web numbers.
> Any future change to tokenomics, consensus, or network identity must update this file first.

## Token
- name: Verdis
- symbol: VRDX
- decimals: 9
- ss58Prefix: 909
- totalSupply: 100,000,000,000 VRDX (100B)
- circulatingSupply: 17,000,000,000 VRDX (17B, testnet)
- units: 1,000,000,000 (1 VRDX = 10^9 Planck)

## Allocation (VRDX)
| Category | Amount | Percentage | Vesting / Lock |
|---|---|---|---|
| Ecosystem & Developer Grants | 25,000,000,000 | 25% | TBD (governance-controlled) |
| PoS Staking Rewards | 20,000,000,000 | 20% | Per-block emission |
| Treasury | 15,000,000,000 | 15% | TBD (DAO-governed) |
| Development | 10,000,000,000 | 10% | TBD (milestone-based) |
| Liquidity | 10,000,000,000 | 10% | AMM pools + exchange listings |
| Community | 5,000,000,000 | 5% | Airdrops, grants, rewards |
| Seed / Strategic | 3,000,000,000 | 3% | 12-month cliff, 24-month linear |
| Public Presale | 2,000,000,000 | 2% | 3-month cliff, 12-month linear |
| Team & Advisors | 5,000,000,000 | 5% | 12-month cliff, 36-month linear |
| **Total** | **100,000,000,000** | **100%** | |

## Consensus
- expectedBlockTimeMs: 6000 (6 seconds)
- blockTimeSeconds: 6
- testnetEpochDuration: 50 blocks (~5 minutes)
- mainnetEpochDuration: 1200 blocks (~2 hours, target)
- babeSameAuthoritiesForever: true (testnet only)
- grandpaSessionPeriod: 50 blocks (matches epoch)
- blockReward: 16 VRDX/block
- consensus: DPoS (BABE block production + GRANDPA finality)

## Network Identity
- chainNameTestnet: Verdis (Development)
- chainIdTestnet: verdis
- chainType: Development
- chainNameMainnet: Verdis
- chainIdMainnet: verdis
- protocolIdMainnet: vrd (TBD for mainnet)
- bootnodesTestnet: 
  - /ip4/127.0.0.1/tcp/30333/p2p/12D3KooW... (Alice, node key 0x01)
  - /ip4/127.0.0.1/tcp/30334/p2p/12D3KooW... (Bob, node key 0x02)
  - /ip4/127.0.0.1/tcp/30335/p2p/12D3KooW... (Charlie, node key 0x03)
- bootnodesMainnet: TBD

## Validators
- currentTestnetNodes: 3 (Alice, Bob, Charlie)
- registeredDposValidators: 21
- activeValidators: 3 (ValidatorCount const in runtime)
- mainnetTargetValidators: 21
- maxValidators: 1000
- maxValidatorsPerNode: 16
- minValidatorStake: 10,000 VRDX
- maxStakePerValidator: 10,000,000,000 VRDX (10B)

## Runtime
- pallets: 36
- unitTests: 144
- runtimeConstantsSource: runtime/src/lib.rs
- chainSpecSource: node/src/chain_spec.rs
- wasmBinary: verdis_runtime::WASM_BINARY

## Web Display
- homepageTests: 144
- homepagePallets: 36
- tokenomicsCategories: 9
- whitepaperPieSegments: 9
- tokenSymbolDisplayed: VRDX
- decimalsDisplayed: 9
- blockTimeDisplayed: 6 seconds

## Audit
- kimiFindings: 15 critical
- kimiStatus: all addressed
- securityScore: 100/100 (18 checks pass)
- soakTestStatus: PASSED (1-node kill, 2-node kill, recovery, 8 epoch rotations, 0 errors)

## Testnet Status (as of 2026-08-09)
- blockHeight: 426+
- finalizedBlock: 420+
- peers: 2
- nodes: 3
- epochRotations: 8 (epoch 0 -> 8)
- errors: 0

## CHANGELOG
- 2026-08-09: Initial creation. All numbers sourced from runtime/src/lib.rs, node/src/chain_spec.rs, and on-chain state.

## RULE
Any future change to tokenomics, consensus, or network identity must update this file first.
No web page, whitepaper, or documentation may display numbers that contradict this manifest.
