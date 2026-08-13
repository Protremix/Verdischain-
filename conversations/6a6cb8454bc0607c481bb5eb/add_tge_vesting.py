#!/usr/bin/env python3
"""
Add a TGE-relative vesting & cliff roadmap section to the whitepaper.
Timeline starts from Day 0 (TGE/sale day) and shows all unlock events.
"""

with open('/var/www/verdiscan/whitepaper/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# CSS for the TGE vesting roadmap
tge_css = """
/* TGE VESTING ROADMAP */
.tge-timeline{position:relative;padding:40px 0 20px;margin:24px 0}
.tge-axis{position:relative;height:4px;background:linear-gradient(90deg,#16a34a,#15803d,#22c55e,#4ade80,#86efac);border-radius:2px;margin:0 40px}
.tge-axis::before{content:'TGE DAY';position:absolute;left:-36px;top:-6px;font-size:10px;font-weight:700;color:#16a34a;font-family:'JetBrains Mono';white-space:nowrap}
.tge-axis::after{content:'YEAR 10';position:absolute;right:-40px;top:-6px;font-size:10px;font-weight:700;color:#15803d;font-family:'JetBrains Mono';white-space:nowrap}
.tge-marker{position:absolute;top:-30px;width:2px;height:64px;background:#16a34a;transform:translateX(-50%)}
.tge-marker-dot{position:absolute;top:-4px;left:-5px;width:12px;height:12px;border-radius:50%;background:#fff;border:2px solid #16a34a;z-index:2}
.tge-marker-label{position:absolute;top:-56px;left:50%;transform:translateX(-50%);font-size:10px;font-weight:700;color:#0f172a;white-space:nowrap;font-family:'Space Grotesk'}
.tge-marker-sub{position:absolute;top:36px;left:50%;transform:translateX(-50%);font-size:9px;color:#64748b;white-space:nowrap;text-align:center;line-height:1.3;width:120px}
.tge-marker.danger .tge-marker-dot{border-color:#ef4444}
.tge-marker.danger .tge-marker-label{color:#ef4444}
.tge-marker.warning .tge-marker-dot{border-color:#f59e0b}
.tge-marker.warning .tge-marker-label{color:#d97706}
.tge-events{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;margin-top:48px}
.tge-event{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px;position:relative;overflow:hidden}
.tge-event::before{content:'';position:absolute;top:0;left:0;width:4px;height:100%;background:var(--accent)}
.tge-event.warning::before{background:#f59e0b}
.tge-event.danger::before{background:#ef4444}
.tge-event.success::before{background:#4ade80}
.tge-event-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.tge-event-when{font-family:'JetBrains Mono';font-size:11px;font-weight:700;color:var(--accent);background:var(--accent-glow);padding:3px 10px;border-radius:6px}
.tge-event.warning .tge-event-when{color:#d97706;background:rgba(245,158,11,0.1)}
.tge-event.danger .tge-event-when{color:#ef4444;background:rgba(239,68,68,0.08)}
.tge-event.success .tge-event-when{color:#16a34a;background:rgba(74,222,128,0.1)}
.tge-event-title{font-size:13px;font-weight:700;color:#0f172a;margin-bottom:4px}
.tge-event-desc{font-size:12px;color:var(--text-2);line-height:1.5}
.tge-event-amt{font-family:'JetBrains Mono';font-size:11px;color:var(--accent);font-weight:600;margin-top:6px;display:block}

/* VESTING TABLE */
.tge-table{width:100%;border-collapse:collapse;margin:16px 0;font-size:12px}
.tge-table th{text-align:left;padding:10px 14px;font-size:10px;text-transform:uppercase;letter-spacing:.5px;color:var(--text-3);background:var(--bg-1);border-bottom:2px solid var(--accent);font-weight:600}
.tge-table td{padding:10px 14px;border-bottom:1px solid var(--border);color:var(--text-2)}
.tge-table tr:last-child td{border-bottom:none}
.tge-table .mono{font-family:'JetBrains Mono';font-size:11px}
.tge-table .unlocked{color:#16a34a;font-weight:600}
.tge-table .locked{color:#ef4444;font-weight:600}
.tge-table .partial{color:#f59e0b;font-weight:600}

/* SUPPLY CURVE */
.supply-chart{display:grid;grid-template-columns:1fr;gap:8px;margin:16px 0}
.supply-row{display:flex;align-items:center;gap:12px;font-size:12px}
.supply-row .sr-when{width:80px;font-weight:600;color:var(--text-2);font-size:11px}
.supply-row .sr-bar{flex:1;height:24px;background:var(--bg-1);border-radius:6px;overflow:hidden;position:relative;border:1px solid var(--border)}
.supply-row .sr-fill{height:100%;background:linear-gradient(90deg,#16a34a,#22c55e);border-radius:6px;transition:width .6s}
.supply-row .sr-val{position:absolute;right:8px;top:50%;transform:translateY(-50%);font-family:'JetBrains Mono';font-size:10px;font-weight:700;color:#fff;text-shadow:0 1px 3px rgba(0,0,0,.3)}
.supply-row .sr-pct{width:48px;text-align:right;font-family:'JetBrains Mono';font-size:11px;font-weight:600;color:var(--accent)}

@media(max-width:768px){.tge-axis{margin:0 20px}.tge-marker-sub{display:none}.tge-events{grid-template-columns:1fr}.supply-row .sr-when{width:64px;font-size:10px}}
"""

# Insert CSS before </style>
html = html.replace('</style>', tge_css + '\n</style>')

# Create the TGE vesting roadmap HTML section
# Insert it after the vesting schedule section (section 3) and before the staking calculator
vesting_section = """
<section id="tge-vesting" class="section-block reveal">
<div class="section-header">
<span class="section-tag">From TGE Day</span>
<h2 class="section-title">3.1. Vesting &amp; Cliff Roadmap (From Token Sale Day)</h2>
<p class="section-desc">Every unlock event measured from Day 0 (TGE &mdash; Token Generation Event). This is the day tokens are sold and released to the market. All cliffs, vesting periods, and circulating supply milestones are calculated from this date.</p>
</div>

<!-- TGE TIMELINE -->
<div class="tge-timeline">
<div class="tge-axis">
<!-- Day 0 -->
<div class="tge-marker" style="left:0%"><div class="tge-marker-dot"></div><span class="tge-marker-label">Day 0</span><div class="tge-marker-sub">TGE<br>8B circulating<br>(8%)</div></div>
<!-- Month 3 -->
<div class="tge-marker warning" style="left:8%"><div class="tge-marker-dot"></div><span class="tge-marker-label">Month 3</span><div class="tge-marker-sub">Community<br>cliff ends</div></div>
<!-- Month 6 -->
<div class="tge-marker warning" style="left:15%"><div class="tge-marker-dot"></div><span class="tge-marker-label">Month 6</span><div class="tge-marker-sub">Presale<br>cliff ends</div></div>
<!-- Month 12 -->
<div class="tge-marker" style="left:25%"><div class="tge-marker-dot"></div><span class="tge-marker-label">Month 12</span><div class="tge-marker-sub">Seed + Team<br>cliff ends</div></div>
<!-- Month 24 -->
<div class="tge-marker success" style="left:45%"><div class="tge-marker-dot"></div><span class="tge-marker-label">Month 24</span><div class="tge-marker-sub">Seed fully<br>vested</div></div>
<!-- Month 36 -->
<div class="tge-marker success" style="left:65%"><div class="tge-marker-dot"></div><span class="tge-marker-label">Month 36</span><div class="tge-marker-sub">Presale fully<br>vested</div></div>
<!-- Month 48 -->
<div class="tge-marker success" style="left:80%"><div class="tge-marker-dot"></div><span class="tge-marker-label">Month 48</span><div class="tge-marker-sub">Team fully<br>vested</div></div>
<!-- Year 10 -->
<div class="tge-marker success" style="left:100%"><div class="tge-marker-dot"></div><span class="tge-marker-label">Year 10</span><div class="tge-marker-sub">Full unlock<br>95B+ circulating</div></div>
</div>
</div>

<!-- EVENT CARDS -->
<div class="tge-events">
<div class="tge-event">
<div class="tge-event-head"><span class="tge-event-title">TGE &mdash; Token Generation Event</span><span class="tge-event-when">Day 0</span></div>
<div class="tge-event-desc">Initial circulating supply: <strong>8B VRDX (8%)</strong>. Liquidity pools seeded. DEX active. Staking rewards begin. All investor tokens are <strong>locked</strong> &mdash; 0% unlocked.</div>
<span class="tge-event-amt">Circulating: 8,000,000,000 VRDX</span>
</div>
<div class="tge-event warning">
<div class="tge-event-head"><span class="tge-event-title">Community Round Cliff Ends</span><span class="tge-event-when">Month 3</span></div>
<div class="tge-event-desc">Community round (1B at $0.003) 3-month cliff completes. <strong>20% TGE release</strong> already unlocked. Linear vesting of remaining 800M begins at <span class="mono">53.3M/month</span> over 15 months.</div>
<span class="tge-event-amt">+200M unlocked &middot; 53.3M/month ongoing</span>
</div>
<div class="tge-event warning">
<div class="tge-event-head"><span class="tge-event-title">Presale Cliff Ends</span><span class="tge-event-when">Month 6</span></div>
<div class="tge-event-desc">Presale round (2B at $0.004) 6-month cliff completes. <strong>25% TGE release</strong> already unlocked. Linear vesting of remaining 1.5B begins at <span class="mono">250M/month</span> over 6 months.</div>
<span class="tge-event-amt">+500M unlocked &middot; 250M/month ongoing</span>
</div>
<div class="tge-event">
<div class="tge-event-head"><span class="tge-event-title">Seed &amp; Team Cliff Ends</span><span class="tge-event-when">Month 12</span></div>
<div class="tge-event-desc">Seed/Private (3B) and Team (5B) 12-month cliffs complete. <strong>0% was unlocked at TGE</strong>. Linear vesting begins: Seed at <span class="mono">125M/month</span> over 24 months. Team at <span class="mono">138.9M/month</span> over 36 months.</div>
<span class="tge-event-amt">Seed: 125M/month &middot; Team: 138.9M/month</span>
</div>
<div class="tge-event success">
<div class="tge-event-head"><span class="tge-event-title">Seed/Private Fully Vested</span><span class="tge-event-when">Month 36</span></div>
<div class="tge-event-desc">All 3B Seed/Private tokens fully unlocked. 24 months of linear vesting complete. No more investor tokens locked from this allocation.</div>
<span class="tge-event-amt">3,000,000,000 fully unlocked</span>
</div>
<div class="tge-event success">
<div class="tge-event-head"><span class="tge-event-title">Team Fully Vested</span><span class="tge-event-when">Month 48</span></div>
<div class="tge-event-desc">All 5B Team &amp; Advisor tokens fully unlocked. 36 months of linear vesting complete. All investor and team tokens now circulating.</div>
<span class="tge-event-amt">5,000,000,000 fully unlocked</span>
</div>
<div class="tge-event success">
<div class="tge-event-head"><span class="tge-event-title">Full Ecosystem Unlock</span><span class="tge-event-when">Year 10</span></div>
<div class="tge-event-desc">Ecosystem (25B) and Staking (20B) fully released. 10-year emission schedule complete. <strong>95B+ VRDX circulating</strong> (95%+ of total supply). Remaining in DAO treasury for perpetual governance.</div>
<span class="tge-event-amt">95,000,000,000+ circulating</span>
</div>
</div>

<!-- VESTING TABLE -->
<h3 style="font-family:'Space Grotesk';font-size:14px;font-weight:700;color:var(--text);margin:24px 0 8px">Unlock Schedule (From TGE Day)</h3>
<table class="tge-table">
<thead><tr><th>Time from TGE</th><th>Event</th><th>Unlocked</th><th>Circulating Supply</th><th>% of 100B</th></tr></thead>
<tbody>
<tr><td><strong>Day 0</strong></td><td>TGE &mdash; tokens sold, market release</td><td class="mono unlocked">8B</td><td class="mono">8,000,000,000</td><td class="mono">8.0%</td></tr>
<tr><td>Month 1-3</td><td>Community 20% TGE release active</td><td class="mono partial">+200M</td><td class="mono">8,200,000,000</td><td class="mono">8.2%</td></tr>
<tr><td><strong>Month 3</strong></td><td>Community cliff ends &mdash; linear vesting begins</td><td class="mono partial">+53.3M/mo</td><td class="mono">~8,360,000,000</td><td class="mono">~8.4%</td></tr>
<tr><td><strong>Month 6</strong></td><td>Presale cliff ends &mdash; linear vesting begins</td><td class="mono partial">+250M/mo</td><td class="mono">~9,500,000,000</td><td class="mono">~9.5%</td></tr>
<tr><td>Month 6-12</td><td>Community + Presale vesting ongoing</td><td class="mono partial">+303M/mo</td><td class="mono">~11,300,000,000</td><td class="mono">~11.3%</td></tr>
<tr><td><strong>Month 12</strong></td><td>Seed + Team cliff ends &mdash; all vesting active</td><td class="mono partial">+263.9M/mo</td><td class="mono">~11,500,000,000</td><td class="mono">~11.5%</td></tr>
<tr><td>Month 12-24</td><td>All categories vesting simultaneously</td><td class="mono partial">~570M/mo</td><td class="mono">~18,300,000,000</td><td class="mono">~18.3%</td></tr>
<tr><td><strong>Month 24</strong></td><td>Community + Presale fully vested</td><td class="mono partial">~263.9M/mo</td><td class="mono">~24,300,000,000</td><td class="mono">~24.3%</td></tr>
<tr><td>Month 24-36</td><td>Seed + Team + Ecosystem vesting</td><td class="mono partial">~400M/mo</td><td class="mono">~36,300,000,000</td><td class="mono">~36.3%</td></tr>
<tr><td><strong>Month 36</strong></td><td>Seed/Private fully vested</td><td class="mono partial">~138.9M/mo</td><td class="mono">~39,300,000,000</td><td class="mono">~39.3%</td></tr>
<tr><td>Month 36-48</td><td>Team + Ecosystem vesting</td><td class="mono partial">~280M/mo</td><td class="mono">~52,900,000,000</td><td class="mono">~52.9%</td></tr>
<tr><td><strong>Month 48</strong></td><td>Team fully vested &mdash; all investors unlocked</td><td class="mono partial">~140M/mo</td><td class="mono">~56,900,000,000</td><td class="mono">~56.9%</td></tr>
<tr><td>Year 5-10</td><td>Ecosystem + Staking emission</td><td class="mono partial">~2B/yr</td><td class="mono">~75,000,000,000</td><td class="mono">~75.0%</td></tr>
<tr><td><strong>Year 10</strong></td><td>Full unlock complete</td><td class="mono unlocked">95B+</td><td class="mono">~95,000,000,000</td><td class="mono">~95.0%</td></tr>
</tbody>
</table>

<!-- CIRCULATING SUPPLY CURVE -->
<h3 style="font-family:'Space Grotesk';font-size:14px;font-weight:700;color:var(--text);margin:24px 0 8px">Circulating Supply Growth (From TGE Day)</h3>
<div class="supply-chart">
<div class="supply-row"><span class="sr-when">Day 0</span><div class="sr-bar"><div class="sr-fill" style="width:8%"><span class="sr-val">8B</span></div></div><span class="sr-pct">8%</span></div>
<div class="supply-row"><span class="sr-when">Month 3</span><div class="sr-bar"><div class="sr-fill" style="width:8.4%"><span class="sr-val">8.4B</span></div></div><span class="sr-pct">8.4%</span></div>
<div class="supply-row"><span class="sr-when">Month 6</span><div class="sr-bar"><div class="sr-fill" style="width:9.5%"><span class="sr-val">9.5B</span></div></div><span class="sr-pct">9.5%</span></div>
<div class="supply-row"><span class="sr-when">Month 12</span><div class="sr-bar"><div class="sr-fill" style="width:11.5%"><span class="sr-val">11.5B</span></div></div><span class="sr-pct">11.5%</span></div>
<div class="supply-row"><span class="sr-when">Month 18</span><div class="sr-bar"><div class="sr-fill" style="width:15%"><span class="sr-val">~15B</span></div></div><span class="sr-pct">15%</span></div>
<div class="supply-row"><span class="sr-when">Month 24</span><div class="sr-bar"><div class="sr-fill" style="width:24%"><span class="sr-val">~24B</span></div></div><span class="sr-pct">24%</span></div>
<div class="supply-row"><span class="sr-when">Month 36</span><div class="sr-bar"><div class="sr-fill" style="width:39%"><span class="sr-val">~39B</span></div></div><span class="sr-pct">39%</span></div>
<div class="supply-row"><span class="sr-when">Month 48</span><div class="sr-bar"><div class="sr-fill" style="width:57%"><span class="sr-val">~57B</span></div></div><span class="sr-pct">57%</span></div>
<div class="supply-row"><span class="sr-when">Year 5</span><div class="sr-bar"><div class="sr-fill" style="width:65%"><span class="sr-val">~65B</span></div></div><span class="sr-pct">65%</span></div>
<div class="supply-row"><span class="sr-when">Year 7</span><div class="sr-bar"><div class="sr-fill" style="width:80%"><span class="sr-val">~80B</span></div></div><span class="sr-pct">80%</span></div>
<div class="supply-row"><span class="sr-when">Year 10</span><div class="sr-bar"><div class="sr-fill" style="width:95%"><span class="sr-val">~95B</span></div></div><span class="sr-pct">95%</span></div>
</div>

<div class="card-panel" style="background:var(--accent-glow);border:1px solid var(--accent);border-radius:var(--radius);padding:16px 20px;margin:16px 0">
<div style="font-size:13px;font-weight:700;color:var(--accent);margin-bottom:6px">&#9888; Key Insight</div>
<div style="font-size:12px;color:var(--text-2);line-height:1.6">From TGE day, <strong>only 8% of tokens are circulating</strong>. Investor tokens are fully locked with 3-12 month cliffs. The first unlock event is at <strong>Month 3</strong> (Community round). The largest unlock wave starts at <strong>Month 12</strong> when Seed + Team cliffs end simultaneously. This design prevents dump pressure and ensures long-term price stability.</div>
</div>
</section>
"""

# Insert after the vesting schedule section, before the staking calculator
# Find the end of the vesting section (section 3) which ends right before section 4
# The staking calculator section starts with id="staking" or the next section-block
insert_marker = '<section id="staking"'
if insert_marker in html:
    html = html.replace(insert_marker, vesting_section + '\n' + insert_marker)
else:
    # Try to find the next section after vesting
    # Look for the calc-staking or section 4
    calc_marker = '<div class="calc-staking"'
    if calc_marker in html:
        html = html.replace(calc_marker, vesting_section + '\n' + calc_marker)
    else:
        # Fallback: insert after the vesting grid
        vesting_end = '</div>\n</section>'
        idx = html.find('vesting-grid')
        if idx > 0:
            # Find the next </section> after vesting-grid
            sec_end = html.find('</section>', idx)
            if sec_end > 0:
                insert_pos = sec_end + len('</section>')
                html = html[:insert_pos] + '\n' + vesting_section + html[insert_pos:]

# Write updated whitepaper
with open('/var/www/verdiscan/whitepaper/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('/opt/verdis-chain-rust/web/whitepaper/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Whitepaper updated: {len(html)} bytes')

# Verify
checks = [
    ('tge-vesting' in html, 'TGE vesting section added'),
    ('tge-timeline' in html, 'TGE timeline visual added'),
    ('tge-events' in html, 'TGE event cards added'),
    ('tge-table' in html, 'TGE unlock table added'),
    ('supply-chart' in html, 'Supply curve chart added'),
    ('Day 0' in html, 'Day 0 / TGE day marker present'),
    ('Month 3' in html, 'Month 3 cliff end present'),
    ('Month 6' in html, 'Month 6 cliff end present'),
    ('Month 12' in html, 'Month 12 cliff end present'),
    ('Year 10' in html, 'Year 10 full unlock present'),
    ('From TGE' in html or 'from TGE' in html, 'TGE-relative labeling present'),
    ('8B' in html, 'Initial 8B circulating'),
    ('95B' in html, 'Final 95B circulating'),
]
for ok, label in checks:
    print('OK' if ok else 'FAIL', ':', label)
