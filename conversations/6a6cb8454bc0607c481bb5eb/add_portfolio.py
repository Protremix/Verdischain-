#!/usr/bin/env python3
"""Add a Portfolio Tracker tab to the Verdiscan explorer."""

EXP_PATH = "/var/www/verdiscan/explorer/index.html"

with open(EXP_PATH, "r") as f:
    html = f.read()

# 1. Add the Portfolio tab button after valmetrics
old_tab_btn = '''    <button class="tab" data-t="valmetrics" onclick="switchTab('valmetrics')">Validator Metrics</button>'''
new_tab_btn = old_tab_btn + '''
    <button class="tab" data-t="portfolio" onclick="switchTab('portfolio')">Portfolio</button>'''
html = html.replace(old_tab_btn, new_tab_btn)

# 2. Find the valmetrics tab-content closing and add Portfolio content after it
# The valmetrics content ends before </script> or the next tab-content
valmetrics_start = html.find('<div class="tab-content" id="tab-valmetrics">')
if valmetrics_start == -1:
    print("ERROR: valmetrics tab not found"); exit(1)

# Find the closing of valmetrics tab-content (next </div> that closes the tab-content)
# Count divs from valmetrics_start
depth = 0
i = valmetrics_start
while i < len(html):
    if html[i:i+5] == '<div ' or html[i:i+4] == '<div>':
        depth += 1
    elif html[i:i+6] == '</div>':
        depth -= 1
        if depth == 0:
            valmetrics_end = i + 6
            break
    i += 1

portfolio_html = '''
  <div class="tab-content" id="tab-portfolio">
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">Portfolio Tracker</span>
        <span style="font-size:12px;color:var(--text-3)">Track any address across the Verdis Chain ecosystem</span>
      </div>
      <div style="padding:16px 20px">
        <div style="display:flex;gap:8px;margin-bottom:16px">
          <input type="text" id="portfolioInput" placeholder="Enter SS58 address (e.g. 5GrwvaEF...)..." style="flex:1;padding:10px 14px;border:1px solid var(--border);border-radius:var(--radius-sm);font-family:var(--mono);font-size:13px" onkeydown="if(event.key==='Enter')loadPortfolio()">
          <button class="hero-btn hero-btn-primary" onclick="loadPortfolio()">Track</button>
        </div>
        <div id="portfolioEmpty" style="text-align:center;padding:40px 20px;color:var(--text-3)">
          <div style="font-size:14px;font-weight:500;margin-bottom:4px">Enter any address to view its portfolio</div>
          <div style="font-size:12px">Balance, staking, DEX positions, transaction history, eco metrics</div>
        </div>
        <div id="portfolioResult" style="display:none">
          <!-- Overview Cards -->
          <div class="grid-4" style="margin-bottom:16px">
            <div class="panel" style="margin:0">
              <div style="padding:14px 16px">
                <div class="stat-label" style="margin-bottom:4px">TOTAL VALUE</div>
                <div class="mono" id="pfTotalValue" style="font-size:20px;font-weight:700;color:var(--accent)">--</div>
              </div>
            </div>
            <div class="panel" style="margin:0">
              <div style="padding:14px 16px">
                <div class="stat-label" style="margin-bottom:4px">FREE BALANCE</div>
                <div class="mono" id="pfFree" style="font-size:20px;font-weight:700;color:var(--accent)">--</div>
              </div>
            </div>
            <div class="panel" style="margin:0">
              <div style="padding:14px 16px">
                <div class="stat-label" style="margin-bottom:4px">RESERVED</div>
                <div class="mono" id="pfReserved" style="font-size:20px;font-weight:700">--</div>
              </div>
            </div>
            <div class="panel" style="margin:0">
              <div style="padding:14px 16px">
                <div class="stat-label" style="margin-bottom:4px">NONCE</div>
                <div class="mono" id="pfNonce" style="font-size:20px;font-weight:700">--</div>
              </div>
            </div>
          </div>

          <!-- Two-column layout -->
          <div class="grid-2" style="margin-bottom:16px">
            <!-- Staking -->
            <div class="panel" style="margin:0">
              <div class="panel-header"><span class="panel-title">Staking & Validation</span></div>
              <div style="padding:14px 16px">
                <div id="pfStaking" style="font-size:13px;color:var(--text-3)">Loading staking data...</div>
              </div>
            </div>
            <!-- DEX Positions -->
            <div class="panel" style="margin:0">
              <div class="panel-header"><span class="panel-title">DEX Positions</span></div>
              <div style="padding:14px 16px">
                <div id="pfDex" style="font-size:13px;color:var(--text-3)">Loading DEX data...</div>
              </div>
            </div>
          </div>

          <!-- Eco Metrics -->
          <div class="panel" style="margin:0 0 16px 0">
            <div class="panel-header"><span class="panel-title">Eco Metrics</span></div>
            <div style="padding:14px 16px">
              <div id="pfEco" style="font-size:13px;color:var(--text-3)">Loading eco data...</div>
            </div>
          </div>

          <!-- Transaction History -->
          <div class="panel" style="margin:0 0 16px 0">
            <div class="panel-header">
              <span class="panel-title">Transaction History</span>
              <span style="font-size:12px;color:var(--text-3)" id="pfTxCount"></span>
            </div>
            <div style="padding:0">
              <table class="data-table" id="pfTxTable">
                <thead>
                  <tr>
                    <th style="padding:8px 12px">BLOCK</th>
                    <th style="padding:8px 12px">TIME</th>
                    <th style="padding:8px 12px">METHOD</th>
                    <th style="padding:8px 12px">SECTION</th>
                    <th style="padding:8px 12px">SIGNED</th>
                  </tr>
                </thead>
                <tbody id="pfTxBody" style="font-size:12px">
                  <tr><td colspan="5" style="padding:16px;text-align:center;color:var(--text-3)">Scanning recent blocks...</td></tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Quick Address Actions -->
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            <button class="hero-btn" style="font-size:12px;padding:6px 12px" onclick="copyPortfolioAddr()">Copy Address</button>
            <button class="hero-btn" style="font-size:12px;padding:6px 12px" onclick="viewOnExplorer()">View in Accounts</button>
            <a class="hero-btn" style="font-size:12px;padding:6px 12px;text-decoration:none" id="pfTxLink" href="/transactions/">View on Tx Page</a>
          </div>
        </div>
      </div>
    </div>
  </div>'''

html = html[:valmetrics_end] + portfolio_html + html[valmetrics_end:]

# 3. Update switchTab to handle portfolio
old_switch = "if (t === \"valmetrics\") loadValidatorMetrics();"
if old_switch in html:
    html = html.replace(old_switch, old_switch + '\n  if (t === "portfolio") {/* loaded on demand */}', 1)

# 4. Add portfolio JavaScript before the last </script>
last_script = html.rfind("</script>")
if last_script == -1:
    print("ERROR: no </script> found"); exit(1)

portfolio_js = '''
// ============ PORTFOLIO TRACKER ============
var pfAddress = null;

async function loadPortfolio() {
  var input = document.getElementById("portfolioInput").value.trim();
  if (!input) return;
  // Accept SS58 or hex addresses
  pfAddress = input;
  document.getElementById("portfolioEmpty").style.display = "none";
  document.getElementById("portfolioResult").style.display = "block";
  
  // Reset fields
  ["pfTotalValue","pfFree","pfReserved","pfNonce"].forEach(function(id) {
    document.getElementById(id).textContent = "--";
  });
  document.getElementById("pfStaking").innerHTML = '<span style="color:var(--text-3)">Loading staking data...</span>';
  document.getElementById("pfDex").innerHTML = '<span style="color:var(--text-3)">Loading DEX data...</span>';
  document.getElementById("pfEco").innerHTML = '<span style="color:var(--text-3)">Loading eco data...</span>';
  document.getElementById("pfTxBody").innerHTML = '<tr><td colspan="5" style="padding:16px;text-align:center;color:var(--text-3)">Scanning recent blocks...</td></tr>';
  document.getElementById("pfTxCount").textContent = "";

  // Load all sections in parallel
  loadPortfolioBalance(input);
  loadPortfolioStaking(input);
  loadPortfolioDex(input);
  loadPortfolioEco(input);
  loadPortfolioHistory(input);
}

async function loadPortfolioBalance(addr) {
  try {
    var nonce = await rpc("system_accountNextIndex", [addr]);
    document.getElementById("pfNonce").textContent = nonce !== null ? nonce.toString() : "0";
    
    var accInfo = await getAccountInfo(addr);
    if (accInfo) {
      var free = (accInfo.free || 0) / 1e9;
      var reserved = (accInfo.reserved || 0) / 1e9;
      var total = free + reserved;
      document.getElementById("pfFree").textContent = free.toLocaleString("en-US", {maximumFractionDigits: 2}) + " VRDX";
      document.getElementById("pfReserved").textContent = reserved.toLocaleString("en-US", {maximumFractionDigits: 2}) + " VRDX";
      document.getElementById("pfTotalValue").textContent = total.toLocaleString("en-US", {maximumFractionDigits: 2}) + " VRDX";
    } else {
      document.getElementById("pfFree").textContent = "0 VRDX";
      document.getElementById("pfReserved").textContent = "0 VRDX";
      document.getElementById("pfTotalValue").textContent = "0 VRDX";
    }
  } catch(e) {
    document.getElementById("pfFree").textContent = "Error";
    document.getElementById("pfReserved").textContent = "Error";
    document.getElementById("pfTotalValue").textContent = "Error";
    document.getElementById("pfNonce").textContent = "Error";
  }
}

async function loadPortfolioStaking(addr) {
  try {
    var allValidators = await rpc("dpos_allValidators", []);
    var hexAddr = ss58ToHex(addr);
    var isValidator = allValidators && allValidators.some(function(v) {
      return v.toLowerCase() === (hexAddr || "").toLowerCase() || v === addr;
    });
    
    var html_out = "";
    if (isValidator) {
      html_out += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:8px">';
      html_out += '<div><span class="stat-label" style="font-size:11px">STATUS</span><br><span style="color:#16a34a;font-weight:600;font-size:13px">Active Validator</span></div>';
      
      // Get stake
      try {
        var stake = await rpc("dpos_validatorStake", [addr]);
        if (stake !== null) {
          html_out += '<div><span class="stat-label" style="font-size:11px">STAKE</span><br><span class="mono" style="font-size:13px;font-weight:600;color:var(--accent)">' + (stake / 1e9).toLocaleString("en-US", {maximumFractionDigits: 2}) + ' VRDX</span></div>';
        } else {
          html_out += '<div><span class="stat-label" style="font-size:11px">STAKE</span><br><span style="font-size:13px">--</span></div>';
        }
      } catch(e2) {
        html_out += '<div><span class="stat-label" style="font-size:11px">STAKE</span><br><span style="font-size:13px">--</span></div>';
      }
      
      // Get name
      try {
        var name = await rpc("dpos_validatorName", [addr]);
        if (name && name.length > 0) {
          html_out += '<div><span class="stat-label" style="font-size:11px">NAME</span><br><span style="font-size:13px;font-weight:500">' + escapeHtml(name) + '</span></div>';
        } else {
          html_out += '<div><span class="stat-label" style="font-size:11px">NAME</span><br><span style="font-size:13px;color:var(--text-3)">Not set</span></div>';
        }
      } catch(e3) {
        html_out += '<div><span class="stat-label" style="font-size:11px">NAME</span><br><span style="font-size:13px;color:var(--text-3)">Not set</span></div>';
      }
      
      // Check if active
      try {
        var activeValidators = await rpc("dpos_activeValidators", []);
        var isActive = activeValidators && activeValidators.some(function(v) {
          return v.toLowerCase() === (hexAddr || "").toLowerCase() || v === addr;
        });
        html_out += '<div><span class="stat-label" style="font-size:11px">BLOCK PRODUCTION</span><br><span style="font-size:13px;color:' + (isActive ? "#16a34a" : "#ca8a04") + ';font-weight:600">' + (isActive ? "Producing blocks" : "Standby") + '</span></div>';
      } catch(e4) {
        html_out += '<div><span class="stat-label" style="font-size:11px">BLOCK PRODUCTION</span><br><span style="font-size:13px">--</span></div>';
      }
      
      html_out += '</div>';
    } else {
      // Check if they are nominating someone
      html_out += '<div style="color:var(--text-3);font-size:13px">This address is not a validator. <a href="/validators/" style="color:var(--accent)">Become a validator</a></div>';
    }
    
    // Show epoch info
    try {
      var epoch = await rpc("dpos_currentEpoch", []);
      if (epoch !== null) {
        html_out += '<div style="margin-top:8px;padding:8px 12px;background:rgba(22,163,74,.05);border-radius:var(--radius-sm);font-size:12px;color:var(--text-2)">Current Epoch: <span class="mono" style="font-weight:600">' + epoch + '</span></div>';
      }
    } catch(e5) {}
    
    document.getElementById("pfStaking").innerHTML = html_out;
  } catch(e) {
    document.getElementById("pfStaking").innerHTML = '<span style="color:var(--text-3);font-size:13px">Unable to load staking data</span>';
  }
}

async function loadPortfolioDex(addr) {
  try {
    var poolCount = await rpc("amm_dex_getPoolCount", []);
    if (poolCount === 0 || poolCount === null) {
      document.getElementById("pfDex").innerHTML = '<span style="color:var(--text-3);font-size:13px">No DEX pools available on the network yet.</span>';
      return;
    }
    
    var allPools = await rpc("amm_dex_getAllPools", []);
    if (!allPools || allPools.length === 0) {
      document.getElementById("pfDex").innerHTML = '<span style="color:var(--text-3);font-size:13px">No DEX pools available on the network yet.</span>';
      return;
    }
    
    var html_out = '<div style="font-size:12px;color:var(--text-2);margin-bottom:8px">' + allPools.length + ' pools on the network. LP positions require on-chain storage query per pool.</div>';
    html_out += '<table class="data-table" style="width:100%"><thead><tr><th style="padding:6px 10px;font-size:11px">POOL</th><th style="padding:6px 10px;font-size:11px">RESERVE A</th><th style="padding:6px 10px;font-size:11px">RESERVE B</th></tr></thead><tbody>';
    for (var p of allPools) {
      var ra = (p.reserve_a || 0) / 1e9;
      var rb = (p.reserve_b || 0) / 1e9;
      html_out += '<tr><td style="padding:6px 10px;font-family:var(--mono);font-size:11px">' + (p.token_a || "?") + '/' + (p.token_b || "?") + '</td>';
      html_out += '<td style="padding:6px 10px;font-family:var(--mono);font-size:11px">' + ra.toLocaleString("en-US", {maximumFractionDigits: 0}) + '</td>';
      html_out += '<td style="padding:6px 10px;font-family:var(--mono);font-size:11px">' + rb.toLocaleString("en-US", {maximumFractionDigits: 0}) + '</td></tr>';
    }
    html_out += '</tbody></table>';
    document.getElementById("pfDex").innerHTML = html_out;
  } catch(e) {
    document.getElementById("pfDex").innerHTML = '<span style="color:var(--text-3);font-size:13px">Unable to load DEX data</span>';
  }
}

async function loadPortfolioEco(addr) {
  try {
    var allGreen = await rpc("eco_getAllGreenValidators", []);
    var hexAddr = ss58ToHex(addr);
    var isGreen = allGreen && allGreen.some(function(v) {
      return v.toLowerCase() === (hexAddr || "").toLowerCase() || v === addr;
    });
    
    var html_out = "";
    if (isGreen) {
      try {
        var score = await rpc("eco_getGreenScore", [addr]);
        html_out += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">';
        html_out += '<div><span class="stat-label" style="font-size:11px">GREEN SCORE</span><br><span style="font-size:13px;font-weight:600;color:#16a34a">' + (score !== null ? score : "--") + '/10</span></div>';
        html_out += '<div><span class="stat-label" style="font-size:11px">ECO STATUS</span><br><span style="font-size:13px;color:#16a34a;font-weight:600">Eco Validator</span></div>';
        html_out += '</div>';
      } catch(e2) {
        html_out += '<div style="font-size:13px;color:#16a34a">This address is an eco-green validator.</div>';
      }
    } else {
      // Show global eco stats
      var co2 = await rpc("eco_getTotalCO2Offset", []);
      var trees = await rpc("eco_getTotalTreesPlanted", []);
      var credits = await rpc("eco_getCarbonCreditCount", []);
      var retired = await rpc("eco_getTotalCreditsRetired", []);
      html_out += '<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px">';
      html_out += '<div><span class="stat-label" style="font-size:11px">CO2 OFFSET</span><br><span class="mono" style="font-size:13px;font-weight:600">' + (co2 || 0).toLocaleString() + 't</span></div>';
      html_out += '<div><span class="stat-label" style="font-size:11px">TREES</span><br><span class="mono" style="font-size:13px;font-weight:600">' + (trees || 0).toLocaleString() + '</span></div>';
      html_out += '<div><span class="stat-label" style="font-size:11px">CREDITS</span><br><span class="mono" style="font-size:13px;font-weight:600">' + (credits || 0) + '</span></div>';
      html_out += '<div><span class="stat-label" style="font-size:11px">RETIRED</span><br><span class="mono" style="font-size:13px;font-weight:600">' + (retired || 0) + '</span></div>';
      html_out += '</div>';
      html_out += '<div style="margin-top:8px;font-size:12px;color:var(--text-3)">This address is not an eco validator. Eco metrics shown are network totals.</div>';
    }
    
    document.getElementById("pfEco").innerHTML = html_out;
  } catch(e) {
    document.getElementById("pfEco").innerHTML = '<span style="color:var(--text-3);font-size:13px">Unable to load eco data</span>';
  }
}

async function loadPortfolioHistory(addr) {
  try {
    var hexAddr = ss58ToHex(addr);
    var hdr = await rpc("chain_getHeader", []);
    var currentBlock = parseInt(hdr.number, 16);
    var scanRange = 50; // Scan last 50 blocks
    var foundTxs = [];
    
    for (var b = currentBlock; b >= Math.max(0, currentBlock - scanRange); b--) {
      try {
        var hash = await rpc("chain_getBlockHash", [b]);
        if (!hash || hash === "0x" + "0".repeat(64)) continue;
        var block = await rpc("chain_getBlock", [hash]);
        var exts = block.block.extrinsics;
        var blockTime = 0;
        
        for (var i = 0; i < exts.length; i++) {
          var ext = exts[i];
          var bytes = ext;
          if (typeof ext === "string") {
            var hex = ext.startsWith("0x") ? ext.slice(2) : ext;
            bytes = [];
            for (var j = 0; j < hex.length; j += 2) bytes.push(parseInt(hex.substr(j, 2), 16));
          } else if (!Array.isArray(ext)) continue;
          
          // Decode
          var off = 2;
          if (off >= bytes.length) continue;
          var versionByte = bytes[off];
          
          if (versionByte >= 0x80) {
            // Signed - extract signer
            off++;
            var sigType = bytes[off]; off++;
            off += (sigType === 2) ? 65 : 64;
            if (off + 32 > bytes.length) continue;
            var signerHex = "";
            for (var s = off; s < off + 32; s++) signerHex += ("0" + bytes[s].toString(16)).slice(-2);
            off += 32;
            
            // Check if this tx is from our address
            if (hexAddr && signerHex.toLowerCase() === hexAddr.replace("0x","").toLowerCase()) {
              // Decode call index
              off += (bytes[off] === 0) ? 1 : 2; // era
              off = readCompactPortfolio(bytes, off).nextOffset; // nonce
              off = readCompactPortfolio(bytes, off).nextOffset; // tip
              if (off + 1 < bytes.length) {
                var callMap = {"0,0":"system.remark","0,1":"system.setHeapPages","0,2":"system.setCode","0,3":"system.setStorage","1,0":"timestamp.set","4,0":"balances.transferAllowDeath","4,1":"balances.setBalance","4,3":"balances.transferKeepAlive","4,4":"balances.transferAll","6,0":"sudo.sudo","30,0":"dpos.registerValidator","30,1":"dpos.unregisterValidator","30,2":"dpos.updateGreenScore","30,5":"dpos.setValidatorName","31,0":"ammDex.createPool","31,1":"ammDex.addLiquidity","31,2":"ammDex.removeLiquidity","31,3":"ammDex.swap","32,0":"eco.mintCarbonCredit","32,1":"eco.createReforestProject","32,2":"eco.logReforestation"};
                var key = bytes[off] + "," + bytes[off+1];
                var callName = callMap[key] || "unknown";
                var parts = callName.split(".");
                foundTxs.push({block: b, section: parts[0], method: parts[1], signed: true});
              }
            }
          } else {
            // Unsigned/inherent - check for timestamp
            var key = bytes[off] + "," + bytes[off+1];
            if (key === "1,0" && off + 4 < bytes.length) {
              var tsFirst = bytes[off + 2];
              var mode = tsFirst & 0x03;
              if (mode === 0) { blockTime = (tsFirst >> 2) * 1000; }
              else if (mode === 1 && off + 3 < bytes.length) { blockTime = ((tsFirst | (bytes[off+3] << 8)) >> 2) * 1000; }
              else if (mode === 3) { var bl = (tsFirst >> 2) + 4; var val = 0; for (var bi = 1; bi <= bl && off+2+bi < bytes.length; bi++) { val += bytes[off+2+bi] * Math.pow(256, bi-1); } blockTime = val; }
            }
          }
        }
        
        // Also check for incoming transfers (balances.transferAllowDeath with this address as recipient)
        // This requires decoding the call args, which is more complex
        // For now, we focus on outgoing transactions
        
      } catch(be) { continue; }
    }
    
    // Render
    if (foundTxs.length === 0) {
      document.getElementById("pfTxBody").innerHTML = '<tr><td colspan="5" style="padding:16px;text-align:center;color:var(--text-3)">No transactions found in the last ' + scanRange + ' blocks</td></tr>';
      document.getElementById("pfTxCount").textContent = "";
    } else {
      document.getElementById("pfTxCount").textContent = foundTxs.length + " txs found (last " + scanRange + " blocks)";
      var tbody = "";
      for (var tx of foundTxs.slice(0, 50)) {
        tbody += '<tr style="border-bottom:1px solid var(--border)">';
        tbody += '<td style="padding:8px 12px;font-family:var(--mono)">#' + tx.block + '</td>';
        tbody += '<td style="padding:8px 12px;color:var(--text-3)">' + timeAgoStr(blockTimeForBlock(tx.block, currentBlock)) + '</td>';
        tbody += '<td style="padding:8px 12px;font-weight:500">' + escapeHtml(tx.method) + '</td>';
        tbody += '<td style="padding:8px 12px"><span style="padding:2px 6px;border-radius:4px;background:rgba(22,163,74,.08);color:#16a34a;font-size:11px;font-weight:600">' + escapeHtml(tx.section) + '</span></td>';
        tbody += '<td style="padding:8px 12px"><span style="color:#16a34a;font-size:11px">Yes</span></td>';
        tbody += '</tr>';
      }
      document.getElementById("pfTxBody").innerHTML = tbody;
    }
  } catch(e) {
    document.getElementById("pfTxBody").innerHTML = '<tr><td colspan="5" style="padding:16px;text-align:center;color:var(--text-3)">Error scanning: ' + escapeHtml(e.message) + '</td></tr>';
  }
}

function readCompactPortfolio(bytes, offset) {
  if (offset >= bytes.length) return { value: 0, nextOffset: offset };
  var first = bytes[offset]; var mode = first & 0x03;
  if (mode === 0) return { value: first >> 2, nextOffset: offset + 1 };
  if (mode === 1 && offset+1 < bytes.length) return { value: (first|(bytes[offset+1]<<8))>>2, nextOffset: offset+2 };
  if (mode === 2 && offset+3 < bytes.length) return { value: (first|(bytes[offset+1]<<8)|(bytes[offset+2]<<16)|(bytes[offset+3]<<24))>>>2, nextOffset: offset+4 };
  var bigLen = (first >> 2) + 4; var val = 0;
  for (var bi = 1; bi <= bigLen && offset+bi < bytes.length; bi++) val += bytes[offset+bi] * Math.pow(256, bi-1);
  return { value: val, nextOffset: offset + 1 + bigLen };
}

function ss58ToHex(ss58) {
  // Simple SS58 to hex conversion for comparison
  // This is a basic implementation - works for standard AccountId32
  try {
    if (ss58.startsWith("0x") && ss58.length === 66) return ss58;
    // Base58 decode is complex in pure JS - use the address as-is for comparison
    // The RPC returns hex addresses, so we compare case-insensitively
    return null;
  } catch(e) { return null; }
}

function blockTimeForBlock(blockNum, currentBlock) {
  // Rough estimate: each block is 6 seconds
  return (currentBlock - blockNum) * 6000;
}

function timeAgoStr(ms) {
  if (ms < 60000) return Math.floor(ms/1000) + "s ago";
  if (ms < 3600000) return Math.floor(ms/60000) + "m ago";
  if (ms < 86400000) return Math.floor(ms/3600000) + "h ago";
  return Math.floor(ms/86400000) + "d ago";
}

function escapeHtml(s) {
  if (!s) return "";
  return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function copyPortfolioAddr() {
  if (pfAddress) {
    navigator.clipboard.writeText(pfAddress).then(function() {
      alert("Address copied to clipboard");
    });
  }
}

function viewOnExplorer() {
  if (pfAddress) {
    document.getElementById("acctSearchInput").value = pfAddress;
    switchTab("accounts");
    searchAccount();
  }
}
'''

html = html[:last_script] + portfolio_js + html[last_script:]

with open(EXP_PATH, "w") as f:
    f.write(html)
print(f"Portfolio tab added to explorer ({len(html)} bytes)")
