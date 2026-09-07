const http = require('http');
const RPC_URL = 'http://127.0.0.1:9933';
const WS_PORT = 9944;

const WebSocket = require('ws');

// ─── ALLOWED METHODS WHITELIST ─────────────────────────────────────────────
// Only safe, read-only methods + signed transaction submission are allowed.
// Unsafe methods (author_insertKey, system_addReservedPeer, state_setStorage, etc.)
// are blocked at this layer. The Substrate node also runs with --rpc-methods=safe
// for defense-in-depth.
const ALLOWED_METHODS = new Set([
  // System (read-only)
  'system_health',
  'system_name',
  'system_version',
  'system_chain',
  'system_properties',
  'system_accountNextIndex',
  // Chain (read-only)
  'chain_getHeader',
  'chain_getBlock',
  'chain_getBlockHash',
  'chain_getFinalizedHead',
  'chain_getFinalisedHead',
  'chain_getHead',
  'chain_getHeadHash',  // alias
  'rpc_methods',
  // State (read-only)
  'state_getRuntimeVersion',
  'state_getStorage',
  'state_getKeysPaged',
  'state_getKeysPagedAt',
  'state_call',
  'state_getMetadata',
  'state_getStorageHash',
  'state_getStorageSize',
  // Payment
  'payment_queryInfo',
  'payment_queryFeeDetails',
  // Transaction submission (signed only — unsigned blocked by node --rpc-methods=safe)
  'author_submitExtrinsic',
  // Subscriptions (safe set)
  'chain_subscribeNewHeads',
  'chain_subscribeNewHead',
  'chain_subscribeAllHeads',
  'chain_subscribeFinalisedHeads',
  'chain_subscribeFinalizedHeads',
  'state_subscribeRuntimeVersion',
  'state_subscribeStorage',
  // Unsubscribe
  'chain_unsubscribeNewHeads',
  'chain_unsubscribeNewHead',
  'chain_unsubscribeAllHeads',
  'chain_unsubscribeFinalisedHeads',
  'chain_unsubscribeFinalizedHeads',
  'state_unsubscribeRuntimeVersion',
  'state_unsubscribeStorage',
]);

// Map subscription methods to their one-shot query equivalents
const subToQuery = {
  'chain_subscribeNewHeads': 'chain_getHeader',
  'chain_subscribeNewHead': 'chain_getHeader',
  'chain_subscribeAllHeads': 'chain_getHeader',
  'chain_subscribeFinalisedHeads': 'chain_getFinalizedHead',
  'chain_subscribeFinalizedHeads': 'chain_getFinalizedHead',
  'state_subscribeRuntimeVersion': 'state_getRuntimeVersion',
  'state_subscribeStorage': 'state_getStorage',
};

const wss = new WebSocket.Server({ port: WS_PORT, host: '127.0.0.1' });
console.log('WS proxy on ' + WS_PORT + ' -> ' + RPC_URL + ' (method-filtered)');

let subCounter = 1;

function rpcCall(method, params) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ jsonrpc: '2.0', method, params: params || [], id: 1 });
    const req = http.request(RPC_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }
    }, (res) => {
      let data = '';
      res.on('data', (c) => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch(e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

wss.on('connection', (ws) => {
  console.log('New WS connection');
  const subscriptions = new Map();
  
  ws.on('message', async (raw) => {
    let msg;
    try { msg = JSON.parse(raw); }
    catch(e) { return; }
    
    const method = msg.method || '';
    
    // ─── METHOD WHITELIST CHECK ─────────────────────────────────────────
    if (!ALLOWED_METHODS.has(method)) {
      console.log('BLOCKED WS method: ' + method);
      ws.send(JSON.stringify({
        jsonrpc: '2.0',
        id: msg.id,
        error: { code: -32601, message: 'Method not allowed: ' + method }
      }));
      return;
    }
    
    const isSubscribe = method.includes('subscribe') || method.includes('submitAndWatch');
    
    if (isSubscribe) {
      // Handle subscription: return sub ID and start polling
      const queryMethod = subToQuery[method];
      const subId = 'sub_' + (subCounter++);
      
      if (queryMethod) {
        // Send initial result (subscription ID)
        ws.send(JSON.stringify({ jsonrpc: '2.0', id: msg.id, result: subId }));
        
        // Send initial data
        try {
          const initial = await rpcCall(queryMethod, msg.params);
          if (initial.result !== undefined) {
            ws.send(JSON.stringify({
              jsonrpc: '2.0',
              method: 'state_storage',
              params: { subscription: subId, result: initial.result }
            }));
          }
        } catch(e) {}
        
        // Poll for changes
        let lastResult = null;
        const timer = setInterval(async () => {
          if (ws.readyState !== WebSocket.OPEN) { clearInterval(timer); return; }
          try {
            const result = await rpcCall(queryMethod, msg.params);
            const resultStr = JSON.stringify(result.result);
            if (resultStr !== lastResult) {
              lastResult = resultStr;
              ws.send(JSON.stringify({
                jsonrpc: '2.0',
                method: 'state_storage',
                params: { subscription: subId, result: result.result }
              }));
            }
          } catch(e) {}
        }, 3000);
        
        subscriptions.set(subId, { timer, method });
      } else {
        // Unknown subscription type - return error
        ws.send(JSON.stringify({ jsonrpc: '2.0', id: msg.id, error: { code: -32601, message: 'Unknown subscription method: ' + method } }));
      }
      
      // Handle unsubscribe
      if (msg.method && msg.method.includes('unsubscribe')) {
        const subId = msg.params && msg.params[0];
        if (subscriptions.has(subId)) {
          clearInterval(subscriptions.get(subId).timer);
          subscriptions.delete(subId);
        }
        ws.send(JSON.stringify({ jsonrpc: '2.0', id: msg.id, result: true }));
      }
    } else {
      // Regular RPC call - forward to HTTP
      try {
        const result = await rpcCall(method, msg.params);
        ws.send(JSON.stringify({ jsonrpc: '2.0', id: msg.id, result: result.result, error: result.error }));
      } catch(e) {
        ws.send(JSON.stringify({ jsonrpc: '2.0', id: msg.id, error: { code: -32603, message: e.message } }));
      }
    }
  });
  
  ws.on('close', () => {
    subscriptions.forEach(s => clearInterval(s.timer));
    subscriptions.clear();
    console.log('WS connection closed');
  });
  
  ws.on('error', () => {});
});
