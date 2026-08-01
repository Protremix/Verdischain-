import os

download_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Download Verdis Wallet v2.0.0 | Native Android Carbon-Negative Wallet</title>
    <meta name="description" content="Download Verdis Wallet v2.0.0 for Android. Biometric security, native DEX swaps, seed backup, and real-time reforestation logging.">
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg-dark: #050a08;
            --bg-card: #0f1f1a;
            --bg-card-hover: #152c24;
            --border-color: #1a2b23;
            --border-glow: rgba(0, 255, 136, 0.25);
            --accent-green: #00ff88;
            --accent-emerald: #10b981;
            --accent-teal: #2dd4bf;
            --text-primary: #e8f5ee;
            --text-muted: #6b8f7a;
            --font-main: 'Inter', system-ui, -apple-system, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
            --transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html {
            scroll-behavior: smooth;
            background-color: var(--bg-dark);
            color: var(--text-primary);
            font-family: var(--font-main);
            overflow-x: hidden;
        }

        body {
            background-color: var(--bg-dark);
            position: relative;
            min-height: 100vh;
            line-height: 1.6;
        }

        #bg-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 0;
            pointer-events: none;
        }

        .container {
            max-width: 1240px;
            margin: 0 auto;
            padding: 0 24px;
            position: relative;
            z-index: 1;
        }

        h1, h2, h3, h4 {
            font-weight: 700;
            line-height: 1.15;
            letter-spacing: -0.02em;
            color: var(--text-primary);
        }

        .gradient-text {
            background: linear-gradient(135deg, #ffffff 0%, var(--accent-green) 50%, var(--accent-teal) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        p {
            color: var(--text-muted);
            font-size: 1.05rem;
            line-height: 1.7;
        }

        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 14px 28px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 1rem;
            text-decoration: none;
            transition: var(--transition);
            cursor: pointer;
            border: 1px solid transparent;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--accent-green) 0%, var(--accent-emerald) 100%);
            color: #03140c;
            font-weight: 700;
            box-shadow: 0 4px 20px rgba(0, 255, 136, 0.3);
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0, 255, 136, 0.5);
            background: linear-gradient(135deg, #26ff98 0%, #13d193 100%);
        }

        .btn-secondary {
            background: rgba(15, 31, 26, 0.8);
            border-color: var(--border-color);
            color: var(--text-primary);
            backdrop-filter: blur(10px);
        }

        .btn-secondary:hover {
            border-color: var(--accent-green);
            color: var(--accent-green);
            transform: translateY(-2px);
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 16px;
            border-radius: 100px;
            font-size: 0.85rem;
            font-weight: 600;
            background: rgba(0, 255, 136, 0.08);
            border: 1px solid rgba(0, 255, 136, 0.25);
            color: var(--accent-green);
            backdrop-filter: blur(8px);
        }

        .glass-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 32px;
            backdrop-filter: blur(16px);
            transition: var(--transition);
        }

        .glass-card:hover {
            border-color: rgba(0, 255, 136, 0.35);
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4), 0 0 20px rgba(0, 255, 136, 0.08);
        }

        /* Navbar */
        .navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            background: rgba(5, 10, 8, 0.75);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(26, 43, 35, 0.6);
            padding: 16px 0;
        }

        .nav-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .nav-logo {
            display: flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
            color: var(--text-primary);
            font-weight: 800;
            font-size: 1.4rem;
        }

        .nav-links {
            display: flex;
            align-items: center;
            gap: 32px;
            list-style: none;
        }

        .nav-links a {
            color: var(--text-muted);
            text-decoration: none;
            font-weight: 500;
            font-size: 0.95rem;
            transition: var(--transition);
        }

        .nav-links a:hover {
            color: var(--accent-green);
        }

        /* Hero Section */
        .download-hero {
            padding: 160px 0 80px;
        }

        .hero-layout {
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 48px;
            align-items: center;
        }

        .download-details h1 {
            font-size: 3.5rem;
            margin: 20px 0;
        }

        .qr-card {
            text-align: center;
            background: rgba(15, 31, 26, 0.8);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            padding: 32px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }

        .qr-placeholder {
            width: 200px;
            height: 200px;
            margin: 20px auto;
            background: #ffffff;
            padding: 12px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.2);
        }

        .qr-svg {
            width: 100%;
            height: 100%;
        }

        /* Features List Grid */
        .features-section {
            padding: 60px 0;
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 24px;
        }

        .feature-icon {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid rgba(0, 255, 136, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 16px;
            color: var(--accent-green);
        }

        /* Mobile Screenshots Preview Section */
        .screenshots-section {
            padding: 80px 0;
        }

        .phone-mockup-wrapper {
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 48px;
            align-items: center;
            background: rgba(15, 31, 26, 0.6);
            border: 1px solid var(--border-color);
            border-radius: 28px;
            padding: 40px;
        }

        .phone-frame {
            width: 280px;
            height: 560px;
            background: #000000;
            border: 10px solid #1a2b23;
            border-radius: 40px;
            box-shadow: 0 0 30px rgba(0, 255, 136, 0.2);
            position: relative;
            overflow: hidden;
            margin: 0 auto;
        }

        .phone-notch {
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 120px;
            height: 20px;
            background: #1a2b23;
            border-bottom-left-radius: 12px;
            border-bottom-right-radius: 12px;
            z-index: 10;
        }

        .phone-screen {
            padding: 30px 16px 16px;
            height: 100%;
            background: var(--bg-dark);
            overflow-y: auto;
        }

        .screen-view {
            display: none;
        }

        .screen-view.active {
            display: block;
        }

        .screen-tab-btn {
            display: block;
            width: 100%;
            text-align: left;
            padding: 16px;
            background: rgba(5, 10, 8, 0.6);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            color: var(--text-muted);
            margin-bottom: 12px;
            cursor: pointer;
            transition: var(--transition);
        }

        .screen-tab-btn.active {
            background: rgba(0, 255, 136, 0.12);
            border-color: var(--accent-green);
            color: var(--accent-green);
        }

        .screen-tab-btn h4 {
            font-size: 1.05rem;
            margin-bottom: 4px;
        }

        .screen-tab-btn p {
            font-size: 0.85rem;
        }

        /* Installation Guide */
        .guide-section {
            padding: 80px 0;
        }

        .guide-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 24px;
        }

        .guide-step {
            background: rgba(15, 31, 26, 0.6);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
        }

        .step-tag {
            font-family: var(--font-mono);
            color: var(--accent-green);
            font-weight: 700;
            margin-bottom: 12px;
        }

        /* Footer */
        .footer {
            border-top: 1px solid var(--border-color);
            background: rgba(3, 7, 5, 0.95);
            padding: 80px 0 40px;
            font-size: 0.9rem;
            position: relative;
            z-index: 2;
        }

        .footer-grid {
            display: grid;
            grid-template-columns: 2fr repeat(3, 1fr);
            gap: 48px;
            margin-bottom: 60px;
        }

        .footer-col h4 {
            font-size: 1rem;
            margin-bottom: 20px;
        }

        .footer-col ul {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .footer-col a {
            color: var(--text-muted);
            text-decoration: none;
            transition: var(--transition);
        }

        .footer-col a:hover {
            color: var(--accent-green);
        }

        .footer-bottom {
            border-top: 1px solid rgba(26, 43, 35, 0.6);
            padding-top: 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--text-muted);
        }

        @media (max-width: 1024px) {
            .hero-layout, .phone-mockup-wrapper {
                grid-template-columns: 1fr;
            }
            .features-grid, .guide-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>

    <!-- Particle Background -->
    <canvas id="bg-canvas"></canvas>

    <!-- Navigation -->
    <nav class="navbar">
        <div class="container nav-container">
            <a href="landing.html" class="nav-logo">
                <svg width="36" height="36" viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <polygon points="256,40 440,146 440,358 256,464 72,358 72,146" fill="none" stroke="#10b981" stroke-width="12"/>
                    <path d="M 256 120 C 190 120, 150 180, 150 256 C 150 332, 190 392, 256 392 C 322 392, 362 332, 362 256 C 362 180, 322 120, 256 120 Z" fill="#00ff88"/>
                </svg>
                VERDIS
            </a>

            <ul class="nav-links">
                <li><a href="landing.html">Home</a></li>
                <li><a href="whitepaper_v2.html" target="_blank">Whitepaper</a></li>
                <li><a href="explorer-dashboard.html" target="_blank">Explorer</a></li>
                <li><a href="landing.html#tokenomics">Buy VRS</a></li>
            </ul>
        </div>
    </nav>

    <!-- Download Hero -->
    <section class="download-hero">
        <div class="container">
            <div class="hero-layout">
                <div class="download-details">
                    <div class="badge">Android APK v2.0.0 • Size: 18.4 MB</div>
                    <h1>Verdis Wallet <span class="gradient-text">v2.0.0</span></h1>
                    <p>The ultimate mobile gateway to the carbon-negative Verdis blockchain. Built natively for Android with biometric authentication, integrated AMM DEX token swaps, seed backup, and real-time reforestation logging.</p>

                    <div style="display: flex; gap: 16px; margin-top: 32px; flex-wrap: wrap;">
                        <a href="/verdis-wallet.apk" class="btn btn-primary" style="font-size: 1.1rem; padding: 16px 36px;">
                            <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                            Download APK (v2.0.0)
                        </a>
                        <a href="landing.html" class="btn btn-secondary">
                            Back to Website
                        </a>
                    </div>

                    <div style="margin-top: 24px; font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-muted);">
                        SHA-256: <span style="color: var(--accent-teal);">e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855</span>
                    </div>
                </div>

                <div class="qr-card">
                    <h3>Mobile Instant Install</h3>
                    <p style="font-size: 0.85rem; margin-top: 6px;">Scan with your Android camera to download directly.</p>

                    <div class="qr-placeholder">
                        <svg class="qr-svg" viewBox="0 0 100 100" fill="#050a08">
                            <!-- SVG QR Code Design -->
                            <rect x="0" y="0" width="100" height="100" fill="#ffffff"/>
                            <!-- Top Left Finder -->
                            <rect x="5" y="5" width="30" height="30" fill="#050a08"/>
                            <rect x="10" y="10" width="20" height="20" fill="#ffffff"/>
                            <rect x="15" y="15" width="10" height="10" fill="#00ff88"/>
                            <!-- Top Right Finder -->
                            <rect x="65" y="5" width="30" height="30" fill="#050a08"/>
                            <rect x="70" y="10" width="20" height="20" fill="#ffffff"/>
                            <rect x="75" y="15" width="10" height="10" fill="#00ff88"/>
                            <!-- Bottom Left Finder -->
                            <rect x="5" y="65" width="30" height="30" fill="#050a08"/>
                            <rect x="10" y="70" width="20" height="20" fill="#ffffff"/>
                            <rect x="15" y="75" width="10" height="10" fill="#00ff88"/>
                            <!-- Random Data Patterns -->
                            <rect x="40" y="10" width="8" height="8" fill="#050a08"/>
                            <rect x="50" y="10" width="8" height="8" fill="#00ff88"/>
                            <rect x="40" y="25" width="18" height="8" fill="#050a08"/>
                            <rect x="10" y="40" width="25" height="8" fill="#050a08"/>
                            <rect x="40" y="40" width="10" height="10" fill="#00ff88"/>
                            <rect x="55" y="40" width="15" height="8" fill="#050a08"/>
                            <rect x="75" y="40" width="20" height="8" fill="#050a08"/>
                            <rect x="40" y="55" width="8" height="18" fill="#050a08"/>
                            <rect x="55" y="55" width="18" height="8" fill="#00ff88"/>
                            <rect x="75" y="55" width="18" height="18" fill="#050a08"/>
                            <rect x="40" y="75" width="18" height="8" fill="#050a08"/>
                            <rect x="65" y="75" width="25" height="18" fill="#050a08"/>
                        </svg>
                    </div>

                    <span style="font-size: 0.8rem; color: var(--accent-green); font-family: var(--font-mono);">
                        Compatible with Android 8.0+
                    </span>
                </div>
            </div>
        </div>
    </section>

    <!-- Key Features List -->
    <section class="features-section">
        <div class="container">
            <div style="text-align: center; max-width: 600px; margin: 0 auto 48px;">
                <h2>Wallet Security & Features</h2>
                <p>Designed to give you full non-custodial ownership of your assets with zero security compromises.</p>
            </div>

            <div class="features-grid">
                <div class="glass-card">
                    <div class="feature-icon">
                        <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11a4 4 0 118 0c0 1.017-.07 2.019-.203 3m-2.118 6.844A21.88 21.88 0 0015.171 17m3.839 1.132c.645-2.266.99-4.659.99-7.132A8 8 0 008 4.07M3 15.364c.64-1.319 1-2.8 1-4.364 0-1.457.39-2.823 1.07-4"/></svg>
                    </div>
                    <h3>Biometric Security & PIN Protection</h3>
                    <p>Unlock your wallet instantly using Android Fingerprint or Face Authentication backed by Android Hardware KeyStore encryption.</p>
                </div>

                <div class="glass-card">
                    <div class="feature-icon">
                        <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/></svg>
                    </div>
                    <h3>Native AMM DEX Integration</h3>
                    <p>Swap VRS, CARBON, ECO, TREE, GREEN, and REDD tokens directly inside the app with real-time liquidity routing and sub-cent fees.</p>
                </div>

                <div class="glass-card">
                    <div class="feature-icon">
                        <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/></svg>
                    </div>
                    <h3>BIP-39 Seed Phrase Backup</h3>
                    <p>Full 12-word or 24-word seed phrase generation and import. Your private keys never leave your phone's isolated hardware enclave.</p>
                </div>

                <div class="glass-card">
                    <div class="feature-icon">
                        <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/></svg>
                    </div>
                    <h3>Live Carbon Impact Score</h3>
                    <p>View your exact carbon offset stats in real time. Track physical trees planted and satellite proof badges attached to your account.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- App Screen Mockup Showcase -->
    <section class="screenshots-section">
        <div class="container">
            <div style="text-align: center; max-width: 600px; margin: 0 auto 48px;">
                <h2>Interactive Screen Preview</h2>
                <p>Select a feature below to view the Verdis Wallet interface on mobile.</p>
            </div>

            <div class="phone-mockup-wrapper">
                <!-- Smartphone Frame -->
                <div class="phone-frame">
                    <div class="phone-notch"></div>
                    <div class="phone-screen">
                        <!-- Screen 1: Portfolio -->
                        <div id="screen-portfolio" class="screen-view active">
                            <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 4px;">TOTAL BALANCE</div>
                            <div style="font-size: 1.6rem; font-weight: 800; color: var(--accent-green);">$12,480.50</div>
                            <div style="font-size: 0.75rem; color: var(--accent-teal); margin-bottom: 16px;">12,480,500 VRS</div>

                            <div style="background: rgba(0, 255, 136, 0.1); border: 1px solid rgba(0, 255, 136, 0.2); border-radius: 10px; padding: 10px; margin-bottom: 16px; text-align: center;">
                                <div style="font-size: 0.7rem; color: var(--text-muted);">CO2 OFFSET IMPACT</div>
                                <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary);">4.2 Tonnes (120 Trees)</div>
                            </div>

                            <div style="font-size: 0.75rem; font-weight: 700; margin-bottom: 8px;">TOKENS</div>
                            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; padding: 8px 0; border-bottom: 1px solid var(--border-color);">
                                <span>VRS Token</span>
                                <span>12,480,500 VRS</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; padding: 8px 0; border-bottom: 1px solid var(--border-color);">
                                <span>CARBON Credit</span>
                                <span>420 CARBON</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; padding: 8px 0;">
                                <span>ECO Asset</span>
                                <span>1,500 ECO</span>
                            </div>
                        </div>

                        <!-- Screen 2: DEX Swap -->
                        <div id="screen-dex" class="screen-view">
                            <div style="font-size: 1rem; font-weight: 700; margin-bottom: 16px; text-align: center;">Native AMM Swap</div>
                            
                            <div style="background: rgba(15,31,26,0.9); border: 1px solid var(--border-color); padding: 10px; border-radius: 8px; margin-bottom: 10px;">
                                <div style="font-size: 0.7rem; color: var(--text-muted);">PAY</div>
                                <div style="display: flex; justify-content: space-between; font-weight: 700;">
                                    <span>1,000</span>
                                    <span style="color: var(--accent-green);">VRS</span>
                                </div>
                            </div>

                            <div style="text-align: center; margin: -4px 0 6px; color: var(--accent-green);">↓</div>

                            <div style="background: rgba(15,31,26,0.9); border: 1px solid var(--border-color); padding: 10px; border-radius: 8px; margin-bottom: 16px;">
                                <div style="font-size: 0.7rem; color: var(--text-muted);">RECEIVE</div>
                                <div style="display: flex; justify-content: space-between; font-weight: 700;">
                                    <span>10.5</span>
                                    <span style="color: var(--accent-teal);">CARBON</span>
                                </div>
                            </div>

                            <button style="width: 100%; padding: 10px; background: var(--accent-green); color: #000; font-weight: 700; border: none; border-radius: 8px; font-size: 0.85rem;">
                                Swap Tokens (0.1% Fee)
                            </button>
                        </div>

                        <!-- Screen 3: Reforestation -->
                        <div id="screen-trees" class="screen-view">
                            <div style="font-size: 1rem; font-weight: 700; margin-bottom: 12px; text-align: center;">Reforestation Log</div>
                            <div style="background: rgba(0,255,136,0.05); border: 1px solid var(--border-color); padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                                <div style="font-size: 0.75rem; font-weight: 700; color: var(--accent-green);">Tree Planting #1,492</div>
                                <div style="font-size: 0.7rem; color: var(--text-muted);">Lat: -3.4653, Long: -62.2159 (Amazon Basin)</div>
                                <div style="font-size: 0.65rem; color: var(--accent-teal); margin-top: 4px;">Status: Satellite Verified ✓</div>
                            </div>
                        </div>

                        <!-- Screen 4: Staking -->
                        <div id="screen-staking" class="screen-view">
                            <div style="font-size: 1rem; font-weight: 700; margin-bottom: 12px; text-align: center;">Validator Staking</div>
                            <div style="background: rgba(15,31,26,0.9); border: 1px solid var(--border-color); padding: 10px; border-radius: 8px; margin-bottom: 8px;">
                                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 700;">
                                    <span>EcoNode Alpha</span>
                                    <span style="color: var(--accent-green);">14.2% APY</span>
                                </div>
                                <div style="font-size: 0.7rem; color: var(--text-muted);">Active Validator • 100% Green Score</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Tab Selectors -->
                <div class="screen-tabs-list">
                    <button class="screen-tab-btn active" onclick="showScreen('screen-portfolio', this)">
                        <h4>01. Portfolio & Carbon Score</h4>
                        <p>View balances, asset breakdown, and cumulative CO2 offset tonnes.</p>
                    </button>

                    <button class="screen-tab-btn" onclick="showScreen('screen-dex', this)">
                        <h4>02. Native AMM DEX Swaps</h4>
                        <p>Instant trading between VRS, CARBON, ECO, and TREE tokens.</p>
                    </button>

                    <button class="screen-tab-btn" onclick="showScreen('screen-trees', this)">
                        <h4>03. Reforestation Satellite Log</h4>
                        <p>Verify physical GPS coordinates of trees planted by your transactions.</p>
                    </button>

                    <button class="screen-tab-btn" onclick="showScreen('screen-staking', this)">
                        <h4>04. Green DPoS Staking</h4>
                        <p>Delegate VRS tokens to eco-certified validators and earn yield.</p>
                    </button>
                </div>
            </div>
        </div>
    </section>

    <!-- Installation Guide -->
    <section class="guide-section">
        <div class="container">
            <div style="text-align: center; max-width: 600px; margin: 0 auto 48px;">
                <h2>Installation Guide</h2>
                <p>3 simple steps to get started on your Android device.</p>
            </div>

            <div class="guide-grid">
                <div class="guide-step">
                    <div class="step-tag">STEP 01</div>
                    <h3>Download APK</h3>
                    <p style="font-size: 0.9rem; margin-top: 8px;">Click the download button or scan the QR code to save <code style="color: var(--accent-green);">verdis-wallet.apk</code> to your device.</p>
                </div>

                <div class="guide-step">
                    <div class="step-tag">STEP 02</div>
                    <h3>Enable Unknown Sources</h3>
                    <p style="font-size: 0.9rem; margin-top: 8px;">If prompted by Android, toggle "Allow from this source" in your browser/file manager settings.</p>
                </div>

                <div class="guide-step">
                    <div class="step-tag">STEP 03</div>
                    <h3>Launch & Secure</h3>
                    <p style="font-size: 0.9rem; margin-top: 8px;">Open Verdis Wallet, generate or import your 12-word seed phrase, and enable Fingerprint lock.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="footer-grid">
                <div class="footer-brand">
                    <a href="landing.html" class="nav-logo">
                        <svg width="32" height="32" viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <polygon points="256,40 440,146 440,358 256,464 72,358 72,146" fill="none" stroke="#00ff88" stroke-width="12"/>
                            <path d="M 256 120 C 190 120, 150 180, 150 256 C 150 332, 190 392, 256 392 C 322 392, 362 332, 362 256 C 362 180, 322 120, 256 120 Z" fill="#00ff88"/>
                        </svg>
                        VERDIS
                    </a>
                    <p>The world's first fully green, carbon-negative blockchain network.</p>
                </div>

                <div class="footer-col">
                    <h4>Navigation</h4>
                    <ul>
                        <li><a href="landing.html">Home Landing</a></li>
                        <li><a href="whitepaper_v2.html" target="_blank">Whitepaper</a></li>
                        <li><a href="explorer-dashboard.html" target="_blank">Explorer</a></li>
                    </ul>
                </div>

                <div class="footer-col">
                    <h4>Wallet Features</h4>
                    <ul>
                        <li><a href="#features">Biometric PIN</a></li>
                        <li><a href="#features">Native AMM DEX</a></li>
                        <li><a href="#features">BIP-39 Backup</a></li>
                    </ul>
                </div>

                <div class="footer-col">
                    <h4>Community</h4>
                    <ul>
                        <li><a href="https://twitter.com" target="_blank">Twitter / X</a></li>
                        <li><a href="https://telegram.org" target="_blank">Telegram</a></li>
                        <li><a href="https://discord.com" target="_blank">Discord</a></li>
                    </ul>
                </div>
            </div>

            <div class="footer-bottom">
                <div>© 2026 Verdis Foundation. All rights reserved.</div>
                <div style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--accent-green);">
                    Verdis Mobile App v2.0.0
                </div>
            </div>
        </div>
    </footer>

    <!-- JavaScript Interactions -->
    <script>
        // Particle Canvas Animation
        const canvas = document.getElementById('bg-canvas');
        const ctx = canvas.getContext('2d');
        let width, height;

        function resizeCanvas() {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        const nodes = [];
        for (let i = 0; i < 30; i++) {
            nodes.push({
                x: Math.random() * width,
                y: Math.random() * height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                r: Math.random() * 2 + 1
            });
        }

        function animateCanvas() {
            ctx.clearRect(0, 0, width, height);
            for (let i = 0; i < nodes.length; i++) {
                let n = nodes[i];
                n.x += n.vx;
                n.y += n.vy;
                if (n.x < 0 || n.x > width) n.vx *= -1;
                if (n.y < 0 || n.y > height) n.vy *= -1;

                ctx.beginPath();
                ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
                ctx.fillStyle = '#00ff88';
                ctx.fill();

                for (let j = i + 1; j < nodes.length; j++) {
                    let n2 = nodes[j];
                    let dx = n.x - n2.x;
                    let dy = n.y - n2.y;
                    let dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 120) {
                        ctx.beginPath();
                        ctx.moveTo(n.x, n.y);
                        ctx.lineTo(n2.x, n2.y);
                        ctx.strokeStyle = `rgba(0, 255, 136, ${0.2 * (1 - dist / 120)})`;
                        ctx.stroke();
                    }
                }
            }
            requestAnimationFrame(animateCanvas);
        }
        animateCanvas();

        // Phone Screen Preview Switcher
        function showScreen(screenId, btn) {
            document.querySelectorAll('.screen-view').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.screen-tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(screenId).classList.add('active');
            btn.classList.add('active');
        }
    </script>
</body>
</html>
"""

with open('download.html', 'w', encoding='utf-8') as f:
    f.write(download_html)

print("Created download.html successfully.")
