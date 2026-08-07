import re

file_path = "/app/conversations/6a6cb8454bc0607c481bb5eb/verdis-landing.html"

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Global color replacements
text = text.replace("#b4f849", "#caff33")
text = text.replace("#0f0f0f", "#1a1a1a")
text = text.replace("#1e1e1e", "#2d2d2d")
text = text.replace("#181818", "#252525")
text = text.replace("#a3e041", "#a8e607")
text = text.replace("180,248,73", "202,255,51")

# 2. CSS Replacement for Hero
new_hero_css = """/* ===== HERO SECTION — Dark container, split layout ===== */
    .hero-section { position: relative; background: var(--canvas); padding: 0 24px; overflow: hidden; }
    .hero-container { max-width: 1300px; margin: 0 auto; background: var(--hero-bg); border-radius: 24px; overflow: hidden; position: relative; min-height: 700px; display: flex; }
    .hero-container::before { content: ''; position: absolute; top: -30%; right: -15%; width: 700px; height: 700px; background: radial-gradient(circle, var(--accent-glow), transparent 55%); opacity: 0.12; animation: pulse-bg 4s ease-in-out infinite; pointer-events: none; }
    .hero-container::after { content: ''; position: absolute; bottom: -20%; left: -10%; width: 500px; height: 500px; background: radial-gradient(circle, rgba(0,168,107,0.15), transparent 60%); opacity: 0.08; animation: pulse-bg 6s ease-in-out infinite 1s; pointer-events: none; }
    @keyframes pulse-bg { 0%,100% { opacity: 0.08; transform: scale(1); } 50% { opacity: 0.15; transform: scale(1.1); } }

    /* ===== NAV ===== */
    .hero-nav { position: absolute; top: 0; left: 0; right: 0; z-index: 20; display: flex; align-items: center; justify-content: space-between; padding: 28px 48px; }
    .nav-brand { font-family: 'Poppins'; font-weight: 800; font-size: 22px; color: var(--text-white); display: flex; align-items: center; gap: 10px; }
    .nav-brand-dot { width: 12px; height: 12px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 16px var(--accent-glow); animation: pulse-dot 2s infinite; }
    @keyframes pulse-dot { 0%,100% { box-shadow: 0 0 16px var(--accent-glow); } 50% { box-shadow: 0 0 28px rgba(202,255,51,0.6); } }
    .nav-links { display: flex; gap: 36px; }
    .nav-links a { color: var(--text-dim); font-size: 14px; font-weight: 500; transition: color 250ms; position: relative; text-decoration: none; }
    .nav-links a::after { content: ''; position: absolute; bottom: -4px; left: 0; width: 0; height: 2px; background: var(--accent); border-radius: 2px; transition: width 250ms; }
    .nav-links a:hover { color: var(--text-white); }
    .nav-links a:hover::after { width: 100%; }
    .nav-cta { display: flex; gap: 12px; align-items: center; }
    .btn-login { color: var(--text-dim); font-size: 14px; font-weight: 500; padding: 8px 16px; transition: color 250ms; background: none; border: none; cursor: pointer; }
    .btn-login:hover { color: var(--text-white); }
    .btn-signup { background: var(--accent); color: var(--hero-bg); font-size: 14px; font-weight: 600; padding: 10px 24px; border-radius: var(--radius-pill); border: none; cursor: pointer; transition: var(--transition); position: relative; overflow: hidden; }
    .btn-signup::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent); transition: left 500ms; }
    .btn-signup:hover::before { left: 100%; }
    .btn-signup:hover { transform: translateY(-2px); box-shadow: 0 8px 24px var(--accent-glow); }

    /* ===== HERO LEFT ===== */
    .hero-left { flex: 1; display: flex; flex-direction: column; justify-content: center; padding: 120px 56px 60px 56px; position: relative; z-index: 5; }
    .hero-badge { display: inline-flex; align-items: center; gap: 8px; padding: 6px 16px; background: var(--accent-light); border: 1px solid var(--accent-border); border-radius: var(--radius-pill); font-size: 13px; font-weight: 600; color: var(--accent); margin-bottom: 28px; width: fit-content; opacity: 0; transform: translateY(20px); animation: slideUp 600ms 200ms forwards; }
    .hero-badge-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent); animation: pulse-dot 2s infinite; }
    .hero-title { font-size: 52px; font-weight: 900; line-height: 1.05; color: var(--text-white); margin-bottom: 24px; letter-spacing: -0.02em; opacity: 0; transform: translateY(30px); animation: slideUp 800ms 400ms forwards; }
    .hero-title .gradient { background: linear-gradient(135deg, #caff33 0%, #a8e607 50%, #00a86b 100%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
    .hero-desc { font-size: 16px; color: var(--text-dim); line-height: 1.8; margin-bottom: 36px; max-width: 500px; opacity: 0; transform: translateY(20px); animation: slideUp 800ms 600ms forwards; }
    .hero-actions { display: flex; gap: 16px; opacity: 0; transform: translateY(20px); animation: slideUp 800ms 800ms forwards; }
    .btn-primary { background: linear-gradient(135deg, #caff33, #a8e607); color: var(--hero-bg); font-size: 15px; font-weight: 700; padding: 14px 32px; border-radius: var(--radius-pill); border: none; cursor: pointer; transition: var(--transition); position: relative; overflow: hidden; display: inline-flex; align-items: center; gap: 8px; }
    .btn-primary::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent); transition: left 500ms; }
    .btn-primary:hover::before { left: 100%; }
    .btn-primary:hover { transform: translateY(-3px); box-shadow: 0 12px 32px var(--accent-glow); }
    .btn-secondary { background: transparent; color: var(--text-white); font-size: 15px; font-weight: 600; padding: 14px 32px; border-radius: var(--radius-pill); border: 1px solid rgba(255,255,255,0.15); cursor: pointer; transition: var(--transition); }
    .btn-secondary:hover { border-color: var(--accent); background: var(--accent-light); color: var(--accent); }
    @keyframes slideUp { to { opacity: 1; transform: translateY(0); } }

    /* ===== HERO RIGHT — 3D Floating Cluster Visual ===== */
    .hero-right {
      flex: 1.15;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 40px 20px;
      min-height: 640px;
    }
    .hero-visual {
      position: relative;
      width: 100%;
      max-width: 620px;
      height: 580px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    #hero-canvas {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 2;
      pointer-events: none;
    }

    /* Lime Green Circle Backdrop */
    .hero-lime-circle {
      position: absolute;
      width: 420px;
      height: 420px;
      border-radius: 50%;
      background: radial-gradient(circle at 35% 35%, #caff33 0%, #a8e607 65%, #88be00 100%);
      box-shadow: 0 0 100px rgba(202, 255, 51, 0.45);
      z-index: 1;
    }

    /* Glassmorphism Common Styles */
    .dex-chart-card,
    .calendar-widget,
    .monitor-frame,
    .mobile-phone-mockup,
    .q-card,
    .v-btn,
    .float-tag {
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.14);
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    }

    /* Float Animations */
    .float-anim-1 { animation: float1 5.5s ease-in-out infinite; }
    .float-anim-2 { animation: float2 7s ease-in-out infinite; }
    .float-anim-3 { animation: float3 6s ease-in-out infinite; }
    .float-anim-4 { animation: float4 5s ease-in-out infinite; }
    .float-anim-5 { animation: float5 6.5s ease-in-out infinite; }
    .float-anim-6 { animation: float6 6s ease-in-out infinite; }

    .float-tag-1 { animation: floatTag1 4s ease-in-out infinite; }
    .float-tag-2 { animation: floatTag2 5s ease-in-out infinite; }
    .float-tag-3 { animation: floatTag3 6s ease-in-out infinite; }
    .float-tag-4 { animation: floatTag4 4.5s ease-in-out infinite; }

    @keyframes float1 { 0%,100% { transform: translateY(0px) rotate(-1.5deg); } 50% { transform: translateY(-14px) rotate(1deg); } }
    @keyframes float2 { 0%,100% { transform: translateY(0px) rotate(2deg); } 50% { transform: translateY(-12px) rotate(-1deg); } }
    @keyframes float3 { 0%,100% { transform: translateY(0px) rotate(-1deg); } 50% { transform: translateY(-16px) rotate(1deg); } }
    @keyframes float4 { 0%,100% { transform: translateY(0px) rotate(2deg) scale(1); } 50% { transform: translateY(-18px) rotate(-1deg) scale(1.02); } }
    @keyframes float5 { 0%,100% { transform: translateY(0px) rotate(1deg); } 50% { transform: translateY(-10px) rotate(-1.5deg); } }
    @keyframes float6 { 0%,100% { transform: translateY(0px) rotate(-1deg); } 50% { transform: translateY(-12px) rotate(1deg); } }

    @keyframes floatTag1 { 0%,100% { transform: translate(0, 0) rotate(-3deg); } 50% { transform: translate(6px, -10px) rotate(2deg); } }
    @keyframes floatTag2 { 0%,100% { transform: translate(0, 0) rotate(2deg); } 50% { transform: translate(-8px, 12px) rotate(-2deg); } }
    @keyframes floatTag3 { 0%,100% { transform: translate(0, 0) rotate(-2deg); } 50% { transform: translate(8px, -8px) rotate(3deg); } }
    @keyframes floatTag4 { 0%,100% { transform: translate(0, 0) rotate(3deg); } 50% { transform: translate(-6px, 10px) rotate(-2deg); } }

    /* 1. DEX Volume Chart Card (Top Left) */
    .dex-chart-card {
      position: absolute;
      top: 2%;
      left: 6%;
      width: 185px;
      background: rgba(45, 45, 45, 0.85);
      border-radius: 18px;
      padding: 14px 16px;
      z-index: 9;
    }
    .dex-card-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
    .dex-play-icon { width: 22px; height: 22px; border-radius: 50%; background: #caff33; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 10px rgba(202,255,51,0.5); }
    .dex-card-title { font-size: 11px; font-weight: 600; color: #ffffff; flex: 1; }
    .dex-badge { font-size: 10px; font-weight: 700; color: #caff33; background: rgba(202,255,51,0.15); padding: 2px 6px; border-radius: 100px; }
    .dex-val-row { display: flex; align-items: baseline; gap: 6px; margin-bottom: 10px; }
    .dex-value { font-size: 18px; font-weight: 800; color: #caff33; }
    .dex-sub { font-size: 10px; color: #b8bcc4; }
    .dex-bars { display: flex; align-items: flex-end; gap: 4px; height: 32px; }
    .dex-bar { flex: 1; height: var(--h); background: linear-gradient(to top, #caff33, #a8e607); border-radius: 3px; }

    /* 2. Calendar Widget - Validator Schedule (Top Right) */
    .calendar-widget {
      position: absolute;
      top: 4%;
      right: 6%;
      width: 190px;
      background: rgba(45, 45, 45, 0.85);
      border-radius: 18px;
      padding: 14px;
      z-index: 8;
    }
    .cal-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
    .cal-title { font-size: 12px; font-weight: 700; color: #ffffff; }
    .cal-badge { font-size: 10px; font-weight: 600; color: #caff33; background: rgba(202,255,51,0.15); padding: 2px 8px; border-radius: 100px; }
    .cal-weekdays { display: grid; grid-template-columns: repeat(7, 1fr); text-align: center; font-size: 9px; font-weight: 600; color: #b8bcc4; margin-bottom: 6px; }
    .cal-days { display: grid; grid-template-columns: repeat(7, 1fr); text-align: center; gap: 3px; font-size: 10px; color: #ffffff; }
    .cal-days span { padding: 3px 0; border-radius: 6px; font-size: 10px; }
    .cal-days span.muted { color: rgba(255,255,255,0.2); }
    .cal-days span.active { background: #caff33; color: #1a1a1a; font-weight: 800; box-shadow: 0 0 8px rgba(202,255,51,0.6); }
    .cal-footer { font-size: 10px; color: #b8bcc4; margin-top: 10px; display: flex; align-items: center; gap: 6px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 8px; }
    .cal-footer-dot { width: 6px; height: 6px; border-radius: 50%; background: #caff33; }

    /* 3. Blockchain Dashboard Monitor Frame (Center) */
    .monitor-frame {
      position: absolute;
      top: 20%;
      left: 18%;
      width: 350px;
      background: rgba(45, 45, 45, 0.88);
      border-radius: 18px;
      overflow: hidden;
      z-index: 4;
    }
    .monitor-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; background: rgba(30, 30, 30, 0.6); border-bottom: 1px solid rgba(255,255,255,0.08); }
    .win-controls { display: flex; gap: 6px; }
    .win-dot { width: 10px; height: 10px; border-radius: 50%; }
    .win-dot.red { background: #ff5f56; }
    .win-dot.yellow { background: #ffbd2e; }
    .win-dot.green { background: #caff33; }
    .monitor-title { font-size: 11px; color: #b8bcc4; font-weight: 500; }
    .monitor-status { font-size: 10px; font-weight: 700; color: #caff33; display: flex; align-items: center; gap: 4px; }
    .status-dot { width: 6px; height: 6px; border-radius: 50%; background: #caff33; box-shadow: 0 0 8px #caff33; }
    .monitor-body { padding: 14px 16px; display: flex; flex-direction: column; gap: 12px; }
    .monitor-metrics { display: flex; justify-content: space-between; gap: 8px; }
    .m-stat { display: flex; flex-direction: column; gap: 2px; }
    .m-lbl { font-size: 10px; color: #b8bcc4; }
    .m-val { font-size: 14px; font-weight: 700; color: #ffffff; }
    .m-val.green { color: #caff33; }
    .monitor-graph { width: 100%; height: 60px; background: rgba(20, 20, 20, 0.4); border-radius: 8px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05); }
    .monitor-log { font-size: 10px; color: #b8bcc4; background: rgba(0,0,0,0.2); padding: 6px 10px; border-radius: 6px; border-left: 2px solid #caff33; }

    /* 4. VRD Wallet Mobile Phone Mockup (Center-Left) */
    .mobile-phone-mockup {
      position: absolute;
      top: 18%;
      left: 0%;
      width: 195px;
      background: rgba(35, 35, 35, 0.92);
      border-radius: 30px;
      padding: 12px;
      z-index: 10;
    }
    .phone-notch { width: 60px; height: 12px; background: #1a1a1a; border-radius: 0 0 10px 10px; margin: -12px auto 8px auto; }
    .phone-screen { display: flex; flex-direction: column; gap: 10px; }
    .phone-status { display: flex; justify-content: space-between; align-items: center; font-size: 10px; color: #b8bcc4; font-weight: 600; padding: 0 4px; }
    .phone-icons { display: flex; align-items: center; gap: 4px; }
    .phone-profile { display: flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.04); padding: 8px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); }
    .profile-avatar { width: 28px; height: 28px; border-radius: 50%; background: rgba(202,255,51,0.15); border: 1px solid #caff33; display: flex; align-items: center; justify-content: center; }
    .profile-info { flex: 1; }
    .profile-name { font-size: 11px; font-weight: 700; color: #ffffff; line-height: 1.1; }
    .profile-address { font-size: 9px; color: #b8bcc4; }
    .phone-login-badge { font-size: 8px; font-weight: 800; color: #1a1a1a; background: #caff33; padding: 2px 6px; border-radius: 100px; }
    .phone-balance-card { background: linear-gradient(135deg, rgba(202,255,51,0.12), rgba(45,45,45,0.6)); padding: 10px; border-radius: 14px; border: 1px solid rgba(202,255,51,0.2); }
    .p-bal-lbl { font-size: 9px; color: #b8bcc4; font-weight: 500; }
    .p-bal-val { font-size: 18px; font-weight: 800; color: #caff33; margin: 2px 0; }
    .p-bal-sub { font-size: 9px; color: #b8bcc4; }
    .p-up { color: #caff33; font-weight: 700; }
    
    /* Circular Progress Ring */
    .phone-staking-ring {
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 6px 0;
    }
    .ring-label {
      position: absolute;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .ring-pct { font-size: 14px; font-weight: 800; color: #caff33; line-height: 1; }
    .ring-txt { font-size: 8px; color: #b8bcc4; font-weight: 600; text-transform: uppercase; }

    .phone-actions { display: flex; gap: 6px; }
    .p-btn { flex: 1; padding: 7px 0; border-radius: 8px; font-size: 10px; font-weight: 700; border: none; cursor: pointer; }
    .p-btn.primary { background: linear-gradient(135deg, #caff33, #a8e607); color: #1a1a1a; }
    .p-btn.outline { background: rgba(255,255,255,0.06); color: #ffffff; border: 1px solid rgba(255,255,255,0.1); }

    /* 5. Quick Stats Grid (Bottom Left) */
    .stats-grid-4 {
      position: absolute;
      bottom: 2%;
      left: 6%;
      width: 220px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      z-index: 9;
    }
    .q-card {
      background: rgba(45, 45, 45, 0.85);
      border-radius: 14px;
      padding: 10px 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .q-icon { width: 26px; height: 26px; border-radius: 8px; background: rgba(202,255,51,0.15); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
    .q-lbl { font-size: 9px; color: #b8bcc4; }
    .q-val { font-size: 11px; font-weight: 700; color: #ffffff; }
    .q-val.green { color: #caff33; }

    /* 6. Vertical Action Stack (Far Right) */
    .vertical-action-stack {
      position: absolute;
      top: 24%;
      right: 2%;
      display: flex;
      flex-direction: column;
      gap: 10px;
      z-index: 10;
    }
    .v-btn {
      width: 44px;
      height: 44px;
      border-radius: 14px;
      background: rgba(45, 45, 45, 0.85);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 250ms ease;
    }
    .v-btn:hover {
      background: #caff33;
      transform: scale(1.1);
      box-shadow: 0 0 20px rgba(202, 255, 51, 0.6);
    }
    .v-btn:hover svg { stroke: #1a1a1a; }

    /* 7. Floating Tags */
    .float-tag {
      position: absolute;
      padding: 5px 12px;
      border-radius: 100px;
      background: rgba(202, 255, 51, 0.15);
      border: 1px solid rgba(202, 255, 51, 0.4);
      color: #caff33;
      font-size: 10px;
      font-weight: 700;
      z-index: 11;
      box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    .tag-staking { top: 0%; right: 28%; }
    .tag-swap { bottom: 10%; right: 18%; }
    .tag-vrd { top: 38%; left: -4%; }
    .tag-carbon { bottom: 2%; right: 38%; }"""

# Replace CSS block in <style>
old_css_pattern = r"/\* ===== HERO SECTION — Dark container, split layout ===== \*/.*?(?=/\* ===== STATS BAR ===== \*/)"
text = re.sub(old_css_pattern, new_hero_css + "\n\n    ", text, flags=re.DOTALL)

# 3. HTML Replacement for Hero Section
new_hero_html = """<section class="hero-section">
    <div class="hero-container">
      <nav class="hero-nav">
        <div class="nav-brand"><span class="nav-brand-dot"></span>Verdis Chain</div>
        <div class="nav-links">
          <a href="#features">Features</a>
          <a href="#tokenomics">Tokenomics</a>
          <a href="#architecture">Architecture</a>
          <a href="#validators">Validators</a>
          <a href="#roadmap">Roadmap</a>
        </div>
        <div class="nav-cta">
          <button class="btn-login">Log In</button>
          <button class="btn-signup">Launch App</button>
        </div>
      </nav>

      <div class="hero-left">
        <div class="hero-badge"><span class="hero-badge-dot"></span> Mainnet Ready · Node Live · 14 Peers</div>
        <h1 class="hero-title">
          <span class="gradient">GREEN BLOCKCHAIN</span><br>
          <span style="color:var(--text-white)">Engineered in Rust</span>
        </h1>
        <p class="hero-desc">Layer-1 blockchain built with Substrate. Native DPoS consensus (BABE + GRANDPA), AMM DEX, EVM with 143 opcodes, and on-chain carbon credit tracking — all powered by 7 production pallets and 260 passing tests.</p>
        <div class="hero-actions">
          <button class="btn-primary" onclick="window.location.href='/explorer'">Open Explorer →</button>
          <button class="btn-secondary" onclick="document.getElementById('features').scrollIntoView()">View Architecture</button>
        </div>
      </div>

      <div class="hero-right">
        <div class="hero-visual">
          <!-- Lime Green Circle Backdrop -->
          <div class="hero-lime-circle"></div>

          <!-- Canvas Network Particles -->
          <canvas id="hero-canvas"></canvas>

          <!-- Floating UI Cluster -->
          <!-- 1. DEX Volume Chart Card (Top-Left) -->
          <div class="dex-chart-card float-anim-1">
            <div class="dex-card-header">
              <div class="dex-play-icon">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="#1a1a1a"><path d="M8 5v14l11-7z"/></svg>
              </div>
              <span class="dex-card-title">DEX Volume</span>
              <span class="dex-badge">+18.5%</span>
            </div>
            <div class="dex-val-row">
              <span class="dex-value mono">$2.84M</span>
              <span class="dex-sub">24h Vol</span>
            </div>
            <div class="dex-bars">
              <div class="dex-bar" style="--h: 40%"></div>
              <div class="dex-bar" style="--h: 65%"></div>
              <div class="dex-bar" style="--h: 45%"></div>
              <div class="dex-bar" style="--h: 85%"></div>
              <div class="dex-bar" style="--h: 60%"></div>
              <div class="dex-bar" style="--h: 95%"></div>
              <div class="dex-bar" style="--h: 75%"></div>
            </div>
          </div>

          <!-- 2. Validator Schedule Calendar Widget (Top-Right) -->
          <div class="calendar-widget float-anim-2">
            <div class="cal-header">
              <span class="cal-title">July 2026</span>
              <span class="cal-badge">Rotation</span>
            </div>
            <div class="cal-weekdays">
              <span>M</span><span>T</span><span>W</span><span>T</span><span>F</span><span>S</span><span>S</span>
            </div>
            <div class="cal-days">
              <span class="muted">29</span><span class="muted">30</span><span>1</span><span>2</span>
              <span class="active">3</span><span>4</span><span>5</span><span>6</span><span>7</span>
              <span class="active">8</span><span>9</span><span>10</span><span>11</span><span>12</span>
              <span>13</span><span class="active">14</span><span>15</span><span>16</span><span>17</span>
              <span>18</span><span class="active">19</span><span>20</span><span>21</span><span>22</span>
              <span>23</span><span>24</span><span class="active">25</span><span>26</span><span>27</span>
              <span class="active">28</span><span>29</span><span>30</span><span>31</span>
            </div>
            <div class="cal-footer">
              <span class="cal-footer-dot"></span> Next Slot in 4h 12m
            </div>
          </div>

          <!-- 3. Blockchain Dashboard Monitor Frame (Center) -->
          <div class="monitor-frame float-anim-3">
            <div class="monitor-header">
              <div class="win-controls">
                <span class="win-dot red"></span>
                <span class="win-dot yellow"></span>
                <span class="win-dot green"></span>
              </div>
              <span class="monitor-title mono">Verdis Node Monitor v2.4</span>
              <span class="monitor-status"><span class="status-dot"></span> LIVE</span>
            </div>
            <div class="monitor-body">
              <div class="monitor-metrics">
                <div class="m-stat">
                  <span class="m-lbl">Block Height</span>
                  <span class="m-val mono">#1,847,392</span>
                </div>
                <div class="m-stat">
                  <span class="m-lbl">Network TPS</span>
                  <span class="m-val mono green">2,450</span>
                </div>
                <div class="m-stat">
                  <span class="m-lbl">Active Peers</span>
                  <span class="m-val mono">14/14</span>
                </div>
              </div>
              <div class="monitor-graph">
                <svg viewBox="0 0 300 70" preserveAspectRatio="none" style="width:100%;height:100%">
                  <defs>
                    <linearGradient id="mon-grad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stop-color="#caff33" stop-opacity="0.4"/>
                      <stop offset="100%" stop-color="#caff33" stop-opacity="0.0"/>
                    </linearGradient>
                  </defs>
                  <path d="M0,50 Q40,10 80,35 T160,20 T240,45 T300,15 L300,70 L0,70 Z" fill="url(#mon-grad)" />
                  <path d="M0,50 Q40,10 80,35 T160,20 T240,45 T300,15" fill="none" stroke="#caff33" stroke-width="2.5" />
                  <circle cx="80" cy="35" r="3.5" fill="#caff33" />
                  <circle cx="160" cy="20" r="3.5" fill="#caff33" />
                  <circle cx="300" cy="15" r="4.5" fill="#caff33" />
                </svg>
              </div>
              <div class="monitor-log mono">
                <span>Block #1847392 · 0.4s ago · 128 txs · 0.02 tCO₂</span>
              </div>
            </div>
          </div>

          <!-- 4. VRD Wallet Mobile Phone Mockup (Center-Left) -->
          <div class="mobile-phone-mockup float-anim-4">
            <div class="phone-notch"></div>
            <div class="phone-screen">
              <div class="phone-status">
                <span>11:08</span>
                <div class="phone-icons">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="#b8bcc4"><path d="M12 3c-4.97 0-9 4.03-9 9 0 2.12.74 4.07 1.97 5.61L4.35 19.4c-.39.39-.39 1.02 0 1.41.39.39 1.02.39 1.41 0l1.9-1.9C9.2 19.53 10.55 20 12 20c4.97 0 9-4.03 9-9s-4.03-9-9-9z"/></svg>
                  <span style="font-size:9px;font-weight:700">5G</span>
                </div>
              </div>
              <div class="phone-profile">
                <div class="profile-avatar">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="#caff33"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
                </div>
                <div class="profile-info">
                  <div class="profile-name">Alex Vance</div>
                  <div class="profile-address mono">0x7F...3A92</div>
                </div>
                <div class="phone-login-badge">LOGGED IN</div>
              </div>
              
              <div class="phone-balance-card">
                <div class="p-bal-lbl">Total Staked Balance</div>
                <div class="p-bal-val mono">4,250.8 VRD</div>
                <div class="p-bal-sub">≈ $14,850 USD <span class="p-up">+12.4%</span></div>
              </div>

              <!-- Circular Staking Progress Ring (75%) -->
              <div class="phone-staking-ring">
                <svg width="72" height="72" viewBox="0 0 80 80">
                  <circle cx="40" cy="40" r="32" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="6"/>
                  <circle cx="40" cy="40" r="32" fill="none" stroke="#caff33" stroke-width="6" 
                          stroke-dasharray="201" stroke-dashoffset="50.25" stroke-linecap="round"
                          transform="rotate(-90 40 40)"/>
                </svg>
                <div class="ring-label">
                  <span class="ring-pct mono">75%</span>
                  <span class="ring-txt">Staked</span>
                </div>
              </div>

              <div class="phone-actions">
                <button class="p-btn primary">Send</button>
                <button class="p-btn outline">Receive</button>
              </div>
            </div>
          </div>

          <!-- 5. Quick Stats 4-Grid Cards (Bottom-Left) -->
          <div class="stats-grid-4 float-anim-5">
            <div class="q-card">
              <div class="q-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="#caff33"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 10h-4v4h-2v-4H7v-2h4V7h2v4h4v2z"/></svg>
              </div>
              <div>
                <div class="q-lbl">Block Height</div>
                <div class="q-val mono">#1.8M</div>
              </div>
            </div>
            <div class="q-card">
              <div class="q-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="#caff33"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>
              </div>
              <div>
                <div class="q-lbl">Speed</div>
                <div class="q-val mono green">2.4k TPS</div>
              </div>
            </div>
            <div class="q-card">
              <div class="q-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="#caff33"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
              </div>
              <div>
                <div class="q-lbl">Peers</div>
                <div class="q-val mono">14 Active</div>
              </div>
            </div>
            <div class="q-card">
              <div class="q-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="#caff33"><path d="M12 3L4 9v12h16V9l-8-6zm0 14.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
              </div>
              <div>
                <div class="q-lbl">Carbon</div>
                <div class="q-val mono green">100% Net Zero</div>
              </div>
            </div>
          </div>

          <!-- 6. Vertical Action Buttons Stack (Far Right) -->
          <div class="vertical-action-stack float-anim-6">
            <button class="v-btn" title="User Profile">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#caff33" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </button>
            <button class="v-btn" title="Send VRD">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#caff33" stroke-width="2"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>
            </button>
            <button class="v-btn" title="Swap Tokens">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#caff33" stroke-width="2"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
            </button>
            <button class="v-btn" title="Stake / Receive">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#caff33" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/></svg>
            </button>
          </div>

          <!-- 7. Small Floating Tags -->
          <div class="float-tag tag-staking float-tag-1">⚡ Staking</div>
          <div class="float-tag tag-swap float-tag-2">🔄 Swap</div>
          <div class="float-tag tag-vrd float-tag-3">🔑 VRD</div>
          <div class="float-tag tag-carbon float-tag-4">🌱 Carbon</div>
        </div>
      </div>
    </div>
  </section>"""

old_html_pattern = r"<section class=\"hero-section\">.*?</section>"
text = re.sub(old_html_pattern, new_hero_html, text, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Update completed successfully!")
