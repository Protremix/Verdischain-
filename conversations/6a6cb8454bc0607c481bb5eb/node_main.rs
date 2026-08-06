//! Verdis Chain Node — Entry Point
//! BABE + GRANDPA full node

use std::sync::Arc;

use clap::Parser;
use sc_cli::{CliConfiguration, Result as CliResult, RunCmd, SubstrateCli};
use sc_service::{Configuration, TaskManager};

use verdis_runtime::Block;

mod chain_spec;
mod rpc;
mod service;

#[derive(Parser)]
#[command(
    name = "verdis",
    about = "Verdis Chain — The world's first fully green, carbon-negative blockchain",
    version = "2.0.0"
)]
struct Cli {
    #[command(subcommand)]
    subcommand: Subcommand,

    #[clap(flatten)]
    run: RunCmd,
}

#[derive(clap::Subcommand)]
enum Subcommand {
    /// Build chain specification
    BuildSpec(sc_cli::BuildSpecCmd),
    /// Export blocks
    ExportBlocks(sc_cli::ExportBlocksCmd),
    /// Import blocks
    ImportBlocks(sc_cli::ImportBlocksCmd),
    /// Revert chain
    Revert(sc_cli::RevertCmd),
    /// Remove whole chain data (database)
    PurgeChain(sc_cli::PurgeChainCmd),
    /// Export state
    ExportState(sc_cli::ExportStateCmd),
}

impl SubstrateCli for Cli {
    fn impl_name(&self) -> String {
        "Verdis Chain".into()
    }

    fn impl_version(&self) -> String {
        env!("CARGO_PKG_VERSION").into()
    }

    fn executable_name(&self) -> String {
        "verdis".into()
    }

    fn description(&self) -> String {
        env!("CARGO_PKG_DESCRIPTION").into()
    }

    fn author(&self) -> String {
        "Protremix".into()
    }

    fn support_url(&self) -> String {
        "https://verdischain.com".into()
    }

    fn copyright_start_year(&self) -> isize {
        2024
    }

    fn load_spec(&self, id: &str) -> CliResult<Box<dyn sc_service::ChainSpec>> {
        Ok(match id {
            "dev" => Box::new(chain_spec::development_config()?) as Box<_>,
            "" | "local" => Box::new(chain_spec::local_testnet_config()?) as Box<_>,
            path => {
                Box::new(chain_spec::ChainSpec::from_json_file(
                    std::path::PathBuf::from(path),
                )?) as Box<_>
            }
        })
    }

    fn native_runtime_version(&self) -> &'static sp_version::RuntimeVersion {
        &verdis_runtime::VERSION
    }
}

fn main() -> CliResult<()> {
    let cli = Cli::parse();

    match &cli.subcommand {
        Subcommand::BuildSpec(cmd) => cmd.run(&cli),
        Subcommand::ExportBlocks(cmd) => {
            let runner = cli.create_runner(cmd)?;
            runner.async_run(|config| {
                let (backend, _) = sc_service::new_full_parts::<
                    Block,
                    verdis_runtime::RuntimeApi,
                    sc_executor::NativeElseWasmExecutor<service::Executor>,
                >(&config, sc_executor::NativeElseWasmExecutor::new(config.wasm_method))?;
                Ok((cmd.run(backend.client()), backend.task_manager))
            })
        }
        Subcommand::ImportBlocks(cmd) => {
            let runner = cli.create_runner(cmd)?;
            runner.async_run(|config| {
                let (backend, _) = sc_service::new_full_parts::<
                    Block,
                    verdis_runtime::RuntimeApi,
                    sc_executor::NativeElseWasmExecutor<service::Executor>,
                >(&config, sc_executor::NativeElseWasmExecutor::new(config.wasm_method))?;
                Ok((cmd.run(backend.client()), backend.task_manager))
            })
        }
        Subcommand::Revert(cmd) => {
            let runner = cli.create_runner(cmd)?;
            runner.async_run(|config| {
                let (backend, _) = sc_service::new_full_parts::<
                    Block,
                    verdis_runtime::RuntimeApi,
                    sc_executor::NativeElseWasmExecutor<service::Executor>,
                >(&config, sc_executor::NativeElseWasmExecutor::new(config.wasm_method))?;
                Ok((cmd.run(backend.client(), backend.task_manager))
                    .map(|_| ((), backend.task_manager)))
            })
        }
        Subcommand::PurgeChain(cmd) => {
            let runner = cli.create_runner(cmd)?;
            runner.sync_run(|config| cmd.run(&config))
        }
        Subcommand::ExportState(cmd) => {
            let runner = cli.create_runner(cmd)?;
            runner.async_run(|config| {
                let (backend, _) = sc_service::new_full_parts::<
                    Block,
                    verdis_runtime::RuntimeApi,
                    sc_executor::NativeElseWasmExecutor<service::Executor>,
                >(&config, sc_executor::NativeElseWasmExecutor::new(config.wasm_method))?;
                Ok((cmd.run(backend.client(), backend.task_manager)?, backend.task_manager))
            })
        }
        None => {
            let runner = cli.create_runner(&cli.run)?;
            runner.run_node_until_exit(|config| async move {
                service::new_full(config)
                    .map(|(task_manager, _)| task_manager)
                    .map_err(Into::into)
            })
        }
    }
}
