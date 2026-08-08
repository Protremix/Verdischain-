#!/usr/bin/env python3
"""Add Tx Search and Validator Metrics tabs to the Verdiscan explorer."""

import re

EXPLORER_PATH = "/var/www/verdiscan/explorer/index.html"

with open(EXPLORER_PATH, "r") as f:
    html = f.read()

# 1. Add new tab buttons after Governance
old_btn = '<button class="tab" data-t="governance" onclick="switchTab(\'governance\')">Governance</button>'
new_btn = old_btn + '\n    <button class="tab" data-t="txsearch" onclick="switchTab(\'txsearch\')">Tx Search</button>\n    <button class="tab" data-t="valmetrics" onclick="switchTab(\'valmetrics\')">Validator Metrics</button>'
html = html.replace(old_btn, new_btn)

# 2. Find the governance tab content end and add new sections after it
gov_marker = '<div class="tab-content" id="tab-governance">'
gov_idx = html.find(gov_marker)
if gov_idx == -1:
    print("ERROR: Could not find governance tab")
    exit(1)

# Find the closing </div> of the governance tab content
# Count opening and closing divs from the gov tab start
depth = 0
i = gov_idx
while i < len(html):
    if html[i:i+4] == '<div':
        depth += 1
    elif html[i:i+6] == '</div>':
        depth -= 1
        if depth == 0:
            gov_end = i + 6
            break
    i += 1

# Build new sections
tx_search_section = '''
  <!-- Tx Search -->
  <div class="tab-content" id="tab-txsearch">
    <div class="panel">
      <div class="panel-header"><span class="panel-title">Advanced Transaction Search</span><span id="txSearchCount" style="font-size:11px;color:var(--text-3);background:var(--accent-glow);padding:3px 10px;border-radius:100px;font-weight:600">0 results</span></div>
      <div style="padding:16px;display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;align-items:end">
        <div>
          <label style="font-size:11px;font-weight:600;color:var(--text-2);text-transform:uppercase;letter-spacing:.05em;display:block;margin-bottom:4px">From Block</label>
          <input id="txSearchFrom" type="number" placeholder="0" style="width:100%;padding:8px 12px;border:1px solid var(--border);border-radius:var(--radius-sm);font-family:var(--mono);font-size:12px;background:var(--bg-1);color:var(--text)">
        </div>
        <div>
          <label style="font-size:11px;font-weight:600;color:var(--text-2);text-transform:uppercase;letter-spacing:.05em;display:block;margin-bottom:4px">To Block</label>
          <input id="txSearchTo" type="number" placeholder="latest" style="width:100%;padding:8px 12px;border:1px solid var(--border);border-radius:var(--radius-sm);font-family:var(--mono);font-size:12px;background:var(--bg-1);color:var(--text)">
        </div>
        <div>
          <label style="font-size:11px;font-weight:600;color:var(--text-2);text-transform:uppercase;letter-spacing:.05em;display:block;margin-bottom:4px">Type</label>
          <select id="txSearchType" style="width:100%;padding:8px 12px;border:1px solid var(--border);border-radius:var(--radius-sm);font-size:12px;background:var(--bg-1);color:var(--text)">
            <option value="">All Types</option>
            <option value="system.remark">system.remark</option>
            <option value="balances.transferKeepAlive">balances.transferKeepAlive</option>
            <option value="balances.transferAllowDeath">balances.transferAllowDeath</option>
            <option value="dpos.registerValidator">dpos.registerValidator</option>
            <option value="dpos.updateGreenScore">dpos.updateGreenScore</option>
            <option value="dpos.setValidatorName">dpos.setValidatorName</option>
            <option value="ammDex.createPool">ammDex.createPool</option>
            <option value="ammDex.addLiquidity">ammDex.addLiquidity</option>
            <option value="ammDex.swap">ammDex.swap</option>
            <option value="ammDex.removeLiquidity">ammDex.removeLiquidity</option>
            <option value="eco.mintCarbonCredit">eco.mintCarbonCredit</option>
            <option value="eco.createReforestProject">eco.createReforestProject</option>
            <option value="eco.logReforestation">eco.logReforestation</option>
          </select>
        </div>
        <div>
          <label style="font-size:11px;font-weight:600;color:var(--text-2);text-transform:uppercase;letter-spacing:.05em;display:block;margin-bottom:4px">Sender Address</label>
          <input id="txSearchSender" type="text" placeholder="SS58 (optional)" style="width:100%;padding:8px 12px;border:1px solid var(--border);border-radius:var(--radius-sm);font-family:var(--mono);font-size:11px;background:var(--bg-1);color:var(--text)">
        </div>
        <div style="display:flex;gap:8px">
          <button onclick="searchTransactions()" style="padding:8px 20px;background:var(--accent);color:#fff;border:none;border-radius:var(--radius-sm);font-size:12px;font-weight:600;cursor:pointer;white-space:nowrap">Search</button>
          <button onclick="clearTxSearch()" style="padding:8px 16px;background:var(--bg-1);color:var(--text-2);border:1px solid var(--border);border-radius:var(--radius-sm);font-size:12px;font-weight:500;cursor:pointer">Clear</button>
        </div>
      </div>
      <div id="txSearchStatus" style="padding:8px 16px;font-size:12px;color:var(--text-3);display:none"></div>
      <div style="overflow-x:auto">
        <table class="tbl"><thead><tr><th>BLOCK</th><th>IDX</th><th>SENDER</th><th>SECTION.METHOD</th><th>HASH</th><th>TIME</th></tr></thead><tbody id="txSearchResults"></tbody></table>
      </div>
    </div>
  </div>
'''

validator_metrics_section = '''
  <!-- Validator Metrics -->
  <div class="tab-content" id="tab-valmetrics">
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">Validator Performance Metrics</span>
        <span id="valMetricsBadge" style="font-size:11px;color:var(--accent);background:var(--accent-glow);padding:3px 10px;border-radius:100px;font-weight:600">-- Active</span>
      </div>
      <div style="padding:16px;display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:16px">
        <div style="background:var(--bg-1);border:1px solid var(--border);border-radius:var(--radius-sm);padding:12px;text-align:center">
          <div style="font-size:20px;font-weight:700;color:var(--accent)" id="vmTotalValidators">--</div>
          <div style="font-size:10px;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:.05em;margin-top:4px">Total Validators</div>
        </div>
        <div style="background:var(--bg-1);border:1px solid var(--border);border-radius:var(--radius-sm);padding:12px;text-align:center">
          <div style="font-size:20px;font-weight:700;color:var(--accent)" id="vmActiveValidators">--</div>
          <div style="font-size:10px;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:.05em;margin-top:4px">Active Validators</div>
        </div>
        <div style="background:var(--bg-1);border:1px solid var(--border);border-radius:var(--radius-sm);padding:12px;text-align:center">
          <div style="font-size:20px;font-weight:700;color:var(--accent)" id="vmGreenValidators">--</div>
          <div style="font-size:10px;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:.05em;margin-top:4px">Green Validators</div>
        </div>
        <div style="background:var(--bg-1);border:1px solid var(--border);border-radius:var(--radius-sm);padding:12px;text-align:center">
          <div style="font-size:20px;font-weight:700;color:var(--accent)" id="vmSessionIndex">--</div>
          <div style="font-size:10px;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:.05em;margin-top:4px">Session Index</div>
        </div>
        <div style="background:var(--bg-1);border:1px solid var(--border);border-radius:var(--radius-sm);padding:12px;text-align:center">
          <div style="font-size:20px;font-weight:700;color:var(--accent)" id="vmEpochIndex">--</div>
          <div style="font-size:10px;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:.05em;margin-top:4px">Epoch Index</div>
        </div>
        <div style="background:var(--bg-1);border:1px solid var(--border);border-radius:var(--radius-sm);padding:12px;text-align:center">
          <div style="font-size:20px;font-weight:700;color:var(--accent)" id="vmBlocksProduced">--</div>
          <div style="font-size:10px;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:.05em;margin-top:4px">Blocks (last 50)</div>
        </div>
      </div>
      <div style="overflow-x:auto">
        <table class="tbl"><thead><tr><th>#</th><th>NAME</th><th>ADDRESS</th><th>STAKE</th><th>GREEN</th><th>STATUS</th><th>BLOCKS</th><th>UPTIME</th></tr></thead><tbody id="valMetricsResults"></tbody></table>
      </div>
    </div>
    <div class="panel" style="margin-top:16px">
      <div class="panel-header"><span class="panel-title">Session and Epoch Monitoring</span></div>
      <div style="padding:16px;display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px">
        <div style="padding:12px;background:var(--bg-1);border-radius:var(--radius-sm);border:1px solid var(--border)">
          <div style="font-size:11px;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:.05em">Current Session</div>
          <div style="font-size:16px;font-weight:700;margin-top:4px" id="vmCurrentSession">--</div>
          <div style="font-size:11px;color:var(--text-3);margin-top:2px" id="vmSessionProgress">--</div>
        </div>
        <div style="padding:12px;background:var(--bg-1);border-radius:var(--radius-sm);border:1px solid var(--border)">
          <div style="font-size:11px;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:.05em">Current Epoch</div>
          <div style="font-size:16px;font-weight:700;margin-top:4px" id="vmCurrentEpoch">--</div>
          <div style="font-size:11px;color:var(--text-3);margin-top:2px" id="vmEpochProgress">--</div>
        </div>
        <div style="padding:12px;background:var(--bg-1);border-radius:var(--radius-sm);border:1px solid var(--border)">
          <div style="font-size:11px;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:.05em">Next Rotation</div>
          <div style="font-size:16px;font-weight:700;margin-top:4px" id="vmNextRotation">--</div>
          <div style="font-size:11px;color:var(--text-3);margin-top:2px" id="vmRotationCountdown">--</div>
        </div>
        <div style="padding:12px;background:var(--bg-1);border-radius:var(--radius-sm);border:1px solid var(--border)">
          <div style="font-size:11px;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:.05em">Validators With Keys</div>
          <div style="font-size:16px;font-weight:700;margin-top:4px" id="vmValidatorsWithKeys">--</div>
          <div style="font-size:11px;color:var(--text-3);margin-top:2px" id="vmKeyStatus">--</div>
        </div>
      </div>
      <div id="vmAlerts" style="padding:8px 16px 16px"></div>
    </div>
  </div>
'''

# Insert new sections after the governance tab
html = html[:gov_end] + "\n" + tx_search_section + validator_metrics_section + html[gov_end:]

# 3. Add JavaScript before </script>
js_code = r'''
// === Advanced Transaction Search ===
async function searchTransactions() {
  const fromBlock = parseInt(document.getElementById("txSearchFrom").value) || 0;
  const toBlockInput = document.getElementById("txSearchTo").value;
  const typeFilter = document.getElementById("txSearchType").value;
  const senderFilter = document.getElementById("txSearchSender").value.trim().toLowerCase();
  const statusEl = document.getElementById("txSearchStatus");
  const resultsEl = document.getElementById("txSearchResults");
  const countEl = document.getElementById("txSearchCount");
  
  statusEl.style.display = "block";
  statusEl.textContent = "Searching...";
  resultsEl.innerHTML = "";
  
  try {
    let toBlock = parseInt(toBlockInput) || 0;
    if (!toBlock) {
      const hdr = await rpc("chain_getHeader", []);
      toBlock = parseInt(hdr.number, 16);
    }
    
    const maxBlocks = 50;
    let actualFrom = fromBlock;
    if (toBlock - fromBlock > maxBlocks) {
      actualFrom = toBlock - maxBlocks;
      statusEl.textContent = "Range too large. Scanning last " + maxBlocks + " blocks (" + actualFrom + " to " + toBlock + ")...";
    } else {
      statusEl.textContent = "Scanning blocks " + actualFrom + " to " + toBlock + "...";
    }
    
    let results = [];
    for (let b = toBlock; b >= actualFrom && results.length < 100; b--) {
      const blockHash = await rpc("chain_getBlockHash", [b]);
      if (!blockHash || blockHash === "0x" + "0".repeat(64)) continue;
      const blockData = await rpc("chain_getBlock", [blockHash]);
      if (!blockData || !blockData.block) continue;
      
      const exts = blockData.block.extrinsics || [];
      for (let i = 0; i < exts.length; i++) {
        const ext = exts[i];
        const callInfo = decodeExtrinsicCall(ext);
        const fullType = callInfo.section + "." + callInfo.method;
        
        if (typeFilter && fullType !== typeFilter) continue;
        if (senderFilter && callInfo.sender && callInfo.sender.toLowerCase().indexOf(senderFilter) === -1) continue;
        
        results.push({
          block: b, index: i, sender: callInfo.sender,
          type: fullType, hash: blockHash
        });
      }
    }
    
    countEl.textContent = results.length + " result" + (results.length !== 1 ? "s" : "");
    statusEl.style.display = "none";
    
    if (results.length === 0) {
      resultsEl.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:20px;color:var(--text-3)">No transactions found</td></tr>';
    } else {
      resultsEl.innerHTML = results.map(function(r) {
        return '<tr style="cursor:pointer" onclick="switchTab(\'blocks\');fetchBlockData(' + r.block + ')">' +
          '<td class="mono">#' + r.block + '</td>' +
          '<td class="mono">' + r.index + '</td>' +
          '<td class="mono" style="font-size:11px">' + (r.sender ? shortenAddr(r.sender) : "--") + '</td>' +
          '<td><span style="background:var(--accent-glow);color:var(--accent-2);padding:2px 8px;border-radius:4px;font-size:11px;font-weight:500">' + r.type + '</span></td>' +
          '<td class="mono" style="font-size:11px">' + shortenHash(r.hash) + '</td>' +
          '<td style="font-size:11px;color:var(--text-3)">' + new Date().toLocaleTimeString() + '</td>' +
          '</tr>';
      }).join("");
    }
  } catch(e) {
    statusEl.textContent = "Error: " + e.message;
    console.error("Tx search error:", e);
  }
}

function decodeExtrinsicCall(extHex) {
  try {
    const hex = extHex.startsWith("0x") ? extHex.slice(2) : extHex;
    const firstByte = parseInt(hex.slice(0, 2), 16);
    
    var callMap = {
      "0,0": ["system","remark"], "0,1": ["system","setHeapPages"],
      "0,2": ["system","setCode"], "0,3": ["system","setStorage"],
      "1,0": ["timestamp","set"],
      "2,0": ["balances","transferAllowDeath"], "2,1": ["balances","setBalance"],
      "2,3": ["balances","transferKeepAlive"], "2,4": ["balances","transferAll"],
      "10,0": ["dpos","registerValidator"], "10,1": ["dpos","unregisterValidator"],
      "10,2": ["dpos","updateGreenScore"], "10,5": ["dpos","setValidatorName"],
      "11,0": ["ammDex","createPool"], "11,1": ["ammDex","addLiquidity"],
      "11,2": ["ammDex","removeLiquidity"], "11,3": ["ammDex","swap"],
      "12,0": ["eco","mintCarbonCredit"], "12,1": ["eco","createReforestProject"],
      "12,2": ["eco","logReforestation"],
    };
    
    if (firstByte >= 0x80) {
      // Signed: try to find call index at various offsets after signature
      var sender = "[signed:" + hex.slice(2, 10) + "...]";
      for (var offset = 200; offset < hex.length - 4; offset += 2) {
        var sec = parseInt(hex.slice(offset, offset+2), 16);
        var meth = parseInt(hex.slice(offset+2, offset+4), 16);
        var key = sec + "," + meth;
        if (callMap[key]) {
          return { section: callMap[key][0], method: callMap[key][1], sender: sender };
        }
      }
      return { section: "signed", method: "unknown", sender: sender };
    } else {
      // Unsigned/inherent
      var sec = parseInt(hex.slice(0, 2), 16);
      var meth = parseInt(hex.slice(2, 4), 16);
      var key = sec + "," + meth;
      if (callMap[key]) {
        return { section: callMap[key][0], method: callMap[key][1], sender: "(inherent)" };
      }
      return { section: "inherent", method: "sec" + sec, sender: "(inherent)" };
    }
  } catch(e) {
    return { section: "error", method: "?", sender: "" };
  }
}

function clearTxSearch() {
  document.getElementById("txSearchFrom").value = "";
  document.getElementById("txSearchTo").value = "";
  document.getElementById("txSearchType").value = "";
  document.getElementById("txSearchSender").value = "";
  document.getElementById("txSearchResults").innerHTML = "";
  document.getElementById("txSearchCount").textContent = "0 results";
  document.getElementById("txSearchStatus").style.display = "none";
}

// === Validator Performance Metrics ===
async function loadValidatorMetrics() {
  try {
    var blockHdr = await rpc("chain_getHeader", []);
    var currentBlock = parseInt(blockHdr.number, 16);
    var allValidators = await rpc("dpos_allValidators", []) || [];
    var activeValidators = await rpc("dpos_activeValidators", []) || [];
    
    var sessionIndex = "--", epochIndex = "--";
    try { var si = await rpc("session_sessionIndex", []); sessionIndex = si != null ? si : "--"; } catch(e) {}
    try { var ei = await rpc("babe_currentEpoch", []); epochIndex = ei ? (ei.index || "--") : "--"; } catch(e) {}
    
    // Count blocks produced per validator in last 50 blocks
    var blockCounts = {};
    var maxBlocks = Math.min(50, currentBlock);
    var blocksChecked = 0;
    for (var b = currentBlock; b > currentBlock - maxBlocks && b >= 0; b--) {
      try {
        var hash = await rpc("chain_getBlockHash", [b]);
        if (!hash || hash === "0x" + "0".repeat(64)) continue;
        var block = await rpc("chain_getBlock", [hash]);
        if (block && block.block && block.block.header) {
          var digest = block.block.header.digest || { logs: [] };
          for (var li = 0; li < (digest.logs || []).length; li++) {
            var log = digest.logs[li];
            if (typeof log === "string" && log.startsWith("0x")) {
              var logHex = log.slice(2);
              if (logHex.startsWith("01")) {
                var authIdx = parseInt(logHex.slice(18, 20), 16);
                if (!isNaN(authIdx)) blockCounts[authIdx] = (blockCounts[authIdx] || 0) + 1;
              }
            }
          }
          blocksChecked++;
        }
      } catch(e) {}
    }
    
    var totalBlocksProduced = 0;
    for (var k in blockCounts) totalBlocksProduced += blockCounts[k];
    
    // Render stats
    document.getElementById("vmTotalValidators").textContent = allValidators.length;
    document.getElementById("vmActiveValidators").textContent = activeValidators.length;
    document.getElementById("vmBlocksProduced").textContent = totalBlocksProduced;
    document.getElementById("vmSessionIndex").textContent = sessionIndex;
    document.getElementById("vmEpochIndex").textContent = epochIndex;
    document.getElementById("vmCurrentSession").textContent = sessionIndex;
    document.getElementById("vmCurrentEpoch").textContent = epochIndex;
    
    var sessionPeriod = 50;
    var blocksIntoSession = currentBlock % sessionPeriod;
    var blocksUntilRotation = sessionPeriod - blocksIntoSession;
    document.getElementById("vmSessionProgress").textContent = "Block " + blocksIntoSession + "/" + sessionPeriod;
    document.getElementById("vmNextRotation").textContent = "Block #" + (currentBlock + blocksUntilRotation);
    document.getElementById("vmRotationCountdown").textContent = blocksUntilRotation + " blocks remaining";
    document.getElementById("vmEpochProgress").textContent = "Slot-based";
    document.getElementById("vmValidatorsWithKeys").textContent = activeValidators.length + "/" + allValidators.length;
    document.getElementById("vmKeyStatus").textContent = (allValidators.length - activeValidators.length) + " missing keys";
    
    // Alerts
    var alerts = [];
    if (allValidators.length - activeValidators.length > 0) {
      alerts.push('<div style="padding:8px 12px;background:rgba(251,191,36,.1);border:1px solid rgba(251,191,36,.3);border-radius:var(--radius-sm);font-size:12px;color:#92400e;margin-bottom:8px">WARNING: ' + (allValidators.length - activeValidators.length) + ' validator(s) missing session keys</div>');
    }
    if (blocksUntilRotation < 10) {
      alerts.push('<div style="padding:8px 12px;background:rgba(22,163,74,.1);border:1px solid rgba(22,163,74,.3);border-radius:var(--radius-sm);font-size:12px;color:var(--accent-2);margin-bottom:8px">Session rotation in ' + blocksUntilRotation + ' blocks</div>');
    }
    if (alerts.length === 0) {
      alerts.push('<div style="padding:8px 12px;background:rgba(34,197,94,.1);border:1px solid rgba(34,197,94,.3);border-radius:var(--radius-sm);font-size:12px;color:var(--accent-2)">All systems operational - no alerts</div>');
    }
    document.getElementById("vmAlerts").innerHTML = alerts.join("");
    
    // Render table
    var activeSet = {};
    for (var ai = 0; ai < activeValidators.length; ai++) {
      activeSet[typeof activeValidators[ai] === "string" ? activeValidators[ai] : JSON.stringify(activeValidators[ai])] = true;
    }
    
    var greenCount = 0;
    var rows = [];
    for (var i = 0; i < allValidators.length; i++) {
      var v = allValidators[i];
      var vStr = typeof v === "string" ? v : JSON.stringify(v);
      var isActive = activeSet[vStr];
      
      var name = "Validator";
      try { var n = await rpc("dpos_validatorName", [v]); if (n) name = n; } catch(e) {}
      
      var stake = "--";
      try { var s = await rpc("dpos_validatorStake", [v]); if (s) stake = (parseInt(s) / 1e9).toFixed(2) + " VRDX"; } catch(e) {}
      
      var greenScore = 0;
      try { var gs = await rpc("eco_getGreenScore", [v]); if (gs) greenScore = parseInt(gs); } catch(e) {}
      if (greenScore > 0) greenCount++;
      
      var bp = blockCounts[i] || 0;
      var uptime = totalBlocksProduced > 0 ? ((bp / totalBlocksProduced) * 100).toFixed(1) + "%" : "0%";
      
      rows.push("<tr>" +
        '<td class="mono">' + (i+1) + '</td>' +
        "<td style='font-weight:600'>" + name + "</td>" +
        '<td class="mono" style="font-size:11px;cursor:pointer;color:var(--accent)" onclick="switchTab(\'accounts\');searchAccount(\'' + v + '\')">' + shortenAddr(v) + "</td>" +
        '<td class="mono">' + stake + "</td>" +
        "<td>" + (greenScore > 0 ? '<span style="background:rgba(22,163,74,.1);color:var(--accent-2);padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600">' + greenScore + "</span>" : '<span style="color:var(--text-3)">0</span>') + "</td>" +
        "<td>" + (isActive ? '<span style="background:rgba(34,197,94,.1);color:#15803d;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600">Active</span>' : '<span style="background:rgba(148,163,184,.1);color:var(--text-3);padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600">Inactive</span>') + "</td>" +
        '<td class="mono">' + bp + "</td>" +
        '<td class="mono">' + uptime + "</td>" +
        "</tr>");
    }
    
    document.getElementById("vmGreenValidators").textContent = greenCount;
    document.getElementById("valMetricsBadge").textContent = activeValidators.length + " Active";
    document.getElementById("valMetricsResults").innerHTML = rows.join("");
  } catch(e) {
    console.error("Validator metrics error:", e);
    document.getElementById("valMetricsResults").innerHTML = '<tr><td colspan="8" style="text-align:center;padding:20px;color:var(--text-3)">Error: ' + e.message + "</td></tr>";
  }
}

// Hook switchTab to load data on new tabs
var origSwitchTab = switchTab;
switchTab = function(t) {
  origSwitchTab(t);
  if (t === "valmetrics") loadValidatorMetrics();
};

'''

html = html.replace("</script>", js_code + "\n</script>")

with open(EXPLORER_PATH, "w") as f:
    f.write(html)

print("Explorer updated: " + str(len(html)) + " bytes")
