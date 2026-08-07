import os

pages_dir = "/var/www/verdiscan"

# 1. Update landing page to show live blockchain metrics
landing = os.path.join(pages_dir, "index.html")
with open(landing, "r") as f:
    content = f.read()

# Add live metrics script before </body>
live_metrics_js = """
<script>
// LIVE BLOCKCHAIN METRICS
async function updateLiveMetrics() {
  const RPC = '/rpc';
  try {
    // Get block height
    const blockRes = await fetch(RPC, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({jsonrpc: '2.0', method: 'chain_getHeader', params: [], id: 1})
    });
    const blockData = await blockRes.json();
    const blockHeight = parseInt(blockData.result?.number || '0x0', 16);
    
    // Get peer count
    const healthRes = await fetch(RPC, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({jsonrpc: '2.0', method: 'system_health', params: [], id: 2})
    });
    const healthData = await healthRes.json();
    const peers = healthData.result?.peers || 0;
    
    // Update any element with data-block-height
    document.querySelectorAll('[data-block-height]').forEach(el => {
      el.textContent = '#' + blockHeight.toLocaleString();
    });
    document.querySelectorAll('[data-peers]').forEach(el => {
      el.textContent = peers + ' Active';
    });
    document.querySelectorAll('[data-network-status]').forEach(el => {
      el.textContent = blockHeight > 0 ? 'Live' : 'Syncing';
    });
    
    // Update hero badge if present
    const badge = document.querySelector('.hero-badge, [class*="badge"]');
    if (badge && blockHeight > 0) {
      const statusText = badge.textContent;
      if (statusText.includes('#')) {
        badge.textContent = statusText.replace(/#\\d+/, '#' + blockHeight);
      }
    }
    
  } catch (e) {
    console.log('Live metrics: RPC not available, using cached data');
  }
}

// Run on load and every 15 seconds
updateLiveMetrics();
setInterval(updateLiveMetrics, 15000);
</script>
"""

if "LIVE BLOCKCHAIN METRICS" not in content:
    content = content.replace("</body>", live_metrics_js + "\n</body>")
    with open(landing, "w") as f:
        f.write(content)
    print("✓ Added live metrics to landing page")
else:
    print("  Live metrics already present")

# 2. Update the hero badge to show live block height
if "Testnet Live" in content:
    content = content.replace(
        "Testnet Live",
        'Testnet Live · Block <span data-block-height>##</span>'
    )
    # Only replace first occurrence
    content = content.replace('Block <span data-block-height>##</span> · Block <span data-block-height>##</span>', 'Block <span data-block-height>##</span>')
    with open(landing, "w") as f:
        f.write(content)
    print("✓ Updated hero badge with live block height")

# 3. Update explorer page to connect to live RPC
explorer = os.path.join(pages_dir, "explorer", "index.html")
if os.path.exists(explorer):
    with open(explorer, "r") as f:
        exp = f.read()
    
    if "LIVE EXPLORER" not in exp:
        # Add live explorer data fetching
        explorer_js = """
<script>
// LIVE EXPLORER DATA
const EXPLORER_RPC = '/rpc';
let explorerWs = null;

async function fetchExplorerData() {
  try {
    // Get latest block
    const blockRes = await fetch(EXPLORER_RPC, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({jsonrpc: '2.0', method: 'chain_getHeader', params: [], id: 1})
    });
    const blockData = await blockRes.json();
    const height = parseInt(blockData.result?.number || '0x0', 16);
    const hash = blockData.result?.parentHash || '';
    
    // Get health
    const healthRes = await fetch(EXPLORER_RPC, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({jsonrpc: '2.0', method: 'system_health', params: [], id: 2})
    });
    const healthData = await healthRes.json();
    
    // Get runtime version
    const versionRes = await fetch(EXPLORER_RPC, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({jsonrpc: '2.0', method: 'state_getRuntimeVersion', params: [], id: 3})
    });
    const versionData = await versionRes.json();
    
    // Update UI
    document.querySelectorAll('[data-explorer-height], #blockHeight, .block-height').forEach(el => {
      el.textContent = '#' + height.toLocaleString();
    });
    document.querySelectorAll('[data-explorer-peers], #peerCount, .peer-count').forEach(el => {
      el.textContent = (healthData.result?.peers || 0) + ' peers';
    });
    document.querySelectorAll('[data-explorer-hash], #blockHash, .block-hash').forEach(el => {
      el.textContent = hash.substring(0, 12) + '...';
    });
    
    // Update status indicator
    const status = document.querySelector('[data-explorer-status], .status-indicator, .live-indicator');
    if (status) {
      status.textContent = 'Live';
      status.style.color = '#caff33';
    }
    
    console.log('Explorer: Block #' + height + ', Peers: ' + (healthData.result?.peers || 0));
  } catch (e) {
    console.log('Explorer: RPC not available');
  }
}

// Connect to WebSocket for real-time updates
function connectWebSocket() {
  try {
    const wsUrl = (location.protocol === 'https:' ? 'wss:' : 'ws:') + '//' + location.host + '/ws';
    explorerWs = new WebSocket(wsUrl);
    
    explorerWs.onopen = function() {
      console.log('Explorer WebSocket connected');
      // Subscribe to new blocks
      explorerWs.send(JSON.stringify({
        jsonrpc: '2.0',
        method: 'chain_subscribeNewHeads',
        params: [],
        id: 1
      }));
    };
    
    explorerWs.onmessage = function(event) {
      try {
        const msg = JSON.parse(event.data);
        if (msg.params && msg.params.result) {
          const block = msg.params.result;
          const height = parseInt(block.number || '0x0', 16);
          console.log('New block: #' + height);
          document.querySelectorAll('[data-explorer-height], #blockHeight, .block-height').forEach(el => {
            el.textContent = '#' + height.toLocaleString();
          });
        }
      } catch (e) {}
    };
    
    explorerWs.onclose = function() {
      console.log('Explorer WebSocket disconnected, reconnecting in 5s...');
      setTimeout(connectWebSocket, 5000);
    };
    
    explorerWs.onerror = function() {
      console.log('Explorer WebSocket error');
    };
  } catch (e) {
    console.log('WebSocket not available, using polling');
  }
}

// Initialize
fetchExplorerData();
connectWebSocket();
setInterval(fetchExplorerData, 10000);
</script>
"""
        exp = exp.replace("</body>", explorer_js + "\n</body>")
        with open(explorer, "w") as f:
            f.write(exp)
        print("✓ Added live explorer data fetching")
    else:
        print("  Explorer live data already present")

# 4. Update the DEX page to show live block height in stats
dex = os.path.join(pages_dir, "dex", "index.html")
if os.path.exists(dex):
    with open(dex, "r") as f:
        dex_content = f.read()
    
    if "LIVE DEX METRICS" not in dex_content:
        dex_live_js = """
<script>
// LIVE DEX METRICS
async function updateDexLiveMetrics() {
  try {
    const res = await fetch('/rpc', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({jsonrpc: '2.0', method: 'chain_getHeader', params: [], id: 1})
    });
    const data = await res.json();
    const height = parseInt(data.result?.number || '0x0', 16);
    
    // Update any block height displays
    document.querySelectorAll('[data-block-height]').forEach(el => {
      el.textContent = '#' + height.toLocaleString();
    });
  } catch (e) {}
}
updateDexLiveMetrics();
setInterval(updateDexLiveMetrics, 15000);
</script>
"""
        dex_content = dex_content.replace("</body>", dex_live_js + "\n</body>")
        with open(dex, "w") as f:
            f.write(dex_content)
        print("✓ Added live metrics to DEX page")

# 5. Update wallet page to show live block height
wallet = os.path.join(pages_dir, "wallet", "index.html")
if os.path.exists(wallet):
    with open(wallet, "r") as f:
        wallet_content = f.read()
    
    if "LIVE WALLET METRICS" not in wallet_content:
        wallet_live_js = """
<script>
async function updateWalletLiveMetrics() {
  try {
    const res = await fetch('/rpc', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({jsonrpc: '2.0', method: 'chain_getHeader', params: [], id: 1})
    });
    const data = await res.json();
    const height = parseInt(data.result?.number || '0x0', 16);
    document.querySelectorAll('[data-block-height]').forEach(el => {
      el.textContent = '#' + height.toLocaleString();
    });
  } catch (e) {}
}
updateWalletLiveMetrics();
setInterval(updateWalletLiveMetrics, 15000);
</script>
"""
        wallet_content = wallet_content.replace("</body>", wallet_live_js + "\n</body>")
        with open(wallet, "w") as f:
            f.write(wallet_content)
        print("✓ Added live metrics to wallet page")

print("\n=== DONE ===")
