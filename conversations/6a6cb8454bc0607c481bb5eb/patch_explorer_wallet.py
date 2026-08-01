# Patch 1: Upgrade explorer showTx/showBlock + add URL param handling
# Patch 2: Enhance dashboard wallet transaction history

import re

# ===== EXPLORER UPGRADE =====
explorer_path = '/opt/verdis/app/dist/web/explorer.html'
with open(explorer_path) as f:
    explorer = f.read()

# Replace showBlock with comprehensive version
old_show_block = '''function showBlock(b){
document.getElementById('modalTitle').textContent='Block #'+b.height;
var c=document.getElementById('modalContent');
c.innerHTML=Object.entries(b).map(function(e){return '<div class="modal-row"><span>'+e[0]+'</span><span>'+e[1]+'</span></div>'}).join('');
document.getElementById('modalOverlay').classList.add('show');
}'''

new_show_block = '''function showBlock(b){
document.getElementById('modalTitle').textContent='Block #'+b.height;
var c=document.getElementById('modalContent');
var bh=b.header||b;
var txs=b.transactions||[];
var html='<div style="display:grid;gap:12px">';
// Block hash
html+='<div style="padding:12px;border:1px solid var(--border);border-radius:10px;background:rgba(0,255,136,0.03)"><div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Block Hash</div><div style="font-family:JetBrains Mono,monospace;font-size:12px;word-break:break-all;color:var(--green)">'+(b.hash||bh.hash||'—')+'</div></div>';
// Grid: Height, Timestamp, Validator
html+='<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">';
html+='<div style="padding:12px;border:1px solid var(--border);border-radius:10px"><div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Height</div><div style="font-family:JetBrains Mono,monospace;font-size:14px;color:var(--green)">#'+(bh.index||b.height||0)+'</div></div>';
html+='<div style="padding:12px;border:1px solid var(--border);border-radius:10px"><div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Timestamp</div><div style="font-size:12px">'+(bh.timestamp?new Date(bh.timestamp).toLocaleString():'—')+'</div></div>';
html+='<div style="padding:12px;border:1px solid var(--border);border-radius:10px"><div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Tx Count</div><div style="font-family:JetBrains Mono,monospace;font-size:14px">'+txs.length+'</div></div>';
html+='</div>';
// Grid: Validator, Previous Hash, Merkle Root
html+='<div style="padding:12px;border:1px solid var(--border);border-radius:10px"><div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Validator</div><div style="font-family:JetBrains Mono,monospace;font-size:12px;color:var(--teal);word-break:break-all">'+(bh.validator||'—')+'</div></div>';
html+='<div style="padding:12px;border:1px solid var(--border);border-radius:10px"><div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Previous Hash</div><div style="font-family:JetBrains Mono,monospace;font-size:11px;word-break:break-all;color:var(--muted)">'+(bh.previousHash||'—')+'</div></div>';
if(bh.merkleRoot)html+='<div style="padding:12px;border:1px solid var(--border);border-radius:10px"><div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Merkle Root</div><div style="font-family:JetBrains Mono,monospace;font-size:11px;word-break:break-all;color:var(--muted)">'+bh.merkleRoot+'</div></div>';
// Transactions in block
if(txs.length){
html+='<div style="padding:12px;border:1px solid var(--border);border-radius:10px"><div style="font-size:12px;color:var(--green);font-weight:600;margin-bottom:10px">Transactions ('+txs.length+')</div>';
txs.forEach(function(tx,i){
var th=tx.id||tx.hash||'';
html+='<div style="padding:8px;margin-bottom:6px;border:1px solid rgba(0,255,136,0.08);border-radius:8px;cursor:pointer" onclick="closeModal();setTimeout(function(){showTxByHash(\\''+th+'\\')},300)"><div style="display:flex;justify-content:space-between;align-items:center"><span style="font-family:JetBrains Mono,monospace;font-size:11px;color:var(--green)">'+shortHash(th)+'</span><span style="font-family:JetBrains Mono,monospace;font-size:12px;color:var(--green)">'+(tx.amount||0)+' VCO</span></div><div style="font-family:JetBrains Mono,monospace;font-size:10px;color:var(--muted);margin-top:4px">'+shortAddr(tx.from||'')+' → '+shortAddr(tx.to||'')+'</div></div>';
});
html+='</div>';
}
html+='</div>';
c.innerHTML=html;
document.getElementById('modalOverlay').classList.add('show');
}'''

if old_show_block in explorer:
    explorer = explorer.replace(old_show_block, new_show_block)
    print("1. Explorer: showBlock upgraded")
else:
    print("1. ERROR: showBlock pattern not found")

# Replace showTx with comprehensive version
old_show_tx = '''function showTx(tx){
document.getElementById('modalTitle').textContent='Transaction';
var c=document.getElementById('modalContent');
c.innerHTML=Object.entries(tx).map(function(e){return '<div class="modal-row"><span>'+e[0]+'</span><span>'+e[1]+'</span></div>'}).join('');
document.getElementById('modalOverlay').classList.add('show');
}'''

new_show_tx = '''async function showTx(tx){
document.getElementById('modalTitle').textContent='Transaction Details';
var c=document.getElementById('modalContent');
var th=tx.id||tx.hash||'';
// If only partial data, fetch full details
if(!tx.from||!tx.signature){
try{var full=await fetch(API+'/api/explorer/tx/'+th).then(r=>r.json());if(full&&!full.error){tx=Object.assign(tx,full.tx||full.transaction||full);var blk=full.block||{};tx._block=blk.header?blk.header.index:(blk.height||blk.blockHeight);tx._blockHash=blk.hash||'';tx._timestamp=blk.header?blk.header.timestamp:(tx.timestamp||null);}}catch(e){}
}
var bh=tx._block!=null?tx._block:(tx.blockIndex||tx.block||tx.blockHeight||'—');
var ts=tx._timestamp||tx.timestamp||null;
var status=tx.status||(th?'success':'pending');
var html='<div style="display:grid;gap:12px">';
// Status badge
html+='<div style="display:flex;align-items:center;gap:8px"><span class="badge '+(status==='failed'?'badge-failed':status==='pending'?'badge-pending':'badge-success')+'" style="font-size:12px;padding:4px 12px">'+(status==='success'?'✓ Success':status==='failed'?'✕ Failed':'⏳ Pending')+'</span><span style="font-size:11px;color:var(--muted)">Block #'+bh+'</span></div>';
// Transaction hash with copy button
html+='<div style="padding:12px;border:1px solid var(--border);border-radius:10px;background:rgba(0,255,136,0.03)"><div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Transaction Hash</div><div style="display:flex;align-items:center;gap:8px"><span style="font-family:JetBrains Mono,monospace;font-size:12px;word-break:break-all;color:var(--green);flex:1">'+th+'</span><button onclick="copyText(\\''+th+'\\')" style="padding:4px 10px;border:1px solid var(--border);border-radius:6px;background:transparent;color:var(--green);cursor:pointer;font-size:11px">Copy</button></div></div>';
// From / To grid
html+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">';
html+='<div style="padding:12px;border:1px solid var(--border);border-radius:10px"><div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">From</div><div style="font-family:JetBrains Mono,monospace;font-size:12px;word-break:break-all;color:var(--teal)">'+(tx.from||'—')+'</div></div>';
html+='<div style="padding:12px;border:1px solid var(--border);border-radius:10px"><div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">To</div><div style="font-family:JetBrains Mono,monospace;font-size:12px;word-break:break-all;color:var(--teal)">'+(tx.to||'—')+'</div></div>';
html+='</div>';
// Amount / Fee grid
html+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">';
html+='<div style="padding:12px;border:1px solid var(--border);border-radius:10px"><div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Amount</div><div style="font-family:JetBrains Mono,monospace;font-size:16px;font-weight:700;color:var(--green)">'+(tx.amount||0)+' VCO</div></div>';
html+='<div style="padding:12px;border:1px solid var(--border);border-radius:10px"><div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Fee</div><div style="font-family:JetBrains Mono,monospace;font-size:14px">'+(tx.fee||0)+' VCO</div></div>';
html+='</div>';
// Nonce / Timestamp grid
html+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">';
html+='<div style="padding:12px;border:1px solid var(--border);border-radius:10px"><div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Nonce</div><div style="font-family:JetBrains Mono,monospace;font-size:13px">'+(tx.nonce!=null?tx.nonce:'—')+'</div></div>';
html+='<div style="padding:12px;border:1px solid var(--border);border-radius:10px"><div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Timestamp</div><div style="font-size:12px">'+(ts?new Date(ts).toLocaleString():'—')+'</div></div>';
html+='</div>';
// Block info with link
if(bh!='—')html+='<div style="padding:12px;border:1px solid var(--border);border-radius:10px"><div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Block</div><div style="font-family:JetBrains Mono,monospace;font-size:13px;cursor:pointer;text-decoration:underline;color:var(--green)" onclick="closeModal();setTimeout(function(){fetchBlockByHeight('+bh+')},300)">#'+bh+'</div></div>';
// Public key
if(tx.publicKey)html+='<div style="padding:12px;border:1px solid var(--border);border-radius:10px"><div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Public Key (secp256k1)</div><div style="font-family:JetBrains Mono,monospace;font-size:11px;word-break:break-all;color:var(--muted)">'+tx.publicKey+'</div></div>';
// Signature
if(tx.signature&&tx.signature!=='unsigned')html+='<div style="padding:12px;border:1px solid var(--border);border-radius:10px"><div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Signature</div><div style="font-family:JetBrains Mono,monospace;font-size:11px;word-break:break-all;color:var(--muted)">'+tx.signature+'</div></div>';
// Recovery bit
if(tx.recovery!=null)html+='<div style="padding:12px;border:1px solid var(--border);border-radius:10px"><div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Recovery Bit</div><div style="font-family:JetBrains Mono,monospace;font-size:13px">'+tx.recovery+'</div></div>';
// Data payload
if(tx.data&&tx.data!=='0x'&&tx.data!==''&&tx.data!==null)html+='<div style="padding:12px;border:1px solid var(--border);border-radius:10px"><div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Data Payload</div><div style="font-family:JetBrains Mono,monospace;font-size:11px;word-break:break-all;color:var(--yellow)">'+tx.data+'</div></div>';
// Block hash
if(tx._blockHash)html+='<div style="padding:12px;border:1px solid var(--border);border-radius:10px"><div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Block Hash</div><div style="font-family:JetBrains Mono,monospace;font-size:11px;word-break:break-all;color:var(--muted)">'+tx._blockHash+'</div></div>';
html+='</div>';
c.innerHTML=html;
document.getElementById('modalOverlay').classList.add('show');
}
async function showTxByHash(hash){
document.getElementById('modalTitle').textContent='Transaction Details';
document.getElementById('modalContent').innerHTML='<div style="color:var(--muted);text-align:center;padding:24px">Loading transaction...</div>';
document.getElementById('modalOverlay').classList.add('show');
try{var r=await fetch(API+'/api/explorer/tx/'+hash).then(r=>r.json());if(r&&!r.error){showTx(r.tx||r.transaction||r);return}document.getElementById('modalContent').innerHTML='<div style="color:var(--red);text-align:center;padding:24px">Transaction not found</div>'}catch(e){document.getElementById('modalContent').innerHTML='<div style="color:var(--red);text-align:center;padding:24px">Error loading transaction</div>'}
}
async function fetchBlockByHeight(height){
try{var r=await fetch(API+'/api/explorer/block/'+height).then(r=>r.json());if(r&&!r.error){showBlock(r.block||r);return}document.getElementById('modalContent').innerHTML='<div style="color:var(--red);text-align:center;padding:24px">Block not found</div>'}catch(e){}
}
function copyText(text){var ta=document.createElement('textarea');ta.value=text;document.body.appendChild(ta);ta.select();document.execCommand('copy');document.body.removeChild(ta)}'''

if old_show_tx in explorer:
    explorer = explorer.replace(old_show_tx, new_show_tx)
    print("2. Explorer: showTx upgraded with full details")
else:
    print("2. ERROR: showTx pattern not found")

# Add URL param handling at the end of the script
old_end = '''fetchStats();fetchBlocks();fetchTransactions();fetchValidators();fetchTokens();fetchSwaps();'''

new_end = '''fetchStats();fetchBlocks();fetchTransactions();fetchValidators();fetchTokens();fetchSwaps();
// URL param handling for shared links
var urlParams=new URLSearchParams(window.location.search);
if(urlParams.get('tx')){setTimeout(function(){showTxByHash(urlParams.get('tx'))},800)}
if(urlParams.get('block')){setTimeout(function(){fetchBlockByHeight(parseInt(urlParams.get('block')))},800)}'''

if old_end in explorer:
    explorer = explorer.replace(old_end, new_end)
    print("3. Explorer: URL param handling added")
else:
    print("3. ERROR: end script pattern not found")

with open(explorer_path, 'w') as f:
    f.write(explorer)

print("\n===== Explorer patched successfully =====\n")

# ===== DASHBOARD WALLET HISTORY UPGRADE =====
dash_path = '/opt/verdis/app/dist/web/dashboard.html'
with open(dash_path) as f:
    dashboard = f.read()

# Find and replace the wallet transaction history rendering
old_wallet_history = """let xh='<div class="text-muted text-sm">No transactions yet</div>';if(t&&Array.isArray(t)&&t.length){xh='<table class="data-table"><thead><tr><th>Hash</th><th>From</th><th>To</th><th>Amount</th></tr></thead><tbody>';t.slice(-20).reverse().forEach(x=>{var xh2=x.hash||x.id||'';xh+='<tr style="cursor:pointer" onclick="showTxDetail(\\''+xh2+'\\')"><td class="mono" style="color:#00ff88">'+shortAddr(xh2)+'</td><td class="mono">'+shortAddr(x.from||'')+'</td><td class="mono">'+shortAddr(x.to||'')+'</td><td class="text-green">'+(x.amount||0)+'</td></tr>'});xh+='</tbody></table>'}document.getElementById('walletTxHistory').innerHTML=xh"""

new_wallet_history = """let xh='<div class="text-muted text-sm">No transactions yet</div>';if(t&&Array.isArray(t)&&t.length){xh='<table class="data-table"><thead><tr><th>Hash</th><th>Dir</th><th>From</th><th>To</th><th>Amount</th><th>Fee</th><th>Block</th><th>Age</th><th>Status</th></tr></thead><tbody>';t.slice(-20).reverse().forEach(x=>{var xh2=x.hash||x.id||'';var dir=x.direction||(x.from===wallet.address?'sent':'received');var isSent=dir==='sent';var status=x.pending?'pending':(x.status||'success');var blk=x.blockIndex||x.block||'—';var age=x.timestamp?timeAgoShort(x.timestamp):'—';xh+='<tr style="cursor:pointer" onclick="showTxDetail(\\''+xh2+'\\')"><td class="mono" style="color:#00ff88">'+shortAddr(xh2,12)+'</td><td style="font-size:14px">'+(isSent?'⬆':'⬇')+'</td><td class="mono">'+shortAddr(x.from||'')+'</td><td class="mono">'+shortAddr(x.to||'')+'</td><td class="'+(isSent?'text-red':'text-green')+'">'+(isSent?'-':'+')+(x.amount||0)+' VCO</td><td class="text-muted">'+(x.fee||0)+'</td><td>'+(blk!=='—'?'<a style="color:#00ff88;cursor:pointer" onclick="event.stopPropagation();showBlockDetail('+blk+')">#'+blk+'</a>':'—')+'</td><td class="text-muted">'+age+'</td><td><span class="badge '+(status==='failed'?'badge-failed':status==='pending'?'badge-pending':'badge-success')+'">'+status+'</span></td></tr>'});xh+='</tbody></table>'}document.getElementById('walletTxHistory').innerHTML=xh"""

if old_wallet_history in dashboard:
    dashboard = dashboard.replace(old_wallet_history, new_wallet_history)
    print("4. Dashboard: wallet transaction history upgraded")
else:
    print("4. ERROR: wallet history pattern not found")

# Add timeAgoShort helper if not present
if 'function timeAgoShort' not in dashboard:
    helper = "function timeAgoShort(ts){if(!ts)return '—';var d=Date.now()-new Date(ts).getTime();var s=Math.floor(d/1000);if(s<60)return s+'s ago';var m=Math.floor(s/60);if(m<60)return m+'m ago';var h=Math.floor(m/60);if(h<24)return h+'h ago';return Math.floor(h/24)+'d ago'}"
    # Add after shortAddr definition
    dashboard = dashboard.replace(
        'function shortAddr',
        helper + '\nfunction shortAddr'
    )
    print("5. Dashboard: timeAgoShort helper added")

with open(dash_path, 'w') as f:
    f.write(dashboard)

print("\n===== Dashboard patched successfully =====\n")
print("All patches applied!")
