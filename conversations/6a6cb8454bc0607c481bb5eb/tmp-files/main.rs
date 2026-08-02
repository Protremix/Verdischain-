//! Verdis Chain Node — Entry Point
//!
//! Architecture: BABE (block production) + GRANDPA (finality)
//! APIs: JSON-RPC + gRPC
//! Chain ID: 909

use std::path::PathBuf;

use clap::Parser;
use sc_cli::{SubstrateCli, RuntimeVersion, ChainSpec, CliConfiguration};
use sc_service::{Configuration, TaskManager};

use verdis_runtime::VERSION;

mod chain_spec;
mod service;

#[derive(Debug, Parser)]
#[command(
    name = "verdis",
    about = "Verdis Chain — The world's first fully green, carbon-negative blockchain",
    version = "2.0.0"
)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Subcommand,

    #[arg(long, default_value = "verdis-testnet")]
    pub name: String,

    #[arg(long)]
    pub chain: Option<PathBuf>,

    #[arg(long, default_value = "30333")]
    pub port: u16,

    #[arg(long, default_value = "9933")]
    pub rpc_port: u16,

    #[arg(long, default_value = "9090")]
    pub grpc_port: u16,

    #[arg(long)]
    pub validator: bool,

    #[arg(long)]
    pub dev: bool,

    #[arg(long)]
    pub tmp: bool,
}

#[derive(Debug, clap::Subcommand)]
pub enum Subcommand {
    /// Build chain specification
    BuildSpec {
        #[arg(long)]
        raw: bool,
        #[arg(long)]
        chain: Option<PathBuf>,
    },
    /// Show node info
    Info,
    /// Run the node (default if no subcommand given)
    Run,
}

impl SubstrateCli for Cli {
    fn impl_name() -> String { "Verdis Chain".to_string() }
    fn impl_version() -> String { "2.0.0".to_string() }
    fn description() -> String { "The world's first fully green, carbon-negative blockchain".to_string() }
    fn support_url() -> String { "https://verdischain.com".to_string() }
    fn copyright_start_year() -> i32 { 2024 }
    fn native_runtime_version() -> RuntimeVersion { VERSION.clone() }
    fn runtime_version() -> RuntimeVersion { VERSION.clone() }
}

fn main() -> sc_cli::Result<()> {
    let cli = Cli::parse();

    match &cli.command {
        Subcommand::Info => {
            print_node_info();
            Ok(())
        }
        Subcommand::BuildSpec { raw, chain } => {
            let spec = chain_spec::VerdisChainSpec::chain_spec();
            let json = serde_json::to_string_pretty(&spec).unwrap();
            println!("{}", json);
            Ok(())
        }
        Subcommand::Run => {
            run_node(cli)
        }
    }
}

fn run_node(cli: Cli) -> sc_cli::Result<()> {
    println!("🌿 Verdis Chain v2.0.0 — Starting node...");
    println!("   Consensus: BABE + GRANDPA");
    println!("   Chain ID: 909");
    println!("   P2P Port: {}", cli.port);
    println!("   JSON-RPC Port: {}", cli.rpc_port);
    println!("   gRPC Port: {}", cli.grpc_port);
    println!("   Validator: {}", if cli.validator { "Yes" } else { "No" });
    println!();

    let chain_spec = chain_spec::VerdisChainSpec::chain_spec();

    let config = Configuration {
        impl_name: "Verdis Chain".to_string(),
        impl_version: "2.0.0".to_string(),
        role: if cli.validator {
            sc_service::Role::Authority
        } else {
            sc_service::Role::Full
        },
        chain_spec,
        network: sc_service::config::NetworkConfiguration {
            listen_addresses: vec![format!("/ip4/0.0.0.0/tcp/{}", cli.port).parse().unwrap()],
            public_addresses: vec![],
            boot_nodes: vec![],
            node_name: cli.name,
            ..Default::default()
        },
        database: sc_service::config::DatabaseConfiguration::RocksDb {
            path: if cli.tmp {
                std::env::temp_dir().join("verdis-db")
            } else {
                PathBuf::from("./data/verdis-db")
            },
            cache_size: 1024,
        },
        keystore: if cli.dev {
            sc_service::config::KeystoreConfig::InMemory
        } else {
            sc_service::config::KeystoreConfig::Path {
                path: PathBuf::from("./data/keystore"),
                password: None,
            }
        },
        rpc_addr: Some(([0, 0, 0, 0], cli.rpc_port).into()),
        rpc_methods: sc_service::config::RpcMethods::Full,
        offchain_worker: sc_service::config::OffchainWorkerConfig {
            enabled: false,
            ..Default::default()
        },
        force_authoring: false,
        prometheus_config: Some(sc_service::config::PrometheusConfiguration {
            port: 9615,
            registry: sc_service::config::Registry::default(),
            external_url: None,
        }),
        telemetry_endpoints: vec![],
        ..Default::default()
    };

    let task_manager = service::new_full(config)?;
    println!("✅ Node started successfully!");
    println!("   BABE block production: Active");
    println!("   GRANDPA finality: Active");
    println!();

    task_manager.future().await;
    Ok(())
}

fn print_node_info() {
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
}
