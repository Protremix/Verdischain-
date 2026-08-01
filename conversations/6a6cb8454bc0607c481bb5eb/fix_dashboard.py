import re

with open("/opt/verdis/app/dist/web/dashboard.html", "r") as f:
    content = f.read()

# 1. Replace loadSale to use /api/ido/info
old_loadSale = """async function loadSale(){const r=await api('sale/stats');if(r&&!r.error)saleStats=r;updateSaleUI()}
function updateSaleUI(){document.getElementById('salePrice').textContent='$'+saleStats.price;document.getElementById('saleRaised').textContent='$'+(saleStats.raised||0).toLocaleString();document.getElementById('saleSold').textContent=(saleStats.sold||0).toLocaleString()+' VCO';const p=((saleStats.sold||0)/saleStats.total*100).toFixed(1);document.getElementById('saleProgress').textContent=p+'%';document.getElementById('saleProgressBar').style.width=p+'%';document.getElementById('saleRemaining').textContent=(saleStats.total-(saleStats.sold||0)).toLocaleString()+' VCO'}
function calcSale(){const c=document.getElementById('salePayment').value,a=parseFloat(document.getElementById('salePayAmount').value);if(!a){document.getElementById('saleReceiveAmount').value='';return}document.getElementById('saleReceiveAmount').value=(a*(saleRates[c]||1000)).toLocaleString()+' VCO'}
async function confirmPurchase(){const c=document.getElementById('salePayment').value,a=parseFloat(document.getElementById('salePayAmount').value),v=document.getElementById('saleVerdisAddr').value.trim();if(!a||!v)return toast('Fill all fields','error');const vs=a*(saleRates[c]||1000);const r=await api('sale/buy','POST',{currency:c,amount:a,verdisAddress:v,vrsAmount:vs});const e=document.getElementById('saleResult');if(r&&r.success){e.innerHTML='<span class="text-green">Purchase confirmed! '+vs.toLocaleString()+' VCO will be sent to '+shortAddr(v)+' within 24h. Order: '+(r.orderId||'—')+'</span>';toast('Purchase confirmed!');if(r.stats){saleStats=r.stats;updateSaleUI()}}else{e.innerHTML='<div class="text-green">Purchase request recorded!<br>Send '+a+' '+c+' to: <span class="mono">0xa1e846855e1768b9C0BEe6E747bedd7bec1Af616</span><br>You will receive '+vs.toLocaleString()+' VCO to '+shortAddr(v)+'<br>Email confirmation to: sales@verdischain.com</div>';toast('Purchase recorded!')}}"""

new_loadSale = """async function loadSale(){
  // Load real IDO data from the blockchain API
  try {
    const r = await fetch(API_BASE+'/api/ido/info');
    const d = await r.json();
    if(d && !d.error) {
      saleStats = {price: d.priceUSD, raised: (d.sold*d.priceUSD), sold: d.sold, total: d.totalAllocation};
      updateSaleUI();
      // Show purchaser count
      const remaining = document.getElementById('saleRemaining');
      if(remaining) remaining.textContent = d.remaining.toLocaleString() + ' VCO';
      // Update progress with real data
      const p = d.progressPct;
      const pe = document.getElementById('saleProgress');
      const pb = document.getElementById('saleProgressBar');
      if(pe) pe.textContent = p + '%';
      if(pb) pb.style.width = p + '%';
    }
  } catch(e) { console.warn('IDO info load failed', e); }
  // Also try the legacy endpoint as fallback
  const r2 = await api('sale/stats');
  if(r2 && !r2.error && !saleStats.sold) { saleStats = r2; updateSaleUI(); }
}
function updateSaleUI(){
  document.getElementById('salePrice').textContent='$'+(saleStats.price||0.001);
  document.getElementById('saleRaised').textContent='$'+(saleStats.raised||0).toLocaleString();
  document.getElementById('saleSold').textContent=(saleStats.sold||0).toLocaleString()+' VCO';
  const p=((saleStats.sold||0)/((saleStats.total||10000000000))*100).toFixed(2);
  document.getElementById('saleProgress').textContent=p+'%';
  document.getElementById('saleProgressBar').style.width=p+'%';
  document.getElementById('saleRemaining').textContent=((saleStats.total||10000000000)-(saleStats.sold||0)).toLocaleString()+' VCO';
}
function calcSale(){
  const a=parseFloat(document.getElementById('salePayAmount').value);
  if(!a){document.getElementById('saleReceiveAmount').value='';return}
  // Price is $0.001 per VCO, so VCO = USD / 0.001 = USD * 1000
  const vco = (a * 1000).toFixed(0);
  document.getElementById('saleReceiveAmount').value = vco.toLocaleString()+' VCO';
}
async function confirmPurchase(){
  const a=parseFloat(document.getElementById('salePayAmount').value);
  let v=document.getElementById('saleVerdisAddr').value.trim();
  // Auto-use connected wallet if available
  if(!v && wallet && wallet.address) { v = wallet.address; document.getElementById('saleVerdisAddr').value = v; }
  if(!a||!v) return toast('Connect your wallet or enter address first','error');
  const vcoAmount = Math.floor(a * 1000);
  if(vcoAmount < 100) return toast('Minimum purchase is 100 VCO ($0.10)','error');
  const e=document.getElementById('saleResult');
  e.innerHTML='<span class="text-muted">Processing purchase...</span>';
  // Call the real IDO API
  const r = await fetch(API_BASE+'/api/ido/purchase', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({address: v, amountVCO: vcoAmount.toString()})
  });
  const d = await r.json();
  if(d && d.success) {
    e.innerHTML='<span class="text-green">✓ Purchased '+d.amountVCO.toLocaleString()+' VCO for $'+d.totalCostUSD+'!<br>New balance: '+d.newBalance.toLocaleString()+' VCO<br>Tx: '+shortAddr(d.txId||'')+'</span>';
    toast('Purchase successful! '+d.amountVCO.toLocaleString()+' VCO added to your wallet');
    // Update wallet display if connected
    if(wallet && wallet.address === v) {
      wallet.balance = d.newBalance;
      updateWalletUI();
      loadWalletData();
    }
    loadSale(); // Refresh sale stats
  } else {
    e.innerHTML='<span class="text-red">✗ '+(d?.error||'Purchase failed')+'</span>';
    toast(d?.error||'Purchase failed','error');
  }
}"""

if old_loadSale in content:
    content = content.replace(old_loadSale, new_loadSale)
    print("Replaced sale functions with IDO API integration")
else:
    print("WARNING: Could not find exact sale function match - trying regex")
    # Try a more flexible approach
    content = re.sub(
        r'async function loadSale\(\).*?async function confirmPurchase\(\).*?\}',
        new_loadSale,
        content,
        flags=re.DOTALL
    )
    print("Replaced via regex")

# 2. Enhance the init function to show a welcome message for returning users
old_init = """function init(){const s=localStorage.getItem('verdis-wallet');if(s){try{wallet=JSON.parse(s);updateWalletUI();loadWalletData()}catch{}}const t=localStorage.getItem('verdis-tab')||'overview';switchTab(t);loadOverview();setInterval(()=>{const a=document.querySelector('.nav-tab.active')?.dataset.tab;if(a==='overview')loadOverview()},15000)}"""

new_init = """function init(){
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
  loadOverview();
  // Auto-refresh wallet balance every 30 seconds
  setInterval(()=>{
    if(wallet && wallet.address){
      fetch(API_BASE+'/api/wallet/'+wallet.address+'/balance')
        .then(r=>r.json())
        .then(d=>{
          if(d && d.balance!==undefined){
            wallet.balance=d.balance;
            const pt=document.getElementById('walletPillText');
            if(pt) pt.textContent=shortAddr(wallet.address)+' | '+d.balance+' VCO';
            const wb=document.getElementById('wBalance');
            if(wb) wb.textContent=d.balance.toLocaleString()+' VCO';
          }
        }).catch(()=>{});
    }
    const a=document.querySelector('.nav-tab.active')?.dataset.tab;
    if(a==='overview')loadOverview();
    if(a==='sale')loadSale();
  },15000);
}"""

if old_init in content:
    content = content.replace(old_init, new_init)
    print("Enhanced init function with wallet persistence and auto-refresh")
else:
    print("WARNING: Could not find exact init function match")

# 3. Auto-fill wallet address in sale form when wallet is connected
old_updateWalletUI = """function updateWalletUI(){const p=document.getElementById('walletPill'),pt=document.getElementById('walletPillText'),d=p.querySelector('.dot'),cv=document.getElementById('walletConnectView'),wv=document.getElementById('walletConnectedView');if(wallet){d.classList.remove('disconnected');pt.textContent=shortAddr(wallet.address)+' | '+(wallet.balance||0)+' VCO';cv.classList.add('hidden');wv.classList.remove('hidden');document.getElementById('wAddr').textContent=wallet.address;document.getElementById('saleVerdisAddr').value=wallet.address;document.getElementById('faucetAddr').value=wallet.address;document.getElementById('nftTo').value=wallet.address}else{d.classList.add('disconnected');pt.textContent='No wallet connected';cv.classList.remove('hidden');wv.classList.add('hidden')}}"""

new_updateWalletUI = """function updateWalletUI(){
  const p=document.getElementById('walletPill'),pt=document.getElementById('walletPillText'),d=p.querySelector('.dot'),cv=document.getElementById('walletConnectView'),wv=document.getElementById('walletConnectedView');
  if(wallet){
    d.classList.remove('disconnected');
    pt.textContent=shortAddr(wallet.address)+' | '+(wallet.balance||0)+' VCO';
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
}"""

if old_updateWalletUI in content:
    content = content.replace(old_updateWalletUI, new_updateWalletUI)
    print("Enhanced updateWalletUI with null-safety")

# 4. Add wallet backup section to the connected wallet view
old_backup = """</div></div>
<div class="card mt-4"><div class="card-header">Transaction History</div><div id="walletTxHistory"></div></div>
</div>
</div>"""

new_backup = """</div></div>
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
</div>"""

if old_backup in content:
    content = content.replace(old_backup, new_backup, 1)
    print("Added wallet backup section")

# 5. Update the wallet section description
content = content.replace(
    "Your wallet stays in your browser.",
    "Your wallet is saved in this browser and restores automatically on each visit. Use Backup to access from other devices."
)

with open("/opt/verdis/app/dist/web/dashboard.html", "w") as f:
    f.write(content)

print("Dashboard updated successfully")
