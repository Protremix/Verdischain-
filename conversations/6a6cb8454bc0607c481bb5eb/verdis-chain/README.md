# Verdis Chain — The World's First Fully Green, Carbon-Negative Blockchain

Built with **Rust + Substrate FRAME** — the same framework powering Polkadot and Kusama.

## Architecture

```
verdis-chain/
├── node/                    # Full blockchain node (networking, RPC, consensus client)
│   ├── src/
│   │   ├── main.rs          # CLI entry point
│   │   ├── service.rs       # Node service (block production, networking, RPC)
│   │   └── chain_spec.rs    # Genesis configuration
│   └── Cargo.toml
├── runtime/                 # Runtime (wasm runtime that contains all pallet logic)
│   ├── src/
│   │   └── lib.rs           # All pallet wiring + runtime API implementations
│   ├── build.rs             # WASM builder
│   └── Cargo.toml
├── pallets/                 # Custom Verdis pallets
│   ├── dpos/                # DPoS consensus (validator registration, voting, rewards, slashing)
│   ├── amm-dex/             # AMM-based DEX (liquidity pools, swaps, LP tokens)
│   ├── eco/                 # Eco tracking (carbon credits, reforestation, green validators)
│   ├── tokenomics/          # Tokenomics enforcement (100B supply, 8-category distribution, IDO)
│   └── vesting/             # Protocol-level vesting (beforeTransfer hook, 30/60-day schedules)
├── Cargo.toml               # Workspace manifest
└── README.md
```

## Custom Pallets

### pallet-dpos
Delegated Proof of Stake consensus with:
- Validator registration with minimum stake (10,000 VRDX)
- Voter delegation (vote for validators by staking)
- Block reward distribution (16 VRDX per block)
- Validator slashing for misbehavior
- Epoch-based validator rotation (top 5 by votes, 100-block epochs)
- Green score tracking per validator
- Max 101 validators

### pallet-amm-dex
Constant-product (x*y=k) AMM with:
- Liquidity pool creation
- Add/remove liquidity (LP tokens)
- Token swaps with 0.3% fee
- Slippage protection (min_amount_out)
- Swap history recording
- Total volume and swap count tracking
- Max 50 pools

### pallet-eco
On-chain ecological impact tracking:
- Carbon credit minting, verification, trading, and retirement
- Reforestation project registration and verification
- Green validator registration with energy source
- Aggregate metrics: total CO2 offset, total trees planted
- Max 1,000 carbon credits, 500 reforest projects, 101 green validators

### pallet-tokenomics
Token economics enforcement:
- 100B total supply, 15B circulating at TGE (15%)
- 8-category distribution: Community (35%), Treasury (20%), Team (15%), Investors (10%), Staking (10%), Liquidity (5%), Advisors (3%), Airdrop (2%)
- 12B investor allocation enforcement
- IDO disclosure consent gating (mandatory)
- Presale price tracking ($0.0005/VRDX)

### pallet-vesting
Protocol-level vesting enforcement:
- Schedule-based token locks (Seed/Private: 60-day, Public/Final: 30-day)
- beforeTransfer hook pattern (Ethereum-style transfer blocking)
- Linear vesting with cliff periods
- Locked/unlocked balance queries
- Integration with transfers, DEX swaps, and staking

## Chain Parameters

| Parameter | Value |
|-----------|-------|
| Chain ID | 909 |
| Block Time | 5 seconds |
| Consensus | DPoS (Aura + Session) |
| Total Supply | 100,000,000,000 VRDX |
| Circulating at TGE | 15,000,000,000 VRDX (15%) |
| Block Reward | 16 VRDX |
| Max Validators | 101 |
| Active Validators | 5 (top by votes) |
| Epoch Length | 100 blocks |
| DEX Fee | 0.3% |
| Min Validator Stake | 10,000 VRDX |
| Max Pools | 50 |
| Cryptography | sr25519 (Schnorr) |

## Building

### Prerequisites

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Add WASM target
rustup target add wasm32-unknown-unknown

# Install dependencies (Ubuntu/Debian)
sudo apt install -y build-essential cmake pkg-config libssl-dev git protobuf-compiler
```

### Build the Node

```bash
cd verdis-chain
cargo build --release
```

### Run a Development Node

```bash
./target/release/verdis --dev --tmp
```

### Run with Custom Chain Spec

```bash
./target/release/verdis --chain verdis --name "verdis-node-1" --validator
```

## Deployment

```bash
# Build optimized release
cargo build --release

# Deploy via systemd
sudo cp verdis.service /etc/systemd/system/
sudo systemctl enable verdis
sudo systemctl start verdis
```

## Genesis Configuration

The genesis state includes:
- 7 DEX pools (CARBON/VRDX, ECO/VRDX, CARBON/ECO, TREE/VRDX, GREEN/VRDX, REDD/VRDX, ECOGR/VRDX)
- 5 initial validators with 1B stake each
- 5 carbon credits (17,000 tons CO2 offset)
- 1 reforestation project (30,000 trees)
- Full 8-category tokenomics distribution
- 4 vesting schedules (seed, private, public, final)

## API Compatibility

- Substrate JSON-RPC (built-in)
- Chain ID 909 for EVM compatibility
- Block time 5s matching previous implementation
- All Verdis-specific data accessible via custom storage queries

## License

MIT
