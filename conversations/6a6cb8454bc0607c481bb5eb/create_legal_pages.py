#!/usr/bin/env python3
"""Create cookie policy, security, and disclaimer pages."""
import os

WEB_ROOT = "/var/www/verdiscan"

# Shared CSS (nav + hero + TOC + content + footer)
SHARED_CSS = """
:root{--bg:#f1f5f9;--card:#fff;--text:#0f172a;--text-dim:#334155;--text-mute:#64748b;--border:#e2e8f0;--accent:#16a34a;--accent-bg:#f0ffe0;--radius:12px;--radius-sm:8px;--font:'Inter',sans-serif;--font-mono:'JetBrains Mono',monospace;--font-head:'Space Grotesk',sans-serif}
*{margin:0;padding:0;box-sizing:border-box}body{font-family:var(--font);background:var(--bg);color:var(--text);line-height:1.7}a{color:inherit;text-decoration:none}a.link{color:#1e40af;text-decoration:underline}
.nav{position:sticky;top:0;z-index:100;background:rgba(255,255,255,.92);backdrop-filter:blur(16px);border-bottom:1px solid var(--border)}.nav-inner{max-width:1280px;margin:0 auto;padding:0 24px;height:64px;display:flex;align-items:center;justify-content:space-between}.nav-logo{display:flex;align-items:center;gap:8px;font-family:var(--font-head);font-weight:700;font-size:20px}.nav-logo img{height:32px}.nav-links{display:flex;align-items:center;gap:2px}.nav-links a{padding:8px 10px;border-radius:var(--radius-sm);font-size:13px;font-weight:500;color:var(--text-dim);transition:all .2s}.nav-links a:hover{background:var(--accent-bg);color:var(--text)}.nav-status{display:flex;align-items:center;gap:6px;font-size:13px;color:#22c55e;font-weight:500}.nav-status .dot{width:8px;height:8px;border-radius:50%;background:#22c55e;box-shadow:0 0 8px #22c55e;animation:pulse 2s infinite}@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}.hamburger{display:none;background:none;border:none;cursor:pointer;padding:8px}.hamburger span{display:block;width:20px;height:2px;background:var(--text);margin:4px 0}
.hero{background:linear-gradient(135deg,#0f172a 0%,#1a2e00 50%,#0f172a 100%);padding:64px 24px 48px;text-align:center;position:relative;overflow:hidden}.hero::before{content:'';position:absolute;inset:0;background:radial-gradient(circle at 30% 50%,rgba(22,163,74,.08) 0%,transparent 50%),radial-gradient(circle at 70% 50%,rgba(22,163,74,.05) 0%,transparent 50%);pointer-events:none}.hero h1{font-family:var(--font-head);font-size:42px;font-weight:700;color:#fff;position:relative}.hero .updated{font-size:15px;color:#94a3b8;margin-top:8px;position:relative}
.toc-layout{display:flex;max-width:1280px;margin:0 auto;padding:40px 24px;gap:32px}.toc{width:240px;flex-shrink:0;position:sticky;top:80px;height:fit-content;max-height:calc(100vh - 100px);overflow-y:auto}.toc h3{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--text-mute);margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid var(--border)}.toc a{display:block;padding:6px 12px;font-size:13px;color:var(--text-dim);border-radius:var(--radius-sm);transition:.15s;cursor:pointer;line-height:1.4}.toc a:hover{background:var(--accent-bg);color:var(--text)}.toc a .num{display:inline-block;width:24px;color:var(--text-mute);font-family:var(--font-mono);font-size:11px}
.content{flex:1;min-width:0;max-width:860px}.content-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:40px 48px;margin-bottom:16px}.section{margin-bottom:40px}.section:last-child{margin-bottom:0}.section h2{font-family:var(--font-head);font-size:22px;font-weight:700;margin-bottom:16px;color:var(--text);display:flex;align-items:baseline;gap:8px}.section h2 .snum{font-size:16px;font-weight:700;color:var(--accent);font-family:var(--font-mono);background:var(--accent-bg);padding:2px 8px;border-radius:6px}.section p{font-size:15px;color:var(--text-dim);margin-bottom:12px}.section ul{list-style:none;margin:8px 0 12px 0;padding-left:20px}.section ul li{font-size:15px;color:var(--text-dim);margin-bottom:6px;padding-left:16px;position:relative}.section ul li::before{content:'\\2022';color:var(--accent);font-weight:700;position:absolute;left:0}.section strong{color:var(--text);font-weight:600}.section table{width:100%;border-collapse:collapse;margin:12px 0}.section table th{background:var(--accent-bg);font-size:13px;font-weight:600;text-align:left;padding:10px 12px;border:1px solid var(--border)}.section table td{font-size:14px;padding:10px 12px;border:1px solid var(--border)}.section table tr:hover td{background:var(--bg)}.section .info-card{background:var(--bg);border:1px solid var(--border);border-radius:var(--radius-sm);padding:20px;margin:12px 0}.section .info-card h3{font-size:16px;font-weight:600;margin-bottom:8px;color:var(--text)}.section .info-card p{font-size:14px;margin-bottom:0}
.footer{background:#0f172a;color:#94a3b8;padding:48px 24px 24px}.footer-inner{max-width:1280px;margin:0 auto;display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;gap:32px}.footer-brand h3{color:#fff;font-family:var(--font-head),sans-serif;font-size:18px;margin-bottom:12px;font-weight:700}.footer-brand p{font-size:14px;max-width:280px;line-height:1.6;color:#94a3b8}.footer-social{display:flex;gap:8px;margin-top:16px}.footer-social a{width:36px;height:36px;border-radius:8px;background:rgba(255,255,255,.05);display:flex;align-items:center;justify-content:center;transition:.2s;color:#94a3b8}.footer-social a:hover{background:rgba(22,163,74,.15);color:#16a34a}.footer-col h4{color:#fff;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;margin-bottom:12px}.footer-col a{display:block;font-size:14px;padding:5px 0;color:#94a3b8;transition:.2s;text-decoration:none}.footer-col a:hover{color:#16a34a}.footer-bottom{max-width:1280px;margin:32px auto 0;padding-top:20px;border-top:1px solid #1e293b;display:flex;justify-content:space-between;font-size:13px;color:#64748b}.footer-bottom a{text-decoration:none;color:#64748b}.footer-bottom a:hover{color:#16a34a}
@media(max-width:1024px){.toc{display:none}.content-card{padding:24px}}@media(max-width:768px){.nav-links{display:none;position:fixed;top:64px;left:0;right:0;background:#fff;flex-direction:column;padding:16px;border-bottom:1px solid var(--border);z-index:99}.nav-links.open{display:flex}.hamburger{display:block}.hero h1{font-size:28px}.footer-inner{grid-template-columns:1fr 1fr;gap:24px}.footer-bottom{flex-direction:column;gap:8px;text-align:center}.content-card{padding:20px}}@media(max-width:480px){.footer-inner{grid-template-columns:1fr}}
"""

NAV_HTML = '<nav class="nav"><div class="nav-inner"><a href="/" class="nav-logo"><img src="/assets/verdis-logo-black.png" alt="Verdis" height="32"></a><div class="nav-links" id="navLinks"><a href="/">Home</a><a href="/explorer/">Verdiscan</a><a href="/dex/">DEX</a><a href="/validators/">Validators</a><a href="/eco/">Eco</a><a href="/faucet/">Faucet</a><a href="/wallet/">Wallet</a><a href="/sale/">Sale</a><a href="/api/">API</a><a href="/docs/">Docs</a></div><div style="display:flex;align-items:center;gap:16px"><div class="nav-status"><span class="dot"></span>Testnet Live</div><button class="hamburger" onclick="document.getElementById(\'navLinks\').classList.toggle(\'open\')"><span></span><span></span><span></span></button></div></div></nav>'

FOOTER_HTML = '''<footer class="footer">
<div class="footer-inner">
<div class="footer-brand">
<h3>VERDIS CHAIN</h3>
<p>The world's first green blockchain with native DPoS consensus, AMM DEX, and carbon credit tracking. Built on Substrate.</p>
<div class="footer-social">
<a href="https://github.com/Protremix/Verdischain-" target="_blank" aria-label="GitHub"><svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.385.6.113.82-.26.82-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.5 11.5 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.218.694.825.576C20.565 21.795 24 17.298 24 12 24 5.37 18.627 0 12 0z"/></svg></a>
<a href="/contact/" aria-label="Contact"><svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M24 4l-12 7-12-7v-2l12 7 12-7v2zm0 2v14h-24v-14l12 7 12-7z"/></svg></a>
</div>
</div>
<div class="footer-col"><h4>Products</h4><a href="/explorer/">Verdiscan</a><a href="/dex/">DEX</a><a href="/wallet/">Web Wallet</a><a href="/faucet/">Faucet</a><a href="/sale/">Token Sale</a></div>
<div class="footer-col"><h4>Resources</h4><a href="/docs/">Documentation</a><a href="/whitepaper/">Whitepaper</a><a href="/tokenomics/">Tokenomics</a><a href="/api/">API Reference</a><a href="https://github.com/Protremix/Verdischain-" target="_blank">GitHub</a></div>
<div class="footer-col"><h4>Community</h4><a href="/validators/">Validators</a><a href="/eco/">Eco Metrics</a><a href="/referral/">Referral Program</a><a href="/incentives/">Validator Incentives</a><a href="/contact/">Contact</a></div>
<div class="footer-col"><h4>Legal</h4><a href="/terms/">Terms of Service</a><a href="/privacy/">Privacy Policy</a><a href="/cookies/">Cookie Policy</a><a href="/security/">Security</a><a href="/disclaimer/">Disclaimer</a></div>
</div>
<div class="footer-bottom"><span>&copy; 2026 Verdis Chain &middot; Protremix &middot; Open-source under MIT License</span><span><a href="/privacy/" style="color:#64748b;text-decoration:none">GDPR Compliant</a> &middot; <a href="/security/" style="color:#64748b;text-decoration:none">Security</a></span></div>
</footer>'''

TOC_SCRIPT = "<script>const sections=document.querySelectorAll('.section');const tocList=document.getElementById('tocList');sections.forEach((s)=>{const h=s.querySelector('h2');if(!h)return;const num=s.id.replace('s','');const text=h.textContent.replace(num,'').trim();const a=document.createElement('a');a.href='#'+s.id;a.innerHTML='<span class=\"num\">'+num+'</span>'+text;tocList.appendChild(a)});</script>"

def build_page(title, meta_desc, canonical, hero_title, updated, sections_html, og_title=None, og_desc=None):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{meta_desc}">
<meta property="og:type" content="website">
<meta property="og:title" content="{og_title or title}">
<meta property="og:description" content="{og_desc or meta_desc}">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="/assets/favicon.ico" type="image/x-icon">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>{SHARED_CSS}</style>
</head>
<body>
{NAV_HTML}
<section class="hero"><h1>{hero_title}</h1><div class="updated">{updated}</div></section>
<div class="toc-layout">
<aside class="toc"><h3>Contents</h3><div id="tocList"></div></aside>
<main class="content"><div class="content-card">
{sections_html}
</div></main>
</div>
{FOOTER_HTML}
{TOC_SCRIPT}
</body>
</html>'''

# ============================================================
# COOKIE POLICY
# ============================================================
cookie_sections = """
<div class="section" id="s1"><h2><span class="snum">1</span> Introduction</h2>
<p>1.1. This Cookie Policy explains how Verdis Chain ("we", "us", or "our"), operated by Protremix, uses cookies and similar technologies on our website at verdischain.com (the "Site"). By using the Site, you consent to the use of cookies as described in this policy.</p>
<p>1.2. Cookies are small text files stored on your device when you visit a website. They are widely used to make websites work more efficiently and to provide information to the site owners.</p></div>

<div class="section" id="s2"><h2><span class="snum">2</span> Types of Cookies We Use</h2>
<p>We use the following categories of cookies on the Site:</p>
<table>
<tr><th>Cookie Type</th><th>Purpose</th><th>Duration</th></tr>
<tr><td><strong>Essential</strong></td><td>Required for the Site to function (navigation, security, session management)</td><td>Session</td></tr>
<tr><td><strong>Functional</strong></td><td>Remember your preferences (theme, language, wallet connection)</td><td>30 days</td></tr>
<tr><td><strong>Analytics</strong></td><td>Track usage patterns to improve Site performance and user experience</td><td>24 hours</td></tr>
<tr><td><strong>Performance</strong></td><td>Monitor RPC endpoint latency and blockchain node health</td><td>Session</td></tr>
</table>
<p>2.1. We do <strong>not</strong> use advertising cookies, third-party tracking cookies, or social media tracking pixels on the Site.</p></div>

<div class="section" id="s3"><h2><span class="snum">3</span> Essential Cookies</h2>
<p>3.1. Essential cookies are necessary for the Site to function properly. They enable core functionality such as network navigation, access to secure areas, and the blockchain RPC connection. The Site cannot function properly without these cookies.</p>
<p>3.2. Essential cookies we use include:</p>
<ul><li><strong>session_id</strong> &mdash; Maintains your session when interacting with the Web Wallet or DEX</li><li><strong>csrf_token</strong> &mdash; Protects against cross-site request forgery attacks</li><li><strong>rpc_endpoint</strong> &mdash; Remembers your preferred RPC node endpoint</li></ul></div>

<div class="section" id="s4"><h2><span class="snum">4</span> Functional Cookies</h2>
<p>4.1. Functional cookies allow the Site to remember choices you make (such as your preferred theme, wallet address, or language) and provide enhanced, more personalized features.</p>
<p>4.2. These cookies are optional and can be disabled without affecting the core functionality of the Site.</p></div>

<div class="section" id="s5"><h2><span class="snum">5</span> Analytics Cookies</h2>
<p>5.1. We use self-hosted analytics to understand how visitors interact with the Site. This helps us improve the user experience and optimize performance. All analytics data is anonymized and aggregated.</p>
<p>5.2. We do not use Google Analytics, Facebook Pixel, or any third-party analytics service that shares data with external parties.</p></div>

<div class="section" id="s6"><h2><span class="snum">6</span> Managing Cookies</h2>
<p>6.1. You can control and manage cookies through your browser settings. Most browsers allow you to:</p>
<ul><li>View all cookies currently stored on your device</li><li>Block all cookies or specific cookies</li><li>Clear all cookies when you close your browser</li><li>Block third-party cookies</li></ul>
<p>6.2. Note that blocking essential cookies may prevent the Site from functioning properly. The Web Wallet, DEX, and Verdiscan explorer require essential cookies to operate.</p></div>

<div class="section" id="s7"><h2><span class="snum">7</span> Blockchain-Specific Data</h2>
<p>7.1. The Verdis Chain Site uses browser storage specific to blockchain interaction:</p>
<ul><li><strong>wallet_address</strong> &mdash; Stores your connected wallet address (public key only, no private keys are ever stored)</li><li><strong>network_type</strong> &mdash; Remembers whether you are connected to testnet or mainnet</li><li><strong>faucet_cooldown</strong> &mdash; Tracks faucet request cooldown periods (testnet only)</li></ul>
<p>7.2. We <strong>never</strong> store private keys, seed phrases, or any sensitive cryptographic material in cookies or browser storage. Wallet connections are made entirely client-side.</p></div>

<div class="section" id="s8"><h2><span class="snum">8</span> Third-Party Services</h2>
<p>8.1. The Site uses Google Fonts for typography. Google may set cookies when loading fonts. We use the <code>preconnect</code> method to minimize data sent to third parties.</p>
<p>8.2. The Site does not embed third-party widgets, social media buttons, or advertising networks that would set additional cookies.</p></div>

<div class="section" id="s9"><h2><span class="snum">9</span> Changes to This Policy</h2>
<p>9.1. We may update this Cookie Policy from time to time. Any changes will be posted on this page with an updated revision date. We encourage you to review this policy periodically.</p>
<p>9.2. If we make material changes, we will provide a prominent notice on the Site prior to the change taking effect.</p></div>

<div class="section" id="s10"><h2><span class="snum">10</span> Contact Us</h2>
<p>10.1. If you have questions about this Cookie Policy, please contact us:</p>
<ul><li>Email: <a class="link" href="mailto:legal@protremix.com">legal@protremix.com</a></li><li>Website: <a class="link" href="/contact/">Contact Page</a></li></ul>
<p>10.2. You may also review our <a class="link" href="/privacy/">Privacy Policy</a> and <a class="link" href="/terms/">Terms of Service</a> for more information.</p></div>
"""

# ============================================================
# SECURITY PAGE
# ============================================================
security_sections = """
<div class="section" id="s1"><h2><span class="snum">1</span> Overview</h2>
<p>1.1. Security is a core priority for Verdis Chain. As a blockchain platform handling user assets through the Web Wallet, DEX, and faucet, we implement multiple layers of security across infrastructure, application, and protocol levels.</p>
<p>1.2. This page documents our security practices, architecture, and responsible disclosure policy. We are committed to transparency and continuous improvement of our security posture.</p></div>

<div class="section" id="s2"><h2><span class="snum">2</span> Infrastructure Security</h2>
<div class="info-card"><h3>Server Hardening</h3><p>SSH key-only authentication (password login disabled), Fail2Ban intrusion prevention, automated security updates, and minimal attack surface through service isolation.</p></div>
<div class="info-card"><h3>SSL/TLS Configuration</h3><p>TLS 1.3 enforced with HSTS, strong cipher suites, OCSP stapling, and automatic certificate renewal via Let's Encrypt. All traffic served over HTTPS with HTTP-to-HTTPS redirects.</p></div>
<div class="info-card"><h3>Security Headers</h3><p>Content-Security-Policy (CSP), X-Frame-Options, X-Content-Type-Options, X-XSS-Protection, Referrer-Policy, and Permissions-Policy headers configured on all pages via nginx.</p></div>
<div class="info-card"><h3>Network Security</h3><p>Firewall rules restrict access to internal services (RPC, database, monitoring). Only HTTP/HTTPS (ports 80/443) and WebSocket endpoints are publicly accessible.</p></div></div>

<div class="section" id="s3"><h2><span class="snum">3</span> Wallet Security</h2>
<p>3.1. The Verdis Chain Web Wallet is a <strong>non-custodial</strong> wallet. This means:</p>
<ul><li>Your private keys are generated and stored entirely in your browser's local storage</li><li>We never transmit, store, or have access to your private keys or seed phrase</li><li>All transactions are signed client-side before being broadcast to the network</li><li>You are solely responsible for backing up your seed phrase securely</li></ul>
<p>3.2. We use <strong>@noble/secp256k1</strong> and <strong>@noble/hashes</strong> for cryptographic operations, which are audited, battle-tested cryptographic libraries.</p>
<p>3.3. The wallet supports importing existing accounts via seed phrase or private key. Imported keys are processed entirely in the browser and never sent to any server.</p></div>

<div class="section" id="s4"><h2><span class="snum">4</span> Blockchain Protocol Security</h2>
<p>4.1. Verdis Chain uses <strong>Delegated Proof of Stake (DPoS)</strong> consensus with the following security properties:</p>
<ul><li><strong>Validator selection</strong> &mdash; 14 active validators elected by token holders</li><li><strong>Slashing</strong> &mdash; Validators can be slashed for malicious behavior (double-signing, downtime)</li><li><strong>Finality</strong> &mdash; Blocks are finalized through GRANDPA consensus</li><li><strong>On-chain governance</strong> &mdash; Protocol upgrades require on-chain approval</li></ul>
<p>4.2. The Substrate framework provides additional security through:</p>
<ul><li>Sandboxed WebAssembly (WASM) execution environment</li><li>Weight-based fee system preventing resource exhaustion attacks</li><li>Storage rent preventing state bloat</li><li>Upgradable runtime without hard forks</li></ul></div>

<div class="section" id="s5"><h2><span class="snum">5</span> Smart Contract Security</h2>
<p>5.1. The Verdis Chain runtime includes the following pallets that have undergone internal security review:</p>
<ul><li><strong>AMM DEX</strong> &mdash; Constant product formula with overflow protection</li><li><strong>DPoS</strong> &mdash; Validator election, staking, and slashing logic</li><li><strong>Eco</strong> &mdash; Carbon credit tracking and green validator scoring</li><li><strong>Tokenomics</strong> &mdash; Token supply, vesting, and allocation management</li><li><strong>EVM</strong> &mdash; Ethereum-compatible smart contract execution</li></ul>
<p>5.2. A comprehensive security audit was conducted in August 2026, covering all pallets. Key findings were remediated:</p>
<ul><li>Fixed division-by-zero vulnerability in <code>remove_liquidity</code></li><li>Fixed self-scoring vulnerability in <code>update_green_score</code></li><li>Added authorization check to <code>mint_carbon_credit</code></li><li>Added overflow protection to LP token minting</li></ul></div>

<div class="section" id="s6"><h2><span class="snum">6</span> DEX Security</h2>
<p>6.1. The AMM DEX implements the following security measures:</p>
<ul><li><strong>Overflow protection</strong> &mdash; All arithmetic operations use checked math</li><li><strong>Slippage protection</strong> &mdash; Users specify minimum output amounts</li><li><strong>Deadline protection</strong> &mdash; Transactions expire after a block deadline</li><li><strong>Reentrancy guard</strong> &mdash; Prevents reentrancy attacks on swap and liquidity functions</li><li><strong>Front-running mitigation</strong> &mdash; Transaction ordering is determined by the block producer</li></ul></div>

<div class="section" id="s7"><h2><span class="snum">7</span> Data Protection</h2>
<p>7.1. We comply with GDPR requirements. See our <a class="link" href="/privacy/">Privacy Policy</a> for details on data collection, processing, and user rights.</p>
<p>7.2. We do not collect or store:</p>
<ul><li>Private keys or seed phrases</li><li>Personally identifiable information beyond what is necessary for service operation</li><li>Analytics data shared with third parties</li></ul>
<p>7.3. Blockchain transactions are public by nature. All transactions on the Verdis Chain are visible on the <a class="link" href="/explorer/">Verdiscan explorer</a>.</p></div>

<div class="section" id="s8"><h2><span class="snum">8</span> Responsible Disclosure</h2>
<p>8.1. We take security vulnerabilities seriously. If you discover a security issue, we encourage responsible disclosure.</p>
<div class="info-card"><h3>How to Report</h3><p>Email: <a class="link" href="mailto:security@protremix.com">security@protremix.com</a><br>Please include a detailed description of the vulnerability, steps to reproduce, and potential impact.</p></div>
<p>8.2. We commit to:</p>
<ul><li>Acknowledging receipt of your report within 48 hours</li><li>Providing an initial assessment within 5 business days</li><li>Notifying you when the vulnerability is fixed</li><li>Crediting responsible disclosure (unless you prefer to remain anonymous)</li></ul>
<p>8.3. We ask that you:</p>
<ul><li>Do not exploit the vulnerability or access others' data</li><li>Do not publicly disclose the vulnerability until it is fixed</li><li>Provide sufficient information to reproduce and verify the issue</li></ul></div>

<div class="section" id="s9"><h2><span class="snum">9</span> Incident Response</h2>
<p>9.1. In the event of a security incident, we will:</p>
<ul><li>Assess the scope and impact immediately</li><li>Notify affected users within 72 hours of confirmation</li><li>Take corrective action to prevent recurrence</li><li>Conduct a post-mortem and publish findings where appropriate</li></ul>
<p>9.2. For critical vulnerabilities affecting user funds, we may pause the DEX or faucet temporarily while remediation is deployed.</p></div>

<div class="section" id="s10"><h2><span class="snum">10</span> Contact</h2>
<p>10.1. For security-related questions or concerns:</p>
<ul><li>Security: <a class="link" href="mailto:security@protremix.com">security@protremix.com</a></li><li>General: <a class="link" href="/contact/">Contact Page</a></li><li>Legal: <a class="link" href="mailto:legal@protremix.com">legal@protremix.com</a></li></ul></div>
"""

# ============================================================
# DISCLAIMER PAGE
# ============================================================
disclaimer_sections = """
<div class="section" id="s1"><h2><span class="snum">1</span> General Disclaimer</h2>
<p>1.1. The information provided by Verdis Chain on verdischain.com is for general informational purposes only. All information on the Site is provided in good faith; however, we make no representation or warranty of any kind, express or implied, regarding the accuracy, adequacy, validity, reliability, availability, or completeness of any information on the Site.</p>
<p>1.2. Under no circumstance shall we have any liability to you for any loss or damage of any kind incurred as a result of the use of the Site or reliance on any information provided on the Site. Your use of the Site and your reliance on any information on the Site is solely at your own risk.</p></div>

<div class="section" id="s2"><h2><span class="snum">2</span> Not Financial Advice</h2>
<p>2.1. The content on the Site, including but not limited to tokenomics, sale pages, DEX interfaces, and validator information, does not constitute financial, investment, trading, or any other type of advice.</p>
<p>2.2. Nothing on the Site should be interpreted as a solicitation, recommendation, endorsement, or offer to buy or sell any tokens, securities, or other financial instruments.</p>
<p>2.3. Cryptocurrency and blockchain investments carry a high level of risk and can result in the loss of your entire investment. You should carefully consider whether trading or holding cryptocurrencies is suitable for you in light of your financial circumstances.</p>
<p>2.4. Always conduct your own research and consult with a qualified financial advisor before making any investment decisions.</p></div>

<div class="section" id="s3"><h2><span class="snum">3</span> Testnet Status</h2>
<p>3.1. The Verdis Chain network is currently operating as a <strong>testnet</strong>. Tokens on the testnet have no monetary value and are provided for testing and development purposes only.</p>
<p>3.2. The testnet may be reset, purged, or experience downtime without prior notice. Any tokens, transactions, or smart contract state on the testnet may be lost.</p>
<p>3.3. The faucet distributes testnet tokens at no cost. Faucet tokens are for testing purposes only and have no real-world value.</p></div>

<div class="section" id="s4"><h2><span class="snum">4</span> Wallet and Key Management</h2>
<p>4.1. The Verdis Chain Web Wallet is non-custodial. You are solely responsible for the security of your private keys and seed phrase.</p>
<p>4.2. If you lose your private keys or seed phrase, your funds cannot be recovered. We do not have access to your keys and cannot assist in recovery.</p>
<p>4.3. Never share your private keys or seed phrase with anyone. Verdis Chain staff will never ask for your private keys or seed phrase.</p></div>

<div class="section" id="s5"><h2><span class="snum">5</span> DEX Risks</h2>
<p>5.1. Using the AMM DEX involves risks including but not limited to:</p>
<ul><li><strong>Impermanent loss</strong> &mdash; The value of liquidity provider tokens may differ from simply holding the underlying assets</li><li><strong>Slippage</strong> &mdash; The executed price may differ from the expected price</li><li><strong>Smart contract risk</strong> &mdash; Bugs or vulnerabilities in the DEX pallet could result in loss of funds</li><li><strong>Liquidity risk</strong> &mdash; You may not be able to withdraw liquidity if the pool is insufficient</li></ul>
<p>5.2. You assume all risks associated with using the DEX. We are not liable for any losses incurred through DEX usage.</p></div>

<div class="section" id="s6"><h2><span class="snum">6</span> No Warranties</h2>
<p>6.1. The Site and all services are provided "as is" and "as available" without any warranties of any kind, either express or implied, including but not limited to implied warranties of merchantability, fitness for a particular purpose, or non-infringement.</p>
<p>6.2. We do not warrant that the Site will be uninterrupted, secure, or error-free, that defects will be corrected, or that the Site or the server that makes it available are free of viruses or other harmful components.</p></div>

<div class="section" id="s7"><h2><span class="snum">7</span> Limitation of Liability</h2>
<p>7.1. To the fullest extent permitted by applicable law, in no event shall Verdis Chain, Protremix, or its affiliates be liable for any indirect, incidental, special, consequential, or punitive damages, or any loss of profits or revenues, whether incurred directly or indirectly, or any loss of data, use, goodwill, or other intangible losses, resulting from your access to or use of the Site or services.</p></div>

<div class="section" id="s8"><h2><span class="snum">8</span> External Links</h2>
<p>8.1. The Site may contain links to other websites or content belonging to or originating from third parties. We do not investigate, monitor, or check such external links for accuracy, adequacy, validity, reliability, availability, or completeness.</p>
<p>8.2. We are not responsible for the content of any external websites. The presence of any external link does not constitute a recommendation or endorsement.</p></div>

<div class="section" id="s9"><h2><span class="snum">9</span> Changes to This Disclaimer</h2>
<p>9.1. We reserve the right to update or change this Disclaimer at any time. Any changes will be posted on this page with an updated revision date.</p></div>

<div class="section" id="s10"><h2><span class="snum">10</span> Contact</h2>
<p>10.1. If you have questions about this Disclaimer, please contact us:</p>
<ul><li>Email: <a class="link" href="mailto:legal@protremix.com">legal@protremix.com</a></li><li>Website: <a class="link" href="/contact/">Contact Page</a></li></ul></div>
"""

# Write pages
for dirname, page_content in [
    ("cookies", build_page(
        "Cookie Policy — Verdis Chain",
        "Cookie Policy for Verdis Chain, Verdiscan explorer, AMM DEX, Web Wallet, and API. Last updated August 8, 2026.",
        "https://verdischain.com/cookies/",
        "Cookie Policy",
        "Last updated: August 8, 2026",
        cookie_sections
    )),
    ("security", build_page(
        "Security — Verdis Chain",
        "Security overview for Verdis Chain, including infrastructure security, wallet security, smart contract audits, and responsible disclosure. Last updated August 8, 2026.",
        "https://verdischain.com/security/",
        "Security",
        "Last updated: August 8, 2026",
        security_sections
    )),
    ("disclaimer", build_page(
        "Disclaimer — Verdis Chain",
        "Disclaimer for Verdis Chain, Verdiscan explorer, AMM DEX, Web Wallet, and associated services. Last updated August 8, 2026.",
        "https://verdischain.com/disclaimer/",
        "Disclaimer",
        "Last updated: August 8, 2026",
        disclaimer_sections
    )),
]:
    dirpath = os.path.join(WEB_ROOT, dirname)
    os.makedirs(dirpath, exist_ok=True)
    open(os.path.join(dirpath, "index.html"), "w").write(page_content)
    print(f"  Created: {dirname}/index.html ({len(page_content)} bytes)")

print("\nDone! All legal pages created.")
