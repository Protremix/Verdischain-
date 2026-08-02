use std::sync::Arc;
use std::time::Duration;

use clap::Parser;
use sc_cli::SubstrateCli;
use sc_service::PartialComponents;

#[derive(Parser)]
#[command(
    name = "verdis",
    about = "Verdis Chain — The world's first fully green, carbon-negative blockchain",
    version
)]
struct Cli {
    #[command(subcommand)]
    subcommand: SubCmd,
}

#[derive(Subcommand)]
enum SubCmd {
    /// Run the Verdis node
    Run(sc_cli::RunCmd),
    /// Build chain specification
    BuildSpec(sc_cli::BuildSpecCmd),
    /// Export blocks
    ExportBlocks(sc_cli::ExportBlocksCmd),
    /// Import blocks
    ImportBlocks(sc_cli::ImportBlocksCmd),
    /// Revert chain
    Revert(sc_cli::RevertCmd),
    /// Remove chain data
    PurgeChain(sc_cli::PurgeChainCmd),
}

fn main() -> sc_cli::Result<()> {
    let cli = Cli::parse();

    match cli.subcommand {
        SubCmd::Run(run_cmd) => {
            let runner = run_cmd.create_runner(&sc_cli::RunnerConfig {
                chain_spec: None,
                base_path: None,
            })?;

            runner.run_node(
                |config| {
                    let service = verdis_service::new_partial(config)?;
                    Ok(Arc::new(service))
                },
                |config| {
                    let service = verdis_service::new_full(config)?;
                    Ok(Arc::new(service))
                },
                "verdis-chain",
            )
        }
        SubCmd::BuildSpec(cmd) => cmd.run(&verdis_chain_spec::VerdisChainSpec::chain_spec()),
        SubCmd::ExportBlocks(cmd) => cmd.run(
            verdis_chain_spec::VerdisChainSpec::chain_spec(),
            |config| {
                let PartialComponents { client, .. } = verdis_service::new_partial(&config)?;
                Ok(Arc::new(client))
            },
        ),
        SubCmd::ImportBlocks(cmd) => cmd.run(
            verdis_chain_spec::VerdisChainSpec::chain_spec(),
            |config| {
                let PartialComponents { client, task_manager, .. } = verdis_service::new_partial(&config)?;
                Ok((Arc::new(client), task_manager))
            },
        ),
        SubCmd::Revert(cmd) => cmd.run(
            verdis_chain_spec::VerdisChainSpec::chain_spec(),
            |config| {
                let PartialComponents { client, backend, .. } = verdis_service::new_partial(&config)?;
                Ok((Arc::new(client), backend))
            },
        ),
        SubCmd::PurgeChain(cmd) => cmd.run(
            verdis_chain_spec::VerdisChainSpec::chain_spec(),
            |config| {
                let PartialComponents { backend, .. } = verdis_service::new_partial(&config)?;
                Ok(backend)
            },
        ),
    }
}
