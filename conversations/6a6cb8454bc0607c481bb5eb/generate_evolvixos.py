import re

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>EvolvixOS — The AI Engineering Operating System</title>
  <meta name="description" content="EvolvixOS is the world's first AI Engineering Operating System. Autonomous AI agents design, build, test, and secure software 24/7." />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="EvolvixOS — The AI Engineering Operating System" />
  <meta property="og:description" content="Autonomous AI agents that design, build, test, and secure software 24/7. 16 core agents, 24 AI providers, plugin marketplace." />
  <meta property="og:url" content="https://evolvixos.com" />
  <link rel="icon" type="image/png" href="/favicon-32.png" sizes="32x32" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />

  <!-- JSON-LD Structured Data for SoftwareApplication -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "EvolvixOS",
    "description": "The AI Engineering Operating System — autonomous AI agents that design, build, test, and secure software 24/7.",
    "applicationCategory": "DeveloperApplication",
    "operatingSystem": "Linux, macOS, Windows, Docker",
    "offers": {
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "USD"
    },
    "author": {
      "@type": "Organization",
      "name": "Protremix"
    }
  }
  </script>

  <style>
    :root {
      --canvas: #b0b5b8;
      --canvas-light: #f8fafc;
      --hero-bg: #1a1a1a;
      --hero-card: #2d2d2d;
      --hero-card-dark: #202020;
      --accent: #6366f1;
      --accent-hover: #5457e6;
      --accent-glow: rgba(99,102,241,0.3);
      --accent-light: rgba(99,102,241,0.1);
      --gradient: linear-gradient(135deg, #6366f1, #8b5cf6, #a78bfa);
      --secondary-accent: #8b5cf6;
      --violet-soft: #a78bfa;
      --text-white: #ffffff;
      --text-muted: #9ca3ad;
      --text-dark: #0f172a;
      --radius: 12px;
      --radius-lg: 20px;
      --radius-pill: 100px;
      --transition: 250ms cubic-bezier(0.16,1,0.3,1);
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body { font-family: 'Poppins', sans-serif; background: var(--canvas-light); color: var(--text-dark); overflow-x: hidden; -webkit-font-smoothing: antialiased; }
    .mono { font-family: 'JetBrains Mono', monospace; }

    a:focus-visible, button:focus-visible { outline: 2px solid var(--accent); outline-offset: 4px; }

    /* ===== SCROLL PROGRESS ===== */
    #scroll-bar { position: fixed; top: 0; left: 0; height: 3px; background: linear-gradient(90deg, #6366f1, #8b5cf6, #a78bfa); z-index: 10000; width: 0; transition: width 50ms; }

    /* ===== CURSOR GLOW ===== */
    #cursor-glow { position: fixed; width: 500px; height: 500px; border-radius: 50%; background: radial-gradient(circle, rgba(99,102,241,0.08) 0%, transparent 70%); pointer-events: none; z-index: 9999; transform: translate(-50%,-50%); opacity: 0; transition: opacity 300ms; }
    body:hover #cursor-glow { opacity: 1; }

    /* ===== HERO SECTION — Template Skeleton: Dark container, split layout ===== */
    .hero-section { position: relative; background: var(--canvas); padding: 0 24px; overflow: hidden; }
    .hero-container { max-width: 1280px; margin: 0 auto; background: var(--hero-bg); border-radius: 24px; overflow: hidden; position: relative; min-height: 640px; display: flex; }
    .hero-container::before { content: ''; position: absolute; top: -50%; right: -20%; width: 600px; height: 600px; background: radial-gradient(circle, var(--accent-glow), transparent 60%); opacity: 0.15; animation: pulse-bg 4s ease-in-out infinite; }
    @keyframes pulse-bg { 0%,100% { opacity: 0.1; transform: scale(1); } 50% { opacity: 0.2; transform: scale(1.1); } }

    /* ===== NAV (inside dark hero) ===== */
    .hero-nav { position: absolute; top: 0; left: 0; right: 0; z-index: 10; display: flex; align-items: center; justify-content: space-between; padding: 24px 40px; }
    .nav-brand { font-family: 'Poppins'; font-weight: 800; font-size: 22px; color: var(--text-white); display: flex; align-items: center; gap: 10px; text-decoration: none; }
    .nav-brand-dot { width: 12px; height: 12px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 16px var(--accent-glow); animation: pulse-dot 2s infinite; }
    @keyframes pulse-dot { 0%,100% { box-shadow: 0 0 16px var(--accent-glow); } 50% { box-shadow: 0 0 24px rgba(99,102,241,0.6); } }
    .nav-links { display: flex; gap: 36px; }
    .nav-links a { color: var(--text-muted); font-size: 14px; font-weight: 500; transition: color 250ms; position: relative; text-decoration: none; }
    .nav-links a::after { content: ''; position: absolute; bottom: -4px; left: 0; width: 0; height: 2px; background: var(--accent); border-radius: 2px; transition: width 250ms; }
    .nav-links a:hover { color: var(--text-white); }
    .nav-links a:hover::after { width: 100%; }
    .nav-cta { display: flex; gap: 12px; align-items: center; }
    .btn-login { color: var(--text-muted); font-size: 14px; font-weight: 500; padding: 8px 16px; transition: color 250ms; text-decoration: none; }
    .btn-login:hover { color: var(--text-white); }
    .btn-signup { background: var(--accent); color: #ffffff; font-size: 14px; font-weight: 600; padding: 10px 24px; border-radius: var(--radius-pill); border: none; cursor: pointer; transition: var(--transition); position: relative; overflow: hidden; text-decoration: none; }
    .btn-signup::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent); transition: left 500ms; }
    .btn-signup:hover::before { left: 100%; }
    .btn-signup:hover { transform: translateY(-2px); box-shadow: 0 8px 24px var(--accent-glow); background: var(--accent-hover); }

    /* ===== HERO LEFT — Text content ===== */
    .hero-left { flex: 1; display: flex; flex-direction: column; justify-content: center; padding: 120px 60px 60px 60px; position: relative; z-index: 5; }
    .hero-badge { display: inline-flex; align-items: center; gap: 8px; padding: 6px 16px; background: var(--accent-light); border: 1px solid rgba(99,102,241,0.3); border-radius: var(--radius-pill); font-size: 13px; font-weight: 600; color: var(--accent); margin-bottom: 24px; width: fit-content; opacity: 0; transform: translateY(20px); animation: slideUp 600ms 200ms forwards; }
    .hero-badge-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent); animation: pulse-dot 2s infinite; }
    .hero-title { font-size: 48px; font-weight: 800; line-height: 1.1; color: var(--text-white); margin-bottom: 24px; opacity: 0; transform: translateY(30px); animation: slideUp 800ms 400ms forwards; }
    .hero-title .accent { color: var(--accent); }
    .hero-title .gradient { background: linear-gradient(135deg, #6366f1, #8b5cf6, #a78bfa); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
    .hero-desc { font-size: 16px; color: var(--text-muted); line-height: 1.8; margin-bottom: 36px; max-width: 480px; opacity: 0; transform: translateY(20px); animation: slideUp 800ms 600ms forwards; }
    .hero-actions { display: flex; gap: 16px; opacity: 0; transform: translateY(20px); animation: slideUp 800ms 800ms forwards; }
    .btn-read-more { background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #ffffff; font-size: 15px; font-weight: 700; padding: 14px 32px; border-radius: var(--radius-pill); border: none; cursor: pointer; transition: var(--transition); position: relative; overflow: hidden; display: inline-flex; align-items: center; gap: 8px; text-decoration: none; }
    .btn-read-more::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent); transition: left 500ms; }
    .btn-read-more:hover::before { left: 100%; }
    .btn-read-more:hover { transform: translateY(-3px); box-shadow: 0 12px 32px var(--accent-glow); }
    .btn-explore { background: transparent; color: var(--text-white); font-size: 15px; font-weight: 600; padding: 14px 32px; border-radius: var(--radius-pill); border: 1px solid rgba(255,255,255,0.2); cursor: pointer; transition: var(--transition); text-decoration: none; }
    .btn-explore:hover { border-color: var(--accent); background: var(--accent-light); }
    @keyframes slideUp { to { opacity: 1; transform: translateY(0); } }

    /* ===== HERO RIGHT — 3D Floating Visual ===== */
    .hero-right { flex: 1; position: relative; display: flex; align-items: center; justify-content: center; padding: 80px 40px; }
    .hero-visual { position: relative; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }
    .hero-circle { position: absolute; width: 340px; height: 340px; border-radius: 50%; background: radial-gradient(circle, rgba(99,102,241,0.25), rgba(99,102,241,0.05) 60%, transparent); animation: pulse-circle 4s ease-in-out infinite; }
    @keyframes pulse-circle { 0%,100% { transform: scale(1); opacity: 0.8; } 50% { transform: scale(1.08); opacity: 1; } }
    #hero-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 2; }

    /* Floating UI cards */
    .float-card { position: absolute; background: var(--hero-card); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 16px 20px; box-shadow: 0 12px 40px rgba(0,0,0,0.4); z-index: 3; backdrop-filter: blur(10px); }
    .float-card-1 { top: 12%; right: 8%; animation: float-1 6s ease-in-out infinite; }
    .float-card-2 { bottom: 18%; left: 8%; animation: float-2 7s ease-in-out infinite; }
    .float-card-3 { top: 45%; right: 4%; animation: float-3 5s ease-in-out infinite; }
    .float-card-4 { bottom: 8%; right: 20%; animation: float-4 8s ease-in-out infinite; }
    @keyframes float-1 { 0%,100% { transform: translateY(0) rotate(-2deg); } 50% { transform: translateY(-12px) rotate(1deg); } }
    @keyframes float-2 { 0%,100% { transform: translateY(0) rotate(2deg); } 50% { transform: translateY(10px) rotate(-1deg); } }
    @keyframes float-3 { 0%,100% { transform: translateY(0) rotate(-1deg); } 50% { transform: translateY(-8px) rotate(2deg); } }
    @keyframes float-4 { 0%,100% { transform: translateY(0) rotate(1deg); } 50% { transform: translateY(6px) rotate(-2deg); } }

    .float-card-label { font-size: 11px; color: var(--text-muted); font-weight: 500; margin-bottom: 6px; }
    .float-card-value { font-size: 18px; font-weight: 700; color: var(--text-white); }
    .float-card-value.indigo { color: var(--accent); }
    .float-card-bar { width: 100%; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-top: 8px; overflow: hidden; }
    .float-card-bar-fill { height: 100%; background: linear-gradient(90deg, #6366f1, #8b5cf6); border-radius: 2px; animation: bar-fill 2s ease-out; }
    @keyframes bar-fill { from { width: 0; } }
    .float-card-icon { width: 32px; height: 32px; border-radius: 8px; background: var(--accent-light); display: flex; align-items: center; justify-content: center; font-size: 16px; margin-bottom: 8px; }

    /* Phone mockup */
    .phone-mockup { position: absolute; width: 160px; height: 320px; background: var(--hero-card-dark); border: 3px solid rgba(255,255,255,0.15); border-radius: 24px; z-index: 3; padding: 20px 16px; display: flex; flex-direction: column; gap: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.5); animation: float-phone 6s ease-in-out infinite; }
    @keyframes float-phone { 0%,100% { transform: translateY(0) rotate(3deg); } 50% { transform: translateY(-16px) rotate(1deg); } }
    .phone-screen-label { font-size: 10px; color: var(--text-muted); font-weight: 500; }
    .phone-screen-value { font-size: 13px; font-weight: 700; color: var(--text-white); }
    .phone-progress-ring { width: 56px; height: 56px; margin: 8px auto; position: relative; }
    .phone-progress-ring svg { transform: rotate(-90deg); }
    .phone-login-btn { background: var(--accent); color: #ffffff; font-size: 12px; font-weight: 700; padding: 8px; border-radius: 8px; text-align: center; cursor: pointer; transition: background 250ms; }
    .phone-login-btn:hover { background: var(--accent-hover); }

    /* ===== SECTION REVEAL ===== */
    .reveal { opacity: 0; transform: translateY(40px); transition: opacity 700ms cubic-bezier(0.16,1,0.3,1), transform 700ms cubic-bezier(0.16,1,0.3,1); }
    .reveal.visible { opacity: 1; transform: translateY(0); }
    .reveal-stagger > * { opacity: 0; transform: translateY(40px); transition: opacity 600ms cubic-bezier(0.16,1,0.3,1), transform 600ms cubic-bezier(0.16,1,0.3,1); }
    .reveal-stagger.visible > *:nth-child(1) { opacity:1; transform:translateY(0); transition-delay:0ms; }
    .reveal-stagger.visible > *:nth-child(2) { opacity:1; transform:translateY(0); transition-delay:80ms; }
    .reveal-stagger.visible > *:nth-child(3) { opacity:1; transform:translateY(0); transition-delay:160ms; }
    .reveal-stagger.visible > *:nth-child(4) { opacity:1; transform:translateY(0); transition-delay:240ms; }
    .reveal-stagger.visible > *:nth-child(5) { opacity:1; transform:translateY(0); transition-delay:320ms; }
    .reveal-stagger.visible > *:nth-child(6) { opacity:1; transform:translateY(0); transition-delay:400ms; }

    /* ===== STATS BAR (light section) ===== */
    .stats-section { background: var(--canvas-light); padding: 80px 24px 40px; }
    .stats-inner { max-width: 1100px; margin: 0 auto; }
    .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
    .stat-card { background: var(--text-white); border: 1px solid #e2e8f0; border-radius: var(--radius-lg); padding: 28px 20px; text-align: center; transition: var(--transition); box-shadow: 0 4px 12px rgba(0,0,0,0.03); }
    .stat-card:hover { transform: translateY(-4px); border-color: rgba(99,102,241,0.3); box-shadow: 0 12px 28px rgba(99,102,241,0.12); }
    .stat-value { font-size: 38px; font-weight: 800; color: var(--text-dark); margin-bottom: 6px; }
    .stat-label { font-size: 13px; color: var(--text-muted); font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }

    /* ===== FEATURES SECTION ===== */
    .features-section { background: var(--canvas-light); padding: 60px 24px 80px; }
    .features-inner { max-width: 1200px; margin: 0 auto; }
    .section-header { text-align: center; margin-bottom: 56px; }
    .section-label { font-size: 13px; font-weight: 600; color: #6366f1; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 12px; display: inline-block; padding: 4px 14px; background: rgba(99,102,241,0.08); border-radius: var(--radius-pill); }
    .section-header h2 { font-size: 36px; font-weight: 800; color: var(--text-dark); margin-bottom: 16px; }
    .section-header p { font-size: 17px; color: var(--text-muted); max-width: 620px; margin: 0 auto; }
    .features-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
    .feature-card { background: var(--text-white); border: 1px solid #e2e8f0; border-radius: var(--radius-lg); padding: 32px; transition: var(--transition); position: relative; overflow: hidden; }
    .feature-card::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: linear-gradient(180deg, #6366f1, #8b5cf6); transform: scaleY(0); transform-origin: top; transition: transform 400ms; }
    .feature-card:hover { border-color: rgba(99,102,241,0.3); box-shadow: 0 8px 24px rgba(0,0,0,0.08); transform: translateY(-4px); }
    .feature-card:hover::before { transform: scaleY(1); }
    .feature-icon { width: 52px; height: 52px; border-radius: 14px; background: rgba(99,102,241,0.08); display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 20px; transition: var(--transition); }
    .feature-card:hover .feature-icon { transform: scale(1.1) rotate(-5deg); background: linear-gradient(135deg, #6366f1, #8b5cf6); }
    .feature-card h3 { font-size: 18px; font-weight: 700; color: var(--text-dark); margin-bottom: 8px; }
    .feature-card p { font-size: 14px; color: var(--text-muted); line-height: 1.7; }
    .feature-tag { display: inline-block; margin-top: 16px; padding: 4px 12px; background: #f1f5f9; border-radius: 6px; font-family: 'JetBrains Mono'; font-size: 12px; color: var(--text-muted); }

    /* ===== ARCHITECTURE SECTION (dark) ===== */
    .arch-section { background: var(--hero-bg); padding: 80px 24px; position: relative; overflow: hidden; }
    .arch-section::before { content: ''; position: absolute; top: 0; right: 0; width: 400px; height: 400px; background: radial-gradient(circle, var(--accent-glow), transparent 60%); opacity: 0.1; }
    .arch-inner { max-width: 1200px; margin: 0 auto; position: relative; }
    .arch-inner .section-header h2 { color: var(--text-white); }
    .arch-inner .section-header p { color: var(--text-muted); }
    .arch-inner .section-label { color: var(--accent); background: var(--accent-light); }
    .arch-layers { display: flex; flex-direction: column; gap: 12px; }
    .arch-layer { display: flex; align-items: center; gap: 20px; padding: 20px 24px; background: var(--hero-card); border: 1px solid rgba(255,255,255,0.08); border-radius: var(--radius); transition: var(--transition); cursor: pointer; }
    .arch-layer:hover { border-color: rgba(99,102,241,0.3); background: var(--hero-card-dark); transform: translateX(8px); }
    .arch-layer-num { font-family: 'JetBrains Mono'; font-size: 13px; color: rgba(255,255,255,0.3); min-width: 32px; transition: color 250ms; }
    .arch-layer:hover .arch-layer-num { color: var(--accent); }
    .arch-layer-name { font-weight: 600; font-size: 16px; color: var(--text-white); min-width: 180px; }
    .arch-layer-desc { font-size: 14px; color: var(--text-muted); flex: 1; }
    .arch-layer-status { font-size: 12px; padding: 4px 10px; border-radius: var(--radius-pill); font-weight: 600; display: flex; align-items: center; gap: 6px; background: rgba(99,102,241,0.15); color: var(--accent); }
    .arch-layer-status::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: var(--accent); animation: pulse-dot 2s infinite; }

    /* ===== CIRCLE COUNTERS SECTION ===== */
    .circle-section { background: var(--canvas-light); padding: 80px 24px; }
    .circle-inner { max-width: 1100px; margin: 0 auto; }
    .circle-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 32px; }
    .circle-card { text-align: center; }
    .circle-svg { width: 160px; height: 160px; margin: 0 auto 16px; position: relative; }
    .circle-svg svg { transform: rotate(-90deg); }
    .circle-bg { fill: none; stroke: #e2e8f0; stroke-width: 8; }
    .circle-fill { fill: none; stroke: url(#indigo-grad); stroke-width: 8; stroke-linecap: round; stroke-dasharray: 440; stroke-dashoffset: 440; transition: stroke-dashoffset 1500ms cubic-bezier(0.16,1,0.3,1); }
    .circle-card.visible .circle-fill { stroke-dashoffset: var(--offset); }
    .circle-count { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); font-family: 'Poppins'; font-size: 32px; font-weight: 800; color: var(--text-dark); }
    .circle-label { font-size: 13px; color: var(--text-muted); font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }

    /* ===== ROADMAP SECTION ===== */
    .roadmap-section { background: var(--canvas-light); padding: 60px 24px 80px; }
    .roadmap-inner { max-width: 1100px; margin: 0 auto; }
    .roadmap-track { position: relative; display: flex; justify-content: space-between; padding: 40px 0; }
    .roadmap-track::before { content: ''; position: absolute; top: 50%; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #6366f1 0%, #6366f1 40%, #8b5cf6 50%, #e2e8f0 60%); transform: scaleX(0); transform-origin: left; transition: transform 1500ms cubic-bezier(0.16,1,0.3,1); }
    .roadmap-track.visible::before { transform: scaleX(1); }
    .roadmap-milestone { text-align: center; position: relative; z-index: 2; flex: 1; }
    .roadmap-dot { width: 16px; height: 16px; border-radius: 50%; margin: 0 auto 12px; border: 3px solid var(--canvas-light); position: relative; }
    .roadmap-milestone.done .roadmap-dot { background: #6366f1; box-shadow: 0 0 0 4px rgba(99,102,241,0.15); }
    .roadmap-milestone.active .roadmap-dot { background: #8b5cf6; box-shadow: 0 0 0 4px rgba(139,92,246,0.15); animation: pulse-ring 2s infinite; }
    @keyframes pulse-ring { 0%,100% { box-shadow: 0 0 0 4px rgba(139,92,246,0.15); } 50% { box-shadow: 0 0 0 8px rgba(139,92,246,0.08); } }
    .roadmap-milestone.planned .roadmap-dot { background: #cbd5e1; }
    .roadmap-status { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }
    .roadmap-milestone.done .roadmap-status { color: #6366f1; }
    .roadmap-milestone.active .roadmap-status { color: #8b5cf6; }
    .roadmap-milestone.planned .roadmap-status { color: #94a3b8; }
    .roadmap-milestone h4 { font-size: 14px; font-weight: 700; color: var(--text-dark); margin-bottom: 4px; }
    .roadmap-milestone p { font-size: 12px; color: var(--text-muted); max-width: 180px; margin: 0 auto; }

    /* ===== CTA SECTION (dark) ===== */
    .cta-section { padding: 80px 24px; }
    .cta-inner { max-width: 1100px; margin: 0 auto; }
    .cta-card { background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); border-radius: var(--radius-lg); padding: 64px 48px; text-align: center; position: relative; overflow: hidden; }
    .cta-card::before { content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, var(--accent-glow) 0%, transparent 50%); animation: rotate 20s linear infinite; opacity: 0.15; }
    @keyframes rotate { to { transform: rotate(360deg); } }
    .cta-card > * { position: relative; z-index: 1; }
    .cta-card h2 { font-size: 32px; font-weight: 800; color: var(--text-white); margin-bottom: 16px; }
    .cta-card p { font-size: 17px; color: var(--text-muted); max-width: 540px; margin: 0 auto 32px; }
    .cta-card .btn-read-more { font-size: 16px; padding: 16px 40px; }

    /* ===== FOOTER ===== */
    .footer { background: var(--hero-bg); padding: 48px 24px 32px; }
    .footer-inner { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 48px; }
    .footer-brand h4 { font-size: 18px; font-weight: 800; color: var(--text-white); margin-bottom: 12px; }
    .footer-brand p { font-size: 14px; color: var(--text-muted); max-width: 320px; line-height: 1.6; }
    .footer-col h5 { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-bottom: 16px; }
    .footer-col a { display: block; font-size: 14px; color: var(--text-muted); margin-bottom: 10px; transition: var(--transition); text-decoration: none; }
    .footer-col a:hover { color: var(--accent); transform: translateX(4px); }
    .footer-bottom { max-width: 1200px; margin: 32px auto 0; padding-top: 24px; border-top: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: space-between; font-size: 13px; color: var(--text-muted); }

    /* ===== RESPONSIVE ===== */
    @media (max-width: 1024px) {
      .features-grid { grid-template-columns: repeat(2,1fr); }
      .circle-grid { grid-template-columns: repeat(2,1fr); }
      .footer-inner { grid-template-columns: 1fr 1fr; }
      .hero-title { font-size: 40px; }
    }
    @media (max-width: 768px) {
      .nav-links { display: none; }
      .hero-container { flex-direction: column; min-height: auto; }
      .hero-left { padding: 100px 32px 40px; }
      .hero-right { padding: 20px; min-height: 400px; }
      .hero-title { font-size: 32px; }
      .stats-grid { grid-template-columns: repeat(2,1fr); }
      .features-grid { grid-template-columns: 1fr; }
      .circle-grid { grid-template-columns: repeat(2,1fr); }
      .arch-layer { flex-direction: column; align-items: flex-start; gap: 8px; }
      .arch-layer-name { min-width: auto; }
      .roadmap-track { flex-direction: column; gap: 24px; }
      .roadmap-track::before { display: none; }
      .cta-card { padding: 40px 24px; }
      .cta-card h2 { font-size: 24px; }
      .footer-inner { grid-template-columns: 1fr; gap: 24px; }
      .footer-bottom { flex-direction: column; gap: 8px; text-align: center; }
    }
    @media (max-width: 480px) {
      .hero-left { padding: 90px 20px 30px; }
      .hero-title { font-size: 28px; }
      .stats-grid { grid-template-columns: 1fr; }
      .circle-grid { grid-template-columns: 1fr; }
      .hero-actions { flex-direction: column; }
    }
  </style>
</head>
<body>

  <!-- Scroll Progress Bar -->
  <div id="scroll-bar"></div>

  <!-- Cursor Glow -->
  <div id="cursor-glow"></div>

  <!-- ===== HERO SECTION ===== -->
  <section class="hero-section">
    <div class="hero-container">
      <!-- Navigation inside dark hero -->
      <nav class="hero-nav" aria-label="Main Navigation">
        <a href="#" class="nav-brand">
          <span class="nav-brand-dot"></span>
          EvolvixOS
        </a>
        <div class="nav-links">
          <a href="#features">Agents</a>
          <a href="#features">AI Gateway</a>
          <a href="#features">Marketplace</a>
          <a href="#architecture">Architecture</a>
          <a href="#roadmap">Roadmap</a>
        </div>
        <div class="nav-cta">
          <a href="/login" class="btn-login">Log In</a>
          <a href="/register" class="btn-signup">Sign Up</a>
        </div>
      </nav>

      <!-- Split Hero: Left Text Content -->
      <div class="hero-left">
        <div class="hero-badge">
          <span class="hero-badge-dot"></span>
          34 Containers Running · Production Live
        </div>
        <h1 class="hero-title">
          <span class="gradient">AI ENGINEERING</span><br>
          Operating System
        </h1>
        <p class="hero-desc">
          Autonomous AI agents that design, build, test, and secure your software 24/7. 16 core agents, 24 AI providers, plugin marketplace, and enterprise-grade infrastructure.
        </p>
        <div class="hero-actions">
          <a href="#features" class="btn-read-more">READ MORE →</a>
          <a href="#architecture" class="btn-explore">Explore</a>
        </div>
      </div>

      <!-- Split Hero: Right 3D Visual -->
      <div class="hero-right">
        <div class="hero-visual">
          <div class="hero-circle"></div>
          
          <!-- Neural Network Canvas -->
          <canvas id="hero-canvas"></canvas>

          <!-- Floating Card 1: Active Agents -->
          <div class="float-card float-card-1">
            <div class="float-card-icon">🤖</div>
            <div class="float-card-label">Active Agents</div>
            <div class="float-card-value mono">16 Live</div>
            <div class="float-card-bar"><div class="float-card-bar-fill" style="width:85%"></div></div>
          </div>

          <!-- Floating Card 2: Tests Passing -->
          <div class="float-card float-card-2">
            <div class="float-card-icon">✅</div>
            <div class="float-card-label">Tests Passing</div>
            <div class="float-card-value indigo mono">615+</div>
            <div class="float-card-bar"><div class="float-card-bar-fill" style="width:98%"></div></div>
          </div>

          <!-- Floating Card 3: AI Providers -->
          <div class="float-card float-card-3">
            <div class="float-card-icon">🧠</div>
            <div class="float-card-label">AI Providers</div>
            <div class="float-card-value mono">24</div>
            <div class="float-card-bar"><div class="float-card-bar-fill" style="width:75%"></div></div>
          </div>

          <!-- Floating Card 4: Containers -->
          <div class="float-card float-card-4">
            <div class="float-card-icon">🐳</div>
            <div class="float-card-label">Containers</div>
            <div class="float-card-value indigo mono">34 Running</div>
            <div class="float-card-bar"><div class="float-card-bar-fill" style="width:92%"></div></div>
          </div>

          <!-- Phone Mockup — Agent Dashboard -->
          <div class="phone-mockup">
            <div>
              <div class="phone-screen-label">Agent Status</div>
              <div class="phone-screen-value">Code Reviewer: Active</div>
            </div>
            <div class="phone-progress-ring">
              <svg width="56" height="56">
                <defs>
                  <linearGradient id="ring-grad" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="#6366f1"/>
                    <stop offset="100%" stop-color="#8b5cf6"/>
                  </linearGradient>
                </defs>
                <circle cx="28" cy="28" r="24" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="4"/>
                <circle cx="28" cy="28" r="24" fill="none" stroke="url(#ring-grad)" stroke-width="4" stroke-linecap="round" stroke-dasharray="150" stroke-dashoffset="19.5" transform="rotate(-90 28 28)"/>
              </svg>
              <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-family:'Poppins';font-size:14px;font-weight:700;color:var(--accent)">87%</div>
            </div>
            <div class="phone-screen-label">Auto-Run</div>
            <div class="phone-screen-value" style="color:var(--accent)">✓ 5 Agents</div>
            <a href="#architecture" class="phone-login-btn" style="text-decoration:none;">View Dashboard</a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ===== STATS BAR ===== -->
  <section class="stats-section" id="stats">
    <div class="stats-inner">
      <div class="stats-grid reveal-stagger">
        <div class="stat-card">
          <div class="stat-value mono" data-count="615" data-suffix="+">0</div>
          <div class="stat-label">Tests Passing</div>
        </div>
        <div class="stat-card">
          <div class="stat-value mono" data-count="34">0</div>
          <div class="stat-label">Live Containers</div>
        </div>
        <div class="stat-card">
          <div class="stat-value mono" data-count="16">0</div>
          <div class="stat-label">Core Agents</div>
        </div>
        <div class="stat-card">
          <div class="stat-value mono" data-count="24">0</div>
          <div class="stat-label">AI Providers</div>
        </div>
      </div>
    </div>
  </section>

  <!-- ===== FEATURES GRID ===== -->
  <section class="features-section" id="features">
    <div class="features-inner">
      <div class="section-header reveal">
        <div class="section-label">Platform Capabilities</div>
        <h2>Engineered for Autonomous AI Workflows</h2>
        <p>From LLM routing to agent orchestration, secure execution, and plugin marketplace — EvolvixOS powers end-to-end AI engineering.</p>
      </div>
      <div class="features-grid reveal-stagger">
        <div class="feature-card">
          <div class="feature-icon">🧠</div>
          <h3>AI Gateway</h3>
          <p>24 providers, intelligent routing, caching, circuit breakers.</p>
          <span class="feature-tag">24 Providers · 10 LLM</span>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🧩</div>
          <h3>Plugin Marketplace</h3>
          <p>12 plugins, 8-step verification, dependency management, versioning.</p>
          <span class="feature-tag">12 Plugins · 8-Step Verification</span>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🔀</div>
          <h3>Agent Orchestration</h3>
          <p>DAG workflows, 9 step types, retry logic, 4 templates.</p>
          <span class="feature-tag">DAG · 9 Step Types</span>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🏢</div>
          <h3>Enterprise & SSO</h3>
          <p>SAML 2.0, OAuth2, multi-tenancy, GDPR compliance.</p>
          <span class="feature-tag">SAML · OAuth2 · GDPR</span>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🛡️</div>
          <h3>RBAC & Security</h3>
          <p>6 roles, 33 permissions, 14 resources, custom roles.</p>
          <span class="feature-tag">6 Roles · 33 Permissions</span>
        </div>
        <div class="feature-card">
          <div class="feature-icon">💻</div>
          <h3>Developer SDK & CLI</h3>
          <p>Python + TypeScript SDKs, system-wide CLI, project scaffolding.</p>
          <span class="feature-tag">Python · TypeScript · CLI</span>
        </div>
      </div>
    </div>
  </section>

  <!-- ===== ARCHITECTURE SECTION (dark) ===== -->
  <section class="arch-section" id="architecture">
    <div class="arch-inner">
      <div class="section-header reveal">
        <div class="section-label">Architecture</div>
        <h2>Six services, one platform</h2>
        <p>Modular microservices designed for continuous execution, high availability, and enterprise security.</p>
      </div>
      <div class="arch-layers reveal-stagger">
        <div class="arch-layer">
          <div class="arch-layer-num">01</div>
          <div class="arch-layer-name">AI Gateway</div>
          <div class="arch-layer-desc">Universal router for 24 AI providers with load balancing, caching, rate limiting</div>
          <div class="arch-layer-status">Live</div>
        </div>
        <div class="arch-layer">
          <div class="arch-layer-num">02</div>
          <div class="arch-layer-name">Agent Framework</div>
          <div class="arch-layer-desc">Agent lifecycle, task queue, memory management, gateway execution</div>
          <div class="arch-layer-status">Live</div>
        </div>
        <div class="arch-layer">
          <div class="arch-layer-num">03</div>
          <div class="arch-layer-name">Plugin Marketplace</div>
          <div class="arch-layer-desc">Discovery, installation, publishing, reviews, verification pipeline</div>
          <div class="arch-layer-status">Live</div>
        </div>
        <div class="arch-layer">
          <div class="arch-layer-num">04</div>
          <div class="arch-layer-name">Enterprise</div>
          <div class="arch-layer-desc">SSO, audit logs, multi-tenancy, GDPR, API usage tracking</div>
          <div class="arch-layer-status">Live</div>
        </div>
        <div class="arch-layer">
          <div class="arch-layer-num">05</div>
          <div class="arch-layer-name">Security</div>
          <div class="arch-layer-desc">RBAC, API keys, rate limiting, input validation, security headers</div>
          <div class="arch-layer-status">Live</div>
        </div>
        <div class="arch-layer">
          <div class="arch-layer-num">06</div>
          <div class="arch-layer-name">Infrastructure</div>
          <div class="arch-layer-desc">PostgreSQL, Redis, Docker, Nginx, WebSocket, task queue with DLQ</div>
          <div class="arch-layer-status">Live</div>
        </div>
      </div>
    </div>
  </section>

  <!-- ===== CIRCLE COUNTERS SECTION ===== -->
  <section class="circle-section">
    <div class="circle-inner">
      <div class="section-header reveal">
        <div class="section-label">Metrics</div>
        <h2>Production scale and system readiness</h2>
      </div>
      <div class="circle-grid reveal-stagger">
        <div class="circle-card" style="--offset: 9">
          <div class="circle-svg">
            <svg width="160" height="160">
              <defs>
                <linearGradient id="indigo-grad" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stop-color="#6366f1"/>
                  <stop offset="100%" stop-color="#8b5cf6"/>
                </linearGradient>
              </defs>
              <circle class="circle-bg" cx="80" cy="80" r="70"/>
              <circle class="circle-fill" cx="80" cy="80" r="70"/>
            </svg>
            <div class="circle-count mono" data-count="615" data-suffix="+">0</div>
          </div>
          <div class="circle-label">Tests Passing</div>
        </div>

        <div class="circle-card" style="--offset: 44">
          <div class="circle-svg">
            <svg width="160" height="160">
              <circle class="circle-bg" cx="80" cy="80" r="70"/>
              <circle class="circle-fill" cx="80" cy="80" r="70" style="stroke-dashoffset:44"/>
            </svg>
            <div class="circle-count mono" data-count="34">0</div>
          </div>
          <div class="circle-label">Containers</div>
        </div>

        <div class="circle-card" style="--offset: 66">
          <div class="circle-svg">
            <svg width="160" height="160">
              <circle class="circle-bg" cx="80" cy="80" r="70"/>
              <circle class="circle-fill" cx="80" cy="80" r="70" style="stroke-dashoffset:66"/>
            </svg>
            <div class="circle-count mono" data-count="47">0</div>
          </div>
          <div class="circle-label">API Endpoints</div>
        </div>

        <div class="circle-card" style="--offset: 35">
          <div class="circle-svg">
            <svg width="160" height="160">
              <circle class="circle-bg" cx="80" cy="80" r="70"/>
              <circle class="circle-fill" cx="80" cy="80" r="70" style="stroke-dashoffset:35"/>
            </svg>
            <div class="circle-count mono" data-count="33">0</div>
          </div>
          <div class="circle-label">RBAC Permissions</div>
        </div>
      </div>
    </div>
  </section>

  <!-- ===== ROADMAP ===== -->
  <section class="roadmap-section" id="roadmap">
    <div class="roadmap-inner">
      <div class="section-header reveal">
        <div class="section-label">Roadmap</div>
        <h2>Execution Milestones</h2>
      </div>
      <div class="roadmap-track reveal">
        <div class="roadmap-milestone done">
          <div class="roadmap-dot"></div>
          <div class="roadmap-status">✓ Completed</div>
          <h4>Core Platform</h4>
          <p>Phases 88-126: 16 core agents, AI gateway, plugin system</p>
        </div>
        <div class="roadmap-milestone done">
          <div class="roadmap-dot"></div>
          <div class="roadmap-status">✓ Completed</div>
          <h4>Infrastructure Hardening</h4>
          <p>34 containers, Docker healthchecks, Redis DLQ queues</p>
        </div>
        <div class="roadmap-milestone active">
          <div class="roadmap-dot"></div>
          <div class="roadmap-status">● Active</div>
          <h4>Premium Platform Launch</h4>
          <p>SaaS dashboard, sub-tier metering, workspace analytics</p>
        </div>
        <div class="roadmap-milestone planned">
          <div class="roadmap-dot"></div>
          <div class="roadmap-status">○ Planned</div>
          <h4>Public API & Marketplace</h4>
          <p>Third-party agent plugins, open developer portal</p>
        </div>
        <div class="roadmap-milestone planned">
          <div class="roadmap-dot"></div>
          <div class="roadmap-status">○ Planned</div>
          <h4>Enterprise Expansion</h4>
          <p>Custom VPC deployments, dedicated agent clusters</p>
        </div>
      </div>
    </div>
  </section>

  <!-- ===== CTA SECTION (dark) ===== -->
  <section class="cta-section">
    <div class="cta-inner">
      <div class="cta-card reveal">
        <h2>Let AI engineering handle the heavy lifting</h2>
        <p>Deploy autonomous agents that write, review, test, and secure your code — 24/7.</p>
        <a href="#features" class="btn-read-more">Explore Agents →</a>
      </div>
    </div>
  </section>

  <!-- ===== FOOTER ===== -->
  <footer class="footer">
    <div class="footer-inner">
      <div class="footer-brand">
        <h4>EvolvixOS</h4>
        <p>The AI Engineering Operating System. Built by Protremix.</p>
      </div>
      <div class="footer-col">
        <h5>Platform</h5>
        <a href="#features">Agents</a>
        <a href="#features">AI Gateway</a>
        <a href="#features">Marketplace</a>
        <a href="#features">Orchestration</a>
      </div>
      <div class="footer-col">
        <h5>Developers</h5>
        <a href="#architecture">Smart Contracts</a>
        <a href="#architecture">Documentation</a>
        <a href="#features">SDK</a>
        <a href="https://github.com" target="_blank" rel="noopener">GitHub</a>
      </div>
      <div class="footer-col">
        <h5>Enterprise</h5>
        <a href="#features">SSO & SAML</a>
        <a href="#features">RBAC</a>
        <a href="#architecture">Monitoring</a>
        <a href="#architecture">Infrastructure</a>
      </div>
    </div>
    <div class="footer-bottom">
      <div>© 2026 EvolvixOS · Powered by Protremix</div>
      <div>evolvixos.com · 62.238.61.145</div>
    </div>
  </footer>

  <!-- ===== JAVASCRIPT ===== -->
  <script>
    // ===== CURSOR GLOW =====
    const glow = document.getElementById('cursor-glow');
    document.addEventListener('mousemove', e => {
      glow.style.left = e.clientX + 'px';
      glow.style.top = e.clientY + 'px';
    });

    // ===== SCROLL PROGRESS =====
    const scrollBar = document.getElementById('scroll-bar');
    window.addEventListener('scroll', () => {
      const totalScroll = document.body.scrollHeight - window.innerHeight;
      const pct = totalScroll > 0 ? (window.scrollY / totalScroll) * 100 : 0;
      scrollBar.style.width = pct + '%';
    });

    // ===== SCROLL REVEAL =====
    const observer = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('visible');
        }
      });
    }, { threshold: 0.15 });
    document.querySelectorAll('.reveal, .reveal-stagger, .circle-card, .roadmap-track').forEach(el => observer.observe(el));

    // ===== ANIMATED COUNTERS =====
    const counterObs = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        const el = e.target;
        const target = parseInt(el.dataset.count);
        const suffix = el.dataset.suffix || '';
        let current = 0;
        const step = target / 60;
        const tick = () => {
          current += step;
          if (current >= target) {
            el.textContent = target + suffix;
            return;
          }
          el.textContent = Math.floor(current) + suffix;
          requestAnimationFrame(tick);
        };
        tick();
        counterObs.unobserve(el);
      });
    }, { threshold: 0.5 });
    document.querySelectorAll('[data-count]').forEach(el => counterObs.observe(el));

    // ===== HERO CANVAS — Neural Network Animation =====
    const canvas = document.getElementById('hero-canvas');
    const ctx = canvas.getContext('2d');
    let W, H;
    let mouse = { x: -1000, y: -1000 };

    function resize() {
      W = canvas.width = canvas.offsetWidth;
      H = canvas.height = canvas.offsetHeight;
      initNetwork();
    }

    let layers = [];
    let pulses = [];

    function initNetwork() {
      layers = [];
      pulses = [];
      const layerCounts = [4, 6, 6, 4];
      const paddingX = 60;
      const usableW = W - paddingX * 2;

      for (let l = 0; l < layerCounts.length; l++) {
        const count = layerCounts[l];
        const x = paddingX + (usableW / (layerCounts.length - 1)) * l;
        const layerNodes = [];
        const usableH = H - 100;
        const stepY = usableH / (count + 1);

        for (let i = 0; i < count; i++) {
          const baseY = 50 + stepY * (i + 1);
          layerNodes.push({
            x: x,
            y: baseY,
            baseX: x,
            baseY: baseY,
            r: 5,
            glow: 0,
            seed: Math.random() * Math.PI * 2
          });
        }
        layers.push(layerNodes);
      }
    }

    window.addEventListener('resize', resize);
    setTimeout(resize, 50);

    canvas.addEventListener('mousemove', e => {
      const rect = canvas.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
    });

    canvas.addEventListener('mouseleave', () => {
      mouse.x = -1000;
      mouse.y = -1000;
    });

    let frame = 0;

    function animate() {
      frame++;
      ctx.clearRect(0, 0, W, H);

      // Spawn signal pulses periodically
      if (frame % 25 === 0 && layers.length > 0) {
        const startNodeIdx = Math.floor(Math.random() * layers[0].length);
        pulses.push({
          layerIdx: 0,
          fromIdx: startNodeIdx,
          toIdx: Math.floor(Math.random() * layers[1].length),
          progress: 0,
          speed: 0.02 + Math.random() * 0.015
        });
      }

      // Update node positions and glow decay
      layers.forEach(layer => {
        layer.forEach(n => {
          n.seed += 0.02;
          const oscX = Math.cos(n.seed) * 3;
          const oscY = Math.sin(n.seed) * 4;
          
          let targetX = n.baseX + oscX;
          let targetY = n.baseY + oscY;

          // Mouse repel
          const dx = targetX - mouse.x;
          const dy = targetY - mouse.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 90 && dist > 0) {
            const force = (90 - dist) / 90 * 18;
            targetX += (dx / dist) * force;
            targetY += (dy / dist) * force;
          }

          n.x += (targetX - n.x) * 0.1;
          n.y += (targetY - n.y) * 0.1;

          if (n.glow > 0) n.glow -= 0.02;
          if (n.glow < 0) n.glow = 0;
        });
      });

      // Draw connections between adjacent layers
      for (let l = 0; l < layers.length - 1; l++) {
        const l1 = layers[l];
        const l2 = layers[l + 1];

        for (let i = 0; i < l1.length; i++) {
          for (let j = 0; j < l2.length; j++) {
            const n1 = l1[i];
            const n2 = l2[j];

            ctx.beginPath();
            ctx.moveTo(n1.x, n1.y);
            ctx.lineTo(n2.x, n2.y);
            ctx.strokeStyle = 'rgba(99, 102, 241, 0.12)';
            ctx.lineWidth = 1;
            ctx.stroke();
          }
        }
      }

      // Update and draw signal pulses
      for (let p = pulses.length - 1; p >= 0; p--) {
        const pulse = pulses[p];
        pulse.progress += pulse.speed;

        const lFrom = layers[pulse.layerIdx];
        const lTo = layers[pulse.layerIdx + 1];

        if (!lFrom || !lTo) {
          pulses.splice(p, 1);
          continue;
        }

        const nFrom = lFrom[pulse.fromIdx];
        const nTo = lTo[pulse.toIdx];

        if (!nFrom || !nTo) {
          pulses.splice(p, 1);
          continue;
        }

        const px = nFrom.x + (nTo.x - nFrom.x) * pulse.progress;
        const py = nFrom.y + (nTo.y - nFrom.y) * pulse.progress;

        // Draw pulse particle
        ctx.beginPath();
        ctx.arc(px, py, 3.5, 0, Math.PI * 2);
        ctx.fillStyle = '#a78bfa';
        ctx.shadowColor = '#8b5cf6';
        ctx.shadowBlur = 10;
        ctx.fill();
        ctx.shadowBlur = 0;

        // When pulse arrives at destination node
        if (pulse.progress >= 1) {
          nTo.glow = 1.0; // Trigger glow

          // If not at final layer, continue pulse to next layer
          if (pulse.layerIdx + 1 < layers.length - 1) {
            pulse.layerIdx++;
            pulse.fromIdx = pulse.toIdx;
            pulse.toIdx = Math.floor(Math.random() * layers[pulse.layerIdx + 1].length);
            pulse.progress = 0;
          } else {
            pulses.splice(p, 1);
          }
        }
      }

      // Draw neurons (nodes)
      layers.forEach((layer, lIdx) => {
        layer.forEach(n => {
          ctx.beginPath();
          const radius = n.r + n.glow * 3;
          ctx.arc(n.x, n.y, radius, 0, Math.PI * 2);

          const alpha = 0.4 + n.glow * 0.6;
          ctx.fillStyle = n.glow > 0.3 ? `rgba(167, 139, 250, ${alpha})` : `rgba(99, 102, 241, ${alpha})`;
          
          if (n.glow > 0.2) {
            ctx.shadowColor = '#6366f1';
            ctx.shadowBlur = 12 * n.glow;
          }
          ctx.fill();
          ctx.shadowBlur = 0;

          // Inner core
          ctx.beginPath();
          ctx.arc(n.x, n.y, 2, 0, Math.PI * 2);
          ctx.fillStyle = '#ffffff';
          ctx.fill();
        });
      });

      requestAnimationFrame(animate);
    }

    animate();
  </script>
</body>
</html>
"""

with open("evolvixos-landing.html", "w") as f:
    f.write(html_content)

print("Generated evolvixos-landing.html successfully! Size:", len(html_content))
