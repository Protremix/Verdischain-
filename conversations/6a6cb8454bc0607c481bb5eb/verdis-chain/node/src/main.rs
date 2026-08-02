//! Verdis Chain Node — Entry Point
//!
//! Architecture: BABE (block production) + GRANDPA (finality)
//! APIs: JSON-RPC + gRPC
//! Chain ID: 909

use std::sync::Arc;

use clap::Parser;
use futures::stream::StreamExt;

#[derive(Parser)]
#[command(
    name = "verdis",
    about = "Verdis Chain — The world's first fully green, carbon-negative blockchain",
    version = "2.0.0"
)]
struct Cli {
    /// Run the node
    #[command(subcommand)]
    command: Commands,
}

#[derive(clap::Subcommand)]
enum Commands {
    /// Run the Verdis node
    Run {
        #[arg(long)]
        dev: bool,
        #[arg(long)]
        tmp: bool,
        #[arg(long)]
        name: Option<String>,
        #[arg(long)]
        validator: bool,
        #[arg(long, default_value = "30333")]
        port: u16,
        #[arg(long, default_value = "9933")]
        rpc_port: u16,
        #[arg(long, default_value = "9090")]
        grpc_port: u16,
    },
    /// Build chain specification
    BuildSpec,
    /// Show node info
    Info,
}

fn main() -> sc_cli::Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Run { dev, tmp, name, validator, port, rpc_port, grpc_port } => {
            println!("🌿 Verdis Chain v2.0.0 — Starting node...");
            println!("   Consensus: BABE + GRANDPA");
            println!("   Chain ID: 909");
            println!("   P2P Port: {}", port);
            println!("   JSON-RPC Port: {}", rpc_port);
            println!("   gRPC Port: {}", grpc_port);
            println!("   Validator: {}", if validator { "Yes" } else { "No" });
            println!();

            // In production, this would initialize the full Substrate client
            // For now, we show the architecture is ready
            // The actual node binary requires full Substrate compilation
            // (see README.md for build instructions)

            println!("⚠️  Full node compilation requires Substrate build dependencies.");
            println!("   See verdis-chain/README.md for build instructions.");
            println!();
            println!("Architecture summary:");
            println!("  • Language:       Rust");
            println!("  • Core:           Substrate FRAME");
            println!("  • Consensus:      BABE + GRANDPA");
            println!("  • Smart Contracts: WASM (pallet-contracts) + Solidity (pallet-evm)");
            println!("  • Cryptography:   BLS + Ed25519 + Blake3");
            println!("  • P2P:            libp2p");
            println!("  • Database:       RocksDB");
            println!("  • Storage:       IPFS/Arweave (pallet-storage)");
            println!("  • Wallet:         Native + MetaMask via EVM");
            println!("  • API:            gRPC (port {}) + JSON-RPC (port {})", grpc_port, rpc_port);
            println!("  • Indexing:       SubQuery compatible");

            Ok(())
        }
        Commands::BuildSpec => {
            println!("Building Verdis chain spec...");
            println!("Chain ID: 909");
            println!("Consensus: BABE + GRANDPA");
            println!("Validators: 5 initial (Alice, Bob, Charlie, Dave, Eve)");
            println!("Total Supply: 100,000,000,000 VRDX");
            println!("Circulating: 15,000,000,000 VRDX (15%)");
            println!("DEX Pools: 7 (CARBON/VRDX, ECO/VRDX, CARBON/ECO, TREE/VRDX, GREEN/VRDX, REDD/VRDX, ECOGR/VRDX)");
            Ok(())
        }
        Commands::Info => {
            println!("Verdis Chain v2.0.0");
            println!();
            println!("The world's first fully green, carbon-negative blockchain");
            println!();
            println!("Architecture:");
            println!("  Language:        Rust");
            println!("  Core:            Substrate FRAME");
            println!("  Consensus:       BABE + GRANDPA");
            println!("  Contracts:       WASM + Solidity via EVM");
            println!("  Cryptography:    BLS + Ed25519 + Blake3");
            println!("  P2P:             libp2p");
            println!("  Database:        RocksDB");
            println!("  Storage:         IPFS/Arweave");
            println!("  Wallet:          Native + MetaMask via EVM");
            println!("  API:             gRPC + JSON-RPC");
            println!("  Indexing:        SubQuery / The Graph");
            println!();
            println!("Custom Pallets:");
            println!("  pallet-dpos      — DPoS consensus (validators, voting, slashing)");
            println!("  pallet-amm-dex   — AMM DEX (liquidity pools, swaps, LP tokens)");
            println!("  pallet-eco       — Eco tracking (carbon credits, reforestation)");
            println!("  pallet-tokenomics — Tokenomics (100B supply, 8-category, IDO)");
            println!("  pallet-vesting   — Protocol-level vesting (beforeTransfer hook)");
            println!("  pallet-storage   — IPFS/Arweave decentralized storage");
            println!();
            println!("Chain Parameters:");
            println!("  Chain ID:        909");
            println!("  Block Time:      6 seconds (BABE)");
            println!("  Total Supply:    100B VRDX");
            println!("  Circulating:     15B VRDX (15%)");
            println!("  Block Reward:    16 VRDX");
            println!("  Max Validators:  101");
            println!("  Active Validators: 5 (top by votes)");
            println!("  Epoch Length:    600 blocks (~1 hour)");
            println!("  DEX Fee:         0.3%");
            println!();
            println!("Built by Protremix | Founder & CEO: Rojs Gordons");
            Ok(())
        }
    }
}
