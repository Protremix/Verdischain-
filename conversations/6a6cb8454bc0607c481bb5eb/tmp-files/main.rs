//! Verdis Chain — CLI Entry Point (Substrate v48)

use clap::Parser;
use sc_cli::{RunCmd, SubstrateCli};
use sc_service::ChainSpec;

use verdis_chain::chain_spec::VerdisChainSpec;
use verdis_chain::service;

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
    Key(sc_cli::KeySubcommand),
    /// Build a chain spec
    BuildSpec(sc_cli::BuildSpecCmd),
    /// Chain info
    ChainInfo(sc_cli::ChainInfoCmd),
    /// Purge chain
    PurgeChain(sc_cli::PurgeChainCmd),
    /// Export blocks
    ExportBlocks(sc_cli::ExportBlocksCmd),
    /// Import blocks
    ImportBlocks(sc_cli::ImportBlocksCmd),
    /// Check blocks
    CheckBlock(sc_cli::CheckBlockCmd),
    /// Revert chain
    Revert(sc_cli::RevertCmd),
    /// Export chain state
    ExportState(sc_cli::ExportStateCmd),
}

impl SubstrateCli for Cli {
    fn impl_name() -> String { "Verdis Chain".into() }
    fn impl_version() -> String { env!("CARGO_PKG_VERSION").into() }
    fn description() -> String {
        "Verdis — The world's first fully green, carbon-negative blockchain ecosystem".into()
    }
    fn author() -> String { "Rojs Gordons <rojs@verdischain.com>".into() }
    fn support_url() -> String { "https://verdischain.com".into() }
    fn copyright_start_year() -> i32 { 2024 }
    fn load_spec(&self, _id: &str) -> Result<Box<dyn ChainSpec>, String> {
        Ok(Box::new(VerdisChainSpec::chain_spec()))
    }
}

fn main() -> sc_cli::Result<()> {
    let cli = Cli::from_args();

    match &cli.subcommand {
        Some(Subcommand::Key(cmd)) => {
            let runner = cli.create_runner(cmd)?;
            runner.sync_run(|config| cmd.run(config))
        }
        Some(Subcommand::BuildSpec(cmd)) => {
            let runner = cli.create_runner(cmd)?;
            runner.sync_run(|config| cmd.run(&config.chain_spec, config.network))
        }
        Some(Subcommand::ChainInfo(cmd)) => {
            let runner = cli.create_runner(cmd)?;
            runner.sync_run(|config| cmd.run::<verdis_runtime::opaque::Block>(&config))
        }
        Some(Subcommand::PurgeChain(cmd)) => {
            let runner = cli.create_runner(cmd)?;
            runner.sync_run(|config| cmd.run(config.database))
        }
        Some(Subcommand::ExportBlocks(cmd)) => {
            let runner = cli.create_runner(cmd)?;
            runner.async_run(|config| {
                let (client, _, _, task_manager) = service::new_partial(&config)?;
                let (future, task_manager) = cmd.run(client, config.database, task_manager)?;
                Ok((future, task_manager))
            })
        }
        Some(Subcommand::ImportBlocks(cmd)) => {
            let runner = cli.create_runner(cmd)?;
            runner.async_run(|config| {
                let (client, _, _, task_manager) = service::new_partial(&config)?;
                let (future, task_manager) = cmd.run(client, config.database, task_manager)?;
                Ok((future, task_manager))
            })
        }
        Some(Subcommand::CheckBlock(cmd)) => {
            let runner = cli.create_runner(cmd)?;
            runner.async_run(|config| {
                let (client, _, _, task_manager) = service::new_partial(&config)?;
                let (future, task_manager) = cmd.run(client, task_manager)?;
                Ok((future, task_manager))
            })
        }
        Some(Subcommand::Revert(cmd)) => {
            let runner = cli.create_runner(cmd)?;
            runner.async_run(|config| {
                let (client, backend, _, task_manager) = service::new_partial(&config)?;
                let (future, task_manager) = cmd.run(client, backend, task_manager)?;
                Ok((future, task_manager))
            })
        }
        Some(Subcommand::ExportState(cmd)) => {
            let runner = cli.create_runner(cmd)?;
            runner.async_run(|config| {
                let (client, _, _, task_manager) = service::new_partial(&config)?;
                let (future, task_manager) = cmd.run(client, config.chain_spec, task_manager)?;
                Ok((future, task_manager))
            })
        }
        None => {
            let runner = cli.create_runner(&cli.run)?;
            runner.run_node_until_exit(|config| async move {
                service::new_full(config).map_err(sc_cli::Error::Service)
            })
        }
    }
}
