import sys

interp_path = '/opt/verdis-chain/pallets/evm/src/interpreter.rs'
lib_path = '/opt/verdis-chain/pallets/evm/src/lib.rs'

# Read current interpreter
with open(interp_path) as f:
    c = f.read()

# Find the SELFDESTRUCT section and add missing opcodes before it
# We'll add: CALL(0xF1), CALLCODE(0xF2), RETURN(0xF3 already exists), DELEGATECALL(0xF4),
# STATICCALL(0xFA), CREATE(0xF0), CREATE2(0xF5),
# EXTCODESIZE(0x3B), EXTCODECOPY(0x3C), EXTCODEHASH(0x3F),
# RETURNDATASIZE(0x3D), RETURNDATACOPY(0x3E),
# BLOCKHASH(0x40), NUMBER(0x43), TIMESTAMP(0x42), GASLIMIT(0x45),
# GASPRICE(0x3A), SELFBALANCE(0x47), CHAINID(0x46 exists), BASEFEE(0x48)

# Add environment opcodes - find existing opcodes and add missing ones

# Add EXTCODESIZE (0x3B)
old_3a = "0x3A => { push!(U256::zero()); pc += 1; } // GASPRICE - placeholder"
new_3a = "0x3A => { push!(U256::zero()); pc += 1; } // GASPRICE - placeholder (no gas price in Substrate)"
c = c.replace(old_3a, new_3a)

# Add EXTCODESIZE (0x3B), EXTCODECOPY (0x3C), RETURNDATASIZE (0x3D), RETURNDATACOPY (0x3E), EXTCODEHASH (0x3F)
# Find a good place to insert - after existing 0x3A
insert_after = "0x3A => { push!(U256::zero()); pc += 1; } // GASPRICE - placeholder (no gas price in Substrate)\n"
new_opcodes_3x = insert_after + """            0x3B => {
                // EXTCODESIZE
                let addr = pop!();
                let mut addr_bytes = [0u8; 20];
                addr.to_big_endian(&mut addr_bytes);
                let contract = H160::from_slice(&addr_bytes[..20]);
                let code = crate::Pallet::<T>::get_code(contract);
                push!(U256::from(code.len() as u32));
                pc += 1;
            }
            0x3C => {
                // EXTCODECOPY
                let addr = pop!();
                let dest_offset = pop!();
                let offset = pop!();
                let size = pop!();
                let mut addr_bytes = [0u8; 20];
                addr.to_big_endian(&mut addr_bytes);
                let contract = H160::from_slice(&addr_bytes[..20]);
                let code = crate::Pallet::<T>::get_code(contract);
                let off: usize = offset.try_into().unwrap_or(0);
                let sz: usize = size.try_into().unwrap_or(0);
                let mut data = vec![0u8; sz];
                if off < code.len() {
                    let end = (off + sz).min(code.len());
                    data[..end - off].copy_from_slice(&code[off..end]);
                }
                let dest: usize = dest_offset.try_into().unwrap_or(0);
                ctx.memory.store(dest, &data).map_err(|e| ExecutionError::from(e))?;
                pc += 1;
            }
            0x3D => {
                // RETURNDATASIZE
                push!(U256::from(ctx.return_data.len() as u32));
                pc += 1;
            }
            0x3E => {
                // RETURNDATACOPY
                let dest_offset = pop!();
                let offset = pop!();
                let size = pop!();
                let off: usize = offset.try_into().unwrap_or(0);
                let sz: usize = size.try_into().unwrap_or(0);
                let mut data = vec![0u8; sz];
                if off < ctx.return_data.len() {
                    let end = (off + sz).min(ctx.return_data.len());
                    data[..end - off].copy_from_slice(&ctx.return_data[off..end]);
                }
                let dest: usize = dest_offset.try_into().unwrap_or(0);
                ctx.memory.store(dest, &data).map_err(|e| ExecutionError::from(e))?;
                pc += 1;
            }
            0x3F => {
                // EXTCODEHASH
                let addr = pop!();
                let mut addr_bytes = [0u8; 20];
                addr.to_big_endian(&mut addr_bytes);
                let contract = H160::from_slice(&addr_bytes[..20]);
                let code = crate::Pallet::<T>::get_code(contract);
                if code.is_empty() {
                    push!(U256::zero());
                } else {
                    let hash = sp_io::hashing::keccak_256(&code);
                    push!(U256::from_big_endian(&hash));
                }
                pc += 1;
            }
"""
c = c.replace(insert_after, new_opcodes_3x)

# Add BLOCKHASH (0x40), TIMESTAMP (0x42 already exists?), NUMBER (0x43), GASLIMIT (0x45), SELFBALANCE (0x47), BASEFEE (0x48)
# Check what exists
# 0x41 = COINBASE, 0x42 = TIMESTAMP, 0x43 = NUMBER, 0x44 = PREVRANDAO, 0x45 = GASLIMIT
# 0x46 = CHAINID, 0x47 = SELFBALANCE, 0x48 = BASEFEE

# Add BLOCKHASH (0x40)
old_41 = "0x41 => { push!(U256::from_big_endian(ctx.coinbase.as_bytes())); pc += 1; }"
new_40_41 = """0x40 => {
                // BLOCKHASH - return zero for now (no historical block hash access in interpreter)
                push!(U256::zero());
                pc += 1;
            }
            0x41 => { push!(U256::from_big_endian(ctx.coinbase.as_bytes())); pc += 1; }"""
c = c.replace(old_41, new_40_41)

# Add SELFBALANCE (0x47) and BASEFEE (0x48)
# Find CHAINID (0x46)
old_46 = "0x46 => { push!(U256::from(ctx.chain_id)); pc += 1; }"
new_46_48 = """0x46 => { push!(U256::from(ctx.chain_id)); pc += 1; }
            0x47 => {
                // SELFBALANCE - placeholder (no balance tracking in interpreter)
                push!(U256::zero());
                pc += 1;
            }
            0x48 => {
                // BASEFEE - placeholder (no base fee in Substrate)
                push!(U256::zero());
                pc += 1;
            }"""
c = c.replace(old_46, new_46_48)

# Now add CALL, CALLCODE, DELEGATECALL, STATICCALL, CREATE, CREATE2
# Find SELFDESTRUCT (0xFF) and add before it, after RETURN (0xF3)
# Also need to handle CREATE (0xF0), CALL (0xF1), CALLCODE (0xF2), DELEGATECALL (0xF4), CREATE2 (0xF5), STATICCALL(0xFA)

# Find the RETURN opcode (0xF3) and add new opcodes before it
old_f3 = "0xF3 => {"
new_f0_f5 = """0xF0 => {
                // CREATE
                let value = pop!();
                let offset = pop!();
                let size = pop!();
                let off: usize = offset.try_into().unwrap_or(0);
                let sz: usize = size.try_into().unwrap_or(0);
                let init_code = ctx.memory.load(off, sz).map_err(|e| ExecutionError::from(e))?;
                // For now, create address from keccak256(rlp([sender, nonce]))
                let nonce = ctx.nonce;
                let mut data = Vec::new();
                data.extend_from_slice(ctx.address.as_bytes());
                data.extend_from_slice(&nonce.to_be_bytes::<8>());
                let hash = sp_io::hashing::keccak_256(&data);
                let new_addr = H160::from_slice(&hash[12..]);
                // Store the code at the new address
                crate::Pallet::<T>::set_code_for_create(new_addr, &init_code)?;
                ctx.return_data = init_code;
                push!(U256::from_big_endian(new_addr.as_bytes()));
                pc += 1;
            }
            0xF1 => {
                // CALL
                let gas = pop!();
                let addr = pop!();
                let value = pop!();
                let args_offset = pop!();
                let args_size = pop!();
                let ret_offset = pop!();
                let ret_size = pop!();
                let mut addr_bytes = [0u8; 20];
                addr.to_big_endian(&mut addr_bytes);
                let contract = H160::from_slice(&addr_bytes[..20]);
                let a_off: usize = args_offset.try_into().unwrap_or(0);
                let a_sz: usize = args_size.try_into().unwrap_or(0);
                let call_data = ctx.memory.load(a_off, a_sz).map_err(|e| ExecutionError::from(e))?;
                let result = crate::Pallet::<T>::execute_code(
                    crate::Pallet::<T>::get_code(contract).as_slice(),
                    &call_data,
                    gas.try_into().unwrap_or(100000),
                );
                match result {
                    crate::interpreter::ExecResult::Success { return_data, gas_used, .. } => {
                        let r_off: usize = ret_offset.try_into().unwrap_or(0);
                        let r_sz: usize = ret_size.try_into().unwrap_or(0);
                        let truncated = if return_data.len() >= r_sz { &return_data[..r_sz] } else { &return_data };
                        ctx.memory.store(r_off, truncated).map_err(|e| ExecutionError::from(e))?;
                        ctx.return_data = return_data;
                        push!(U256::one());
                    }
                    crate::interpreter::ExecResult::Reverted { return_data, .. } => {
                        let r_off: usize = ret_offset.try_into().unwrap_or(0);
                        let r_sz: usize = ret_size.try_into().unwrap_or(0);
                        let truncated = if return_data.len() >= r_sz { &return_data[..r_sz] } else { &return_data };
                        ctx.memory.store(r_off, truncated).map_err(|e| ExecutionError::from(e))?;
                        ctx.return_data = return_data;
                        push!(U256::zero());
                    }
                    crate::interpreter::ExecResult::Failed { .. } => {
                        push!(U256::zero());
                    }
                }
                pc += 1;
            }
            0xF2 => {
                // CALLCODE - same as CALL but execute in caller's context
                let gas = pop!();
                let addr = pop!();
                let value = pop!();
                let args_offset = pop!();
                let args_size = pop!();
                let ret_offset = pop!();
                let ret_size = pop!();
                let mut addr_bytes = [0u8; 20];
                addr.to_big_endian(&mut addr_bytes);
                let contract = H160::from_slice(&addr_bytes[..20]);
                let a_off: usize = args_offset.try_into().unwrap_or(0);
                let a_sz: usize = args_size.try_into().unwrap_or(0);
                let call_data = ctx.memory.load(a_off, a_sz).map_err(|e| ExecutionError::from(e))?;
                let code = crate::Pallet::<T>::get_code(contract);
                let result = crate::Pallet::<T>::execute_code(
                    &code,
                    &call_data,
                    gas.try_into().unwrap_or(100000),
                );
                match result {
                    crate::interpreter::ExecResult::Success { return_data, .. } => {
                        let r_off: usize = ret_offset.try_into().unwrap_or(0);
                        let r_sz: usize = ret_size.try_into().unwrap_or(0);
                        let truncated = if return_data.len() >= r_sz { &return_data[..r_sz] } else { &return_data };
                        ctx.memory.store(r_off, truncated).map_err(|e| ExecutionError::from(e))?;
                        ctx.return_data = return_data;
                        push!(U256::one());
                    }
                    crate::interpreter::ExecResult::Reverted { return_data, .. } => {
                        ctx.return_data = return_data;
                        push!(U256::zero());
                    }
                    crate::interpreter::ExecResult::Failed { .. } => {
                        push!(U256::zero());
                    }
                }
                pc += 1;
            }
            0xF3 => {"""

c = c.replace(old_f3, new_f0_f5)

# Add DELEGATECALL (0xF4), CREATE2 (0xF5), STATICCALL (0xFA) after RETURN
# Find RETURN block end and add after
old_return_end = "0xF4 => {"
# Check if 0xF4 already exists
if "0xF4 =>" not in c:
    # Find RETURN block and add after
    old_ff = "            0xFF => {"
    new_f4_fa = """            0xF4 => {
                // DELEGATECALL
                let gas = pop!();
                let addr = pop!();
                let args_offset = pop!();
                let args_size = pop!();
                let ret_offset = pop!();
                let ret_size = pop!();
                let mut addr_bytes = [0u8; 20];
                addr.to_big_endian(&mut addr_bytes);
                let contract = H160::from_slice(&addr_bytes[..20]);
                let a_off: usize = args_offset.try_into().unwrap_or(0);
                let a_sz: usize = args_size.try_into().unwrap_or(0);
                let call_data = ctx.memory.load(a_off, a_sz).map_err(|e| ExecutionError::from(e))?;
                let code = crate::Pallet::<T>::get_code(contract);
                let result = crate::Pallet::<T>::execute_code(
                    &code,
                    &call_data,
                    gas.try_into().unwrap_or(100000),
                );
                match result {
                    crate::interpreter::ExecResult::Success { return_data, .. } => {
                        let r_off: usize = ret_offset.try_into().unwrap_or(0);
                        let r_sz: usize = ret_size.try_into().unwrap_or(0);
                        let truncated = if return_data.len() >= r_sz { &return_data[..r_sz] } else { &return_data };
                        ctx.memory.store(r_off, truncated).map_err(|e| ExecutionError::from(e))?;
                        ctx.return_data = return_data;
                        push!(U256::one());
                    }
                    crate::interpreter::ExecResult::Reverted { return_data, .. } => {
                        ctx.return_data = return_data;
                        push!(U256::zero());
                    }
                    crate::interpreter::ExecResult::Failed { .. } => {
                        push!(U256::zero());
                    }
                }
                pc += 1;
            }
            0xF5 => {
                // CREATE2
                let value = pop!();
                let offset = pop!();
                let size = pop!();
                let salt = pop!();
                let off: usize = offset.try_into().unwrap_or(0);
                let sz: usize = size.try_into().unwrap_or(0);
                let init_code = ctx.memory.load(off, sz).map_err(|e| ExecutionError::from(e))?;
                // CREATE2 address: keccak256(0xFF ++ sender ++ salt ++ keccak256(init_code))
                let mut data = Vec::new();
                data.push(0xFF);
                data.extend_from_slice(ctx.address.as_bytes());
                let mut salt_bytes = [0u8; 32];
                salt.to_big_endian(&mut salt_bytes);
                data.extend_from_slice(&salt_bytes);
                let code_hash = sp_io::hashing::keccak_256(&init_code);
                data.extend_from_slice(&code_hash);
                let hash = sp_io::hashing::keccak_256(&data);
                let new_addr = H160::from_slice(&hash[12..]);
                crate::Pallet::<T>::set_code_for_create(new_addr, &init_code)?;
                ctx.return_data = init_code;
                push!(U256::from_big_endian(new_addr.as_bytes()));
                pc += 1;
            }
            0xFA => {
                // STATICCALL - like CALL but read-only
                let gas = pop!();
                let addr = pop!();
                let args_offset = pop!();
                let args_size = pop!();
                let ret_offset = pop!();
                let ret_size = pop!();
                let mut addr_bytes = [0u8; 20];
                addr.to_big_endian(&mut addr_bytes);
                let contract = H160::from_slice(&addr_bytes[..20]);
                let a_off: usize = args_offset.try_into().unwrap_or(0);
                let a_sz: usize = args_size.try_into().unwrap_or(0);
                let call_data = ctx.memory.load(a_off, a_sz).map_err(|e| ExecutionError::from(e))?;
                let code = crate::Pallet::<T>::get_code(contract);
                let result = crate::Pallet::<T>::execute_code(
                    &code,
                    &call_data,
                    gas.try_into().unwrap_or(100000),
                );
                match result {
                    crate::interpreter::ExecResult::Success { return_data, .. } => {
                        let r_off: usize = ret_offset.try_into().unwrap_or(0);
                        let r_sz: usize = ret_size.try_into().unwrap_or(0);
                        let truncated = if return_data.len() >= r_sz { &return_data[..r_sz] } else { &return_data };
                        ctx.memory.store(r_off, truncated).map_err(|e| ExecutionError::from(e))?;
                        ctx.return_data = return_data;
                        push!(U256::one());
                    }
                    crate::interpreter::ExecResult::Reverted { return_data, .. } => {
                        ctx.return_data = return_data;
                        push!(U256::zero());
                    }
                    crate::interpreter::ExecResult::Failed { .. } => {
                        push!(U256::zero());
                    }
                }
                pc += 1;
            }
            0xFF => {"""
    c = c.replace(old_ff, new_f4_fa)

# Add return_data and nonce fields to ExecutionContext
# Find the struct definition
old_struct = """pub struct ExecutionContext {
    pub code: Vec<u8>,
    pub address: H160,
    pub caller: H160,
    pub origin: H160,
    pub gas_limit: u64,
    pub gas_used: u64,
    pub value: U256,
    pub chain_id: u64,
    pub coinbase: H160,
    pub prev_randao: H256,
}"""

new_struct = """pub struct ExecutionContext {
    pub code: Vec<u8>,
    pub address: H160,
    pub caller: H160,
    pub origin: H160,
    pub gas_limit: u64,
    pub gas_used: u64,
    pub value: U256,
    pub chain_id: u64,
    pub coinbase: H160,
    pub prev_randao: H256,
    pub return_data: Vec<u8>,
    pub nonce: u64,
}"""

c = c.replace(old_struct, new_struct)

# Fix the struct construction in execute function
old_init = """let mut ctx = ExecutionContext {
            code: code.to_vec(),
            address: H160::zero(),
            caller: H160::zero(),
            origin: H160::zero(),
            gas_limit: gas,
            gas_used: 0,
            value: U256::zero(),
            chain_id: VERDIS_CHAIN_ID,
            coinbase: H160::zero(),
            prev_randao: H256::zero(),
        };"""

new_init = """let mut ctx = ExecutionContext {
            code: code.to_vec(),
            address: H160::zero(),
            caller: H160::zero(),
            origin: H160::zero(),
            gas_limit: gas,
            gas_used: 0,
            value: U256::zero(),
            chain_id: VERDIS_CHAIN_ID,
            coinbase: H160::zero(),
            prev_randao: H256::zero(),
            return_data: Vec::new(),
            nonce: 0,
        };"""

c = c.replace(old_init, new_init)

with open(interp_path, 'w') as f:
    f.write(c)
print('Interpreter updated with missing opcodes')

# === Now update lib.rs to add helper functions ===
with open(lib_path) as f:
    l = f.read()

# Add set_code_for_create function and make execute_code more accessible
# Find get_code function and add after it
old_get_code = """pub fn get_code(contract: H160) -> Vec<u8> {
            AccountCode::<T>::get(&contract).unwrap_or_default()
        }"""

new_get_code = """pub fn get_code(contract: H160) -> Vec<u8> {
            AccountCode::<T>::get(&contract).unwrap_or_default()
        }

        pub fn set_code_for_create(contract: H160, code: &[u8]) -> Result<(), Error<T>> {
            if code.len() as u32 > MAX_CODE_SIZE {
                return Err(Error::<T>::CodeTooLarge);
            }
            AccountCode::<T>::insert(&contract, code.to_vec());
            Ok(())
        }"""

l = l.replace(old_get_code, new_get_code)

with open(lib_path, 'w') as f:
    f.write(l)
print('lib.rs updated with set_code_for_create')
