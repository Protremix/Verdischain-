use crate::error::{CoreError, CoreResult};

/// SCALE codec — compact encoding for Substrate extrinsics
/// 
/// SCALE (Simple Concatenated Aggregate Little-Endian) is Parity's
/// lightweight encoding format used in Substrate/Polkadot.

/// SCALE compact encoding for unsigned integers
pub fn encode_compact(value: u128) -> Vec<u8> {
    if value < 64 {
        // Single-byte mode: 0b00xxxxxx
        vec![(value as u8) << 2]
    } else if value < 16384 {
        // Two-byte mode: 0b01xxxxxx xxxxxxxx
        let v = (value as u16) << 2 | 0b01;
        vec![(v & 0xff) as u8, (v >> 8) as u8]
    } else if value < (1 << 30) {
        // Four-byte mode: 0b10xxxxxx (6 bits + 24 bits)
        let v = ((value as u32) << 2) | 0b10;
        v.to_le_bytes().to_vec()
    } else {
        // Big-integer mode: 0b11xxxxxx
        // Lower 6 bits = byte count - 4
        let mut bytes = value.to_le_bytes().to_vec();
        // Remove trailing zeros
        while bytes.last() == Some(&0) && bytes.len() > 1 {
            bytes.pop();
        }
        let byte_count = bytes.len();
        if byte_count > 67 {
            panic!("Compact encoding overflow: {} bytes", byte_count);
        }
        let mut result = vec![((byte_count - 4) << 2) as u8 | 0b11];
        result.extend_from_slice(&bytes);
        result
    }
}

/// SCALE compact decoding
pub fn decode_compact(data: &[u8]) -> CoreResult<(u128, usize)> {
    if data.is_empty() {
        return Err(CoreError::ScaleDecode("Empty data for compact".into()));
    }
    
    let first = data[0];
    let mode = first & 0b11;
    
    match mode {
        0 => {
            // Single-byte
            Ok(((first >> 2) as u128, 1))
        }
        1 => {
            // Two-byte
            if data.len() < 2 {
                return Err(CoreError::ScaleDecode("Need 2 bytes for compact".into()));
            }
            let val = ((first as u16) | ((data[1] as u16) << 8)) >> 2;
            Ok((val as u128, 2))
        }
        2 => {
            // Four-byte
            if data.len() < 4 {
                return Err(CoreError::ScaleDecode("Need 4 bytes for compact".into()));
            }
            let val = u32::from_le_bytes([data[0], data[1], data[2], data[3]]) >> 2;
            Ok((val as u128, 4))
        }
        3 => {
            // Big-integer
            let byte_count = ((first >> 2) as usize) + 4;
            if data.len() < 1 + byte_count {
                return Err(CoreError::ScaleDecode(format!(
                    "Need {} bytes for big compact, have {}", 1 + byte_count, data.len()
                )));
            }
            let mut padded = [0u8; 16];
            padded[..byte_count].copy_from_slice(&data[1..1 + byte_count]);
            let val = u128::from_le_bytes(padded);
            Ok((val, 1 + byte_count))
        }
        _ => unreachable!(),
    }
}

/// Encode a u32 as fixed 4 bytes LE
pub fn encode_u32(value: u32) -> Vec<u8> {
    value.to_le_bytes().to_vec()
}

/// Encode a u64 as fixed 8 bytes LE
pub fn encode_u64(value: u64) -> Vec<u8> {
    value.to_le_bytes().to_vec()
}

/// Encode a u128 as fixed 16 bytes LE
pub fn encode_u128(value: u128) -> Vec<u8> {
    value.to_le_bytes().to_vec()
}

/// Encode a Vec<u8> with length prefix (compact)
pub fn encode_vec_u8(data: &[u8]) -> Vec<u8> {
    let mut result = encode_compact(data.len() as u128);
    result.extend_from_slice(data);
    result
}

/// Encode a String with length prefix (compact)
pub fn encode_string(s: &str) -> Vec<u8> {
    encode_vec_u8(s.as_bytes())
}

/// Encode a bool (single byte)
pub fn encode_bool(value: bool) -> Vec<u8> {
    vec![if value { 1 } else { 0 }]
}

/// Encode an Option<T> (1 byte prefix + value or none)
pub fn encode_option<T, F: Fn(&T) -> Vec<u8>>(value: &Option<T>, encoder: F) -> Vec<u8> {
    match value {
        Some(v) => {
            let mut result = vec![1u8];
            result.extend(encoder(v));
            result
        }
        None => vec![0u8],
    }
}

/// Encode an enum variant index as a single byte
pub fn encode_enum_variant(variant: u8) -> Vec<u8> {
    vec![variant]
}

/// Encode a Vector of items with compact length prefix
pub fn encode_vec<T, F: Fn(&T) -> Vec<u8>>(items: &[T], encoder: F) -> Vec<u8> {
    let mut result = encode_compact(items.len() as u128);
    for item in items {
        result.extend(encoder(item));
    }
    result
}

/// Encode a 32-byte fixed-size array (public key, hash, etc.)
pub fn encode_fixed32(bytes: &[u8; 32]) -> Vec<u8> {
    bytes.to_vec()
}

/// Encode a 64-byte fixed-size array (signature)
pub fn encode_fixed64(bytes: &[u8; 64]) -> Vec<u8> {
    bytes.to_vec()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_compact_single() {
        let encoded = encode_compact(10);
        assert_eq!(encoded, vec![10 << 2]); // 40
        let (decoded, len) = decode_compact(&encoded).unwrap();
        assert_eq!(decoded, 10);
        assert_eq!(len, 1);
    }

    #[test]
    fn test_compact_two() {
        let encoded = encode_compact(100);
        let (decoded, len) = decode_compact(&encoded).unwrap();
        assert_eq!(decoded, 100);
        assert_eq!(len, 2);
    }

    #[test]
    fn test_compact_four() {
        let encoded = encode_compact(100000);
        let (decoded, len) = decode_compact(&encoded).unwrap();
        assert_eq!(decoded, 100000);
        assert_eq!(len, 4);
    }

    #[test]
    fn test_compact_big() {
        let value: u128 = 1_000_000_000_000;
        let encoded = encode_compact(value);
        let (decoded, _) = decode_compact(&encoded).unwrap();
        assert_eq!(decoded, value);
    }

    #[test]
    fn test_encode_u32() {
        assert_eq!(encode_u32(0x12345678), vec![0x78, 0x56, 0x34, 0x12]);
    }

    #[test]
    fn test_encode_string() {
        let encoded = encode_string("hello");
        assert_eq!(&encoded[0], &20); // compact(5) = 5 << 2 = 20
        assert_eq!(&encoded[1..], b"hello");
    }
}
