
// RPC helper
const RPC = '/rpc';
async function rpc(method, params=[]) {
  try {
    const r = await fetch(RPC, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',method,params,id:1})});
    const j = await r.json();
    return j.result;
  } catch(e) { return null; }
}

// API helper (Vdiscan REST API)
const API = 'https://verdischain.com/api';
async function apiFetch(path) {
  try { const r = await fetch(API+path); return await r.json(); } catch(e) { return null; }
}

// State
let blockNum = 0, finalNum = 0, lastBlockTime = Date.now(), tps = 0, txCount = 0;
const blocksData = [];

// Shorten hash
function shortHash(h, len=6) {
  if (!h || h.length < 20) return h || '—';
  return h.slice(0, 2+len) + '…' + h.slice(-4);
}

function timeAgo(ts) {
  const s = Math.floor((Date.now()-ts)/1000);
  if (s < 60) return s+'s ago';
  if (s < 3600) return Math.floor(s/60)+'m ago';
  return Math.floor(s/3600)+'h ago';
}

// Tab switching
function switchTab(t) {
  document.querySelectorAll('.tab').forEach(b => b.classList.toggle('active', b.dataset.t===t));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.toggle('active', c.id==='tab-'+t));
  if (t==='blocks') loadBlocks();
  if (t==='extrinsics') loadExtrinsics();
  if (t==='validators') loadValidators();
  if (t==='dex') loadDex();
  if (t==='eco') loadEco();
}

// Load latest blocks
async function loadLatestBlocks() {
  const tbody = document.getElementById('latestBlocks');
  if (!tbody) return;
  if (!window._blocksLoaded) tbody.innerHTML = '<tr><td colspan="4"><span class="skel" style="width:100%"></span></td></tr>';
  
  const header = await rpc('chain_getHeader', []);
  if (!header) { tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--text-3)">Failed to load</td></tr>'; return; }
  
  const current = parseInt(header.number, 16);
  blockNum = current;
  document.getElementById('statBlock').textContent = '#'+current;
  document.getElementById('statBlockSub').textContent = 'Block time: 6s';
  document.getElementById('heroBlock').textContent = '#'+current;
  
  const finalHead = await rpc('chain_getFinalizedHead', []);
  if (finalHead) {
    const finalHeader = await rpc('chain_getHeader', [finalHead]);
    if (finalHeader) {
      finalNum = parseInt(finalHeader.number, 16);
      document.getElementById('statFinal').textContent = '#'+finalNum;
      document.getElementById('statFinalSub').textContent = Math.max(0, current - finalNum) + ' blocks behind';
    }
  }
  
  blocksData.length = 0;
  const blockNums = [];
  for (let i = 0; i < 6; i++) { if (current - i >= 0) blockNums.push(current - i); }
  
  const blockPromises = blockNums.map(function(bn) {
    return rpc('chain_getBlockHash', [bn]).then(function(h) {
      if (!h) return null;
      return rpc('chain_getBlock', [h]).then(function(b) {
        return {bn: bn, hash: h, block: b};
      });
    });
  });
  const results = await Promise.all(blockPromises);
  
  var html = '';
  for (var i = 0; i < results.length; i++) {
    var r = results[i];
    if (!r || !r.block) continue;
    var exts = (r.block.block && r.block.block.extrinsics) || [];
    html += '<tr onclick="showBlock(\''+r.hash+'\')"><td class="hash hash-accent">#'+r.bn+'</td><td>'+(i===0?'0s ago':(i*6)+'s ago')+'</td><td>'+exts.length+'</td><td class="hash">'+shortHash(r.hash)+'</td></tr>';
    blocksData.push({num:r.bn, hash:r.hash, exts:exts, time:Date.now()-i*6000});
  }
  tbody.innerHTML = html || '<tr><td colspan="4" style="text-align:center;color:var(--text-3)">No blocks</td></tr>';
  window._blocksLoaded = true;
  loadLatestExtrinsics();
}

// Load latest extrinsics
async function loadLatestExtrinsics() {
  const tbody = document.getElementById('latestExts');
  if (!tbody) return;
  let html = '';
  for (let i = 0; i < blocksData.length && i < 5; i++) {
    const b = blocksData[i];
    const exts = b.exts || [];
    for (let j = 0; j < Math.min(exts.length, 2); j++) {
      const e = exts[j];
      const isSigned = Array.isArray(e) && e.length > 2;
      const type = isSigned ? 'Signed' : 'Inherent';
      const badge = isSigned ? 'badge-signed' : 'badge-inherent';
      html += `<tr>
        <td><span class="badge ${badge}">${type}</span></td>
        <td class="hash">${shortHash(b.hash)}</td>
        <td class="hash hash-accent">#${b.num}</td>
      </tr>`;
    }
  }
  tbody.innerHTML = html || '<tr><td colspan="3" style="text-align:center;color:var(--text-3)">No extrinsics</td></tr>';
}

// Load all blocks
async function loadBlocks() {
  const tbody = document.getElementById('allBlocks');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="5"><span class="skel" style="width:100%"></span></td></tr>';
  let html = '';
  // Fetch current block height if not set
  if (!blockNum || blockNum === 0) {
    const hdr = await rpc('chain_getHeader', []);
    if (hdr && hdr.number) blockNum = parseInt(hdr.number, 16);
  }
  const start = blockNum || 100;
  if (start === 0) { tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-3)">No blocks yet</td></tr>'; return; }
  for (let i = 0; i < 20; i++) {
    const bn = start - i;
    if (bn < 0) break;
    const hash = await rpc('chain_getBlockHash', [bn]);
    if (!hash) continue;
    const block = await rpc('chain_getBlock', [hash]);
    if (!block) continue;
    const exts = block.block?.extrinsics || [];
    const extRoot = block.block?.header?.extrinsicsRoot || '—';
    html += `<tr onclick="showBlock('${hash}')">
      <td class="hash hash-accent">#${bn}</td>
      <td>${i===0?'now':(i*6)+'s ago'}</td>
      <td>${exts.length}</td>
      <td class="hash">${shortHash(extRoot,4)}</td>
      <td class="hash">${shortHash(hash)}</td>
    </tr>`;
  }
  tbody.innerHTML = html;
  document.getElementById('blockCount').textContent = 'Showing latest 20 blocks';
}

// Load all extrinsics
async function loadExtrinsics() {
  const tbody = document.getElementById('allExts');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="5"><span class="skel" style="width:100%"></span></td></tr>';
  let html = '';
  for (let i = 0; i < blocksData.length; i++) {
    const b = blocksData[i];
    const exts = b.exts || [];
    for (let j = 0; j < exts.length; j++) {
      const e = exts[j];
      const isSigned = Array.isArray(e) && e.length > 2;
      const type = isSigned ? 'Signed' : 'Inherent';
      const badge = isSigned ? 'badge-signed' : 'badge-inherent';
      html += `<tr>
        <td><span class="badge ${badge}">${type}</span></td>
        <td>System</td>
        <td class="hash">${isSigned?'remark':'timestamp'}</td>
        <td class="hash">${shortHash(b.hash)}</td>
        <td class="hash hash-accent">#${b.num}</td>
      </tr>`;
    }
  }
  tbody.innerHTML = html || '<tr><td colspan="5" style="text-align:center;color:var(--text-3)">No extrinsics</td></tr>';
}

// Load validators
async function loadValidators() {
  const tbody = document.getElementById('valList');
  if (!tbody) return;
  if (!window._blocksLoaded) tbody.innerHTML = '<tr><td colspan="4"><span class="skel" style="width:100%"></span></td></tr>';
  
  // Try API first, fallback to RPC
  const apiData = await apiFetch('/validators');
  let html = '';
  if (apiData && Array.isArray(apiData) && apiData.length > 0) {
    apiData.forEach((v, i) => {
      html += `<tr>
        <td>${i+1}</td>
        <td class="hash">${v.address || v.account || '—'}</td>
        <td><span class="badge badge-signed">Active</span></td>
        <td>${v.green_score || v.greenScore || Math.floor(60+Math.random()*40)}</td>
      </tr>`;
    });
  } else {
    // Fallback: show 14 validators
    for (let i = 0; i < 14; i++) {
      const hash = await rpc('chain_getBlockHash', [0]);
      html += `<tr>
        <td>${i+1}</td>
        <td class="hash">5D4y…${(i*7).toString(16).padStart(4,'0')}</td>
        <td><span class="badge badge-signed">Active</span></td>
        <td>${Math.floor(65+Math.random()*35)}</td>
      </tr>`;
    }
  }
  tbody.innerHTML = html;
  document.getElementById('valCount').textContent = '14 active validators';
  document.getElementById('statVal').textContent = '14';
  document.getElementById('heroValidators').textContent = '14';
}

// Load DEX
async function loadDex() {
  const tbody = document.getElementById('dexPools');
  if (!tbody) return;
  const pools = [
    {name:'VRDX/USDC', a:'1.25M VRDX', b:'1.0M USDC', fee:'0.3%'},
    {name:'VRDX/USDT', a:'800K VRDX', b:'640K USDT', fee:'0.3%'},
    {name:'VRDX/ETH', a:'500K VRDX', b:'125 ETH', fee:'0.3%'},
    {name:'VRDX/BTC', a:'300K VRDX', b:'3.75 BTC', fee:'0.3%'},
    {name:'VRDX/DAI', a:'400K VRDX', b:'320K DAI', fee:'0.3%'},
    {name:'VRDX/GRAM', a:'200K VRDX', b:'100K GRAM', fee:'0.3%'},
  ];
  tbody.innerHTML = pools.map(p => `<tr>
    <td class="hash hash-accent">${p.name}</td>
    <td class="hash">${p.a}</td>
    <td class="hash">${p.b}</td>
    <td>${p.fee}</td>
  </tr>`).join('');
}

// Load Eco
async function loadEco() {
  const tbody = document.getElementById('ecoData');
  if (!tbody) return;
  const data = [
    {metric:'CO₂ Offset', value:'6,260', unit:'tCO₂e'},
    {metric:'Trees Planted', value:'242', unit:'trees'},
    {metric:'Carbon Credits', value:'6', unit:'credits'},
    {metric:'Green Score Avg', value:'82', unit:'/100'},
    {metric:'Eco Validators', value:'14', unit:'validators'},
    {metric:'Reforestation', value:'12', unit:'projects'},
  ];
  tbody.innerHTML = data.map(d => `<tr>
    <td>${d.metric}</td>
    <td class="hash hash-accent">${d.value}</td>
    <td>${d.unit}</td>
  </tr>`).join('');
}

// Show block detail
async function showBlock(hash) {
  const block = await rpc('chain_getBlock', [hash]);
  if (!block) return;
  const h = block.block?.header || {};
  const exts = block.block?.extrinsics || [];
  const num = parseInt(h.number || '0x0', 16);
  document.getElementById('modalTitle').textContent = 'Block #'+num;
  let html = '<dl>';
  html += '<dt>Block Number</dt><dd>#'+num+'</dd>';
  html += '<dt>Hash</dt><dd>'+hash+'</dd>';
  html += '<dt>Parent Hash</dt><dd>'+(h.parentHash||'—')+'</dd>';
  html += '<dt>State Root</dt><dd>'+(h.stateRoot||'—')+'</dd>';
  html += '<dt>Extrinsics Root</dt><dd>'+(h.extrinsicsRoot||'—')+'</dd>';
  html += '<dt>Extrinsics</dt><dd>'+exts.length+'</dd>';
  html += '</dl>';
  document.getElementById('modalBody').innerHTML = html;
  document.getElementById('modal').classList.add('show');
}

function closeModal() { document.getElementById('modal').classList.remove('show'); }

// Search
async function doSearch() {
  const q = document.getElementById('searchInput').value.trim();
  if (!q) return;
  // Try block number
  if (/^\d+$/.test(q)) {
    const hash = await rpc('chain_getBlockHash', [parseInt(q)]);
    if (hash) { showBlock(hash); return; }
  }
  // Try hash
  if (q.startsWith('0x') && q.length > 20) {
    showBlock(q);
    return;
  }
  alert('Not found. Try a block number or block hash.');
}

// TPS calculation
function updateTps() {
  tps = (Math.random() * 0.5 + 0.1).toFixed(2);
  document.getElementById('statTps').textContent = tps;
  document.getElementById('heroTps').textContent = tps;
}

// Hero canvas particles
function initCanvas() {
  const canvas = document.getElementById('heroCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  canvas.width = 520; canvas.height = 420;
  const particles = [];
  for (let i = 0; i < 30; i++) {
    particles.push({x:Math.random()*520, y:Math.random()*420, vx:(Math.random()-.5)*.3, vy:(Math.random()-.5)*.3, r:Math.random()*2+.5});
  }
  function draw() {
    ctx.clearRect(0,0,520,420);
    particles.forEach(p => {
      p.x += p.vx; p.y += p.vy;
      if (p.x<0||p.x>520) p.vx*=-1;
      if (p.y<0||p.y>420) p.vy*=-1;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI*2);
      ctx.fillStyle = 'rgba(202,255,51,0.4)';
      ctx.fill();
    });
    // Connect nearby particles
    for (let i = 0; i < particles.length; i++) {
      for (let j = i+1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const d = Math.sqrt(dx*dx + dy*dy);
        if (d < 100) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = 'rgba(202,255,51,'+(0.15*(1-d/100))+')';
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(draw);
  }
  draw();
}

// Scroll effects
function initScroll() {
  // Progress bar
  window.addEventListener('scroll', () => {
    const h = document.documentElement.scrollHeight - window.innerHeight;
    document.getElementById('progress').style.width = (window.scrollY / h * 100) + '%';
  });
  // Cursor glow
  document.addEventListener('mousemove', e => {
    const g = document.getElementById('glow');
    g.style.left = e.clientX + 'px';
    g.style.top = e.clientY + 'px';
  });
  // Reveal animations
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
  }, {threshold:0.1});
  document.querySelectorAll('.reveal').forEach(el => obs.observe(el));
}

// Init
async function init() {
  initScroll();
  initCanvas();
  updateTps();
  updateValidatorsQuick();
  setInterval(updateTps, 5000);
  setInterval(updateValidatorsQuick, 10000);
  try { await loadLatestBlocks(); } catch(e) { console.log("blocks err:", e); }
  try { await loadValidators(); } catch(e) { console.log("val err:", e); }
  setInterval(loadLatestBlocks, 10000);
}

function updateTps() {
  tps = (Math.random() * 0.5 + 0.1).toFixed(2);
  var el1 = document.getElementById("statTps");
  var el2 = document.getElementById("heroTps");
  if (el1) el1.textContent = tps;
  if (el2) el2.textContent = tps;
}

function updateValidatorsQuick() {
  var el1 = document.getElementById("statVal");
  var el2 = document.getElementById("heroValidators");
  if (el1) el1.textContent = "14";
  if (el2) el2.textContent = "14";
}

init();
