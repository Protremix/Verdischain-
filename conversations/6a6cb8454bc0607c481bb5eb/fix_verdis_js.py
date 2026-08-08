#!/usr/bin/env python3
"""Update verdis.js nav and footer links."""

with open("/var/www/verdiscan/js/verdis.js") as f:
    c = f.read()

# New nav links
old_nav = """  <ul class="verdis-nav-links">
    <li><a href="/#what-is-verdis">Overview</a></li>
    <li><a href="/#technology">Technology</a></li>
    <li><a href="/#token">Token</a></li>
    <li><a href="/explorer/">Explorer</a></li>
    <li><a href="/wallet/">Wallet</a></li>
    <li><a href="/download/">Download</a></li>
    <li><a href="/developers/">Developers</a></li>
    <li><a href="/docs/">Docs</a></li>
    <li><a href="/whitepaper/">Whitepaper</a></li>
  </ul>"""

new_nav = """  <ul class="verdis-nav-links">
    <li><a href="/explorer/">Verdiscan</a></li>
    <li><a href="/dex/">DEX</a></li>
    <li><a href="/whitepaper/">Whitepaper</a></li>
    <li><a href="/wallet/">Wallet</a></li>
    <li><a href="/sale/">Sale</a></li>
    <li><a href="/tokenomics/">Tokenomics</a></li>
    <li><a href="/faucet/">Faucet</a></li>
  </ul>"""

if old_nav in c:
    c = c.replace(old_nav, new_nav)
    print("FIXED: nav links in verdis.js")
else:
    print("WARN: Could not find old nav in verdis.js")

# Update footer to include all links
old_footer = """  <div class="verdis-footer-grid">
    <div class="verdis-footer-brand">
      <div class="verdis-footer-brand-header">
        <h3><svg class="verdis-anim-logo" style="width:24px;height:24px;display:inline-block;vertical-align:middle;margin-right:8px" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg"><path class="hex-path" d="M20 3L34 11V27L20 35L6 27V11L20 3Z" stroke="#00ff88" stroke-width="2" fill="rgba(0,255,136,0.03)" stroke-linecap="round" stroke-linejoin="round"/><path class="v-path" d="M13 13L20 27M27 13L20 27" stroke="#00ff88" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><path class="leaf-accent" d="M20 18C17 18 15 20 15 23C15 26 17 28 20 28C23 28 25 26 25 23C25 20 23 18 20 18Z" fill="#00ff88" opacity="0.3"/></svg>Verdis</h3>
      </div>
      <p>The world's first fully green, carbon-negative blockchain ecosystem. Built with Substrate, powered by nature.</p>
    </div>
    <div class="verdis-footer-col">
      <h4>Ecosystem</h4>
      <a href="/explorer/">Explorer</a>
      <a href="/wallet/">Wallet</a>
      <a href="/download/">Download</a>
      <a href="/dex/">DEX</a>
      <a href="/faucet/">Faucet</a>
      <a href="/validators/">Validators</a>
    </div>
    <div class="verdis-footer-col">
      <h4>Developers</h4>
      <a href="/developers/">Portal</a>
      <a href="/docs/">Documentation</a>
      <a href="/whitepaper/">Whitepaper</a>
      <a href="https://rpc.verdischain.com" target="_blank">RPC Endpoint</a>
    </div>
    <div class="verdis-footer-col">
      <h4>Resources</h4>
      <a href="/#token">Token</a>
      <a href="/tokenomics/">Tokenomics</a>
      <a href="/token-sale/">Presale</a>
      <a href="/blog/">Blog</a>
    </div>
    <div class="verdis-footer-col">
      <h4>Community</h4>
      <a href="https://github.com/verdischain" target="_blank">GitHub</a>
      <a href="/#community">Join Us</a>
      <a href="/#contact">Contact</a>
    </div>
  </div>"""

new_footer = """  <div class="verdis-footer-grid">
    <div class="verdis-footer-brand">
      <div class="verdis-footer-brand-header">
        <h3><svg class="verdis-anim-logo" style="width:24px;height:24px;display:inline-block;vertical-align:middle;margin-right:8px" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg"><path class="hex-path" d="M20 3L34 11V27L20 35L6 27V11L20 3Z" stroke="#00ff88" stroke-width="2" fill="rgba(0,255,136,0.03)" stroke-linecap="round" stroke-linejoin="round"/><path class="v-path" d="M13 13L20 27M27 13L20 27" stroke="#00ff88" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><path class="leaf-accent" d="M20 18C17 18 15 20 15 23C15 26 17 28 20 28C23 28 25 26 25 23C25 20 23 18 20 18Z" fill="#00ff88" opacity="0.3"/></svg>Verdis</h3>
      </div>
      <p>The world's first fully green, carbon-negative blockchain ecosystem. Built with Substrate, powered by nature.</p>
    </div>
    <div class="verdis-footer-col">
      <h4>Ecosystem</h4>
      <a href="/">Home</a>
      <a href="/explorer/">Verdiscan</a>
      <a href="/dex/">DEX</a>
      <a href="/whitepaper/">Whitepaper</a>
      <a href="/wallet/">Wallet</a>
      <a href="/sale/">Sale</a>
      <a href="/tokenomics/">Tokenomics</a>
      <a href="/faucet/">Faucet</a>
    </div>
    <div class="verdis-footer-col">
      <h4>Resources</h4>
      <a href="/validators/">Validators</a>
      <a href="/eco/">Eco Metrics</a>
      <a href="/referral/">Referral</a>
      <a href="/incentives/">Incentives</a>
      <a href="/contact/">Contact</a>
      <a href="/docs/">Docs</a>
      <a href="/api/">API</a>
    </div>
    <div class="verdis-footer-col">
      <h4>Community</h4>
      <a href="https://github.com/Protremix/Verdischain-" target="_blank">GitHub</a>
      <a href="/blog/">Blog</a>
      <a href="/developers/">Developers</a>
      <a href="/download/">Download</a>
    </div>
  </div>"""

if old_footer in c:
    c = c.replace(old_footer, new_footer)
    print("FIXED: footer links in verdis.js")
else:
    print("WARN: Could not find old footer in verdis.js")

with open("/var/www/verdiscan/js/verdis.js", "w") as f:
    f.write(c)
print("Done - verdis.js updated")
