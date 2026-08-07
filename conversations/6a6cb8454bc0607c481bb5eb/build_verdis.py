content = """<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verdis Chain | The World's First Green Blockchain Engineered in Rust</title>
    <meta name="description" content="Verdis Chain is a carbon-negative, high-performance Layer-1 blockchain built on Substrate and Rust. Featuring native DPoS consensus, EVM compatibility, AMM DEX, and zero-carbon proofs.">
    <meta property="og:title" content="Verdis Chain — Green Blockchain Infrastructure">
    <meta property="og:description" content="Engineered in Rust. Carbon-negative, ultra-fast, and EVM compatible. Explore the architecture.">
    <meta property="og:type" content="website">

    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">

    <style>
        /* ==========================================================================
           DESIGN SYSTEM & CSS VARIABLES (LIGHT THEME)
           ========================================================================== */
        :root {
            --bg-main: #f8fafc;
            --bg-card: #ffffff;
            --bg-card-hover: #f1f5f9;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --text-light: #94a3b8;
            --border-color: #e2e8f0;
            --border-focus: #a7f3d0;

            --primary: #00a86b;
            --primary-hover: #009460;
            --primary-light: #ecfdf5;
            --primary-border: #a7f3d0;

            --accent-emerald: #10b981;
            --accent-teal: #2dd4bf;
            --accent-indigo: #6366f1;

            --font-heading: 'Space Grotesk', -apple-system, sans-serif;
            --font-body: 'Inter', -apple-system, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;

            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 24px;

            --shadow-sm: 0 2px 8px rgba(15, 23, 42, 0.04);
            --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
            --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.10);
            --shadow-xl: 0 16px 36px rgba(15, 23, 42, 0.12);
            --shadow-glow: 0 0 25px rgba(0, 168, 107, 0.22);

            --mouse-x: 50vw;
            --mouse-y: 50vh;
        }

        /* Reset & Base Styles */
        *, *::before, *::after {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        html {
            scroll-behavior: smooth;
            font-size: 16px;
            background-color: var(--bg-main);
            color: var(--text-main);
            font-family: var(--font-body);
            overflow-x: hidden;
            -webkit-font-smoothing: antialiased;
        }

        body {
            position: relative;
            min-height: 100vh;
            line-height: 1.6;
            overflow-x: hidden;
        }

        /* WCAG Focus Visible */
        a:focus-visible, button:focus-visible {
            outline: 3px solid var(--primary);
            outline-offset: 3px;
            border-radius: 4px;
        }

        /* Typography */
        h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-heading);
            color: var(--text-main);
            line-height: 1.15;
            letter-spacing: -0.02em;
        }

        .font-mono {
            font-family: var(--font-mono);
        }

        /* Gradient Text */
        .gradient-text {
            background: linear-gradient(135deg, #00a86b 0%, #10b981 50%, #2dd4bf 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: inline-block;
        }

        /* ==========================================================================
           1. CURSOR GLOW EFFECT
           ========================================================================== */
        #cursor-glow {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            pointer-events: none;
            z-index: 9999;
            background: radial-gradient(600px circle at var(--mouse-x) var(--mouse-y), rgba(0, 168, 107, 0.08), transparent 80%);
            transition: opacity 0.3s ease;
        }

        /* ==========================================================================
           2. SCROLL PROGRESS BAR
           ========================================================================== */
        #scroll-progress-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: rgba(226, 232, 240, 0.5);
            z-index: 10000;
        }

        #scroll-progress {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #00a86b, #10b981, #2dd4bf);
            transition: width 0.1s linear;
        }

        /* ==========================================================================
           HEADER & NAVIGATION (11. NAV UNDERLINE & 12. BUTTON SHINE)
           ========================================================================== */
        header {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            z-index: 1000;
            background: rgba(248, 250, 252, 0.88);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-bottom: 1px solid rgba(226, 232, 240, 0.8);
            transition: padding 0.3s ease, background-color 0.3s ease;
        }

        .nav-container {
            max-width: 1280px;
            margin: 0 auto;
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .brand-logo {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            text-decoration: none;
            font-family: var(--font-heading);
            font-weight: 700;
            font-size: 1.4rem;
            color: var(--text-main);
        }

        .logo-icon {
            width: 38px;
            height: 38px;
            background: linear-gradient(135deg, var(--primary), var(--accent-teal));
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            box-shadow: 0 4px 12px rgba(0, 168, 107, 0.3);
        }

        .nav-links {
            display: flex;
            align-items: center;
            gap: 2.25rem;
            list-style: none;
        }

        .nav-link {
            position: relative;
            text-decoration: none;
            color: var(--text-muted);
            font-weight: 500;
            font-size: 0.95rem;
            padding: 0.5rem 0;
            transition: color 0.2s ease;
        }

        .nav-link:hover {
            color: var(--primary);
        }

        /* 11. Nav Underline Animation */
        .nav-link::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 2px;
            background: var(--primary);
            transform: scaleX(0);
            transform-origin: right;
            transition: transform 0.3s cubic-bezier(0.65, 0, 0.35, 1);
        }

        .nav-link:hover::after {
            transform: scaleX(1);
            transform-origin: left;
        }

        .nav-actions {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        /* 12. Button Shine Effect */
        .btn-shine {
            position: relative;
            overflow: hidden;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            padding: 0.75rem 1.5rem;
            border-radius: var(--radius-md);
            font-family: var(--font-body);
            font-weight: 600;
            font-size: 0.95rem;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.25s ease;
            min-height: 44px;
        }

        .btn-shine::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(255, 255, 255, 0.45),
                transparent
            );
            transition: left 0.65s ease;
        }

        .btn-shine:hover::before {
            left: 100%;
        }

        .btn-primary {
            background: var(--primary);
            color: white;
            border: none;
            box-shadow: var(--shadow-md), 0 2px 8px rgba(0, 168, 107, 0.25);
        }

        .btn-primary:hover {
            background: var(--primary-hover);
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg), var(--shadow-glow);
        }

        .btn-secondary {
            background: white;
            color: var(--text-main);
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-sm);
        }

        .btn-secondary:hover {
            border-color: var(--primary);
            color: var(--primary);
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }

        /* Mobile Menu Button */
        .mobile-toggle {
            display: none;
            background: none;
            border: none;
            cursor: pointer;
            padding: 0.5rem;
            color: var(--text-main);
            min-height: 44px;
            min-width: 44px;
        }

        /* ==========================================================================
           SECTION 1: HERO SECTION (FULL SCREEN, CINEMATIC)
           ========================================================================== */
        .hero-section {
            position: relative;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 8rem 2rem 4rem;
            overflow: hidden;
            background: radial-gradient(circle at 50% 20%, #f0fdf4 0%, #f8fafc 70%);
        }

        /* 9. Hero Canvas Particle Network */
        #hero-canvas {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
            pointer-events: auto;
        }

        /* 8. Floating Gradient Blobs */
        .blob-container {
            position: absolute;
            inset: 0;
            pointer-events: none;
            z-index: 2;
            overflow: hidden;
        }

        .blob {
            position: absolute;
            border-radius: 50%;
            filter: blur(90px);
            opacity: 0.35;
            animation: floatBlob 20s infinite ease-in-out alternate;
        }

        .blob-1 {
            top: -10%;
            left: 15%;
            width: 500px;
            height: 500px;
            background: #a7f3d0;
            animation-duration: 18s;
        }

        .blob-2 {
            top: 30%;
            right: 10%;
            width: 450px;
            height: 450px;
            background: #99f6e4;
            animation-duration: 22s;
            animation-delay: -5s;
        }

        .blob-3 {
            bottom: 5%;
            left: 30%;
            width: 400px;
            height: 400px;
            background: #6ee7b7;
            animation-duration: 25s;
            animation-delay: -10s;
        }

        @keyframes floatBlob {
            0% { transform: translate(0, 0) scale(1); }
            33% { transform: translate(40px, -60px) scale(1.1); }
            66% { transform: translate(-30px, 40px) scale(0.92); }
            100% { transform: translate(20px, -20px) scale(1.05); }
        }

        .hero-content {
            position: relative;
            z-index: 10;
            max-width: 900px;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        /* Badge with Pulsing Dot */
        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.6rem;
            padding: 0.45rem 1.1rem;
            border-radius: 100px;
            background: rgba(236, 253, 245, 0.9);
            border: 1px solid var(--primary-border);
            color: var(--primary);
            font-family: var(--font-mono);
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 2rem;
            box-shadow: 0 2px 10px rgba(0, 168, 107, 0.1);
            backdrop-filter: blur(8px);
        }

        .pulse-dot {
            width: 8px;
            height: 8px;
            background-color: var(--primary);
            border-radius: 50%;
            position: relative;
        }

        .pulse-dot::after {
            content: '';
            position: absolute;
            inset: -4px;
            border-radius: 50%;
            background-color: var(--primary);
            opacity: 0.6;
            animation: pulseRing 1.8s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
        }

        @keyframes pulseRing {
            0% { transform: scale(0.5); opacity: 0.8; }
            100% { transform: scale(2.2); opacity: 0; }
        }

        /* 10. Staggered Text Reveals */
        .hero-stagger-1 {
            opacity: 0;
            transform: translateY(30px);
            animation: slideUpFade 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards 0.1s;
        }

        .hero-stagger-2 {
            opacity: 0;
            transform: translateY(30px);
            animation: slideUpFade 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards 0.3s;
        }

        .hero-stagger-3 {
            opacity: 0;
            transform: translateY(30px);
            animation: slideUpFade 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards 0.5s;
        }

        .hero-stagger-4 {
            opacity: 0;
            transform: translateY(30px);
            animation: slideUpFade 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards 0.7s;
        }

        @keyframes slideUpFade {
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .hero-title {
            font-size: clamp(2.5rem, 5vw + 1rem, 4.25rem);
            font-weight: 700;
            line-height: 1.1;
            margin-bottom: 1.5rem;
            letter-spacing: -0.03em;
        }

        .hero-subtitle {
            font-size: clamp(1.1rem, 2vw, 1.35rem);
            color: var(--text-muted);
            max-width: 680px;
            margin-bottom: 2.5rem;
            font-weight: 400;
        }

        .hero-ctas {
            display: flex;
            align-items: center;
            gap: 1.25rem;
            flex-wrap: wrap;
            justify-content: center;
        }

        .scroll-indicator {
            position: absolute;
            bottom: 2rem;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.5rem;
            color: var(--text-muted);
            font-size: 0.8rem;
            font-family: var(--font-mono);
            z-index: 10;
            opacity: 0.8;
            text-decoration: none;
            transition: opacity 0.2s ease;
        }

        .scroll-indicator:hover {
            opacity: 1;
            color: var(--primary);
        }

        .scroll-arrow {
            width: 20px;
            height: 20px;
            animation: bounceArrow 2s infinite;
        }

        @keyframes bounceArrow {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(6px); }
            60% { transform: translateY(3px); }
        }

        /* ==========================================================================
           SECTION HEADER UTILITY (UNIQUE SECTION DESIGNS)
           ========================================================================== */
        .section-header {
            text-align: center;
            max-width: 750px;
            margin: 0 auto 4rem;
        }

        .section-tag {
            display: inline-block;
            font-family: var(--font-mono);
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--primary);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.75rem;
            background: var(--primary-light);
            padding: 0.25rem 0.75rem;
            border-radius: 100px;
            border: 1px solid var(--primary-border);
        }

        .section-title {
            font-size: clamp(2rem, 3.5vw, 2.8rem);
            font-weight: 700;
            margin-bottom: 1rem;
        }

        .section-desc {
            font-size: 1.1rem;
            color: var(--text-muted);
        }

        /* 3. Intersection Observer Scroll Reveal */
        .reveal {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1), transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .reveal.active {
            opacity: 1;
            transform: translateY(0);
        }

        /* 13. Card Hover Lift + Shadow Utility */
        .hover-lift {
            transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.3s ease;
        }

        .hover-lift:hover {
            transform: translateY(-6px);
            box-shadow: var(--shadow-xl), 0 0 20px rgba(0, 168, 107, 0.1);
            border-color: var(--primary-border);
        }

        /* ==========================================================================
           SECTION 2: HORIZONTAL SCROLL FEATURES (PINNED/STICKY)
           ========================================================================== */
        .horizontal-scroll-wrapper {
            position: relative;
            height: 260vh; /* Extra scroll distance for horizontal movement */
            background: #ffffff;
            border-top: 1px solid var(--border-color);
            border-bottom: 1px solid var(--border-color);
        }

        .horizontal-sticky-container {
            position: sticky;
            top: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            overflow: hidden;
            padding: 3rem 0;
        }

        .horizontal-header {
            margin-bottom: 2rem;
            padding: 0 2rem;
        }

        .horizontal-track-container {
            width: 100%;
            overflow: hidden;
        }

        /* 7. Horizontal Scroll Section */
        .horizontal-track {
            display: flex;
            gap: 2rem;
            padding: 1rem 5vw;
            width: max-content;
            will-change: transform;
            transition: transform 0.1s ease-out;
        }

        .feature-card {
            width: 380px;
            flex-shrink: 0;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 2.25rem;
            box-shadow: var(--shadow-md);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
        }

        .feature-icon-box {
            width: 52px;
            height: 52px;
            border-radius: var(--radius-md);
            background: var(--primary-light);
            border: 1px solid var(--primary-border);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary);
            margin-bottom: 1.5rem;
        }

        .feature-card h3 {
            font-size: 1.35rem;
            margin-bottom: 0.75rem;
        }

        .feature-card p {
            color: var(--text-muted);
            font-size: 0.95rem;
            line-height: 1.6;
            margin-bottom: 1.75rem;
        }

        .tag-pill {
            display: inline-block;
            align-self: flex-start;
            padding: 0.3rem 0.75rem;
            border-radius: 100px;
            background: #f1f5f9;
            color: var(--text-main);
            font-family: var(--font-mono);
            font-size: 0.75rem;
            font-weight: 600;
            border: 1px solid var(--border-color);
        }

        /* ==========================================================================
           SECTION 3: VERTICAL TIMELINE (ARCHITECTURE LAYERS)
           ========================================================================== */
        .timeline-section {
            padding: 7rem 2rem;
            background: var(--bg-main);
            position: relative;
        }

        .timeline-container {
            max-width: 1000px;
            margin: 0 auto;
            position: relative;
            padding: 2rem 0;
            display: flex;
            flex-direction: column;
        }

        /* 14. Timeline Line Fill Animation */
        .timeline-center-line {
            position: absolute;
            top: 0;
            bottom: 0;
            left: 50%;
            width: 4px;
            background: var(--border-color);
            transform: translateX(-50%);
            border-radius: 2px;
        }

        .timeline-line-fill {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 0%;
            background: linear-gradient(180deg, var(--primary), var(--accent-teal));
            border-radius: 2px;
            transition: height 0.1s linear;
        }

        .timeline-item {
            display: flex;
            justify-content: flex-end;
            padding-right: 50px;
            position: relative;
            margin-bottom: 4rem;
            width: 50%;
        }

        .timeline-item.right {
            align-self: flex-end;
            margin-left: 50%;
            padding-right: 0;
            padding-left: 50px;
            justify-content: flex-start;
        }

        .timeline-dot {
            position: absolute;
            top: 24px;
            right: -12px;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: white;
            border: 4px solid var(--primary);
            box-shadow: 0 0 10px rgba(0, 168, 107, 0.4);
            z-index: 5;
            transition: transform 0.3s ease;
        }

        .timeline-item.right .timeline-dot {
            right: auto;
            left: -12px;
        }

        .timeline-card {
            background: white;
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 2rem;
            box-shadow: var(--shadow-md);
            width: 100%;
            max-width: 440px;
            position: relative;
        }

        .timeline-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.75rem;
        }

        .timeline-number {
            font-family: var(--font-mono);
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--primary);
        }

        .status-badge {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-family: var(--font-mono);
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--primary);
            background: var(--primary-light);
            padding: 0.25rem 0.6rem;
            border-radius: 100px;
            border: 1px solid var(--primary-border);
        }

        .timeline-card h3 {
            font-size: 1.25rem;
            margin-bottom: 0.5rem;
        }

        .timeline-card p {
            color: var(--text-muted);
            font-size: 0.92rem;
            line-height: 1.55;
        }

        /* ==========================================================================
           SECTION 4: 3D TILT CARDS (PALLETS)
           ========================================================================== */
        .pallets-section {
            padding: 7rem 2rem;
            background: #ffffff;
            border-top: 1px solid var(--border-color);
            border-bottom: 1px solid var(--border-color);
        }

        /* 6. 3D Tilt Cards Container */
        .pallets-grid {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 2rem;
            perspective: 1000px;
        }

        .pallet-card {
            background: var(--bg-main);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 2rem;
            position: relative;
            transform-style: preserve-3d;
            transition: transform 0.15s ease-out, box-shadow 0.15s ease-out, border-color 0.2s ease;
            cursor: pointer;
            box-shadow: var(--shadow-md);
        }

        .pallet-card:hover {
            border-color: var(--primary);
            box-shadow: var(--shadow-xl), 0 0 25px rgba(0, 168, 107, 0.15);
        }

        .pallet-glare {
            position: absolute;
            inset: 0;
            border-radius: var(--radius-lg);
            background: radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.6), transparent 70%);
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.15s ease-out;
            z-index: 10;
        }

        .pallet-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.25rem;
            transform: translateZ(30px);
        }

        .pallet-name {
            font-family: var(--font-mono);
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text-main);
        }

        .tests-badge {
            font-family: var(--font-mono);
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--primary);
            background: var(--primary-light);
            border: 1px solid var(--primary-border);
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
        }

        .pallet-card p {
            color: var(--text-muted);
            font-size: 0.92rem;
            line-height: 1.6;
            margin-bottom: 1.5rem;
            transform: translateZ(20px);
        }

        .pallet-footer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-family: var(--font-mono);
            font-size: 0.8rem;
            color: var(--text-light);
            transform: translateZ(25px);
            border-top: 1px dashed var(--border-color);
            padding-top: 1rem;
        }

        /* ==========================================================================
           SECTION 5: CIRCLE COUNTERS (STATS)
           ========================================================================== */
        .stats-section {
            padding: 7rem 2rem;
            background: var(--bg-main);
        }

        .stats-grid {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 2.5rem;
        }

        .stat-card {
            background: white;
            border: 1px solid var(--border-color);
            border-radius: var(--radius-xl);
            padding: 2.5rem 1.5rem;
            text-align: center;
            box-shadow: var(--shadow-md);
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        /* 5. SVG Progress Rings & 4. Animated Counters */
        .ring-container {
            position: relative;
            width: 160px;
            height: 160px;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .ring-svg {
            transform: rotate(-90deg);
            width: 100%;
            height: 100%;
        }

        .ring-bg {
            fill: none;
            stroke: #f1f5f9;
            stroke-width: 8;
        }

        .ring-circle {
            fill: none;
            stroke: url(#ring-gradient);
            stroke-width: 8;
            stroke-linecap: round;
            stroke-dasharray: 440;
            stroke-dashoffset: 440;
            transition: stroke-dashoffset 2s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .ring-content {
            position: absolute;
            inset: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: var(--font-mono);
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--text-main);
        }

        .stat-label {
            font-family: var(--font-heading);
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }

        .stat-sub {
            font-size: 0.85rem;
            color: var(--text-muted);
        }

        /* ==========================================================================
           SECTION 6: ROADMAP (PARALLAX DEPTH)
           ========================================================================== */
        .roadmap-section {
            padding: 7rem 2rem;
            background: #ffffff;
            border-top: 1px solid var(--border-color);
            position: relative;
            overflow: hidden;
        }

        .roadmap-container {
            max-width: 1280px;
            margin: 0 auto;
            position: relative;
        }

        /* 15. Parallax Depth Roadmap Cards */
        .roadmap-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 1.5rem;
            position: relative;
            z-index: 5;
        }

        .roadmap-card {
            background: var(--bg-main);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 1.75rem;
            box-shadow: var(--shadow-md);
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            will-change: transform;
            transition: transform 0.1s ease-out;
        }

        .roadmap-card.done {
            border-top: 4px solid var(--primary);
        }

        .roadmap-card.active {
            border-top: 4px solid var(--accent-indigo);
            background: #f5f3ff;
            border-color: #c7d2fe;
            box-shadow: 0 10px 25px rgba(99, 102, 241, 0.15);
        }

        .roadmap-card.planned {
            border-top: 4px solid #cbd5e1;
            opacity: 0.85;
        }

        .roadmap-phase {
            font-family: var(--font-mono);
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
        }

        .roadmap-card h3 {
            font-size: 1.15rem;
            margin-bottom: 1rem;
        }

        .roadmap-status {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.25rem 0.6rem;
            border-radius: 100px;
            font-family: var(--font-mono);
            font-size: 0.72rem;
            font-weight: 700;
            margin-bottom: 1.25rem;
        }

        .roadmap-status.status-done {
            background: var(--primary-light);
            color: var(--primary);
            border: 1px solid var(--primary-border);
        }

        .roadmap-status.status-active {
            background: #e0e7ff;
            color: var(--accent-indigo);
            border: 1px solid #a5b4fc;
        }

        .roadmap-status.status-planned {
            background: #f1f5f9;
            color: var(--text-muted);
            border: 1px solid #e2e8f0;
        }

        .roadmap-list {
            list-style: none;
            font-size: 0.88rem;
            color: var(--text-muted);
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .roadmap-list li {
            display: flex;
            align-items: flex-start;
            gap: 0.5rem;
        }

        .roadmap-list li::before {
            content: '•';
            color: var(--primary);
            font-weight: bold;
        }

        .roadmap-card.active .roadmap-list li::before {
            color: var(--accent-indigo);
        }

        /* Background Parallax Mesh Lines */
        .roadmap-bg-decor {
            position: absolute;
            inset: 0;
            pointer-events: none;
            opacity: 0.05;
            background-image: radial-gradient(var(--text-main) 1px, transparent 1px);
            background-size: 24px 24px;
        }

        /* ==========================================================================
           SECTION 7: CTA + FOOTER
           ========================================================================== */
        .cta-section {
            padding: 6rem 2rem;
            background: var(--bg-main);
        }

        .cta-box {
            max-width: 1100px;
            margin: 0 auto;
            background: linear-gradient(135deg, #00a86b 0%, #10b981 50%, #059669 100%);
            border-radius: var(--radius-xl);
            padding: 5rem 3rem;
            text-align: center;
            color: white;
            position: relative;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0, 168, 107, 0.3);
        }

        /* Dynamic Conic Gradient Background Highlight */
        .cta-glow-bg {
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: conic-gradient(from 0deg, transparent 0deg, rgba(255, 255, 255, 0.15) 60deg, transparent 120deg);
            animation: rotateConic 15s linear infinite;
            pointer-events: none;
        }

        @keyframes rotateConic {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        .cta-content {
            position: relative;
            z-index: 5;
            max-width: 700px;
            margin: 0 auto;
        }

        .cta-box h2 {
            color: white;
            font-size: clamp(2.2rem, 4vw, 3rem);
            margin-bottom: 1.25rem;
        }

        .cta-box p {
            font-size: 1.15rem;
            opacity: 0.95;
            margin-bottom: 2.5rem;
        }

        .cta-btn {
            background: white;
            color: var(--primary);
            font-weight: 700;
            padding: 1rem 2.25rem;
            font-size: 1.05rem;
            border-radius: var(--radius-md);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        }

        .cta-btn:hover {
            background: #f8fafc;
            color: var(--primary-hover);
            transform: translateY(-3px);
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.2);
        }

        /* FOOTER */
        footer {
            background: #0f172a;
            color: #94a3b8;
            padding: 5rem 2rem 2rem;
            border-top: 1px solid #1e293b;
        }

        .footer-container {
            max-width: 1280px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 2fr repeat(3, 1fr);
            gap: 4rem;
            margin-bottom: 4rem;
        }

        .footer-brand {
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }

        .footer-logo {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-family: var(--font-heading);
            font-size: 1.4rem;
            font-weight: 700;
            color: white;
            text-decoration: none;
        }

        .footer-desc {
            font-size: 0.95rem;
            line-height: 1.6;
            max-width: 320px;
        }

        .footer-col h4 {
            color: white;
            font-family: var(--font-heading);
            font-size: 1rem;
            margin-bottom: 1.25rem;
        }

        .footer-links {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .footer-links a {
            color: #94a3b8;
            text-decoration: none;
            font-size: 0.92rem;
            transition: color 0.2s ease;
        }

        .footer-links a:hover {
            color: var(--accent-teal);
        }

        .footer-bottom {
            max-width: 1280px;
            margin: 0 auto;
            padding-top: 2rem;
            border-top: 1px solid #1e293b;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.88rem;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .server-status {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-family: var(--font-mono);
            font-size: 0.8rem;
            color: #38bdf8;
            background: rgba(56, 189, 248, 0.1);
            padding: 0.3rem 0.75rem;
            border-radius: 100px;
            border: 1px solid rgba(56, 189, 248, 0.2);
        }

        /* RESPONSIVE DESIGN */
        @media (max-width: 1024px) {
            .footer-container {
                grid-template-columns: 1fr 1fr;
            }
            .timeline-item, .timeline-item.right {
                width: 100%;
                padding-left: 60px;
                padding-right: 0;
                margin-left: 0;
                justify-content: flex-start;
            }
            .timeline-center-line {
                left: 20px;
            }
            .timeline-dot, .timeline-item.right .timeline-dot {
                left: 8px;
                right: auto;
            }
        }

        @media (max-width: 768px) {
            .nav-links {
                display: none;
            }
            .mobile-toggle {
                display: block;
            }
            .horizontal-scroll-wrapper {
                height: auto;
            }
            .horizontal-sticky-container {
                position: relative;
                height: auto;
            }
            .horizontal-track {
                flex-direction: column;
                width: 100%;
                padding: 0 1rem;
            }
            .feature-card {
                width: 100%;
            }
            .footer-container {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>

    <!-- 1. Cursor Glow Element -->
    <div id="cursor-glow" aria-hidden="true"></div>

    <!-- 2. Scroll Progress Bar -->
    <div id="scroll-progress-container" aria-hidden="true">
        <div id="scroll-progress"></div>
    </div>

    <!-- HEADER / NAVIGATION -->
    <header id="site-header">
        <div class="nav-container">
            <a href="#" class="brand-logo" aria-label="Verdis Chain Homepage">
                <div class="logo-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.4 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/>
                        <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>
                    </svg>
                </div>
                <span>Verdis</span>
            </a>

            <nav aria-label="Main Navigation">
                <ul class="nav-links">
                    <li><a href="#features" class="nav-link">Features</a></li>
                    <li><a href="#architecture" class="nav-link">Architecture</a></li>
                    <li><a href="#pallets" class="nav-link">Pallets</a></li>
                    <li><a href="#metrics" class="nav-link">Metrics</a></li>
                    <li><a href="#roadmap" class="nav-link">Roadmap</a></li>
                </ul>
            </nav>

            <div class="nav-actions">
                <a href="#cta" class="btn-shine btn-primary">
                    <span>Open Explorer</span>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
                </a>
            </div>
        </div>
    </header>

    <main>
        <!-- ==========================================================================
             SECTION 1: HERO (FULL-SCREEN, CINEMATIC)
             ========================================================================== -->
        <section class="hero-section" id="hero">
            <!-- 9. Animated Canvas Particles -->
            <canvas id="hero-canvas"></canvas>

            <!-- 8. Floating Gradient Blobs -->
            <div class="blob-container" aria-hidden="true">
                <div class="blob blob-1"></div>
                <div class="blob blob-2"></div>
                <div class="blob blob-3"></div>
            </div>

            <div class="hero-content">
                <!-- Stagger 1: Badge -->
                <div class="hero-stagger-1">
                    <div class="hero-badge">
                        <span class="pulse-dot" aria-hidden="true"></span>
                        <span>Mainnet Ready · Node Live</span>
                    </div>
                </div>

                <!-- Stagger 2: H1 Title -->
                <div class="hero-stagger-2">
                    <h1 class="hero-title">
                        The World's First <span class="gradient-text">Green Blockchain</span> Engineered in Rust
                    </h1>
                </div>

                <!-- Stagger 3: Subtitle -->
                <div class="hero-stagger-3">
                    <p class="hero-subtitle">
                        Ultra-fast, carbon-negative Layer-1 protocol powered by BABE & GRANDPA consensus. High throughput with zero compromise on decentralization.
                    </p>
                </div>

                <!-- Stagger 4: CTAs -->
                <div class="hero-stagger-4">
                    <div class="hero-ctas">
                        <a href="#cta" class="btn-shine btn-primary">
                            <span>Open Explorer -></span>
                        </a>
                        <a href="#architecture" class="btn-shine btn-secondary">
                            <span>View Architecture</span>
                        </a>
                    </div>
                </div>
            </div>

            <a href="#features" class="scroll-indicator" aria-label="Scroll to features">
                <span>Scroll to explore</span>
                <svg class="scroll-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 10l5 5 5-5"/></svg>
            </a>
        </section>

        <!-- ==========================================================================
             SECTION 2: HORIZONTAL SCROLL FEATURES
             ========================================================================== -->
        <section class="horizontal-scroll-wrapper" id="features">
            <div class="horizontal-sticky-container">
                <div class="section-header horizontal-header">
                    <span class="section-tag">Core Capabilities</span>
                    <h2 class="section-title">Everything you need to build on green infrastructure</h2>
                    <p class="section-desc">Modular, high-throughput, carbon-negative blockchain primitives engineered in Rust.</p>
                </div>

                <div class="horizontal-track-container">
                    <div class="horizontal-track" id="horizontalTrack">
                        <!-- Card 1 -->
                        <div class="feature-card hover-lift">
                            <div>
                                <div class="feature-icon-box">
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
                                </div>
                                <h3>DPoS Consensus</h3>
                                <p>BABE block production paired with GRANDPA deterministic finality. Energy consumption reduced by 99.99% compared to traditional PoW networks.</p>
                            </div>
                            <span class="tag-pill">BABE+GRANDPA</span>
                        </div>

                        <!-- Card 2 -->
                        <div class="feature-card hover-lift">
                            <div>
                                <div class="feature-icon-box">
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 3 21 3 21 8"/><line x1="4" y1="20" x2="21" y2="3"/><polyline points="21 16 21 21 16 21"/><line x1="15" y1="15" x2="21" y2="21"/><line x1="4" y1="4" x2="9" y2="9"/></svg>
                                </div>
                                <h3>AMM DEX</h3>
                                <p>Native on-chain automated market maker supporting constant product liquidity pools, flash swaps, and zero-slippage eco token pairs.</p>
                            </div>
                            <span class="tag-pill">SWAP PROTOCOL</span>
                        </div>

                        <!-- Card 3 -->
                        <div class="feature-card hover-lift">
                            <div>
                                <div class="feature-icon-box">
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.4 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>
                                </div>
                                <h3>Carbon Credit Tracking</h3>
                                <p>Integrated pallet for minting, retiring, and auditing verified carbon credits with cryptographic proof of real-world green impact.</p>
                            </div>
                            <span class="tag-pill">LEAF VERIFIED</span>
                        </div>

                        <!-- Card 4 -->
                        <div class="feature-card hover-lift">
                            <div>
                                <div class="feature-icon-box">
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                                </div>
                                <h3>EVM Smart Contracts</h3>
                                <p>Full execution engine supporting 143 opcodes under Chain ID 909. Seamless deployment with standard Ethereum toolchains.</p>
                            </div>
                            <span class="tag-pill">143 OPCODES · CHAIN 909</span>
                        </div>

                        <!-- Card 5 -->
                        <div class="feature-card hover-lift">
                            <div>
                                <div class="feature-icon-box">
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                                </div>
                                <h3>Tokenomics & Vesting</h3>
                                <p>Precision minting schedules with 100B max supply, 12B genesis allocation, and multi-signature linear cliff vesting schedules.</p>
                            </div>
                            <span class="tag-pill">100B SUPPLY · 12B ALLOC</span>
                        </div>

                        <!-- Card 6 -->
                        <div class="feature-card hover-lift">
                            <div>
                                <div class="feature-icon-box">
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"/><line x1="9" y1="6" x2="9" y2="6.01"/><line x1="15" y1="6" x2="15" y2="6.01"/><line x1="9" y1="10" x2="9" y2="10.01"/><line x1="15" y1="10" x2="15" y2="10.01"/><line x1="9" y1="14" x2="9" y2="14.01"/><line x1="15" y1="14" x2="15" y2="14.01"/><line x1="9" y1="18" x2="15" y2="18"/></svg>
                                </div>
                                <h3>Substrate + Rust Core</h3>
                                <p>Built directly on Substrate and Rust for memory safety, concurrency, and forkless runtime upgrades.</p>
                            </div>
                            <span class="tag-pill">RUST ENGINE</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- ==========================================================================
             SECTION 3: VERTICAL TIMELINE (ARCHITECTURE LAYERS)
             ========================================================================== -->
        <section class="timeline-section" id="architecture">
            <div class="section-header reveal">
                <span class="section-tag">System Stack</span>
                <h2 class="section-title">Seven layers, one chain</h2>
                <p class="section-desc">A complete green layer-1 architecture engineered from state storage to smart contracts.</p>
            </div>

            <div class="timeline-container">
                <!-- 14. Central Line with Fill Effect -->
                <div class="timeline-center-line">
                    <div class="timeline-line-fill" id="timelineLineFill"></div>
                </div>

                <!-- Layer 1 -->
                <div class="timeline-item reveal">
                    <div class="timeline-dot"></div>
                    <div class="timeline-card hover-lift">
                        <div class="timeline-header">
                            <span class="timeline-number">01</span>
                            <span class="status-badge"><span class="pulse-dot"></span> Live</span>
                        </div>
                        <h3>DPoS Consensus</h3>
                        <p>BABE block production and GRANDPA finality gadget guaranteeing deterministic 1-second block completion with validator rotation.</p>
                    </div>
                </div>

                <!-- Layer 2 -->
                <div class="timeline-item right reveal">
                    <div class="timeline-dot"></div>
                    <div class="timeline-card hover-lift">
                        <div class="timeline-header">
                            <span class="timeline-number">02</span>
                            <span class="status-badge"><span class="pulse-dot"></span> Live</span>
                        </div>
                        <h3>AMM DEX</h3>
                        <p>Substrate-native automated market maker facilitating high-speed token exchange and liquidity provider fee distribution.</p>
                    </div>
                </div>

                <!-- Layer 3 -->
                <div class="timeline-item reveal">
                    <div class="timeline-dot"></div>
                    <div class="timeline-card hover-lift">
                        <div class="timeline-header">
                            <span class="timeline-number">03</span>
                            <span class="status-badge"><span class="pulse-dot"></span> Live</span>
                        </div>
                        <h3>Eco Module</h3>
                        <p>Real-time carbon offset validation engine interfacing with IoT green energy sensors and verified carbon registries.</p>
                    </div>
                </div>

                <!-- Layer 4 -->
                <div class="timeline-item right reveal">
                    <div class="timeline-dot"></div>
                    <div class="timeline-card hover-lift">
                        <div class="timeline-header">
                            <span class="timeline-number">04</span>
                            <span class="status-badge"><span class="pulse-dot"></span> Live</span>
                        </div>
                        <h3>EVM Subsystem</h3>
                        <p>Chain ID 909 execution environment supporting 143 Ethereum opcodes, Solidity smart contracts, and Web3 RPC adapters.</p>
                    </div>
                </div>

                <!-- Layer 5 -->
                <div class="timeline-item reveal">
                    <div class="timeline-dot"></div>
                    <div class="timeline-card hover-lift">
                        <div class="timeline-header">
                            <span class="timeline-number">05</span>
                            <span class="status-badge"><span class="pulse-dot"></span> Live</span>
                        </div>
                        <h3>Tokenomics Core</h3>
                        <p>100B supply token economy with 12B allocation, dynamic fee burning mechanism, and automated staking rewards.</p>
                    </div>
                </div>

                <!-- Layer 6 -->
                <div class="timeline-item right reveal">
                    <div class="timeline-dot"></div>
                    <div class="timeline-card hover-lift">
                        <div class="timeline-header">
                            <span class="timeline-number">06</span>
                            <span class="status-badge"><span class="pulse-dot"></span> Live</span>
                        </div>
                        <h3>Vesting Module</h3>
                        <p>On-chain linear unlock schedules and programmatic treasury releases for long-term ecosystem sustainability.</p>
                    </div>
                </div>

                <!-- Layer 7 -->
                <div class="timeline-item reveal">
                    <div class="timeline-dot"></div>
                    <div class="timeline-card hover-lift">
                        <div class="timeline-header">
                            <span class="timeline-number">07</span>
                            <span class="status-badge"><span class="pulse-dot"></span> Live</span>
                        </div>
                        <h3>Storage Layer</h3>
                        <p>High-density RocksDB state Trie storage with zero-knowledge state proof compression and instant snapshot creation.</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- ==========================================================================
             SECTION 4: 3D TILT CARDS (PALLETS)
             ========================================================================== -->
        <section class="pallets-section" id="pallets">
            <div class="section-header reveal">
                <span class="section-tag">Rust Runtime</span>
                <h2 class="section-title">Production-ready modules</h2>
                <p class="section-desc">Thoroughly benchmarked and unit-tested Substrate pallets forming the core runtime engine.</p>
            </div>

            <!-- 6. 3D Perspective Tilt Grid -->
            <div class="pallets-grid">
                <!-- Pallet 1 -->
                <div class="pallet-card" data-tilt>
                    <div class="pallet-glare"></div>
                    <div class="pallet-header">
                        <span class="pallet-name">pallet-dpos</span>
                        <span class="tests-badge">34 tests</span>
                    </div>
                    <p>Handles validator registration, election rounds, slashing conditions, and BABE/GRANDPA key rotation algorithms.</p>
                    <div class="pallet-footer">
                        <span>34 tests passing</span>
                        <span>v1.2.0</span>
                    </div>
                </div>

                <!-- Pallet 2 -->
                <div class="pallet-card" data-tilt>
                    <div class="pallet-glare"></div>
                    <div class="pallet-header">
                        <span class="pallet-name">pallet-amm-dex</span>
                        <span class="tests-badge">25 tests</span>
                    </div>
                    <p>Substrate liquidity management, automated swap calculations, LP token issuance, and anti-frontrunning protection.</p>
                    <div class="pallet-footer">
                        <span>25 tests passing</span>
                        <span>v1.4.1</span>
                    </div>
                </div>

                <!-- Pallet 3 -->
                <div class="pallet-card" data-tilt>
                    <div class="pallet-glare"></div>
                    <div class="pallet-header">
                        <span class="pallet-name">pallet-eco</span>
                        <span class="tests-badge">33 tests</span>
                    </div>
                    <p>Verifies renewable energy credits, issues verified eco-certificates, and manages carbon offset retirement ledger.</p>
                    <div class="pallet-footer">
                        <span>33 tests passing</span>
                        <span>v2.0.0</span>
                    </div>
                </div>

                <!-- Pallet 4 -->
                <div class="pallet-card" data-tilt>
                    <div class="pallet-glare"></div>
                    <div class="pallet-header">
                        <span class="pallet-name">pallet-evm</span>
                        <span class="tests-badge">102 tests</span>
                    </div>
                    <p>Full Ethereum Virtual Machine interpreter, gas accounting, precompiled contracts, and Chain ID 909 state storage.</p>
                    <div class="pallet-footer">
                        <span>102 tests passing</span>
                        <span>v3.1.0</span>
                    </div>
                </div>

                <!-- Pallet 5 -->
                <div class="pallet-card" data-tilt>
                    <div class="pallet-glare"></div>
                    <div class="pallet-header">
                        <span class="pallet-name">pallet-tokenomics</span>
                        <span class="tests-badge">23 tests</span>
                    </div>
                    <p>Manages 100B VRS total supply, dynamic transaction fee burns, staker yield distribution, and treasury inflation.</p>
                    <div class="pallet-footer">
                        <span>23 tests passing</span>
                        <span>v1.0.5</span>
                    </div>
                </div>

                <!-- Pallet 6 -->
                <div class="pallet-card" data-tilt>
                    <div class="pallet-glare"></div>
                    <div class="pallet-header">
                        <span class="pallet-name">pallet-vesting</span>
                        <span class="tests-badge">10 tests</span>
                    </div>
                    <p>Time-locked token schedules, linear block-by-block unlocks, cliff periods, and multi-sig administrative controls.</p>
                    <div class="pallet-footer">
                        <span>10 tests passing</span>
                        <span>v1.1.2</span>
                    </div>
                </div>

                <!-- Pallet 7 -->
                <div class="pallet-card" data-tilt>
                    <div class="pallet-glare"></div>
                    <div class="pallet-header">
                        <span class="pallet-name">pallet-storage</span>
                        <span class="tests-badge">9 tests</span>
                    </div>
                    <p>On-chain state pruning, cryptographic Merkle trie proof generator, and zero-knowledge state commitment verifier.</p>
                    <div class="pallet-footer">
                        <span>9 tests passing</span>
                        <span>v1.0.0</span>
                    </div>
                </div>
            </div>
        </section>

        <!-- ==========================================================================
             SECTION 5: CIRCLE COUNTERS (STATS)
             ========================================================================== -->
        <section class="stats-section" id="metrics">
            <div class="section-header reveal">
                <span class="section-tag">Verified Benchmarks</span>
                <h2 class="section-title">Built for scale, ready for production</h2>
                <p class="section-desc">Real-time network telemetry and verified test suite coverage across active testnets.</p>
            </div>

            <!-- SVG Gradient Definition -->
            <svg style="width:0;height:0;position:absolute;" aria-hidden="true">
                <defs>
                    <linearGradient id="ring-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#00a86b"/>
                        <stop offset="50%" stop-color="#10b981"/>
                        <stop offset="100%" stop-color="#2dd4bf"/>
                    </linearGradient>
                </defs>
            </svg>

            <div class="stats-grid">
                <!-- Stat 1 -->
                <div class="stat-card reveal hover-lift">
                    <div class="ring-container">
                        <svg class="ring-svg" viewBox="0 0 160 160">
                            <circle class="ring-bg" cx="80" cy="80" r="70"/>
                            <circle class="ring-circle" cx="80" cy="80" r="70" data-percent="100"/>
                        </svg>
                        <div class="ring-content">
                            <span class="counter" data-target="100" data-suffix="B">0</span>
                        </div>
                    </div>
                    <div class="stat-label">Total Supply</div>
                    <div class="stat-sub">Fixed Genesis VRS Allocation</div>
                </div>

                <!-- Stat 2 -->
                <div class="stat-card reveal hover-lift" style="transition-delay: 0.1s;">
                    <div class="ring-container">
                        <svg class="ring-svg" viewBox="0 0 160 160">
                            <circle class="ring-bg" cx="80" cy="80" r="70"/>
                            <circle class="ring-circle" cx="80" cy="80" r="70" data-percent="100"/>
                        </svg>
                        <div class="ring-content">
                            <span class="counter" data-target="143" data-suffix="">0</span>
                        </div>
                    </div>
                    <div class="stat-label">EVM Opcodes</div>
                    <div class="stat-sub">Chain ID 909 Bytecode Standard</div>
                </div>

                <!-- Stat 3 -->
                <div class="stat-card reveal hover-lift" style="transition-delay: 0.2s;">
                    <div class="ring-container">
                        <svg class="ring-svg" viewBox="0 0 160 160">
                            <circle class="ring-bg" cx="80" cy="80" r="70"/>
                            <circle class="ring-circle" cx="80" cy="80" r="70" data-percent="100"/>
                        </svg>
                        <div class="ring-content">
                            <span class="counter" data-target="260" data-suffix="">0</span>
                        </div>
                    </div>
                    <div class="stat-label">Tests Passing</div>
                    <div class="stat-sub">100% Runtime Code Coverage</div>
                </div>

                <!-- Stat 4 -->
                <div class="stat-card reveal hover-lift" style="transition-delay: 0.3s;">
                    <div class="ring-container">
                        <svg class="ring-svg" viewBox="0 0 160 160">
                            <circle class="ring-bg" cx="80" cy="80" r="70"/>
                            <circle class="ring-circle" cx="80" cy="80" r="70" data-percent="100"/>
                        </svg>
                        <div class="ring-content">
                            <span class="counter" data-target="7" data-suffix="">0</span>
                        </div>
                    </div>
                    <div class="stat-label">Production Pallets</div>
                    <div class="stat-sub">Modular Substrate Runtime</div>
                </div>
            </div>
        </section>

        <!-- ==========================================================================
             SECTION 6: ROADMAP (PARALLAX DEPTH)
             ========================================================================== -->
        <section class="roadmap-section" id="roadmap">
            <div class="roadmap-bg-decor" aria-hidden="true"></div>

            <div class="roadmap-container">
                <div class="section-header reveal">
                    <span class="section-tag">Future Horizons</span>
                    <h2 class="section-title">What's built and what's next</h2>
                    <p class="section-desc">Our milestone progression towards a fully autonomous green decentralized economy.</p>
                </div>

                <!-- 15. Parallax Depth Grid -->
                <div class="roadmap-grid">
                    <!-- Milestone 1 -->
                    <div class="roadmap-card done hover-lift" data-parallax-depth="0.08">
                        <div>
                            <div class="roadmap-phase">PHASE 01</div>
                            <h3>Core Blockchain</h3>
                            <div class="roadmap-status status-done">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                                <span>DONE</span>
                            </div>
                            <ul class="roadmap-list">
                                <li>Phases 86-129 Completed</li>
                                <li>BABE & GRANDPA Engines</li>
                                <li>7 Core Rust Pallets Built</li>
                                <li>260 Unit Tests Passing</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Milestone 2 -->
                    <div class="roadmap-card done hover-lift" data-parallax-depth="-0.06">
                        <div>
                            <div class="roadmap-phase">PHASE 02</div>
                            <h3>Verdiscan Explorer</h3>
                            <div class="roadmap-status status-done">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                                <span>DONE</span>
                            </div>
                            <ul class="roadmap-list">
                                <li>Real-time Block Scanner</li>
                                <li>EVM Contract Verifier</li>
                                <li>Carbon Credit Dashboard</li>
                                <li>WebSocket Live Feeds</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Milestone 3 -->
                    <div class="roadmap-card active hover-lift" data-parallax-depth="0.12">
                        <div>
                            <div class="roadmap-phase">PHASE 03</div>
                            <h3>Premium Platform Launch</h3>
                            <div class="roadmap-status status-active">
                                <span class="pulse-dot"></span>
                                <span>ACTIVE NOW</span>
                            </div>
                            <ul class="roadmap-list">
                                <li>Public Testnet 2.0 Live</li>
                                <li>Developer Portal & SDK</li>
                                <li>AMM DEX Incentives</li>
                                <li>Eco Oracle Integrations</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Milestone 4 -->
                    <div class="roadmap-card planned hover-lift" data-parallax-depth="-0.04">
                        <div>
                            <div class="roadmap-phase">PHASE 04</div>
                            <h3>Mainnet Deployment</h3>
                            <div class="roadmap-status status-planned">
                                <span>PLANNED</span>
                            </div>
                            <ul class="roadmap-list">
                                <li>Genesis Block Minting</li>
                                <li>Validator Staking Onboarding</li>
                                <li>EVM Cross-Chain Bridge</li>
                                <li>Governance DAO Activation</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Milestone 5 -->
                    <div class="roadmap-card planned hover-lift" data-parallax-depth="0.07">
                        <div>
                            <div class="roadmap-phase">PHASE 05</div>
                            <h3>Ecosystem Expansion</h3>
                            <div class="roadmap-status status-planned">
                                <span>PLANNED</span>
                            </div>
                            <ul class="roadmap-list">
                                <li>Carbon Offset Derivatives</li>
                                <li>Zero-Knowledge Rollups</li>
                                <li>Enterprise IoT Sensors</li>
                                <li>Global Green Grants</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- ==========================================================================
             SECTION 7: CTA + FOOTER
             ========================================================================== -->
        <section class="cta-section" id="cta">
            <div class="cta-box reveal">
                <div class="cta-glow-bg" aria-hidden="true"></div>
                <div class="cta-content">
                    <h2>Start building on green infrastructure</h2>
                    <p>Deploy Solidity contracts under Chain 909, stake validator nodes, or launch eco-dApps on the world's cleanest blockchain.</p>
                    <a href="#hero" class="btn-shine cta-btn">
                        <span>Open Explorer -></span>
                    </a>
                </div>
            </div>
        </section>
    </main>

    <!-- FOOTER -->
    <footer>
        <div class="footer-container">
            <div class="footer-brand">
                <a href="#" class="footer-logo">
                    <div class="logo-icon">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.4 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>
                    </div>
                    <span>Verdis Chain</span>
                </a>
                <p class="footer-desc">
                    The world's first green blockchain engineered in Rust. Carbon-negative, ultra-fast, and EVM compatible.
                </p>
            </div>

            <div class="footer-col">
                <h4>Platform</h4>
                <ul class="footer-links">
                    <li><a href="#hero">Overview</a></li>
                    <li><a href="#features">Features</a></li>
                    <li><a href="#architecture">Architecture</a></li>
                    <li><a href="#metrics">Telemetry</a></li>
                </ul>
            </div>

            <div class="footer-col">
                <h4>Developers</h4>
                <ul class="footer-links">
                    <li><a href="#pallets">Rust Pallets</a></li>
                    <li><a href="#architecture">EVM Gateway</a></li>
                    <li><a href="#metrics">Benchmarks</a></li>
                    <li><a href="#roadmap">Roadmap</a></li>
                </ul>
            </div>

            <div class="footer-col">
                <h4>Community</h4>
                <ul class="footer-links">
                    <li><a href="#">Discord Server</a></li>
                    <li><a href="#">Telegram Group</a></li>
                    <li><a href="#">Twitter / X</a></li>
                    <li><a href="#">GitHub Repo</a></li>
                </ul>
            </div>
        </div>

        <div class="footer-bottom">
            <div>
                © 2026 Verdis Chain Foundation. All rights reserved. Built with Rust & Substrate.
            </div>
            <div class="server-status">
                <span class="pulse-dot" style="background:#38bdf8;" aria-hidden="true"></span>
                <span>Mainnet Node · Block #1,489,230 · Latency: 12ms</span>
            </div>
        </div>
    </footer>

    <!-- ==========================================================================
       VANILLA JAVASCRIPT ANIMATION ENGINES
       ========================================================================== -->
    <script>
        document.addEventListener('DOMContentLoaded', () => {

            /* ==========================================================================
               1. CURSOR GLOW EFFECT ENGINE
               ========================================================================== */
            window.addEventListener('mousemove', (e) => {
                document.documentElement.style.setProperty('--mouse-x', `${e.clientX}px`);
                document.documentElement.style.setProperty('--mouse-y', `${e.clientY}px`);
            });

            /* ==========================================================================
               2. SCROLL PROGRESS BAR ENGINE
               ========================================================================== */
            const scrollProgress = document.getElementById('scroll-progress');
            window.addEventListener('scroll', () => {
                const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
                const progress = (window.scrollY / totalHeight) * 100;
                scrollProgress.style.width = `${Math.min(100, Math.max(0, progress))}%`;
            });

            /* ==========================================================================
               9. CANVAS PARTICLE NETWORK IN HERO
               ========================================================================== */
            const canvas = document.getElementById('hero-canvas');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                let width = canvas.width = canvas.offsetWidth;
                let height = canvas.height = canvas.offsetHeight;

                window.addEventListener('resize', () => {
                    width = canvas.width = canvas.offsetWidth;
                    height = canvas.height = canvas.offsetHeight;
                });

                // Mouse repel state
                let mouseX = -1000;
                let mouseY = -1000;
                canvas.addEventListener('mousemove', (e) => {
                    const rect = canvas.getBoundingClientRect();
                    mouseX = e.clientX - rect.left;
                    mouseY = e.clientY - rect.top;
                });

                canvas.addEventListener('mouseleave', () => {
                    mouseX = -1000;
                    mouseY = -1000;
                });

                // Generate 45 nodes
                const nodeCount = 45;
                const nodes = [];
                for (let i = 0; i < nodeCount; i++) {
                    nodes.push({
                        x: Math.random() * width,
                        y: Math.random() * height,
                        vx: (Math.random() - 0.5) * 0.8,
                        vy: (Math.random() - 0.5) * 0.8,
                        radius: Math.random() * 2.5 + 1.5,
                        pulse: Math.random() * Math.PI
                    });
                }

                function renderCanvas() {
                    ctx.clearRect(0, 0, width, height);

                    // Update & draw nodes
                    nodes.forEach((node, idx) => {
                        // Movement
                        node.x += node.vx;
                        node.y += node.vy;

                        // Bounce walls
                        if (node.x < 0 || node.x > width) node.vx *= -1;
                        if (node.y < 0 || node.y > height) node.vy *= -1;

                        // Mouse repulsion force
                        const dx = mouseX - node.x;
                        const dy = mouseY - node.y;
                        const dist = Math.sqrt(dx * dx + dy * dy);
                        if (dist < 140) {
                            const angle = Math.atan2(dy, dx);
                            const force = (140 - dist) / 140;
                            node.x -= Math.cos(angle) * force * 3;
                            node.y -= Math.sin(angle) * force * 3;
                        }

                        // Pulse radius
                        node.pulse += 0.03;
                        const currentRadius = node.radius + Math.sin(node.pulse) * 0.8;

                        // Draw particle dot
                        ctx.beginPath();
                        ctx.arc(node.x, node.y, Math.max(0.5, currentRadius), 0, Math.PI * 2);
                        ctx.fillStyle = 'rgba(0, 168, 107, 0.7)';
                        ctx.fill();

                        // Connect lines to nearby nodes
                        for (let j = idx + 1; j < nodes.length; j++) {
                            const other = nodes[j];
                            const ldx = other.x - node.x;
                            const ldy = other.y - node.y;
                            const ldist = Math.sqrt(ldx * ldx + ldy * ldy);

                            if (ldist < 130) {
                                const opacity = (1 - ldist / 130) * 0.25;
                                ctx.beginPath();
                                ctx.moveTo(node.x, node.y);
                                ctx.lineTo(other.x, other.y);
                                ctx.strokeStyle = `rgba(0, 168, 107, ${opacity})`;
                                ctx.lineWidth = 1;
                                ctx.stroke();
                            }
                        }
                    });

                    requestAnimationFrame(renderCanvas);
                }
                renderCanvas();
            }

            /* ==========================================================================
               7. HORIZONTAL SCROLL FEATURE SECTION ENGINE
               ========================================================================== */
            const horizontalWrapper = document.querySelector('.horizontal-scroll-wrapper');
            const horizontalTrack = document.getElementById('horizontalTrack');

            if (horizontalWrapper && horizontalTrack) {
                window.addEventListener('scroll', () => {
                    const rect = horizontalWrapper.getBoundingClientRect();
                    const wrapperHeight = horizontalWrapper.offsetHeight;
                    const windowHeight = window.innerHeight;

                    // Calculate scroll progress through horizontal section [0 to 1]
                    const scrollProgress = -rect.top / (wrapperHeight - windowHeight);
                    const clampedProgress = Math.min(1, Math.max(0, scrollProgress));

                    // Calculate total overflow width of cards
                    const trackWidth = horizontalTrack.scrollWidth;
                    const maxTranslate = trackWidth - window.innerWidth + 80;

                    if (maxTranslate > 0) {
                        const translateX = -clampedProgress * maxTranslate;
                        horizontalTrack.style.transform = `translateX(${translateX}px)`;
                    }
                });
            }

            /* ==========================================================================
               14. TIMELINE LINE FILL ENGINE
               ========================================================================== */
            const timelineSection = document.getElementById('architecture');
            const timelineLineFill = document.getElementById('timelineLineFill');

            if (timelineSection && timelineLineFill) {
                window.addEventListener('scroll', () => {
                    const rect = timelineSection.getBoundingClientRect();
                    const windowHeight = window.innerHeight;
                    const totalDist = rect.height;
                    const currentDist = windowHeight - rect.top;

                    let fillPercent = (currentDist / totalDist) * 100;
                    fillPercent = Math.min(100, Math.max(0, fillPercent));
                    timelineLineFill.style.height = `${fillPercent}%`;
                });
            }

            /* ==========================================================================
               6. 3D PERSPECTIVE TILT CARDS ENGINE
               ========================================================================== */
            const tiltCards = document.querySelectorAll('[data-tilt]');

            tiltCards.forEach(card => {
                const glare = card.querySelector('.pallet-glare');

                card.addEventListener('mousemove', (e) => {
                    const rect = card.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;

                    const centerX = rect.width / 2;
                    const centerY = rect.height / 2;

                    const rotateX = ((y - centerY) / centerY) * -12; // Max 12 deg tilt
                    const rotateY = ((x - centerX) / centerX) * 12;

                    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;

                    if (glare) {
                        glare.style.opacity = '1';
                        glare.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(255, 255, 255, 0.5), transparent 70%)`;
                    }
                });

                card.addEventListener('mouseleave', () => {
                    card.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`;
                    if (glare) {
                        glare.style.opacity = '0';
                    }
                });
            });

            /* ==========================================================================
               3. INTERSECTION OBSERVER SCROLL REVEALS & 4/5. COUNTERS & PROGRESS RINGS
               ========================================================================== */
            const revealElements = document.querySelectorAll('.reveal');

            const observerOptions = {
                threshold: 0.15,
                rootMargin: '0px 0px -50px 0px'
            };

            const revealObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('active');

                        // Trigger circle rings & counters inside stat cards if present
                        if (entry.target.classList.contains('stat-card')) {
                            animateStatCard(entry.target);
                        }
                    }
                });
            }, observerOptions);

            revealElements.forEach(el => revealObserver.observe(el));

            // Observe stat cards
            document.querySelectorAll('.stat-card').forEach(card => revealObserver.observe(card));

            function animateStatCard(card) {
                if (card.dataset.animated) return;
                card.dataset.animated = "true";

                // Animate SVG Ring
                const ringCircle = card.querySelector('.ring-circle');
                if (ringCircle) {
                    const percent = parseFloat(ringCircle.dataset.percent) || 100;
                    const circumference = 440; // 2 * PI * 70
                    const offset = circumference - (percent / 100) * circumference;
                    ringCircle.style.strokeDashoffset = offset;
                }

                // Animate Number Counter
                const counter = card.querySelector('.counter');
                if (counter) {
                    const target = parseInt(counter.dataset.target, 10);
                    const suffix = counter.dataset.suffix || '';
                    const duration = 2000; // ms
                    const startTime = performance.now();

                    function updateCounter(currentTime) {
                        const elapsed = currentTime - startTime;
                        const progress = Math.min(elapsed / duration, 1);
                        // Ease out quad
                        const easeProgress = 1 - (1 - progress) * (1 - progress);
                        const currentVal = Math.floor(easeProgress * target);

                        counter.textContent = currentVal + suffix;

                        if (progress < 1) {
                            requestAnimationFrame(updateCounter);
                        } else {
                            counter.textContent = target + suffix;
                        }
                    }
                    requestAnimationFrame(updateCounter);
                }
            }

            /* ==========================================================================
               15. PARALLAX DEPTH ON ROADMAP ITEMS
               ========================================================================== */
            const roadmapSection = document.getElementById('roadmap');
            const parallaxCards = document.querySelectorAll('[data-parallax-depth]');

            if (roadmapSection && parallaxCards.length > 0) {
                window.addEventListener('scroll', () => {
                    const rect = roadmapSection.getBoundingClientRect();
                    const windowHeight = window.innerHeight;

                    if (rect.top < windowHeight && rect.bottom > 0) {
                        const relativeScroll = windowHeight - rect.top;

                        parallaxCards.forEach(card => {
                            const depth = parseFloat(card.dataset.parallaxDepth) || 0.05;
                            const translateY = (relativeScroll - windowHeight / 2) * depth;
                            card.style.transform = `translateY(${translateY}px)`;
                        });
                    }
                });
            }
        });
    </script>
</body>
</html>
"""
with open("verdis-landing.html", "w") as out:
    out.write(content)
print("Done!")