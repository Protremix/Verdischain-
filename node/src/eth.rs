//! Frontier (EVM) node-side plumbing.
//!
//! Kept separate so the EVM additions to the node are reviewable in isolation.
//!
//! IMPORTANT typing note: `crate::service::FullClient` is itself an `Arc<...>`. Every Frontier
//! API takes `Arc<C>` where C is the BARE client type, so this module uses `BareClient` for the
//! generic parameter and keeps each `Arc` explicit. Passing `FullClient` where `C` is expected
//! yields `Arc<Arc<Client>>`, which fails a pile of trait bounds (HeaderBackend,
//! BlockchainEvents, ProvideRuntimeApi) in a way that looks like missing impls but is not.
//!
//! Deliberately NOT included:
//!   * EthPubSub (eth_subscribe) - needs a subscription executor; MetaMask does not require it
//!   * EthDevSigner - would let the NODE sign with dev keys; unacceptable with real balances

use std::{collections::BTreeMap, path::PathBuf, sync::Arc, time::Duration};

use futures::StreamExt;
use sc_client_api::BlockchainEvents;
use sc_service::{Configuration, TaskManager};
use sc_transaction_pool_api::TransactionPool;
use verdis_runtime::opaque::Block;

pub use fc_rpc::{EthTask, StorageOverrideHandler};
pub use fc_rpc_core::types::{FeeHistoryCache, FeeHistoryCacheLimit, FilterPool};

use crate::service::{ExecutorDispatch, FullBackend};

/// The BARE client type - `service::FullClient` is this wrapped in an Arc.
pub type BareClient = sc_service::TFullClient<
    Block,
    verdis_runtime::RuntimeApi,
    sc_executor::NativeElseWasmExecutor<ExecutorDispatch>,
>;

pub type FrontierBackend = fc_db::kv::Backend<Block, BareClient>;

/// Frontier keeps its own database beside the substrate one.
pub fn db_config_dir(config: &Configuration) -> PathBuf {
    config.base_path.config_dir(config.chain_spec.id())
}

/// Shared state the eth RPC handlers need.
pub struct FrontierPartial {
    pub filter_pool: FilterPool,
    pub fee_history_cache: FeeHistoryCache,
    pub fee_history_cache_limit: FeeHistoryCacheLimit,
}

pub fn new_frontier_partial() -> FrontierPartial {
    FrontierPartial {
        filter_pool: Arc::new(std::sync::Mutex::new(BTreeMap::new())),
        fee_history_cache: Arc::new(std::sync::Mutex::new(BTreeMap::new())),
        // Bounded so a long-running node cannot grow this cache without limit.
        fee_history_cache_limit: 2048,
    }
}

/// Open (or create) the Frontier KV backend, following the node's OWN database choice.
///
/// `Backend::open` mirrors whatever `--database` the node was started with; hardcoding a source
/// here would bolt a rocksdb ethereum index onto a paritydb node, and picking a variant whose
/// cargo feature is not enabled fails at RUNTIME with "Supported db sources: ...", not at compile
/// time.
pub fn open_frontier_backend(
    client: Arc<BareClient>,
    config: &Configuration,
) -> Result<FrontierBackend, String> {
    fc_db::kv::Backend::<Block, BareClient>::open(client, &config.database, &db_config_dir(config))
}

/// Spawn the tasks that keep the ethereum view of the chain current.
///
/// The mapping worker is ESSENTIAL: if it stops, eth_getBlockByNumber would keep answering with
/// stale data rather than failing, which is worse than the node going down.
#[allow(clippy::too_many_arguments)]
pub fn spawn_frontier_tasks(
    task_manager: &TaskManager,
    client: Arc<BareClient>,
    substrate_backend: Arc<FullBackend>,
    frontier_backend: Arc<FrontierBackend>,
    filter_pool: FilterPool,
    storage_override: Arc<dyn fc_storage::StorageOverride<Block>>,
    fee_history_cache: FeeHistoryCache,
    fee_history_cache_limit: FeeHistoryCacheLimit,
    sync_oracle: Arc<dyn sp_consensus::SyncOracle + Send + Sync>,
    pubsub_notification_sinks: Arc<
        fc_mapping_sync::EthereumBlockNotificationSinks<
            fc_mapping_sync::EthereumBlockNotification<Block>,
        >,
    >,
    state_pruning_blocks: Option<u64>,
) {
    task_manager.spawn_essential_handle().spawn(
        "frontier-mapping-sync-worker",
        Some("frontier"),
        fc_mapping_sync::kv::MappingSyncWorker::new(
            client.import_notification_stream(),
            Duration::new(6, 0),
            client.clone(),
            substrate_backend,
            storage_override.clone(),
            frontier_backend,
            3,
            // VERDIS: sync_from. Passing 0 makes the worker index from genesis, but a chain that was
            // UPGRADED into the EVM has no Ethereum blocks before the activation height, and its
            // genesis state is usually pruned - the worker then never advances and eth_blockNumber
            // stays 0 while `latest` resolves to genesis and fails with
            // UnknownBlock("State already discarded"). Queries by explicit block number still work,
            // which is how this was diagnosed.
            //
            // Read the activation height from the environment so one binary serves all networks:
            // a fresh/dev chain leaves it unset (0, unchanged behaviour), an upgraded chain sets it
            // to the block where spec with the EVM went live.
            std::env::var("VERDIS_EVM_SYNC_FROM")
                .ok()
                .and_then(|v| v.parse::<u32>().ok())
                .unwrap_or(0)
                .into(),
            state_pruning_blocks,
            fc_mapping_sync::SyncStrategy::Normal,
            sync_oracle,
            pubsub_notification_sinks,
        )
        .for_each(|()| futures::future::ready(())),
    );

    // Prune stale eth_newFilter subscriptions.
    const FILTER_RETAIN_THRESHOLD: u64 = 100;
    task_manager.spawn_essential_handle().spawn(
        "frontier-filter-pool",
        Some("frontier"),
        EthTask::filter_pool_task(client.clone(), filter_pool, FILTER_RETAIN_THRESHOLD),
    );

    task_manager.spawn_essential_handle().spawn(
        "frontier-fee-history",
        Some("frontier"),
        EthTask::fee_history_task(
            client,
            storage_override,
            fee_history_cache,
            fee_history_cache_limit,
        ),
    );
}

/// Unused-import guard: TransactionPool is needed by callers of this module's RPC assembly.
#[allow(dead_code)]
fn _assert_pool_trait_in_scope<P: TransactionPool>() {}
