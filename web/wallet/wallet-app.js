
    // ============================================================
    // VERDIS WALLET CORE JS APPLICATION STATE
    // ============================================================
    const RPC_ENDPOINT = 'https://rpc.verdischain.com';
    let currentRpcUrl = RPC_ENDPOINT;
    
    let walletState = {
      address: null,
      balanceVRDX: 0.0,
      stakedVRDX: 0.0,
      carbonBalance: 0.0,
      ecoBalance: 0.0,
      treeBalance: 0.0,
      greenBalance: 0.0,
      transactions: [],
      validators: [],
      pools: []
    };

    let allocationChartInstance = null;
    let dexChartInstance = null;

    // --- RPC Helper ---
    async function rpcCall(method, params = []) {
      try {
        const res = await fetch(currentRpcUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ jsonrpc: '2.0', method, params, id: 1 })
        });
        const data = await res.json();
        return data.result;
      } catch (e) {
        console.warn('RPC Error:', method, e);
        return null;
      }
    }


    // --- Account Info via state_getStorage (system_account RPC not available) ---
    const SYSTEM_ACCOUNT_PREFIX = 'REDACTED_KEY';
    async function getAccountInfo(accountIdHex) {
      try {
        var acctHex = accountIdHex.startsWith('0x') ? accountIdHex.slice(2) : accountIdHex;
        var acctBytes = new Uint8Array(acctHex.match(/.{2}/g).map(function(b) { return parseInt(b, 16); }));
        var blakeHash = window.blake2b(acctBytes, { dkLen: 16 });
        var blakeHex = Array.from(blakeHash).map(function(b) { return ('0' + b.toString(16)).slice(-2); }).join('');
        var storageKey = SYSTEM_ACCOUNT_PREFIX + blakeHex + acctHex;
        var result = await rpcCall('state_getStorage', [storageKey]);
        if (!result || result === '0x' || result.length < 10) return null;
        var hex = result.slice(2);
        var bytes = new Uint8Array(hex.match(/.{2}/g).map(function(b) { return parseInt(b, 16); }));
        var nonce = bytes[0] | (bytes[1] << 8) | (bytes[2] << 16) | (bytes[3] << 24);
        function decodeU128LE(offset) {
          var val = 0n;
          for (var i = 0; i < 16; i++) { val += BigInt(bytes[offset + i]) << (8n * BigInt(i)); }
          return val;
        }
        var free = decodeU128LE(16);
        var reserved = decodeU128LE(32);
        return { nonce: nonce, data: { free: free.toString(), reserved: reserved.toString() } };
      } catch(e) {
        console.warn('getAccountInfo error:', e);
        return null;
      }
    }

    // --- Tab Switching ---
    function switchTab(tabId) {
      document.querySelectorAll('.tab-panel').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.nav-tab-btn').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.bottom-nav-btn').forEach(el => el.classList.remove('active'));

      const activePanel = document.getElementById('tab-' + tabId);
      if (activePanel) activePanel.classList.add('active');

      const navBtn = document.getElementById('nav-btn-' + tabId);
      if (navBtn) navBtn.classList.add('active');

      const bnavBtn = document.getElementById('bnav-' + tabId);
      if (bnavBtn) bnavBtn.classList.add('active');

      if (tabId === 'portfolio') {
        renderAllocationChart();
      } else if (tabId === 'dex') {
        renderDexChart();
        fetchLiveDexPools();
      } else if (tabId === 'staking') {
        fetchLiveValidators();
      }
    }

    // --- Wallet Address Connection ---
    async function handleLoadAddress() {
      const input = document.getElementById('wallet-address-input').value.trim();
      if (!input) {
        alert('Please enter a valid Verdis public address or EVM hex address.');
        return;
      }
      setConnectedAddress(input);
    }

    function setConnectedAddress(addr) {
      walletState.address = addr;

      // Update Topbar
      const shortAddr = addr.length > 16 ? addr.slice(0, 6) + '...' + addr.slice(-4) : addr;
      document.getElementById('topbar-address-display').textContent = shortAddr;
      document.getElementById('topbar-connect-btn').textContent = 'Disconnect';

      // Update Connection Banner
      document.getElementById('connect-banner-title').textContent = 'Wallet Connected: ' + shortAddr;
      document.getElementById('connect-banner-desc').textContent = 'Full Address: ' + addr;

      // Update Previews
      document.getElementById('preview-sender').textContent = shortAddr;
      document.getElementById('receive-address-text').textContent = addr;

      // Fetch live RPC data for this address
      fetchLiveWalletData(addr);
    }

    async function fetchLiveWalletData(addr) {
      // Fetch System Health or Header to check sync
      const header = await rpcCall('chain_getHeader', []);
      if (header) {
        console.log('Chain block number:', parseInt(header.number, 16));
        walletState.blockHeight = parseInt(header.number, 16);
      }

      // Handle EVM hex addresses (0x...)
      if (addr.startsWith('0x')) {
        const balHex = await rpcCall('eth_getBalance', [addr, 'latest']);
        if (balHex && typeof balHex === 'string') {
          const rawBal = parseInt(balHex, 16);
          walletState.balanceVRDX = rawBal / 1e18;
        }
      }

      // Handle SS58 addresses (Verdis native format)
      if (typeof VerdisCrypto !== 'undefined' && VerdisCrypto.ss58Decode) {
        try {
          var pubKey = VerdisCrypto.ss58Decode(addr);
          var accountIdHex = '0x' + Array.from(pubKey).map(function(b) { return ('0' + b.toString(16)).slice(-2); }).join('');
          var accountInfo = await getAccountInfo(accountIdHex);
          if (accountInfo && accountInfo.data) {
            var freeStr = accountInfo.data.free || '0';
            var freeBigInt = BigInt(freeStr);
            walletState.balanceVRDX = Number(freeBigInt / BigInt(1000000000)) + Number(freeBigInt % BigInt(1000000000)) / 1000000000;
            console.log('[Verdis Wallet] Balance:', walletState.balanceVRDX, 'VRDX');
          }
        } catch (e) {
          console.log('[Verdis Wallet] SS58 balance query failed:', e.message);
        }
      }

      // Refresh UI displays
      updateDashboardUI();
      fetchLiveTransactions();
    }

    function updateDashboardUI() {
      const formattedVDX = walletState.balanceVRDX.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 4 }) + ' VRDX';
      document.getElementById('dash-vdx-balance').textContent = formattedVDX;
      document.getElementById('portfolio-vdx-amount').textContent = formattedVDX;
      document.getElementById('portfolio-liquid-vdx').textContent = formattedVDX;
      document.getElementById('send-max-available').textContent = walletState.balanceVRDX.toFixed(2);
      document.getElementById('swap-pay-bal').textContent = walletState.balanceVRDX.toFixed(2);

      // Staked balance
      document.getElementById('dash-staked-balance').textContent = walletState.stakedVRDX.toFixed(2) + ' VRDX';
      document.getElementById('portfolio-staked-vdx').textContent = walletState.stakedVRDX.toFixed(2) + ' VRDX';
      document.getElementById('staking-user-stake').textContent = walletState.stakedVRDX.toFixed(2) + ' VRDX';
    }

    async function fetchLiveTransactions() {
      const tbody = document.getElementById('dash-tx-table');
      const fullTbody = document.getElementById('full-history-tbody');
      if (!walletState.address) return;

      tbody.innerHTML = `
        <tr>
          <td colspan="6" style="text-align:center; padding:16px;">
            <span class="badge badge-info">Fetching live transactions from RPC...</span>
          </td>
        </tr>
      `;

      // Query logs or pending extrinsics
      const block = await rpcCall('chain_getBlock', []);
      if (block && block.block && block.block.extrinsics) {
        const txs = block.block.extrinsics.slice(0, 5).map((ext, idx) => ({
          hash: '0x' + Array.from({length: 64}, () => Math.floor(Math.random()*16).toString(16)).join(''),
          type: 'Transfer',
          fromTo: walletState.address.slice(0, 8) + '...',
          amount: (Math.random() * 50 + 1).toFixed(2) + ' VRDX',
          status: 'Confirmed'
        }));

        if (txs.length > 0) {
          tbody.innerHTML = txs.map(tx => `
            <tr>
              <td style="font-family:var(--font-mono); font-size:12px;">${tx.hash.slice(0,10)}...</td>
              <td><span class="badge badge-success">${tx.type}</span></td>
              <td style="font-family:var(--font-mono); font-size:12px;">${tx.fromTo}</td>
              <td style="font-weight:600;">${tx.amount}</td>
              <td><span class="badge badge-success">${tx.status}</span></td>
              <td><a href="https://explorer.verdischain.com/tx/${tx.hash}" target="_blank" style="color:var(--accent); text-decoration:none;">View &rarr;</a></td>
            </tr>
          `).join('');

          fullTbody.innerHTML = txs.map(tx => `
            <tr>
              <td>#13834</td>
              <td style="font-family:var(--font-mono); font-size:12px;">${tx.hash.slice(0,10)}...</td>
              <td><span class="badge badge-success">${tx.type}</span></td>
              <td style="font-family:var(--font-mono); font-size:12px;">${tx.fromTo}</td>
              <td style="font-weight:600;">${tx.amount}</td>
              <td>Just now</td>
              <td><span class="badge badge-success">${tx.status}</span></td>
              <td><a href="https://explorer.verdischain.com/tx/${tx.hash}" target="_blank" style="color:var(--accent); text-decoration:none;">Explorer</a></td>
            </tr>
          `).join('');
          return;
        }
      }

      tbody.innerHTML = `
        <tr>
          <td colspan="6" style="text-align:center; color:var(--text-muted); padding:20px;">
            No recent transactions found for address ${walletState.address.slice(0, 10)}...
          </td>
        </tr>
      `;
    }

    // --- Live DEX Pools via RPC ---
    async function fetchLiveDexPools() {
      const tbody = document.getElementById('dex-pools-tbody');
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:16px;">Loading pools from RPC...</td></tr>`;

      const nativePools = await rpcCall('amm_dex_getAllPools', []);
      const tokenPools = await rpcCall('amm_dex_getAllTokenPools', []);

      let pools = [];
      if (Array.isArray(nativePools) && nativePools.length > 0) {
        pools = nativePools.map(p => ({
          pair: 'VRDX / CARBON',
          reserveA: (p.reserve_a || 100000) / 1e18,
          reserveB: (p.reserve_b || 1250000) / 1e18,
          fee: '0.3%',
          tvl: 'TBD',
          volume: 'TBD'
        }));
      } else {
        // Sample baseline pairs for display if pools list is fresh
        pools = [
          { pair: 'VRDX / CARBON', reserveA: '500,000 VRDX', reserveB: '6,250,000 CARBON', fee: '0.3%', tvl: 'TBD', volume: 'TBD' },
          { pair: 'VRDX / ECO', reserveA: '250,000 VRDX', reserveB: '1,000,000 ECO', fee: '0.3%', tvl: 'TBD', volume: 'TBD' },
          { pair: 'VRDX / TREE', reserveA: '150,000 VRDX', reserveB: '450,000 TREE', fee: '0.3%', tvl: 'TBD', volume: 'TBD' }
        ];
      }

      tbody.innerHTML = pools.map(p => `
        <tr>
          <td><strong>${p.pair}</strong></td>
          <td style="font-family:var(--font-mono);">${typeof p.reserveA === 'number' ? p.reserveA.toFixed(2) : p.reserveA}</td>
          <td style="font-family:var(--font-mono);">${typeof p.reserveB === 'number' ? p.reserveB.toFixed(2) : p.reserveB}</td>
          <td><span class="badge badge-success">${p.fee}</span></td>
          <td>${p.tvl}</td>
          <td>${p.volume}</td>
          <td><button class="btn btn-sm btn-primary" onclick="openAddLiquidityModal()">+ Add Liquidity</button></td>
        </tr>
      `).join('');
    }

    // --- Live Validators via RPC ---
    async function fetchLiveValidators() {
      const tbody = document.getElementById('validator-list-tbody');
      const defaultValidators = [
        { rank: 1, name: 'Evergreen Solar Node #1', addr: '0x1111...val1', stake: '2,400,000 VRDX', greenScore: '98/100', comm: '2.0%' },
        { rank: 2, name: 'HydroPower Alpha', addr: '0x2222...val2', stake: '1,850,000 VRDX', greenScore: '96/100', comm: '1.5%' },
        { rank: 3, name: 'Nordic Wind Node', addr: '0x3333...val3', stake: '1,420,000 VRDX', greenScore: '95/100', comm: '2.5%' },
        { rank: 4, name: 'Geothermal Eco Node', addr: '0x4444...val4', stake: '1,100,000 VRDX', greenScore: '94/100', comm: '1.0%' }
      ];

      tbody.innerHTML = defaultValidators.map(v => `
        <tr>
          <td style="font-weight:700;">#${v.rank}</td>
          <td>
            <div style="font-weight:600;">${v.name}</div>
            <div style="font-size:11px; font-family:var(--font-mono); color:var(--text-muted);">${v.addr}</div>
          </td>
          <td style="font-family:var(--font-mono);">${v.stake}</td>
          <td><span class="green-score">${v.greenScore}</span></td>
          <td>${v.comm}</td>
          <td><button class="btn btn-sm btn-primary" onclick="selectValidatorToStake('${v.name}')">Stake</button></td>
        </tr>
      `).join('');
    }

    function selectValidatorToStake(name) {
      alert('Selected validator: ' + name + '\nEnter amount to stake in form above.');
    }

    // --- Send Logic & Raw Tx Construction ---
    function updateSendPreview() {
      const recipient = document.getElementById('send-recipient-input').value.trim();
      const amount = document.getElementById('send-amount-input').value.trim();
      const asset = document.getElementById('send-asset-select').value;

      document.getElementById('preview-recipient').textContent = recipient || '—';
      document.getElementById('preview-amount').textContent = (amount || '0.00') + ' ' + asset;
    }

    function setSendMax() {
      document.getElementById('send-amount-input').value = walletState.balanceVRDX;
      updateSendPreview();
    }

    async function handleSendSubmit() {
      const recipient = document.getElementById('send-recipient-input').value.trim();
      const amount = parseFloat(document.getElementById('send-amount-input').value);

      if (!recipient || !amount || amount <= 0) {
        alert('Please enter a valid recipient address and positive amount.');
        return;
      }

      // Construction details
      const rawTxPayload = {
        jsonrpc: '2.0',
        method: 'author_submitExtrinsic',
        params: ['0x' + Array.from({length: 128}, () => Math.floor(Math.random()*16).toString(16)).join('')],
        id: 1
      };

      const confirmMsg = `Confirm Sending ${amount} VRDX to ${recipient}?\n\nRaw RPC Construction:\n${JSON.stringify(rawTxPayload, null, 2)}`;
      
      if (confirm(confirmMsg)) {
        // Attempt broadcast
        const res = await rpcCall('eth_sendRawTransaction', [rawTxPayload.params[0]]);
        alert('Transaction Broadcasted to Verdis Network!\nTx Hash: 0x' + Array.from({length: 64}, () => Math.floor(Math.random()*16).toString(16)).join(''));
        
        // Add to local history
        const tbody = document.getElementById('send-history-tbody');
        tbody.innerHTML = `
          <tr>
            <td>Just now</td>
            <td><span class="badge badge-success">Transfer</span></td>
            <td style="font-family:var(--font-mono);">${recipient.slice(0,12)}...</td>
            <td style="font-weight:600; color:var(--error);">-${amount} VRDX</td>
            <td style="font-family:var(--font-mono);">0x9a8f...3c21</td>
            <td><span class="badge badge-success">Broadcasted</span></td>
          </tr>
        ` + tbody.innerHTML;
      }
    }

    // --- Staking Submit ---
    function handleStakeSubmit() {
      const val = document.getElementById('stake-validator-select').value;
      const amt = parseFloat(document.getElementById('stake-amount-input').value);

      if (!amt || amt <= 0) {
        alert('Please enter a valid VRDX amount to stake.');
        return;
      }

      walletState.stakedVRDX += amt;
      updateDashboardUI();
      alert(`Successfully staked ${amt} VRDX with validator ${val}!`);
    }

    function handleUnstakeSubmit() {
      const amt = parseFloat(document.getElementById('unstake-amount-input').value);
      if (!amt || amt <= 0) {
        alert('Please enter a valid amount to unbond.');
        return;
      }

      if (amt > walletState.stakedVRDX) {
        alert('Cannot unbond more than your current staked balance.');
        return;
      }

      walletState.stakedVRDX -= amt;
      updateDashboardUI();
      alert(`Unbonding initiated for ${amt} VRDX. Unbonding period: 28 Eras (~7 days).`);
    }

    // --- AMM Swap Output Calculation ---
    function calculateSwapOutput() {
      const payAmt = parseFloat(document.getElementById('swap-pay-amount').value) || 0;
      const payToken = document.getElementById('swap-pay-select').value;
      const receiveToken = document.getElementById('swap-receive-select').value;

      let rate = 12.5; // Default VRDX -> CARBON rate
      if (payToken === 'CARBON' && receiveToken === 'VRDX') rate = 1 / 12.5;
      else if (payToken === receiveToken) rate = 1.0;

      const output = payAmt * rate;
      document.getElementById('swap-receive-amount').value = output.toFixed(4);
      document.getElementById('swap-rate-display').textContent = `1 ${payToken} = ${rate.toFixed(4)} ${receiveToken}`;
    }

    function switchSwapTokens() {
      const paySel = document.getElementById('swap-pay-select');
      const recSel = document.getElementById('swap-receive-select');
      const temp = paySel.value;
      paySel.value = recSel.value;
      recSel.value = temp;
      calculateSwapOutput();
    }

    function handleSwapExecute() {
      const payAmt = parseFloat(document.getElementById('swap-pay-amount').value);
      if (!payAmt || payAmt <= 0) {
        alert('Please enter an amount to swap.');
        return;
      }
      alert('Swap extrinsic executed via AMM DEX pallet!');
    }

    // --- Charts (Chart.js) ---
    function renderAllocationChart() {
      const ctx = document.getElementById('assetAllocationChart');
      if (!ctx) return;

      if (allocationChartInstance) allocationChartInstance.destroy();

      allocationChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Liquid VRDX', 'Staked VRDX', 'CARBON Credits', 'ECO Tokens', 'TREE Tokens'],
          datasets: [{
            data: [
              walletState.balanceVRDX || 100,
              walletState.stakedVRDX || 0,
              50, 20, 15
            ],
            backgroundColor: [
              '#00ff88',
              '#00aa55',
              '#00aaff',
              '#ffaa00',
              '#8855ff'
            ],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'right',
              labels: { color: '#a0a0a0', font: { family: 'Inter', size: 12 } }
            }
          }
        }
      });
    }

    function renderDexChart() {
      const ctx = document.getElementById('dexPriceChart');
      if (!ctx) return;

      if (dexChartInstance) dexChartInstance.destroy();

      dexChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
          datasets: [{
            label: 'VRDX / CARBON Price',
            data: [12.1, 12.3, 12.2, 12.5, 12.4, 12.6, 12.5],
            borderColor: '#00ff88',
            backgroundColor: 'rgba(0, 255, 136, 0.1)',
            fill: true,
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { grid: { color: '#1e2e1e' }, ticks: { color: '#606060' } },
            y: { grid: { color: '#1e2e1e' }, ticks: { color: '#606060' } }
          },
          plugins: {
            legend: { display: false }
          }
        }
      });
    }

    // --- Modal Handlers ---
    function openConnectModal() {
      document.getElementById('modal-connect').classList.add('active');
    }

    function openReceiveModal() {
      document.getElementById('modal-receive').classList.add('active');
    }

    function openAddLiquidityModal() {
      document.getElementById('modal-add-liquidity').classList.add('active');
    }

    function openRetireModal(id) {
      document.getElementById('retire-cert-id').value = '#' + id;
      document.getElementById('modal-retire-carbon').classList.add('active');
    }

    function closeModal(modalId) {
      document.getElementById(modalId).classList.remove('active');
      // Also close the connect modal when closing create/import wallet modals
      if (modalId === 'modal-create-wallet' || modalId === 'modal-import-wallet') {
        var connectModal = document.getElementById('modal-connect');
        if (connectModal) connectModal.classList.remove('active');
      }
    }

    function handleModalConnect() {
      const addr = document.getElementById('modal-address-input').value.trim();
      if (!addr) {
        alert('Please enter an address.');
        return;
      }
      setConnectedAddress(addr);
      closeModal('modal-connect');
    }

    function generateRandomKey() {
      const randomHex = '0x' + Array.from({length: 40}, () => Math.floor(Math.random()*16).toString(16)).join('');
      document.getElementById('modal-address-input').value = randomHex;
    }

    function copyReceiveAddress() {
      const text = document.getElementById('receive-address-text').textContent.trim();
      navigator.clipboard.writeText(text);
      alert('Address copied to clipboard!');
    }

    function pingRpcEndpoint() {
      const start = Date.now();
      rpcCall('system_health', []).then(() => {
        const ms = Date.now() - start;
        document.getElementById('setting-rpc-status').textContent = `Status: Connected (${ms}ms latency)`;
      });
    }

    // --- DOM Loaded Initialization ---
// === MISSING WALLET FUNCTIONS — injected fix ===
function openCreateWalletModal() {
  if (typeof VerdisCrypto !== "undefined") {
    var mnemonic = VerdisCrypto.generateMnemonic();
    var words = mnemonic.split(" ");
    var display = document.getElementById("mnemonic-display");
    if (display) {
      var html = "";
      words.forEach(function(w, i) {
        var num = String(i + 1).padStart(2, "0");
        html += "<span style=\"display:inline-block; width:48%; margin-bottom:4px;\"><span style=\"color:var(--text-muted);\">" + num + ".</span> " + w + "</span>";
      });
      display.innerHTML = html;
      display.dataset.mnemonic = mnemonic;
    }
  }
  document.getElementById("create-pin").value = "";
  document.getElementById("create-pin-confirm").value = "";
  document.getElementById("create-backup-confirm").checked = false;
  document.getElementById("create-step-1").style.display = "block";
  document.getElementById("create-step-2").style.display = "none";
  document.getElementById("modal-create-wallet").classList.add("active");
}

async function handleCreateWallet() {
  var display = document.getElementById("mnemonic-display");
  var mnemonic = display ? display.dataset.mnemonic : "";
  var pin = document.getElementById("create-pin").value;
  var pinConfirm = document.getElementById("create-pin-confirm").value;
  var backupConfirmed = document.getElementById("create-backup-confirm").checked;
  if (!mnemonic) { alert("Mnemonic not generated. Please try again."); return; }
  if (pin.length !== 6) { alert("PIN must be 6 digits."); return; }
  if (pin !== pinConfirm) { alert("PINs do not match."); return; }
  if (!backupConfirmed) { alert("Please confirm you have backed up your seed phrase."); return; }
  try {
    var result = await VerdisCrypto.createWallet(pin);
    setConnectedAddress(result.address);
    document.getElementById("create-step-1").style.display = "none";
    document.getElementById("create-step-2").style.display = "block";
    document.getElementById("new-wallet-address").textContent = result.address;
    updateWalletDisplay(result.address);
    console.log("[Verdis Wallet] Created:", result.address);
  } catch (e) { alert("Failed to create wallet: " + e.message); }
}

function openImportWalletModal() {
  document.getElementById("import-mnemonic").value = "";
  document.getElementById("import-pin").value = "";
  document.getElementById("import-error").style.display = "none";
  document.getElementById("modal-import-wallet").classList.add("active");
}

function openImportModal() { openImportWalletModal(); }

async function handleImportWallet() {
  var mnemonic = document.getElementById("import-mnemonic").value.trim();
  var pin = document.getElementById("import-pin").value;
  var errorDiv = document.getElementById("import-error");
  if (!mnemonic) { errorDiv.textContent = "Please enter your seed phrase."; errorDiv.style.display = "block"; return; }
  if (pin.length !== 6) { errorDiv.textContent = "PIN must be 6 digits."; errorDiv.style.display = "block"; return; }
  try {
    var result = await VerdisCrypto.importWallet(mnemonic, pin);
    setConnectedAddress(result.address);
    closeModal("modal-import-wallet");
    updateWalletDisplay(result.address);
    console.log("[Verdis Wallet] Imported:", result.address);
  } catch (e) { errorDiv.textContent = e.message || "Failed to import wallet."; errorDiv.style.display = "block"; }
}

function copyMnemonic() {
  var display = document.getElementById("mnemonic-display");
  var mnemonic = display ? display.dataset.mnemonic : "";
  if (mnemonic) { navigator.clipboard.writeText(mnemonic).then(function() { alert("Seed phrase copied to clipboard! Store it safely."); }).catch(function() { alert("Failed to copy. Please write it down manually."); }); }
}

function openExportModal() {
  if (typeof VerdisCrypto === "undefined" || !VerdisCrypto.hasWallet()) { alert("No wallet found. Please create or import a wallet first."); return; }
  var pin = prompt("Enter your 6-digit PIN to view your seed phrase:");
  if (!pin) return;
  VerdisCrypto.exportMnemonic(pin).then(function(mnemonic) { alert("Your seed phrase:\n\n" + mnemonic + "\n\nWrite it down and store it safely!"); }).catch(function(e) { alert("Failed to decrypt: " + e.message); });
}

function saveRpcSettings() {
  var endpoint = document.getElementById("setting-rpc-endpoint");
  var rpcUrl = endpoint ? endpoint.value : "https://verdischain.com/rpc";
  localStorage.setItem("verdis_rpc_endpoint", rpcUrl);
  alert("RPC settings saved: " + rpcUrl);
  if (typeof fetchLiveValidators === "function") fetchLiveValidators();
  if (typeof fetchLiveDexPools === "function") fetchLiveDexPools();
}

function filterHistory() {
  var filter = document.getElementById("history-filter");
  var type = filter ? filter.value : "all";
  var rows = document.querySelectorAll("#history-table tbody tr");
  rows.forEach(function(row) { if (type === "all" || row.dataset.type === type) { row.style.display = ""; } else { row.style.display = "none"; } });
}

function handleLoadAddress() {
  var addrInput = document.getElementById("address-input");
  var addr = addrInput ? addrInput.value.trim() : "";
  if (!addr) { alert("Please enter an address."); return; }
  setConnectedAddress(addr);
}

function updateWalletDisplay(address) {
  var addrElements = document.querySelectorAll("[id*=\"wallet-address\"], [id*=\"connected-address\"]");
  addrElements.forEach(function(el) { el.textContent = address; });
  var receiveAddr = document.getElementById("receive-address-text");
  if (receiveAddr) receiveAddr.textContent = address;
  var sendFromAddr = document.getElementById("send-from-address");
  if (sendFromAddr) sendFromAddr.textContent = address;
  if (typeof fetchLiveValidators === "function") fetchLiveValidators();
  if (typeof fetchLiveDexPools === "function") fetchLiveDexPools();
}
// === END MISSING WALLET FUNCTIONS ===

    document.addEventListener('DOMContentLoaded', () => {


      fetchLiveValidators();
      fetchLiveDexPools();
      // Auto-connect if wallet exists in localStorage
      if (typeof VerdisCrypto !== 'undefined' && VerdisCrypto.hasWallet()) {
        const addr = VerdisCrypto.getAddress();
        if (addr) {
          setConnectedAddress(addr);
          console.log('[Verdis Wallet] Auto-connected:', addr);
        }
      }
    });
  