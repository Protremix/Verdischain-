use crate::error::{CoreError, CoreResult};
use crate::ss58;

/// Storage key generation for Substrate
/// 
/// Storage keys are computed as: twox_128(pallet_name) ++ twox_128(storage_name) ++ key_hash

/// Compute twox_128 (first 16 bytes of xxHash128)
/// Substrate's twox_128 uses two xxHash64 computations with different seeds
pub fn twox_128(data: &[u8]) -> [u8; 16] {
    let mut result = [0u8; 16];
    
    // First 8 bytes: xxHash64 with seed 0
    let h1 = xxhash64(data, 0);
    result[..8].copy_from_slice(&h1.to_le_bytes());
    
    // Second 8 bytes: xxHash64 with seed 0x9E3779B97F4A7C15
    let h2 = xxhash64(data, 0x9E3779B97F4A7C15);
    result[8..].copy_from_slice(&h2.to_le_bytes());
    
    result
}

/// Compute twox_256 (first 32 bytes of xxHash256)
pub fn twox_256(data: &[u8]) -> [u8; 32] {
    let mut result = [0u8; 32];
    let seeds: [u64; 4] = [
        0,
        0x9E3779B97F4A7C15,
        0xC2B2AE3D27D4EB4F,
        0x165667B19E3779F9,
    ];
    
    for (i, &seed) in seeds.iter().enumerate() {
        let h = xxhash64(data, seed);
        result[i * 8..(i + 1) * 8].copy_from_slice(&h.to_le_bytes());
    }
    
    result
}

/// Compute Blake2-256 hash (re-exported from ss58 module)
pub fn blake2_256(data: &[u8]) -> [u8; 32] {
    ss58::blake2_256(data)
}

/// Compute xxHash64 with a given seed
fn xxhash64(data: &[u8], seed: u64) -> u64 {
    use twox_hash::XxHash64;
    let mut hasher = XxHash64::with_seed(seed);
    use std::io::Write;
    hasher.write_all(data).unwrap();
    hasher.finish()
}

/// Generate a storage key for a simple value in a pallet
pub fn storage_value_key(pallet: &str, storage: &str) -> Vec<u8> {
    let mut key = Vec::new();
    key.extend_from_slice(&twox_128(pallet.as_bytes()));
    key.extend_from_slice(&twox_128(storage.as_bytes()));
    key
}

/// Generate a storage key for a map entry (Blake2_256 key hasher)
pub fn storage_map_key(pallet: &str, storage: &str, key: &[u8]) -> Vec<u8> {
    let mut result = storage_value_key(pallet, storage);
    let key_hash = blake2_256(key);
    result.extend_from_slice(&key_hash);
    result
}

/// Generate a storage key using twox_128 for the key hash
pub fn storage_map_key_twox(pallet: &str, storage: &str, key: &[u8]) -> Vec<u8> {
    let mut result = storage_value_key(pallet, storage);
    let key_hash = twox_128(key);
    result.extend_from_slice(&key_hash);
    result
}

/// Storage hasher types
#[derive(Clone, Copy)]
pub enum StorageHasher {
    Blake2_256,
    Blake2_128,
    Twox128,
    Twox256,
    Identity,
}

fn hash_key(data: &[u8], hasher: StorageHasher) -> Vec<u8> {
    match hasher {
        StorageHasher::Blake2_256 => blake2_256(data).to_vec(),
        StorageHasher::Blake2_128 => ss58::blake2_256(data)[..16].to_vec(),
        StorageHasher::Twox128 => twox_128(data).to_vec(),
        StorageHasher::Twox256 => twox_256(data).to_vec(),
        StorageHasher::Identity => data.to_vec(),
    }
}

/// Generate the storage key for System::Account(account_id)
pub fn system_account_key(public_key: &[u8; 32]) -> Vec<u8> {
    storage_map_key_twox("System", "Account", public_key)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_twox_128() {
        let hash = twox_128(b"System");
        assert_eq!(hash.len(), 16);
    }

    #[test]
    fn test_blake2_256() {
        let hash = blake2_256(b"hello");
        assert_eq!(hash.len(), 32);
    }

    #[test]
    fn test_storage_value_key() {
        let key = storage_value_key("System", "Number");
        assert_eq!(key.len(), 32);
    }
}
