# Verdis Chain v2.0 — The World's First Fully Green, Carbon-Negative Blockchain

Built with **Rust + Substrate FRAME** — the same framework powering Polkadot and Kusama.

## Architecture Specification

| Component | Technology |
|-----------|-----------|
| **Language** | Rust |
| **Core** | Substrate FRAME |
| **P2P** | libp2p |
| **Database** | RocksDB |
| **Smart Contracts** | WASM (pallet-contracts) + Solidity via EVM (pallet-evm) |
| **Consensus** | BABE (block production) + GRANDPA (finality) |
| **Cryptography** | BLS (GRANDPA) + Ed25519 (session) + Blake3 (content hashing) |
| **Storage** | IPFS / Arweave (pallet-storage) |
| **Wallet** | Native + MetaMask via EVM (Chain ID 909) |
| **API** | gRPC (port 9090) + JSON-RPC (port 9933) |
| **Indexing** | SubQuery / The Graph compatible |

## Project Structure

```
verdis-chain/
├── node/                        # Full blockchain node
│   ├── src/
│   │   ├── main.rs             # CLI entry point (run, build-spec, info)
│   │   └── service.rs          # BABE+GRANDPA service, networking, RPC
│   ├── proto/
│   │   └── verdis.proto        # gRPC API definitions (25+ RPC methods)
│   └── Cargo.toml
├── runtime/                     # Substrate runtime (WASM)
│   ├── src/
│   │   └── lib.rs              # All pallet wiring + runtime APIs
│   ├── build.rs                # WASM builder
│   └── Cargo.toml
├── pallets/                     # Custom Verdis pallets
│   ├── dpos/                   # DPoS consensus (validators, voting, slashing)
│   ├── amm-dex/                # AMM DEX (liquidity pools, swaps, LP tokens)
│   ├── eco/                    # Eco tracking (carbon credits, reforestation)
│   ├── tokenomics/             # Tokenomics (100B supply, 8-category, IDO)
│   ├── vesting/                # Protocol-level vesting (beforeTransfer hook)
│   └── storage/                # IPFS/Arweave decentralized storage
├── Cargo.toml                  # Workspace manifest
└── README.md
```

## Custom Pallets

### pallet-dpos — DPoS Consensus
- Validator registration with minimum stake (10,000 VRDX)
- Voter delegation (vote for validators by staking)
- Block reward distribution (16 VRDX per block)
- Validator slashing for misbehavior
- Epoch-based validator rotation (top 5 by votes, 600-block epochs)
- Green score tracking per validator
- Max 101 validators
- Session manager integration (works with BABE/GRANDPA)

### pallet-amm-dex — AMM DEX
- Constant-product (x*y=k) liquidity pools
- Add/remove liquidity with LP tokens
- Token swaps with 0.3% fee
- Slippage protection (min_amount_out)
- Swap history recording
- Total volume and swap count tracking
- Max 50 pools

### pallet-eco — Eco Tracking
- Carbon credit minting, verification, trading, and retirement
- Reforestation project registration and verification
- Green validator registration with energy source tracking
- Aggregate metrics: total CO2 offset, total trees planted
- Max 1,000 carbon credits, 500 reforest projects, 101 green validators

### pallet-tokenomics — Token Economics
- 100B total supply, 15B circulating at TGE (15%)
- 8-category distribution:
  - Community (35%), Treasury (20%), Team (15%), Investors (10%)
  - Staking (10%), Liquidity (5%), Advisors (3%), Airdrop (2%)
- 12B investor allocation enforcement
- IDO disclosure consent gating (mandatory)
- Presale price tracking ($0.0005/VRDX)

### pallet-vesting — Protocol-Level Vesting
- Schedule-based token locks (Seed/Private: 60-day, Public/Final: 30-day)
- beforeTransfer hook pattern (Ethereum-style transfer blocking)
- Linear vesting with cliff periods
- Locked/unlocked balance queries
- Integration with transfers, DEX swaps, and staking

### pallet-storage — IPFS/Arweave Storage
- IPFS CID registration and verification
- Arweave transaction ID tracking
- Content verification via Blake3 hashing
- Storage provider registration with reputation
- Pinning requests and status tracking
- Max 10,000 storage records

## Chain Parameters

| Parameter | Value |
|-----------|-------|
| Chain ID | 909 |
| Block Time | 6 seconds (BABE) |
| Consensus | BABE (production) + GRANDPA (finality) |
| Total Supply | 100,000,000,000 VRDX |
| Circulating at TGE | 15,000,000,000 VRDX (15%) |
| Block Reward | 16 VRDX |
| Max Validators | 101 |
| Active Validators | 5 (top by votes) |
| Epoch Length | 600 blocks (~1 hour) |
| DEX Fee | 0.3% |
| Min Validator Stake | 10,000 VRDX |
| Max Pools | 50 |
| EVM Gas Limit | 30,000,000 per block |
| Cryptography | BLS12-381 (GRANDPA), Ed25519 (session), Blake3 (content) |

## gRPC API (port 9090)

25+ RPC methods covering:
- **Blockchain**: GetBlock, GetLatestBlock, GetBlockRange, GetTransaction, GetChainInfo
- **Validators**: GetValidators, GetActiveValidators, GetValidator, GetEpochInfo
- **DEX**: GetPools, GetPool, GetSwapHistory
- **Eco**: GetCarbonCredits, GetReforestProjects, GetEcoMetrics
- **Tokenomics**: GetTokenomics, GetVestingSchedules
- **Storage**: GetStorageRecords, GetStorageProviders
- **Streaming**: SubscribeBlocks, SubscribeTransactions
- **Transactions**: SubmitTransaction

See `node/proto/verdis.proto` for full protobuf definitions.

## Smart Contracts

### WASM Contracts (pallet-contracts)
- Native Substrate smart contracts compiled to WASM
- ink! language support
- Lower gas costs than EVM
- Direct access to Substrate runtime APIs

### Solidity Contracts (pallet-evm via Frontier)
- Full EVM compatibility
- MetaMask / Trust Wallet / WalletConnect support
- Chain ID 909 for EIP-155 compatibility
- Solidity 0.8.x contracts supported
- Standard ERC-20, ERC-721, ERC-1155 compatible

## Building

### Prerequisites

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Add WASM target
rustup target add wasm32-unknown-unknown

# Install system dependencies (Ubuntu/Debian)
sudo apt install -y build-essential cmake pkg-config libssl-dev \
    git protobuf-compiler libclang-dev llvm

# Install system dependencies (macOS)
brew install cmake pkg-config openssl protobuf llvm
```

### Build

```bash
cd verdis-chain
cargo build --release

# With EVM RPC support
cargo build --release --features evm-rpc

# With gRPC server
cargo build --release --features grpc
```

### Run

```bash
# Development mode (single node)
./target/release/verdis run --dev --tmp

# Production validator
./target/release/verdis run --validator --name "verdis-node-1"

# With custom ports
./target/release/verdis run --port 30333 --rpc-port 9933 --grpc-port 9090
```

## Deployment (verdischain.com)

```bash
# Build optimized release
cargo build --release

# Deploy via systemd
sudo cp verdis.service /etc/systemd/system/
sudo systemctl enable verdis
sudo systemctl start verdis
```

## MetaMask Integration

Add Verdis Chain to MetaMask:
- Network Name: Verdis Chain
- RPC URL: https://verdischain.com/rpc
- Chain ID: 909
- Symbol: VRDX
- Explorer: https://verdischain.com/explorer

## SubQuery Indexing

Create a `project.yaml` for SubQuery:
```yaml
specVersion: 1.0.0
name: verdis-indexer
version: 1.0.0
runner:
  node:
    name: "@subql/node"
    version: "*"
  query:
    name: "@subql/query"
    version: "*"
schema: ./schema.graphql
network:
  endpoint: wss://verdischain.com/ws
  chainId: 909
dataSources:
  - kind: substrate/Runtime
    startBlock: 1
    mapping:
      handlers:
        - handler: handleBlock
          kind: substrate/BlockHandler
        - handler: handleTransaction
          kind: substrate/CallHandler
        - handler: handleEcoEvent
          kind: substrate/EventHandler
          filter:
            module: eco
```

## Genesis Configuration

- 7 DEX pools (CARBON/VRDX, ECO/VRDX, CARBON/ECO, TREE/VRDX, GREEN/VRDX, REDD/VRDX, ECOGR/VRDX)
- 5 initial validators with 1B stake each
- 5 carbon credits (17,000 tons CO2 offset)
- 1 reforestation project (30,000 trees)
- Full 8-category tokenomics distribution
- 4 vesting schedules (seed, private, public, final)

## License

MIT

## Built by

**Protremix** | Founder & CEO: **Rojs Gordons**
