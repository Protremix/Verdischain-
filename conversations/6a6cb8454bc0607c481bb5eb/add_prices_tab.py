#!/usr/bin/env python3
"""Add Price Analytics tab to Verdiscan explorer."""

EXP_PATH = "/var/www/verdiscan/explorer/index.html"

with open(EXP_PATH, "r") as f:
    html = f.read()

# 1. Add Chart.js CDN to head (before </head>)
chartjs_cdn = '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>'
if "chart.js" not in html.lower() or "chart.umd" not in html.lower():
    html = html.replace("</head>", f'  {chartjs_cdn}\n</head>')
    print("Chart.js CDN added")

# 2. Add Prices tab button after Portfolio button
old_portfolio_btn = '<button class="tab" data-t="portfolio" onclick="switchTab(\'portfolio\')">Portfolio</button>'
prices_btn = old_portfolio_btn + '\n    <button class="tab" data-t="prices" onclick="switchTab(\'prices\')">Prices</button>'
if 'data-t="prices"' not in html:
    html = html.replace(old_portfolio_btn, prices_btn)
    print("Prices tab button added")

# 3. Add Prices tab content after tab-portfolio closes (before the modal)
prices_html = '''  <div class="tab-content" id="tab-prices">
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">Token Price Analytics</span>
        <span class="panel-link" id="pricesUpdated">—</span>
      </div>
      <div style="padding:20px">
        <!-- Token Price Cards -->
        <div id="priceCardsGrid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px;margin-bottom:24px">
          <div style="text-align:center;padding:40px;color:var(--text-3);grid-column:1/-1">Loading price data...</div>
        </div>

        <!-- Price Chart -->
        <div class="panel" style="margin-bottom:16px;border:1px solid var(--border);border-radius:var(--radius)">
          <div class="panel-header">
            <span class="panel-title">Price History (VRDX pairs)</span>
            <span class="panel-link" id="priceChartRange">Last 24h · 30s intervals</span>
          </div>
          <div style="padding:16px">
            <div style="display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap" id="priceLegend"></div>
            <canvas id="priceChart" width="800" height="300" style="width:100%;height:300px"></canvas>
          </div>
        </div>

        <!-- Two column: TVL Chart + Pool Table -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
          <div class="panel" style="border:1px solid var(--border);border-radius:var(--radius)">
            <div class="panel-header">
              <span class="panel-title">Pool Liquidity (TVL)</span>
              <span class="panel-link" id="tvlTotal">—</span>
            </div>
            <div style="padding:16px">
              <canvas id="tvlChart" width="400" height="240" style="width:100%;height:240px"></canvas>
            </div>
          </div>
          <div class="panel" style="border:1px solid var(--border);border-radius:var(--radius)">
            <div class="panel-header">
              <span class="panel-title">Pool Comparison</span>
              <span class="panel-link" id="poolCount">—</span>
            </div>
            <div style="padding:12px;overflow-x:auto">
              <table class="data-table" style="width:100%;font-size:12px">
                <thead>
                  <tr>
                    <th style="padding:6px 8px;text-align:left">PAIR</th>
                    <th style="padding:6px 8px;text-align:right">RESERVE A</th>
                    <th style="padding:6px 8px;text-align:right">RESERVE B</th>
                    <th style="padding:6px 8px;text-align:right">PRICE</th>
                    <th style="padding:6px 8px;text-align:right">TVL</th>
                  </tr>
                </thead>
                <tbody id="poolTableBody">
                  <tr><td colspan="5" style="text-align:center;padding:20px;color:var(--text-3)">Loading...</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div style="margin-top:16px;font-size:11px;color:var(--text-3);text-align:center">
          Price data sampled every 30 seconds by the Verdis price collector. Historical data accumulates over time.
          Prices derived from AMM pool reserves (price = reserve_b / reserve_a).
        </div>
      </div>
    </div>
  </div>

'''

# Find the closing of tab-portfolio div and insert prices tab before the modal
old_modal = '<!-- Modal -->\n<div class="modal" id="modal"'
if 'id="tab-prices"' not in html:
    html = html.replace(old_modal, prices_html + old_modal)
    print("Prices tab content added")

# 4. Add JavaScript for prices tab (before the last </script>)
prices_js = '''
// ===== PRICE ANALYTICS TAB =====
var priceChartInstance = null;
var tvlChartInstance = null;

function bytesToStr(b) {
  if (!b) return "?";
  if (typeof b === "string") return b;
  if (Array.isArray(b)) return b.map(function(x) { return String.fromCharCode(x); }).join("");
  return String(b);
}

async function loadPricesTab() {
  try {
    // Fetch live pool data
    var poolsResp = await fetch("/rpc", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({jsonrpc:"2.0",id:1,method:"amm_dex_getAllPools",params:[]})
    });
    var poolsData = await poolsResp.json();
    var pools = poolsData.result || [];

    // Fetch price history
    var historyResp = await fetch("/price-history.json?_=" + Date.now());
    var historyData = null;
    if (historyResp.ok) {
      historyData = await historyResp.json();
    }

    // Fetch block height
    var blockResp = await fetch("/rpc", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({jsonrpc:"2.0",id:1,method:"chain_getBlock",params:[]})
    });
    var blockData = await blockResp.json();
    var blockNum = parseInt(blockData.result.block.header.number, 16);

    renderPriceCards(pools);
    renderPoolTable(pools);
    renderTVLChart(pools);
    renderPriceChart(historyData);
    document.getElementById("pricesUpdated").textContent = "Block #" + blockNum;
    document.getElementById("poolCount").textContent = pools.length + " pools";
  } catch(e) {
    console.error("Prices tab error:", e);
    document.getElementById("priceCardsGrid").innerHTML = '<div style="text-align:center;padding:40px;color:var(--error);grid-column:1/-1">Failed to load price data: ' + e.message + '</div>';
  }
}

function renderPriceCards(pools) {
  var grid = document.getElementById("priceCardsGrid");
  var tokens = {};

  // Extract token prices relative to VRDX
  for (var p of pools) {
    var ta = bytesToStr(p.token_a);
    var tb = bytesToStr(p.token_b);
    var ra = parseInt(p.reserve_a) / 1e9;
    var rb = parseInt(p.reserve_b) / 1e9;

    if (ta === "VRDX" && rb > 0) {
      tokens[tb] = {price: ra / rb, reserve: rb, pair: ta + "/" + tb};
    } else if (tb === "VRDX" && ra > 0) {
      tokens[ta] = {price: rb / ra, reserve: ra, pair: ta + "/" + tb};
    }
  }

  // Add VRDX itself
  tokens["VRDX"] = {price: 1.0, reserve: 0, pair: "VRDX (base)"};

  var html_out = "";
  var tokenColors = {
    "VRDX": "#16a34a", "ECO": "#06b6d4", "CARBON": "#8b5cf6",
    "TREE": "#22c55e", "GREEN": "#84cc16", "REDD": "#ef4444"
  };

  for (var t in tokens) {
    var info = tokens[t];
    var color = tokenColors[t] || "#6b7280";
    var priceStr = info.price < 0.01 ? info.price.toFixed(6) : info.price.toFixed(4);
    var reserveStr = info.reserve > 0 ? (info.reserve > 1e6 ? (info.reserve/1e6).toFixed(1) + "M" : info.reserve.toLocaleString("en-US", {maximumFractionDigits:0})) : "—";
    html_out += '<div style="background:var(--card);border:1px solid var(--border);border-radius:var(--radius-sm);padding:14px;position:relative;overflow:hidden">';
    html_out += '<div style="position:absolute;top:0;left:0;width:3px;height:100%;background:' + color + '"></div>';
    html_out += '<div style="font-family:var(--display);font-weight:700;font-size:14px;color:var(--text);margin-bottom:4px">' + t + '</div>';
    html_out += '<div class="mono" style="font-size:18px;font-weight:600;color:' + color + '">' + priceStr + '</div>';
    html_out += '<div style="font-size:10px;color:var(--text-3);margin-top:4px">VRDX price · Supply: ' + reserveStr + '</div>';
    html_out += '</div>';
  }

  grid.innerHTML = html_out;
}

function renderPoolTable(pools) {
  var tbody = document.getElementById("poolTableBody");
  if (!pools.length) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:20px;color:var(--text-3)">No pools found</td></tr>';
    return;
  }

  var html_out = "";
  var totalTvl = 0;
  for (var p of pools) {
    var ta = bytesToStr(p.token_a);
    var tb = bytesToStr(p.token_b);
    var ra = parseInt(p.reserve_a) / 1e9;
    var rb = parseInt(p.reserve_b) / 1e9;
    var price = ra > 0 ? (rb / ra).toFixed(4) : "—";
    var tvl = ra + rb;
    totalTvl += tvl;
    html_out += '<tr style="border-bottom:1px solid var(--border)">';
    html_out += '<td style="padding:6px 8px;font-weight:600">' + ta + '/' + tb + '</td>';
    html_out += '<td style="padding:6px 8px;text-align:right;font-family:var(--mono)">' + ra.toLocaleString("en-US", {maximumFractionDigits:0}) + '</td>';
    html_out += '<td style="padding:6px 8px;text-align:right;font-family:var(--mono)">' + rb.toLocaleString("en-US", {maximumFractionDigits:0}) + '</td>';
    html_out += '<td style="padding:6px 8px;text-align:right;font-family:var(--mono);color:var(--accent)">' + price + '</td>';
    html_out += '<td style="padding:6px 8px;text-align:right;font-family:var(--mono)">' + tvl.toLocaleString("en-US", {maximumFractionDigits:0}) + '</td>';
    html_out += '</tr>';
  }
  tbody.innerHTML = html_out;
  document.getElementById("tvlTotal").textContent = totalTvl.toLocaleString("en-US", {maximumFractionDigits:0}) + " VRDX";
}

function renderTVLChart(pools) {
  var ctx = document.getElementById("tvlChart");
  if (!ctx) return;

  var labels = pools.map(function(p) { return bytesToStr(p.token_a) + "/" + bytesToStr(p.token_b); });
  var data = pools.map(function(p) { return (parseInt(p.reserve_a) + parseInt(p.reserve_b)) / 1e9; });

  if (tvlChartInstance) tvlChartInstance.destroy();

  tvlChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "TVL (VRDX)",
        data: data,
        backgroundColor: "rgba(22, 163, 74, 0.6)",
        borderColor: "#16a34a",
        borderWidth: 0,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#1a1a1a",
          titleColor: "#fff",
          bodyColor: "#16a34a",
          callbacks: {
            label: function(ctx) { return ctx.parsed.y.toLocaleString("en-US", {maximumFractionDigits:0}) + " VRDX"; }
          }
        }
      },
      scales: {
        x: { ticks: { font: { size: 10 }, color: "#94a3b8" }, grid: { display: false } },
        y: { ticks: { font: { size: 10 }, color: "#94a3b8", callback: function(v) { return v.toLocaleString(); } }, grid: { color: "#e2e8f0" } }
      }
    }
  });
}

function renderPriceChart(historyData) {
  var ctx = document.getElementById("priceChart");
  if (!ctx) return;

  var tokenColors = {
    "ECO": "#06b6d4", "CARBON": "#8b5cf6", "TREE": "#22c55e",
    "GREEN": "#84cc16", "REDD": "#ef4444"
  };

  if (!historyData || !historyData.history || historyData.history.length < 2) {
    // Not enough data yet
    if (priceChartInstance) priceChartInstance.destroy();
    var ctx2d = ctx.getContext("2d");
    ctx2d.clearRect(0, 0, ctx.width, ctx.height);
    ctx2d.fillStyle = "#94a3b8";
    ctx2d.font = "13px Inter, sans-serif";
    ctx2d.textAlign = "center";
    ctx2d.fillText("Collecting price data... Charts will appear as history accumulates.", ctx.width / 2, ctx.height / 2);
    document.getElementById("priceChartRange").textContent = "Building history (0 points)";
    document.getElementById("priceLegend").innerHTML = "";
    return;
  }

  var history = historyData.history;
  document.getElementById("priceChartRange").textContent = history.length + " data points · " + 
    new Date(history[0].timestamp).toLocaleTimeString() + " → " + 
    new Date(history[history.length-1].timestamp).toLocaleTimeString();

  // Build datasets for each token
  var labels = history.map(function(h) {
    return new Date(h.timestamp).toLocaleTimeString("en-US", {hour: "2-digit", minute: "2-digit", second: "2-digit"});
  });

  var datasets = [];
  var legendHtml = "";
  for (var token in tokenColors) {
    var tokenData = history.map(function(h) {
      return h.tokens && h.tokens[token] ? h.tokens[token] : null;
    });

    // Only add if we have data for this token
    if (tokenData.some(function(v) { return v !== null; })) {
      var color = tokenColors[token];
      datasets.push({
        label: token + "/VRDX",
        data: tokenData,
        borderColor: color,
        backgroundColor: color + "20",
        borderWidth: 2,
        fill: false,
        tension: 0.3,
        pointRadius: 0,
        pointHoverRadius: 4,
        spanGaps: true
      });
      legendHtml += '<div style="display:flex;align-items:center;gap:6px;font-size:11px"><div style="width:10px;height:2px;background:' + color + ';border-radius:1px"></div>' + token + '/VRDX</div>';
    }
  }

  document.getElementById("priceLegend").innerHTML = legendHtml;

  if (priceChartInstance) priceChartInstance.destroy();

  priceChartInstance = new Chart(ctx, {
    type: "line",
    data: { labels: labels, datasets: datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#1a1a1a",
          titleColor: "#fff",
          bodyColor: "#fff",
          borderColor: "#334155",
          borderWidth: 1,
          callbacks: {
            label: function(ctx) { return ctx.dataset.label + ": " + (ctx.parsed.y !== null ? ctx.parsed.y.toFixed(4) : "no data"); }
          }
        }
      },
      scales: {
        x: {
          ticks: { font: { size: 9 }, color: "#94a3b8", maxTicksLimit: 12, autoSkip: true },
          grid: { color: "#f1f5f9" }
        },
        y: {
          ticks: { font: { size: 10 }, color: "#94a3b8", callback: function(v) { return v.toFixed(4); } },
          grid: { color: "#e2e8f0" }
        }
      }
    }
  });
}

// Load prices tab on tab switch
var origSwitchTab = switchTab;
switchTab = function(tab) {
  origSwitchTab(tab);
  if (tab === "prices") {
    loadPricesTab();
  }
};
'''

# Insert before the last </script>
last_script_idx = html.rfind("</script>")
if 'loadPricesTab' not in html:
    html = html[:last_script_idx] + prices_js + "\n" + html[last_script_idx:]
    print("Prices JavaScript added")

with open(EXP_PATH, "w") as f:
    f.write(html)
print(f"All price analytics inserted ({len(html)} bytes)")
