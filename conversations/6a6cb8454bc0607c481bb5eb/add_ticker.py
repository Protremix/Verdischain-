import re

with open("/var/www/verdiscan/explorer/index.html") as f:
    content = f.read()

# 1. Add Top Markets ticker CSS
ticker_css = """
/* Top Markets Ticker */
.market-ticker{display:flex;align-items:center;gap:0;padding:10px 16px;background:var(--card);border:1px solid var(--border);border-radius:var(--radius);margin:12px 0;overflow:hidden;position:relative}
.market-ticker-label{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:var(--accent);white-space:nowrap;padding-right:14px;border-right:1px solid var(--border);margin-right:14px;flex-shrink:0}
.market-ticker-scroll{display:flex;gap:24px;overflow:hidden;flex:1;mask-image:linear-gradient(90deg,transparent,#000 5%,#000 95%,transparent)}
.market-ticker-scroll:hover{animation-play-state:paused}
.ticker-item{display:flex;align-items:center;gap:6px;white-space:nowrap;flex-shrink:0}
.ticker-rank{font-size:10px;color:var(--text-3);font-weight:600}
.ticker-pair{font-size:13px;font-weight:600;color:var(--text)}
.ticker-tvl{font-size:12px;color:var(--text-2)}
.ticker-change{font-size:11px;font-weight:600;padding:2px 6px;border-radius:4px}
.ticker-change.pos{color:#16a34a;background:rgba(22,163,74,.1)}
.ticker-change.neg{color:#dc2626;background:rgba(220,38,38,.1)}
@keyframes scroll-ticker{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
.market-ticker-scroll-inner{display:flex;gap:24px;animation:scroll-ticker 40s linear infinite}
.market-ticker-scroll:hover .market-ticker-scroll-inner{animation-play-state:paused}
"""

if "/* Top Markets Ticker */" not in content:
    # Insert CSS before the closing </style> tag
    content = content.replace("</style>", ticker_css + "</style>", 1)

# 2. Add Top Markets ticker HTML between info cards and search
ticker_html = """
<!-- Top Markets Ticker -->
<div class="market-ticker" id="marketTicker" style="display:none">
  <div class="market-ticker-label">⚡ Top Markets</div>
  <div class="market-ticker-scroll">
    <div class="market-ticker-scroll-inner" id="tickerInner">
      <!-- Populated by JS -->
    </div>
  </div>
</div>
"""

if "marketTicker" not in content:
    # Insert before the search section
    content = content.replace('<!-- Search -->', ticker_html + '\n<!-- Search -->', 1)

# 3. Add JavaScript to populate the ticker
ticker_js = """
// ===== Top Markets Ticker =====
async function loadMarketTicker() {
  try {
    const pools = await rpc('amm_dex_getAllPools', []);
    if (!pools || !pools.length) return;

    // Sort pools by TVL (reserveA + reserveB) descending
    const sorted = pools.map(p => {
      const reserveA = BigInt(p.reserve_a || p.reserveA || '0');
      const reserveB = BigInt(p.reserve_b || p.reserveB || '0');
      const tvl = reserveA + reserveB;
      return { ...p, tvl };
    }).sort((a, b) => b.tvl > a.tvl ? 1 : -1).slice(0, 10);

    const tickerInner = document.getElementById('tickerInner');
    if (!tickerInner) return;

    // Duplicate items for seamless scroll
    const items = [...sorted, ...sorted];
    tickerInner.innerHTML = items.map((p, i) => {
      const rank = (i % sorted.length) + 1;
      const tokenA = p.token_a || p.tokenA || 'VRDX';
      const tokenB = p.token_b || p.tokenB || 'USDC';
      const tvlNum = Number(p.tvl) / 10**9;
      const tvlStr = tvlNum >= 1e9 ? (tvlNum/1e9).toFixed(2)+'B' : tvlNum >= 1e6 ? (tvlNum/1e6).toFixed(2)+'M' : tvlNum >= 1e3 ? (tvlNum/1e3).toFixed(1)+'K' : tvlNum.toFixed(0);
      return '<div class="ticker-item">' +
        '<span class="ticker-rank">#'+rank+'</span>' +
        '<span class="ticker-pair">'+tokenA+'-'+tokenB+'</span>' +
        '<span class="ticker-tvl">'+tvlStr+'</span>' +
        '</div>';
    }).join('');

    document.getElementById('marketTicker').style.display = 'flex';
  } catch(e) {
    console.log('Ticker error:', e);
  }
}
"""

if "loadMarketTicker" not in content:
    # Insert before the init function or at the end of the script
    # Find a good insertion point - after the loadEco function or similar
    init_match = re.search(r'//\s*==*\s*Init\s*==*', content)
    if init_match:
        content = content[:init_match.start()] + ticker_js + '\n' + content[init_match.start():]
    else:
        # Just insert before </script>
        content = content.replace('</script>', ticker_js + '\n</script>', 1)

    # Also add the call to loadMarketTicker in the init sequence
    # Find where loadBlocks or other init functions are called
    if 'loadStats();' in content:
        content = content.replace('loadStats();', 'loadStats();\n  loadMarketTicker();', 1)
    elif 'loadStats()' in content:
        content = content.replace('loadStats()', 'loadStats()\n  loadMarketTicker()', 1)

with open("/var/www/verdiscan/explorer/index.html", "w") as f:
    f.write(content)

print("Top Markets ticker added")
print("File size:", len(content))
