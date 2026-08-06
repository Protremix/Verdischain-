//! Verdis Chain RPC
//! Standard Substrate RPC (System + Transaction Payment)

use std::sync::Arc;

use jsonrpsee::RpcModule;
use sc_client_api::AuxStore;
use sc_rpc_api::DenyUnsafe;
use sp_api::ProvideRuntimeApi;
use sp_blockchain::{HeaderBackend, Error as BlockChainError};
use sp_runtime::traits::Block as BlockT;
use substrate_frame_rpc_system::SystemApi;
use pallet_transaction_payment_rpc::TransactionPaymentApi;

use verdis_runtime::{Block, BlockNumber};

pub struct FullDeps<C, P> {
    pub client: Arc<C>,
    pub pool: P,
    pub deny_unsafe: DenyUnsafe,
}

pub fn create_full<C, P>(
    deps: FullDeps<C, P>,
) -> Result<RpcModule<()>, Box<dyn std::error::Error + Send + Sync>>
where
    C: ProvideRuntimeApi<Block>
        + HeaderBackend<Block>
        + AuxStore
        + Send
        + Sync
        + 'static,
    C::Api: SystemApi<Block, BlockNumber>
        + TransactionPaymentApi<Block, u128>,
    P: sc_transaction_pool_api::LocalTransactionPool<Block> + Send + Sync + 'static,
{
    let mut io = RpcModule::new(());
    let FullDeps { client, pool, deny_unsafe } = deps;

    // System RPC
    let system = substrate_frame_rpc_system::System::new(
        client.clone(),
        pool,
        deny_unsafe,
    );
    io.merge(system.into_rpc())?;

    // Transaction Payment RPC
    let tx_payment = pallet_transaction_payment_rpc::TransactionPayment::new(
        client,
    );
    io.merge(tx_payment.into_rpc())?;

    Ok(io)
}
