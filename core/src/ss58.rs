use crate::error::{CoreError, CoreResult};
use sha2::{Sha256, Digest};

/// SS58 prefix for Verdis Chain
pub const VERDIS_SS58_PREFIX: u16 = 909;

/// SS58 checksum length
const SS58_CHECKSUM_LEN: usize = 2;

/// Encode a public key to an SS58 address with the given prefix
pub fn encode_address(public_key: &[u8; 32], prefix: u16) -> String {
    let prefix_bytes = encode_prefix(prefix);
    
    // Checksum: Blake2-256(prefix + public_key), first 2 bytes
    let checksum_input: Vec<u8> = prefix_bytes.iter()
        .chain(public_key.iter())
        .copied()
        .collect();
    let hash = blake2_256(&checksum_input);
    
    let mut full = Vec::with_capacity(prefix_bytes.len() + 32 + SS58_CHECKSUM_LEN);
    full.extend_from_slice(&prefix_bytes);
    full.extend_from_slice(public_key);
    full.extend_from_slice(&hash[..SS58_CHECKSUM_LEN]);
    
    bs58::encode(&full).into_string()
}

/// Decode an SS58 address to a 32-byte public key
pub fn decode_address(address: &str) -> CoreResult<[u8; 32]> {
    let (pubkey, _prefix) = decode_address_with_prefix(address)?;
    Ok(pubkey)
}

/// Decode an SS58 address and return both the public key and prefix
pub fn decode_address_with_prefix(address: &str) -> CoreResult<([u8; 32], u16)> {
    let decoded = bs58::decode(address).into_vec()
        .map_err(|e| CoreError::InvalidAddress(format!("Base58 decode: {}", e)))?;
    
    if decoded.len() < 35 {
        return Err(CoreError::InvalidAddress(format!("Address too short: {} bytes", decoded.len())));
    }
    
    let (prefix_len, prefix_val) = decode_prefix(&decoded)?;
    let addr_start = prefix_len;
    let addr_end = decoded.len() - SS58_CHECKSUM_LEN;
    
    if addr_end.saturating_sub(addr_start) != 32 {
        return Err(CoreError::InvalidAddress(format!(
            "Invalid address length: expected 32 bytes, got {}", addr_end.saturating_sub(addr_start)
        )));
    }
    
    // Verify checksum
    let checksum_input = &decoded[..addr_end];
    let hash = blake2_256(checksum_input);
    
    if hash[..SS58_CHECKSUM_LEN] != decoded[addr_end..] {
        return Err(CoreError::InvalidAddress("Checksum mismatch".into()));
    }
    
    let mut pubkey = [0u8; 32];
    pubkey.copy_from_slice(&decoded[addr_start..addr_end]);
    Ok((pubkey, prefix_val))
}

/// Encode a u16 prefix as SS58 varint bytes
fn encode_prefix(prefix: u16) -> Vec<u8> {
    if prefix < 64 {
        vec![prefix as u8]
    } else {
        let b0 = ((prefix >> 8) & 0x3f) as u8 | 0x40;
        let b1 = (prefix & 0xff) as u8;
        vec![b0, b1]
    }
}

/// Decode the prefix from the first bytes of an SS58 address
fn decode_prefix(bytes: &[u8]) -> CoreResult<(usize, u16)> {
    if bytes.is_empty() {
        return Err(CoreError::InvalidAddress("Empty address".into()));
    }
    
    let b0 = bytes[0];
    if b0 < 48 {
        Ok((1, b0 as u16))
    } else if b0 < 64 {
        Ok((1, b0 as u16))
    } else if b0 < 64 + 16 {
        if bytes.len() < 2 {
            return Err(CoreError::InvalidAddress("Prefix too short".into()));
        }
        let prefix = ((b0 as u16 & 0x3f) << 8) | (bytes[1] as u16);
        Ok((2, prefix))
    } else {
        if bytes.len() < 4 {
            return Err(CoreError::InvalidAddress("Prefix too short".into()));
        }
        let prefix = ((b0 as u16 & 0x3f) << 10)
            | ((bytes[1] as u16) << 2)
            | ((bytes[2] as u16) >> 6);
        Ok((4, prefix))
    }
}

/// Compute Blake2-256 hash
pub fn blake2_256(data: &[u8]) -> [u8; 32] {
    use blake2::Blake2b512;
    use blake2::Digest;
    let mut hasher = Blake2b512::new();
    hasher.update(data);
    let result = hasher.finalize();
    let mut hash = [0u8; 32];
    hash.copy_from_slice(&result[..32]);
    hash
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_encode_decode_roundtrip() {
        let pubkey = [42u8; 32];
        let address = encode_address(&pubkey, 909);
        println!("Address: {}", address);
        let (decoded, prefix) = decode_address_with_prefix(&address).unwrap();
        assert_eq!(decoded, pubkey);
        assert_eq!(prefix, 909);
    }

    #[test]
    fn test_decode_invalid() {
        let result = decode_address("invalid");
        assert!(result.is_err());
    }
}
