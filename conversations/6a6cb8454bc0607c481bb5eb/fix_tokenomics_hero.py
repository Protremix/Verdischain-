#!/usr/bin/env python3
"""Fix tokenomics hero section old references."""

with open('/opt/verdis-repo/dist/web/tokenomics/index.html', 'r') as f:
    content = f.read()

# Fix hero description
content = content.replace(
    'A balanced 100-billion supply distribution engineered for long-term decentralization, ecosystem liquidity, and sustainable validator incentives. 12B allocated to investors across 4 IDO phases.',
    'A balanced 100-billion supply distribution engineered for long-term utility, network security, and sustainable ecosystem growth. 4 fundraising rounds: Seed, Community, Presale, and TGE. Total raised: $18M. FDV: $500M.'
)

# Fix floating card - replace old phases with new rounds
old_card = '''      <div class="price-big" style="font-size:14px">12B VRDX (12%)</div>
      <div class="mini-row" style="margin-top:8px"><span class="l">Seed (3B)</span><span class="v">$4.5M</span></div>
      <div class="mini-row"><span class="l">Phase 2 (Private)</span><span class="v">3B</span></div>
      <div class="mini-row"><span class="l">Presale (2B)</span><span class="v">$8M</span></div>
      <div class="mini-row"><span class="l">Phase 4 (Public)</span><span class="v">2B</span></div>'''

new_card = '''      <div class="price-big" style="font-size:14px">$18M Total Raised</div>
      <div class="mini-row" style="margin-top:8px"><span class="l">Seed (3B)</span><span class="v">$4.5M</span></div>
      <div class="mini-row"><span class="l">Community (1B)</span><span class="v">$3M</span></div>
      <div class="mini-row"><span class="l">Presale (2B)</span><span class="v">$8M</span></div>
      <div class="mini-row"><span class="l">TGE/IDO (0.5B)</span><span class="v">$2.5M</span></div>'''

content = content.replace(old_card, new_card)

# Fix Hard Cap -> FDV at TGE
content = content.replace(
    '<div class="mini-row"><span class="l">Hard Cap</span><span class="v">$17.5M</span></div>',
    '<div class="mini-row"><span class="l">FDV at TGE</span><span class="v">$500M</span></div>'
)

# Fix the floating card label
content = content.replace(
    '<div style="font-size:12px;color:var(--text-3);margin-bottom:6px">Total Raised</div>',
    '<div style="font-size:12px;color:var(--text-3);margin-bottom:6px">Fundraising Rounds</div>'
)

with open('/opt/verdis-repo/dist/web/tokenomics/index.html', 'w') as f:
    f.write(content)
print("Tokenomics hero section fixed!")
