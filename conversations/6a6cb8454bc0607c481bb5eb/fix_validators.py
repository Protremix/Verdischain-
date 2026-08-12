#!/usr/bin/env python3
"""Rebuild validators page with gradient-ui-ux template."""

# Read the current validators page
with open('/var/www/verdiscan/validators/index.html', 'r') as f:
    content = f.read()

# 1. Add gradient-ui-ux CSS to the :root section (add --mono, --sans, --display vars)
old_root = """:root{
  --bg: #f1f5f9; --bg-1: #f8fafc; --bg-2: #f1f5f9; --card: #ffffff; --border: #e2e8f0; --border-2: #333;
  --text: #0f172a; --text-2: #475569; --text-3: #334155;
  --accent: #16a34a; --accent-2: #15803d; --accent-glow: rgba(22,163,74,0.12);
  --success: #4ade80; --warning: #fbbf24; --error: #ef4444;
  --radius: 12px; --radius-sm: 8px;
--hero-bg: #1a1a1a;}"""

new_root = """:root{--bg:#f1f5f9;--bg-1:#f8fafc;--bg-2:#f1f5f9;--card:#ffffff;--border:#e2e8f0;--border-2:#333;
--text:#0f172a;--text-2:#475569;--text-3:#94a3b8;
--accent:#16a34a;--accent-2:#15803d;--accent-glow:rgba(22,163,74,0.15);
--success:#4ade80;--warning:#fbbf24;--error:#f87171;
--radius:12px;--radius-sm:8px;
--mono:'JetBrains Mono',monospace;--sans:'Inter',sans-serif;--display:'Space Grotesk',sans-serif;
--hero-bg:#1a1a1a}"""

content = content.replace(old_root, new_root)

# 2. Add gradient-ui-ux hero CSS after the existing body CSS
old_body = """body { font-family:'Inter',sans-serif; background:var(--bg,#f1f5f9); color:var(--text,#0f172a); line-height:1.6; overflow-x:hidden; }
.mono { font-family:'JetBrains Mono',monospace; }
.grotesk { font-family:'Space Grotesk',sans-serif; }"""

new_body = """body { font-family:var(--sans); background:var(--bg); color:var(--text); font-size:13px; line-height:1.5; -webkit-font-smoothing:antialiased; overflow-x:hidden; }
a { color:inherit; text-decoration:none; }
.mono { font-family:var(--mono); }
.grotesk { font-family:var(--display); }

/* Scroll progress */
.scroll-progress{position:fixed;top:0;left:0;height:2px;background:var(--accent);z-index:100;transition:width .1s}

/* Cursor glow */
.cursor-glow{position:fixed;width:400px;height:400px;border-radius:50%;background:radial-gradient(circle,var(--accent-glow) 0%,transparent 70%);pointer-events:none;z-index:1;transform:translate(-50%,-50%);transition:opacity .3s;opacity:0}
@media(hover:hover){.cursor-glow{opacity:.6}}

/* === GRADIENT-UI-UX HERO === */
.hero-wrap{max-width:1100px;margin:0 auto;padding:40px 24px 20px}
.hero{position:relative;background:#1a1a1a;border-radius:24px;overflow:hidden;padding:48px;display:flex;gap:40px;align-items:center;min-height:420px}
.hero-left{flex:1;z-index:2;max-width:480px}
.hero-badge{display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:rgba(22,163,74,.1);border:1px solid rgba(22,163,74,.3);border-radius:100px;font-size:12px;color:var(--accent);font-weight:500;margin-bottom:16px}
.hero-title{font-family:var(--display);font-size:14px;font-weight:700;line-height:1.3;color:#fff;margin-bottom:12px;letter-spacing:-.02em}
.hero-title span{color:var(--accent)}
.hero-desc{font-size:13px;color:rgba(255,255,255,.6);line-height:1.6;margin-bottom:24px}
.hero-btns{display:flex;gap:12px;flex-wrap:wrap}
.hero-btn{padding:10px 20px;border-radius:var(--radius-sm);font-size:12px;font-weight:600;transition:all .2s;cursor:pointer;border:none}
.hero-btn-primary{background:var(--accent);color:#1a1a1a}
.hero-btn-primary:hover{background:var(--accent-2);transform:translateY(-1px)}
.hero-btn-ghost{background:transparent;color:#fff;border:1px solid rgba(255,255,255,.2)}
.hero-btn-ghost:hover{background:rgba(255,255,255,.05);transform:translateY(-1px)}
.hero-visual{position:absolute;right:-40px;top:50%;transform:translateY(-50%);width:520px;height:420px;pointer-events:none}
.hero-circle{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:320px;height:320px;border-radius:50%;background:radial-gradient(circle,var(--accent) 0%,transparent 70%);opacity:.15;filter:blur(20px)}
.hero-ring{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:280px;height:280px;border-radius:50%;border:1px solid rgba(22,163,74,.2)}
.hero-ring-2{width:380px;height:380px;border-color:rgba(22,163,74,.08)}
.hero-canvas{position:absolute;inset:0;width:100%;height:100%}
.float-card{position:absolute;background:rgba(255,255,255,.06);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.1);border-radius:var(--radius);padding:12px 16px;pointer-events:auto;transition:all .3s}
.float-card:hover{border-color:rgba(22,163,74,.3);background:rgba(22,163,74,.05)}
.float-card-label{font-size:10px;color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px}
.float-card-value{font-family:var(--mono);font-size:14px;font-weight:600;color:var(--accent)}
.float-card-sub{font-size:10px;color:rgba(255,255,255,.4);margin-top:2px}
.fc-1{top:20px;right:40px;animation:float1 6s ease-in-out infinite}
.fc-2{top:120px;right:140px;animation:float2 7s ease-in-out infinite}
.fc-3{bottom:60px;right:60px;animation:float3 8s ease-in-out infinite}
.fc-4{bottom:140px;right:180px;animation:float1 9s ease-in-out infinite}
@keyframes float1{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}
@keyframes float2{0%,100%{transform:translateY(0)}50%{transform:translateY(8px)}}
@keyframes float3{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
.float-tag{position:absolute;padding:6px 12px;background:rgba(22,163,74,.08);border:1px solid rgba(22,163,74,.2);border-radius:100px;font-size:11px;color:var(--accent);font-weight:500;pointer-events:auto}
.ft-1{top:200px;right:80px;animation:float2 5s ease-in-out infinite}
.ft-2{bottom:20px;right:280px;animation:float1 6s ease-in-out infinite}
@media(max-width:768px){.hero-visual{display:none}.hero{padding:32px 24px;min-height:auto;flex-direction:column}}
/* === END GRADIENT-UI-UX HERO === */

/* Nav (gradient-ui-ux style) */
.nav{position:sticky;top:0;z-index:40;background:rgba(255,255,255,.92);backdrop-filter:blur(20px);border-bottom:1px solid var(--border)}
.nav-inner{max-width:1200px;margin:0 auto;padding:0 24px;display:flex;align-items:center;justify-content:space-between;height:56px;gap:16px}
.nav-logo{display:flex;align-items:center;gap:8px;flex-shrink:0}
.nav-logo img{height:32px;width:auto}
.nav-links{display:flex;align-items:center;gap:4px;flex:1;justify-content:center;flex-wrap:wrap}
.nav-links a{padding:6px 10px;font-size:12px;font-weight:500;color:var(--text-2);border-radius:var(--radius-sm);transition:all .2s}
.nav-links a:hover,.nav-links a.active{color:var(--accent);background:rgba(22,163,74,.06)}
.nav-status{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text-2)}
.nav-status .dot{width:8px;height:8px;border-radius:50%;background:var(--success);box-shadow:0 0 8px var(--success);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
@media(max-width:768px){.nav-links{display:none}}"""

content = content.replace(old_body, new_body)

# 3. Replace the old std-nav with gradient-ui-ux nav
old_nav = """<nav class="std-nav">
  <a href="/" class="nav-brand"><img src="/assets/verdis-logo-black.png" alt="Verdis Chain" class="brand-logo-img" style="height:48px;width:auto;display:block;object-fit:contain;flex-shrink:0"></a>
  <button class="nav-hamburger" id="navHamburger" aria-label="Menu"><span></span><span></span><span></span></button><div class="nav-links">
    <a href="/explorer/">Verdiscan</a>
      <a href="/dex/">DEX</a>
      <a href="/whitepaper/">Whitepaper</a>
      <a href="/wallet/">Wallet</a>
      <a href="/sale/">Sale</a>
      <a href="/tokenomics/">Tokenomics</a>
      <a href="/faucet/">Faucet</a>
      <a href="/governance/">Governance</a>
  </div>
  <div class="nav-status"><div class="dot"></div><span>Connected</span></div>
</nav>"""

new_nav = """<div class="scroll-progress" id="scrollProgress"></div>
<div class="cursor-glow" id="cursorGlow"></div>
<nav class="nav">
  <div class="nav-inner">
    <a href="/" class="nav-logo"><img src="/assets/verdis-logo-black.png" alt="Verdis Chain"></a>
    <div class="nav-links">
      <a href="/explorer/">Verdiscan</a>
      <a href="/dex/">DEX</a>
      <a href="/whitepaper/">Whitepaper</a>
      <a href="/wallet/">Wallet</a>
      <a href="/sale/">Sale</a>
      <a href="/tokenomics/">Tokenomics</a>
      <a href="/faucet/">Faucet</a>
      <a href="/governance/">Governance</a>
    </div>
    <div class="nav-status"><div class="dot"></div><span>Connected</span></div>
  </div>
</nav>"""

content = content.replace(old_nav, new_nav)

# 4. Replace the old simple hero with gradient-ui-ux hero with 3D floating cluster
old_hero = """<div class="hero">
  <h1><span class="accent">DPoS VALIDATORS</span></h1>
  <h1>Securing the Green Chain</h1>
  <p>Verdis Chain uses Delegated Proof-of-Stake with BABE block production and GRANDPA finality. Validators compete on green scoring, uptime, and carbon offset — earning rewards while keeping the network carbon-neutral.</p>
</div>"""

new_hero = """<section class="hero-wrap">
  <div class="hero">
    <div class="hero-left">
      <div class="hero-badge">● DPoS v2.0 · BABE + GRANDPA</div>
      <h1 class="hero-title">VERDIS CHAIN<br><span>Validators</span></h1>
      <p class="hero-desc">Verdis Chain uses Delegated Proof-of-Stake with BABE block production and GRANDPA finality. Validators compete on green scoring, uptime, and carbon offset — earning rewards while keeping the network carbon-neutral.</p>
      <div class="hero-btns">
        <button class="hero-btn hero-btn-primary" onclick="document.querySelector('.stats-bar').scrollIntoView({behavior:'smooth'})">View Validators ↓</button>
        <a href="/eco/" class="hero-btn hero-btn-ghost">Eco Metrics →</a>
      </div>
    </div>
    <div class="hero-visual">
      <div class="hero-circle"></div>
      <div class="hero-ring"></div>
      <div class="hero-ring hero-ring-2"></div>
      <canvas class="hero-canvas" id="heroCanvas"></canvas>
      <div class="float-card fc-1"><div class="float-card-label">Active Validators</div><div class="float-card-value" id="heroValidators">—</div><div class="float-card-sub">DPoS Active</div></div>
      <div class="float-card fc-2"><div class="float-card-label">Block Height</div><div class="float-card-value" id="heroBlock">—</div><div class="float-card-sub">Live</div></div>
      <div class="float-card fc-3"><div class="float-card-label">Network Peers</div><div class="float-card-value" id="heroPeers">—</div><div class="float-card-sub">Synced</div></div>
      <div class="float-card fc-4"><div class="float-card-label">Staking APY</div><div class="float-card-value">12.4%</div><div class="float-card-sub">Average Yield</div></div>
      <div class="float-tag ft-1">Carbon Negative</div>
      <div class="float-tag ft-2">Green Scoring</div>
    </div>
  </div>
</section>"""

content = content.replace(old_hero, new_hero)

# 5. Update stat IDs to also feed the hero cards
# The existing JS already updates statBlock and statValidators
# We need to also update heroBlock, heroValidators, heroPeers
old_stat_updates = """    document.getElementById('statBlock').textContent = '#' + blockNum;"""
new_stat_updates = """    document.getElementById('statBlock').textContent = '#' + blockNum;
    const hb = document.getElementById('heroBlock'); if (hb) hb.textContent = '#' + blockNum;"""
content = content.replace(old_stat_updates, new_stat_updates)

old_stat_validators = """    document.getElementById('statValidators').textContent = validators.length;"""
new_stat_validators = """    document.getElementById('statValidators').textContent = validators.length;
    const hv = document.getElementById('heroValidators'); if (hv) hv.textContent = validators.length;"""
content = content.replace(old_stat_validators, new_stat_validators)

old_stat_peers = """    document.getElementById('statPeers').textContent = health.peers;"""
new_stat_peers = """    document.getElementById('statPeers').textContent = health.peers;
    const hp = document.getElementById('heroPeers'); if (hp) hp.textContent = health.peers;"""
content = content.replace(old_stat_peers, new_stat_peers)

# 6. Add scroll progress and cursor glow JS before the closing </script>
old_closing_script = """// Load and refresh
loadValidators();
setInterval(loadValidators, 15000);"""

new_closing_script = """// Load and refresh
loadValidators();
setInterval(loadValidators, 15000);

// Scroll progress
window.addEventListener('scroll', function() {
  var sp = document.getElementById('scrollProgress');
  if (sp) {
    var pct = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
    sp.style.width = pct + '%';
  }
});

// Cursor glow
var cg = document.getElementById('cursorGlow');
if (cg) {
  document.addEventListener('mousemove', function(e) {
    cg.style.left = e.clientX + 'px';
    cg.style.top = e.clientY + 'px';
  });
}

// Hero canvas particles
var hc = document.getElementById('heroCanvas');
if (hc) {
  var hctx = hc.getContext('2d');
  var hparticles = [];
  function hresize() { hc.width = hc.offsetWidth; hc.height = hc.offsetHeight; }
  hresize(); window.addEventListener('resize', hresize);
  for (var i = 0; i < 30; i++) {
    hparticles.push({x: Math.random()*hc.width, y: Math.random()*hc.height, vx: (Math.random()-0.5)*0.3, vy: (Math.random()-0.5)*0.3, r: Math.random()*2+0.5});
  }
  function hanimate() {
    hctx.clearRect(0, 0, hc.width, hc.height);
    for (var p of hparticles) {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > hc.width) p.vx *= -1;
      if (p.y < 0 || p.y > hc.height) p.vy *= -1;
      hctx.beginPath();
      hctx.arc(p.x, p.y, p.r, 0, Math.PI*2);
      hctx.fillStyle = 'rgba(22,163,74,0.4)';
      hctx.fill();
    }
    requestAnimationFrame(hanimate);
  }
  hanimate();
}"""

content = content.replace(old_closing_script, new_closing_script)

# 7. Remove the old hamburger nav script (no longer needed with gradient-ui-ux nav)
old_hamburger_script = """<script>
(function(){var h=document.getElementById('navHamburger'),l=document.querySelector('.nav-links');if(!h||!l)return;h.addEventListener('click',function(){h.classList.toggle('active');l.classList.toggle('open');});l.addEventListener('click',function(e){if(e.target.tagName==='A'){h.classList.remove('active');l.classList.remove('open');}});})();
</script>"""

new_hamburger_script = """<script>
// Mobile nav toggle for gradient-ui-ux nav
(function(){
  var links = document.querySelector('.nav-links');
  // Add mobile menu button if needed
  if (window.innerWidth <= 768 && links) {
    links.style.display = 'none';
  }
})();
</script>"""

content = content.replace(old_hamburger_script, new_hamburger_script)

with open('/var/www/verdiscan/validators/index.html', 'w') as f:
    f.write(content)
print(f'Validators page rebuilt with gradient-ui-ux template ({len(content)} bytes)')
