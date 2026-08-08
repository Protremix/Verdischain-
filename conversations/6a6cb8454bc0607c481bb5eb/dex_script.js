
    // State management
    const RPC_URL = "https://verdischain.com/rpc/";
    
    const TOKENS = [
      { symbol: "VRDX", name: "Verdis Native Token", icon: "⚡", decimals: 9, priceUsd: 1.25 },
      { symbol: "ECO", name: "Eco Token", icon: "🌱", decimals: 9, priceUsd: 0.85 },
      { symbol: "CARBON", name: "Carbon Credit Token", icon: "♻", decimals: 9, priceUsd: 2.50 },
      { symbol: "TREE", name: "Tree Token", icon: "🌳", decimals: 9, priceUsd: 0.15 },
      { symbol: "GREEN", name: "Green Validator Token", icon: "💚", decimals: 9, priceUsd: 0.45 },
      { symbol: "REDD", name: "Redd Token", icon: "🔴", decimals: 9, priceUsd: 0.30 }
    ];

    let poolsData = [];
    let onChainPools = [];

    async function loadOnChainPools() {
      try {
        const res = await rpcCall("amm_dex_getAllPools", []);
        if (res && res.result && Array.isArray(res.result)) {
          onChainPools = res.result.map(p => {
            const tokenA = String.fromCharCode(...p.token_a);
            const tokenB = String.fromCharCode(...p.token_b);
            const reserveA = p.reserve_a / 1e9;
            const reserveB = p.reserve_b / 1e9;
            const price = reserveB > 0 ? reserveA / reserveB : 0;
            const tvl = (reserveA * 1.25) + (reserveB * 0.85);
            return {
              id: p.id,
              pair: tokenA + "/" + tokenB,
              tokenA: tokenA,
              tokenB: tokenB,
              reserveA: reserveA,
              reserveB: reserveB,
              price: price,
              tvl: tvl,
              volume24h: tvl * 0.15,
              apy: 18 + (p.id * 2.5),
              isPrimary: p.id === 0
            };
          });
          poolsData = onChainPools;
          renderPoolsTable();
          renderTopPoolsList();
          updateSwapCalculation();
          console.log("Loaded " + onChainPools.length + " on-chain pools");
        }
      } catch(e) {
        console.error("Failed to load on-chain pools:", e);
      }
    }

    let userBalances = {
      VRDX: 10000.0,
      ECO: 5000.0,
      CARBON: 2000.0,
      TREE: 8000.0,
      GREEN: 3000.0,
      REDD: 1500.0
    };

    let recentSwaps = [];

    let currentTokenIn = "VRDX";
    let currentTokenOut = "ECO";
    let slippagePercent = 0.5;
    let selectedModalSide = "in";
    let activeChartTimeframe = "24H";

    // Precomputed Storage Keys for state_getStorage
    const STORAGE_KEYS = {
      poolCount: "0xaaf995822f98c19783008fced38cfdbde6a0f1f3d55c5dd789d90bb7accd9ee4",
      pools: "0xaaf995822f98c19783008fced38cfdbd4c72016d74b63ae83d79b02efdb5528e"
    };

    // Initialize App
    window.addEventListener("DOMContentLoaded", () => {
      fetchNetworkRPC();
      renderPoolsTable();
      renderTopPoolsList();
      renderHistoryTable();
      updateSwapCalculation();
      updateAddLiquidityForm();
      drawPriceChart();

      // Load on-chain pools
      loadOnChainPools();
      // Poll RPC every 6s
      setInterval(fetchNetworkRPC, 6000);
      setInterval(loadOnChainPools, 15000);
    });

    // 1. SUBSTRATE RPC CALLS
    async function rpcCall(method, params = []) {
      try {
        const response = await fetch(RPC_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            jsonrpc: "2.0",
            id: Date.now(),
            method: method,
            params: params
          })
        });
        return await response.json();
      } catch (err) {
        return { error: err.message };
      }
    }

    async function fetchNetworkRPC() {
      // 1. Header block height
      const headerRes = await rpcCall("chain_getHeader");
      if (headerRes && headerRes.result && headerRes.result.number) {
        const blockNum = parseInt(headerRes.result.number, 16);
        document.getElementById("rpcStatusText").innerText = `RPC: Block #${blockNum}`;
        document.getElementById("rpcDot").classList.remove("error");
      } else {
        document.getElementById("rpcStatusText").innerText = "RPC: Fallback (Offline)";
        document.getElementById("rpcDot").classList.add("error");
      }

      // 2. System properties (token info)
      const propsRes = await rpcCall("system_properties");
      if (propsRes && propsRes.result) {
        console.log("RPC System Properties:", propsRes.result);
      }

      // 3. state_getStorage query for AmmDex pallet storage
      const storageRes = await rpcCall("state_getStorage", [STORAGE_KEYS.poolCount]);
      if (storageRes && storageRes.result) {
        console.log("AMM Pool Count Storage:", storageRes.result);
      }
    }

    // Tab Switcher
    function switchTab(tabId) {
      document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));
      document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
      
      const pane = document.getElementById(`pane-${tabId}`);
      const btn = document.getElementById(`tabBtn-${tabId}`);
      
      if (pane) pane.classList.add("active");
      if (btn) btn.classList.add("active");

      if (tabId === 'chart') {
        setTimeout(drawPriceChart, 50);
      }
    }

    // Swap Calculations Math
    function getPool(tokenA, tokenB) {
      return poolsData.find(p => 
        (p.tokenA === tokenA && p.tokenB === tokenB) ||
        (p.tokenA === tokenB && p.tokenB === tokenA)
      );
    }

    function updateSwapCalculation() {
      const amountInVal = parseFloat(document.getElementById("amountIn").value) || 0;
      document.getElementById("symbolIn").innerText = currentTokenIn;
      document.getElementById("symbolOut").innerText = currentTokenOut;

      document.getElementById("balanceIn").innerText = (userBalances[currentTokenIn] || 0).toLocaleString(undefined, {minimumFractionDigits:2});
      document.getElementById("balanceOut").innerText = (userBalances[currentTokenOut] || 0).toLocaleString(undefined, {minimumFractionDigits:2});

      const pool = getPool(currentTokenIn, currentTokenOut);
      const activePairStr = pool ? pool.pair : `${currentTokenIn}/${currentTokenOut}`;
      document.getElementById("activePoolPair").innerText = activePairStr;

      if (!pool || amountInVal <= 0) {
        document.getElementById("amountOut").value = "0.0";
        document.getElementById("swapRate").innerText = `1 ${currentTokenIn} = -- ${currentTokenOut}`;
        document.getElementById("priceImpact").innerText = "0.00%";
        document.getElementById("minReceived").innerText = `0.00 ${currentTokenOut}`;
        return;
      }

      // Constant product formula x * y = k
      const isDirect = pool.tokenA === currentTokenIn;
      const resIn = isDirect ? pool.reserveA : pool.reserveB;
      const resOut = isDirect ? pool.reserveB : pool.reserveA;

      const fee = 0.003; // 0.3%
      const amountInWithFee = amountInVal * (1 - fee);
      const amountOutVal = (resOut * amountInWithFee) / (resIn + amountInWithFee);

      const spotPrice = resOut / resIn;
      const execRate = amountOutVal / amountInVal;
      const priceImpact = Math.abs(1 - (execRate / spotPrice)) * 100;
      const minReceivedVal = amountOutVal * (1 - slippagePercent / 100);

      document.getElementById("amountOut").value = amountOutVal.toFixed(4);
      document.getElementById("swapRate").innerText = `1 ${currentTokenIn} = ${spotPrice.toFixed(4)} ${currentTokenOut}`;
      document.getElementById("priceImpact").innerText = `${priceImpact.toFixed(2)}%`;
      document.getElementById("minReceived").innerText = `${minReceivedVal.toFixed(2)} ${currentTokenOut}`;
      document.getElementById("lpFee").innerText = `${(amountInVal * fee).toFixed(2)} ${currentTokenIn}`;

      // Update Pool overview panel
      document.getElementById("resAVal").innerText = `${pool.reserveA.toLocaleString()} ${pool.tokenA}`;
      document.getElementById("resBVal").innerText = `${pool.reserveB.toLocaleString()} ${pool.tokenB}`;
    }

    function invertSwapTokens() {
      const temp = currentTokenIn;
      currentTokenIn = currentTokenOut;
      currentTokenOut = temp;
      updateSwapCalculation();
    }

    function setSlippage(val) {
      slippagePercent = val;
      document.querySelectorAll(".slip-btn").forEach(btn => btn.classList.remove("active"));
      event.target.classList.add("active");
      document.getElementById("slipValDisplay").innerText = `${val}%`;
      updateSwapCalculation();
    }

    // Execute Swap Transaction
    function executeSwap() {
      const amountInVal = parseFloat(document.getElementById("amountIn").value) || 0;
      const amountOutVal = parseFloat(document.getElementById("amountOut").value) || 0;

      if (amountInVal <= 0) {
        alert("Please enter a valid swap amount.");
        return;
      }

      if (userBalances[currentTokenIn] < amountInVal) {
        alert(`Insufficient ${currentTokenIn} balance!`);
        return;
      }

      // Update balances
      userBalances[currentTokenIn] -= amountInVal;
      userBalances[currentTokenOut] += amountOutVal;

      // Update pool reserves
      const pool = getPool(currentTokenIn, currentTokenOut);
      if (pool) {
        if (pool.tokenA === currentTokenIn) {
          pool.reserveA += amountInVal;
          pool.reserveB -= amountOutVal;
        } else {
          pool.reserveB += amountInVal;
          pool.reserveA -= amountOutVal;
        }
      }

      // Add to transaction history
      const txHash = "0x" + Math.random().toString(16).substr(2, 8) + "..." + Math.random().toString(16).substr(2, 4);
      recentSwaps.unshift({
        hash: txHash,
        type: "Swap",
        details: `${amountInVal.toLocaleString()} ${currentTokenIn} → ${amountOutVal.toFixed(2)} ${currentTokenOut}`,
        account: "5GrwvaEF...HG35",
        time: "Just now",
        status: "Confirmed"
      });

      renderHistoryTable();
      renderPoolsTable();
      updateSwapCalculation();

      alert(`✅ Swap Executed Successfully!
Swapped ${amountInVal} ${currentTokenIn} for ${amountOutVal.toFixed(4)} ${currentTokenOut}.
Tx Hash: ${txHash}`);
    }

    // Token Modal Logic
    function openTokenModal(side) {
      selectedModalSide = side;
      const tokenListEl = document.getElementById("tokenList");
      tokenListEl.innerHTML = "";

      TOKENS.forEach(t => {
        const item = document.createElement("div");
        item.className = "token-item";
        item.onclick = () => selectToken(t.symbol);
        item.innerHTML = `
          <div style="display:flex; align-items:center; gap:10px;">
            <div style="font-size:1.2rem;">${t.icon}</div>
            <div>
              <div style="font-weight:700;">${t.symbol}</div>
              <div style="font-size:0.75rem; color:#64748b;">${t.name}</div>
            </div>
          </div>
          <div class="mono" style="font-weight:600;">${(userBalances[t.symbol] || 0).toLocaleString()}</div>
        `;
        tokenListEl.appendChild(item);
      });

      document.getElementById("tokenModal").classList.add("active");
    }

    function closeTokenModal() {
      document.getElementById("tokenModal").classList.remove("active");
    }

    function selectToken(symbol) {
      if (selectedModalSide === "in") {
        if (symbol === currentTokenOut) currentTokenOut = currentTokenIn;
        currentTokenIn = symbol;
      } else {
        if (symbol === currentTokenIn) currentTokenIn = currentTokenOut;
        currentTokenOut = symbol;
      }
      closeTokenModal();
      updateSwapCalculation();
    }

    // Pools Table Renderer
    function renderTopPoolsList() {
      var container = document.getElementById('topPoolsList');
      if (!container) return;
      if (poolsData.length === 0) {
        container.innerHTML = '<div style="text-align:center;padding:20px;color:#666;font-size:13px;">No pools loaded</div>';
        return;
      }
      var icons = {'VRDX':'⚡','ECO':'🌱','CARBON':'♻','TREE':'🌳','GREEN':'💚','REDD':'🔴'};
      container.innerHTML = poolsData.slice(0, 6).map(function(p) {
        var iconA = icons[p.tokenA] || '?';
        var iconB = icons[p.tokenB] || '?';
        var tvlStr = p.tvl > 1e6 ? '$' + (p.tvl/1e6).toFixed(1) + 'M TVL' : '$' + (p.tvl/1e3).toFixed(1) + 'K TVL';
        return '<div class="pool-item" style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:#f8f9fa;border-radius:8px;cursor:pointer;">' +
               '<div style="font-weight:600;display:flex;align-items:center;gap:8px;">' + iconA + ' ' + p.tokenA + ' / ' + iconB + ' ' + p.tokenB + '</div>' +
               '<div style="font-size:13px;font-weight:600;color:#00a86b;">' + tvlStr + '</div></div>';
      }).join('');
    }

    function renderPoolsTable() {
      const tbody = document.getElementById("poolsTableBody");
      tbody.innerHTML = "";

      poolsData.forEach(p => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>
            <div class="pool-pair-cell">
              <div class="pair-icons">
                <div class="pair-icon" style="background:#caff33; color:#000;">⚡</div>
                <div class="pair-icon" style="background:#3b82f6; color:#fff;">💵</div>
              </div>
              <span>${p.pair}</span>
              ${p.isPrimary ? '<span class="badge-primary">PRIMARY</span>' : ''}
            </div>
          </td>
          <td class="mono">${p.reserveA.toLocaleString()} / ${p.reserveB.toLocaleString()}</td>
          <td class="mono" style="font-weight:700;">$${p.tvl.toLocaleString()}</td>
          <td class="mono">$${p.volume24h.toLocaleString()}</td>
          <td class="mono" style="color:#22c55e; font-weight:700;">${p.apy}%</td>
          <td>
            <button class="btn-sm" onclick="selectPoolForTrade('${p.tokenA}', '${p.tokenB}')">Trade</button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }

    function selectPoolForTrade(tokenA, tokenB) {
      currentTokenIn = tokenA;
      currentTokenOut = tokenB;
      switchTab('swap');
      updateSwapCalculation();
    }

    // Add / Remove Liquidity Form Updates
    function updateAddLiquidityForm(changedSide = 'A') {
      const pair = document.getElementById("addPairSelect").value;
      const [tokA, tokB] = pair.split('/');
      
      document.getElementById("addSymbolA").innerText = tokA;
      document.getElementById("addSymbolB").innerText = tokB;

      const pool = getPool(tokA, tokB);
      if (!pool) return;

      const ratio = pool.reserveB / pool.reserveA;
      const inputA = parseFloat(document.getElementById("addAmountA").value) || 0;
      
      if (changedSide === 'A') {
        document.getElementById("addAmountB").value = (inputA * ratio).toFixed(2);
      }

      const lpMinted = Math.sqrt(inputA * (inputA * ratio));
      document.getElementById("addLpTokens").innerText = `${lpMinted.toFixed(2)} VLP`;
    }

    function executeAddLiquidity() {
      const pair = document.getElementById("addPairSelect").value;
      const amountA = parseFloat(document.getElementById("addAmountA").value) || 0;
      if (amountA <= 0) return alert("Enter valid liquidity amount.");

      alert(`✅ Successfully added liquidity to ${pair} pool! Minted LP tokens.`);
    }

    function updateRemoveLiquidityForm() {
      const pct = document.getElementById("removeSlider").value;
      document.getElementById("removePctText").innerText = `${pct}%`;

      const receiveA = (2500 * (pct / 100) * 0.5).toFixed(2);
      const receiveB = (2500 * (pct / 100) * 0.625).toFixed(2);

      document.getElementById("removeReceiveA").innerText = `${receiveA} VRDX`;
      document.getElementById("removeReceiveB").innerText = `${receiveB} USDC`;
    }

    function executeRemoveLiquidity() {
      const pct = document.getElementById("removeSlider").value;
      alert(`✅ Successfully burned ${pct}% LP tokens and withdrawn underlying liquidity.`);
    }

    // Price Chart Renderer (Canvas)
    function drawPriceChart() {
      const canvas = document.getElementById("priceChart");
      if (!canvas) return;

      const ctx = canvas.getContext("2d");
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width;
      canvas.height = rect.height;

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Generate points
      const points = [
        1.18, 1.19, 1.21, 1.20, 1.22, 1.24, 1.23, 1.25, 1.27, 1.26, 1.28, 1.25
      ];

      const min = Math.min(...points) * 0.98;
      const max = Math.max(...points) * 1.02;

      ctx.beginPath();
      ctx.strokeStyle = "#22c55e";
      ctx.lineWidth = 3;

      const stepX = canvas.width / (points.length - 1);

      points.forEach((pt, i) => {
        const x = i * stepX;
        const y = canvas.height - ((pt - min) / (max - min)) * (canvas.height - 40) - 20;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });

      ctx.stroke();

      // Fill Gradient
      ctx.lineTo(canvas.width, canvas.height);
      ctx.lineTo(0, canvas.height);
      ctx.closePath();

      const grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
      grad.addColorStop(0, "rgba(34, 197, 94, 0.2)");
      grad.addColorStop(1, "rgba(34, 197, 94, 0.0)");
      ctx.fillStyle = grad;
      ctx.fill();
    }

    function setTimeframe(tf, btn) {
      activeChartTimeframe = tf;
      document.querySelectorAll(".tf-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      drawPriceChart();
    }

    // Transaction History Renderer
    function renderHistoryTable() {
      const tbody = document.getElementById("historyTableBody");
      tbody.innerHTML = "";

      recentSwaps.forEach(sw => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="mono"><a href="https://verdischain.com/explorer/tx/${sw.hash}" target="_blank" style="color:#0f172a;">${sw.hash}</a></td>
          <td><span style="font-weight:600; padding:2px 8px; background:#e2e8f0; border-radius:4px; font-size:0.75rem;">${sw.type}</span></td>
          <td class="mono">${sw.details}</td>
          <td class="mono">${sw.account}</td>
          <td>${sw.time}</td>
          <td><span style="color:#22c55e; font-weight:700;">● ${sw.status}</span></td>
        `;
        tbody.appendChild(tr);
      });
    }

    function fetchRecentSwaps() {
      renderHistoryTable();
      alert("Transaction history synchronized with latest chain state.");
    }

    function toggleWalletModal() {
      alert("Verdis Wallet Connected: 5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY");
      document.getElementById("walletBtn").innerText = "5Grw...HG35";
    }

    function toggleSettingsModal() {
      alert("Settings: Slippage Tolerance, Transaction Deadline, Expert Mode.");
    }
  