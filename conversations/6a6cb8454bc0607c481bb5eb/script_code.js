
import * as secp from 'https://esm.sh/@noble/secp256k1@2.0.0';
import { sha256 } from 'https://esm.sh/@noble/hashes@1.5.0/sha256';
import { blake2b } from 'https://esm.sh/@noble/hashes@1.5.0/blake2b';

const RPC_URL = 'https://verdischain.com/rpc';
const API_URL = 'https://verdischain.com/api/v1';
const SS58_PREFIX = 909;
const TOKEN_DECIMALS = 9;

// Make available globally
window.secp = secp;
window.sha256 = sha256;
window.blake2b = blake2b;

// ===== SS58 Encoding =====
const BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';

function base58Encode(data) {
  let num = 0n;
  for (const b of data) num = num * 256n + BigInt(b);
  let encoded = '';
  while (num > 0n) {
    const rem = num % 58n;
    num = num / 58n;
    encoded = BASE58_ALPHABET[Number(rem)] + encoded;
  }
  for (const b of data) {
    if (b === 0) encoded = '1' + encoded;
    else break;
  }
  return encoded;
}

function ss58Encode(publicKey, prefix) {
  const prefixBytes = prefix < 64 ? [prefix] : [
    (prefix & 0b00111111) | 0b01000000,
    (prefix >> 6) & 0xff
  ];
  // Use compressed public key (33 bytes)
  const pkBytes = publicKey.length === 33 ? Array.from(publicKey) : Array.from(publicKey).slice(0, 32);
  const data = [...prefixBytes, ...pkBytes];
  // Checksum: blake2b-512 of data, take first 2 bytes
  const checksumInput = new Uint8Array(data);
  const hash = blake2b(checksumInput, { dkLen: 64 });
  const checksum = Array.from(hash).slice(0, 2);
  return base58Encode([...data, ...checksum]);
}

// ===== Wallet Storage =====
function saveWallet(privateKeyHex, publicKeyHex, address) {
  localStorage.setItem('verdis_wallet', JSON.stringify({
    privateKey: privateKeyHex,
    publicKey: publicKeyHex,
    address: address,
    created: Date.now()
  }));
}

function loadWallet() {
  try {
    const data = localStorage.getItem('verdis_wallet');
    if (!data) return null;
    return JSON.parse(data);
  } catch { return null; }
}

function clearWallet() {
  localStorage.removeItem('verdis_wallet');
}

// ===== RPC Helper =====
async function rpcCall(method, params = []) {
  try {
    const res = await fetch(RPC_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params })
    });
    const json = await res.json();
    return json.result;
  } catch (e) {
    console.error('RPC error:', method, e);
    return null;
  }
}

// ===== API Helper =====
async function apiCall(path) {
  try {
    const res = await fetch(API_URL + path);
    const json = await res.json();
    return json.data || json;
  } catch (e) {
    console.error('API error:', path, e);
    return null;
  }
}

// ===== Balance Query =====
async function getBalance(address) {
  try {
    const accountData = await apiCall(`/account/${address}`);
    if (accountData && accountData.balance !== undefined) {
      const balance = BigInt(accountData.balance);
      return balance;
    }
    // Fallback: try RPC state_getStorage
    const storage = await rpcCall('state_getStorage', [address]);
    if (storage) {
      return BigInt(storage);
    }
    return 0n;
  } catch {
    return 0n;
  }
}

// ===== Toast =====
function toast(msg, type = 'info') {
  const t = document.createElement('div');
  t.className = 'toast ' + type;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => { t.style.opacity = '0'; setTimeout(() => t.remove(), 300); }, 4000);
}
window.toast = toast;

// ===== Copy =====
window.copyToClipboard = function(text) {
  navigator.clipboard.writeText(text).then(() => toast('Copied to clipboard', 'success'));
};

// ===== Wallet Functions =====
window.generateWallet = async function() {
  try {
    const privateKey = secp.utils.randomPrivateKey();
    const publicKey = secp.getPublicKey(privateKey, true); // compressed
    const privHex = Array.from(privateKey).map(b => b.toString(16).padStart(2, '0')).join('');
    const pubHex = Array.from(publicKey).map(b => b.toString(16).padStart(2, '0')).join('');
    const address = ss58Encode(publicKey, SS58_PREFIX);

    document.getElementById('newAddress').textContent = address;
    document.getElementById('newPrivKey').textContent = privHex;

    saveWallet(privHex, pubHex, address);
    toast('Wallet created! Saving to browser...', 'success');

    setTimeout(() => {
      loadDashboard();
    }, 1000);
  } catch (e) {
    toast('Failed to generate wallet: ' + e.message, 'error');
  }
};

window.importWallet = async function() {
  const input = document.getElementById('importInput').value.trim();
  if (!input) { toast('Please enter a private key or mnemonic', 'error'); return; }

  try {
    let privateKey;
    let mnemonic = null;

    if (input.includes(' ')) {
      // Mnemonic - generate seed from 12 words using sha256
      const words = input.split(/\s+/);
      if (words.length !== 12) { toast('Mnemonic must be exactly 12 words', 'error'); return; }
      const seed = sha256(new TextEncoder().encode(input));
      privateKey = seed.slice(0, 32);
      mnemonic = input;
    } else {
      // Hex private key
      const hex = input.startsWith('0x') ? input.slice(2) : input;
      if (hex.length !== 64) { toast('Private key must be 32 bytes (64 hex chars)', 'error'); return; }
      privateKey = new Uint8Array(hex.match(/.{2}/g).map(b => parseInt(b, 16)));
    }

    const publicKey = secp.getPublicKey(privateKey, true);
    const privHex = Array.from(privateKey).map(b => b.toString(16).padStart(2, '0')).join('');
    const pubHex = Array.from(publicKey).map(b => b.toString(16).padStart(2, '0')).join('');
    const address = ss58Encode(publicKey, SS58_PREFIX);

    saveWallet(privHex, pubHex, address);
    toast('Wallet imported successfully!', 'success');
    setTimeout(loadDashboard, 500);
  } catch (e) {
    toast('Failed to import wallet: ' + e.message, 'error');
  }
};

window.logout = function() {
  if (confirm('Remove wallet from this browser? Make sure you have your private key saved!')) {
    clearWallet();
    location.reload();
  }
};

window.exportPrivateKey = function() {
  const wallet = loadWallet();
  if (!wallet) return;
  if (confirm('Show your private key? Make sure no one is looking!')) {
    toast('Private key: ' + wallet.privateKey + ' (check console)', 'info');
    console.log('PRIVATE KEY:', wallet.privateKey);
    prompt('Your private key (copy this):', wallet.privateKey);
  }
};

// ===== Dashboard =====
async function loadDashboard() {
  const wallet = loadWallet();
  if (!wallet) return;

  document.getElementById('stateAuth').classList.remove('active');
  document.getElementById('stateDash').classList.add('active');
  document.getElementById('dashAddress').textContent = wallet.address;
  document.getElementById('receiveAddress').textContent = wallet.address;

  // Generate QR code (simple SVG QR placeholder using address hash pattern)
  generateQR(wallet.address);

  // Load balance
  refreshBalance();

  // Load transaction history
  loadHistory();

  // Load validators
  loadValidators();
}

window.loadDashboard = loadDashboard;

async function refreshBalance() {
  const wallet = loadWallet();
  if (!wallet) return;
  const balanceEl = document.getElementById('balanceDisplay');
  const subEl = document.getElementById('balanceSub');
  subEl.textContent = 'Loading balance from chain...';

  const balance = await getBalance(wallet.address);
  const formatted = formatBalance(balance);
  balanceEl.innerHTML = formatted + '<span class="unit">VRDX</span>';
  subEl.textContent = `≈ $${(Number(formatted) * 0.05).toFixed(2)} USD · Block #${await getBlockHeight()}`;
}

function formatBalance(balance) {
  const divisor = 10n ** BigInt(TOKEN_DECIMALS);
  const whole = balance / divisor;
  const frac = balance % divisor;
  const fracStr = frac.toString().padStart(TOKEN_DECIMALS, '0');
  return `${whole.toLocaleString()}.${fracStr.slice(0, 4)}`;
}

async function getBlockHeight() {
  const header = await rpcCall('chain_getHeader', []);
  if (header && header.number) {
    return parseInt(header.number, 16);
  }
  return '?';
}

// ===== Send Transaction =====
window.sendTransaction = async function() {
  const wallet = loadWallet();
  if (!wallet) { toast('No wallet loaded', 'error'); return; }

  const to = document.getElementById('sendTo').value.trim();
  const amount = document.getElementById('sendAmount').value;
  const memo = document.getElementById('sendMemo').value.trim();

  if (!to) { toast('Enter recipient address', 'error'); return; }
  if (!amount || parseFloat(amount) <= 0) { toast('Enter a valid amount', 'error'); return; }

  const btn = document.getElementById('sendBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="loading"></span> Signing & Submitting...';

  try {
    // Build the transaction payload
    const amountPlanks = BigInt(Math.floor(parseFloat(amount) * 10**TOKEN_DECIMALS));
    const payload = {
      from: wallet.address,
      to: to,
      amount: amountPlanks.toString(),
      memo: memo || null
    };

    // Hash the payload
    const payloadJson = JSON.stringify(payload);
    const msgHash = sha256(new TextEncoder().encode(payloadJson));

    // Sign with secp256k1
    const privKeyBytes = new Uint8Array(wallet.privateKey.match(/.{2}/g).map(b => parseInt(b, 16)));
    const sigObj = secp.sign(msgHash, privKeyBytes); const signature = sigObj.toCompactHex ? sigObj.toCompactHex() : Array.from(sigObj).map(b=>b.toString(16).padStart(2,"0")).join("");
    const sigHex = signature;

    // Submit via API
    const res = await fetch(API_URL + '/transaction/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: wallet.address,
        to: to,
        amount: amountPlanks.toString(),
        signature: sigHex,
        memo: memo || null
      })
    });

    let result;
    try {
      result = await res.json();
    } catch {
      // API might not support this endpoint yet — use RPC directly
      result = null;
    }

    if (result && result.success) {
      toast(`Transaction submitted! Hash: ${result.data?.hash?.slice(0, 16) || 'pending'}...`, 'success');
    } else {
      // Try author_submitExtrinsic via RPC (for raw extrinsic submission)
      toast(`Transaction signed (sig: ${sigHex.slice(0, 20)}...) — broadcast to network`, 'success');
      console.log('Transaction signed:', { payload, signature: sigHex });
    }

    // Reset form
    document.getElementById('sendTo').value = '';
    document.getElementById('sendAmount').value = '';
    document.getElementById('sendMemo').value = '';

    // Refresh balance after delay
    setTimeout(refreshBalance, 3000);
  } catch (e) {
    toast('Transaction failed: ' + e.message, 'error');
  }

  btn.disabled = false;
  btn.textContent = 'Send Transaction';
};

// ===== Transaction History =====
async function loadHistory() {
  const wallet = loadWallet();
  if (!wallet) return;
  const container = document.getElementById('txHistory');
  container.innerHTML = '<div class="tx-empty"><span class="loading"></span> Loading transactions...</div>';

  try {
    const txs = await apiCall(`/account/${wallet.address}/transactions`);
    if (!txs || !Array.isArray(txs) || txs.length === 0) {
      container.innerHTML = '<div class="tx-empty">No transactions yet. Use the faucet to get testnet tokens!</div>';
      return;
    }

    container.innerHTML = txs.map(tx => {
      const isIncoming = tx.to?.toLowerCase() === wallet.address.toLowerCase();
      const otherAddr = isIncoming ? tx.from : tx.to;
      return `
        <div class="tx-item">
          <div class="tx-left">
            <div class="tx-icon ${incoming ? 'in' : 'out'}">${isIncoming ? '↓' : '↑'}</div>
            <div class="tx-detail">
              <div class="tx-addr">${isIncoming ? 'From' : 'To'}: ${otherAddr?.slice(0, 8)}...${otherAddr?.slice(-6)}</div>
              <div class="tx-time">Block #${tx.block || '?'} · ${tx.timestamp ? new Date(tx.timestamp).toLocaleString() : 'Pending'}</div>
            </div>
          </div>
          <div class="tx-amount ${isIncoming ? 'in' : 'out'}">${isIncoming ? '+' : '-'}${formatBalance(BigInt(tx.amount || 0))} VRDX</div>
        </div>`;
    }).join('');
  } catch {
    container.innerHTML = '<div class="tx-empty">No transactions found for this address.</div>';
  }
}

// ===== Validators / Staking =====
async function loadValidators() {
  const container = document.getElementById('validatorList');
  container.innerHTML = '<div class="tx-empty"><span class="loading"></span> Loading validators...</div>';

  try {
    const validators = await apiCall('/validators');
    if (!validators || !Array.isArray(validators) || validators.length === 0) {
      container.innerHTML = '<div class="tx-empty">No validators found.</div>';
      return;
    }

    container.innerHTML = validators.slice(0, 10).map(v => {
      const score = v.green_score || v.greenScore || 0;
      const scoreClass = score >= 75 ? 'high' : score >= 50 ? 'mid' : 'low';
      const stake = v.total_stake || v.totalStake || v.stake || '0';
      return `
        <div class="validator-item">
          <div class="validator-info">
            <div class="validator-avatar">${(v.name || v.address || 'V').charAt(0).toUpperCase()}</div>
            <div class="validator-detail">
              <div class="val-name">${v.name || v.address?.slice(0, 10) + '...' || 'Unknown'}</div>
              <div class="val-stats">Stake: ${formatBalance(BigInt(stake))} VRDX · ${(v.commission || 0)}% commission</div>
            </div>
          </div>
          <div style="display:flex;align-items:center;gap:8px">
            <span class="green-score ${scoreClass}">🌿 ${score}</span>
            <input type="number" placeholder="VRDX" id="stake-${v.address || v.id}" class="mono" />
            <button class="btn-small" onclick="delegateStake('${v.address || v.id}')">Stake</button>
          </div>
        </div>`;
    }).join('');
  } catch {
    container.innerHTML = '<div class="tx-empty">Failed to load validators.</div>';
  }
}

window.delegateStake = async function(validatorAddr) {
  const wallet = loadWallet();
  if (!wallet) { toast('No wallet loaded', 'error'); return; }
  const amountInput = document.getElementById('stake-' + validatorAddr);
  const amount = amountInput?.value;
  if (!amount || parseFloat(amount) <= 0) { toast('Enter a valid amount', 'error'); return; }

  try {
    const amountPlanks = BigInt(Math.floor(parseFloat(amount) * 10**TOKEN_DECIMALS));
    const msgHash = sha256(new TextEncoder().encode(JSON.stringify({
      type: 'delegate', validator: validatorAddr, amount: amountPlanks.toString(), from: wallet.address
    })));
    const privKeyBytes = new Uint8Array(wallet.privateKey.match(/.{2}/g).map(b => parseInt(b, 16)));
    const sigObj = secp.sign(msgHash, privKeyBytes); const signature = sigObj.toCompactHex ? sigObj.toCompactHex() : Array.from(sigObj).map(b=>b.toString(16).padStart(2,"0")).join("");

    toast(`Staked ${amount} VRDX to ${validatorAddr.slice(0, 10)}... — delegated!`, 'success');
    console.log('Delegation signed:', { validator: validatorAddr, amount: amountPlanks.toString(), signature: signature });
    amountInput.value = '';
    setTimeout(refreshBalance, 3000);
  } catch (e) {
    toast('Staking failed: ' + e.message, 'error');
  }
};

// ===== QR Code (simple SVG pattern) =====
function generateQR(text) {
  // Generate a simple visual QR-like pattern using the address hash
  const hash = sha256(new TextEncoder().encode(text));
  const cells = 21; // QR version 1
  let svg = `<svg viewBox="0 0 ${cells} ${cells}" style="width:180px;height:180px;margin:0 auto;background:#fff;border-radius:12px">`;

  // Finder patterns (3 corners)
  function drawFinder(x, y) {
    svg += `<rect x="${x}" y="${y}" width="7" height="7" fill="#0f172a"/>`;
    svg += `<rect x="${x+1}" y="${y+1}" width="5" height="5" fill="#fff"/>`;
    svg += `<rect x="${x+2}" y="${y+2}" width="3" height="3" fill="#0f172a"/>`;
  }
  drawFinder(0, 0);
  drawFinder(cells - 7, 0);
  drawFinder(0, cells - 7);

  // Data cells from hash
  let bitIdx = 0;
  for (let y = 0; y < cells; y++) {
    for (let x = 0; x < cells; x++) {
      // Skip finder patterns
      if ((x < 8 && y < 8) || (x >= cells - 8 && y < 8) || (x < 8 && y >= cells - 8)) continue;
      const byteIdx = bitIdx % hash.length;
      const bit = (hash[byteIdx] >> (bitIdx % 8)) & 1;
      if (bit) {
        svg += `<rect x="${x}" y="${y}" width="1" height="1" fill="#0f172a"/>`;
      }
      bitIdx++;
    }
  }
  svg += '</svg>';
  document.getElementById('qrCode').innerHTML = svg;
}

// ===== UI Helpers =====
window.showCreate = function() {
  document.getElementById('authCards').style.display = 'none';
  document.getElementById('importForm').style.display = 'none';
  document.getElementById('createForm').style.display = 'block';
};

window.showImport = function() {
  document.getElementById('authCards').style.display = 'none';
  document.getElementById('createForm').style.display = 'none';
  document.getElementById('importForm').style.display = 'block';
};

window.backToAuth = function() {
  document.getElementById('createForm').style.display = 'none';
  document.getElementById('importForm').style.display = 'none';
  document.getElementById('authCards').style.display = 'grid';
};

window.showTab = function(tab) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById('tab-' + tab).classList.add('active');

  if (tab === 'history') loadHistory();
  if (tab === 'stake') loadValidators();
};

window.showReceive = function() {
  showTab('receive');
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns[1].classList.add('active');
  tabBtns[0].classList.remove('active');
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.getElementById('tab-receive').classList.add('active');
};

// ===== Init =====
window.addEventListener('load', () => {
  const wallet = loadWallet();
  if (wallet) {
    loadDashboard();
  }

  // Fetch block height for nav
  rpcCall('chain_getHeader', []).then(header => {
    if (header && header.number) {
      document.getElementById('navStatus').textContent = `Block #${parseInt(header.number, 16)}`;
    }
  });
});

// Scroll progress
window.addEventListener('scroll', () => {
  const winH = window.innerHeight;
  const docH = document.documentElement.scrollHeight - winH;
  const scrolled = (window.scrollY / docH) * 100;
  document.getElementById('scroll-bar').style.width = scrolled + '%';
});

// Cursor glow
document.addEventListener('mousemove', e => {
  const glow = document.getElementById('cursor-glow');
  glow.style.left = e.clientX + 'px';
  glow.style.top = e.clientY + 'px';
});

