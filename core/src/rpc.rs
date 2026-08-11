use crate::error::{CoreError, CoreResult};
use serde::{Deserialize, Serialize};
use serde_json::Value;

/// JSON-RPC 2.0 client for Substrate nodes
/// 
/// Native implementation uses reqwest (blocking)
/// WASM implementation uses web-sys fetch (async)

#[cfg(feature = "native")]
pub struct RpcClient {
    url: String,
    client: reqwest::blocking::Client,
    request_id: std::cell::Cell<u64>,
}

#[cfg(feature = "native")]
impl RpcClient {
    pub fn new(url: &str) -> Self {
        RpcClient {
            url: url.to_string(),
            client: reqwest::blocking::Client::builder()
                .timeout(std::time::Duration::from_secs(30))
                .build()
                .expect("Failed to create HTTP client"),
            request_id: std::cell::Cell::new(1),
        }
    }

    pub fn request(&self, method: &str, params: Vec<Value>) -> CoreResult<Value> {
        let id = self.request_id.get();
        self.request_id.set(id + 1);

        let request = serde_json::json!({
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": id,
        });

        let response = self.client
            .post(&self.url)
            .header("Content-Type", "application/json")
            .json(&request)
            .send()
            .map_err(|e| CoreError::Network(format!("RPC request failed: {}", e)))?;

        if !response.status().is_success() {
            return Err(CoreError::Rpc(format!(
                "HTTP {}: {}",
                response.status(),
                response.status().canonical_reason().unwrap_or("Unknown")
            )));
        }

        let json: Value = response.json()
            .map_err(|e| CoreError::Rpc(format!("Failed to parse response: {}", e)))?;

        if let Some(error) = json.get("error") {
            return Err(CoreError::Rpc(format!(
                "RPC error {}: {}",
                error.get("code").and_then(|c| c.as_i64()).unwrap_or(-1),
                error.get("message").and_then(|m| m.as_str()).unwrap_or("Unknown")
            )));
        }

        json.get("result")
            .cloned()
            .ok_or_else(|| CoreError::Rpc("Missing result field".into()))
    }

    /// Subscribe to a JSON-RPC stream (WebSocket would be needed for full support)
    /// For now, this just does a single request
    pub fn url(&self) -> &str {
        &self.url
    }
}

#[cfg(feature = "wasm")]
pub struct RpcClient {
    url: String,
}

#[cfg(feature = "wasm")]
impl RpcClient {
    pub fn new(url: &str) -> Self {
        RpcClient { url: url.to_string() }
    }

    // In WASM, RPC calls are async and need to use fetch
    // This is a stub — the Flutter app will handle HTTP natively
    pub fn url(&self) -> &str {
        &self.url
    }
}

/// JSON-RPC request helper
pub fn build_rpc_request(id: u64, method: &str, params: Vec<Value>) -> Value {
    serde_json::json!({
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": id,
    })
}

/// Parse a JSON-RPC response
pub fn parse_rpc_response(response: &str) -> CoreResult<Value> {
    let json: Value = serde_json::from_str(response)
        .map_err(|e| CoreError::Rpc(format!("Invalid JSON: {}", e)))?;

    if let Some(error) = json.get("error") {
        return Err(CoreError::Rpc(format!(
            "RPC error: {}",
            error.get("message").and_then(|m| m.as_str()).unwrap_or("Unknown")
        )));
    }

    json.get("result")
        .cloned()
        .ok_or_else(|| CoreError::Rpc("Missing result field".into()))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_build_rpc_request() {
        let req = build_rpc_request(1, "chain_getBlockHash", vec![0.into()]);
        assert_eq!(req["jsonrpc"], "2.0");
        assert_eq!(req["method"], "chain_getBlockHash");
        assert_eq!(req["id"], 1);
    }

    #[test]
    fn test_parse_rpc_response_success() {
        let response = r#"{"jsonrpc":"2.0","id":1,"result":"0x1234"}"#;
        let result = parse_rpc_response(response).unwrap();
        assert_eq!(result, "0x1234");
    }

    #[test]
    fn test_parse_rpc_response_error() {
        let response = r#"{"jsonrpc":"2.0","id":1,"error":{"code":-32601,"message":"Method not found"}}"#;
        let result = parse_rpc_response(response);
        assert!(result.is_err());
    }
}
