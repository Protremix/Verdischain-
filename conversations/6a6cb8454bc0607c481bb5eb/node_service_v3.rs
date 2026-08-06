//! Verdis Chain Full Node Service
//! BABE block production + GRANDPA finality

use std::sync::Arc;

use sc_basic_authorship::ProposerFactory;
use sc_client_api::{Backend, BlockBackend};
use sc_consensus_babe::{self, BabeBlockImport, BabeLink, SlotProportion};
use sc_consensus_grandpa::{self, GrandpaBlockImport, LinkHalf};
use sc_executor::NativeElseWasmExecutor;
use sc_service::{
    BuildNetworkParams, Configuration, PartialComponents, TaskManager,
};
use sc_telemetry::{Telemetry, TelemetryWorker};
use sc_transaction_pool::BasicPool;
use sp_consensus::SelectChain;
use sp_keystore::KeystorePtr;
use sp_runtime::traits::Block as BlockT;

use verdis_runtime::{
    opaque::Block as OpaqueBlock,
    Block, RuntimeApi,
};

pub type FullClient = sc_service::TFullClient<
    Block,
    RuntimeApi,
    NativeElseWasmExecutor<Executor>,
>;

pub type FullBackend = sc_service::TFullBackend<Block>;
pub type FullSelectChain = sc_consensus::LongestChain<FullBackend, Block>;

pub struct Executor;

impl sc_executor::NativeExecutionDispatch for Executor {
    #[cfg(feature = "runtime-benchmarks")]
    type ExtendHostFunctions = frame_benchmarking::benchmarking::HostFunctions;
    #[cfg(not(feature = "runtime-benchmarks"))]
    type ExtendHostFunctions = ();

    fn dispatch(_info: sc_executor::RuntimeVersionInfo) -> &'static dyn sc_executor::NativeExecutionDispatch {
        &Executor
    }
}

type GrandpaBlockImportType = GrandpaBlockImport<
    FullBackend,
    Block,
    FullClient,
    FullSelectChain,
>;

type BabeBlockImportType = BabeBlockImport<
    Block,
    FullClient,
    GrandpaBlockImportType,
>;

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
            BabeBlockImportType,
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
            NativeElseWasmExecutor::<Executor>::new(config.wasm_method),
        )?;

    let client = Arc::new(client);

    let select_chain = sc_consensus::LongestChain::new(backend.clone());

    let grandpa_block_import = sc_consensus_grandpa::block_import(
        client.clone(),
        &(client.clone(), backend.clone()),
        select_chain.clone(),
    )?;

    let slot_duration = sc_consensus_babe::SlotDuration::from_millis(6000)?;
    let expected_block_time = sc_consensus_babe::ExpectedBlockTime::from_millis(6000);

    let (block_import, babe_link) = sc_consensus_babe::block_import(
        slot_duration,
        expected_block_time,
        grandpa_block_import,
        client.clone(),
    )?;

    let import_queue = sc_consensus_babe::import_queue(
        babe_link.clone(),
        block_import.clone(),
        |_, _| async move {
            let timestamp = sp_timestamp::InherentDataProvider::from_system_time();
            let slot = sp_consensus_babe::inherents::InherentDataProvider::from_timestamp_and_slot_duration(
                timestamp.0,
                sc_consensus_babe::SlotDuration::from_millis(6000)?,
            );
            let inherent_data = sp_inherents::InherentData::new()
                .put_data(sp_timestamp::INHERENT_IDENTIFIER, &timestamp)
                .put_data(sp_consensus_babe::inherents::INHERENT_IDENTIFIER, &slot)?;
            Ok(inherent_data)
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

    let grandpa_link = sc_consensus_grandpa::LinkHalf::new(
        client.clone(),
        &(client.clone(), backend.clone()),
        select_chain.clone(),
    );

    Ok(PartialComponents {
        client,
        backend,
        task_manager,
        import_queue,
        keystore_container,
        select_chain,
        transaction_pool,
        other: (block_import, babe_link, grandpa_link, telemetry),
    })
}

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
        sc_service::build_network(BuildNetworkParams {
            config: &config,
            client: client.clone(),
            transaction_pool: transaction_pool.clone(),
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
            sync_oracle: network.clone(),
            client.clone(),
            select_chain.clone(),
            task_manager.spawn_essential_handle(),
            telemetry.as_mut(),
        )?;
        task_manager.spawn_essential_handle().spawn("grandpa-voter", grandpa_voter);
    }

    // Start BABE worker
    if config.role.is_authority() {
        let proposer = ProposerFactory::new(
            task_manager.spawn_essential_handle(),
            client.clone(),
            transaction_pool.clone(),
            None,
            None,
            telemetry.as_mut(),
        );

        let babe_worker = sc_consensus_babe::start_babe(sc_consensus_babe::BabeParams {
            keystore: keystore_container.local_keystore(),
            client: client.clone(),
            select_chain: select_chain.clone(),
            block_import: block_import.clone(),
            sync_oracle: network.clone(),
            justification_sync_link: network.clone(),
            creation_inherent_data: |_, _| async move {
                let timestamp = sp_timestamp::InherentDataProvider::from_system_time();
                let slot = sp_consensus_babe::inherents::InherentDataProvider::from_timestamp_and_slot_duration(
                    timestamp.0,
                    sc_consensus_babe::SlotDuration::from_millis(6000)?,
                );
                let inherent_data = sp_inherents::InherentData::new()
                    .put_data(sp_timestamp::INHERENT_IDENTIFIER, &timestamp)
                    .put_data(sp_consensus_babe::inherents::INHERENT_IDENTIFIER, &slot)?;
                Ok(inherent_data)
            },
            babe_link: babe_link.clone(),
            block_proposal_slot_portion: SlotProportion::new(0.5),
            max_block_proposal_slot_portion: None,
            proposer,
            telemetry: telemetry.as_mut(),
        })?;
        task_manager.spawn_essential_handle().spawn("babe", babe_worker);
    }

    // Setup RPC
    let rpc_extensions_builder = {
        let client = client.clone();
        let pool = transaction_pool.clone();
        let backend = backend.clone();
        Box::new(move |deny_unsafe, _| {
            let deps = crate::rpc::FullDeps {
                client: client.clone(),
                pool: pool.clone(),
                backend: backend.clone(),
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
