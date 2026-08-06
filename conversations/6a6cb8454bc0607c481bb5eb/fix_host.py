import sys

interp_path = '/opt/verdis-chain/pallets/evm/src/interpreter.rs'
lib_path = '/opt/verdis-chain/pallets/evm/src/lib.rs'

with open(interp_path) as f:
    c = f.read()

# 1. Add EvmHost trait after imports
trait_def = '''
/// Host interface for EVM interpreter to access external state
pub trait EvmHost {
    fn get_code(&self, contract: H160) -> Vec<u8>;
    fn set_code(&mut self, contract: H160, code: Vec<u8>) -> Result<(), ExecutionError>;
    fn execute_code(&self, code: &[u8], calldata: &[u8], gas: u64) -> ExecResult;
    fn get_storage(&self, contract: H160, key: H256) -> H256;
    fn set_storage_value(&mut self, contract: H160, key: H256, value: H256);
}

'''

# Insert after the constants
c = c.replace(
    '/// EVM execution result',
    trait_def + '/// EVM execution result'
)

# 2. Add return_data to ExecutionContext
c = c.replace(
    '    pub base_fee: U256,\n    pub self_balance: U256,\n    pub balance: U256,\n}',
    '    pub base_fee: U256,\n    pub self_balance: U256,\n    pub balance: U256,\n    pub return_data: Vec<u8>,\n}'
)

# 3. Make execute function take EvmHost
c = c.replace(
    'pub fn execute(ctx: &mut ExecutionContext) -> ExecResult {',
    'pub fn execute<H: EvmHost>(ctx: &mut ExecutionContext, host: &mut H) -> ExecResult {'
)

# 4. Replace all crate::Pallet::<T>:: calls with host calls
# EXTCODESIZE
c = c.replace(
    "let code = crate::Pallet::<T>::get_code(contract);\n                push!(U256::from(code.len() as u32));",
    "let code = host.get_code(contract);\n                push!(U256::from(code.len() as u32));"
)

# EXTCODECOPY
c = c.replace(
    "let code = crate::Pallet::<T>::get_code(contract);\n                let off: usize = offset.try_into().unwrap_or(0);\n                let sz: usize = size.try_into().unwrap_or(0);\n                let mut data = vec![0u8; sz];\n                if off < code.len() {\n                    let end = (off + sz).min(code.len());\n                    data[..end - off].copy_from_slice(&code[off..end]);\n                }\n                let dest: usize = dest_offset.try_into().unwrap_or(0);\n                ctx.memory.store(dest, &data).map_err(|e| ExecutionError::from(e))?",
    "let code = host.get_code(contract);\n                let off: usize = offset.try_into().unwrap_or(0);\n                let sz: usize = size.try_into().unwrap_or(0);\n                let mut data = vec![0u8; sz];\n                if off < code.len() {\n                    let end = (off + sz).min(code.len());\n                    data[..end - off].copy_from_slice(&code[off..end]);\n                }\n                let dest: usize = dest_offset.try_into().unwrap_or(0);\n                ctx.memory.store(dest, &data).map_err(|e| ExecutionError::from(e))?"
)

# EXTCODEHASH
c = c.replace(
    "let code = crate::Pallet::<T>::get_code(contract);\n                if code.is_empty() {",
    "let code = host.get_code(contract);\n                if code.is_empty() {"
)

# CREATE
c = c.replace(
    "crate::Pallet::<T>::set_code_for_create(new_addr, &init_code)?;",
    "host.set_code(new_addr, init_code.clone()).map_err(|e| e)?;"
)

# CALL
c = c.replace(
    "let result = crate::Pallet::<T>::execute_code(\n                    crate::Pallet::<T>::get_code(contract).as_slice(),\n                    &call_data,\n                    gas.try_into().unwrap_or(100000),\n                );",
    "let code = host.get_code(contract);\n                let result = host.execute_code(&code, &call_data, gas.try_into().unwrap_or(100000));"
)

# CALLCODE
c = c.replace(
    "let code = crate::Pallet::<T>::get_code(contract);\n                let result = crate::Pallet::<T>::execute_code(\n                    &code,\n                    &call_data,\n                    gas.try_into().unwrap_or(100000),\n                );\n                match result {\n                    crate::interpreter::ExecResult::Success { return_data, .. } => {\n                        let r_off: usize = ret_offset.try_into().unwrap_or(0);\n                        let r_sz: usize = ret_size.try_into().unwrap_or(0);\n                        let truncated = if return_data.len() >= r_sz { &return_data[..r_sz] } else { &return_data };\n                        ctx.memory.store(r_off, truncated).map_err(|e| ExecutionError::from(e))?;\n                        ctx.return_data = return_data;\n                        push!(U256::one());\n                    }\n                    crate::interpreter::ExecResult::Reverted { return_data, .. } => {\n                        let r_off: usize = ret_offset.try_into().unwrap_or(0);\n                        let r_sz: usize = ret_size.try_into().unwrap_or(0);\n                        let truncated = if return_data.len() >= r_sz { &return_data[..r_sz] } else { &return_data };\n                        ctx.memory.store(r_off, truncated).map_err(|e| ExecutionError::from(e))?;\n                        ctx.return_data = return_data;\n                        push!(U256::zero());\n                    }\n                    crate::interpreter::ExecResult::Failed { .. } => {\n                        push!(U256::zero());\n                    }\n                }",
    "let code = host.get_code(contract);\n                let result = host.execute_code(&code, &call_data, gas.try_into().unwrap_or(100000));\n                match result {\n                    ExecResult::Success { return_data, .. } => {\n                        let r_off: usize = ret_offset.try_into().unwrap_or(0);\n                        let r_sz: usize = ret_size.try_into().unwrap_or(0);\n                        let truncated = if return_data.len() >= r_sz { &return_data[..r_sz] } else { &return_data };\n                        ctx.memory.store(r_off, truncated).map_err(|e| ExecutionError::from(e))?;\n                        ctx.return_data = return_data;\n                        push!(U256::one());\n                    }\n                    ExecResult::Reverted { return_data, .. } => {\n                        let r_off: usize = ret_offset.try_into().unwrap_or(0);\n                        let r_sz: usize = ret_size.try_into().unwrap_or(0);\n                        let truncated = if return_data.len() >= r_sz { &return_data[..r_sz] } else { &return_data };\n                        ctx.memory.store(r_off, truncated).map_err(|e| ExecutionError::from(e))?;\n                        ctx.return_data = return_data;\n                        push!(U256::zero());\n                    }\n                    ExecResult::Failed { .. } => {\n                        push!(U256::zero());\n                    }\n                }"
)

# DELEGATECALL - replace the block that references crate::Pallet::<T>
c = c.replace(
    "let code = crate::Pallet::<T>::get_code(contract);\n                let result = crate::Pallet::<T>::execute_code(\n                    &code,\n                    &call_data,\n                    gas.try_into().unwrap_or(100000),\n                );\n                match result {\n                    crate::interpreter::ExecResult::Success { return_data, .. } => {\n                        let r_off: usize = ret_offset.try_into().unwrap_or(0);\n                        let r_sz: usize = ret_size.try_into().unwrap_or(0);\n                        let truncated = if return_data.len() >= r_sz { &return_data[..r_sz] } else { &return_data };\n                        ctx.memory.store(r_off, truncated).map_err(|e| ExecutionError::from(e))?;\n                        ctx.return_data = return_data;\n                        push!(U256::one());\n                    }\n                    crate::interpreter::ExecResult::Reverted { return_data, .. } => {\n                        ctx.return_data = return_data;\n                        push!(U256::zero());\n                    }\n                    crate::interpreter::ExecResult::Failed { .. } => {\n                        push!(U256::zero());\n                    }\n                }",
    "let code = host.get_code(contract);\n                let result = host.execute_code(&code, &call_data, gas.try_into().unwrap_or(100000));\n                match result {\n                    ExecResult::Success { return_data, .. } => {\n                        let r_off: usize = ret_offset.try_into().unwrap_or(0);\n                        let r_sz: usize = ret_size.try_into().unwrap_or(0);\n                        let truncated = if return_data.len() >= r_sz { &return_data[..r_sz] } else { &return_data };\n                        ctx.memory.store(r_off, truncated).map_err(|e| ExecutionError::from(e))?;\n                        ctx.return_data = return_data;\n                        push!(U256::one());\n                    }\n                    ExecResult::Reverted { return_data, .. } => {\n                        ctx.return_data = return_data;\n                        push!(U256::zero());\n                    }\n                    ExecResult::Failed { .. } => {\n                        push!(U256::zero());\n                    }\n                }"
)

# CREATE2
c = c.replace(
    "crate::Pallet::<T>::set_code_for_create(new_addr, &init_code)?;\n                ctx.return_data = init_code;",
    "host.set_code(new_addr, init_code.clone()).map_err(|e| e)?;\n                ctx.return_data = init_code;"
)

# STATICCALL - same pattern
c = c.replace(
    "let code = crate::Pallet::<T>::get_code(contract);\n                let result = crate::Pallet::<T>::execute_code(\n                    &code,\n                    &call_data,\n                    gas.try_into().unwrap_or(100000),\n                );\n                match result {\n                    crate::interpreter::ExecResult::Success { return_data, .. } => {\n                        let r_off: usize = ret_offset.try_into().unwrap_or(0);\n                        let r_sz: usize = ret_size.try_into().unwrap_or(0);\n                        let truncated = if return_data.len() >= r_sz { &return_data[..r_sz] } else { &return_data };\n                        ctx.memory.store(r_off, truncated).map_err(|e| ExecutionError::from(e))?;\n                        ctx.return_data = return_data;\n                        push!(U256::one());\n                    }\n                    crate::interpreter::ExecResult::Reverted { return_data, .. } => {\n                        ctx.return_data = return_data;\n                        push!(U256::zero());\n                    }\n                    crate::interpreter::ExecResult::Failed { .. } => {\n                        push!(U256::zero());\n                    }\n                }",
    "let code = host.get_code(contract);\n                let result = host.execute_code(&code, &call_data, gas.try_into().unwrap_or(100000));\n                match result {\n                    ExecResult::Success { return_data, .. } => {\n                        let r_off: usize = ret_offset.try_into().unwrap_or(0);\n                        let r_sz: usize = ret_size.try_into().unwrap_or(0);\n                        let truncated = if return_data.len() >= r_sz { &return_data[..r_sz] } else { &return_data };\n                        ctx.memory.store(r_off, truncated).map_err(|e| ExecutionError::from(e))?;\n                        ctx.return_data = return_data;\n                        push!(U256::one());\n                    }\n                    ExecResult::Reverted { return_data, .. } => {\n                        ctx.return_data = return_data;\n                        push!(U256::zero());\n                    }\n                    ExecResult::Failed { .. } => {\n                        push!(U256::zero());\n                    }\n                }"
)

# Fix to_big_endian calls (0 arguments in this version)
# Use encode() instead
c = c.replace('addr.to_big_endian(&mut addr_bytes)', 'let mut e = addr.encode(); e.resize(20, 0); addr_bytes.copy_from_slice(&e[..20])')
c = c.replace('salt.to_big_endian(&mut salt_bytes)', 'let mut s = salt.encode(); s.resize(32, 0); salt_bytes.copy_from_slice(&s[..32])')

# Fix the return_data initialization in execute function
# The execute function creates ExecutionContext somewhere - need to add return_data: Vec::new()
# Actually the context is created outside execute, in lib.rs. So we need to add it there.

with open(interp_path, 'w') as f:
    f.write(c)
print('Interpreter refactored with EvmHost trait')

# === Update lib.rs ===
with open(lib_path) as f:
    l = f.read()

# Add EvmHost implementation for Pallet<T>
host_impl = '''
impl<T: Config> interpreter::EvmHost for Pallet<T> {
    fn get_code(&self, contract: H160) -> Vec<u8> {
        AccountCode::<T>::get(&contract).unwrap_or_default()
    }

    fn set_code(&mut self, contract: H160, code: Vec<u8>) -> Result<(), interpreter::ExecutionError> {
        if code.len() as u32 > MAX_CODE_SIZE {
            return Err(interpreter::ExecutionError::Other("code too large"));
        }
        AccountCode::<T>::insert(&contract, code);
        Ok(())
    }

    fn execute_code(&self, code: &[u8], calldata: &[u8], gas: u64) -> interpreter::ExecResult {
        if code.is_empty() {
            return interpreter::ExecResult::Success {
                return_data: Vec::new(),
                gas_used: 0,
            };
        }
        let mut ctx = interpreter::ExecutionContext {
            caller: H160::zero(),
            address: H160::zero(),
            origin: H160::zero(),
            callvalue: U256::zero(),
            calldata,
            code,
            gas_limit: gas,
            gas_used: 0,
            chain_id: VERDIS_CHAIN_ID,
            block_number: frame_system::Pallet::<T>::block_number().try_into().unwrap_or(0),
            block_timestamp: 0,
            block_gaslimit: 30_000_000,
            coinbase: H160::zero(),
            gas_price: U256::zero(),
            prev_randao: H256::zero(),
            base_fee: U256::zero(),
            self_balance: U256::zero(),
            balance: U256::zero(),
            return_data: Vec::new(),
        };
        // We need a separate host for nested calls - use a dummy host for now
        let mut dummy = DummyHost::<T> { _phantom: Default::default() };
        interpreter::execute(&mut ctx, &mut dummy)
    }

    fn get_storage(&self, contract: H160, key: H256) -> H256 {
        ContractStorage::<T>::get(&contract, &key).unwrap_or_default()
    }

    fn set_storage_value(&mut self, contract: H160, key: H256, value: H256) {
        ContractStorage::<T>::insert(&contract, &key, value);
    }
}

/// Dummy host for nested calls (reads from storage, no writes)
struct DummyHost<T: Config> {
    _phantom: sp_std::marker::PhantomData<T>,
}

impl<T: Config> interpreter::EvmHost for DummyHost<T> {
    fn get_code(&self, contract: H160) -> Vec<u8> {
        AccountCode::<T>::get(&contract).unwrap_or_default()
    }

    fn set_code(&mut self, _contract: H160, _code: Vec<u8>) -> Result<(), interpreter::ExecutionError> {
        Err(interpreter::ExecutionError::Other("cannot set code in nested call"))
    }

    fn execute_code(&self, code: &[u8], calldata: &[u8], gas: u64) -> interpreter::ExecResult {
        if code.is_empty() {
            return interpreter::ExecResult::Success {
                return_data: Vec::new(),
                gas_used: 0,
            };
        }
        let mut ctx = interpreter::ExecutionContext {
            caller: H160::zero(),
            address: H160::zero(),
            origin: H160::zero(),
            callvalue: U256::zero(),
            calldata,
            code,
            gas_limit: gas,
            gas_used: 0,
            chain_id: VERDIS_CHAIN_ID,
            block_number: frame_system::Pallet::<T>::block_number().try_into().unwrap_or(0),
            block_timestamp: 0,
            block_gaslimit: 30_000_000,
            coinbase: H160::zero(),
            gas_price: U256::zero(),
            prev_randao: H256::zero(),
            base_fee: U256::zero(),
            self_balance: U256::zero(),
            balance: U256::zero(),
            return_data: Vec::new(),
        };
        let mut dummy = DummyHost::<T> { _phantom: Default::default() };
        interpreter::execute(&mut ctx, &mut dummy)
    }

    fn get_storage(&self, contract: H160, key: H256) -> H256 {
        ContractStorage::<T>::get(&contract, &key).unwrap_or_default()
    }

    fn set_storage_value(&mut self, _contract: H160, _key: H256, _value: H256) {
        // No-op in nested calls
    }
}

'''

# Insert the host impl after the Config impl
# Find a good insertion point - after the Config impl block
l = l.replace(
    'impl<T: Config> Pallet<T> {',
    host_impl + 'impl<T: Config> Pallet<T> {'
)

# Update execute_code function to use the new execute with host
old_execute = 'interpreter::execute(&mut ctx)'
new_execute = 'interpreter::execute(&mut ctx, self)'
l = l.replace(old_execute, new_execute)

# Also update any other call to interpreter::execute
l = l.replace('interpreter::execute(&mut ctx, &mut dummy)', 'interpreter::execute(&mut ctx, &mut dummy)')

with open(lib_path, 'w') as f:
    f.write(l)
print('lib.rs updated with EvmHost implementation')
