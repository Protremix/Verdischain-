#!/usr/bin/env python3
"""Fix Referral page: zero out all fake data since IDO hasn't started."""

with open("/var/www/verdiscan/referral/index.html") as f:
    html = f.read()

# 1. Hero stats: Total Paid $4.2M → $0
html = html.replace(
    '<div class="hero-stat"><div class="label">Total Paid</div><div class="value">$4.2M</div></div>',
    '<div class="hero-stat"><div class="label">Total Paid</div><div class="value">$0</div></div>'
)

# 2. Float card: Your Earnings $12,450 → $0
html = html.replace(
    '<div class="price-big">$12,450</div>',
    '<div class="price-big">$0</div>'
)
html = html.replace(
    '+ $2,340 this week',
    'No earnings yet — IDO starting soon'
)

# 3. Float card: Total Referrals 847 → 0
html = html.replace(
    '<span class="l">Total Referrals</span><span class="v">847</span>',
    '<span class="l">Total Referrals</span><span class="v">0</span>'
)

# 4. Float card: Conversion Rate 23.4% → 0%
html = html.replace(
    '<span class="l">Conversion Rate</span><span class="v">23.4%</span>',
    '<span class="l">Conversion Rate</span><span class="v">0%</span>'
)

# 5. Float card: Your Rank #7 → —
html = html.replace(
    'font-weight:700;color:var(--accent)">#7</div>',
    'font-weight:700;color:var(--accent)">—</div>'
)

# 6. Float card: of 3,847 affiliates → of 0 affiliates
html = html.replace(
    'of 3,847 affiliates',
    'of 0 affiliates'
)

# 7. Dashboard: Total Referrals 847, +24 this week → 0, No referrals yet
html = html.replace(
    '<div class="value">847</div><div class="sub">+24 this week</div>',
    '<div class="value">0</div><div class="sub">No referrals yet</div>'
)

# 8. Dashboard: Total Earnings $12,450, 498,000 VRDX → $0, 0 VRDX
html = html.replace(
    '<div class="value">$12,450</div><div class="sub">498,000 VRDX</div>',
    '<div class="value">$0</div><div class="sub">0 VRDX</div>'
)

# 9. Dashboard: Conversion Rate 23.4%, Industry avg: 8% → 0%, No data yet
html = html.replace(
    '<div class="value">23.4%</div><div class="sub">Industry avg: 8%</div>',
    '<div class="value">0%</div><div class="sub">No data yet</div>'
)

# 10. Dashboard: Active This Week 38, Friends buying now → 0, No activity yet
html = html.replace(
    '<div class="value">38</div><div class="sub">Friends buying now</div>',
    '<div class="value">0</div><div class="sub">No activity yet</div>'
)

# 11. Leaderboard: replace fake entries with empty state
old_leader_js = """function renderLeaderboard(){const leaders=[{rank:1,addr:'0xDeFi...8aF2',refs:1247,vol:'$2.8M',earn:'1.12M',badge:'\U0001f3c6 Diamond'},{rank:2,addr:'0xNoCo...3bC9',refs:982,vol:'$2.1M',earn:'840K',badge:'\U0001f947 Platinum'},{rank:3,addr:'0xStak...9fE1',refs:756,vol:'$1.6M',earn:'640K',badge:'\U0001f948 Gold'},{rank:4,addr:'0xWhal...1dA4',refs:534,vol:'$1.2M',earn:'480K',badge:'\U0001f949 Silver'},{rank:5,addr:'0xCryp...7eF0',refs:412,vol:'$890K',earn:'356K',badge:'\u2b50 Pro'},{rank:6,addr:'0xBloc...2cD5',refs:298,vol:'$650K',earn:'260K',badge:'\u2b50 Pro'},{rank:7,addr:'0xYouR...ddress',refs:847,vol:'$1.9M',earn:'498K',badge:'\u2b50 Pro'},{rank:8,addr:'0xNodE...8aB3',refs:234,vol:'$520K',earn:'208K',badge:'\u2b50 Pro'},{rank:9,addr:'0xGree...5fC7',refs:187,vol:'$410K',earn:'164K',badge:'\u2b50 Active'},{rank:10,addr:'0xEcoW...1eD9',refs:142,vol:'$310K',earn:'124K',badge:'\u2b50 Active'}];const html=leaders.map(l=>`<tr><td><span class="rank-badge rank-${l.rank<=3?l.rank:''}">${l.rank}</span></td><td class="mono" style="font-size:13px">${l.addr}</td><td>${l.refs}</td><td class="mono">${l.vol}</td><td class="mono" style="color:var(--accent)">${l.earn}</td><td>${l.badge}</td></tr>`).join('');document.getElementById('leaderbody').innerHTML=html}"""

new_leader_js = """function renderLeaderboard(){document.getElementById('leaderbody').innerHTML='<tr><td colspan="6" style="text-align:center;padding:48px 20px;color:var(--text-3);font-size:14px">No affiliates yet \u2014 be the first to share your referral link when the IDO goes live!</td></tr>'}"""

html = html.replace(old_leader_js, new_leader_js)

# 12. FAQ: "Top affiliates have earned over $500,000 in VRDX tokens" → changed
html = html.replace(
    "No. You can refer as many people as you want. The more referrals, the more you earn. Top affiliates have earned over $500,000 in VRDX tokens.",
    "No. You can refer as many people as you want. The more referrals, the more you earn. Start sharing your link early to maximize your earnings when the IDO goes live."
)

# 13. FAQ: "Your dashboard shows total referrals, conversion rate, earnings breakdown by tier, and weekly activity charts. All in real-time."
html = html.replace(
    "Yes. Your dashboard shows total referrals, conversion rate, earnings breakdown by tier, and weekly activity charts. All in real-time.",
    "Yes. Your dashboard will show total referrals, conversion rate, earnings breakdown by tier, and weekly activity charts. All updated in real-time once the IDO begins."
)

# 14. Referral link input value - keep the link, it's just a demo placeholder

with open("/var/www/verdiscan/referral/index.html", "w") as f:
    f.write(html)

# Verify
checks = [
    ("Total Paid</div><div class=\"value\">$0", "total paid zeroed"),
    ('price-big">$0', "earnings zeroed"),
    ("No earnings yet", "earnings text"),
    ('v">0</span>\n</div>\n<div class="mini-row"><span class="l">Conversion Rate', "referrals zeroed"),
    ("of 0 affiliates", "affiliates zeroed"),
    ("No affiliates yet", "leaderboard empty"),
    ("$0</div><div class=\"sub\">0 VRDX", "dashboard earnings zeroed"),
    ("Start sharing your link early", "FAQ fixed"),
]
for text, label in checks:
    if text in html:
        print(f"  \u2713 {label}")
    else:
        print(f"  \u2717 {label}: NOT FOUND")

print("Referral page fixed")
