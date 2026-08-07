import re

with open('/app/conversations/6a6cb8454bc0607c481bb5eb/verdis-docs.html', 'r') as f:
    original_text = f.read()

# Split original into hero section and body below hero
hero_end_idx = original_text.find('<section class="section-light" id="quickstart">')
if hero_end_idx == -1:
    raise Exception("Could not find quickstart section start")

body_below_hero = original_text[hero_end_idx:]

# Perform color replacements in body_below_hero
body_below_hero = body_below_hero.replace('#b4f849', '#caff33')
body_below_hero = body_below_hero.replace('#a3e041', '#a8e607')
body_below_hero = body_below_hero.replace('#84fe87', '#a8e607')
body_below_hero = body_below_hero.replace('#0f0f0f', '#1a1a1a')
body_below_hero = body_below_hero.replace('#1e1e1e', '#2d2d2d')
body_below_hero = body_below_hero.replace('#181818', '#252525')
body_below_hero = body_below_hero.replace('#202020', '#252525')
body_below_hero = body_below_hero.replace('180,248,73', '202,255,51')

new_hero_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Verdis Chain — Developer Documentation v2.0</title>
  <meta name="description" content="Official documentation for Verdis Chain. Build green decentralized applications with Rust, Substrate, EVM smart contracts, and carbon credit APIs." />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="Verdis Chain — Developer Documentation v2.0" />
  <meta property="og:description" content="Build on Verdis Chain with Rust + Substrate. 7 production pallets, 143 EVM opcodes, native DEX, and carbon credit APIs." />
  <meta property="og:url" content="https://verdischain.com/docs" />
  <link rel="icon" type="image/png" href="/favicon-32.png" sizes="32x32" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    :root {
      --canvas: #e8ebee;
      --canvas-light: #f1f5f9;
      --hero-bg: #1a1a1a;
      --hero-card: #2d2d2d;
      --hero-card-dark: #252525;
      --hero-border: rgba(255,255,255,0.08);
      --accent: #caff33;
      --accent-hover: #a8e607;
      --accent-2: #a8e607;
      --accent-3: #00a86b;
      --accent-glow: rgba(202,255,51,0.35);
      --accent-light: rgba(202,255,51,0.08);
      --accent-border: rgba(202,255,51,0.25);
      --accent-gradient: linear-gradient(135deg, #caff33, #a8e607);
      --text-white: #ffffff;
      --text-dim: #b8bcc4;
      --text-muted: #6b7080;
      --text-dark: #0f172a;
      --text-dark-muted: #64748b;
      --radius: 12px;
      --radius-lg: 20px;
      --radius-pill: 100px;
      --transition: 300ms cubic-bezier(0.16,1,0.3,1);
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body { font-family: 'Poppins', sans-serif; background: var(--canvas-light); color: var(--text-dark); overflow-x: hidden; -webkit-font-smoothing: antialiased; }
    .mono { font-family: 'JetBrains Mono', monospace; }

    /* ===== SCROLL PROGRESS ===== */
    #scroll-bar { position: fixed; top: 0; left: 0; height: 3px; background: linear-gradient(90deg, #caff33, #a8e607, #00a86b); z-index: 10000; width: 0; transition: width 50ms; }

    /* ===== CURSOR GLOW ===== */
    #cursor-glow { position: fixed; width: 500px; height: 500px; border-radius: 50%; background: radial-gradient(circle, rgba(202,255,51,0.06) 0%, transparent 70%); pointer-events: none; z-index: 9999; transform: translate(-50%,-50%); opacity: 0; transition: opacity 300ms; }
    body:hover #cursor-glow { opacity: 1; }

    /* ===== HERO SECTION — Dark container on light canvas ===== */
    .hero-section { position: relative; background: var(--canvas); padding: 0 24px 24px; overflow: hidden; }
    .hero-container { max-width: 1280px; margin: 0 auto; background: var(--hero-bg); border-radius: 24px; overflow: hidden; position: relative; min-height: 720px; display: flex; box-shadow: 0 20px 50px rgba(0,0,0,0.2); }
    .hero-container::before { content: ''; position: absolute; top: -50%; right: -20%; width: 600px; height: 600px; background: radial-gradient(circle, var(--accent-glow), transparent 60%); opacity: 0.15; animation: pulse-bg 4s ease-in-out infinite; }
    @keyframes pulse-bg { 0%,100% { opacity: 0.1; transform: scale(1); } 50% { opacity: 0.2; transform: scale(1.1); } }

    /* ===== NAV (inside dark hero) ===== */
    .hero-nav { position: absolute; top: 0; left: 0; right: 0; z-index: 20; display: flex; align-items: center; justify-content: space-between; padding: 24px 40px; }
    .nav-brand { font-family: 'Poppins', sans-serif; font-weight: 800; font-size: 22px; color: var(--text-white); display: flex; align-items: center; gap: 10px; text-decoration: none; }
    .nav-brand-dot { width: 12px; height: 12px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 16px var(--accent-glow); animation: pulse-dot 2s infinite; }
    @keyframes pulse-dot { 0%,100% { box-shadow: 0 0 16px var(--accent-glow); } 50% { box-shadow: 0 0 24px rgba(202,255,51,0.6); } }
    .nav-links { display: flex; gap: 36px; }
    .nav-links a { color: var(--text-muted); font-size: 14px; font-weight: 500; text-decoration: none; transition: color 250ms; position: relative; }
    .nav-links a::after { content: ''; position: absolute; bottom: -4px; left: 0; width: 0; height: 2px; background: var(--accent); border-radius: 2px; transition: width 250ms; }
    .nav-links a:hover { color: var(--text-white); }
    .nav-links a:hover::after { width: 100%; }
    .nav-cta { display: flex; gap: 12px; align-items: center; }
    .btn-login { color: var(--text-muted); font-size: 14px; font-weight: 500; text-decoration: none; padding: 8px 16px; transition: color 250ms; }
    .btn-login:hover { color: var(--text-white); }
    .btn-signup { background: var(--accent); color: var(--hero-bg); font-size: 14px; font-weight: 600; padding: 10px 24px; border-radius: var(--radius-pill); border: none; cursor: pointer; transition: var(--transition); text-decoration: none; position: relative; overflow: hidden; display: inline-block; }
    .btn-signup::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent); transition: left 500ms; }
    .btn-signup:hover::before { left: 100%; }
    .btn-signup:hover { transform: translateY(-2px); box-shadow: 0 8px 24px var(--accent-glow); }

    /* ===== HERO LEFT ===== */
    .hero-left { flex: 1; max-width: 540px; display: flex; flex-direction: column; justify-content: center; padding: 120px 0 60px 60px; position: relative; z-index: 10; }
    .hero-badge { display: inline-flex; align-items: center; gap: 8px; padding: 6px 16px; background: var(--accent-light); border: 1px solid rgba(202,255,51,0.3); border-radius: var(--radius-pill); font-size: 13px; font-weight: 600; color: var(--accent); margin-bottom: 24px; width: fit-content; opacity: 0; transform: translateY(20px); animation: slideUp 600ms 200ms forwards; }
    .hero-badge-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent); animation: pulse-dot 2s infinite; }
    .hero-title { font-size: 52px; font-weight: 900; line-height: 1.05; color: var(--text-white); margin-bottom: 20px; letter-spacing: -1px; opacity: 0; transform: translateY(30px); animation: slideUp 800ms 400ms forwards; }
    .hero-title .gradient { background: linear-gradient(135deg, #caff33 0%, #a8e607 50%, #ffffff 100%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
    .hero-desc { font-size: 15px; color: var(--text-muted); line-height: 1.7; margin-bottom: 30px; max-width: 500px; opacity: 0; transform: translateY(20px); animation: slideUp 800ms 600ms forwards; }
    
    /* Search Bar Pill */
    .search-wrapper { position: relative; max-width: 460px; margin-bottom: 28px; opacity: 0; transform: translateY(20px); animation: slideUp 800ms 700ms forwards; }
    .search-input { width: 100%; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.15); padding: 14px 22px 14px 50px; border-radius: var(--radius-pill); font-family: 'Poppins', sans-serif; font-size: 14px; color: var(--text-white); outline: none; transition: var(--transition); backdrop-filter: blur(10px); }
    .search-input::placeholder { color: var(--text-muted); }
    .search-input:focus { border-color: var(--accent); background: rgba(255,255,255,0.09); box-shadow: 0 0 20px var(--accent-glow); }
    .search-icon { position: absolute; left: 20px; top: 50%; transform: translateY(-50%); color: var(--text-muted); font-size: 16px; pointer-events: none; transition: color 250ms; }
    .search-input:focus + .search-icon { color: var(--accent); }
    .search-kbd { position: absolute; right: 16px; top: 50%; transform: translateY(-50%); background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.15); border-radius: 6px; padding: 2px 8px; font-size: 11px; color: var(--text-muted); font-family: 'JetBrains Mono', monospace; pointer-events: none; }

    .hero-actions { display: flex; gap: 16px; opacity: 0; transform: translateY(20px); animation: slideUp 800ms 800ms forwards; }
    .btn-read-more { background: linear-gradient(135deg, #caff33, #a8e607); color: var(--hero-bg); font-size: 15px; font-weight: 700; padding: 14px 32px; border-radius: var(--radius-pill); border: none; cursor: pointer; transition: var(--transition); position: relative; overflow: hidden; display: inline-flex; align-items: center; gap: 8px; text-decoration: none; }
    .btn-read-more::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent); transition: left 500ms; }
    .btn-read-more:hover::before { left: 100%; }
    .btn-read-more:hover { transform: translateY(-3px); box-shadow: 0 12px 32px var(--accent-glow); }
    .btn-explore { background: transparent; color: var(--text-white); font-size: 15px; font-weight: 600; padding: 14px 32px; border-radius: var(--radius-pill); border: 1px solid rgba(255,255,255,0.2); cursor: pointer; transition: var(--transition); text-decoration: none; display: inline-flex; align-items: center; gap: 8px; }
    .btn-explore:hover { border-color: var(--accent); background: var(--accent-light); color: var(--accent); }
    @keyframes slideUp { to { opacity: 1; transform: translateY(0); } }

    /* ===== HERO RIGHT — COMPLEX 3D FLOATING UI CLUSTER ===== */
    .hero-right { flex: 1.25; position: relative; height: 680px; display: flex; align-items: center; justify-content: center; padding: 40px 20px 40px 0; z-index: 5; }
    #hero-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; }

    /* Large Lime Green Circle Background */
    .hero-bg-lime-circle {
      position: absolute;
      top: 50%;
      left: 48%;
      transform: translate(-50%, -50%);
      width: 360px;
      height: 360px;
      border-radius: 50%;
      background: radial-gradient(circle at 35% 35%, #caff33 0%, #a8e607 60%, rgba(202,255,51,0.2) 100%);
      box-shadow: 0 0 90px rgba(202,255,51,0.45);
      z-index: 1;
      pointer-events: none;
      opacity: 0.85;
    }

    /* Floating Elements Glass-morphism Base */
    .floating-element {
      position: absolute;
      background: rgba(45, 45, 45, 0.85);
      border: 1px solid rgba(255, 255, 255, 0.14);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
      border-radius: 18px;
      transition: transform 300ms ease, box-shadow 300ms ease;
      z-index: 3;
    }
    .floating-element:hover {
      border-color: rgba(202, 255, 51, 0.4);
      box-shadow: 0 24px 70px rgba(0, 0, 0, 0.6), 0 0 20px rgba(202, 255, 51, 0.2);
    }

    /* 1. Central Monitor Frame (Code Editor) */
    .central-monitor {
      top: 50%;
      left: 44%;
      transform: translate(-50%, -50%);
      width: 410px;
      z-index: 4;
      overflow: hidden;
      border-color: rgba(255, 255, 255, 0.18);
      animation: float-main 6s ease-in-out infinite alternate;
    }
    .monitor-topbar { display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: rgba(30, 30, 30, 0.85); border-bottom: 1px solid rgba(255, 255, 255, 0.08); }
    .topbar-dots { display: flex; gap: 6px; }
    .topbar-dots .dot { width: 10px; height: 10px; border-radius: 50%; }
    .dot-red { background: #ff5f56; }
    .dot-yellow { background: #ffbd2e; }
    .dot-green { background: #27c93f; }
    .monitor-title { font-family: 'JetBrains Mono', monospace; font-size: 11.5px; color: var(--text-dim); display: flex; align-items: center; gap: 6px; }
    .btn-copy-code { background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.1); color: var(--text-dim); border-radius: 6px; padding: 3px 8px; font-size: 11px; cursor: pointer; display: flex; align-items: center; gap: 4px; transition: all 200ms; }
    .btn-copy-code:hover { background: rgba(202, 255, 51, 0.15); border-color: var(--accent); color: var(--accent); }
    .monitor-code { padding: 14px 16px; font-family: 'JetBrains Mono', monospace; font-size: 11px; line-height: 1.65; color: #e2e8f0; background: #1a1a1a; overflow-x: auto; }
    .monitor-code .kw { color: #caff33; font-weight: 600; }
    .monitor-code .fn { color: #38bdf8; }
    .monitor-code .ty { color: #a8e607; }
    .monitor-code .cm { color: #6b7080; font-style: italic; }

    /* 2. Mobile Phone Mockup */
    .phone-mockup {
      top: 8%;
      right: 10%;
      width: 185px;
      padding: 14px 12px 16px;
      border-radius: 22px;
      z-index: 5;
      border-color: rgba(202, 255, 51, 0.3);
      animation: float-phone 5s ease-in-out infinite alternate;
    }
    .phone-notch { width: 48px; height: 4px; background: rgba(255, 255, 255, 0.2); border-radius: 10px; margin: 0 auto 12px; }
    .phone-header { margin-bottom: 12px; }
    .phone-profile { display: flex; align-items: center; gap: 8px; }
    .phone-avatar { width: 28px; height: 28px; border-radius: 50%; background: var(--accent-light); border: 1px solid var(--accent); display: flex; align-items: center; justify-content: center; font-size: 12px; }
    .phone-user { display: flex; flex-direction: column; }
    .phone-name { font-size: 12px; font-weight: 700; color: var(--text-white); }
    .phone-status { font-size: 10px; color: var(--text-muted); display: flex; align-items: center; gap: 4px; }
    .phone-status .status-dot { width: 5px; height: 5px; border-radius: 50%; background: #caff33; display: inline-block; }

    .phone-endpoints { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
    .endpoint-item { display: flex; align-items: center; gap: 6px; background: rgba(255, 255, 255, 0.04); padding: 5px 8px; border-radius: 8px; font-family: 'JetBrains Mono', monospace; font-size: 10px; }
    .badge { padding: 1px 5px; border-radius: 4px; font-size: 9px; font-weight: 700; }
    .badge-get { background: rgba(56, 189, 248, 0.2); color: #38bdf8; }
    .badge-post { background: rgba(202, 255, 51, 0.2); color: #caff33; }
    .badge-rpc { background: rgba(168, 230, 7, 0.2); color: #a8e607; }
    .ep-path { color: var(--text-dim); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

    .phone-progress-card { display: flex; align-items: center; gap: 10px; background: rgba(202, 255, 51, 0.08); border: 1px solid rgba(202, 255, 51, 0.25); padding: 8px 10px; border-radius: 12px; }
    .progress-ring-wrap { position: relative; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; }
    .progress-ring { transform: rotate(-90deg); }
    .progress-ring .ring-bg { stroke: rgba(255, 255, 255, 0.1); }
    .progress-ring .ring-fill { stroke: #caff33; stroke-linecap: round; transition: stroke-dashoffset 500ms; }
    .ring-text { position: absolute; font-size: 11px; font-weight: 800; color: #caff33; font-family: 'JetBrains Mono', monospace; }
    .progress-info { display: flex; flex-direction: column; }
    .prog-title { font-size: 11px; font-weight: 700; color: var(--text-white); }
    .prog-sub { font-size: 9px; color: var(--text-muted); }

    /* 3. Calendar Widget */
    .calendar-widget {
      bottom: 8%;
      right: 12%;
      width: 205px;
      padding: 12px 14px;
      border-radius: 18px;
      z-index: 5;
      animation: float-cal 7s ease-in-out infinite alternate;
    }
    .cal-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
    .cal-title { display: flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 700; color: var(--text-white); }
    .cal-badge { background: var(--accent); color: #1a1a1a; font-size: 9px; font-weight: 800; padding: 1px 6px; border-radius: 10px; }
    .cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 3px; text-align: center; font-size: 10px; margin-bottom: 8px; }
    .cal-day-name { font-weight: 600; color: var(--text-muted); padding-bottom: 4px; }
    .cal-date { color: var(--text-dim); padding: 3px 0; border-radius: 6px; font-family: 'JetBrains Mono', monospace; }
    .cal-date.muted { color: rgba(255, 255, 255, 0.2); }
    .cal-date.active-release { background: #caff33; color: #1a1a1a; font-weight: 800; box-shadow: 0 0 10px rgba(202,255,51,0.5); }
    .cal-legend { font-size: 9.5px; color: var(--text-dim); display: flex; align-items: center; gap: 5px; padding-top: 6px; border-top: 1px solid rgba(255, 255, 255, 0.08); }
    .cal-legend .leg-dot { width: 6px; height: 6px; border-radius: 50%; background: #caff33; }

    /* 4. Grid of 4 Small Cards (Dev Stats) */
    .dev-stats-grid {
      bottom: 4%;
      left: 3%;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      width: 215px;
      background: transparent;
      border: none;
      box-shadow: none;
      backdrop-filter: none;
      -webkit-backdrop-filter: none;
      z-index: 5;
      animation: float-stats 5.5s ease-in-out infinite alternate;
    }
    .stat-card {
      background: rgba(45, 45, 45, 0.88);
      border: 1px solid rgba(202, 255, 51, 0.22);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border-radius: 14px;
      padding: 8px 10px;
      display: flex;
      align-items: center;
      gap: 8px;
      box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
      transition: transform 200ms;
    }
    .stat-card:hover { transform: translateY(-2px); border-color: var(--accent); }
    .stat-icon { font-size: 16px; }
    .stat-info { display: flex; flex-direction: column; }
    .stat-val { font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 800; color: #caff33; line-height: 1.1; }
    .stat-lbl { font-size: 9.5px; color: var(--text-dim); }

    /* 5. Card with Play Icon + Bar Chart */
    .chart-card {
      top: 5%;
      left: 2%;
      width: 210px;
      padding: 12px 14px;
      border-radius: 16px;
      z-index: 5;
      animation: float-chart 4.5s ease-in-out infinite alternate;
    }
    .chart-header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
    .play-btn-circle { width: 28px; height: 28px; border-radius: 50%; background: #caff33; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 12px rgba(202, 255, 51, 0.5); }
    .chart-titles { display: flex; flex-direction: column; }
    .chart-main-title { font-size: 12px; font-weight: 700; color: var(--text-white); }
    .chart-sub-title { font-size: 9.5px; color: #caff33; font-weight: 600; }
    .chart-bars { display: flex; align-items: flex-end; justify-content: space-between; height: 40px; gap: 4px; padding-top: 4px; }
    .bar-col { flex: 1; background: rgba(255, 255, 255, 0.08); height: 100%; border-radius: 4px; display: flex; align-items: flex-end; overflow: hidden; }
    .bar-fill { width: 100%; background: linear-gradient(to top, #a8e607, #caff33); border-radius: 4px; box-shadow: 0 0 8px rgba(202, 255, 51, 0.4); }

    /* 6. Vertical Button Stack */
    .vertical-action-stack {
      top: 32%;
      right: 1.5%;
      display: flex;
      flex-direction: column;
      gap: 10px;
      background: transparent;
      border: none;
      box-shadow: none;
      backdrop-filter: none;
      -webkit-backdrop-filter: none;
      z-index: 6;
      animation: float-btns 6.5s ease-in-out infinite alternate;
    }
    .action-btn {
      width: 42px;
      height: 42px;
      border-radius: 12px;
      background: rgba(45, 45, 45, 0.9);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: var(--text-white);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
      transition: all 250ms;
    }
    .action-btn:hover { background: rgba(202, 255, 51, 0.15); border-color: #caff33; color: #caff33; box-shadow: 0 0 16px rgba(202, 255, 51, 0.4); transform: scale(1.08); }

    /* 7. Floating Tech Tags */
    .float-tag { padding: 5px 12px; border-radius: var(--radius-pill); font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #caff33; background: rgba(30, 30, 30, 0.85); border: 1px solid rgba(202, 255, 51, 0.35); z-index: 6; box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4); position: absolute; }
    .tag-rust { top: 2%; left: 45%; animation: float-tag1 4s infinite alternate ease-in-out; }
    .tag-substrate { top: 32%; left: -2%; animation: float-tag2 5.5s infinite alternate ease-in-out; }
    .tag-evm { bottom: 22%; left: 42%; animation: float-tag3 4.8s infinite alternate ease-in-out; }
    .tag-wasm { top: 22%; right: -2%; animation: float-tag4 5.2s infinite alternate ease-in-out; }

    /* Keyframe Animations */
    @keyframes float-main { 0% { transform: translate(-50%, -50%) translateY(0px); } 100% { transform: translate(-50%, -50%) translateY(-12px); } }
    @keyframes float-phone { 0% { transform: translateY(0px) rotate(0deg); } 100% { transform: translateY(-15px) rotate(1deg); } }
    @keyframes float-cal { 0% { transform: translateY(0px); } 100% { transform: translateY(-12px); } }
    @keyframes float-stats { 0% { transform: translateY(0px); } 100% { transform: translateY(-10px); } }
    @keyframes float-chart { 0% { transform: translateY(0px) rotate(0deg); } 100% { transform: translateY(-14px) rotate(-1deg); } }
    @keyframes float-btns { 0% { transform: translateY(0px); } 100% { transform: translateY(-10px); } }
    @keyframes float-tag1 { 0% { transform: translateY(0); } 100% { transform: translateY(-8px); } }
    @keyframes float-tag2 { 0% { transform: translateY(0); } 100% { transform: translateY(-10px); } }
    @keyframes float-tag3 { 0% { transform: translateY(0); } 100% { transform: translateY(-7px); } }
    @keyframes float-tag4 { 0% { transform: translateY(0); } 100% { transform: translateY(-9px); } }

    /* Existing Section Dark / Section Light overrides if any */
    .section-dark { background: #1a1a1a; color: var(--text-white); padding: 80px 24px; }
    .section-light { background: var(--canvas-light); color: var(--text-dark); padding: 80px 24px; }
    .card-dark { background: #2d2d2d; border: 1px solid rgba(255,255,255,0.08); border-radius: var(--radius); padding: 24px; }
    .card-light { background: #ffffff; border: 1px solid rgba(0,0,0,0.06); border-radius: var(--radius); padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); }
  </style>
</head>
<body>
  <div id="scroll-bar"></div>
  <div id="cursor-glow"></div>

  <!-- ===== HERO SECTION ===== -->
  <section class="hero-section">
    <div class="hero-container">
      
      <!-- NAV -->
      <nav class="hero-nav">
        <a href="/" class="nav-brand">
          <div class="nav-brand-dot"></div>
          Verdis Chain
        </a>
        <div class="nav-links">
          <a href="#quickstart">Quick Start</a>
          <a href="#pallets">Pallets</a>
          <a href="#rpc">RPC Methods</a>
          <a href="#code-examples">Code Examples</a>
        </div>
        <div class="nav-cta">
          <a href="#" class="btn-login">Sign In</a>
          <a href="#" class="btn-signup">Sign Up</a>
        </div>
      </nav>

      <!-- SPLIT HERO LEFT -->
      <div class="hero-left">
        <div class="hero-badge">
          <div class="hero-badge-dot"></div>
          Developer Documentation v2.0
        </div>
        <h1 class="hero-title">
          DEVELOPER<br>
          <span class="gradient">DOCS</span>
        </h1>
        <p class="hero-desc">
          Build on Verdis Chain with Rust + Substrate. 7 production pallets, 143 EVM opcodes, native DEX, and carbon credit APIs.
        </p>

        <!-- Search Bar -->
        <div class="search-wrapper">
          <input type="text" id="doc-search" class="search-input" placeholder="Search documentation, pallets, RPC methods..." autocomplete="off" />
          <span class="search-icon">🔍</span>
          <span class="search-kbd">⌘K</span>
        </div>

        <!-- CTA Buttons -->
        <div class="hero-actions">
          <a href="#quickstart" class="btn-read-more">Getting Started →</a>
          <a href="#rpc" class="btn-explore">API Reference</a>
        </div>
      </div>

      <!-- SPLIT HERO RIGHT — COMPLEX 3D FLOATING UI CLUSTER -->
      <div class="hero-right">
        <canvas id="hero-canvas"></canvas>

        <!-- Background Lime Sphere Circle -->
        <div class="hero-bg-lime-circle"></div>

        <!-- 1. Central Monitor Frame (Code Editor) -->
        <div class="floating-element central-monitor">
          <div class="monitor-topbar">
            <div class="topbar-dots">
              <span class="dot dot-red"></span>
              <span class="dot dot-yellow"></span>
              <span class="dot dot-green"></span>
            </div>
            <div class="monitor-title">
              <span>🦀</span> runtime.rs
            </div>
            <button class="btn-copy-code" onclick="copySnippet('runtime-code', this)" title="Copy Code">
              📋 Copy
            </button>
          </div>
          <div class="monitor-code" id="runtime-code">
<span class="cm">// Substrate Pallet - Carbon Credit Trading</span>
<span class="kw">#[frame_support::pallet]</span>
<span class="kw">pub mod</span> <span class="fn">pallet</span> {
    <span class="kw">use</span> frame_support::pallet_prelude::*;

    <span class="kw">#[pallet::storage]</span>
    <span class="kw">pub type</span> <span class="ty">CarbonBalance</span>&lt;<span class="ty">T</span>: <span class="ty">Config</span>&gt; = <span class="ty">StorageMap</span>&lt;
        <span class="ty">_</span>, <span class="ty">Blake2_128Concat</span>, <span class="ty">AccountId</span>, <span class="ty">u128</span>
    &gt;;

    <span class="kw">#[pallet::call]</span>
    <span class="kw">impl</span>&lt;<span class="ty">T</span>: <span class="ty">Config</span>&gt; <span class="ty">Pallet</span>&lt;<span class="ty">T</span>&gt; {
        <span class="kw">pub fn</span> <span class="fn">retire_credits</span>(origin: <span class="ty">OriginFor</span>&lt;<span class="ty">T</span>&gt;, amt: <span class="ty">u128</span>) -&gt; <span class="ty">DispatchResult</span> {
            <span class="kw">let</span> sender = ensure_signed(origin)?;
            <span class="ty">CarbonBalance</span>::&lt;<span class="ty">T</span>&gt;::mutate(&sender, |b| *b -= amt);
            <span class="kw">Ok</span>(())
        }
    }
}</div>
        </div>

        <!-- 2. Mobile Phone Mockup -->
        <div class="floating-element phone-mockup">
          <div class="phone-notch"></div>
          <div class="phone-header">
            <div class="phone-profile">
              <div class="phone-avatar">⚡</div>
              <div class="phone-user">
                <div class="phone-name">API Docs</div>
                <div class="phone-status"><span class="status-dot"></span> Online</div>
              </div>
            </div>
          </div>
          <div class="phone-content">
            <div class="phone-endpoints">
              <div class="endpoint-item">
                <span class="badge badge-get">GET</span>
                <span class="ep-path">/pallet/carbon</span>
              </div>
              <div class="endpoint-item">
                <span class="badge badge-post">POST</span>
                <span class="ep-path">/tx/submit</span>
              </div>
              <div class="endpoint-item">
                <span class="badge badge-rpc">RPC</span>
                <span class="ep-path">/state/storage</span>
              </div>
            </div>
            <div class="phone-progress-card">
              <div class="progress-ring-wrap">
                <svg class="progress-ring" width="44" height="44" viewBox="0 0 64 64">
                  <circle class="ring-bg" cx="32" cy="32" r="26" stroke-width="6" fill="none" />
                  <circle class="ring-fill" cx="32" cy="32" r="26" stroke-width="6" fill="none" stroke-dasharray="163.36" stroke-dashoffset="40.84" />
                </svg>
                <span class="ring-text">75%</span>
              </div>
              <div class="progress-info">
                <div class="prog-title">Coverage</div>
                <div class="prog-sub">195/260 Suites</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. Calendar Widget -->
        <div class="floating-element calendar-widget">
          <div class="cal-header">
            <div class="cal-title">
              <span>📅</span>
              <span>August 2026</span>
            </div>
            <span class="cal-badge">v2.0</span>
          </div>
          <div class="cal-grid">
            <div class="cal-day-name">M</div><div class="cal-day-name">T</div><div class="cal-day-name">W</div><div class="cal-day-name">T</div><div class="cal-day-name">F</div><div class="cal-day-name">S</div><div class="cal-day-name">S</div>
            <div class="cal-date muted">27</div><div class="cal-date muted">28</div><div class="cal-date muted">29</div><div class="cal-date muted">30</div><div class="cal-date">31</div><div class="cal-date">1</div><div class="cal-date">2</div>
            <div class="cal-date">3</div><div class="cal-date">4</div><div class="cal-date">5</div><div class="cal-date">6</div><div class="cal-date">7</div><div class="cal-date">8</div><div class="cal-date">9</div>
            <div class="cal-date">10</div><div class="cal-date">11</div><div class="cal-date">12</div><div class="cal-date">13</div><div class="cal-date">14</div><div class="cal-date active-release">15</div><div class="cal-date">16</div>
            <div class="cal-date">17</div><div class="cal-date">18</div><div class="cal-date">19</div><div class="cal-date">20</div><div class="cal-date">21</div><div class="cal-date active-release">22</div><div class="cal-date">23</div>
            <div class="cal-date">24</div><div class="cal-date">25</div><div class="cal-date">26</div><div class="cal-date">27</div><div class="cal-date">28</div><div class="cal-date active-release">29</div><div class="cal-date">30</div>
          </div>
          <div class="cal-legend">
            <span class="leg-dot"></span> Aug 15: v2.0 Release
          </div>
        </div>

        <!-- 4. Grid of 4 Small Cards (Dev Stats) -->
        <div class="floating-element dev-stats-grid">
          <div class="stat-card">
            <div class="stat-icon">🧪</div>
            <div class="stat-info">
              <div class="stat-val">260</div>
              <div class="stat-lbl">Tests</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⚡</div>
            <div class="stat-info">
              <div class="stat-val">143</div>
              <div class="stat-lbl">Opcodes</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📦</div>
            <div class="stat-info">
              <div class="stat-val">7</div>
              <div class="stat-lbl">Pallets</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🛠️</div>
            <div class="stat-info">
              <div class="stat-val">51</div>
              <div class="stat-lbl">SDK Methods</div>
            </div>
          </div>
        </div>

        <!-- 5. Card with Play Icon + Bar Chart -->
        <div class="floating-element chart-card">
          <div class="chart-header">
            <div class="play-btn-circle">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="#1a1a1a"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
            </div>
            <div class="chart-titles">
              <div class="chart-main-title">Passing Tests</div>
              <div class="chart-sub-title">100% Pass Rate</div>
            </div>
          </div>
          <div class="chart-bars">
            <div class="bar-col"><div class="bar-fill" style="height: 65%;"></div></div>
            <div class="bar-col"><div class="bar-fill" style="height: 80%;"></div></div>
            <div class="bar-col"><div class="bar-fill" style="height: 75%;"></div></div>
            <div class="bar-col"><div class="bar-fill" style="height: 90%;"></div></div>
            <div class="bar-col"><div class="bar-fill" style="height: 85%;"></div></div>
            <div class="bar-col"><div class="bar-fill" style="height: 100%;"></div></div>
            <div class="bar-col"><div class="bar-fill" style="height: 95%;"></div></div>
          </div>
        </div>

        <!-- 6. Vertical Stack of 4 Square Buttons -->
        <div class="floating-element vertical-action-stack">
          <button class="action-btn" onclick="copySnippet('runtime-code', this)" title="Copy Code">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
          </button>
          <button class="action-btn" title="Run Code / Up">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="19" x2="12" y2="5"></line><polyline points="5 12 12 5 19 12"></polyline></svg>
          </button>
          <button class="action-btn" title="Cargo Build / Circle">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="8"></circle></svg>
          </button>
          <button class="action-btn" title="Run Tests / Down">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><polyline points="19 12 12 19 5 12"></polyline></svg>
          </button>
        </div>

        <!-- 7. Small Floating Tech Tags -->
        <div class="float-tag tag-rust">Rust</div>
        <div class="float-tag tag-substrate">Substrate</div>
        <div class="float-tag tag-evm">EVM</div>
        <div class="float-tag tag-wasm">WASM</div>

      </div>

    </div>
  </section>

"""

full_updated_content = new_hero_html + body_below_hero

with open('/app/conversations/6a6cb8454bc0607c481bb5eb/verdis-docs.html', 'w') as f:
    f.write(full_updated_content)

print("Successfully wrote updated verdis-docs.html")
