#!/usr/bin/env python3
"""Rebuild the wallet system in the dashboard - fix all bugs"""

with open('/opt/verdis/app/dist/web/dashboard.html') as f:
    html = f.read()

# ============================================================
# 1. Replace the wallet HTML section (remove duplicate label, clean structure)
# ============================================================
old_wallet_html = '''<div class="section" id="section-wallet">
<div class="code-section-label">// NATIVE_WALLET_MANAGER</div>
<div class="code-section-label">// NATIVE_WALLET_MANAGER</div>
<div class="explore-header"><h2>Native Wallet</h2><p>Create a new Verdis wallet or import an existing one. Your wallet is saved in this browser and restores automatically on each visit. Use Backup to access from other devices.</p></div>
<div id="walletConnectView">
<div class="grid-2">
<div class="card"><div class="card-header">Create New Wallet</div>
<p class="text-muted text-sm mb-4">Generates a new Verdis wallet with private key and mnemonic.</p>
<button class="btn btn-primary w-full" onclick="nativeCreateWallet()">Create Native Wallet</button>
</div>
<div class="card"><div class="card-header">Import Wallet</div>
<div class="form-group"><label>Private Key or 12-Word Mnemonic</label><input type="password" id="importKey" placeholder="Paste private key or mnemonic..." class="mono"></div>
<button class="btn btn-blue w-full" onclick="nativeImportWallet()">Import Wallet</button>
</div></div>
<div class="card mt-4" style="border-color:rgba(88,166,255,.3)"><div class="card-header text-blue">External Wallet (Optional)</div>
<p class="text-muted text-sm mb-4">Connect MetaMask or Trust Wallet. Native wallet works without any extension.</p>
<div class="flex gap-2">
<button class="btn btn-sm" onclick="connectMetaMask()">Connect MetaMask</button>
<button class="btn btn-sm" onclick="addVerdisNetwork()">Add Verdis Network</button>
<button class="btn btn-sm" onclick="addVRSToken()">Add VRS Token</button>
</div></div>
</div>
<div id="walletConnectedView" class="hidden">
<div class="grid-3">
<div class="card"><div class="card-header">Address</div><div class="mono text-sm" id="wAddr" style="word-break:break-all">—</div><button class="btn btn-sm mt-2" onclick="copyText(wallet.address)">Copy</button></div>
<div class="card"><div class="card-header">VRS Balance</div><div class="text-2xl text-green" id="wBalance">0 VRS</div></div>
<div class="card"><div class="card-header">Staked</div><div class="text-xl text-purple" id="wStaked">0 VRS</div></div>
</div>
<div class="grid-2 mt-4">
<div class="card"><div class="card-header">Send VRS</div>
<div class="form-group"><label>To Address</label><input type="text" id="sendTo" placeholder="0x..." class="mono"></div>
<div class="grid-2"><div class="form-group"><label>Amount</label><input type="number" id="sendAmount" placeholder="100" step="0.000001"></div><div class="form-group"><label>Gas</label><input type="text" value="0.001 VRS" disabled></div></div>
<button class="btn btn-primary w-full" onclick="nativeSendTx()">Send Transaction</button>
<div id="sendResult" class="text-sm mt-2"></div></div>
<div class="card"><div class="card-header">Token Balances</div><div id="tokenBalances"></div>
<div class="card-header mt-4">Wallet Actions</div>
<div class="flex gap-2 mt-2">
<button class="btn btn-sm" onclick="claimFaucet()">Claim 1000 VRS</button>
<button class="btn btn-sm" onclick="switchTab('sale')">Buy VRS</button>
<button class="btn btn-sm btn-red" onclick="nativeDisconnect()">Disconnect</button>
</div>
<div class="text-sm text-muted mt-2">Private Key: <span class="mono text-green" id="wPrivKey" style="cursor:pointer" onclick="togglePrivKey()">[click to show]</span></div>
</div></div>
<div class="card mt-4"><div class="card-header">Wallet Backup & Cross-Device Access</div>
<p class="text-muted text-sm mb-2">Save your private key to access this wallet from any device or browser. Share it with NOBODY.</p>
<div class="flex gap-2 items-center">
<input type="text" id="backupKey" readonly class="mono text-sm" style="flex:1;opacity:0.7" value="[click reveal below]">
<button class="btn btn-sm" onclick="const pk=document.getElementById('backupKey');pk.value=wallet?.privateKey||'—';pk.style.opacity='1'">Reveal Key</button>
<button class="btn btn-sm" onclick="copyText(wallet?.privateKey||'')">Copy Key</button>
</div>
<p class="text-muted text-sm mt-2">To access on another device: Dashboard → Import Wallet → paste this key.</p>
</div>
<div class="card mt-4"><div class="card-header">Transaction History</div><div id="walletTxHistory"></div></div>
</div>
</div>'''

new_wallet_html = '''<div class="section" id="section-wallet">
<div class="code-section-label">// NATIVE_WALLET_MANAGER</div>
<div class="explore-header"><h2>Native Wallet</h2><p>Create a new Verdis wallet or import an existing one. Your wallet is saved in this browser and restores automatically on each visit.</p></div>

<!-- CONNECT VIEW -->
<div id="walletConnectView">
<div class="grid-2">
<div class="card"><div class="card-header">Create New Wallet</div>
<p class="text-muted text-sm mb-4">Generates a new Verdis wallet with private key and mnemonic phrase.</p>
<button class="btn btn-primary w-full" id="btnCreateWallet" onclick="nativeCreateWallet()">Create Native Wallet</button>
</div>
<div class="card"><div class="card-header">Import Wallet</div>
<div class="form-group"><label>Private Key or 12-Word Mnemonic</label><input type="password" id="importKey" placeholder="Paste private key or mnemonic..." class="mono" onkeypress="if(event.key==='Enter')nativeImportWallet()"></div>
<button class="btn btn-blue w-full" id="btnImportWallet" onclick="nativeImportWallet()">Import Wallet</button>
</div></div>
<div class="card mt-4" style="border-color:rgba(88,166,255,.3)"><div class="card-header text-blue">External Wallet (Optional)</div>
<p class="text-muted text-sm mb-4">Connect MetaMask. Native wallet works without any extension.</p>
<div class="flex gap-2">
<button class="btn btn-sm" onclick="connectMetaMask()">Connect MetaMask</button>
<button class="btn btn-sm" onclick="addVerdisNetwork()">Add Verdis Network</button>
</div></div>
</div>

<!-- CONNECTED VIEW -->
<div id="walletConnectedView" class="hidden">
<div class="grid-3">
<div class="card"><div class="card-header">Address</div><div class="mono text-sm" id="wAddr" style="word-break:break-all">—</div><button class="btn btn-sm mt-2" onclick="copyText(wallet?.address||'')">Copy Address</button></div>
<div class="card"><div class="card-header">VRS Balance</div><div class="text-2xl text-green" id="wBalance">0 VRS</div><button class="btn btn-sm mt-2" onclick="loadWalletData()">Refresh</button></div>
<div class="card"><div class="card-header">Staked</div><div class="text-xl text-purple" id="wStaked">0 VRS</div></div>
</div>

<div class="grid-2 mt-4">
<!-- SEND -->
<div class="card"><div class="card-header">Send VRS</div>
<div class="form-group"><label>To Address</label><input type="text" id="sendTo" placeholder="0x..." class="mono"></div>
<div class="grid-2"><div class="form-group"><label>Amount</label><input type="number" id="sendAmount" placeholder="100" step="0.000001"></div><div class="form-group"><label>Fee</label><input type="text" value="1 VRS" disabled></div></div>
<button class="btn btn-primary w-full" id="btnSendTx" onclick="nativeSendTx()">Send Transaction</button>
<div id="sendResult" class="text-sm mt-2"></div>
</div>

<!-- ACTIONS + TOKENS -->
<div class="card">
<div class="card-header">Token Balances</div><div id="tokenBalances"></div>
<div class="card-header mt-4">Wallet Actions</div>
<div class="flex gap-2 mt-2" style="flex-wrap:wrap">
<button class="btn btn-sm" onclick="claimFaucet()">Claim 1000 VRS</button>
<button class="btn btn-sm" onclick="switchTab('sale')">Buy VRS</button>
<button class="btn btn-sm" onclick="switchTab('staking')">Stake</button>
<button class="btn btn-sm btn-red" onclick="nativeDisconnect()">Disconnect</button>
</div>
<div class="text-sm text-muted mt-2">Private Key: <span class="mono text-green" id="wPrivKey" style="cursor:pointer" onclick="togglePrivKey()">[click to show]</span></div>
</div>
</div>

<!-- BACKUP -->
<div class="card mt-4"><div class="card-header">Wallet Backup & Cross-Device Access</div>
<p class="text-muted text-sm mb-2">Save your private key to access this wallet from any device. Share it with NOBODY.</p>
<div class="flex gap-2 items-center">
<input type="text" id="backupKey" readonly class="mono text-sm" style="flex:1;opacity:0.7" value="[click reveal below]">
<button class="btn btn-sm" onclick="const pk=document.getElementById('backupKey');pk.value=wallet?.privateKey||'—';pk.style.opacity='1'">Reveal Key</button>
<button class="btn btn-sm" onclick="copyText(wallet?.privateKey||'')">Copy Key</button>
</div>
<p class="text-muted text-sm mt-2">To access on another device: Dashboard → Import Wallet → paste this key.</p>
</div>

<!-- TX HISTORY -->
<div class="card mt-4"><div class="card-header">Transaction History</div><div id="walletTxHistory"><div class="text-muted text-sm">Connect wallet to view transactions</div></div></div>
</div>
</div>'''

if old_wallet_html in html:
    html = html.replace(old_wallet_html, new_wallet_html, 1)
    print("1. Replaced wallet HTML section")
else:
    print("1. ERROR: wallet HTML not found")

# ============================================================
# 2. Fix loadTabData - remove the broken loadTokenomics inside it
# ============================================================
old_loadtab = '''function loadTabData(t){
    

    // New tab data loaders
    
    if (t === 'nameservice') loadVNS();
    
    
    if (t === 'tokenomics') loadTokenomics();
    // Governance already has its own loader, ensure it's called
    if (t === 'governance') loadGovernance();
async function loadTokenomics(){try{const s=await api("tokenomics/stats");if(!s||s.error)return;const d=document.getElementById("tokenomicsData");if(d&&s){d.innerHTML=statCard("Total Supply",(s.totalSupply||0).toLocaleString())+statCard("Circulating",(s.circulating||0).toLocaleString())+statCard("Burned",(s.burned||0).toLocaleString())+statCard("Staked",(s.staked||0).toLocaleString())+statCard("Treasury",(s.treasury||0).toLocaleString())+statCard("Block Reward",s.blockReward||16);const f=document.getElementById("feeDistribution");if(f&&s.fees){f.innerHTML=Object.entries(s.fees).map(([k,v])=>"<div style=\\"display:flex;justify-content:space-between;padding:4px 0\\"><span style=\\"color:#888\\">"+k+"</span><span style=\\"color:#00ff88\\">"+v+"</span></div>").join("")}}}catch(e){console.error(e)}}
switch(t){case'overview':loadOverview();break;case'blocks':loadBlocks();break;case'txs':loadTxs();break;case'validators':loadValidators();break;case'dex':loadDex();break;case'staking':loadStaking();break;case'eco':loadEco();break;case'governance':loadGovernance();break;case'contracts':loadContracts();break;case'nft':loadNFT();break;case'wallet':if(wallet)loadWalletData();break;case'sale':loadSale();break}}'''

new_loadtab = '''function loadTabData(t){
    if(t==='nameservice')loadVNS();
    if(t==='tokenomics')loadTokenomics();
    if(t==='governance')loadGovernance();
    switch(t){
        case'overview':loadOverview();break;
        case'blocks':loadBlocks();break;
        case'txs':loadTxs();break;
        case'validators':loadValidators();break;
        case'dex':loadDex();break;
        case'staking':loadStaking();break;
        case'eco':loadEco();break;
        case'governance':loadGovernance();break;
        case'contracts':loadContracts();break;
        case'nft':loadNFT();break;
        case'wallet':if(wallet)loadWalletData();break;
        case'sale':loadSale();break;
        case'faucet':break;
    }
}'''

if old_loadtab in html:
    html = html.replace(old_loadtab, new_loadtab, 1)
    print("2. Fixed loadTabData")
else:
    print("2. ERROR: loadTabData not found")

# ============================================================
# 3. Replace ALL wallet JS functions with clean implementations
# ============================================================
old_wallet_js = '''// NATIVE WALLET
function nativeCreateWallet(){fetch(API_BASE+'/api/wallet/create-mnemonic',{method:'POST'}).then(r=>r.json()).then(d=>{if(d.error)return toast(d.error,'error');wallet={address:d.address,privateKey:d.privateKey,publicKey:d.publicKey,mnemonic:d.mnemonic||null};localStorage.setItem('verdis-wallet',JSON.stringify(wallet));updateWalletUI();if(d.mnemonic){toast('Wallet created! Save your mnemonic!');setTimeout(()=>{alert('SAVE THIS MNEMONIC PHASE\\n\\n'+d.mnemonic+'\\n\\nThis is your wallet backup. Anyone with this phrase can access your funds. Store it safely!');},100);}else{toast('Wallet created!');}loadWalletData()})}
function nativeImportWallet(){const k=document.getElementById('importKey').value.trim();if(!k)return toast('Enter key or mnemonic','error');if(k.split(' ').length>=12){fetch(API_BASE+'/api/wallet/create-mnemonic',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mnemonic:k})}).then(r=>r.json()).then(d=>{if(d.error)return toast(d.error,'error');wallet={address:d.address,privateKey:d.privateKey,publicKey:d.publicKey,mnemonic:k};localStorage.setItem('verdis-wallet',JSON.stringify(wallet));updateWalletUI();toast('Wallet imported!');loadWalletData()})}else{fetch(API_BASE+'/api/wallet/create-mnemonic',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({privateKey:k})}).then(r=>r.json()).then(d=>{if(d.error)return toast(d.error||'Import failed','error');wallet={address:d.address,privateKey:d.privateKey,publicKey:d.publicKey};localStorage.setItem('verdis-wallet',JSON.stringify(wallet));updateWalletUI();toast('Wallet imported!');loadWalletData()})}}
function nativeDisconnect(){wallet=null;localStorage.removeItem('verdis-wallet');updateWalletUI();toast('Disconnected')}
function togglePrivKey(){const e=document.getElementById('wPrivKey');if(e.textContent==='[click to show]'){e.textContent=wallet?.privateKey||'—';e.style.color='var(--red)'}else{e.textContent='[click to show]';e.style.color='var(--green)'}}
function updateWalletUI(){
  const p=document.getElementById('walletPill'),pt=document.getElementById('walletPillText'),d=p.querySelector('.dot'),cv=document.getElementById('walletConnectView'),wv=document.getElementById('walletConnectedView');
  if(wallet){
    d.classList.remove('disconnected');
    pt.textContent=shortAddr(wallet.address)+' | '+(wallet.balance||0)+' VRS';
    cv.classList.add('hidden');
    wv.classList.remove('hidden');
    document.getElementById('wAddr').textContent=wallet.address;
    // Auto-fill wallet address in sale form
    const sa=document.getElementById('saleVerdisAddr');
    if(sa) sa.value=wallet.address;
    const fa=document.getElementById('faucetAddr');
    if(fa) fa.value=wallet.address;
    const nt=document.getElementById('nftTo');
    if(nt) nt.value=wallet.address;
  } else {
    d.classList.add('disconnected');
    pt.textContent='No wallet connected';
    cv.classList.remove('hidden');
    wv.classList.add('hidden');
  }
}
async function loadWalletData(){if(!wallet)return;const[b,s,t,tb]=await Promise.all([api('wallet/'+wallet.address+'/balance'),api('wallet/'+wallet.address+'/staked'),api('wallet/'+wallet.address+'/transactions'),api('dex/token/balances/'+wallet.address)]);if(b&&!b.error&&b.balance!==undefined){wallet.balance=b.balance;document.getElementById('wBalance').textContent=b.balance.toLocaleString()+' VRS';document.getElementById('walletPillText').textContent=shortAddr(wallet.address)+' | '+b.balance+' VRS';}if(s&&!s.error)document.getElementById('wStaked').textContent=(s.staked||0).toLocaleString()+' VRS';let th='<div class="text-muted text-sm">No token balances</div>';const tbData=tb?.balances||tb;if(tbData&&Array.isArray(tbData)&&tbData.length)th=tbData.map(x=>'<div class="flex justify-between" style="padding:4px 0"><span class="mono">'+(x.symbol||x.token)+'</span><span class="text-green">'+x.balance+'</span></div>').join('');else if(tbData&&typeof tbData==='object'&&Object.keys(tbData).length)th=Object.entries(tbData).filter(([k,v])=>typeof v!=='object').map(([k,v])=>'<div class="flex justify-between" style="padding:4px 0"><span class="mono">'+k+'</span><span class="text-green">'+v+'</span></div>').join('');document.getElementById('tokenBalances').innerHTML=th;let xh='<div class="text-muted text-sm">No transactions yet</div>';if(t&&Array.isArray(t)&&t.length){xh='<table class="data-table"><thead><tr><th>Hash</th><th>Dir</th><th>From</th><th>To</th><th>Amount</th><th>Fee</th><th>Block</th><th>Age</th><th>Status</th></tr></thead><tbody>';t.slice(-20).reverse().forEach(x=>{var xh2=x.hash||x.id||'';var dir=x.direction||(x.from===wallet.address?'sent':'received');var isSent=dir==='sent';var status=x.pending?'pending':(x.status||'success');var blk=x.blockIndex||x.block||'—';var age=x.timestamp?timeAgoShort(x.timestamp):'—';xh+='<tr style="cursor:pointer" onclick="showTxDetail(\\''+xh2+'\\')"><td class="mono" style="color:#00ff88">'+shortAddr(xh2,12)+'</td><td style="font-size:14px">'+(isSent?'⬆':'⬇')+'</td><td class="mono">'+shortAddr(x.from||'')+'</td><td class="mono">'+shortAddr(x.to||'')+'</td><td class="'+(isSent?'text-red':'text-green')+'">'+(isSent?'-':'+')+(x.amount||0)+' VRS</td><td class="text-muted">'+(x.fee||0)+'</td><td>'+(blk!=='—'?'<a style="color:#00ff88;cursor:pointer" onclick="event.stopPropagation();showBlockDetail('+blk+')">#'+blk+'</a>':'—')+'</td><td class="text-muted">'+age+'</td><td><span class="badge '+(status==='failed'?'badge-failed':status==='pending'?'badge-pending':'badge-success')+'">'+status+'</span></td></tr>'});xh+='</tbody></table>'}document.getElementById('walletTxHistory').innerHTML=xh}
async function nativeSendTx(){const to=document.getElementById('sendTo').value.trim(),am=parseFloat(document.getElementById('sendAmount').value);if(!to||!am)return toast('Enter address and amount','error');if(!wallet)return toast('Connect wallet','error');const r=await api('transaction/send','POST',{from:wallet.address,privateKey:wallet.privateKey,to,amount:am});const e=document.getElementById('sendResult');if(r&&r.txId){var txUrl=location.origin+'/dashboard?tx='+r.txId;e.innerHTML='<div style="margin-top:8px;padding:12px;border:1px solid #30363d;border-radius:8px;background:#0d1117"><div class="text-green" style="font-size:14px;margin-bottom:8px">✓ Transaction sent!</div><div class="text-muted text-sm" style="margin-bottom:4px">Tx Hash:</div><div class="mono text-sm" style="word-break:break-all;margin-bottom:10px">'+r.txId+'</div><div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn btn-sm btn-primary" onclick="showTxDetail(\\''+r.txId+'\\')">View in Explorer</button><button class="btn btn-sm" onclick="copyTxLink(\\''+r.txId+'\\')">Copy Link</button><button class="btn btn-sm" onclick="shareTx(\\''+r.txId+'\\')">Share</button></div></div>';toast('Transaction sent!');loadWalletData()}else e.innerHTML='<span class="text-red">Error: '+(r&&r.error||'failed')+'</span>'}
async function claimFaucet(){if(!wallet)return toast('Connect wallet','error');const r=await api('faucet/claim','POST',{address:wallet.address});if(r.success){toast('1000 VRS claimed!');loadWalletData()}else toast(r.error||'Error','error')}
async function claimFaucetManual(){const a=document.getElementById('faucetAddr').value.trim();if(!a)return toast('Enter address','error');const r=await api('faucet/claim','POST',{address:a});const e=document.getElementById('faucetResult');if(r.success){var txId=r.txId||r.txHash||'';var html='<div style="margin-top:8px;padding:12px;border:1px solid #30363d;border-radius:8px;background:#0d1117"><div class="text-green" style="margin-bottom:8px">✓ 1000 VRS sent to '+shortAddr(a)+'</div>';if(txId){html+='<div class="text-muted text-sm" style="margin-bottom:4px">Tx Hash:</div><div class="mono text-sm" style="word-break:break-all;margin-bottom:10px">'+txId+'</div><div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn btn-sm btn-primary" onclick="showTxDetail(\\''+txId+'\\')">View in Explorer</button><button class="btn btn-sm" onclick="copyTxLink(\\''+txId+'\\')">Copy Link</button></div>'}html+='</div>';e.innerHTML=html;toast('Claimed!')}else e.innerHTML='<span class="text-red">'+(r.error||'Error')+'</span>'}
async function connectMetaMask(){if(typeof window.ethereum==='undefined')return toast('MetaMask not found','error');try{const a=await window.ethereum.request({method:'eth_requestAccounts'});wallet={address:a[0],privateKey:null,external:true};localStorage.setItem('verdis-wallet',JSON.stringify(wallet));updateWalletUI();toast('MetaMask connected');loadWalletData()}catch(e){toast(e.message,'error')}}
async function addVerdisNetwork(){if(typeof window.ethereum==='undefined')return toast('MetaMask not found','error');try{await window.ethereum.request({method:'wallet_addEthereumChain',params:[{chainId:'0x38d',chainName:'Verdis',nativeCurrency:{name:'Verdis',symbol:'VRS',decimals:18},rpcUrls:['https://rpc.verdischain.com'],blockExplorerUrls:['https://verdischain.com']}]});toast('Network added')}catch(e){toast(e.message,'error')}}
async function addVRSToken(){if(typeof window.ethereum==='undefined')return toast('MetaMask not found','error');try{await window.ethereum.request({method:'wallet_watchAsset',params:{type:'ERC20',options:{address:'0x0000000000000000000000000000000000000000',symbol:'VRS',decimals:18}}});toast('Token added')}catch(e){toast(e.message,'error')}}'''

new_wallet_js = '''// === NATIVE WALLET (clean rebuild) ===
let _walletBusy=false;

function _setBtn(id,label,disabled){
  const b=document.getElementById(id);
  if(b){b.textContent=label;b.disabled=disabled;b.style.opacity=disabled?'0.5':'1';}
}

async function nativeCreateWallet(){
  if(_walletBusy)return;
  _walletBusy=true;_setBtn('btnCreateWallet','Creating...',true);
  try{
    const r=await fetch(API_BASE+'/api/wallet/create-mnemonic',{method:'POST'});
    const d=await r.json();
    if(d.error){toast(d.error,'error');return;}
    wallet={address:d.address,privateKey:d.privateKey,publicKey:d.publicKey,mnemonic:d.mnemonic||null,balance:0};
    localStorage.setItem('verdis-wallet',JSON.stringify(wallet));
    updateWalletUI();
    if(d.mnemonic){
      toast('Wallet created! Save your mnemonic!');
      setTimeout(()=>{
        alert('SAVE THIS MNEMONIC PHRASE\\n\\n'+d.mnemonic+'\\n\\nThis is your wallet backup.\\nAnyone with this phrase can access your funds.\\nStore it safely!');
      },200);
    }else{toast('Wallet created!');}
    await loadWalletData();
  }catch(e){toast('Failed to create wallet: '+e.message,'error');}
  finally{_walletBusy=false;_setBtn('btnCreateWallet','Create Native Wallet',false);}
}

async function nativeImportWallet(){
  if(_walletBusy)return;
  const k=document.getElementById('importKey').value.trim();
  if(!k){toast('Enter a private key or mnemonic','error');return;}
  _walletBusy=true;_setBtn('btnImportWallet','Importing...',true);
  try{
    const body=k.split(' ').length>=12?{mnemonic:k}:{privateKey:k};
    const r=await fetch(API_BASE+'/api/wallet/create-mnemonic',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    const d=await r.json();
    if(d.error){toast(d.error||'Import failed','error');return;}
    wallet={address:d.address,privateKey:d.privateKey,publicKey:d.publicKey,mnemonic:k.split(' ').length>=12?k:null,balance:0};
    localStorage.setItem('verdis-wallet',JSON.stringify(wallet));
    document.getElementById('importKey').value='';
    updateWalletUI();
    toast('Wallet imported!');
    await loadWalletData();
  }catch(e){toast('Failed to import wallet: '+e.message,'error');}
  finally{_walletBusy=false;_setBtn('btnImportWallet','Import Wallet',false);}
}

function nativeDisconnect(){
  wallet=null;
  localStorage.removeItem('verdis-wallet');
  updateWalletUI();
  // Clear send form
  const sr=document.getElementById('sendResult');if(sr)sr.innerHTML='';
  const st=document.getElementById('sendTo');if(st)st.value='';
  const sa=document.getElementById('sendAmount');if(sa)sa.value='';
  toast('Wallet disconnected');
}

function togglePrivKey(){
  const e=document.getElementById('wPrivKey');
  if(!e)return;
  if(e.textContent==='[click to show]'){
    e.textContent=wallet?.privateKey||'[no key]';
    e.style.color='#ff4444';
  }else{
    e.textContent='[click to show]';
    e.style.color='#00ff88';
  }
}

function updateWalletUI(){
  const p=document.getElementById('walletPill');
  const pt=document.getElementById('walletPillText');
  const cv=document.getElementById('walletConnectView');
  const wv=document.getElementById('walletConnectedView');
  if(!p||!pt||!cv||!wv)return;
  if(wallet){
    const dot=p.querySelector('.dot');
    if(dot)dot.classList.remove('disconnected');
    pt.textContent=shortAddr(wallet.address)+' | '+(wallet.balance||0)+' VRS';
    cv.classList.add('hidden');
    wv.classList.remove('hidden');
    const addrEl=document.getElementById('wAddr');
    if(addrEl)addrEl.textContent=wallet.address;
    // Auto-fill forms
    const sa=document.getElementById('saleVerdisAddr');if(sa)sa.value=wallet.address;
    const fa=document.getElementById('faucetAddr');if(fa)fa.value=wallet.address;
    const nt=document.getElementById('nftTo');if(nt)nt.value=wallet.address;
    // Reset private key display
    const pk=document.getElementById('wPrivKey');
    if(pk){pk.textContent='[click to show]';pk.style.color='#00ff88';}
  }else{
    const dot=p.querySelector('.dot');
    if(dot)dot.classList.add('disconnected');
    pt.textContent='No wallet connected';
    cv.classList.remove('hidden');
    wv.classList.add('hidden');
  }
}

async function loadWalletData(){
  if(!wallet||!wallet.address)return;
  const addr=wallet.address;
  try{
    const [b,s,t,tb]=await Promise.all([
      api('wallet/'+addr+'/balance'),
      api('wallet/'+addr+'/staked'),
      api('wallet/'+addr+'/transactions'),
      api('dex/token/balances/'+addr)
    ]);
    // Balance
    if(b&&!b.error&&b.balance!==undefined){
      wallet.balance=b.balance;
      const wb=document.getElementById('wBalance');
      if(wb)wb.textContent=b.balance.toLocaleString()+' VRS';
      const pt=document.getElementById('walletPillText');
      if(pt)pt.textContent=shortAddr(addr)+' | '+b.balance+' VRS';
    }
    // Staked
    if(s&&!s.error){
      const ws=document.getElementById('wStaked');
      if(ws)ws.textContent=(s.staked||0).toLocaleString()+' VRS';
    }
    // Token balances
    const tbel=document.getElementById('tokenBalances');
    if(tbel){
      let th='<div class="text-muted text-sm">No token balances</div>';
      const tbData=tb?.balances||tb;
      if(Array.isArray(tbData)&&tbData.length){
        th=tbData.map(x=>'<div class="flex justify-between" style="padding:4px 0"><span class="mono">'+(x.symbol||x.token)+'</span><span class="text-green">'+x.balance+'</span></div>').join('');
      }else if(tbData&&typeof tbData==='object'&&Object.keys(tbData).length){
        th=Object.entries(tbData).filter(([k,v])=>typeof v!=='object').map(([k,v])=>'<div class="flex justify-between" style="padding:4px 0"><span class="mono">'+k+'</span><span class="text-green">'+v+'</span></div>').join('');
      }
      tbel.innerHTML=th;
    }
    // Transaction history
    const txEl=document.getElementById('walletTxHistory');
    if(txEl){
      if(t&&Array.isArray(t)&&t.length){
        let xh='<table class="data-table"><thead><tr><th>Hash</th><th>Dir</th><th>From</th><th>To</th><th>Amount</th><th>Fee</th><th>Block</th><th>Age</th><th>Status</th></tr></thead><tbody>';
        t.slice(-20).reverse().forEach(x=>{
          const hash=x.hash||x.id||'';
          const isSent=(x.from||'').toLowerCase()===addr.toLowerCase();
          const status=x.pending?'pending':(x.status||'success');
          const blk=x.blockIndex||x.block||'—';
          const age=x.timestamp?timeAgoShort(x.timestamp):'—';
          xh+='<tr style="cursor:pointer" onclick="showTxDetail(\\''+hash+'\\')"><td class="mono" style="color:#00ff88">'+shortAddr(hash,12)+'</td><td style="font-size:14px">'+(isSent?'⬆':'⬇')+'</td><td class="mono">'+shortAddr(x.from||'',8)+'</td><td class="mono">'+shortAddr(x.to||'',8)+'</td><td class="'+(isSent?'text-red':'text-green')+'">'+(isSent?'-':'+')+(x.amount||0)+' VRS</td><td class="text-muted">'+(x.fee||0)+'</td><td>'+(blk!=='—'?'<a style="color:#00ff88;cursor:pointer" onclick="event.stopPropagation();showBlockDetail('+blk+')">#'+blk+'</a>':'—')+'</td><td class="text-muted">'+age+'</td><td><span class="badge '+(status==='failed'?'badge-failed':status==='pending'?'badge-pending':'badge-success')+'">'+status+'</span></td></tr>';
        });
        xh+='</tbody></table>';
        txEl.innerHTML=xh;
      }else{
        txEl.innerHTML='<div class="text-muted text-sm">No transactions yet</div>';
      }
    }
  }catch(e){console.error('loadWalletData error:',e);toast('Failed to load wallet data','error');}
}

async function nativeSendTx(){
  if(_walletBusy)return;
  const to=document.getElementById('sendTo').value.trim();
  const am=parseFloat(document.getElementById('sendAmount').value);
  if(!to){toast('Enter a recipient address','error');return;}
  if(!to.startsWith('0x')||to.length<10){toast('Invalid address format','error');return;}
  if(!am||am<=0){toast('Enter a valid amount','error');return;}
  if(!wallet){toast('Connect wallet first','error');return;}
  if(!wallet.privateKey){toast('This is an external wallet (MetaMask). Cannot sign with native send. Use MetaMask to send.','error');return;}
  _walletBusy=true;_setBtn('btnSendTx','Sending...',true);
  const e=document.getElementById('sendResult');
  if(e)e.innerHTML='<div class="text-muted">Sending '+am+' VRS to '+shortAddr(to)+'...</div>';
  try{
    const r=await api('transaction/send','POST',{from:wallet.address,privateKey:wallet.privateKey,to,amount:am});
    if(r&&r.txId){
      e.innerHTML='<div style="margin-top:8px;padding:12px;border:1px solid rgba(0,255,136,0.3);border-radius:8px;background:rgba(0,255,136,0.05)"><div class="text-green" style="font-size:14px;margin-bottom:8px">✓ Transaction sent!</div><div class="text-muted text-sm" style="margin-bottom:4px">Tx Hash:</div><div class="mono text-sm" style="word-break:break-all;margin-bottom:10px">'+r.txId+'</div><div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn btn-sm btn-primary" onclick="showTxDetail(\\''+r.txId+'\\')">View in Explorer</button><button class="btn btn-sm" onclick="copyTxLink(\\''+r.txId+'\\')">Copy Link</button></div></div>';
      toast('Transaction sent!');
      document.getElementById('sendTo').value='';
      document.getElementById('sendAmount').value='';
      await loadWalletData();
    }else{
      e.innerHTML='<span class="text-red">Error: '+(r&&r.error||'Transaction failed')+'</span>';
      toast(r?.error||'Transaction failed','error');
    }
  }catch(e){
    e.innerHTML='<span class="text-red">Error: '+e.message+'</span>';
    toast('Send failed: '+e.message,'error');
  }
  finally{_walletBusy=false;_setBtn('btnSendTx','Send Transaction',false);}
}

async function claimFaucet(){
  if(!wallet){toast('Connect wallet first','error');return;}
  const r=await api('faucet/claim','POST',{address:wallet.address});
  if(r.success){toast('1000 VRS claimed!');await loadWalletData();}
  else toast(r.error||'Faucet error','error');
}

async function claimFaucetManual(){
  const a=document.getElementById('faucetAddr')?.value.trim();
  if(!a){toast('Enter an address','error');return;}
  const r=await api('faucet/claim','POST',{address:a});
  const e=document.getElementById('faucetResult');
  if(!e)return;
  if(r.success){
    const txId=r.txId||r.txHash||'';
    let html='<div style="margin-top:8px;padding:12px;border:1px solid rgba(0,255,136,0.3);border-radius:8px;background:rgba(0,255,136,0.05)"><div class="text-green" style="margin-bottom:8px">✓ 1000 VRS sent to '+shortAddr(a)+'</div>';
    if(txId)html+='<div class="text-muted text-sm" style="margin-bottom:4px">Tx Hash:</div><div class="mono text-sm" style="word-break:break-all;margin-bottom:10px">'+txId+'</div><div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn btn-sm btn-primary" onclick="showTxDetail(\\''+txId+'\\')">View in Explorer</button><button class="btn btn-sm" onclick="copyTxLink(\\''+txId+'\\')">Copy Link</button></div>';
    html+='</div>';
    e.innerHTML=html;
    toast('Claimed!');
  }else{
    e.innerHTML='<span class="text-red">'+(r.error||'Error')+'</span>';
    toast(r.error||'Error','error');
  }
}

async function connectMetaMask(){
  if(typeof window.ethereum==='undefined'){toast('MetaMask not found. Install it or use native wallet.','error');return;}
  try{
    const a=await window.ethereum.request({method:'eth_requestAccounts'});
    wallet={address:a[0],privateKey:null,publicKey:null,external:true,balance:0};
    localStorage.setItem('verdis-wallet',JSON.stringify(wallet));
    updateWalletUI();
    toast('MetaMask connected (view-only — use MetaMask to send)');
    await loadWalletData();
  }catch(e){toast(e.message||'MetaMask connection failed','error');}
}

async function addVerdisNetwork(){
  if(typeof window.ethereum==='undefined'){toast('MetaMask not found','error');return;}
  try{
    await window.ethereum.request({method:'wallet_addEthereumChain',params:[{chainId:'0x38d',chainName:'Verdis',nativeCurrency:{name:'Verdis',symbol:'VRS',decimals:18},rpcUrls:['https://rpc.verdischain.com'],blockExplorerUrls:['https://verdischain.com']}]});
    toast('Verdis network added to MetaMask');
  }catch(e){toast(e.message||'Failed to add network','error');}
}

// Tokenomics loader (moved out of loadTabData)
async function loadTokenomics(){
  try{
    const s=await api('tokenomics/stats');
    if(!s||s.error)return;
    const d=document.getElementById('tokenomicsData');
    if(d&&s){
      d.innerHTML=statCard('Total Supply',(s.totalSupply||0).toLocaleString())+statCard('Circulating',(s.circulating||0).toLocaleString())+statCard('Burned',(s.burned||0).toLocaleString())+statCard('Staked',(s.staked||0).toLocaleString())+statCard('Treasury',(s.treasury||0).toLocaleString())+statCard('Block Reward',s.blockReward||16);
    }
    const f=document.getElementById('feeDistribution');
    if(f&&s.fees){
      f.innerHTML=Object.entries(s.fees).map(([k,v])=>'<div style="display:flex;justify-content:space-between;padding:4px 0"><span style="color:#888">'+k+'</span><span style="color:#00ff88">'+v+'</span></div>').join('');
    }
  }catch(e){console.error('loadTokenomics error:',e);}
}'''

if old_wallet_js in html:
    html = html.replace(old_wallet_js, new_wallet_js, 1)
    print("3. Replaced all wallet JS functions")
else:
    print("3. ERROR: wallet JS block not found")
    # Try to find a smaller unique piece
    if '// NATIVE WALLET' in html:
        print("   Found '// NATIVE WALLET' marker, trying smaller replacement...")
    else:
        print("   Marker not found at all")

# ============================================================
# 4. Fix the init() function to be more robust
# ============================================================
old_init = '''function init(){
  // Restore wallet from localStorage (per-user, persists across sessions)
  const s=localStorage.getItem('verdis-wallet');
  if(s){
    try{
      wallet=JSON.parse(s);
      updateWalletUI();
      loadWalletData();
      // Show welcome message for returning users
      setTimeout(()=>{
        if(wallet && wallet.address){
          toast('Welcome back! '+shortAddr(wallet.address));
        }
      },1000);
    }catch{console.warn('Failed to restore wallet from localStorage')}
  }
  const t=localStorage.getItem('verdis-tab')||'overview';
  switchTab(t);
  setTimeout(()=>loadOverview(),500);
  // Auto-refresh wallet balance every 30 seconds
  setInterval(()=>{
    if(wallet && wallet.address){
      fetch(API_BASE+'/api/wallet/'+wallet.address+'/balance')
        .then(r=>r.json())
        .then(d=>{
          if(d && d.balance!==undefined){
            wallet.balance=d.balance;
            const pt=document.getElementById('walletPillText');
            if(pt) pt.textContent=shortAddr(wallet.address)+' | '+d.balance+' VRS';
            const wb=document.getElementById('wBalance');
            if(wb) wb.textContent=d.balance.toLocaleString()+' VRS';
          }
        }).catch(()=>{});
    }
    const a=document.querySelector('.nav-tab.active')?.dataset.tab;
    if(a==='overview')loadOverview();
    if(a==='sale')loadSale();
  },30000);
}'''

new_init = '''function init(){
  // Restore wallet from localStorage
  const s=localStorage.getItem('verdis-wallet');
  if(s){
    try{
      wallet=JSON.parse(s);
      updateWalletUI();
      setTimeout(()=>loadWalletData(),300);
      setTimeout(()=>{
        if(wallet&&wallet.address)toast('Welcome back! '+shortAddr(wallet.address));
      },1000);
    }catch(e){console.warn('Failed to restore wallet:',e);localStorage.removeItem('verdis-wallet');}
  }
  // Restore active tab
  const t=localStorage.getItem('verdis-tab')||'overview';
  switchTab(t);
  setTimeout(()=>loadOverview(),500);
  // Auto-refresh every 30s
  setInterval(()=>{
    if(wallet&&wallet.address){
      fetch(API_BASE+'/api/wallet/'+wallet.address+'/balance')
        .then(r=>r.json())
        .then(d=>{
          if(d&&d.balance!==undefined){
            wallet.balance=d.balance;
            const pt=document.getElementById('walletPillText');
            if(pt)pt.textContent=shortAddr(wallet.address)+' | '+d.balance+' VRS';
            const wb=document.getElementById('wBalance');
            if(wb)wb.textContent=d.balance.toLocaleString()+' VRS';
          }
        }).catch(()=>{});
    }
    const a=document.querySelector('.nav-tab.active')?.dataset.tab;
    if(a==='overview')loadOverview();
    if(a==='sale')loadSale();
  },30000);
}'''

if old_init in html:
    html = html.replace(old_init, new_init, 1)
    print("4. Fixed init() function")
else:
    print("4. ERROR: init() not found exactly, checking...")

with open('/opt/verdis/app/dist/web/dashboard.html', 'w') as f:
    f.write(html)
print("\nDashboard wallet rebuilt!")
