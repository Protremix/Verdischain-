import re

path = '/opt/verdis/app/dist/web/dashboard.html'
with open(path) as f:
    html = f.read()

# 1. Add modal HTML before the main script
modal_html = """
<!-- BLOCK/TX DETAIL MODAL -->
<div id="detailModal" class="hidden" style="position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.85);backdrop-filter:blur(8px);display:flex;align-items:center;justify-content:center;padding:20px" onclick="if(event.target===this)closeDetailModal()">
  <div style="background:#0d1117;border:1px solid #30363d;border-radius:12px;max-width:700px;width:100%;max-height:85vh;overflow-y:auto;padding:24px;box-shadow:0 0 40px rgba(0,255,136,.1)">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h3 id="detailTitle" style="font-size:18px;color:#00ff88">Details</h3>
      <button onclick="closeDetailModal()" style="background:none;border:none;color:#8b949e;font-size:24px;cursor:pointer;padding:0 8px">&times;</button>
    </div>
    <div id="detailBody"></div>
  </div>
</div>
"""

# Insert modal before <script>\nlet wallet=null
script_marker = "<script>\nlet wallet=null"
if script_marker in html:
    html = html.replace(script_marker, modal_html + "\n" + script_marker)
    print('1. Modal HTML added')
else:
    idx = html.find('let wallet=null')
    if idx >= 0:
        insert_point = html.rfind('<script>', 0, idx)
        if insert_point >= 0:
            html = html[:insert_point] + modal_html + "\n" + html[insert_point:]
            print('1. Modal HTML added (alt)')
        else:
            print('1. ERROR: could not find script tag')
    else:
        print('1. ERROR: could not find wallet variable')

# 2. Add detail JS functions after loadTxs line
detail_js = r"""
// BLOCK & TX DETAIL MODAL FUNCTIONS
async function showBlockDetail(index){
  var modal=document.getElementById('detailModal');
  var title=document.getElementById('detailTitle');
  var body=document.getElementById('detailBody');
  if(!modal)return;
  modal.classList.remove('hidden');
  modal.style.display='flex';
  title.textContent='Block #'+index;
  body.innerHTML='<div class="text-muted">Loading...</div>';
  var b=await api('blockchain/block/'+index);
  if(!b||b.error){body.innerHTML='<span class="text-red">Error: '+(b&&b.error||'Not found')+'</span>';return}
  var h=b.header||{};
  var txs=b.transactions||[];
  var html='<div style="display:grid;gap:12px">';
  html+='<div class="card" style="padding:12px"><div class="text-muted text-sm" style="margin-bottom:4px">Block Hash</div><div class="mono text-sm" style="word-break:break-all">'+(b.hash||'\u2014')+'</div></div>';
  html+='<div class="grid-2"><div class="card" style="padding:12px"><div class="text-muted text-sm">Height</div><div class="text-green">'+(h.index!=null?h.index:'\u2014')+'</div></div>';
  html+='<div class="card" style="padding:12px"><div class="text-muted text-sm">Timestamp</div><div class="text-sm">'+(h.timestamp?new Date(h.timestamp).toLocaleString():'\u2014')+'</div></div></div>';
  html+='<div class="card" style="padding:12px"><div class="text-muted text-sm" style="margin-bottom:4px">Previous Hash</div><div class="mono text-sm" style="word-break:break-all">'+(h.previousHash||'\u2014')+'</div></div>';
  html+='<div class="card" style="padding:12px"><div class="text-muted text-sm" style="margin-bottom:4px">Merkle Root</div><div class="mono text-sm" style="word-break:break-all">'+(h.merkleRoot||'\u2014')+'</div></div>';
  html+='<div class="grid-2"><div class="card" style="padding:12px"><div class="text-muted text-sm">Validator</div><div class="mono text-sm">'+shortAddr(h.validator||'')+'</div></div>';
  html+='<div class="card" style="padding:12px"><div class="text-muted text-sm">Gas Used</div><div class="text-sm">'+(h.gasUsed||0)+'</div></div></div>';
  html+='<div class="grid-2"><div class="card" style="padding:12px"><div class="text-muted text-sm">Gas Limit</div><div class="text-sm">'+(h.gasLimit||'\u2014')+'</div></div>';
  html+='<div class="card" style="padding:12px"><div class="text-muted text-sm">Base Fee</div><div class="text-sm">'+(h.baseFee||'\u2014')+'</div></div></div>';
  if(h.validatorSignature)html+='<div class="card" style="padding:12px"><div class="text-muted text-sm" style="margin-bottom:4px">Validator Signature</div><div class="mono text-sm" style="word-break:break-all">'+h.validatorSignature+'</div></div>';
  html+='<div class="card" style="padding:12px"><div class="text-muted text-sm" style="margin-bottom:8px">Transactions ('+txs.length+')</div>';
  if(txs.length===0)html+='<div class="text-muted text-sm">No transactions in this block</div>';
  else{html+='<div style="display:grid;gap:6px">';txs.forEach(function(tx,i){var th=tx.hash||tx.id||'';html+='<div style="padding:8px;border:1px solid #30363d;border-radius:6px;cursor:pointer" onclick="showTxDetail(\''+th+'\')"><div class="flex justify-between"><span class="mono text-sm">'+shortAddr(th,12)+'</span><span class="text-green">'+(tx.amount||0)+' VCO</span></div><div class="text-muted text-sm" style="margin-top:4px">From: '+shortAddr(tx.from||'')+' \u2192 To: '+shortAddr(tx.to||'')+'</div></div>'});html+='</div>'}
  html+='</div></div>';
  body.innerHTML=html;
}
async function showTxDetail(hash){
  var modal=document.getElementById('detailModal');
  var title=document.getElementById('detailTitle');
  var body=document.getElementById('detailBody');
  if(!modal)return;
  modal.classList.remove('hidden');
  modal.style.display='flex';
  title.textContent='Transaction Details';
  body.innerHTML='<div class="text-muted">Loading...</div>';
  var r=await api('explorer/tx/'+hash);
  if(!r||r.error){body.innerHTML='<span class="text-red">Error: '+(r&&r.error||'Not found')+'</span>';return}
  var tx=r.tx||r.transaction||r;
  var block=r.block||{};
  var bh=block.header||{};
  var html='<div style="display:grid;gap:12px">';
  html+='<div class="card" style="padding:12px"><div class="text-muted text-sm" style="margin-bottom:4px">Transaction Hash</div><div class="mono text-sm" style="word-break:break-all">'+(tx.id||hash)+'</div></div>';
  html+='<div class="grid-2"><div class="card" style="padding:12px"><div class="text-muted text-sm">From</div><div class="mono text-sm" style="word-break:break-all">'+(tx.from||'\u2014')+'</div></div>';
  html+='<div class="card" style="padding:12px"><div class="text-muted text-sm">To</div><div class="mono text-sm" style="word-break:break-all">'+(tx.to||'\u2014')+'</div></div></div>';
  html+='<div class="grid-2"><div class="card" style="padding:12px"><div class="text-muted text-sm">Amount</div><div class="text-green">'+(tx.amount||0)+' VCO</div></div>';
  html+='<div class="card" style="padding:12px"><div class="text-muted text-sm">Fee</div><div class="text-sm">'+(tx.fee||0)+' VCO</div></div></div>';
  html+='<div class="grid-2"><div class="card" style="padding:12px"><div class="text-muted text-sm">Nonce</div><div class="text-sm">'+(tx.nonce!=null?tx.nonce:'\u2014')+'</div></div>';
  if(bh.index!=null){html+='<div class="card" style="padding:12px"><div class="text-muted text-sm">Block</div><div class="text-sm" style="cursor:pointer;text-decoration:underline;color:#00ff88" onclick="showBlockDetail('+bh.index+')">#'+bh.index+'</div></div></div>'}else{html+='<div class="card" style="padding:12px"><div class="text-muted text-sm">Block</div><div class="text-sm">\u2014</div></div></div>'}
  html+='<div class="card" style="padding:12px"><div class="text-muted text-sm">Timestamp</div><div class="text-sm">'+(tx.timestamp?new Date(tx.timestamp).toLocaleString():'\u2014')+'</div></div>';
  if(tx.publicKey)html+='<div class="card" style="padding:12px"><div class="text-muted text-sm" style="margin-bottom:4px">Public Key</div><div class="mono text-sm" style="word-break:break-all">'+tx.publicKey+'</div></div>';
  if(tx.signature)html+='<div class="card" style="padding:12px"><div class="text-muted text-sm" style="margin-bottom:4px">Signature</div><div class="mono text-sm" style="word-break:break-all">'+tx.signature+'</div></div>';
  if(tx.recovery!=null)html+='<div class="card" style="padding:12px"><div class="text-muted text-sm">Recovery Bit</div><div class="text-sm">'+tx.recovery+'</div></div>';
  if(tx.data&&tx.data!=='0x'&&tx.data!=='')html+='<div class="card" style="padding:12px"><div class="text-muted text-sm" style="margin-bottom:4px">Data</div><div class="mono text-sm" style="word-break:break-all">'+tx.data+'</div></div>';
  html+='</div>';
  body.innerHTML=html;
}
function closeDetailModal(){
  var modal=document.getElementById('detailModal');
  if(modal){modal.classList.add('hidden');modal.style.display='none'}
}
"""

# Find loadTxs and insert after it
txs_start = html.find('async function loadTxs()')
if txs_start < 0:
    print('2. ERROR: loadTxs not found')
else:
    # Find the end of the loadTxs function - look for the next blank line or next comment
    search_area = html[txs_start:txs_start+500]
    join_end = search_area.find(".join('')}")
    if join_end >= 0:
        actual_end = txs_start + join_end + len(".join('')}")
        # Find the newline after the closing }
        newline_pos = html.find('\n', actual_end) + 1
        html = html[:newline_pos] + detail_js + '\n' + html[newline_pos:]
        print('2. Detail JS functions added after loadTxs')
    else:
        print('2. ERROR: could not find end of loadTxs')

# 3. Update loadBlocks to add onclick handlers
old_blocks = "async function loadBlocks(){const b=await api('blockchain/blocks?limit=50');if(!b||!Array.isArray(b))return;document.getElementById('blocksTable').innerHTML=b.map(x=>'<tr>"
if old_blocks in html:
    new_blocks = old_blocks.replace(
        "b.map(x=>'<tr>",
        "b.map(x=>'<tr style=\"cursor:pointer\" onclick=\"showBlockDetail('+x.header.index+')\">"
    ).replace(
        "<td class=\"mono\">'+x.header.index+'</td>",
        "<td class=\"mono\" style=\"color:#00ff88\">'+x.header.index+'</td>"
    )
    html = html.replace(old_blocks, new_blocks)
    print('3. loadBlocks updated with click handlers')
else:
    print('3. WARNING: loadBlocks pattern not found')

# 4. Update loadTxs to add onclick handlers
old_txs = "async function loadTxs(){const t=await api('blockchain/transactions?limit=50');if(!t||!Array.isArray(t))return;document.getElementById('txsTable').innerHTML=t.map(x=>'<tr>"
if old_txs in html:
    new_txs = old_txs.replace(
        "t.map(x=>'<tr>",
        "t.map(x=>{var h=x.hash||x.id||'';return '<tr style=\"cursor:pointer\" onclick=\"showTxDetail(\\''+h+'\\')\">"
    ).replace(
        "<td class=\"mono\">'+shortAddr(x.hash||x.id||'',10)",
        "<td class=\"mono\" style=\"color:#00ff88\">'+shortAddr(h,10)"
    )
    # Need to also close the function with .join('')}
    # Actually this is getting complex with the map returning. Let me do a full replacement.
    print('4. loadTxs - doing full replacement...')
    
    # Find the full loadTxs function
    txs_start2 = html.find('async function loadTxs()')
    search_area2 = html[txs_start2:txs_start2+600]
    join_end2 = search_area2.find(".join('')}")
    actual_end2 = txs_start2 + join_end2 + len(".join('')}")
    
    new_load_txs = "async function loadTxs(){const t=await api('blockchain/transactions?limit=50');if(!t||!Array.isArray(t))return;document.getElementById('txsTable').innerHTML=t.map(x=>{var h=x.hash||x.id||'';return '<tr style=\"cursor:pointer\" onclick=\"showTxDetail(\\''+h+'\\')\"><td class=\"mono\" style=\"color:#00ff88\">'+shortAddr(h,10)+'</td><td class=\"mono\">'+shortAddr(x.from||'')+'</td><td class=\"mono\">'+shortAddr(x.to||'')+'</td><td class=\"text-green\">'+(x.amount||0)+'</td><td>'+(x.blockIndex||'\u2014')+'</td></tr>'}).join('')}"
    
    html = html[:txs_start2] + new_load_txs + html[actual_end2:]
    print('4. loadTxs updated with click handlers')
else:
    print('4. WARNING: loadTxs pattern not found')

# 5. Update loadOverview recent blocks to be clickable
old_recent = "document.getElementById('ovRecentBlocks').innerHTML=b.slice(0,5).map(x=>'<div class=\"flex justify-between\" style=\"padding:6px 0;border-bottom:1px solid var(--border-light)\"><span class=\"mono text-sm\">#'"
if old_recent in html:
    new_recent = "document.getElementById('ovRecentBlocks').innerHTML=b.slice(0,5).map(x=>'<div class=\"flex justify-between\" style=\"padding:6px 0;border-bottom:1px solid var(--border-light);cursor:pointer\" onclick=\"showBlockDetail('+x.header.index+')\"><span class=\"mono text-sm\" style=\"color:#00ff88\">#'"
    html = html.replace(old_recent, new_recent)
    print('5. Recent blocks in overview made clickable')
else:
    print('5. WARNING: recent blocks pattern not found')

with open(path, 'w') as f:
    f.write(html)
print('\nAll block/tx detail features added!')
