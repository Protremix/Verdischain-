import re

path = '/opt/verdis/app/dist/web/dashboard.html'
with open(path) as f:
    html = f.read()

changes = 0

# 1. Update nativeSendTx to show explorer link + copy + view buttons
old_send = "if(r&&r.txId){e.innerHTML='<span class=\"text-green\">Sent! Tx: '+shortAddr(r.txId)+'</span>';toast('Transaction sent!');loadWalletData()}else e.innerHTML='<span class=\"text-red\">Error: '+(r?.error||'failed')+'</span>'"

new_send = """if(r&&r.txId){var txUrl=location.origin+'/dashboard?tx='+r.txId;e.innerHTML='<div style="margin-top:8px;padding:12px;border:1px solid #30363d;border-radius:8px;background:#0d1117"><div class="text-green" style="font-size:14px;margin-bottom:8px">✓ Transaction sent!</div><div class="text-muted text-sm" style="margin-bottom:4px">Tx Hash:</div><div class="mono text-sm" style="word-break:break-all;margin-bottom:10px">'+r.txId+'</div><div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn btn-sm btn-primary" onclick="showTxDetail(\\''+r.txId+'\\')">View in Explorer</button><button class="btn btn-sm" onclick="copyTxLink(\\''+r.txId+'\\')">Copy Link</button><button class="btn btn-sm" onclick="shareTx(\\''+r.txId+'\\')">Share</button></div></div>';toast('Transaction sent!');loadWalletData()}else e.innerHTML='<span class="text-red">Error: '+(r&&r.error||'failed')+'</span>'"""

if old_send in html:
    html = html.replace(old_send, new_send)
    changes += 1
    print('1. nativeSendTx updated with explorer link')
else:
    print('1. WARNING: nativeSendTx pattern not found')

# 2. Update claimFaucetManual to show tx link
old_faucet = "if(r.success){e.innerHTML='<span class=\"text-green\">1000 VCO sent to '+shortAddr(a)+'</span>';toast('Claimed!')}else e.innerHTML='<span class=\"text-red\">'+(r.error||'Error')+'</span>'"

new_faucet = """if(r.success){var txId=r.txId||r.txHash||'';var html='<div style="margin-top:8px;padding:12px;border:1px solid #30363d;border-radius:8px;background:#0d1117"><div class="text-green" style="margin-bottom:8px">✓ 1000 VCO sent to '+shortAddr(a)+'</div>';if(txId){html+='<div class="text-muted text-sm" style="margin-bottom:4px">Tx Hash:</div><div class="mono text-sm" style="word-break:break-all;margin-bottom:10px">'+txId+'</div><div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn btn-sm btn-primary" onclick="showTxDetail(\\''+txId+'\\')">View in Explorer</button><button class="btn btn-sm" onclick="copyTxLink(\\''+txId+'\\')">Copy Link</button></div>'}html+='</div>';e.innerHTML=html;toast('Claimed!')}else e.innerHTML='<span class="text-red">'+(r.error||'Error')+'</span>'"""

if old_faucet in html:
    html = html.replace(old_faucet, new_faucet)
    changes += 1
    print('2. claimFaucetManual updated with explorer link')
else:
    print('2. WARNING: claimFaucet pattern not found')

# 3. Update token sale purchase to show tx link
old_purchase = "e.innerHTML='<span class=\"text-green\">✓ Purchased '+d.amountVCO.toLocaleString()+' VCO for $'+d.totalCostUSD+'!<br>New balance: '+d.newBalance.toLocaleString()+' VCO<br>Tx: '+shortAddr(d.txId||'')+'</span>'"

new_purchase = """var txId=d.txId||'';var html='<div style="padding:12px;border:1px solid #30363d;border-radius:8px;background:#0d1117"><div class="text-green" style="margin-bottom:8px">✓ Purchased '+d.amountVCO.toLocaleString()+' VCO for $'+d.totalCostUSD+'!</div><div class="text-sm" style="margin-bottom:8px">New balance: '+d.newBalance.toLocaleString()+' VCO</div>';if(txId){html+='<div class="text-muted text-sm" style="margin-bottom:4px">Tx Hash:</div><div class="mono text-sm" style="word-break:break-all;margin-bottom:10px">'+txId+'</div><div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn btn-sm btn-primary" onclick="showTxDetail(\\''+txId+'\\')">View in Explorer</button><button class="btn btn-sm" onclick="copyTxLink(\\''+txId+'\\')">Copy Link</button></div>'}html+='</div>';e.innerHTML=html"""

if old_purchase in html:
    html = html.replace(old_purchase, new_purchase)
    changes += 1
    print('3. Token sale purchase updated with explorer link')
else:
    print('3. WARNING: purchase pattern not found')

# 4. Make wallet transaction history hashes clickable
old_history = "t.slice(-20).reverse().forEach(x=>{xh+='<tr><td class=\"mono\">'+shortAddr(x.hash||x.id||'')+'</td><td class=\"mono\">'+shortAddr(x.from||'')+'</td><td class=\"mono\">'+shortAddr(x.to||'')+'</td><td class=\"text-green\">'+(x.amount||0)+'</td></tr>'});"

new_history = "t.slice(-20).reverse().forEach(x=>{var xh2=x.hash||x.id||'';xh+='<tr style=\"cursor:pointer\" onclick=\"showTxDetail(\\''+xh2+'\\')\"><td class=\"mono\" style=\"color:#00ff88\">'+shortAddr(xh2)+'</td><td class=\"mono\">'+shortAddr(x.from||'')+'</td><td class=\"mono\">'+shortAddr(x.to||'')+'</td><td class=\"text-green\">'+(x.amount||0)+'</td></tr>'});"

if old_history in html:
    html = html.replace(old_history, new_history)
    changes += 1
    print('4. Wallet tx history made clickable')
else:
    print('4. WARNING: tx history pattern not found')

# 5. Add copyTxLink and shareTx helper functions after closeDetailModal
helper_js = """
// TX SHARE HELPERS
function copyTxLink(hash){
  var url=location.origin+'/dashboard?tx='+hash;
  navigator.clipboard.writeText(url).then(function(){toast('Link copied to clipboard!')}).catch(function(){
    var ta=document.createElement('textarea');ta.value=url;document.body.appendChild(ta);ta.select();document.execCommand('copy');document.body.removeChild(ta);toast('Link copied!')
  })
}
function shareTx(hash){
  var url=location.origin+'/dashboard?tx='+hash;
  if(navigator.share){navigator.share({title:'Verdis Transaction',text:'Check this transaction on Verdis Chain',url:url}).catch(function(){})}
  else{copyTxLink(hash)}
}
"""

# Insert after closeDetailModal function
close_modal_marker = "function closeDetailModal(){"
if close_modal_marker in html:
    idx = html.find(close_modal_marker)
    # Find the end of this function (next \n after closing })
    func_end = html.find('\n', idx + 100)
    # Find the actual end of the one-liner function
    brace_end = html.find('}', idx)
    line_end = html.find('\n', brace_end) + 1
    html = html[:line_end] + helper_js + '\n' + html[line_end:]
    changes += 1
    print('5. copyTxLink & shareTx helpers added')
else:
    print('5. WARNING: closeDetailModal not found')

# 6. Add URL param support for ?tx= and ?block= on page load
# Find the init() function and add URL param check at the end
init_check = """
// Check URL params for shared tx/block links
var urlParams=new URLSearchParams(location.search);
if(urlParams.get('tx')){setTimeout(function(){showTxDetail(urlParams.get('tx'))},800)}
if(urlParams.get('block')){setTimeout(function(){showBlockDetail(parseInt(urlParams.get('block')))},800)}
"""

# Find the init() function and add before its closing brace
init_marker = "async function init(){"
if init_marker in html:
    init_start = html.find(init_marker)
    # Find the closing } of init() - look for the last } before the next function or </script>
    # init() ends with a closing brace followed by newline
    # Let's find it by looking for "init()" call or the end pattern
    init_area = html[init_start:init_start+2000]
    # The init function ends with "switchTab(currentTab)" or similar + "}"
    # Let's find the pattern
    patterns = [
        "switchTab(currentTab);setTimeout(()=>loadOverview(),500);",
        "switchTab(currentTab);loadOverview();",
        "switchTab(currentTab);",
    ]
    for p in patterns:
        if p in init_area:
            insert_pos = html.find(p, init_start) + len(p)
            html = html[:insert_pos] + init_check + html[insert_pos:]
            changes += 1
            print('6. URL param check added to init()')
            break
    else:
        # Just insert before the last } in init_area
        # Find the last closing brace
        print('6. WARNING: init() end pattern not found, trying alternate...')
        # Look for "init()" call at end of script
        init_call = html.find("init();", init_start)
        if init_call >= 0:
            # Insert before init() call
            html = html[:init_call] + init_check + '\n' + html[init_call:]
            changes += 1
            print('6. URL param check added before init() call')
        else:
            print('6. ERROR: could not find init() call')
else:
    print('6. WARNING: init() not found')

# 7. Also add the explorer link to the block detail modal "Recent Blocks" in overview
# Already done in previous fix (clickable recent blocks)

with open(path, 'w') as f:
    f.write(html)

print(f'\n{changes} changes applied successfully!')
