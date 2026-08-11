use crate::error::{CoreError, CoreResult};
use crate::keypair::Account;
use crate::extrinsic::{self, Era, CallIndices};
use crate::storage;
use crate::rpc::RpcClient;
use serde_json::Value;

/// High-level Substrate API for Verdis Chain
pub struct SubstrateApi {
    rpc: RpcClient,
    call_indices: CallIndices,
    genesis_hash: Option<[u8; 32]>,
    chain_properties: Option<ChainProperties>,
}

#[derive(Clone, Debug)]
pub struct ChainProperties {
    pub token_symbol: String,
    pub token_decimals: u8,
    pub ss58_prefix: u16,
}

impl SubstrateApi {
    pub fn new(rpc_url: &str) -> Self {
        SubstrateApi {
            rpc: RpcClient::new(rpc_url),
            call_indices: extrinsic::default_call_indices(),
            genesis_hash: None,
            chain_properties: None,
        }
    }

    pub fn set_rpc_url(&mut self, url: &str) {
        self.rpc = RpcClient::new(url);
        self.genesis_hash = None;
        self.chain_properties = None;
    }

    pub fn genesis_hash(&mut self) -> CoreResult<[u8; 32]> {
        if let Some(hash) = self.genesis_hash {
            return Ok(hash);
        }
        let result = self.rpc.request("chain_getBlockHash", vec![Value::Null])?;
        let hash_str = result.as_str()
            .ok_or_else(|| CoreError::Rpc("Block hash is not a string".into()))?;
        let hash_bytes = hex::decode(hash_str.strip_prefix("0x").unwrap_or(hash_str))?;
        if hash_bytes.len() != 32 {
            return Err(CoreError::Rpc(format!("Genesis hash wrong size: {}", hash_bytes.len())));
        }
        let mut hash = [0u8; 32];
        hash.copy_from_slice(&hash_bytes);
        self.genesis_hash = Some(hash);
        Ok(hash)
    }

    pub fn block_hash(&self, block_number: Option<u64>) -> CoreResult<[u8; 32]> {
        let params = match block_number {
            Some(n) => vec![Value::from(n)],
            None => vec![Value::Null],
        };
        let result = self.rpc.request("chain_getBlockHash", params)?;
        let hash_str = result.as_str()
            .ok_or_else(|| CoreError::Rpc("Block hash is not a string".into()))?;
        let hash_bytes = hex::decode(hash_str.strip_prefix("0x").unwrap_or(hash_str))?;
        let mut hash = [0u8; 32];
        hash.copy_from_slice(&hash_bytes);
        Ok(hash)
    }

    pub fn runtime_version(&self) -> CoreResult<Value> {
        self.rpc.request("state_getRuntimeVersion", vec![])
    }

    pub fn chain_name(&self) -> CoreResult<String> {
        let result = self.rpc.request("system_chain", vec![])?;
        result.as_str()
            .map(|s| s.to_string())
            .ok_or_else(|| CoreError::Rpc("Chain name is not a string".into()))
    }

    pub fn chain_properties(&mut self) -> CoreResult<ChainProperties> {
        if let Some(props) = &self.chain_properties {
            return Ok(props.clone());
        }
        let result = self.rpc.request("system_properties", vec![])?;
        let token_symbol = result.get("tokenSymbol")
            .and_then(|v| v.as_str())
            .unwrap_or("VRS")
            .to_string();
        let token_decimals = result.get("tokenDecimals")
            .and_then(|v| v.as_u64())
            .unwrap_or(9) as u8;
        let ss58_prefix = result.get("ss58Format")
            .and_then(|v| v.as_u64())
            .unwrap_or(909) as u16;
        let props = ChainProperties {
            token_symbol,
            token_decimals,
            ss58_prefix,
        };
        self.chain_properties = Some(props.clone());
        Ok(props)
    }

    pub fn get_balance(&self, address: &str) -> CoreResult<(u128, u128)> {
        let (pub_key, _prefix) = crate::ss58::decode_address_with_prefix(address)?;
        let storage_key = storage::system_account_key(&pub_key);
        let key_hex = format!("0x{}", hex::encode(&storage_key));
        
        let result = self.rpc.request("state_getStorage", vec![Value::from(key_hex)])?;
        
        if result.is_null() {
            return Ok((0, 0));
        }
        
        let data_hex = result.as_str()
            .ok_or_else(|| CoreError::Rpc("Storage value is not a string".into()))?;
        let data = hex::decode(data_hex.strip_prefix("0x").unwrap_or(data_hex))?;
        
        if data.len() < 4 * 4 + 2 * 16 {
            return Ok((0, 0));
        }
        
        let mut offset = 0;
        let _nonce = u32::from_le_bytes([
            data[offset], data[offset+1], data[offset+2], data[offset+3]
        ]);
        offset += 4;
        // consumers
        offset += 4;
        // providers
        offset += 4;
        // sufficients
        offset += 4;
        
        let free = u128::from_le_bytes(data[offset..offset+16].try_into().unwrap_or([0u8; 16]));
        offset += 16;
        let reserved = u128::from_le_bytes(data[offset..offset+16].try_into().unwrap_or([0u8; 16]));
        
        Ok((free, reserved))
    }

    pub fn get_nonce(&self, address: &str) -> CoreResult<u64> {
        let (pub_key, _) = crate::ss58::decode_address_with_prefix(address)?;
        let storage_key = storage::system_account_key(&pub_key);
        let key_hex = format!("0x{}", hex::encode(&storage_key));
        
        let result = self.rpc.request("state_getStorage", vec![Value::from(key_hex)])?;
        
        if result.is_null() {
            return Ok(0);
        }
        
        let data_hex = result.as_str()
            .ok_or_else(|| CoreError::Rpc("Storage value is not a string".into()))?;
        let data = hex::decode(data_hex.strip_prefix("0x").unwrap_or(data_hex))?;
        
        if data.len() < 4 {
            return Ok(0);
        }
        
        let nonce = u32::from_le_bytes([
            data[0], data[1], data[2], data[3]
        ]) as u64;
        
        Ok(nonce)
    }

    pub fn block_number(&self) -> CoreResult<u64> {
        let header = self.rpc.request("chain_getHeader", vec![Value::Null])?;
        let number_str = header.get("number")
            .and_then(|n| n.as_str())
            .ok_or_else(|| CoreError::Rpc("Missing block number".into()))?;
        let number = hex::decode(number_str.strip_prefix("0x").unwrap_or(number_str))?;
        let (val, _) = crate::scale::decode_compact(&number)?;
        Ok(val as u64)
    }

    pub fn get_header(&self, block_hash: Option<&[u8; 32]>) -> CoreResult<Value> {
        let params = match block_hash {
            Some(hash) => vec![Value::from(format!("0x{}", hex::encode(hash)))],
            None => vec![Value::Null],
        };
        self.rpc.request("chain_getHeader", params)
    }

    pub fn get_block(&self, block_hash: Option<&[u8; 32]>) -> CoreResult<Value> {
        let params = match block_hash {
            Some(hash) => vec![Value::from(format!("0x{}", hex::encode(hash)))],
            None => vec![Value::Null],
        };
        self.rpc.request("chain_getBlock", params)
    }

    pub fn transfer(
        &mut self,
        account: &Account,
        pin: &str,
        dest_address: &str,
        amount: u128,
    ) -> CoreResult<String> {
        let nonce = self.get_nonce(&account.address)?;
        let genesis = self.genesis_hash()?;
        let block_hash = self.block_hash(None)?;
        let rt_version = self.runtime_version()?;
        let spec_version = rt_version.get("specVersion")
            .and_then(|v| v.as_u64())
            .unwrap_or(0) as u32;
        let tx_version = rt_version.get("transactionVersion")
            .and_then(|v| v.as_u64())
            .unwrap_or(0) as u32;
        
        let (dest_pubkey, _) = crate::ss58::decode_address_with_prefix(dest_address)?;
        
        let (pallet_idx, call_idx) = self.call_indices.balances_transfer;
        let call = extrinsic::build_balances_transfer(
            pallet_idx, call_idx, &dest_pubkey, amount
        );
        
        let extrinsic_bytes = extrinsic::build_and_sign_extrinsic(
            account, pin, &call, nonce, 0, Era::Immortal,
            spec_version, tx_version, &genesis, &block_hash
        )?;
        
        let hex_extrinsic = format!("0x{}", hex::encode(&extrinsic_bytes));
        let result = self.rpc.request(
            "author_submitExtrinsic",
            vec![Value::from(hex_extrinsic)]
        )?;
        
        result.as_str()
            .map(|s| s.to_string())
            .ok_or_else(|| CoreError::ExtrinsicRejected("TX hash is not a string".into()))
    }

    pub fn staking_bond(
        &mut self,
        account: &Account,
        pin: &str,
        controller_address: &str,
        amount: u128,
    ) -> CoreResult<String> {
        let nonce = self.get_nonce(&account.address)?;
        let genesis = self.genesis_hash()?;
        let block_hash = self.block_hash(None)?;
        let rt_version = self.runtime_version()?;
        let spec_version = rt_version.get("specVersion")
            .and_then(|v| v.as_u64()).unwrap_or(0) as u32;
        let tx_version = rt_version.get("transactionVersion")
            .and_then(|v| v.as_u64()).unwrap_or(0) as u32;
        
        let (controller_pubkey, _) = crate::ss58::decode_address_with_prefix(controller_address)?;
        
        let (pallet_idx, call_idx) = self.call_indices.staking_bond;
        let call = extrinsic::build_staking_bond(
            pallet_idx, call_idx, &controller_pubkey, amount,
            extrinsic::RewardDestination::Staked
        );
        
        let extrinsic_bytes = extrinsic::build_and_sign_extrinsic(
            account, pin, &call, nonce, 0, Era::Immortal,
            spec_version, tx_version, &genesis, &block_hash
        )?;
        
        let hex_extrinsic = format!("0x{}", hex::encode(&extrinsic_bytes));
        let result = self.rpc.request(
            "author_submitExtrinsic", vec![Value::from(hex_extrinsic)]
        )?;
        
        result.as_str()
            .map(|s| s.to_string())
            .ok_or_else(|| CoreError::ExtrinsicRejected("TX hash is not a string".into()))
    }

    pub fn staking_nominate(
        &mut self,
        account: &Account,
        pin: &str,
        targets: &[&str],
    ) -> CoreResult<String> {
        let nonce = self.get_nonce(&account.address)?;
        let genesis = self.genesis_hash()?;
        let block_hash = self.block_hash(None)?;
        let rt_version = self.runtime_version()?;
        let spec_version = rt_version.get("specVersion")
            .and_then(|v| v.as_u64()).unwrap_or(0) as u32;
        let tx_version = rt_version.get("transactionVersion")
            .and_then(|v| v.as_u64()).unwrap_or(0) as u32;
        
        let target_keys: Vec<[u8; 32]> = targets.iter()
            .map(|addr| crate::ss58::decode_address_with_prefix(addr))
            .collect::<CoreResult<Vec<_>>>()?
            .into_iter().map(|(k, _)| k).collect();
        let target_refs: Vec<&[u8; 32]> = target_keys.iter().collect();
        
        let (pallet_idx, call_idx) = self.call_indices.staking_nominate;
        let call = extrinsic::build_staking_nominate(
            pallet_idx, call_idx, &target_refs
        );
        
        let extrinsic_bytes = extrinsic::build_and_sign_extrinsic(
            account, pin, &call, nonce, 0, Era::Immortal,
            spec_version, tx_version, &genesis, &block_hash
        )?;
        
        let hex_extrinsic = format!("0x{}", hex::encode(&extrinsic_bytes));
        let result = self.rpc.request(
            "author_submitExtrinsic", vec![Value::from(hex_extrinsic)]
        )?;
        
        result.as_str()
            .map(|s| s.to_string())
            .ok_or_else(|| CoreError::ExtrinsicRejected("TX hash is not a string".into()))
    }

    pub fn get_storage(&self, storage_key: &[u8]) -> CoreResult<Option<Vec<u8>>> {
        let key_hex = format!("0x{}", hex::encode(storage_key));
        let result = self.rpc.request("state_getStorage", vec![Value::from(key_hex)])?;
        
        if result.is_null() {
            return Ok(None);
        }
        
        let data_hex = result.as_str()
            .ok_or_else(|| CoreError::Rpc("Storage value is not a string".into()))?;
        let data = hex::decode(data_hex.strip_prefix("0x").unwrap_or(data_hex))?;
        Ok(Some(data))
    }

    pub fn pending_extrinsics(&self) -> CoreResult<Vec<Value>> {
        let result = self.rpc.request("author_pendingExtrinsics", vec![])?;
        result.as_array()
            .cloned()
            .ok_or_else(|| CoreError::Rpc("Pending extrinsics is not an array".into()))
    }

    pub fn system_health(&self) -> CoreResult<Value> {
        self.rpc.request("system_health", vec![])
    }

    pub fn system_peers(&self) -> CoreResult<Vec<Value>> {
        let result = self.rpc.request("system_peers", vec![])?;
        result.as_array()
            .cloned()
            .ok_or_else(|| CoreError::Rpc("Peers is not an array".into()))
    }

    pub fn system_local_peer_id(&self) -> CoreResult<String> {
        let result = self.rpc.request("system_localPeerId", vec![])?;
        result.as_str()
            .map(|s| s.to_string())
            .ok_or_else(|| CoreError::Rpc("Peer ID is not a string".into()))
    }
}
