//! Verdis Core — Shared wallet library for all platforms
//!
//! This crate provides the shared blockchain logic used by:
//! - Flutter mobile app (via FFI)
//! - Tauri desktop app (via direct linking)
//! - Web app (via WASM)
//! - Browser extension (via WASM)

pub mod error;
pub mod keypair;
pub mod ss58;
pub mod scale;
pub mod storage;
pub mod extrinsic;
pub mod rpc;
pub mod api;

// Re-export the most commonly used types
pub use error::{CoreError, CoreResult};
pub use keypair::Account;
pub use ss58::{encode_address, decode_address, decode_address_with_prefix, VERDIS_SS58_PREFIX};
pub use api::SubstrateApi;
pub use extrinsic::{Era, CallIndices, RewardDestination};

/// Library version
pub const VERSION: &str = "2.0.0";

/// Verdis Chain network configuration
#[derive(Clone, Debug)]
pub struct NetworkConfig {
    pub name: String,
    pub rpc_url: String,
    pub ws_url: String,
    pub chain_id: u64,
    pub ss58_prefix: u16,
    pub token_symbol: String,
    pub token_decimals: u8,
}

impl Default for NetworkConfig {
    fn default() -> Self {
        NetworkConfig {
            name: "Verdis Chain".to_string(),
            rpc_url: "https://verdischain.com/rpc".to_string(),
            ws_url: "wss://verdischain.com/ws".to_string(),
            chain_id: 909,
            ss58_prefix: 909,
            token_symbol: "VRS".to_string(),
            token_decimals: 9,
        }
    }
}

/// Convenience function to create a new SubstrateApi with Verdis defaults
pub fn connect(config: &NetworkConfig) -> SubstrateApi {
    SubstrateApi::new(&config.rpc_url)
}

/// Create a new wallet account
pub fn create_account(name: &str, pin: &str) -> CoreResult<Account> {
    Account::generate(name, pin)
}

/// Import a wallet from a hex seed
pub fn import_account(name: &str, pin: &str, seed_hex: &str) -> CoreResult<Account> {
    Account::from_seed(name, pin, seed_hex)
}

/// Import a wallet from a mnemonic phrase
pub fn import_account_from_mnemonic(name: &str, pin: &str, mnemonic: &str) -> CoreResult<Account> {
    Account::from_mnemonic(name, pin, mnemonic)
}

/// Format a balance amount with proper decimals
pub fn format_balance(amount: u128, decimals: u8) -> String {
    let divisor = 10u128.pow(decimals as u32);
    let whole = amount / divisor;
    let frac = amount % divisor;
    if frac == 0 {
        format!("{}", whole)
    } else {
        let frac_str = format!("{:0>width$}", frac, width = decimals as usize);
        let trimmed = frac_str.trim_end_matches('0');
        format!("{}.{}", whole, trimmed)
    }
}

/// Parse a human-readable balance string to raw units
pub fn parse_balance(amount_str: &str, decimals: u8) -> CoreResult<u128> {
    let parts: Vec<&str> = amount_str.split('.').collect();
    let whole: u128 = parts.get(0)
        .and_then(|s| s.parse().ok())
        .unwrap_or(0);
    let frac: u128 = if parts.len() > 1 {
        let frac_str = format!("{:0<width$}", parts[1], width = decimals as usize);
        let trimmed = &frac_str[..decimals as usize];
        trimmed.parse().unwrap_or(0)
    } else {
        0
    };
    let multiplier = 10u128.pow(decimals as u32);
    Ok(whole * multiplier + frac)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_format_balance() {
        assert_eq!(format_balance(1_000_000_000, 9), "1");
        assert_eq!(format_balance(1_500_000_000, 9), "1.5");
        assert_eq!(format_balance(1_234_567_890, 9), "1.23456789");
    }

    #[test]
    fn test_parse_balance() {
        assert_eq!(parse_balance("1", 9).unwrap(), 1_000_000_000);
        assert_eq!(parse_balance("1.5", 9).unwrap(), 1_500_000_000);
        assert_eq!(parse_balance("0.000000001", 9).unwrap(), 1);
    }

    #[test]
    fn test_default_config() {
        let config = NetworkConfig::default();
        assert_eq!(config.chain_id, 909);
        assert_eq!(config.ss58_prefix, 909);
        assert_eq!(config.token_symbol, "VRS");
    }
}
