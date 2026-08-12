#!/usr/bin/env python3
"""Add click-to-detail modal for wallet transaction history."""

with open('/var/www/verdiscan/wallet/index.html', 'r') as f:
    content = f.read()

# 1. Add modal CSS right after the tx-item CSS block
modal_css = """
.tx-modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.4);z-index:9999;display:none;align-items:center;justify-content:center;backdrop-filter:blur(4px)}
.tx-modal-overlay.active{display:flex}
.tx-modal{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:24px;max-width:440px;width:90%;max-height:80vh;overflow-y:auto;box-shadow:0 8px 32px rgba(0,0,0,0.15)}
.tx-modal h3{font-size:16px;font-weight:700;color:#0f172a;margin-bottom:16px;display:flex;align-items:center;gap:8px}
.tx-modal-row{display:flex;justify-content:space-between;align-items:flex-start;padding:10px 0;border-bottom:1px solid #f1f5f9}
.tx-modal-row:last-child{border-bottom:none}
.tx-modal-label{font-size:12px;color:#64748b;font-weight:500;white-space:nowrap}
.tx-modal-value{font-family:'JetBrains Mono',monospace;font-size:12px;color:#0f172a;text-align:right;word-break:break-all;max-width:260px}
.tx-modal-close{position:absolute;top:12px;right:16px;cursor:pointer;font-size:20px;color:#94a3b8;background:none;border:none}
.tx-modal-close:hover{color:#0f172a}
.tx-modal-link{color:#16a34a;text-decoration:none;font-size:12px;font-weight:600}
.tx-modal-link:hover{text-decoration:underline}
"""

content = content.replace(
    '.tx-item {\n  opacity: 0;',
    modal_css + '\n.tx-item {\n  opacity: 0;'
)

# 2. Add modal HTML before closing body tag
modal_html = """<!-- TX Detail Modal -->
<div class="tx-modal-overlay" id="txModalOverlay" onclick="if(event.target===this)closeTxModal()">
<div class="tx-modal" style="position:relative">
<button class="tx-modal-close" onclick="closeTxModal()">&times;</button>
<h3 id="txModalTitle">Transaction</h3>
<div id="txModalBody"></div>
</div>
</div>
"""

content = content.replace('</body>', modal_html + '\n</body>')

# 3. Add click handlers to tx items
old_render = """    container.replaceChildren();
    txs.forEach(tx => {
      const div = document.createElement('div');
      div.className = 'tx-item';
      const iconEl = document.createElement('span');
      iconEl.className = 'tx-icon';
      if (tx.type === 'received') {
        iconEl.textContent = '\u2193';
        iconEl.style.color = '#16a34a';
      } else if (tx.type === 'sent') {
        iconEl.textContent = '\u2191';
        iconEl.style.color = '#ef4444';
      } else {
        iconEl.textContent = '\u25C6';
        iconEl.style.color = '#64748b';
      }
      const fromEl = document.createElement('span');
      fromEl.className = 'tx-from';
      if (tx.type === 'received') {
        fromEl.textContent = 'From: ' + (tx.signer || '?').slice(0, 12) + '...';
      } else if (tx.type === 'sent') {
        fromEl.textContent = 'To: ' + (tx.dest || '?').slice(0, 12) + '...';
      } else {
        fromEl.textContent = 'Remark: ' + (tx.value || '').slice(0, 30);
      }
      const blockEl = document.createElement('span');
      blockEl.className = 'tx-block';
      blockEl.textContent = '#' + tx.block;
      const amtEl = document.createElement('span');
      amtEl.className = 'tx-amount';
      if (tx.type === 'received') {
        amtEl.textContent = '+ ' + (tx.value || '');
        amtEl.style.color = '#16a34a';
      } else if (tx.type === 'sent') {
        amtEl.textContent = '- ' + (tx.value || '');
        amtEl.style.color = '#ef4444';
      } else {
        amtEl.textContent = '';
      }
      div.appendChild(iconEl);
      div.appendChild(fromEl);
      div.appendChild(blockEl);
      div.appendChild(amtEl);
      container.appendChild(div);
    });"""

new_render = """    container.replaceChildren();
    txs.forEach((tx, idx) => {
      const div = document.createElement('div');
      div.className = 'tx-item';
      div.style.cursor = 'pointer';
      div.onclick = () => showTxDetail(tx);

      const iconEl = document.createElement('span');
      iconEl.className = 'tx-icon';
      if (tx.type === 'received') {
        iconEl.textContent = '\u2193';
        iconEl.style.color = '#16a34a';
      } else if (tx.type === 'sent') {
        iconEl.textContent = '\u2191';
        iconEl.style.color = '#ef4444';
      } else {
        iconEl.textContent = '\u25C6';
        iconEl.style.color = '#64748b';
      }
      const fromEl = document.createElement('span');
      fromEl.className = 'tx-from';
      if (tx.type === 'received') {
        fromEl.textContent = 'From: ' + (tx.signer || '?').slice(0, 12) + '...';
      } else if (tx.type === 'sent') {
        fromEl.textContent = 'To: ' + (tx.dest || '?').slice(0, 12) + '...';
      } else {
        fromEl.textContent = 'Remark: ' + (tx.value || '').slice(0, 30);
      }
      const blockEl = document.createElement('span');
      blockEl.className = 'tx-block';
      blockEl.textContent = '#' + tx.block;
      const amtEl = document.createElement('span');
      amtEl.className = 'tx-amount';
      if (tx.type === 'received') {
        amtEl.textContent = '+ ' + (tx.value || '');
        amtEl.style.color = '#16a34a';
      } else if (tx.type === 'sent') {
        amtEl.textContent = '- ' + (tx.value || '');
        amtEl.style.color = '#ef4444';
      } else {
        amtEl.textContent = '';
      }
      div.appendChild(iconEl);
      div.appendChild(fromEl);
      div.appendChild(blockEl);
      div.appendChild(amtEl);
      container.appendChild(div);
    });"""

content = content.replace(old_render, new_render, 1)

# 4. Add showTxDetail and closeTxModal functions before loadValidators
modal_js = """
function showTxDetail(tx) {
  const overlay = document.getElementById('txModalOverlay');
  const title = document.getElementById('txModalTitle');
  const body = document.getElementById('txModalBody');
  if (!overlay || !title || !body) return;

  const isReceived = tx.type === 'received';
  const icon = isReceived ? '\u2193 Received' : (tx.type === 'sent' ? '\u2191 Sent' : '\u25C6 Remark');
  title.innerHTML = icon;

  const rows = [];
  rows.push(['Type', tx.method || 'Transfer']);
  rows.push(['Block', '#' + tx.block]);
  if (tx.hash) rows.push(['Hash', tx.hash]);
  if (tx.signer) rows.push(['From', tx.signer]);
  if (tx.dest) rows.push(['To', tx.dest]);
  if (tx.value && tx.type !== 'remark') rows.push(['Amount', (tx.type === 'received' ? '+ ' : '- ') + tx.value]);

  let html = '';
  for (const [label, val] of rows) {
    html += '<div class="tx-modal-row"><span class="tx-modal-label">' + label + '</span><span class="tx-modal-value">' + val + '</span></div>';
  }
  html += '<div class="tx-modal-row"><span class="tx-modal-label">Explorer</span><a class="tx-modal-link" href="/transactions/#' + tx.block + '" target="_blank">View on Verdiscan \u2192</a></div>';
  body.innerHTML = html;

  overlay.classList.add('active');
}

function closeTxModal() {
  const overlay = document.getElementById('txModalOverlay');
  if (overlay) overlay.classList.remove('active');
}

"""

content = content.replace(
    'async function loadValidators() {',
    modal_js + 'async function loadValidators() {'
)

with open('/var/www/verdiscan/wallet/index.html', 'w') as f:
    f.write(content)
print('MODAL ADDED: Click-to-detail + tx modal')
