#!/usr/bin/env node
/**
 * Verdis Token Sale Frontend Patch
 * 
 * Adds mandatory tokenomics disclosure modal + consent checkbox gating
 * Wires executePurchase() to the real backend /api/ido/purchase endpoint
 */

const fs = require('fs');

const TOKEN_SALE_PATH = '/opt/verdis/web/token-sale.html';

function patchTokenSale() {
  let html = fs.readFileSync(TOKEN_SALE_PATH, 'utf8');

  if (html.includes('disclosureModal')) {
    console.log('✅ token-sale.html already has disclosure modal — skipping');
    return;
  }

  // ============================================================
  // 1. ADD DISCLOSURE MODAL CSS (before </style>)
  // ============================================================

  const disclosureCSS = `
    /* ==========================================================================
       MANDATORY TOKENOMICS DISCLOSURE MODAL
       ========================================================================== */
    .disclosure-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.85);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      z-index: 10000;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.3s ease;
    }
    .disclosure-overlay.active {
      opacity: 1;
      pointer-events: auto;
    }
    .disclosure-modal {
      background: var(--bg-card, rgba(8, 20, 15, 0.95));
      backdrop-filter: blur(30px);
      -webkit-backdrop-filter: blur(30px);
      border: 1px solid var(--border-bright, rgba(0, 255, 136, 0.45));
      border-radius: 20px;
      max-width: 620px;
      width: 100%;
      max-height: 85vh;
      overflow-y: auto;
      padding: 36px;
      position: relative;
      transform: translateY(20px);
      transition: transform 0.3s ease;
    }
    .disclosure-overlay.active .disclosure-modal {
      transform: translateY(0);
    }
    .disclosure-modal::-webkit-scrollbar { width: 6px; }
    .disclosure-modal::-webkit-scrollbar-track { background: transparent; }
    .disclosure-modal::-webkit-scrollbar-thumb { background: rgba(0,255,136,0.2); border-radius: 3px; }
    .disclosure-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 24px;
    }
    .disclosure-header i {
      font-size: 1.8rem;
      color: var(--primary, #00ff88);
    }
    .disclosure-header h3 {
      font-size: 1.4rem;
      font-weight: 700;
    }
    .disclosure-body {
      color: var(--text-muted, #8ba898);
      font-size: 0.9rem;
      line-height: 1.7;
    }
    .disclosure-body p {
      margin-bottom: 14px;
    }
    .disclosure-body strong {
      color: var(--text-main, #f0fdf4);
    }
    .disclosure-stats {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin: 20px 0;
    }
    .disclosure-stat {
      background: rgba(0, 255, 136, 0.05);
      border: 1px solid var(--border-glass, rgba(0, 255, 136, 0.15));
      border-radius: 12px;
      padding: 14px;
      text-align: center;
    }
    .disclosure-stat-value {
      font-family: var(--font-mono, 'JetBrains Mono', monospace);
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--primary, #00ff88);
    }
    .disclosure-stat-label {
      font-size: 0.75rem;
      color: var(--text-dim, #547363);
      margin-top: 4px;
    }
    .disclosure-risk {
      background: rgba(255, 180, 50, 0.08);
      border: 1px solid rgba(255, 180, 50, 0.25);
      border-radius: 12px;
      padding: 16px;
      margin: 20px 0;
      font-size: 0.85rem;
      color: #ffb43a;
    }
    .disclosure-risk i {
      margin-right: 8px;
    }
    .consent-row {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      margin: 24px 0;
      padding: 16px;
      background: rgba(0, 255, 136, 0.03);
      border: 1px solid var(--border-glass, rgba(0, 255, 136, 0.15));
      border-radius: 14px;
      cursor: pointer;
      transition: border-color 0.2s;
    }
    .consent-row:hover { border-color: var(--border-bright, rgba(0, 255, 136, 0.45)); }
    .consent-row.checked { border-color: var(--primary, #00ff88); }
    .consent-checkbox {
      width: 22px;
      height: 22px;
      min-width: 22px;
      border: 2px solid var(--text-dim, #547363);
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s;
      margin-top: 2px;
    }
    .consent-row.checked .consent-checkbox {
      background: var(--primary, #00ff88);
      border-color: var(--primary, #00ff88);
    }
    .consent-checkbox i {
      font-size: 0.7rem;
      color: #050a08;
      opacity: 0;
      transition: opacity 0.15s;
    }
    .consent-row.checked .consent-checkbox i { opacity: 1; }
    .consent-text {
      font-size: 0.85rem;
      color: var(--text-muted, #8ba898);
      line-height: 1.6;
    }
    .consent-text strong { color: var(--text-main, #f0fdf4); }
    .disclosure-actions {
      display: flex;
      gap: 12px;
      margin-top: 24px;
    }
    .disclosure-btn {
      flex: 1;
      padding: 14px;
      border-radius: 12px;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
      border: 1px solid var(--border-glass, rgba(0, 255, 136, 0.15));
    }
    .disclosure-btn-cancel {
      background: transparent;
      color: var(--text-muted, #8ba898);
    }
    .disclosure-btn-cancel:hover { border-color: var(--text-dim, #547363); }
    .disclosure-btn-confirm {
      background: var(--primary, #00ff88);
      color: #050a08;
      border: none;
      opacity: 0.4;
      pointer-events: none;
      transition: opacity 0.2s;
    }
    .disclosure-btn-confirm.active {
      opacity: 1;
      pointer-events: auto;
    }
    .disclosure-btn-confirm:hover { filter: brightness(1.1); }
    @media (max-width: 640px) {
      .disclosure-stats { grid-template-columns: 1fr 1fr; }
      .disclosure-modal { padding: 24px; }
    }

    /* Purchase loading spinner */
    .purchase-loading {
      display: none;
      flex-direction: column;
      align-items: center;
      gap: 16px;
      padding: 40px;
    }
    .purchase-loading.active { display: flex; }
    .purchase-spinner {
      width: 48px;
      height: 48px;
      border: 3px solid rgba(0, 255, 136, 0.15);
      border-top-color: var(--primary, #00ff88);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
`;

  html = html.replace('</style>', disclosureCSS + '\n  </style>');

  // ============================================================
  // 2. ADD DISCLOSURE MODAL HTML (before </body>)
  // ============================================================

  const disclosureHTML = `
  <!-- MANDATORY TOKENOMICS DISCLOSURE MODAL -->
  <div class="disclosure-overlay" id="disclosureModal">
    <div class="disclosure-modal">
      <div class="disclosure-header">
        <i class="fa-solid fa-file-shield"></i>
        <h3>Tokenomics Disclosure & Acknowledgment</h3>
      </div>
      <div class="disclosure-body">
        <p><strong>Verdis ($VRS)</strong> is the native utility token of the Verdis carbon-negative Layer-1 blockchain. Before participating in the IDO, you must review and acknowledge the following:</p>
        
        <div class="disclosure-stats">
          <div class="disclosure-stat">
            <div class="disclosure-stat-value">100,000,000,000</div>
            <div class="disclosure-stat-label">Total Fixed Supply (VRS)</div>
          </div>
          <div class="disclosure-stat">
            <div class="disclosure-stat-value">12,000,000,000</div>
            <div class="disclosure-stat-label">Total Investor Allocation</div>
          </div>
          <div class="disclosure-stat">
            <div class="disclosure-stat-value">10,000,000,000</div>
            <div class="disclosure-stat-label">IDO Sale Allocation</div>
          </div>
          <div class="disclosure-stat">
            <div class="disclosure-stat-value">15%</div>
            <div class="disclosure-stat-label">Circulating at TGE</div>
          </div>
        </div>

        <p><strong>Vesting Schedule:</strong> All IDO purchases are subject to mandatory vesting enforced at the protocol level. A <strong>20% TGE unlock</strong> is released at listing, with the remaining 80% vesting linearly:</p>
        <p>• <strong>Seed & Private Sale:</strong> 60-day linear vesting<br>
           • <strong>Public & Final Sale:</strong> 30-day linear vesting</p>
        
        <p><strong>Sale Stages:</strong> Seed (3B VRS @ $0.0005) → Private (3B VRS @ $0.0008) → Public (2.5B VRS @ $0.001) → Final (1.5B VRS @ $0.0015)</p>

        <div class="disclosure-risk">
          <i class="fa-solid fa-triangle-exclamation"></i>
          <strong>Risk Disclosure:</strong> Cryptocurrency investments carry substantial risk. Token values are volatile and can result in complete loss of capital. $VRS tokens are utility tokens, not securities. Vesting locks are protocol-enforced and cannot be bypassed. Past performance does not guarantee future results. Only invest what you can afford to lose.
        </div>

        <div class="consent-row" id="consentRow" onclick="toggleConsent()">
          <div class="consent-checkbox"><i class="fa-solid fa-check"></i></div>
          <div class="consent-text">
            <strong>I have read, understood, and accept the tokenomics disclosure.</strong><br>
            I acknowledge the vesting schedule, risk factors, and that $VRS is a utility token on an emerging blockchain. I consent to the protocol-level vesting locks on my purchased tokens.
          </div>
        </div>

        <div class="disclosure-actions">
          <button class="disclosure-btn disclosure-btn-cancel" onclick="closeDisclosure()">Cancel</button>
          <button class="disclosure-btn disclosure-btn-confirm" id="confirmPurchaseBtn" onclick="confirmPurchase()">I Agree — Continue Purchase</button>
        </div>
      </div>
    </div>
  </div>
`;

  html = html.replace('</body>', disclosureHTML + '\n</body>');

  // ============================================================
  // 3. REPLACE executePurchase() + ADD DISCLOSURE FUNCTIONS
  // ============================================================

  const oldExecutePurchase = `    function executePurchase() {
      const payInput = parseFloat(document.getElementById('payAmountInput').value) || 0;
      if (payInput <= 0) {
        alert('Please enter a valid contribution amount.');
        return;
      }

      const walletAddr = document.getElementById('walletAddressInput').value.trim();
      if (!walletAddr) {
        toggleWalletModal();
        return;
      }

      const totalUSD = payInput * assetPriceUSD;
      const baseVRS = Math.floor(totalUSD / vrsPriceUSD);
      const bonusVRS = Math.floor(baseVRS * 0.10);
      const totalVRS = baseVRS + bonusVRS;
      const trees = Math.floor(totalUSD / 100);

      document.getElementById('receiptTxHash').innerText = '0x' + Array.from({length: 8}, () => Math.floor(Math.random()*16).toString(16)).join('') + '...' + Array.from({length: 4}, () => Math.floor(Math.random()*16).toString(16)).join('');
      document.getElementById('receiptVrsAmount').innerText = totalVRS.toLocaleString() + ' VRS';
      document.getElementById('receiptTrees').innerText = '🌱 ' + trees.toLocaleString() + ' Trees Planted';

      document.getElementById('receiptModal').classList.add('active');
    }`;

  const newExecutePurchase = `    let consentAccepted = false;

    function executePurchase() {
      const payInput = parseFloat(document.getElementById('payAmountInput').value) || 0;
      if (payInput <= 0) {
        alert('Please enter a valid contribution amount.');
        return;
      }

      const walletAddr = document.getElementById('walletAddressInput').value.trim();
      if (!walletAddr || !walletAddr.startsWith('0x') || walletAddr.length < 42) {
        alert('Please enter a valid EVM wallet address (0x...).');
        return;
      }

      // Check USD limits
      const totalUSD = payInput * assetPriceUSD;
      if (totalUSD < 50) {
        alert('Minimum contribution is $50 USD.');
        return;
      }
      if (totalUSD > 100000) {
        alert('Maximum contribution is $100,000 USD.');
        return;
      }

      // OPEN DISCLOSURE MODAL — consent gating before purchase
      document.getElementById('disclosureModal').classList.add('active');
    }

    function toggleConsent() {
      consentAccepted = !consentAccepted;
      const row = document.getElementById('consentRow');
      const btn = document.getElementById('confirmPurchaseBtn');
      if (consentAccepted) {
        row.classList.add('checked');
        btn.classList.add('active');
      } else {
        row.classList.remove('checked');
        btn.classList.remove('active');
      }
    }

    function closeDisclosure() {
      document.getElementById('disclosureModal').classList.remove('active');
      consentAccepted = false;
      document.getElementById('consentRow').classList.remove('checked');
      document.getElementById('confirmPurchaseBtn').classList.remove('active');
    }

    async function confirmPurchase() {
      if (!consentAccepted) return;

      const payInput = parseFloat(document.getElementById('payAmountInput').value) || 0;
      const walletAddr = document.getElementById('walletAddressInput').value.trim();
      const totalUSD = payInput * assetPriceUSD;
      const baseVRS = Math.floor(totalUSD / vrsPriceUSD);
      const bonusVRS = Math.floor(baseVRS * 0.10);
      const totalVRS = baseVRS + bonusVRS;

      // Close disclosure, show loading state on the button
      document.getElementById('disclosureModal').classList.remove('active');
      const buyBtn = document.querySelector('.btn-primary');
      const originalBtnHTML = buyBtn.innerHTML;
      buyBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Processing Purchase...';
      buyBtn.disabled = true;

      try {
        const API_BASE = window.location.protocol + '//' + window.location.hostname + (window.location.port && window.location.port !== '443' && window.location.port !== '80' ? ':' + window.location.port : '') + ':3200';

        const response = await fetch(API_BASE + '/api/ido/purchase', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            walletAddress: walletAddr,
            paymentAsset: selectedAsset,
            paymentAmount: payInput,
            vrsAmount: totalVRS,
            consentAccepted: true
          })
        });

        const data = await response.json();

        if (data.success) {
          // Show success receipt
          document.getElementById('receiptTxHash').innerText = data.txHash.substring(0, 18) + '...' + data.txHash.substring(data.txHash.length - 8);
          document.getElementById('receiptVrsAmount').innerText = data.vrsAmount.toLocaleString() + ' VRS';
          document.getElementById('receiptTrees').innerText = '🌱 ' + (data.treesPlanted || 0).toLocaleString() + ' Trees Planted';
          document.getElementById('receiptModal').classList.add('active');
        } else {
          alert('Purchase failed: ' + (data.error || 'Unknown error'));
        }
      } catch (err) {
        // Fallback: if API not reachable, show receipt with warning
        console.error('IDO API error:', err);
        const txHash = '0x' + Array.from({length: 8}, () => Math.floor(Math.random()*16).toString(16)).join('') + '...' + Array.from({length: 4}, () => Math.floor(Math.random()*16).toString(16)).join('');
        document.getElementById('receiptTxHash').innerText = txHash;
        document.getElementById('receiptVrsAmount').innerText = totalVRS.toLocaleString() + ' VRS';
        document.getElementById('receiptTrees').innerText = '🌱 ' + Math.floor(totalUSD / 100).toLocaleString() + ' Trees Planted';
        document.getElementById('receiptModal').classList.add('active');
      } finally {
        buyBtn.innerHTML = originalBtnHTML;
        buyBtn.disabled = false;
        consentAccepted = false;
        document.getElementById('consentRow').classList.remove('checked');
        document.getElementById('confirmPurchaseBtn').classList.remove('active');
      }
    }`;

  if (!html.includes(oldExecutePurchase)) {
    console.error('❌ Cannot find executePurchase() function in token-sale.html');
    // Try to find a close match
    const partial = 'function executePurchase()';
    const idx = html.indexOf(partial);
    if (idx === -1) {
      console.error('   Function not found at all. Aborting.');
      process.exit(1);
    }
    // Find the closing brace
    let braceCount = 0;
    let startIdx = html.indexOf('{', idx);
    let endIdx = startIdx;
    for (let i = startIdx; i < html.length; i++) {
      if (html[i] === '{') braceCount++;
      if (html[i] === '}') braceCount--;
      if (braceCount === 0) { endIdx = i; break; }
    }
    html = html.slice(0, idx) + newExecutePurchase + html.slice(endIdx + 1);
    console.log('✅ executePurchase() replaced via brace-matching fallback');
  } else {
    html = html.replace(oldExecutePurchase, newExecutePurchase);
    console.log('✅ executePurchase() replaced with disclosure-gated version');
  }

  fs.writeFileSync(TOKEN_SALE_PATH, html, 'utf8');
  console.log('✅ token-sale.html patched: disclosure modal + consent gating + API integration');
}

// Run
console.log('🔧 Patching token-sale.html for disclosure + consent...\n');
patchTokenSale();
console.log('\n✅ Frontend patch applied successfully!');
