import sys

filepath = '/opt/verdis-chain/pallets/evm/src/interpreter.rs'

with open(filepath) as f:
    c = f.read()

# Add codec::Encode import
c = c.replace(
    'use sp_core::{H160, H256, U256};\nuse sp_std::vec::Vec;',
    'use sp_core::{H160, H256, U256};\nuse sp_std::vec::Vec;\nuse codec::Encode;'
)

# Replace the to_big_endian/to_little_endian approach with manual byte construction
old = """let mut bytes = [0u8; 32];
        val.to_little_endian(&mut bytes);
        bytes.reverse();
        self.store(offset, &bytes)"""

new = """let mut encoded = val.encode();
        encoded.reverse();
        let mut bytes = [0u8; 32];
        let len = encoded.len().min(32);
        bytes[32-len..].copy_from_slice(&encoded[..len]);
        self.store(offset, &bytes)"""

c = c.replace(old, new)

with open(filepath, 'w') as f:
    f.write(c)

print('Fixed store_u256')
