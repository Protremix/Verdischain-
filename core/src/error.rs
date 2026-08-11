use thiserror::Error;

#[derive(Error, Debug)]
pub enum CoreError {
    #[error("Invalid address: {0}")]
    InvalidAddress(String),
    #[error("Invalid seed/key: {0}")]
    InvalidKey(String),
    #[error("Invalid signature: {0}")]
    InvalidSignature(String),
    #[error("RPC error: {0}")]
    Rpc(String),
    #[error("Network error: {0}")]
    Network(String),
    #[error("Scale decode error: {0}")]
    ScaleDecode(String),
    #[error("Scale encode error: {0}")]
    ScaleEncode(String),
    #[error("Storage error: {0}")]
    Storage(String),
    #[error("Insufficient balance: have {have}, need {need}")]
    InsufficientBalance { have: String, need: String },
    #[error("Account not found: {0}")]
    AccountNotFound(String),
    #[error("PIN required")]
    PinRequired,
    #[error("Invalid PIN")]
    InvalidPin,
    #[error("Biometric auth failed: {0}")]
    BiometricFailed(String),
    #[error("Not connected to node")]
    NotConnected,
    #[error("Extrinsic rejected: {0}")]
    ExtrinsicRejected(String),
    #[error("Metadata not found for pallet '{0}'")]
    MetadataNotFound(String),
    #[error("{0}")]
    Other(String),
}

impl From<serde_json::Error> for CoreError {
    fn from(e: serde_json::Error) -> Self {
        CoreError::Rpc(format!("JSON error: {}", e))
    }
}

impl From<hex::FromHexError> for CoreError {
    fn from(e: hex::FromHexError) -> Self {
        CoreError::InvalidKey(format!("Hex decode: {}", e))
    }
}

#[cfg(feature = "native")]
impl From<reqwest::Error> for CoreError {
    fn from(e: reqwest::Error) -> Self {
        CoreError::Network(format!("{}", e))
    }
}

pub type CoreResult<T> = Result<T, CoreError>;
