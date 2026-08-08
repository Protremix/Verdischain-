#!/usr/bin/env python3
"""Create cookie policy, security page, and professional footer for all Verdis Chain pages."""

import os
import re

WEB_ROOT = "/var/www/verdiscan"

FOOTER_HTML = '''<footer class="footer">
<div class="footer-inner">
<div class="footer-brand">
<h3>VERDIS CHAIN</h3>
<p>The world's first green blockchain with native DPoS consensus, AMM DEX, and carbon credit tracking. Built on Substrate.</p>
<div class="footer-social">
<a href="https://github.com/Protremix/Verdischain-" target="_blank" aria-label="GitHub"><svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.385.6.113.82-.26.82-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.5 11.5 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.218.694.825.576C20.565 21.795 24 17.298 24 12 24 5.37 18.627 0 12 0z"/></svg></a>
<a href="/contact/" aria-label="Contact"><svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M24 4l-12 7-12-7v-2l12 7 12-7v2zm0 2v14h-24v-14l12 7 12-7z"/></svg></a>
<a href="/status/" aria-label="Network Status"><svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg></a>
</div>
</div>
<div class="footer-col"><h4>Products</h4><a href="/explorer/">Verdiscan</a><a href="/dex/">DEX</a><a href="/wallet/">Web Wallet</a><a href="/faucet/">Faucet</a><a href="/sale/">Token Sale</a></div>
<div class="footer-col"><h4>Resources</h4><a href="/docs/">Documentation</a><a href="/whitepaper/">Whitepaper</a><a href="/tokenomics/">Tokenomics</a><a href="/api/">API Reference</a><a href="https://github.com/Protremix/Verdischain-" target="_blank">GitHub</a></div>
<div class="footer-col"><h4>Community</h4><a href="/validators/">Validators</a><a href="/eco/">Eco Metrics</a><a href="/referral/">Referral Program</a><a href="/incentives/">Validator Incentives</a><a href="/contact/">Contact</a></div>
<div class="footer-col"><h4>Legal</h4><a href="/terms/">Terms of Service</a><a href="/privacy/">Privacy Policy</a><a href="/cookies/">Cookie Policy</a><a href="/security/">Security</a><a href="/disclaimer/">Disclaimer</a></div>
</div>
<div class="footer-bottom"><span>&copy; 2026 Verdis Chain &middot; Protremix &middot; Open-source under MIT License</span><span><a href="/privacy/" style="color:#64748b;text-decoration:none">GDPR Compliant</a> &middot; <a href="/security/" style="color:#64748b;text-decoration:none">Security</a></span></div>
</footer>'''

FOOTER_CSS = ".footer{background:#0f172a;color:#94a3b8;padding:48px 24px 24px}.footer-inner{max-width:1280px;margin:0 auto;display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;gap:32px}.footer-brand h3{color:#fff;font-family:var(--font-head),sans-serif;font-size:18px;margin-bottom:12px;font-weight:700}.footer-brand p{font-size:14px;max-width:280px;line-height:1.6;color:#94a3b8}.footer-social{display:flex;gap:8px;margin-top:16px}.footer-social a{width:36px;height:36px;border-radius:8px;background:rgba(255,255,255,.05);display:flex;align-items:center;justify-content:center;transition:.2s;color:#94a3b8}.footer-social a:hover{background:rgba(22,163,74,.15);color:#16a34a}.footer-col h4{color:#fff;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;margin-bottom:12px}.footer-col a{display:block;font-size:14px;padding:5px 0;color:#94a3b8;transition:.2s;text-decoration:none}.footer-col a:hover{color:#16a34a}.footer-bottom{max-width:1280px;margin:32px auto 0;padding-top:20px;border-top:1px solid #1e293b;display:flex;justify-content:space-between;font-size:13px;color:#64748b}.footer-bottom a{text-decoration:none;color:#64748b}.footer-bottom a:hover{color:#16a34a}@media(max-width:768px){.footer-inner{grid-template-columns:1fr 1fr;gap:24px}.footer-bottom{flex-direction:column;gap:8px;text-align:center}}@media(max-width:480px){.footer-inner{grid-template-columns:1fr}}"

# Old footer patterns
OLD_FOOTER_PATTERN = re.compile(
    r'<footer class="footer">\s*<div class="footer-links">.*?</div>\s*<div class="footer-copy">.*?</div>\s*</footer>',
    re.DOTALL
)

OLD_FOOTER_PATTERN_2 = re.compile(
    r'<footer class="footer">\s*<div class="footer-inner">.*?</div>\s*<div class="footer-bottom">.*?</div>\s*<div class="footer-copy">.*?</div>\s*</footer>',
    re.DOTALL
)

PAGES = [
    "index", "explorer", "dex", "wallet", "sale", "tokenomics",
    "faucet", "validators", "eco", "referral", "incentives",
    "contact", "api", "docs", "whitepaper", "terms", "privacy"
]

updated = []
failed = []

for page in PAGES:
    path = os.path.join(WEB_ROOT, page, "index.html")
    if not os.path.exists(path):
        failed.append(f"{page}: file not found")
        continue

    content = open(path, "r").read()
    original = content

    new_content = OLD_FOOTER_PATTERN.sub(FOOTER_HTML, content)
    if new_content == content:
        new_content = OLD_FOOTER_PATTERN_2.sub(FOOTER_HTML, content)
    if new_content == content:
        generic_match = re.search(r'<footer[^>]*>.*?</footer>', content, re.DOTALL)
        if generic_match:
            new_content = content[:generic_match.start()] + FOOTER_HTML + content[generic_match.end():]
        else:
            failed.append(f"{page}: no footer found")
            continue

    # Add footer CSS if not present
    if "footer-social" not in new_content and "</style>" in new_content:
        new_content = new_content.replace("</style>", FOOTER_CSS + "\n</style>", 1)

    if new_content != original:
        open(path, "w").write(new_content)
        updated.append(page)
    else:
        failed.append(f"{page}: no changes needed")

print("=== FOOTER UPDATES ===")
for p in updated:
    print(f"  OK: {p}")
print(f"Total updated: {len(updated)}")

if failed:
    print("\n=== FAILED ===")
    for f in failed:
        print(f"  SKIP: {f}")
