use crate::error::{CoreError, CoreResult};
use crate::keypair::Account;
use crate::scale;
use crate::storage;

/// Extrinsic builder for Substrate-compatible chains
/// 
/// A signed extrinsic format:
/// [version: u8 (0x84 = signed, v4)]
/// [signer: AccountId32 + signature type prefix]
/// [signature: Ed25519 64 bytes]
/// [signed extensions: era, nonce, tip, genesis hash, block hash]
/// [call: pallet_index + call_index + args]

pub const EXTRINSIC_VERSION: u8 = 0x84; // version 4, signed

/// Era for transaction mortality
#[derive(Clone, Copy)]
pub enum Era {
    /// Immortal transaction (valid forever)
    Immortal,
    /// Mortal transaction, expires after ~(2^period) blocks
    Mortal { period: u64, phase: u64 },
}

impl Era {
    /// Create a mortal era with the given period (must be power of 2, >= 4)
    pub fn mortal(period: u64, current_block: u64) -> Self {
        assert!(period >= 4 && period.is_power_of_two());
        let phase = current_block % period;
        Era::Mortal { period, phase }
    }

    /// Encode the era
    pub fn encode(&self) -> Vec<u8> {
        match self {
            Era::Immortal => vec![0x00],
            Era::Mortal { period, phase } => {
                // Encode as (period, phase) with trailing zeros trimmed
                // period encoded as log2(period) << 2 | trailing_zeros_phase
                let period_trailing = period.trailing_zeros();
                let encoded_period = (period_trailing - 1) << 2;
                
                // Phase is encoded with the same bit-width as period
                let quantized_phase = phase >> period_trailing;
                let phase_low = (quantized_phase & 0x03) as u8;
                let first_byte = (encoded_period as u8) | phase_low;
                
                let phase_bytes = quantized_phase.to_le_bytes();
                let mut trimmed_phase = phase_bytes[..((period_trailing as usize - 1) / 8 + 1)].to_vec();
                
                let mut result = vec![first_byte];
                result.append(&mut trimmed_phase);
                result
            }
        }
    }
}

/// Build a Balances::transfer call
/// Call: [pallet_index] [call_index] [dest: MultiAddress<AccountId32>] [value: Compact<Balance>]
pub fn build_balances_transfer(
    pallet_index: u8,
    call_index: u8,
    dest_public_key: &[u8; 32],
    amount: u128,
) -> Vec<u8> {
    let mut call = Vec::new();
    
    // Pallet index
    call.push(pallet_index);
    
    // Call index
    call.push(call_index);
    
    // Destination: MultiAddress::Id(AccountId32) = variant 0 + 32 bytes
    call.push(0x00); // Id variant
    call.extend_from_slice(dest_public_key);
    
    // Amount: Compact<Balance>
    call.extend(scale::encode_compact(amount));
    
    call
}

/// Build a complete signed extrinsic
pub fn build_and_sign_extrinsic(
    account: &Account,
    pin: &str,
    call_data: &[u8],
    nonce: u64,
    tip: u128,
    era: Era,
    spec_version: u32,
    transaction_version: u32,
    genesis_hash: &[u8; 32],
    block_hash: &[u8; 32],
) -> CoreResult<Vec<u8>> {
    // Build the signing payload
    let signing_payload = build_signing_payload(
        call_data,
        nonce,
        tip,
        era,
        spec_version,
        transaction_version,
        genesis_hash,
        block_hash,
    );
    
    // Sign the payload with Ed25519
    let signature = account.sign(pin, &signing_payload)?;
    
    // Build the extrinsic
    let mut extrinsic = Vec::new();
    
    // Version byte (signed, v4)
    extrinsic.push(EXTRINSIC_VERSION);
    
    // Signer: MultiAddress::Id(AccountId32)
    extrinsic.push(0x00); // Id variant
    extrinsic.extend_from_slice(&account.public_key);
    
    // Signature: Ed25519 (sig type is implicit in v4)
    extrinsic.extend_from_slice(&signature);
    
    // Signed extensions:
    // - era
    extrinsic.extend(era.encode());
    // - nonce (compact)
    extrinsic.extend(scale::encode_compact(nonce as u128));
    // - tip (compact)
    extrinsic.extend(scale::encode_compact(tip));
    
    // Call data
    extrinsic.extend_from_slice(call_data);
    
    // Length-prefix the entire extrinsic (compact)
    let len = extrinsic.len();
    let mut prefixed = scale::encode_compact(len as u128);
    prefixed.extend(extrinsic);
    
    Ok(prefixed)
}

/// Build the signing payload that gets signed
fn build_signing_payload(
    call_data: &[u8],
    nonce: u64,
    tip: u128,
    era: Era,
    spec_version: u32,
    transaction_version: u32,
    genesis_hash: &[u8; 32],
    block_hash: &[u8; 32],
) -> Vec<u8> {
    let mut payload = Vec::new();
    
    // Call data
    payload.extend_from_slice(call_data);
    
    // Era
    payload.extend(era.encode());
    
    // Nonce (compact)
    payload.extend(scale::encode_compact(nonce as u128));
    
    // Tip (compact)
    payload.extend(scale::encode_compact(tip));
    
    // Spec version
    payload.extend(scale::encode_u32(spec_version));
    
    // Transaction version
    payload.extend(scale::encode_u32(transaction_version));
    
    // Genesis hash
    payload.extend_from_slice(genesis_hash);
    
    // Block hash (mortality checkpoint)
    payload.extend_from_slice(block_hash);
    
    payload
}

/// Get pallet and call indices from the chain's metadata
/// In a real wallet, these come from state_getMetadata
/// For now, we hardcode the common ones for a Substrate FRAME chain
pub struct CallIndices {
    pub balances_transfer: (u8, u8),       // (pallet_idx, call_idx)
    pub balances_transfer_all: (u8, u8),
    pub utility_batch: (u8, u8),
    pub staking_bond: (u8, u8),
    pub staking_nominate: (u8, u8),
    pub staking_unbond: (u8, u8),
    pub staking_withdraw: (u8, u8),
    pub session_set_keys: (u8, u8),
    pub timestamp_set: (u8, u8),
    pub sudo_execute: (u8, u8),
}

/// Default call indices for a standard FRAME-based Substrate chain
/// These may vary — in production, fetch from metadata
pub fn default_call_indices() -> CallIndices {
    CallIndices {
        balances_transfer: (5, 0),         // Balances::transfer
        balances_transfer_all: (5, 2),     // Balances::transfer_all
        utility_batch: (10, 0),            // Utility::batch
        staking_bond: (7, 0),             // Staking::bond
        staking_nominate: (7, 5),         // Staking::nominate
        staking_unbond: (7, 6),           // Staking::unbond
        staking_withdraw: (7, 8),         // Staking::withdraw_unbonded
        session_set_keys: (8, 0),         // Session::set_keys
        timestamp_set: (3, 0),            // Timestamp::set
        sudo_execute: (0, 1),             // Sudo::execute
    }
}

/// Build a Staking::bond call
pub fn build_staking_bond(
    pallet_index: u8,
    call_index: u8,
    controller_public_key: &[u8; 32],
    amount: u128,
    reward_destination: RewardDestination,
) -> Vec<u8> {
    let mut call = Vec::new();
    call.push(pallet_index);
    call.push(call_index);
    
    // Controller: MultiAddress::Id
    call.push(0x00);
    call.extend_from_slice(controller_public_key);
    
    // Value: Compact<Balance>
    call.extend(scale::encode_compact(amount));
    
    // Reward destination: enum
    call.push(reward_destination as u8);
    
    call
}

/// Build a Staking::nominate call
pub fn build_staking_nominate(
    pallet_index: u8,
    call_index: u8,
    targets: &[&[u8; 32]],
) -> Vec<u8> {
    let mut call = Vec::new();
    call.push(pallet_index);
    call.push(call_index);
    
    // Targets: Vec<MultiAddress<AccountId32>>
    call.extend(scale::encode_compact(targets.len() as u128));
    for target in targets {
        call.push(0x00); // Id variant
        call.extend_from_slice(target.as_slice());
    }
    
    call
}

/// Build a Staking::unbond call
pub fn build_staking_unbond(
    pallet_index: u8,
    call_index: u8,
    amount: u128,
) -> Vec<u8> {
    let mut call = Vec::new();
    call.push(pallet_index);
    call.push(call_index);
    call.extend(scale::encode_compact(amount));
    call
}

#[derive(Clone, Copy)]
#[repr(u8)]
pub enum RewardDestination {
    Staked = 0,
    Stash = 1,
    Controller = 2,
    Account = 3,
    None = 4,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_era_immortal() {
        let era = Era::Immortal;
        assert_eq!(era.encode(), vec![0x00]);
    }

    #[test]
    fn test_build_balances_transfer() {
        let dest = [1u8; 32];
        let call = build_balances_transfer(5, 0, &dest, 1_000_000_000_000);
        assert_eq!(call[0], 5); // pallet index
        assert_eq!(call[1], 0); // call index
        assert_eq!(call[2], 0); // MultiAddress::Id
        assert_eq!(&call[3..35], &dest); // dest
    }
}
