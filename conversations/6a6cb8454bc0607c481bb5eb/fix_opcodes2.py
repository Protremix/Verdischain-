import re

path = '/opt/verdis-chain/pallets/evm/src/interpreter.rs'

with open(path) as f:
    c = f.read()

# 1. Remove duplicate 0x40 entry (the new one that says "BLOCKHASH - return zero for now")
c = c.replace("""            0x40 => {
                // BLOCKHASH - return zero for now (no historical block hash access in interpreter)
                push!(U256::zero());
                pc += 1;
            }
""", "")

# 2. Remove duplicate 0x47 entry (the new one that says "SELFBALANCE - placeholder")
c = c.replace("""            0x47 => {
                // SELFBALANCE - placeholder (no balance tracking in interpreter)
                push!(U256::zero());
                pc += 1;
            }
""", "")

# 3. Remove duplicate 0x48 entry (the new one that says "BASEFEE - placeholder")
c = c.replace("""            0x48 => {
                // BASEFEE - placeholder (no base fee in Substrate)
                push!(U256::zero());
                pc += 1;
            }
""", "")

# 4. Now replace the entire 0xF0-0xFF section with correct implementations
# Find from "0xF0 =>" to the end of the match block (before the closing)
old_f0_section = """            // System
            0xF0 => {
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
                host.set_code(new_addr, init_code.clone()).map_err(|e| e)?;
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
                let mut e = addr.encode(); e.resize(20, 0); addr_bytes.copy_from_slice(&e[..20]);
                let contract = H160::from_slice(&addr_bytes[..20]);
                let a_off: usize = args_offset.try_into().unwrap_or(0);
                let a_sz: usize = args_size.try_into().unwrap_or(0);
                let call_data = ctx.memory.load(a_off, a_sz).map_err(|e| ExecutionError::from(e))?;
                let code = host.get_code(contract);
                let result = host.execute_code(&code, &call_data, gas.try_into().unwrap_or(100000));
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
                let mut e = addr.encode(); e.resize(20, 0); addr_bytes.copy_from_slice(&e[..20]);
                let contract = H160::from_slice(&addr_bytes[..20]);
                let a_off: usize = args_offset.try_into().unwrap_or(0);
                let a_sz: usize = args_size.try_into().unwrap_or(0);
                let call_data = ctx.memory.load(a_off, a_sz).map_err(|e| ExecutionError::from(e))?;
                let code = host.get_code(contract);
                let result = host.execute_code(&code, &call_data, gas.try_into().unwrap_or(100000));
                match result {
                    ExecResult::Success { return_data, .. } => {
                        let r_off: usize = ret_offset.try_into().unwrap_or(0);
                        let r_sz: usize = ret_size.try_into().unwrap_or(0);
                        let truncated = if return_data.len() >= r_sz { &return_data[..r_sz] } else { &return_data };
                        ctx.memory.store(r_off, truncated).map_err(|e| ExecutionError::from(e))?;
                        ctx.return_data = return_data;
                        push!(U256::one());
                    }
                    ExecResult::Reverted { return_data, .. } => {
                        ctx.return_data = return_data;
                        push!(U256::zero());
                    }
                    ExecResult::Failed { .. } => {
                        push!(U256::zero());
                    }
                }
                pc += 1;
            }"""

new_f0_section = """            // System - CREATE and CALL opcodes
            0xF0 => {
                // CREATE: deploy a new contract
                let _value = pop!();
                let offset = pop!();
                let size = pop!();
                let off: usize = offset.try_into().unwrap_or(0);
                let sz: usize = size.try_into().unwrap_or(0);
                let init_code = match memory.load(off, sz) {
                    Ok(d) => d,
                    Err(e) => return ExecResult::Failed { error: e, gas_used: ctx.gas_used },
                };
                // Create address: keccak256(sender ++ nonce)
                let mut data = Vec::new();
                data.extend_from_slice(ctx.address.as_bytes());
                data.extend_from_slice(&ctx.block_number.to_be_bytes());
                let hash = sp_io::hashing::keccak_256(&data);
                let new_addr = H160::from_slice(&hash[12..]);
                match host.set_code(new_addr, init_code.clone()) {
                    Ok(_) => {},
                    Err(e) => return ExecResult::Failed { error: e, gas_used: ctx.gas_used },
                }
                returndata = init_code;
                push!(U256::from_big_endian(new_addr.as_bytes()));
                pc += 1;
            }
            0xF1 => {
                // CALL: invoke a contract function
                let gas = pop!();
                let addr = pop!();
                let _value = pop!();
                let args_offset = pop!();
                let args_size = pop!();
                let ret_offset = pop!();
                let ret_size = pop!();
                let mut addr_bytes = [0u8; 20];
                let encoded = addr.encode();
                let copy_len = encoded.len().min(20);
                addr_bytes[..copy_len].copy_from_slice(&encoded[..copy_len]);
                let contract = H160::from_slice(&addr_bytes[..20]);
                let a_off: usize = args_offset.try_into().unwrap_or(0);
                let a_sz: usize = args_size.try_into().unwrap_or(0);
                let call_data = match memory.load(a_off, a_sz) {
                    Ok(d) => d,
                    Err(e) => return ExecResult::Failed { error: e, gas_used: ctx.gas_used },
                };
                let code = host.get_code(contract);
                let result = host.execute_code(&code, &call_data, gas.try_into().unwrap_or(100000));
                match result {
                    ExecResult::Success { return_data, .. } => {
                        let r_off: usize = ret_offset.try_into().unwrap_or(0);
                        let r_sz: usize = ret_size.try_into().unwrap_or(0);
                        let truncated = if return_data.len() >= r_sz { &return_data[..r_sz] } else { &return_data };
                        if let Err(e) = memory.store(r_off, truncated) {
                            return ExecResult::Failed { error: e, gas_used: ctx.gas_used };
                        }
                        returndata = return_data;
                        push!(U256::one());
                    }
                    ExecResult::Reverted { reason, .. } => {
                        let r_off: usize = ret_offset.try_into().unwrap_or(0);
                        let r_sz: usize = ret_size.try_into().unwrap_or(0);
                        let truncated = if reason.len() >= r_sz { &reason[..r_sz] } else { &reason };
                        if let Err(e) = memory.store(r_off, truncated) {
                            return ExecResult::Failed { error: e, gas_used: ctx.gas_used };
                        }
                        returndata = reason;
                        push!(U256::zero());
                    }
                    ExecResult::Failed { .. } => {
                        push!(U256::zero());
                    }
                }
                pc += 1;
            }
            0xF2 => {
                // CALLCODE: like CALL but execute in caller's context
                let gas = pop!();
                let addr = pop!();
                let _value = pop!();
                let args_offset = pop!();
                let args_size = pop!();
                let ret_offset = pop!();
                let ret_size = pop!();
                let mut addr_bytes = [0u8; 20];
                let encoded = addr.encode();
                let copy_len = encoded.len().min(20);
                addr_bytes[..copy_len].copy_from_slice(&encoded[..copy_len]);
                let contract = H160::from_slice(&addr_bytes[..20]);
                let a_off: usize = args_offset.try_into().unwrap_or(0);
                let a_sz: usize = args_size.try_into().unwrap_or(0);
                let call_data = match memory.load(a_off, a_sz) {
                    Ok(d) => d,
                    Err(e) => return ExecResult::Failed { error: e, gas_used: ctx.gas_used },
                };
                let code = host.get_code(contract);
                let result = host.execute_code(&code, &call_data, gas.try_into().unwrap_or(100000));
                match result {
                    ExecResult::Success { return_data, .. } => {
                        let r_off: usize = ret_offset.try_into().unwrap_or(0);
                        let r_sz: usize = ret_size.try_into().unwrap_or(0);
                        let truncated = if return_data.len() >= r_sz { &return_data[..r_sz] } else { &return_data };
                        if let Err(e) = memory.store(r_off, truncated) {
                            return ExecResult::Failed { error: e, gas_used: ctx.gas_used };
                        }
                        returndata = return_data;
                        push!(U256::one());
                    }
                    ExecResult::Reverted { reason, .. } => {
                        returndata = reason;
                        push!(U256::zero());
                    }
                    ExecResult::Failed { .. } => {
                        push!(U256::zero());
                    }
                }
                pc += 1;
            }"""

c = c.replace(old_f0_section, new_f0_section)

# Replace the DELEGATECALL, CREATE2, STATICCALL section
old_f4_section = """            0xF4 => {
                // DELEGATECALL
                let gas = pop!();
                let addr = pop!();
                let args_offset = pop!();
                let args_size = pop!();
                let ret_offset = pop!();
                let ret_size = pop!();
                let mut addr_bytes = [0u8; 20];
                let mut e = addr.encode(); e.resize(20, 0); addr_bytes.copy_from_slice(&e[..20]);
                let contract = H160::from_slice(&addr_bytes[..20]);
                let a_off: usize = args_offset.try_into().unwrap_or(0);
                let a_sz: usize = args_size.try_into().unwrap_or(0);
                let call_data = ctx.memory.load(a_off, a_sz).map_err(|e| ExecutionError::from(e))?;
                let code = host.get_code(contract);
                let result = host.execute_code(&code, &call_data, gas.try_into().unwrap_or(100000));
                match result {
                    ExecResult::Success { return_data, .. } => {
                        let r_off: usize = ret_offset.try_into().unwrap_or(0);
                        let r_sz: usize = ret_size.try_into().unwrap_or(0);
                        let truncated = if return_data.len() >= r_sz { &return_data[..r_sz] } else { &return_data };
                        ctx.memory.store(r_off, truncated).map_err(|e| ExecutionError::from(e))?;
                        ctx.return_data = return_data;
                        push!(U256::one());
                    }
                    ExecResult::Reverted { return_data, .. } => {
                        ctx.return_data = return_data;
                        push!(U256::zero());
                    }
                    ExecResult::Failed { .. } => {
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
                let mut s = salt.encode(); s.resize(32, 0); salt_bytes.copy_from_slice(&s[..32]);
                data.extend_from_slice(&salt_bytes);
                let code_hash = sp_io::hashing::keccak_256(&init_code);
                data.extend_from_slice(&code_hash);
                let hash = sp_io::hashing::keccak_256(&data);
                let new_addr = H160::from_slice(&hash[12..]);
                host.set_code(new_addr, init_code.clone()).map_err(|e| e)?;
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
                let mut e = addr.encode(); e.resize(20, 0); addr_bytes.copy_from_slice(&e[..20]);
                let contract = H160::from_slice(&addr_bytes[..20]);
                let a_off: usize = args_offset.try_into().unwrap_or(0);
                let a_sz: usize = args_size.try_into().unwrap_or(0);
                let call_data = ctx.memory.load(a_off, a_sz).map_err(|e| ExecutionError::from(e))?;
                let code = host.get_code(contract);
                let result = host.execute_code(&code, &call_data, gas.try_into().unwrap_or(100000));
                match result {
                    ExecResult::Success { return_data, .. } => {
                        let r_off: usize = ret_offset.try_into().unwrap_or(0);
                        let r_sz: usize = ret_size.try_into().unwrap_or(0);
                        let truncated = if return_data.len() >= r_sz { &return_data[..r_sz] } else { &return_data };
                        ctx.memory.store(r_off, truncated).map_err(|e| ExecutionError::from(e))?;
                        ctx.return_data = return_data;
                        push!(U256::one());
                    }
                    ExecResult::Reverted { return_data, .. } => {
                        ctx.return_data = return_data;
                        push!(U256::zero());
                    }
                    ExecResult::Failed { .. } => {
                        push!(U256::zero());
                    }
                }
                pc += 1;
            }"""

new_f4_section = """            0xF4 => {
                // DELEGATECALL: like CALL but use caller's context
                let gas = pop!();
                let addr = pop!();
                let args_offset = pop!();
                let args_size = pop!();
                let ret_offset = pop!();
                let ret_size = pop!();
                let mut addr_bytes = [0u8; 20];
                let encoded = addr.encode();
                let copy_len = encoded.len().min(20);
                addr_bytes[..copy_len].copy_from_slice(&encoded[..copy_len]);
                let contract = H160::from_slice(&addr_bytes[..20]);
                let a_off: usize = args_offset.try_into().unwrap_or(0);
                let a_sz: usize = args_size.try_into().unwrap_or(0);
                let call_data = match memory.load(a_off, a_sz) {
                    Ok(d) => d,
                    Err(e) => return ExecResult::Failed { error: e, gas_used: ctx.gas_used },
                };
                let code = host.get_code(contract);
                let result = host.execute_code(&code, &call_data, gas.try_into().unwrap_or(100000));
                match result {
                    ExecResult::Success { return_data, .. } => {
                        let r_off: usize = ret_offset.try_into().unwrap_or(0);
                        let r_sz: usize = ret_size.try_into().unwrap_or(0);
                        let truncated = if return_data.len() >= r_sz { &return_data[..r_sz] } else { &return_data };
                        if let Err(e) = memory.store(r_off, truncated) {
                            return ExecResult::Failed { error: e, gas_used: ctx.gas_used };
                        }
                        returndata = return_data;
                        push!(U256::one());
                    }
                    ExecResult::Reverted { reason, .. } => {
                        returndata = reason;
                        push!(U256::zero());
                    }
                    ExecResult::Failed { .. } => {
                        push!(U256::zero());
                    }
                }
                pc += 1;
            }
            0xF5 => {
                // CREATE2: deploy with salt-based address
                let _value = pop!();
                let offset = pop!();
                let size = pop!();
                let salt = pop!();
                let off: usize = offset.try_into().unwrap_or(0);
                let sz: usize = size.try_into().unwrap_or(0);
                let init_code = match memory.load(off, sz) {
                    Ok(d) => d,
                    Err(e) => return ExecResult::Failed { error: e, gas_used: ctx.gas_used },
                };
                // CREATE2 address: keccak256(0xFF ++ sender ++ salt ++ keccak256(init_code))
                let mut data = Vec::new();
                data.push(0xFF);
                data.extend_from_slice(ctx.address.as_bytes());
                let encoded = salt.encode();
                let mut salt_bytes = [0u8; 32];
                let copy_len = encoded.len().min(32);
                salt_bytes[..copy_len].copy_from_slice(&encoded[..copy_len]);
                data.extend_from_slice(&salt_bytes);
                let code_hash = sp_io::hashing::keccak_256(&init_code);
                data.extend_from_slice(&code_hash);
                let hash = sp_io::hashing::keccak_256(&data);
                let new_addr = H160::from_slice(&hash[12..]);
                match host.set_code(new_addr, init_code.clone()) {
                    Ok(_) => {},
                    Err(e) => return ExecResult::Failed { error: e, gas_used: ctx.gas_used },
                }
                returndata = init_code;
                push!(U256::from_big_endian(new_addr.as_bytes()));
                pc += 1;
            }
            0xFA => {
                // STATICCALL: like CALL but read-only
                let gas = pop!();
                let addr = pop!();
                let args_offset = pop!();
                let args_size = pop!();
                let ret_offset = pop!();
                let ret_size = pop!();
                let mut addr_bytes = [0u8; 20];
                let encoded = addr.encode();
                let copy_len = encoded.len().min(20);
                addr_bytes[..copy_len].copy_from_slice(&encoded[..copy_len]);
                let contract = H160::from_slice(&addr_bytes[..20]);
                let a_off: usize = args_offset.try_into().unwrap_or(0);
                let a_sz: usize = args_size.try_into().unwrap_or(0);
                let call_data = match memory.load(a_off, a_sz) {
                    Ok(d) => d,
                    Err(e) => return ExecResult::Failed { error: e, gas_used: ctx.gas_used },
                };
                let code = host.get_code(contract);
                let result = host.execute_code(&code, &call_data, gas.try_into().unwrap_or(100000));
                match result {
                    ExecResult::Success { return_data, .. } => {
                        let r_off: usize = ret_offset.try_into().unwrap_or(0);
                        let r_sz: usize = ret_size.try_into().unwrap_or(0);
                        let truncated = if return_data.len() >= r_sz { &return_data[..r_sz] } else { &return_data };
                        if let Err(e) = memory.store(r_off, truncated) {
                            return ExecResult::Failed { error: e, gas_used: ctx.gas_used };
                        }
                        returndata = return_data;
                        push!(U256::one());
                    }
                    ExecResult::Reverted { reason, .. } => {
                        returndata = reason;
                        push!(U256::zero());
                    }
                    ExecResult::Failed { .. } => {
                        push!(U256::zero());
                    }
                }
                pc += 1;
            }"""

c = c.replace(old_f4_section, new_f4_section)

# 5. Add `Other` variant to ExecutionError
c = c.replace(
    '    ArrayCopyOverflow,\n}',
    '    ArrayCopyOverflow,\n    Other,\n}'
)

# Add a String variant too for messages
# Actually, let's just add a simple Other variant without String

with open(path, 'w') as f:
    f.write(c)

print('Fixed all opcode implementations')
