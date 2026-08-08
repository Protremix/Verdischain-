
// RPC CONFIGURATION
const RPC_URL = '/rpc';
const FALLBACK_RPC_URL = 'https://verdischain.com/rpc';
let nextId = 1;

// Helper to query JSON-RPC
async function rpc(method, params = []) {
  const payload = JSON.stringify({ jsonrpc: '2.0', method, params, id: nextId++ });
  try {
    const res = await fetch(RPC_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: payload
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    if (data.error) throw data.error;
    return data.result;
  } catch (err) {
    // Fallback to full domain if relative proxy fails
    const res = await fetch(FALLBACK_RPC_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: payload
    });
    const data = await res.json();
    if (data.error) throw data.error;
    return data.result;
  }
}

// Convert Hex to Number
function hexToNum(hex) {
  if (!hex) return 0;
  return parseInt(hex, 16);
}

// Load Live RPC Data
async function loadLiveRPC() {
  const statusEl = document.getElementById('nav-network');
  try {
    // 1. Get Block Header
    const header = await rpc('chain_getHeader');
    if (header && header.number) {
      const blockNum = hexToNum(header.number).toLocaleString();
      document.getElementById('stat-block').textContent = '#' + blockNum;
      document.getElementById('hero-block-num').textContent = blockNum;
    }

    // 2. Get Peers & Sync Status
    try {
      const health = await rpc('system_health');
      if (health) {
        document.getElementById('stat-peers').textContent = health.peers || 0;
      }
    } catch (e) {
      }

    // 3. Get Active Validators
    try {
      const validators = await rpc('dpos_activeValidators');
      if (Array.isArray(validators)) {
        document.getElementById('stat-validators').textContent = validators.length;
      }
    } catch (e) {
      }

    // 4. Try eco-specific RPC calls
    try {
      const credits = await rpc('eco_getCarbonCreditCount');
      if (credits && credits.totalOffset) {
        }
    } catch (e) {
      try {
        const creditsAlt = await rpc('eco_carbonCredits');
        if (creditsAlt) } catch (err) {}
    }

    try {
      const reforest = await rpc('eco_getReforestProjectCount');
      if (reforest) } catch (e) {
      try {
        const reforestAlt = await rpc('eco_reforestationLog');
        if (reforestAlt) } catch (err) {}
    }

    if (statusEl) statusEl.textContent = 'Connected';
  } catch (err) {
    console.warn('RPC Poll Error:', err);
    if (statusEl) statusEl.textContent = 'RPC Standby';
  }
}

// SIMULATOR CALCULATOR
function updateScoreCalc() {
  const ren = parseFloat(document.getElementById('input-ren').value);
  const off = parseFloat(document.getElementById('input-off').value);
  const eff = parseFloat(document.getElementById('input-eff').value);

  document.getElementById('val-ren-txt').innerText = ren + '%';
  document.getElementById('val-off-txt').innerText = off + '%';
  document.getElementById('val-eff-txt').innerText = eff;

  // Formula: Renewable(30%) + Offset(25%) + Hardware(20%) + Fixed Uptime & Community(25%)
  const score = (ren * 0.30) + (off * 0.25) + (eff * 0.20) + 24.5;
  document.getElementById('calc-final-score').innerText = score.toFixed(1);

  const bonus = ((score - 50) * 0.33).toFixed(1);
  document.getElementById('calc-apy-boost').innerText = '+' + (bonus > 0 ? bonus : '0.0') + '% Staking Bonus';
}

// TABLE FILTER & SEARCH
function filterProjects(region, evt) {
  const btns = document.querySelectorAll('.btn-filter');
  btns.forEach(b => b.classList.remove('active'));
  if (evt && evt.target) evt.target.classList.add('active');

  const rows = document.querySelectorAll('#reforestationTable tbody tr');
  rows.forEach(row => {
    if (region === 'All' || row.getAttribute('data-region') === region) {
      row.style.display = '';
    } else {
      row.style.display = 'none';
    }
  });
}

function searchTable() {
  const query = document.getElementById('projectSearch').value.toLowerCase();
  const rows = document.querySelectorAll('#reforestationTable tbody tr');
  rows.forEach(row => {
    const text = row.innerText.toLowerCase();
    row.style.display = text.includes(query) ? '' : 'none';
  });
}

// CERTIFICATE PREVIEW
function updateCertPreview() {
  const name = document.getElementById('certNameInput').value || 'Verdis Eco Alliance Corp';
  const ton = parseFloat(document.getElementById('certTonInput').value) || 0;
  const proj = document.getElementById('certProjectSelect').value;

  document.getElementById('pcName').innerText = name;
  document.getElementById('pcAmount').innerText = ton.toFixed(2) + ' tCO2e';
  document.getElementById('pcProject').innerText = proj;
  
  let hashNum = 0;
  for (let i = 0; i < name.length; i++) hashNum += name.charCodeAt(i);
  let hashDisplay = '0x' + Math.abs(Math.floor(hashNum * ton * 889412)).toString(16).padStart(8, '0') + '...12e8';
  document.getElementById('pcHash').innerText = 'HASH: ' + hashDisplay;
}

// MODAL LOGIC
let currentUnitPrice = 14.50;

function openModal(title, price, isRetire = false) {
  currentUnitPrice = price;
  document.getElementById('modalTitle').innerText = (isRetire ? 'Retire cVRDX Credits: ' : 'Buy cVRDX Credits: ') + title;
  document.getElementById('modalUnitPrice').innerText = '$' + price.toFixed(2);
  document.getElementById('modalAmount').value = 10;
  calcModalTotal();
  document.getElementById('tradeModal').classList.add('active');
}

function closeModal() {
  document.getElementById('tradeModal').classList.remove('active');
}

function calcModalTotal() {
  const amt = parseFloat(document.getElementById('modalAmount').value) || 0;
  const total = amt * currentUnitPrice;
  document.getElementById('modalTotalCost').innerText = '$' + total.toFixed(2);
}

function confirmTrade() {
  alert('Transaction submitted to Verdis Mainnet! Your cVRDX carbon credits order is processing.');
  closeModal();
}

// INITIALIZATION
window.addEventListener('DOMContentLoaded', () => {
  loadLiveRPC();
  setInterval(loadLiveRPC, 12000);
});
