#!/usr/bin/env python3
"""
Add founder Rojs Gordons to both whitepaper.html and team.html
"""

FOUNDER_IMAGE = "https://media.base44.com/images/public/6a6cb8410d1dcb778817254f/9c2be2776_generated_image.png"

FOUNDER_CARD = '''<!-- Team Member 0: Founder & CEO -->
<div style="display:flex;gap:20px;margin:20px 0;padding:20px;background:rgba(0,255,136,0.06);border:1px solid rgba(0,255,136,0.2);border-radius:12px;flex-wrap:wrap;align-items:flex-start;">
<div style="flex-shrink:0;width:100px;height:100px;border-radius:50%;overflow:hidden;border:2px solid rgba(0,255,136,0.4);">
<img src="''' + FOUNDER_IMAGE + '''" alt="Rojs Gordons — Founder & CEO" style="width:100%;height:100%;object-fit:cover;">
</div>
<div style="flex:1;min-width:250px;">
<div style="font-size:1.15rem;font-weight:700;color:#00ff88;">Rojs Gordons</div>
<div style="font-size:0.9rem;color:#e8e8e8;margin:2px 0;font-weight:600;">Founder &amp; CEO</div>
<div style="font-size:0.85rem;color:#00ff88;margin:4px 0;">Blockchain Architecture &middot; Fintech &middot; Protocol Design</div>
<p class="tech-para" style="margin:8px 0;"><strong>Experience:</strong> 15+ years in software engineering and technology leadership. Founder and CEO of <strong>Protremix</strong>, a software development company specializing in blockchain infrastructure, fintech platforms, and scalable distributed systems. Led the architecture and delivery of <strong>Anerium</strong>, a high-performance fintech platform, along with multiple production-grade financial systems serving thousands of users. Deep expertise in Layer-1 blockchain design, consensus mechanisms (DPoS/PoS), cryptographic primitives (secp256k1, Keccak256), and EVM-compatible virtual machine implementation.</p>
<p class="tech-para" style="margin:6px 0;"><strong>Background:</strong> Under the Protremix banner, Rojs has overseen the full lifecycle of enterprise fintech products — from protocol-level architecture to mobile wallet deployment and exchange integration. His work on Anerium demonstrated novel approaches to high-throughput transaction processing and secure multi-signature asset management. With Verdis, he brings this fintech and protocol engineering experience to build the world&rsquo;s first fully green, carbon-negative blockchain ecosystem — combining production-grade financial infrastructure with on-chain ecological impact tracking.</p>
<p class="tech-para" style="margin:6px 0;"><strong>Technologies:</strong> Node.js, TypeScript, Rust, Solidity, React, Express.js, PostgreSQL, Redis, Docker, Nginx, WebSocket, @noble/secp256k1, @noble/hashes</p>
<p class="tech-para" style="margin:6px 0;"><strong>Notable Projects:</strong> Anerium (fintech platform), Verdis Chain (Layer-1 blockchain), Protremix (software development company), multiple DeFi and payment systems</p>
<div style="display:flex;gap:12px;margin-top:10px;">
<a href="https://github.com/verdischain" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:#e8e8e8;padding:6px 14px;border-radius:6px;font-size:0.8rem;text-decoration:none;">
<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>GitHub</a>
<a href="https://protremix.com" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:#e8e8e8;padding:6px 14px;border-radius:6px;font-size:0.8rem;text-decoration:none;">Protremix</a>
</div>
</div>
</div>'''

# === 1. Update whitepaper.html ===
with open("/opt/verdis/app/dist/web/whitepaper.html", "r") as f:
    html = f.read()

# Find the "25.1 — Core Team" subsection and insert founder card right after it
# The first team member card starts with "<!-- Team Member 1: Lead Architect"
insert_marker = '<!-- Team Member 1: Lead Architect'
insert_idx = html.find(insert_marker)

if insert_idx != -1:
    html = html[:insert_idx] + FOUNDER_CARD + '\n' + html[insert_idx:]
    print("✅ Added founder card to whitepaper.html (before Lead Architect)")
else:
    print("⚠️ Could not find Team Member 1 marker in whitepaper")

# Also update the team intro paragraph to mention the founder
old_intro = "Verdis t(ru)inetwith Verdis Research Foundation"
if old_intro in html:
    new_intro = "Verdis was founded by Rojs Gordons, technology entrepreneur and CEO of Protremix, alongside the Verdis Research Foundation"
    html = html.replace(old_intro, new_intro)
    print("✅ Updated team intro paragraph with founder mention")

with open("/opt/verdis/app/dist/web/whitepaper.html", "w") as f:
    f.write(html)
print(f"Whitepaper size: {len(html):,} chars")

# === 2. Update team.html ===
with open("/opt/verdis/app/dist/web/team.html", "r") as f:
    team_html = f.read()

# Find where to insert the founder in team.html
# Look for the first team member card
team_markers = [
    "<!-- Team Member 1",
    "<!-- Team Member",
    'class="team-card',
    'class="team-member',
    'class="member-card',
]

inserted = False
for marker in team_markers:
    idx = team_html.find(marker)
    if idx != -1:
        team_html = team_html[:idx] + FOUNDER_CARD + '\n' + team_html[idx:]
        print(f"✅ Added founder card to team.html (before '{marker}')")
        inserted = True
        break

if not inserted:
    # Try to find any team grid or container
    for container in ['class="team-grid', 'class="team-container', 'class="team-list', 'class="cards-grid']:
        idx = team_html.find(container)
        if idx != -1:
            # Find the closing > of this element
            close = team_html.find('>', idx)
            if close != -1:
                team_html = team_html[:close+1] + '\n' + FOUNDER_CARD + team_html[close+1:]
                print(f"✅ Added founder card to team.html (after '{container}')")
                inserted = True
                break

if not inserted:
    print("⚠️ Could not find insertion point in team.html")
    # Print first 2000 chars to understand structure
    print("Team.html structure (first 2000 chars):")
    print(team_html[:2000])

if inserted:
    with open("/opt/verdis/app/dist/web/team.html", "w") as f:
        f.write(team_html)
    print(f"Team page size: {len(team_html):,} chars")

print("\n=== Done! ===")
