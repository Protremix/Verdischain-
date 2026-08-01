#!/usr/bin/env python3
"""Add ZK Proofs and Parallel Execution tabs to the dashboard"""

with open('/opt/verdis/app/dist/web/dashboard.html') as f:
    html = f.read()

# 1. Add new tab buttons after the tokenomics tab
old_tabs = '<div class="nav-tab" data-tab="tokenomics">💰 Tokenomics</div>'
new_tabs = '''<div class="nav-tab" data-tab="tokenomics">💰 Tokenomics</div>
<div class="nav-tab" data-tab="zk">🔒 ZK Proofs</div>
<div class="nav-tab" data-tab="parallel">⚡ Parallel Exec</div>'''

if old_tabs in html:
    html = html.replace(old_tabs, new_tabs, 1)
    print("1. Added tab buttons")
else:
    print("1. ERROR: tab button not found")

# 2. Add section HTML after the tokenomics section
old_section = '''    </div>
</div>

<script>
// === Governance Tab Functions ==='''

new_section = '''    </div>
</div>

<div id="section-zk" class="section">
    <div class="glass-card" style="background:rgba(10,20,15,0.85);border:1px solid rgba(0,255,136,0.15);border-radius:16px;padding:24px;margin-bottom:20px;">
        <h2 style="color:#00ff88;font-size:20px;margin-bottom:16px;">🔒 Zero-Knowledge Proofs</h2>
        <p style="color:#888;font-size:13px;margin-bottom:16px;">Prove transaction validity without revealing amounts, addresses, or balances. Supports range proofs, private transfers, and state proofs.</p>
        <div id="zkStats" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:20px;"></div>
        
        <h3 style="color:#ccc;font-size:14px;margin:20px 0 12px;">Generate Range Proof</h3>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;">
            <input id="zkRangeValue" type="number" placeholder="Value" style="background:#0a1410;border:1px solid rgba(0,255,136,0.2);color:#fff;border-radius:8px;padding:8px 12px;width:120px;">
            <input id="zkRangeMax" type="number" placeholder="Max" style="background:#0a1410;border:1px solid rgba(0,255,136,0.2);color:#fff;border-radius:8px;padding:8px 12px;width:120px;">
            <button onclick="generateRangeProof()" style="background:#00ff88;color:#000;border:none;border-radius:8px;padding:8px 16px;font-weight:600;cursor:pointer;">Generate</button>
        </div>
        <div id="zkRangeResult" style="font-size:12px;color:#888;margin-bottom:16px;"></div>
        
        <h3 style="color:#ccc;font-size:14px;margin:20px 0 12px;">Private Transfer Proof</h3>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;">
            <input id="zkTransferSender" placeholder="Sender Address" style="background:#0a1410;border:1px solid rgba(0,255,136,0.2);color:#fff;border-radius:8px;padding:8px 12px;width:200px;font-size:11px;">
            <input id="zkTransferRecipient" placeholder="Recipient" style="background:#0a1410;border:1px solid rgba(0,255,136,0.2);color:#fff;border-radius:8px;padding:8px 12px;width:200px;font-size:11px;">
            <input id="zkTransferAmount" type="number" placeholder="Amount" style="background:#0a1410;border:1px solid rgba(0,255,136,0.2);color:#fff;border-radius:8px;padding:8px 12px;width:100px;">
            <button onclick="generatePrivateTransfer()" style="background:#00ff88;color:#000;border:none;border-radius:8px;padding:8px 16px;font-weight:600;cursor:pointer;">Prove</button>
        </div>
        <div id="zkTransferResult" style="font-size:12px;color:#888;"></div>
    </div>
</div>

<div id="section-parallel" class="section">
    <div class="glass-card" style="background:rgba(10,20,15,0.85);border:1px solid rgba(0,255,136,0.15);border-radius:16px;padding:24px;margin-bottom:20px;">
        <h2 style="color:#00ff88;font-size:20px;margin-bottom:16px;">⚡ Parallel Transaction Execution</h2>
        <p style="color:#888;font-size:13px;margin-bottom:16px;">Transactions within a block are grouped by read/write set analysis and executed in parallel batches. Non-conflicting transactions run simultaneously.</p>
        <div id="parallelStats" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;"></div>
        <h3 style="color:#ccc;font-size:14px;margin:20px 0 12px;">How It Works</h3>
        <div style="color:#aaa;font-size:13px;line-height:1.8;">
            <p>1. Each transaction's read/write set is analyzed (addresses touched, pools modified, contracts called)</p>
            <p>2. Transactions with no overlapping write sets are grouped into parallel batches</p>
            <p>3. Batches execute simultaneously using greedy conflict detection</p>
            <p>4. Conflicting transactions fall back to sequential execution</p>
        </div>
    </div>
</div>

<script>
// === ZK Proofs Tab Functions ===
async function loadZKStats() {
    try {
        const stats = await fetch('/api/zk/stats').then(r => r.json());
        document.getElementById('zkStats').innerHTML = 
            statCard('Proofs Generated', stats.proofCount) +
            statCard('Verified Proofs', stats.verifiedCount) +
            statCard('Private Transfers', stats.privateTransfers) +
            statCard('Active Commitments', stats.activeCommitments) +
            statCard('Used Nullifiers', stats.usedNullifiers) +
            statCard('Enabled', stats.enabled ? '✓' : '✗');
    } catch(e) { console.error('ZK stats error:', e); }
}

async function generateRangeProof() {
    const value = document.getElementById('zkRangeValue').value;
    const max = document.getElementById('zkRangeMax').value;
    if (!value || !max) return;
    try {
        const result = await fetch('/api/zk/range-proof', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({value: parseInt(value), max: parseInt(max), blinding: 'a1b2c3d4e5f6'})
        }).then(r => r.json());
        if (result.success) {
            document.getElementById('zkRangeResult').innerHTML = 
                '<span style="color:#00ff88;">✓ Range proof generated</span><br>' +
                'Commitment: ' + result.proof.commitment.substring(0,30) + '...<br>' +
                'In Range: ' + result.proof.proof.inRange + '<br>' +
                'Value Hash: ' + result.proof.valueHash.substring(0,30) + '...';
        }
    } catch(e) { document.getElementById('zkRangeResult').innerHTML = '<span style="color:#ff4444;">Error: ' + e.message + '</span>'; }
}

async function generatePrivateTransfer() {
    const sender = document.getElementById('zkTransferSender').value;
    const recipient = document.getElementById('zkTransferRecipient').value;
    const amount = document.getElementById('zkTransferAmount').value;
    if (!sender || !recipient || !amount) return;
    try {
        const result = await fetch('/api/zk/private-transfer', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({senderAddress: sender, recipientAddress: recipient, amount: parseInt(amount), senderBalance: 999999999})
        }).then(r => r.json());
        if (result.success) {
            document.getElementById('zkTransferResult').innerHTML = 
                '<span style="color:#00ff88;">✓ Private transfer proof created</span><br>' +
                'Nullifier: ' + result.proof.nullifier.substring(0,30) + '...<br>' +
                'Amount Commitment: ' + result.proof.amountCommitment.substring(0,30) + '...<br>' +
                'Sender Commitment: ' + result.proof.senderCommitment.substring(0,30) + '...';
        }
    } catch(e) { document.getElementById('zkTransferResult').innerHTML = '<span style="color:#ff4444;">Error: ' + e.message + '</span>'; }
}

// === Parallel Exec Tab Functions ===
async function loadParallelStats() {
    try {
        const stats = await fetch('/api/parallel-exec/stats').then(r => r.json());
        document.getElementById('parallelStats').innerHTML = 
            statCard('Max Workers', stats.maxWorkers) +
            statCard('Enabled', stats.enabled ? '✓' : '✗') +
            statCard('Mode', stats.mode) +
            statCard('Conflict Resolution', stats.conflictResolution);
    } catch(e) { console.error('Parallel stats error:', e); }
}

function statCard(label, value) {
    return '<div style="background:#0a1410;border:1px solid rgba(0,255,136,0.1);border-radius:12px;padding:16px;"><div style="color:#888;font-size:11px;margin-bottom:4px;">' + label + '</div><div style="color:#00ff88;font-size:18px;font-weight:700;">' + value + '</div></div>';
}

// === Governance Tab Functions ==='''

if old_section in html:
    html = html.replace(old_section, new_section, 1)
    print("2. Added section HTML and JS functions")
else:
    print("2. ERROR: section insertion point not found")

# 3. Add ZK and Parallel to loadTabData switch
old_load = 'function loadTabData(t){'
new_load = '''function loadTabData(t){
    if(t==='zk'){loadZKStats();return;}
    if(t==='parallel'){loadParallelStats();return;}
'''

if old_load in html:
    html = html.replace(old_load, new_load, 1)
    print("3. Added tab data loaders")
else:
    print("3. ERROR: loadTabData not found")

with open('/opt/verdis/app/dist/web/dashboard.html', 'w') as f:
    f.write(html)
print("Dashboard updated!")
