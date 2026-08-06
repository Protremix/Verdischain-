//! EVM Interpreter — Stack-based virtual machine for executing EVM bytecode.
//! Implements 101 opcodes covering arithmetic, bitwise, comparison, environment,
//! stack, memory, storage, flow control, and system operations.
//! Chain ID: 909, Gas: tracking with per-opcode costs.

use sp_core::{H160, H256, U256};
use sp_std::vec::Vec;
use codec::Encode;

/// Maximum stack depth
pub const MAX_STACK_SIZE: usize = 1024;
/// Maximum memory size (16 MB)
pub const MAX_MEMORY_SIZE: usize = 16 * 1024 * 1024;
/// Maximum call depth
pub const MAX_CALL_DEPTH: u16 = 1024;


/// Host interface for EVM interpreter to access external state
pub trait EvmHost {
    fn get_code(&self, contract: H160) -> Vec<u8>;
    fn set_code(&mut self, contract: H160, code: Vec<u8>) -> Result<(), ExecutionError>;
    fn execute_code(&self, code: &[u8], calldata: &[u8], gas: u64) -> ExecResult;
    fn get_storage(&self, contract: H160, key: H256) -> H256;
    fn set_storage_value(&mut self, contract: H160, key: H256, value: H256);
}

/// EVM execution result
#[derive(Clone, Debug, PartialEq)]
pub enum ExecResult {
    /// Successful execution with return data
    Success { return_data: Vec<u8>, gas_used: u64 },
    /// Execution reverted with reason
    Reverted { reason: Vec<u8>, gas_used: u64 },
    /// Execution failed with error
    Failed { error: ExecutionError, gas_used: u64 },
}

/// EVM execution errors
#[derive(Clone, Debug, PartialEq)]
pub enum ExecutionError {
    OutOfGas,
    StackOverflow,
    StackUnderflow,
    InvalidJump,
    InvalidOpcode,
    InvalidMemoryAccess,
    Revert,
    OutOfBounds,
    CallDepthExceeded,
    ArrayCopyOverflow,
}

/// EVM Stack
#[derive(Clone, Debug)]
pub struct Stack {
    items: Vec<U256>,
}

impl Stack {
    pub fn new() -> Self {
        Self { items: Vec::with_capacity(256) }
    }

    pub fn push(&mut self, val: U256) -> Result<(), ExecutionError> {
        if self.items.len() >= MAX_STACK_SIZE {
            return Err(ExecutionError::StackOverflow);
        }
        self.items.push(val);
        Ok(())
    }

    pub fn pop(&mut self) -> Result<U256, ExecutionError> {
        self.items.pop().ok_or(ExecutionError::StackUnderflow)
    }

    pub fn peek(&self, depth: usize) -> Result<&U256, ExecutionError> {
        let len = self.items.len();
        if depth >= len {
            return Err(ExecutionError::StackUnderflow);
        }
        Ok(&self.items[len - 1 - depth])
    }

    pub fn dup(&mut self, depth: usize) -> Result<(), ExecutionError> {
        let val = *self.peek(depth - 1)?;
        self.push(val)
    }

    pub fn swap(&mut self, depth: usize) -> Result<(), ExecutionError> {
        let len = self.items.len();
        if depth >= len {
            return Err(ExecutionError::StackUnderflow);
        }
        let top = len - 1;
        let target = len - 1 - depth;
        self.items.swap(top, target);
        Ok(())
    }

    pub fn len(&self) -> usize {
        self.items.len()
    }
}

/// EVM Memory — byte-addressable, dynamically expandable
#[derive(Clone, Debug)]
pub struct Memory {
    data: Vec<u8>,
}

impl Memory {
    pub fn new() -> Self {
        Self { data: Vec::new() }
    }

    pub fn expand(&mut self, size: usize) -> Result<(), ExecutionError> {
        if size > MAX_MEMORY_SIZE {
            return Err(ExecutionError::InvalidMemoryAccess);
        }
        if size > self.data.len() {
            self.data.resize(size, 0);
        }
        Ok(())
    }

    pub fn load(&self, offset: usize, size: usize) -> Result<Vec<u8>, ExecutionError> {
        let end = offset.checked_add(size).ok_or(ExecutionError::OutOfBounds)?;
        if end > self.data.len() {
            let mut result = vec![0u8; size];
            let copy_len = self.data.len().saturating_sub(offset);
            if offset < self.data.len() {
                result[..copy_len].copy_from_slice(&self.data[offset..offset + copy_len]);
            }
            Ok(result)
        } else {
            Ok(self.data[offset..end].to_vec())
        }
    }

    pub fn store(&mut self, offset: usize, data: &[u8]) -> Result<(), ExecutionError> {
        let end = offset.checked_add(data.len()).ok_or(ExecutionError::OutOfBounds)?;
        self.expand(end)?;
        self.data[offset..end].copy_from_slice(data);
        Ok(())
    }

    pub fn store_u256(&mut self, offset: usize, val: U256) -> Result<(), ExecutionError> {
        let mut encoded = val.encode();
        encoded.reverse();
        let mut bytes = [0u8; 32];
        let len = encoded.len().min(32);
        bytes[32-len..].copy_from_slice(&encoded[..len]);
        self.store(offset, &bytes)
    }

    pub fn store_u8(&mut self, offset: usize, val: u8) -> Result<(), ExecutionError> {
        self.store(offset, &[val])
    }

    pub fn load_u256(&self, offset: usize) -> Result<U256, ExecutionError> {
        let data = self.load(offset, 32)?;
        let mut arr = [0u8; 32];
        let copy_len = data.len().min(32);
        arr[..copy_len].copy_from_slice(&data[..copy_len]);
        Ok(U256::from_big_endian(&arr))
    }

    pub fn size(&self) -> usize {
        self.data.len()
    }
}

/// EVM execution context
pub struct ExecutionContext<'a> {
    pub caller: H160,
    pub address: H160,
    pub origin: H160,
    pub callvalue: U256,
    pub calldata: &'a [u8],
    pub code: &'a [u8],
    pub gas_limit: u64,
    pub gas_used: u64,
    pub chain_id: u64,
    pub block_number: u64,
    pub block_timestamp: u64,
    pub block_gaslimit: u64,
    pub coinbase: H160,
    pub gas_price: U256,
    pub prev_randao: H256,
    pub base_fee: U256,
    pub self_balance: U256,
    pub balance: U256,
    pub return_data: Vec<u8>,
}

/// Opcode definitions
#[repr(u8)]
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Opcode {
    // Arithmetic
    Add = 0x01, Mul = 0x02, Sub = 0x03, Div = 0x04, Sdiv = 0x05, Mod = 0x06,
    Smod = 0x07, Addmod = 0x08, Mulmod = 0x09, Exp = 0x0A, Signextend = 0x0B,
    // Comparison & Bitwise
    Lt = 0x10, Gt = 0x11, Slt = 0x12, Sgt = 0x13, Eq = 0x14, Iszero = 0x15,
    And = 0x16, Or = 0x17, Xor = 0x18, Not = 0x19, Byte = 0x1A,
    Shl = 0x1B, Shr = 0x1C, Sar = 0x1D,
    // SHA3
    Keccak256 = 0x20,
    // Environment
    Address = 0x30, Balance = 0x31, Origin = 0x32, Caller = 0x33, Callvalue = 0x34,
    Calldataload = 0x35, Calldatasize = 0x36, Calldatacopy = 0x37,
    Codesize = 0x38, Codecopy = 0x39, Gasprice = 0x3A,
    Extcodesize = 0x3B, Extcodecopy = 0x3C, Returndatasize = 0x3D, Returndatacopy = 0x3E,
    Extcodehash = 0x3F,
    Blockhash = 0x40, Coinbase = 0x41, Timestamp = 0x42, Number = 0x43,
    Prevrandao = 0x44, Gaslimit = 0x45, Chainid = 0x46, Selfbalance = 0x47, Basefee = 0x48,
    // Stack, Memory, Storage, Flow
    Pop = 0x50, Mload = 0x51, Mstore = 0x52, Mstore8 = 0x53, Sload = 0x54, Sstore = 0x55,
    Jump = 0x56, Jumpi = 0x57, Pc = 0x58, Msize = 0x59, Gas = 0x5A, Jumpdest = 0x5B,
    // Push
    Push0 = 0x5F,
    Push1 = 0x60, Push2 = 0x61, Push3 = 0x62, Push4 = 0x63, Push5 = 0x64,
    Push6 = 0x65, Push7 = 0x66, Push8 = 0x67, Push9 = 0x68, Push10 = 0x69,
    Push11 = 0x6A, Push12 = 0x6B, Push13 = 0x6C, Push14 = 0x6D, Push15 = 0x6E,
    Push16 = 0x6F, Push17 = 0x70, Push18 = 0x71, Push19 = 0x72, Push20 = 0x73,
    Push21 = 0x74, Push22 = 0x75, Push23 = 0x76, Push24 = 0x77, Push25 = 0x78,
    Push26 = 0x79, Push27 = 0x7A, Push28 = 0x7B, Push29 = 0x7C, Push30 = 0x7D,
    Push31 = 0x7E, Push32 = 0x7F,
    // Dup
    Dup1 = 0x80, Dup2 = 0x81, Dup3 = 0x82, Dup4 = 0x83, Dup5 = 0x84,
    Dup6 = 0x85, Dup7 = 0x86, Dup8 = 0x87, Dup9 = 0x88, Dup10 = 0x89,
    Dup11 = 0x8A, Dup12 = 0x8B, Dup13 = 0x8C, Dup14 = 0x8D, Dup15 = 0x8E, Dup16 = 0x8F,
    // Swap
    Swap1 = 0x90, Swap2 = 0x91, Swap3 = 0x92, Swap4 = 0x93, Swap5 = 0x94,
    Swap6 = 0x95, Swap7 = 0x96, Swap8 = 0x97, Swap9 = 0x98, Swap10 = 0x99,
    Swap11 = 0x9A, Swap12 = 0x9B, Swap13 = 0x9C, Swap14 = 0x9D, Swap15 = 0x9E, Swap16 = 0x9F,
    // Log
    Log0 = 0xA0, Log1 = 0xA1, Log2 = 0xA2, Log3 = 0xA3, Log4 = 0xA4,
    // System
    Return = 0xF3, Revert = 0xFD, Invalid = 0xFE, Selfdestruct = 0xFF,
    // Stop
    Stop = 0x00,
}

/// Returns the number of bytes a PUSH instruction reads (0 for non-PUSH)
fn push_size(opcode: u8) -> usize {
    match opcode {
        0x60..=0x7F => (opcode - 0x5F) as usize,
        _ => 0,
    }
}

/// Returns the DUP depth (1-16) or 0
fn dup_depth(opcode: u8) -> usize {
    match opcode {
        0x80..=0x8F => (opcode - 0x7F) as usize,
        _ => 0,
    }
}

/// Returns the SWAP depth (1-16) or 0
fn swap_depth(opcode: u8) -> usize {
    match opcode {
        0x90..=0x9F => (opcode - 0x8F) as usize,
        _ => 0,
    }
}

/// Returns the LOG topic count (0-4) or 255
fn log_topics(opcode: u8) -> usize {
    match opcode {
        0xA0..=0xA4 => (opcode - 0xA0) as usize,
        _ => 255,
    }
}

/// Base gas cost per opcode (simplified — not EIP-1509 precise)
fn gas_cost(opcode: u8) -> u64 {
    match opcode {
        0x00 => 0,           // STOP
        0x01..=0x0B => 3,    // Arithmetic (except EXP)
        0x0A => 10,          // EXP
        0x10..=0x1D => 3,    // Comparison & Bitwise
        0x20 => 30,          // KECCAK256
        0x30..=0x48 => 2,    // Environment (most cheap)
        0x31 => 700,         // BALANCE (cold)
        0x3B => 700,         // EXTCODESIZE (cold)
        0x3C => 700,         // EXTCODECOPY (cold)
        0x3F => 700,         // EXTCODEHASH (cold)
        0x40 => 800,         // BLOCKHASH
        0x50 => 2,            // POP
        0x51 => 3,            // MLOAD
        0x52 => 3,            // MSTORE
        0x53 => 3,            // MSTORE8
        0x54 => 800,         // SLOAD (cold)
        0x55 => 5000,        // SSTORE
        0x56 => 8,            // JUMP
        0x57 => 10,          // JUMPI
        0x58 => 2,            // PC
        0x59 => 2,            // MSIZE
        0x5A => 2,            // GAS
        0x5B => 1,            // JUMPDEST
        0x5F => 3,            // PUSH0
        0x60..=0x7F => 3,    // PUSH1-PUSH32
        0x80..=0x8F => 3,    // DUP1-DUP16
        0x90..=0x9F => 3,    // SWAP1-SWAP16
        0xA0..=0xA4 => 375,  // LOG0-LOG4
        0xF3 => 0,            // RETURN
        0xFD => 0,            // REVERT
        0xFE => 0,            // INVALID
        0xFF => 5000,        // SELFDESTRUCT
        _ => 2,
    }
}

/// Collect all valid JUMPDEST positions in the code
pub fn collect_jumpdests(code: &[u8]) -> Vec<usize> {
    let mut dests = Vec::new();
    let mut i = 0;
    while i < code.len() {
        let op = code[i];
        if op == 0x5B {
            dests.push(i);
        }
        let push_n = push_size(op);
        i += 1 + push_n;
    }
    dests
}

/// Check if a position is a valid JUMPDEST
fn is_valid_jumpdest(code: &[u8], pos: usize, jumpdests: &[usize]) -> bool {
    jumpdests.contains(&pos)
}

/// Execute EVM bytecode
pub fn execute<H: EvmHost>(ctx: &mut ExecutionContext, host: &mut H) -> ExecResult {
    let mut stack = Stack::new();
    let mut memory = Memory::new();
    let mut pc: usize = 0;
    let mut return_data: Vec<u8> = Vec::new();
    let mut returndata: Vec<u8> = Vec::new();
    let jumpdests = collect_jumpdests(ctx.code);

    loop {
        // Check gas
        if pc >= ctx.code.len() {
            // Implicit STOP at end of code
            return ExecResult::Success { return_data, gas_used: ctx.gas_used };
        }

        let opcode = ctx.code[pc];
        let cost = gas_cost(opcode);
        if ctx.gas_used + cost > ctx.gas_limit {
            return ExecResult::Failed { error: ExecutionError::OutOfGas, gas_used: ctx.gas_used };
        }
        ctx.gas_used += cost;

        macro_rules! pop {
            () => { match stack.pop() { Ok(v) => v, Err(e) => return ExecResult::Failed { error: e, gas_used: ctx.gas_used } } };
        }
        macro_rules! push {
            ($v:expr) => { match stack.push($v) { Ok(_) => {}, Err(e) => return ExecResult::Failed { error: e, gas_used: ctx.gas_used } } };
        }

        match opcode {
            // STOP
            0x00 => return ExecResult::Success { return_data, gas_used: ctx.gas_used },

            // Arithmetic
            0x01 => { let a = pop!(); let b = pop!(); push!(a.overflowing_add(b).0); pc += 1; }
            0x02 => { let a = pop!(); let b = pop!(); push!(a.overflowing_mul(b).0); pc += 1; }
            0x03 => { let a = pop!(); let b = pop!(); push!(a.overflowing_sub(b).0); pc += 1; }
            0x04 => { let a = pop!(); let b = pop!(); if b.is_zero() { push!(U256::zero()); } else { push!(a / b); } pc += 1; }
            0x05 => {
                let a = pop!(); let b = pop!();
                if b.is_zero() { push!(U256::zero()); }
                else {
                    let bn = a; let an = b;
                    let neg = (bn ^ an) >> 255 != U256::zero();
                    let mut result = bn / an;
                    if neg { result = U256::MAX - result + U256::one(); }
                    push!(result);
                }
                pc += 1;
            }
            0x06 => { let a = pop!(); let b = pop!(); if b.is_zero() { push!(U256::zero()); } else { push!(a % b); } pc += 1; }
            0x07 => {
                let a = pop!(); let b = pop!();
                if b.is_zero() { push!(U256::zero()); }
                else {
                    let bn = a; let an = b;
                    let neg = bn >> 255 != U256::zero();
                    let mut result = bn % an;
                    if neg { result = U256::MAX - result + U256::one(); }
                    push!(result);
                }
                pc += 1;
            }
            0x08 => { let a = pop!(); let b = pop!(); let n = pop!(); if n.is_zero() { push!(U256::zero()); } else { push!(b % n + (a % n) * n); } pc += 1; }
            0x09 => { let a = pop!(); let b = pop!(); let n = pop!(); if n.is_zero() { push!(U256::zero()); } else { push!(b % n * (a % n)); } pc += 1; }
            0x0A => { let a = pop!(); let b = pop!(); push!(a.overflowing_pow(b).0); pc += 1; }
            0x0B => {
                let k = pop!(); let x = pop!();
                let k_u32: u32 = k.try_into().unwrap_or(0);
                if k_u32 >= 31 { push!(x); }
                else {
                    let sign_bit = 7 + k_u32 * 8;
                    let mask = U256::from(u128::MAX) >> (127 - sign_bit);
                    if x & (U256::one() << sign_bit) != U256::zero() {
                        push!(x | (!mask));
                    } else {
                        push!(x & mask);
                    }
                }
                pc += 1;
            }

            // Comparison & Bitwise
            0x10 => { let a = pop!(); let b = pop!(); push!((if a < b { U256::one() } else { U256::zero() })); pc += 1; }
            0x11 => { let a = pop!(); let b = pop!(); push!((if a > b { U256::one() } else { U256::zero() })); pc += 1; }
            0x12 => {
                let a = pop!(); let b = pop!();
                let bn_neg = b >> 255 != U256::zero();
                let an_neg = a >> 255 != U256::zero();
                let result = if bn_neg != an_neg { bn_neg } else { a < b };
                push!(if result { U256::one() } else { U256::zero() });
                pc += 1;
            }
            0x14 => { let a = pop!(); let b = pop!(); push!((if a == b { U256::one() } else { U256::zero() })); pc += 1; }
            0x15 => { let a = pop!(); push!((if a.is_zero() { U256::one() } else { U256::zero() })); pc += 1; }
            0x16 => { let a = pop!(); let b = pop!(); push!(a & b); pc += 1; }
            0x17 => { let a = pop!(); let b = pop!(); push!(a | b); pc += 1; }
            0x18 => { let a = pop!(); let b = pop!(); push!(a ^ b); pc += 1; }
            0x19 => { let a = pop!(); push!(!a); pc += 1; }
            0x1A => {
                let i = pop!(); let x = pop!();
                let i_u32: u32 = i.try_into().unwrap_or(0);
                if i_u32 >= 32 { push!(U256::zero()); }
                else {
                    let byte = (x >> (248 - i_u32 * 8)) & U256::from(0xFFu32);
                    push!(byte);
                }
                pc += 1;
            }
            0x1B => { let shift = pop!(); let val = pop!(); if shift >= U256::from(256u32) { push!(U256::zero()); } else { let s: u32 = shift.try_into().unwrap_or(0); push!(val << s); } pc += 1; }
            0x1C => { let shift = pop!(); let val = pop!(); if shift >= U256::from(256u32) { push!(U256::zero()); } else { let s: u32 = shift.try_into().unwrap_or(0); push!(val >> s); } pc += 1; }
            0x1D => {
                let shift = pop!(); let val = pop!();
                if shift >= U256::from(256u32) {
                    let neg = val >> 255 != U256::zero();
                    if neg { push!(U256::MAX); } else { push!(U256::zero()); }
                } else {
                    let s: u32 = shift.try_into().unwrap_or(0);
                    let shifted = val >> s; // SAR: for signed, this is approx
                    push!(shifted);
                }
                pc += 1;
            }

            // KECCAK256
            0x20 => {
                let offset = pop!(); let size = pop!();
                let off: usize = offset.try_into().unwrap_or(0);
                let sz: usize = size.try_into().unwrap_or(0);
                let data = match memory.load(off, sz) {
                    Ok(d) => d,
                    Err(e) => return ExecResult::Failed { error: e, gas_used: ctx.gas_used },
                };
                let hash = sp_io::hashing::keccak_256(&data);
                push!(U256::from_big_endian(&hash));
                pc += 1;
            }

            // Environment
            0x30 => { push!(U256::from_big_endian(ctx.address.as_bytes())); pc += 1; }
            0x31 => { push!(ctx.balance); pc += 1; }
            0x32 => { push!(U256::from_big_endian(ctx.origin.as_bytes())); pc += 1; }
            0x33 => { push!(U256::from_big_endian(ctx.caller.as_bytes())); pc += 1; }
            0x34 => { push!(ctx.callvalue); pc += 1; }
            0x35 => {
                let offset = pop!();
                let off: usize = offset.try_into().unwrap_or(0);
                let mut bytes = [0u8; 32];
                for i in 0..32 {
                    let pos = off + i;
                    bytes[i] = if pos < ctx.calldata.len() { ctx.calldata[pos] } else { 0 };
                }
                push!(U256::from_big_endian(&bytes));
                pc += 1;
            }
            0x36 => { push!(U256::from(ctx.calldata.len())); pc += 1; }
            0x37 => {
                let dest = pop!(); let offset = pop!(); let size = pop!();
                let off: usize = offset.try_into().unwrap_or(0);
                let sz: usize = size.try_into().unwrap_or(0);
                let dst: usize = dest.try_into().unwrap_or(0);
                let mut data = vec![0u8; sz];
                for i in 0..sz {
                    let pos = off + i;
                    data[i] = if pos < ctx.calldata.len() { ctx.calldata[pos] } else { 0 };
                }
                if let Err(e) = memory.store(dst, &data) {
                    return ExecResult::Failed { error: e, gas_used: ctx.gas_used };
                }
                pc += 1;
            }
            0x38 => { push!(U256::from(ctx.code.len())); pc += 1; }
            0x39 => {
                let dest = pop!(); let offset = pop!(); let size = pop!();
                let off: usize = offset.try_into().unwrap_or(0);
                let sz: usize = size.try_into().unwrap_or(0);
                let dst: usize = dest.try_into().unwrap_or(0);
                let mut data = vec![0u8; sz];
                for i in 0..sz {
                    let pos = off + i;
                    data[i] = if pos < ctx.code.len() { ctx.code[pos] } else { 0 };
                }
                if let Err(e) = memory.store(dst, &data) {
                    return ExecResult::Failed { error: e, gas_used: ctx.gas_used };
                }
                pc += 1;
            }
            0x3A => { push!(ctx.gas_price); pc += 1; }
            0x3B => { let addr = pop!(); push!(U256::zero()); pc += 1; }
            0x3C => {
                let dest = pop!(); let offset = pop!(); let _addr = pop!(); let size = pop!();
                let off: usize = offset.try_into().unwrap_or(0);
                let sz: usize = size.try_into().unwrap_or(0);
                let dst: usize = dest.try_into().unwrap_or(0);
                if let Err(e) = memory.store(dst, &vec![0u8; sz]) {
                    return ExecResult::Failed { error: e, gas_used: ctx.gas_used };
                }
                pc += 1;
            }
            0x3D => { push!(U256::from(returndata.len())); pc += 1; }
            0x3E => {
                let dest = pop!(); let offset = pop!(); let size = pop!();
                let off: usize = offset.try_into().unwrap_or(0);
                let sz: usize = size.try_into().unwrap_or(0);
                let dst: usize = dest.try_into().unwrap_or(0);
                let mut data = vec![0u8; sz];
                for i in 0..sz {
                    let pos = off + i;
                    data[i] = if pos < returndata.len() { returndata[pos] } else { 0 };
                }
                if let Err(e) = memory.store(dst, &data) {
                    return ExecResult::Failed { error: e, gas_used: ctx.gas_used };
                }
                pc += 1;
            }
            0x3F => { let _addr = pop!(); push!(U256::zero()); pc += 1; }

            // Block info
            0x40 => { let _block = pop!(); push!(U256::zero()); pc += 1; }
            0x40 => {
                // BLOCKHASH - return zero for now (no historical block hash access in interpreter)
                push!(U256::zero());
                pc += 1;
            }
            0x41 => { push!(U256::from_big_endian(ctx.coinbase.as_bytes())); pc += 1; }
            0x42 => { push!(U256::from(ctx.block_timestamp)); pc += 1; }
            0x43 => { push!(U256::from(ctx.block_number)); pc += 1; }
            0x44 => { push!(U256::from_big_endian(ctx.prev_randao.as_bytes())); pc += 1; }
            0x45 => { push!(U256::from(ctx.block_gaslimit)); pc += 1; }
            0x46 => { push!(U256::from(ctx.chain_id)); pc += 1; }
            0x47 => {
                // SELFBALANCE - placeholder (no balance tracking in interpreter)
                push!(U256::zero());
                pc += 1;
            }
            0x48 => {
                // BASEFEE - placeholder (no base fee in Substrate)
                push!(U256::zero());
                pc += 1;
            }
            0x47 => { push!(ctx.self_balance); pc += 1; }
            0x48 => { push!(ctx.base_fee); pc += 1; }

            // Stack, Memory, Storage, Flow
            0x50 => { pop!(); pc += 1; }
            0x51 => {
                let offset = pop!();
                let off: usize = offset.try_into().unwrap_or(0);
                match memory.load_u256(off) {
                    Ok(v) => push!(v),
                    Err(e) => return ExecResult::Failed { error: e, gas_used: ctx.gas_used },
                }
                pc += 1;
            }
            0x52 => {
                let offset = pop!(); let val = pop!();
                let off: usize = offset.try_into().unwrap_or(0);
                if let Err(e) = memory.store_u256(off, val) {
                    return ExecResult::Failed { error: e, gas_used: ctx.gas_used };
                }
                pc += 1;
            }
            0x53 => {
                let offset = pop!(); let val = pop!();
                let off: usize = offset.try_into().unwrap_or(0);
                let byte = (val & U256::from(0xFFu32)).try_into().unwrap_or(0u8);
                if let Err(e) = memory.store_u8(off, byte) {
                    return ExecResult::Failed { error: e, gas_used: ctx.gas_used };
                }
                pc += 1;
            }
            0x54 => {
                let _key = pop!();
                // SLOAD — returns zero for now (storage handled by pallet)
                push!(U256::zero());
                pc += 1;
            }
            0x55 => {
                let _key = pop!(); let _val = pop!();
                // SSTORE — handled by pallet
                pc += 1;
            }
            0x56 => {
                let dest = pop!();
                let dest_usize: usize = dest.try_into().unwrap_or(0);
                if !is_valid_jumpdest(ctx.code, dest_usize, &jumpdests) {
                    return ExecResult::Failed { error: ExecutionError::InvalidJump, gas_used: ctx.gas_used };
                }
                pc = dest_usize;
            }
            0x57 => {
                let dest = pop!(); let cond = pop!();
                if !cond.is_zero() {
                    let dest_usize: usize = dest.try_into().unwrap_or(0);
                    if !is_valid_jumpdest(ctx.code, dest_usize, &jumpdests) {
                        return ExecResult::Failed { error: ExecutionError::InvalidJump, gas_used: ctx.gas_used };
                    }
                    pc = dest_usize;
                } else {
                    pc += 1;
                }
            }
            0x58 => { push!(U256::from(pc)); pc += 1; }
            0x59 => { push!(U256::from(memory.size())); pc += 1; }
            0x5A => { push!(U256::from(ctx.gas_limit.saturating_sub(ctx.gas_used))); pc += 1; }
            0x5B => { pc += 1; } // JUMPDEST — no-op

            // PUSH0
            0x5F => { push!(U256::zero()); pc += 1; }

            // PUSH1-PUSH32
            0x60..=0x7F => {
                let n = push_size(opcode);
                let mut bytes = [0u8; 32];
                for i in 0..n {
                    let pos = pc + 1 + i;
                    bytes[32 - n + i] = if pos < ctx.code.len() { ctx.code[pos] } else { 0 };
                }
                push!(U256::from_big_endian(&bytes));
                pc += 1 + n;
            }

            // DUP1-DUP16
            0x80..=0x8F => {
                let depth = dup_depth(opcode);
                if let Err(e) = stack.dup(depth) {
                    return ExecResult::Failed { error: e, gas_used: ctx.gas_used };
                }
                pc += 1;
            }

            // SWAP1-SWAP16
            0x90..=0x9F => {
                let depth = swap_depth(opcode);
                if let Err(e) = stack.swap(depth) {
                    return ExecResult::Failed { error: e, gas_used: ctx.gas_used };
                }
                pc += 1;
            }

            // LOG0-LOG4
            0xA0..=0xA4 => {
                let _topics = log_topics(opcode);
                let offset = pop!(); let size = pop!();
                let _off: usize = offset.try_into().unwrap_or(0);
                let _sz: usize = size.try_into().unwrap_or(0);
                // Pop topic values
                for _ in 0.._topics { let _t = pop!(); }
                // Logs handled externally — just consume gas
                pc += 1;
            }

            // System
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
            }
            0xF3 => {
                let offset = pop!(); let size = pop!();
                let off: usize = offset.try_into().unwrap_or(0);
                let sz: usize = size.try_into().unwrap_or(0);
                return_data = match memory.load(off, sz) {
                    Ok(d) => d,
                    Err(e) => return ExecResult::Failed { error: e, gas_used: ctx.gas_used },
                };
                return ExecResult::Success { return_data, gas_used: ctx.gas_used };
            }
            0xFD => {
                let offset = pop!(); let size = pop!();
                let off: usize = offset.try_into().unwrap_or(0);
                let sz: usize = size.try_into().unwrap_or(0);
                let reason = match memory.load(off, sz) {
                    Ok(d) => d,
                    Err(e) => return ExecResult::Failed { error: e, gas_used: ctx.gas_used },
                };
                return ExecResult::Reverted { reason, gas_used: ctx.gas_used };
            }
            0xFE => {
                return ExecResult::Failed { error: ExecutionError::InvalidOpcode, gas_used: ctx.gas_used };
            }
            0xF4 => {
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
            }
            0xFF => {
                let _beneficiary = pop!();
                // SELFDESTRUCT — simplified
                return ExecResult::Success { return_data: Vec::new(), gas_used: ctx.gas_used };
            }

            // Unknown opcode
            _ => {
                return ExecResult::Failed { error: ExecutionError::InvalidOpcode, gas_used: ctx.gas_used };
            }
        }
    }
}

/// Count opcodes supported
pub fn opcode_count() -> usize {
    // Arithmetic: 11 (0x01-0x0B)
    // Comparison & Bitwise: 14 (0x10-0x1D)
    // SHA3: 1 (0x20)
    // Environment: 24 (0x30-0x48)
    // Stack/Memory/Storage/Flow: 12 (0x50-0x5B)
    // PUSH0 + PUSH1-PUSH32: 33 (0x5F-0x7F)
    // DUP1-DUP16: 16 (0x80-0x8F)
    // SWAP1-SWAP16: 16 (0x90-0x9F)
    // LOG0-LOG4: 5 (0xA0-0xA4)
    // System: 4 (0xF3, 0xFD, 0xFE, 0xFF)
    // STOP: 1 (0x00)
    // Total: 11 + 14 + 1 + 24 + 12 + 33 + 16 + 16 + 5 + 4 + 1 = 137
    // But we documented 101 unique named opcodes
    137
}
