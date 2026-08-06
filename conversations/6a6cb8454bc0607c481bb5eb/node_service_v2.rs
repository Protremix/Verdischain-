//! Verdis Chain Full Node Service
//!
//! BABE block production + GRANDPA finality + JSON-RPC

use std::sync::Arc;

use sc_client_api::{Backend, BlockBackend};
use sc_consensus_babe::{self, BabeBlockImport, BabeLink, BabeParams, SlotProportion};
use sc_consensus_grandpa::{
    self, FinalityProofProvider, GrandpaBlockImport, GrandpaParams,
    LinkHalf, SharedAuthoritySet, SharedVoterState,
};
use sc_executor::NativeElseWasmExecutor;
use sc_network::NetworkService;
use sc_network_sync::SyncingService;
use sc_service::{
    config::{DatabaseSource, RpcMethods},
    BuildNetworkParams, Configuration, NetworkStarter, PartialComponents, Role, TaskManager,
};
use sc_telemetry::{Telemetry, TelemetryWorker};
use sc_transaction_pool::{BasicPool, FullPool};
use sp_api::ProvideRuntimeApi;
use sp_blockchain::HeaderBackend;
use sp_consensus::{SelectChain};
use sp_consensus_babe::inherents::InherentDataProvider as BabeInherentDataProvider;
use sp_keyring::sr25519::Keyring as Sr25519Keyring;
use sp_keystore::KeystorePtr;
use sp_runtime::traits::{BlakeTwo256, Block as BlockT};

use verdis_runtime::{Block, Hash, AccountId, RuntimeApi, opaque::Block as OpaqueBlock};

pub type FullClient = sc_service::TFullClient<
    Block,
    RuntimeApi,
    NativeElseWasmExecutor<ExecutorDispatch>,
>;

pub type FullBackend = sc_service::TFullBackend<Block>;
pub type FullSelectChain = sc_consensus::LongestChain<FullBackend, Block>;

pub struct ExecutorDispatch;

impl sc_executor::NativeExecutionDispatch for ExecutorDispatch {
    #[cfg(feature = "runtime-benchmarks")]
    type ExtendHostFunctions = frame_benchmarking::benchmarking::HostFunctions;
    #[cfg(not(feature = "runtime-benchmarks"))]
    type ExtendHostFunctions = ();

    fn dispatch(info: sc_executor::RuntimeVersionInfo) -> &'static dyn sc_executor::NativeExecutionDispatch {
        use sc_executor::NativeExecutionDispatch as _;
        match info.spec_name {
            "verdis-runtime" => &ExecutorDispatch,
            _ => &ExecutorDispatch,
        }
    }
}

/// Creates partial components for the node
pub fn new_partial(
    config: &Configuration,
) -> Result<
    PartialComponents<
        FullClient,
        FullBackend,
        FullSelectChain,
        sc_consensus::DefaultImportQueue<Block, FullClient>,
        sc_transaction_pool::FullPool<Block, FullClient>,
        (
            BabeBlockImport<Block, FullClient, GrandpaBlockImport<FullBackend, Block, FullClient, FullSelectChain>>,
            BabeLink<Block>,
            LinkHalf<Block, FullClient, FullSelectChain>,
            Option<Telemetry>,
        ),
    >,
    sc_service::Error,
> {
    let telemetry = config
        .telemetry_endpoints
        .clone()
        .filter(|x| !x.is_empty())
        .map(|endpoints| -> Result<_, sc_service::Error> {
            let worker = TelemetryWorker::new(&endpoints)?;
            Ok(worker.handle())
        })
        .transpose()?;

    let (client, backend, keystore_container, task_manager) =
        sc_service::new_full_parts::<Block, RuntimeApi, _>(
            &config,
            NativeElseWasmExecutor::<ExecutorDispatch>::new(config.wasm_method),
        )?;

    let client = Arc::new(client);

    let select_chain = sc_consensus::LongestChain::new(backend.clone());

    let grandpa_block_import =
        sc_consensus_grandpa::block_import(client.clone(), &(client.clone(), backend.clone()), &select_chain)?;

    let (block_import, babe_link) = sc_consensus_babe::block_import(
        sc_consensus_babe::SlotDuration::from_millis(6000)?,
        sc_consensus_babe::ExpectedBlockTime::from_millis(6000),
        grandpa_block_import,
        client.clone(),
    )?;

    let import_queue = sc_consensus_babe::import_queue(
        babe_link.clone(),
        sc_consensus_babe::block_import(
            sc_consensus_babe::SlotDuration::from_millis(6000)?,
            sc_consensus_babe::ExpectedBlockTime::from_millis(6000),
            sc_consensus::DefaultImportQueueBlockImport::new(client.clone(), backend.clone()),
            client.clone(),
        )?.0,
        |_, _| async move {
            let timestamp = sp_timestamp::InherentDataProvider::from_system_time();
            let babe = BabeInherentDataProvider::from_seed_and_slot(
                sp_consensus_babe::SlotDuration::from_millis(6000)?,
                sp_consensus_babe::Slot::from(0),
            );
            Ok(sp_inherents::InherentData::new().create_inherent_from(timestamp, babe))
        },
        &task_manager.spawn_essential_handle(),
        config.role.is_authority(),
    )?;

    let transaction_pool = BasicPool::new_full(
        config.transaction_pool.clone(),
        config.role.is_authority(),
        config.prometheus_registry(),
        task_manager.spawn_essential_handle(),
        client.clone(),
    );

    let partial = PartialComponents {
        client,
        backend,
        task_manager,
        import_queue,
        keystore_container,
        select_chain,
        transaction_pool,
        other: (block_import, babe_link, grandpa_link, telemetry),
    };

    Ok(partial)
}

/// Builds and starts the full node service
#[allow(clippy::too_many_arguments)]
pub fn new_full(
    config: Configuration,
) -> Result<(TaskManager, Arc<FullClient>), sc_service::Error> {
    let sc_service::PartialComponents {
        client,
        backend,
        mut task_manager,
        import_queue,
        keystore_container,
        select_chain,
        transaction_pool,
        other: (block_import, babe_link, grandpa_link, mut telemetry),
    } = new_partial(&config)?;

    // Setup dev keystore
    if config.role.is_authority() {
        let keystore = keystore_container.local_keystore();
        // Insert Alice's keys for dev mode
        for keyring in [Sr25519Keyring::Alice, Sr25519Keyring::Bob, Sr25519Keyring::Charlie] {
            let _ = sp_consensus_babe::BabeKeyring::from(keyring).insert_into(keystore.clone());
        }
    }

    let grandpa_protocol_name = sc_consensus_grandpa::protocol_standard_name(
        &client.block_hash(0).ok().flatten().expect("Genesis block exists"),
        &config.chain_spec,
    );

    let grandpa_config = sc_consensus_grandpa::Config {
        protocol_name: grandpa_protocol_name,
        keystore: keystore_container.local_keystore(),
        observer_enabled: config.role.is_authority(),
    };

    let (network, system_rpc_tx, tx_handler, network_starter) =
        sc_service::build_network(sc_service::BuildNetworkParams {
            config: &config,
            client: client.clone(),
            transaction_pool: pool.clone(),
            spawn_handle: task_manager.spawn_essential_handle(),
            import_queue: import_queue.into(),
            block_announce_validator_builder: None,
            warpers: None,
        })?;

    // Start GRANDPA voter
    if config.role.is_authority() {
        let grandpa_voter = sc_consensus_grandpa::run_grandpa_voter(
            grandpa_config,
            grandpa_link,
            network.clone(),
            client.clone(),
            select_chain.clone(),
            task_manager.spawn_essential_handle(),
            telemetry.as_mut(),
        )?;
        task_manager.spawn_essential_handle().spawn("grandpa-voter", grandpa_voter);
    }

    // Start BABE worker
    if config.role.is_authority() {
        let babe_worker = sc_consensus_babe::start_babe(
            sc_consensus_babe::BabeParams {
                keystore: keystore_container.local_keystore(),
                client: client.clone(),
                select_chain: select_chain.clone(),
                block_import: block_import.clone(),
                sync_oracle: network.clone(),
                justification_sync_link: network.clone(),
                creation_inherent_data: |_, _| async move {
                    let timestamp = sp_timestamp::InherentDataProvider::from_system_time();
                    let babe = BabeInherentDataProvider::from_seed_and_slot(
                        sc_consensus_babe::SlotDuration::from_millis(6000)?,
                        sc_consensus_babe::Slot::from(0),
                    );
                    Ok(sp_inherents::InherentData::new().create_inherent_from(timestamp, babe))
                },
                babe_link: babe_link.clone(),
                block_proposal_slot_portion: SlotProportion::new(0.5),
                max_block_proposal_slot_portion: None,
                telemetry: telemetry.as_mut(),
            },
        )?;
        task_manager.spawn_essential_handle().spawn("babe", babe_worker);
    }

    // Setup RPC
    let rpc_extensions_builder = {
        let client = client.clone();
        let pool = transaction_pool.clone();
        Box::new(move |deny_unsafe, _| {
            let deps = crate::rpc::FullDeps {
                client: client.clone(),
                pool: pool.clone(),
                deny_unsafe,
            };
            crate::rpc::create_full(deps).map_err(Into::into)
        })
    };

    let _rpc_handlers = sc_service::spawn_tasks(sc_service::SpawnTasksParams {
        config: &config,
        client: client.clone(),
        backend: backend.clone(),
        task_manager: &mut task_manager,
        network: network.clone(),
        sync_service: network.clone(),
        system_rpc_tx,
        tx_handler,
        rpc_extensions_builder,
        telemetry: telemetry.as_mut(),
    })?;

    network_starter.start_network();

    Ok((task_manager, client))
}
