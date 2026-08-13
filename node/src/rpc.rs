//! AmmDex RPC module — exposes pool queries via JSON-RPC

use jsonrpsee::core::RpcResult;
use jsonrpsee::proc_macros::rpc;
use jsonrpsee::types::error::{ErrorObject, INTERNAL_ERROR_CODE};
use pallet_amm_dex::{Pool, TokenPool};
use sp_api::ProvideRuntimeApi;
use sp_blockchain::HeaderBackend;
use std::sync::Arc;
use verdis_runtime::opaque::Block;
use verdis_runtime::AmmDexApi as AmmDexRuntimeApi;
use verdis_runtime::{AccountId, Balance};

fn rpc_err(e: impl std::fmt::Display) -> ErrorObject<'static> {
    ErrorObject::owned(INTERNAL_ERROR_CODE, e.to_string(), None::<()>)
}

#[rpc(server)]
pub trait AmmDexRpc {
    #[method(name = "amm_dex_getPool")]
    fn get_pool(&self, pool_id: u32) -> RpcResult<Option<Pool<AccountId, Balance>>>;

    #[method(name = "amm_dex_getPoolCount")]
    fn get_pool_count(&self) -> RpcResult<u32>;

    #[method(name = "amm_dex_getAllPools")]
    fn get_all_pools(&self) -> RpcResult<Vec<Pool<AccountId, Balance>>>;

    #[method(name = "amm_dex_getTokenPool")]
    fn get_token_pool(&self, pool_id: u32) -> RpcResult<Option<TokenPool<AccountId, Balance>>>;

    #[method(name = "amm_dex_getTokenPoolCount")]
    fn get_token_pool_count(&self) -> RpcResult<u32>;

    #[method(name = "amm_dex_getAllTokenPools")]
    fn get_all_token_pools(&self) -> RpcResult<Vec<TokenPool<AccountId, Balance>>>;

    #[method(name = "amm_dex_getLiquidity")]
    fn get_liquidity(&self, pool_id: u32, account: AccountId) -> RpcResult<Balance>;

    #[method(name = "amm_dex_getTokenLiquidity")]
    fn get_token_liquidity(&self, pool_id: u32, account: AccountId) -> RpcResult<Balance>;

    #[method(name = "amm_dex_getPrice")]
    fn get_price(&self, pool_id: u32, token: Vec<u8>) -> RpcResult<Option<Balance>>;
}

pub struct AmmDexRpcImpl<C> {
    client: Arc<C>,
}

impl<C> AmmDexRpcImpl<C> {
    pub fn new(client: Arc<C>) -> Self {
        Self { client }
    }
}

impl<C> AmmDexRpcServer for AmmDexRpcImpl<C>
where
    C: ProvideRuntimeApi<Block> + HeaderBackend<Block> + 'static,
    C::Api: AmmDexRuntimeApi<Block>,
{
    fn get_pool(&self, pool_id: u32) -> RpcResult<Option<Pool<AccountId, Balance>>> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_pool(at, pool_id)
            .map_err(rpc_err)
    }

    fn get_pool_count(&self) -> RpcResult<u32> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_pool_count(at)
            .map_err(rpc_err)
    }

    fn get_all_pools(&self) -> RpcResult<Vec<Pool<AccountId, Balance>>> {
        let at = self.client.info().best_hash;
        self.client.runtime_api().get_all_pools(at).map_err(rpc_err)
    }

    fn get_token_pool(&self, pool_id: u32) -> RpcResult<Option<TokenPool<AccountId, Balance>>> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_token_pool(at, pool_id)
            .map_err(rpc_err)
    }

    fn get_token_pool_count(&self) -> RpcResult<u32> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_token_pool_count(at)
            .map_err(rpc_err)
    }

    fn get_all_token_pools(&self) -> RpcResult<Vec<TokenPool<AccountId, Balance>>> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_all_token_pools(at)
            .map_err(rpc_err)
    }

    fn get_liquidity(&self, pool_id: u32, account: AccountId) -> RpcResult<Balance> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_liquidity(at, pool_id, account)
            .map_err(rpc_err)
    }

    fn get_token_liquidity(&self, pool_id: u32, account: AccountId) -> RpcResult<Balance> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_token_liquidity(at, pool_id, account)
            .map_err(rpc_err)
    }

    fn get_price(&self, pool_id: u32, token: Vec<u8>) -> RpcResult<Option<Balance>> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_price(at, pool_id, token)
            .map_err(rpc_err)
    }
}

// === DposApi RPC ===
use verdis_runtime::DposApi as DposRuntimeApi;

#[rpc(server)]
pub trait DposRpc {
    #[method(name = "dpos_activeValidators")]
    fn active_validators(&self) -> RpcResult<Vec<AccountId>>;

    #[method(name = "dpos_allValidators")]
    fn all_validators(&self) -> RpcResult<Vec<AccountId>>;

    #[method(name = "dpos_validatorStake")]
    fn validator_stake(&self, validator: AccountId) -> RpcResult<Balance>;

    #[method(name = "dpos_currentEpoch")]
    fn current_epoch(&self) -> RpcResult<u32>;

    #[method(name = "dpos_validatorName")]
    fn get_validator_name(&self, validator: AccountId) -> RpcResult<Option<Vec<u8>>>;
}

pub struct DposRpcImpl<C> {
    client: Arc<C>,
}

impl<C> DposRpcImpl<C> {
    pub fn new(client: Arc<C>) -> Self {
        Self { client }
    }
}

impl<C> DposRpcServer for DposRpcImpl<C>
where
    C: ProvideRuntimeApi<Block> + HeaderBackend<Block> + 'static,
    C::Api: DposRuntimeApi<Block>,
{
    fn active_validators(&self) -> RpcResult<Vec<AccountId>> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .active_validators(at)
            .map_err(rpc_err)
    }

    fn all_validators(&self) -> RpcResult<Vec<AccountId>> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .all_validators(at)
            .map_err(rpc_err)
    }

    fn validator_stake(&self, validator: AccountId) -> RpcResult<Balance> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .validator_stake(at, validator)
            .map_err(rpc_err)
    }

    fn current_epoch(&self) -> RpcResult<u32> {
        let at = self.client.info().best_hash;
        self.client.runtime_api().current_epoch(at).map_err(rpc_err)
    }

    fn get_validator_name(&self, validator: AccountId) -> RpcResult<Option<Vec<u8>>> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_validator_name(at, validator)
            .map_err(rpc_err)
    }
}

// === EcoApi RPC ===
use verdis_runtime::EcoApi as EcoRuntimeApi;

#[rpc(server)]
pub trait EcoRpc {
    #[method(name = "eco_getTotalCO2Offset")]
    fn get_total_co2_offset(&self) -> RpcResult<u64>;

    #[method(name = "eco_getTotalTreesPlanted")]
    fn get_total_trees_planted(&self) -> RpcResult<u32>;

    #[method(name = "eco_getTotalCreditsRetired")]
    fn get_total_credits_retired(&self) -> RpcResult<u64>;

    #[method(name = "eco_getCarbonCreditCount")]
    fn get_carbon_credit_count(&self) -> RpcResult<u32>;

    #[method(name = "eco_getReforestProjectCount")]
    fn get_reforest_project_count(&self) -> RpcResult<u32>;

    #[method(name = "eco_getGreenValidatorCount")]
    fn get_green_validator_count(&self) -> RpcResult<u32>;

    #[method(name = "eco_getGreenScore")]
    fn get_green_score(&self, validator: AccountId) -> RpcResult<Option<u8>>;

    #[method(name = "eco_getAllGreenValidators")]
    fn get_all_green_validators(&self) -> RpcResult<Vec<(AccountId, u8)>>;
}

pub struct EcoRpcImpl<C> {
    client: Arc<C>,
}

impl<C> EcoRpcImpl<C> {
    pub fn new(client: Arc<C>) -> Self {
        Self { client }
    }
}

impl<C> EcoRpcServer for EcoRpcImpl<C>
where
    C: ProvideRuntimeApi<Block> + HeaderBackend<Block> + 'static,
    C::Api: EcoRuntimeApi<Block>,
{
    fn get_total_co2_offset(&self) -> RpcResult<u64> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_total_co2_offset(at)
            .map_err(rpc_err)
    }

    fn get_total_trees_planted(&self) -> RpcResult<u32> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_total_trees_planted(at)
            .map_err(rpc_err)
    }

    fn get_total_credits_retired(&self) -> RpcResult<u64> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_total_credits_retired(at)
            .map_err(rpc_err)
    }

    fn get_carbon_credit_count(&self) -> RpcResult<u32> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_carbon_credit_count(at)
            .map_err(rpc_err)
    }

    fn get_reforest_project_count(&self) -> RpcResult<u32> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_reforest_project_count(at)
            .map_err(rpc_err)
    }

    fn get_green_validator_count(&self) -> RpcResult<u32> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_green_validator_count(at)
            .map_err(rpc_err)
    }

    fn get_green_score(&self, validator: AccountId) -> RpcResult<Option<u8>> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_green_score(at, validator)
            .map_err(rpc_err)
    }

    fn get_all_green_validators(&self) -> RpcResult<Vec<(AccountId, u8)>> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_all_green_validators(at)
            .map_err(rpc_err)
    }
}

// === ContractsApi RPC ===
use verdis_runtime::ContractsApi as ContractsRuntimeApi;
use verdis_runtime::Hash;

#[rpc(server)]
pub trait ContractsRpc {
    /// Query a storage entry of a contract.
    #[method(name = "contracts_getStorage")]
    fn get_storage(&self, address: AccountId, key: Vec<u8>) -> RpcResult<Option<Vec<u8>>>;

    /// Simulate a call to a contract (read-only, no state change).
    #[method(name = "contracts_call")]
    fn call(
        &self,
        origin: AccountId,
        dest: AccountId,
        value: Balance,
        gas_limit: Option<u64>,
        storage_deposit_limit: Option<Balance>,
        input_data: Vec<u8>,
    ) -> RpcResult<ContractCallResult>;

    /// Instantiate a new contract (read-only simulation).
    #[method(name = "contracts_instantiate")]
    fn instantiate(
        &self,
        origin: AccountId,
        value: Balance,
        gas_limit: Option<u64>,
        storage_deposit_limit: Option<Balance>,
        code_hash: Hash,
        data: Vec<u8>,
        salt: Vec<u8>,
    ) -> RpcResult<ContractInstantiateResult>;
}

/// Simplified contract call result for JSON-RPC.
#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct ContractCallResult {
    pub success: bool,
    pub output: Vec<u8>,
    pub gas_consumed: u64,
    pub error: Option<String>,
}

/// Simplified contract instantiate result for JSON-RPC.
#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct ContractInstantiateResult {
    pub success: bool,
    pub address: Option<AccountId>,
    pub gas_consumed: u64,
    pub error: Option<String>,
}

pub struct ContractsRpcImpl<C> {
    client: Arc<C>,
}

impl<C> ContractsRpcImpl<C> {
    pub fn new(client: Arc<C>) -> Self {
        Self { client }
    }
}

impl<C> ContractsRpcServer for ContractsRpcImpl<C>
where
    C: ProvideRuntimeApi<Block> + HeaderBackend<Block> + 'static,
    C::Api: ContractsRuntimeApi<Block>,
{
    fn get_storage(&self, address: AccountId, key: Vec<u8>) -> RpcResult<Option<Vec<u8>>> {
        let at = self.client.info().best_hash;
        let result = self
            .client
            .runtime_api()
            .get_storage(at, address, key)
            .map_err(rpc_err)?;
        result.map_err(|e| rpc_err(format!("{:?}", e)))
    }

    fn call(
        &self,
        origin: AccountId,
        dest: AccountId,
        value: Balance,
        gas_limit: Option<u64>,
        storage_deposit_limit: Option<Balance>,
        input_data: Vec<u8>,
    ) -> RpcResult<ContractCallResult> {
        let at = self.client.info().best_hash;
        let weight =
            gas_limit.map(|ref_time| frame_support::weights::Weight::from_parts(ref_time, 0));
        let result = self
            .client
            .runtime_api()
            .call(
                at,
                origin,
                dest,
                value,
                weight,
                storage_deposit_limit,
                input_data,
            )
            .map_err(rpc_err)?;

        match result.result {
            Ok(exec_result) => Ok(ContractCallResult {
                success: !exec_result.did_revert(),
                output: exec_result.data.clone(),
                gas_consumed: result.gas_consumed.ref_time(),
                error: None,
            }),
            Err(err) => Ok(ContractCallResult {
                success: false,
                output: Vec::new(),
                gas_consumed: result.gas_consumed.ref_time(),
                error: Some(format!("{:?}", err)),
            }),
        }
    }

    fn instantiate(
        &self,
        origin: AccountId,
        value: Balance,
        gas_limit: Option<u64>,
        storage_deposit_limit: Option<Balance>,
        code_hash: Hash,
        data: Vec<u8>,
        salt: Vec<u8>,
    ) -> RpcResult<ContractInstantiateResult> {
        let at = self.client.info().best_hash;
        let weight =
            gas_limit.map(|ref_time| frame_support::weights::Weight::from_parts(ref_time, 0));
        let contract_code = verdis_runtime::pallet_contracts::Code::Existing(code_hash);
        let result = self
            .client
            .runtime_api()
            .instantiate(
                at,
                origin,
                value,
                weight,
                storage_deposit_limit,
                contract_code,
                data,
                salt,
            )
            .map_err(rpc_err)?;

        match result.result {
            Ok(instantiate_result) => Ok(ContractInstantiateResult {
                success: !instantiate_result.result.did_revert(),
                address: Some(instantiate_result.account_id.clone()),
                gas_consumed: result.gas_consumed.ref_time(),
                error: None,
            }),
            Err(err) => Ok(ContractInstantiateResult {
                success: false,
                address: None,
                gas_consumed: result.gas_consumed.ref_time(),
                error: Some(format!("{:?}", err)),
            }),
        }
    }
}
