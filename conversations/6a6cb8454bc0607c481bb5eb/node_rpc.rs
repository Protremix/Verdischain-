//! Verdis Chain RPC
//! Standard Substrate RPC + BABE + GRANDPA

use std::sync::Arc;

use jsonrpsee::RpcModule;
use sc_client_api::{AuxStore, BlockBackend};
use sc_consensus_babe_rpc::BabeRpcHandler;
use sc_consensus_grandpa_rpc::GrandpaRpcHandler;
use sc_rpc_api::DenyUnsafe;
use sp_api::ProvideRuntimeApi;
use sp_blockchain::{HeaderBackend, Metadata, Error as BlockChainError};
use sp_consensus::SelectChain;
use sp_consensus_babe::BabeApi;
use sp_consensus_grandpa::StorageProvider;
use sp_runtime::traits::Block as BlockT;
use substrate_frame_rpc_system::SystemApi;
use pallet_transaction_payment_rpc::TransactionPaymentApi;

use verdis_runtime::{Block, BlockNumber};

pub struct FullDeps<C, P, B> {
    pub client: Arc<C>,
    pub pool: P,
    pub backend: B,
    pub deny_unsafe: DenyUnsafe,
}

pub fn create_full<C, P, B>(
    deps: FullDeps<C, P, B>,
) -> Result<RpcModule<()>, Box<dyn std::error::Error + Send + Sync>>
where
    C: ProvideRuntimeApi<Block>
        + HeaderBackend<Block>
        + AuxStore
        + BlockBackend<Block>
        + Metadata<Block>
        + Send
        + Sync
        + 'static,
    C::Api: SystemApi<Block, BlockNumber>
        + TransactionPaymentApi<Block, u128>
        + BabeApi<Block>,
    P: sc_transaction_pool_api::LocalTransactionPool<Block> + Send + Sync + 'static,
    B: StorageProvider<Block, C> + Send + Sync + 'static,
{
    let mut io = RpcModule::new(());
    let FullDeps { client, pool, backend, deny_unsafe } = deps;

    // System RPC
    let system = substrate_frame_rpc_system::System::new(
        client.clone(),
        pool.clone(),
        deny_unsafe,
    );
    io.merge(system.into_rpc())?;

    // Transaction Payment RPC
    let tx_payment = pallet_transaction_payment_rpc::TransactionPayment::new(
        client.clone(),
    );
    io.merge(tx_payment.into_rpc())?;

    // BABE RPC
    let babe = BabeRpcHandler::new(client.clone(), deny_unsafe);
    io.merge(babe.into_rpc())?;

    // GRANDPA RPC
    let grandpa = GrandpaRpcHandler::new(client, backend, deny_unsafe);
    io.merge(grandpa.into_rpc())?;

    Ok(io)
}
