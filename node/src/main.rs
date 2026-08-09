//! Verdis Chain — CLI Entry Point (Substrate v48)

#![allow(deprecated, unused_imports, unused_variables, clippy::all, dead_code)]
mod chain_spec;
mod service;

use clap::Parser;
use sc_cli::{RunCmd, SubstrateCli};
use sc_service::ChainSpec;

use chain_spec::{load_spec, VerdisChainSpec};
use service::ExecutorDispatch;
use verdis_runtime::opaque::Block;

#[derive(Parser)]
#[command(
    name = "verdis",
    author = "Rojs Gordons <rojs@verdischain.com>",
    version,
    about = "Verdis — The world's first fully green, carbon-negative blockchain ecosystem",
    long_about = None,
    propagate_version = true,
    args_conflicts_with_subcommands = true,
    subcommand_negates_reqs = true,
)]
struct Cli {
    #[command(subcommand)]
    subcommand: Option<Subcommand>,
    #[clap(flatten)]
    run: RunCmd,
}

#[derive(Debug, clap::Subcommand)]
enum Subcommand {
    /// Key management
    Key {
        #[command(subcommand)]
        subcommand: sc_cli::KeySubcommand,
    },
    /// Build a chain spec
    BuildSpec(#[command(flatten)] sc_cli::BuildSpecCmd),
    /// Chain info
    ChainInfo(#[command(flatten)] sc_cli::ChainInfoCmd),
    /// Purge chain
    PurgeChain(#[command(flatten)] sc_cli::PurgeChainCmd),
}

impl SubstrateCli for Cli {
    fn impl_name() -> String {
        "Verdis Chain".into()
    }
    fn impl_version() -> String {
        env!("CARGO_PKG_VERSION").into()
    }
    fn description() -> String {
        "Verdis — The world's first fully green, carbon-negative blockchain ecosystem".into()
    }
    fn author() -> String {
        "Rojs Gordons <rojs@verdischain.com>".into()
    }
    fn support_url() -> String {
        "https://verdischain.com".into()
    }
    fn copyright_start_year() -> i32 {
        2024
    }
    fn load_spec(&self, id: &str) -> Result<Box<dyn ChainSpec>, String> {
        Ok(Box::new(load_spec(id)))
    }
}

fn main() -> sc_cli::Result<()> {
    let cli = Cli::from_args();

    match &cli.subcommand {
        Some(Subcommand::Key { subcommand }) => subcommand.run(&cli),
        Some(Subcommand::BuildSpec(cmd)) => {
            let runner = cli.create_runner(cmd)?;
            runner.sync_run(|config| cmd.run(config.chain_spec, config.network))
        }
        Some(Subcommand::ChainInfo(cmd)) => {
            let runner = cli.create_runner(cmd)?;
            runner.sync_run(|config| cmd.run::<Block>(&config))
        }
        Some(Subcommand::PurgeChain(cmd)) => {
            let runner = cli.create_runner(cmd)?;
            runner.sync_run(|config| cmd.run(config.database))
        }
        None => {
            let runner = cli.create_runner(&cli.run)?;
            runner.run_node_until_exit(|config| async move {
                service::new_full::<
                    sc_network::service::NetworkWorker<
                        Block,
                        <Block as sp_runtime::traits::Block>::Hash,
                    >,
                >(config)
                .map_err(|e| e.into())
            })
        }
    }
}
