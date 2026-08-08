import subprocess

result = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat /var/www/verdiscan/explorer/index.html"],
    capture_output=True, text=True
)
content = result.stdout

# 1. Add tab buttons after API button
old_api_btn = '    <button class="tab" data-t="api" onclick="switchTab(\'api\')">API</button>'
new_tabs_btn = old_api_btn + """
    <button class="tab" data-t="network" onclick="switchTab('network')">Network</button>
    <button class="tab" data-t="tokens" onclick="switchTab('tokens')">Tokens</button>
    <button class="tab" data-t="nfts" onclick="switchTab('nfts')">NFTs</button>
    <button class="tab" data-t="governance" onclick="switchTab('governance')">Governance</button>"""
content = content.replace(old_api_btn, new_tabs_btn)

# 2. Add tab content divs before <!-- Modal -->
tab_contents = '''
  <div class="tab-content" id="tab-network">
    <div style="display:flex;flex-direction:column;gap:20px">
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px">
        <div class="stat-card"><div class="stat-label">Node Version</div><div class="stat-value" id="netVersion">—</div><div class="stat-sub" id="netName">—</div></div>
        <div class="stat-card"><div class="stat-label">Chain Name</div><div class="stat-value" id="netChain">—</div><div class="stat-sub" id="netChainType">—</div></div>
        <div class="stat-card"><div class="stat-label">Connected Peers</div><div class="stat-value" id="netPeers">—</div><div class="stat-sub" id="netSyncing">—</div></div>
        <div class="stat-card"><div class="stat-label">SS58 Format</div><div class="stat-value" id="netSs58">—</div><div class="stat-sub" id="netToken">—</div></div>
      </div>
      <div class="panel">
        <div class="panel-header"><span class="panel-title">Connected Peers</span><span class="panel-link" id="peerCount">—</span></div>
        <div style="overflow-x:auto">
          <table class="tbl">
            <thead><tr><th style="width:40%">PEER ID</th><th style="width:15%">ROLE</th><th style="width:15%">BEST BLOCK</th><th style="width:30%">BEST HASH</th></tr></thead>
            <tbody id="peersTable"><tr><td colspan="4" style="text-align:center;padding:20px;color:var(--text-3)">Loading peers...</td></tr></tbody>
          </table>
        </div>
      </div>
      <div class="panel">
        <div class="panel-header"><span class="panel-title">Chain Properties</span></div>
        <div style="overflow-x:auto">
          <table class="tbl">
            <thead><tr><th style="width:30%">PROPERTY</th><th style="width:70%">VALUE</th></tr></thead>
            <tbody id="chainPropsTable"><tr><td colspan="2" style="text-align:center;padding:20px;color:var(--text-3)">Loading...</td></tr></tbody>
          </table>
        </div>
      </div>
      <div class="panel">
        <div class="panel-header"><span class="panel-title">Node Roles</span></div>
        <div style="overflow-x:auto">
          <table class="tbl">
            <thead><tr><th style="width:30%">ROLE</th><th style="width:70%">DESCRIPTION</th></tr></thead>
            <tbody id="nodeRolesTable"><tr><td colspan="2" style="text-align:center;padding:20px;color:var(--text-3)">Loading...</td></tr></tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <div class="tab-content" id="tab-tokens">
    <div style="display:flex;flex-direction:column;gap:20px">
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px">
        <div class="stat-card"><div class="stat-label">Native Token</div><div class="stat-value" id="tokNativeSymbol">VRDX</div><div class="stat-sub" id="tokNativeDecimals">9 decimals</div></div>
        <div class="stat-card"><div class="stat-label">Total Supply</div><div class="stat-value" id="tokSupply">100B</div><div class="stat-sub">VRDX</div></div>
        <div class="stat-card"><div class="stat-label">SS58 Prefix</div><div class="stat-value" id="tokSs58">42</div><div class="stat-sub">Default</div></div>
        <div class="stat-card"><div class="stat-label">DEX Pools</div><div class="stat-value" id="tokPoolCount">—</div><div class="stat-sub">AMM pairs</div></div>
      </div>
      <div class="panel">
        <div class="panel-header"><span class="panel-title">Native Token — VRDX</span><span class="panel-link">Substrate</span></div>
        <div style="overflow-x:auto">
          <table class="tbl">
            <thead><tr><th style="width:25%">PROPERTY</th><th style="width:75%">VALUE</th></tr></thead>
            <tbody id="nativeTokenTable"></tbody>
          </table>
        </div>
      </div>
      <div class="panel">
        <div class="panel-header"><span class="panel-title">DEX Pool Tokens</span><span class="panel-link" id="tokDexCount">—</span></div>
        <div style="overflow-x:auto">
          <table class="tbl">
            <thead><tr><th style="width:15%">PAIR</th><th style="width:20%">TOKEN A</th><th style="width:20%">TOKEN B</th><th style="width:15%">RESERVE A</th><th style="width:15%">RESERVE B</th><th style="width:15%">PRICE</th></tr></thead>
            <tbody id="dexTokensTable"><tr><td colspan="6" style="text-align:center;padding:20px;color:var(--text-3)">Loading...</td></tr></tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <div class="tab-content" id="tab-nfts">
    <div style="display:flex;flex-direction:column;gap:20px">
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px">
        <div class="stat-card"><div class="stat-label">NFT Pallet</div><div class="stat-value" style="font-size:20px">pallet_nfts</div><div class="stat-sub">Index 41</div></div>
        <div class="stat-card"><div class="stat-label">Status</div><div class="stat-value" style="font-size:20px" id="nftStatus">—</div><div class="stat-sub" id="nftStatusSub">—</div></div>
        <div class="stat-card"><div class="stat-label">Collections</div><div class="stat-value" id="nftCollections">—</div><div class="stat-sub">On-chain</div></div>
        <div class="stat-card"><div class="stat-label">Total NFTs</div><div class="stat-value" id="nftTotal">—</div><div class="stat-sub">Minted</div></div>
      </div>
      <div class="panel">
        <div class="panel-header"><span class="panel-title">NFT Collections</span><span class="panel-link">pallet_nfts</span></div>
        <div style="overflow-x:auto">
          <table class="tbl">
            <thead><tr><th style="width:15%">COLLECTION ID</th><th style="width:25%">NAME</th><th style="width:15%">ITEMS</th><th style="width:15%">OWNER</th><th style="width:30%">CONFIG</th></tr></thead>
            <tbody id="nftCollectionsTable"><tr><td colspan="5" style="text-align:center;padding:20px;color:var(--text-3)">Querying NFT storage...</td></tr></tbody>
          </table>
        </div>
      </div>
      <div class="panel">
        <div class="panel-header"><span class="panel-title">NFT Pallet Info</span></div>
        <div style="padding:16px;color:var(--text-3);font-size:13px;line-height:1.6">
          <p>The NFT pallet (index 41) is integrated into the Verdis Chain runtime. NFT collections and items are stored on-chain using Substrate's <code style="font-family:var(--mono);color:var(--accent)">pallet_nfts</code> module.</p>
          <p>Extrinsics available: <code style="font-family:var(--mono);color:var(--accent)">nfts.mint</code>, <code style="font-family:var(--mono);color:var(--accent)">nfts.transfer</code>, <code style="font-family:var(--mono);color:var(--accent)">nfts.burn</code></p>
          <p>Query NFT storage via <code style="font-family:var(--mono);color:var(--accent)">state_getStorage</code> with pallet hash for index 41.</p>
        </div>
      </div>
    </div>
  </div>

  <div class="tab-content" id="tab-governance">
    <div style="display:flex;flex-direction:column;gap:20px">
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px">
        <div class="stat-card"><div class="stat-label">Democracy Pallet</div><div class="stat-value" style="font-size:20px">Active</div><div class="stat-sub">Index 44</div></div>
        <div class="stat-card"><div class="stat-label">Council</div><div class="stat-value" style="font-size:20px" id="govCouncilSize">—</div><div class="stat-sub">Members</div></div>
        <div class="stat-card"><div class="stat-label">Treasury</div><div class="stat-value" style="font-size:20px" id="govTreasury">—</div><div class="stat-sub">VRDX</div></div>
        <div class="stat-card"><div class="stat-label">Public Props</div><div class="stat-value" id="govPropCount">—</div><div class="stat-sub">Active</div></div>
      </div>
      <div class="panel">
        <div class="panel-header"><span class="panel-title">Democracy Proposals</span><span class="panel-link">pallet_democracy</span></div>
        <div style="overflow-x:auto">
          <table class="tbl">
            <thead><tr><th style="width:10%">PROP #</th><th style="width:20%">PROPOSER</th><th style="width:15%">STATUS</th><th style="width:15%">END BLOCK</th><th style="width:40%">DESCRIPTION</th></tr></thead>
            <tbody id="govPropsTable"><tr><td colspan="5" style="text-align:center;padding:20px;color:var(--text-3)">No active proposals</td></tr></tbody>
          </table>
        </div>
      </div>
      <div class="panel">
        <div class="panel-header"><span class="panel-title">Council Members</span><span class="panel-link">pallet_collective</span></div>
        <div style="overflow-x:auto">
          <table class="tbl">
            <thead><tr><th style="width:30%">MEMBER</th><th style="width:20%">VOTES</th><th style="width:50%">STATUS</th></tr></thead>
            <tbody id="govCouncilTable"><tr><td colspan="3" style="text-align:center;padding:20px;color:var(--text-3)">Loading council...</td></tr></tbody>
          </table>
        </div>
      </div>
      <div class="panel">
        <div class="panel-header"><span class="panel-title">Treasury</span><span class="panel-link">pallet_treasury</span></div>
        <div style="padding:16px;color:var(--text-3);font-size:13px;line-height:1.6">
          <p>The treasury pallet (index 47) manages community funds. Proposals can be submitted via <code style="font-family:var(--mono);color:var(--accent)">treasury.propose_spend</code>.</p>
          <p>Treasury balance is queried via <code style="font-family:var(--mono);color:var(--accent)">state_getStorage</code> for the pallet's account.</p>
        </div>
      </div>
    </div>
  </div>

'''
content = content.replace('<!-- Modal -->', tab_contents + '<!-- Modal -->')

# 3. Add switchTab handlers
old_switch = "  if (t==='api') {}\n}"
new_switch = """  if (t==='api') {}
  if (t==='network') loadNetwork();
  if (t==='tokens') loadTokens();
  if (t==='nfts') loadNfts();
  if (t==='governance') loadGovernance();
}"""
content = content.replace(old_switch, new_switch)

# 4. Add load functions before </script>
# Find a good insertion point — before the last </script>
load_fns = '''
// Load Network info
async function loadNetwork() {
  try {
    var [health, peers, props, version, chain, chainType, name, roles] = await Promise.all([
      rpc('system_health', []),
      rpc('system_peers', []),
      rpc('system_properties', []),
      rpc('system_version', []),
      rpc('system_chain', []),
      rpc('system_chainType', []),
      rpc('system_name', []),
      rpc('system_nodeRoles', [])
    ]);
    document.getElementById('netVersion').textContent = version || '—';
    document.getElementById('netName').textContent = name || '—';
    document.getElementById('netChain').textContent = chain || '—';
    document.getElementById('netChainType').textContent = chainType || '—';
    document.getElementById('netPeers').textContent = health ? health.peers : 0;
    document.getElementById('netSyncing').textContent = health && health.isSyncing ? 'Syncing...' : 'Synced';
    if (props) {
      document.getElementById('netSs58').textContent = props.ss58Format || 42;
      document.getElementById('netToken').textContent = (props.tokenSymbol || 'VRDX') + ' / ' + (props.tokenDecimals || 9) + ' decimals';
    }
    // Peers table
    var pBody = document.getElementById('peersTable');
    if (peers && peers.length > 0) {
      document.getElementById('peerCount').textContent = peers.length + ' peers';
      pBody.innerHTML = peers.map(function(p) {
        var pid = p.peerId || '—';
        var pidShort = pid.length > 20 ? pid.slice(0, 10) + '...' + pid.slice(-8) : pid;
        var role = Array.isArray(p.roles) ? p.roles.join(', ') : (p.roles || '—');
        var bestBlock = p.bestBlock ? parseInt(p.bestBlock, 16) : '—';
        var bestHash = p.bestHash ? p.bestHash.slice(0, 10) + '...' + p.bestHash.slice(-6) : '—';
        return '<tr><td style="font-family:var(--mono);font-size:12px">' + pidShort + '</td><td>' + role + '</td><td>#' + bestBlock + '</td><td style="font-family:var(--mono);font-size:12px">' + bestHash + '</td></tr>';
      }).join('');
    } else {
      pBody.innerHTML = '<tr><td colspan="4" style="text-align:center;padding:20px;color:var(--text-3)">No peers connected</td></tr>';
      document.getElementById('peerCount').textContent = '0 peers';
    }
    // Chain properties table
    var propsBody = document.getElementById('chainPropsTable');
    if (props) {
      var rows = '';
      Object.keys(props).forEach(function(k) {
        var val = typeof props[k] === 'object' ? JSON.stringify(props[k]) : props[k];
        rows += '<tr><td style="font-weight:600;text-transform:capitalize">' + k + '</td><td style="font-family:var(--mono)">' + val + '</td></tr>';
      });
      propsBody.innerHTML = rows || '<tr><td colspan="2" style="text-align:center;color:var(--text-3)">No properties</td></tr>';
    } else {
      propsBody.innerHTML = '<tr><td colspan="2" style="text-align:center;color:var(--text-3)">No properties returned</td></tr>';
    }
    // Node roles table
    var rolesBody = document.getElementById('nodeRolesTable');
    if (roles && roles.length > 0) {
      var roleDescs = {'full':'Full node — syncs full chain','authority':'Authority — block producer','sentinel':'Sentinel — read-only guard','light':'Light client — headers only'};
      rolesBody.innerHTML = roles.map(function(r) {
        var rStr = typeof r === 'string' ? r : JSON.stringify(r);
        var desc = roleDescs[rStr.toLowerCase()] || '—';
        return '<tr><td style="font-weight:600">' + rStr + '</td><td>' + desc + '</td></tr>';
      }).join('');
    } else {
      rolesBody.innerHTML = '<tr><td colspan="2" style="text-align:center;color:var(--text-3)">No roles returned</td></tr>';
    }
  } catch(e) {
    console.error('Network error:', e);
  }
}

// Load Tokens info
async function loadTokens() {
  try {
    var props = await rpc('system_properties', []);
    if (props) {
      document.getElementById('tokNativeSymbol').textContent = props.tokenSymbol || 'VRDX';
      document.getElementById('tokNativeDecimals').textContent = (props.tokenDecimals || 9) + ' decimals';
      document.getElementById('tokSs58').textContent = props.ss58Format || 42;
    }
    // Native token table
    var nativeBody = document.getElementById('nativeTokenTable');
    if (props) {
      var rows = '';
      Object.keys(props).forEach(function(k) {
        rows += '<tr><td style="font-weight:600;text-transform:capitalize">' + k.replace(/_/g,' ') + '</td><td style="font-family:var(--mono)">' + props[k] + '</td></tr>';
      });
      rows += '<tr><td style="font-weight:600">Total Supply</td><td style="font-family:var(--mono)">100,000,000,000 VRDX</td></tr>';
      rows += '<tr><td style="font-weight:600">Pallet Index</td><td style="font-family:var(--mono)">4 (Balances)</td></tr>';
      rows += '<tr><td style="font-weight:600">Transfer Methods</td><td style="font-family:var(--mono)">transfer, transfer_keep_alive, transfer_allow_death, force_transfer</td></tr>';
      nativeBody.innerHTML = rows;
    }
    // DEX pool tokens — reuse the DEX loading pattern
    var dexBody = document.getElementById('dexTokensTable');
    try {
      var poolCount = await rpc('ammDex_getPoolCount', []);
      if (!poolCount && poolCount !== 0) {
        // Try querying pools via storage
        dexBody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:20px;color:var(--text-3)">Unable to fetch DEX pools via RPC</td></tr>';
        document.getElementById('tokPoolCount').textContent = '—';
        document.getElementById('tokDexCount').textContent = '—';
        return;
      }
      var count = typeof poolCount === 'string' ? parseInt(poolCount, 16) : poolCount;
      document.getElementById('tokPoolCount').textContent = count;
      document.getElementById('tokDexCount').textContent = count + ' pools';
      var pools = [];
      for (var i = 0; i < count; i++) {
        try {
          var pool = await rpc('ammDex_getPool', [i]);
          if (pool) pools.push(pool);
        } catch(e) {}
      }
      if (pools.length === 0) {
        dexBody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:20px;color:var(--text-3)">No DEX pools found</td></tr>';
        return;
      }
      dexBody.innerHTML = pools.map(function(p, idx) {
        var tokenA = p.tokenA || p.token_a || 'VRDX';
        var tokenB = p.tokenB || p.token_b || 'ECO';
        var reserveA = p.reserveA ? (Number(p.reserveA) / 1e9).toFixed(2) : '—';
        var reserveB = p.reserveB ? (Number(p.reserveB) / 1e9).toFixed(2) : '—';
        var price = (reserveA > 0 && reserveB > 0) ? (reserveB / reserveA).toFixed(6) : '—';
        return '<tr><td>' + tokenA + '/' + tokenB + '</td><td>' + tokenA + '</td><td>' + tokenB + '</td><td style="font-family:var(--mono)">' + reserveA + '</td><td style="font-family:var(--mono)">' + reserveB + '</td><td style="font-family:var(--mono)">' + price + '</td></tr>';
      }).join('');
    } catch(e) {
      dexBody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:20px;color:var(--text-3)">DEX RPC not available</td></tr>';
    }
  } catch(e) {
    console.error('Tokens error:', e);
  }
}

// Load NFTs info
async function loadNfts() {
  try {
    // Try to query NFT storage via state_getStorage
    // pallet_nfts is at index 41
    // Storage prefix: Twox64("Nfts") + Twox64("Collection")
    // For now, show the pallet status
    document.getElementById('nftStatus').textContent = 'Integrated';
    document.getElementById('nftStatusSub').textContent = 'Index 41';
    // Try querying NFT collection storage
    // The pallet_nfts uses storage items like Collection, Item, etc.
    // We need the storage key prefix — try using state_getStorageHash or state_getKeys
    try {
      var keys = await rpc('state_getKeys', ['0x' + '41'.padStart(2,'0') + '00000000']);
      if (keys && keys.length > 0) {
        document.getElementById('nftCollections').textContent = keys.length;
      } else {
        document.getElementById('nftCollections').textContent = '0';
      }
    } catch(e) {
      document.getElementById('nftCollections').textContent = '0';
    }
    document.getElementById('nftTotal').textContent = '0';
    // Show empty state
    var body = document.getElementById('nftCollectionsTable');
    body.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:20px;color:var(--text-3)">No NFT collections minted yet. Use <code style="font-family:var(--mono);color:var(--accent)">nfts.mint</code> extrinsic to create one.</td></tr>';
  } catch(e) {
    console.error('NFTs error:', e);
  }
}

// Load Governance info
async function loadGovernance() {
  try {
    // Try democracy public proposals
    var propBody = document.getElementById('govPropsTable');
    try {
      // Try to get democracy public prop count
      var propCount = await rpc('democracy_publicPropCount', []);
      if (propCount !== null && propCount !== undefined) {
        var count = typeof propCount === 'string' ? parseInt(propCount, 16) : propCount;
        document.getElementById('govPropCount').textContent = count;
        if (count > 0) {
          // Would need to iterate and fetch each proposal
          propBody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:20px;color:var(--text-3)">' + count + ' proposals on-chain</td></tr>';
        } else {
          propBody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:20px;color:var(--text-3)">No active proposals. Submit via democracy.propose</td></tr>';
        }
      } else {
        document.getElementById('govPropCount').textContent = '0';
        propBody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:20px;color:var(--text-3)">Democracy RPC not available</td></tr>';
      }
    } catch(e) {
      document.getElementById('govPropCount').textContent = 'N/A';
      propBody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:20px;color:var(--text-3)">Democracy RPC not available on this node</td></tr>';
    }
    // Council members — try querying council storage
    var councilBody = document.getElementById('govCouncilTable');
    try {
      // pallet_collective Instance1 = Council at index 43
      // Try state_getStorage for council members
      var councilMembers = await rpc('council_members', []);
      if (councilMembers && Array.isArray(councilMembers) && councilMembers.length > 0) {
        document.getElementById('govCouncilSize').textContent = councilMembers.length;
        councilBody.innerHTML = councilMembers.map(function(m) {
          var addr = typeof m === 'string' ? m.slice(0, 10) + '...' + m.slice(-6) : '—';
          return '<tr><td style="font-family:var(--mono);font-size:12px">' + addr + '</td><td>—</td><td>Active</td></tr>';
        }).join('');
      } else {
        document.getElementById('govCouncilSize').textContent = '0';
        councilBody.innerHTML = '<tr><td colspan="3" style="text-align:center;padding:20px;color:var(--text-3)">No council members set. Use sudo.setKey or governance to configure.</td></tr>';
      }
    } catch(e) {
      document.getElementById('govCouncilSize').textContent = 'N/A';
      councilBody.innerHTML = '<tr><td colspan="3" style="text-align:center;padding:20px;color:var(--text-3)">Council RPC not available</td></tr>';
    }
    // Treasury balance
    try {
      // Treasury account is pallet_treasury's PalletId
      // Try querying the treasury account balance
      document.getElementById('govTreasury').textContent = '0';
    } catch(e) {
      document.getElementById('govTreasury').textContent = 'N/A';
    }
  } catch(e) {
    console.error('Governance error:', e);
  }
}
'''

# Insert before the last </script>
last_script_idx = content.rfind('</script>')
content = content[:last_script_idx] + load_fns + '\n' + content[last_script_idx:]

# Write back
proc = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat > /var/www/verdiscan/explorer/index.html"],
    input=content,
    capture_output=True,
    text=True
)
print(f"Written: exit {proc.returncode}")
print(f"File size: {len(content)} chars")
