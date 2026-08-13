with open('/tmp/whitepaper_correct.html', 'r') as f:
    html = f.read()

# Find the team-grid block
team_start = html.find('<div class="team-grid">')
if team_start == -1:
    print("ERROR: team-grid not found")
    exit(1)

# Find the matching closing div
depth = 0
i = team_start
while i < len(html):
    if html[i:i+5] == '<div ':
        depth += 1
    elif html[i:i+6] == '</div>':
        depth -= 1
        if depth == 0:
            team_end = i + 6
            break
    i += 1

# Build the 6 team cards using existing CSS classes
new_team = """<div class="team-grid">
<div class="team-card"><div class="team-avatar">DJ</div><div class="team-name">Dorian Jean</div><div class="team-role">CEO &amp; Founder</div><div class="team-bio">CEO of Verdischain and owner of Shilat18 Ltd, specializing in recycling of eco-products. 10+ years in the eco-products and recycling industry with practical knowledge of sustainable technologies, circular-economy principles, and environmentally focused business development. Leads strategic direction, business development, partnerships, and ecosystem expansion.</div><div class="team-socials"><a href="#" class="team-social" aria-label="LinkedIn" title="LinkedIn"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M20.5 2h-17A1.5 1.5 0 002 3.5v17A1.5 1.5 0 003.5 22h17a1.5 1.5 0 001.5-1.5v-17A1.5 1.5 0 0020.5 2zM8 19H5v-9h3zM6.5 8.25A1.75 1.75 0 118.5 6.5a1.78 1.78 0 01-2 1.75zM19 19h-3v-4.74c0-1.42-.6-1.93-1.38-1.93A1.74 1.74 0 0013 14.19a.66.66 0 000 .14V19h-3v-9h2.9v1.3a3.11 3.11 0 012.7-1.4c1.55 0 3.36.86 3.36 3.66z"/></svg></a></div></div>
<div class="team-card"><div class="team-avatar" style="background:linear-gradient(135deg,#38bdf8,#a855f7)">MJ</div><div class="team-name">Mark Jamestown</div><div class="team-role">CTO / Lead Engineer</div><div class="team-bio">Responsible for blockchain architecture, Substrate runtime development, consensus, security, infrastructure, and core protocol development. Leads the technical development of the Verdischain Layer-1 architecture and the engineering direction of the blockchain protocol.</div><div class="team-socials"><a href="https://github.com/Protremix/Verdischain-" target="_blank" class="team-social" aria-label="GitHub" title="GitHub"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .3a12 12 0 00-3.8 23.4c.6.1.8-.3.8-.6v-2c-3.3.7-4-1.6-4-1.6-.6-1.4-1.4-1.8-1.4-1.8-1-.7.1-.7.1-.7 1.2.1 1.9 1.2 1.9 1.2 1 1.8 2.8 1.3 3.5 1 .1-.8.4-1.3.7-1.6-2.7-.3-5.5-1.3-5.5-6 0-1.3.5-2.4 1.2-3.2-.1-.3-.5-1.5.1-3.2 0 0 1-.3 3.3 1.2a11.5 11.5 0 016 0c2.3-1.5 3.3-1.2 3.3-1.2.6 1.7.2 2.9.1 3.2.8.8 1.2 1.9 1.2 3.2 0 4.6-2.8 5.7-5.5 6 .4.4.8 1.1.8 2.2v3.3c0 .3.2.7.8.6A12 12 0 0012 .3"/></svg></a></div></div>
<div class="team-card"><div class="team-avatar" style="background:linear-gradient(135deg,#fbbf24,#ef4444)">EJ</div><div class="team-name">Elizabeth Jefferson</div><div class="team-role">Head of Product</div><div class="team-bio">Responsible for product strategy, ecosystem development, wallet, explorer, and user experience. Oversees Verdischain user-facing products and ecosystem services, with a focus on creating accessible tools for users, developers, validators, and ecosystem participants.</div><div class="team-socials"><a href="#" class="team-social" aria-label="LinkedIn" title="LinkedIn"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M20.5 2h-17A1.5 1.5 0 002 3.5v17A1.5 1.5 0 003.5 22h17a1.5 1.5 0 001.5-1.5v-17A1.5 1.5 0 0020.5 2zM8 19H5v-9h3zM6.5 8.25A1.75 1.75 0 118.5 6.5a1.78 1.78 0 01-2 1.75zM19 19h-3v-4.74c0-1.42-.6-1.93-1.38-1.93A1.74 1.74 0 0013 14.19a.66.66 0 000 .14V19h-3v-9h2.9v1.3a3.11 3.11 0 012.7-1.4c1.55 0 3.36.86 3.36 3.66z"/></svg></a></div></div>
<div class="team-card"><div class="team-avatar">RG</div><div class="team-name">Rojs Gordons</div><div class="team-role">Co-Founder &amp; Marketing</div><div class="team-bio">Responsible for community growth, communications, marketing, and ecosystem partnerships. Leads community and communications strategy, focusing on ecosystem awareness, developer outreach, community development, strategic communications, and partnerships.</div><div class="team-socials"><a href="#" class="team-social" aria-label="LinkedIn" title="LinkedIn"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M20.5 2h-17A1.5 1.5 0 002 3.5v17A1.5 1.5 0 003.5 22h17a1.5 1.5 0 001.5-1.5v-17A1.5 1.5 0 0020.5 2zM8 19H5v-9h3zM6.5 8.25A1.75 1.75 0 118.5 6.5a1.78 1.78 0 01-2 1.75zM19 19h-3v-4.74c0-1.42-.6-1.93-1.38-1.93A1.74 1.74 0 0013 14.19a.66.66 0 000 .14V19h-3v-9h2.9v1.3a3.11 3.11 0 012.7-1.4c1.55 0 3.36.86 3.36 3.66z"/></svg></a><a href="https://github.com/Protremix" target="_blank" class="team-social" aria-label="GitHub" title="GitHub"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .3a12 12 0 00-3.8 23.4c.6.1.8-.3.8-.6v-2c-3.3.7-4-1.6-4-1.6-.6-1.4-1.4-1.8-1.4-1.8-1-.7.1-.7.1-.7 1.2.1 1.9 1.2 1.9 1.2 1 1.8 2.8 1.3 3.5 1 .1-.8.4-1.3.7-1.6-2.7-.3-5.5-1.3-5.5-6 0-1.3.5-2.4 1.2-3.2-.1-.3-.5-1.5.1-3.2 0 0 1-.3 3.3 1.2a11.5 11.5 0 016 0c2.3-1.5 3.3-1.2 3.3-1.2.6 1.7.2 2.9.1 3.2.8.8 1.2 1.9 1.2 3.2 0 4.6-2.8 5.7-5.5 6 .4.4.8 1.1.8 2.2v3.3c0 .3.2.7.8.6A12 12 0 0012 .3"/></svg></a></div></div>
<div class="team-card"><div class="team-avatar" style="background:linear-gradient(135deg,#a855f7,#6366f1)">MM</div><div class="team-name">María Dolores Márquez de Prado</div><div class="team-role">Legal Counsel</div><div class="team-bio">Advises Verdischain on corporate structure, blockchain regulatory matters, token-related legal considerations, and commercial agreements. Graduated in Law from the Complutense University of Madrid. Served as prosecutor in the Provincial Court of Guipuzcoa and the National Court for 17+ years. Appointed Prosecutor of the Supreme Court (1999-2007). Author of publications on criminal law.</div><div class="team-socials"><a href="#" class="team-social" aria-label="LinkedIn" title="LinkedIn"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M20.5 2h-17A1.5 1.5 0 002 3.5v17A1.5 1.5 0 003.5 22h17a1.5 1.5 0 001.5-1.5v-17A1.5 1.5 0 0020.5 2zM8 19H5v-9h3zM6.5 8.25A1.75 1.75 0 118.5 6.5a1.78 1.78 0 01-2 1.75zM19 19h-3v-4.74c0-1.42-.6-1.93-1.38-1.93A1.74 1.74 0 0013 14.19a.66.66 0 000 .14V19h-3v-9h2.9v1.3a3.11 3.11 0 012.7-1.4c1.55 0 3.36.86 3.36 3.66z"/></svg></a></div></div>
<div class="team-card"><div class="team-avatar" style="background:linear-gradient(135deg,#0ea5e9,#6366f1)">IM</div><div class="team-name">Ignacio Martínez-Arrieta</div><div class="team-role">Legal &amp; Compliance</div><div class="team-bio">Member of the Madrid Bar Association since 2010. Graduated in Law from the Complutense University of Madrid and University of Paris 1 Pantheon-Sorbonne. Master's in EU Law (Competition Law) from ULB Brussels, and Master's in Economic Criminal Law from Rey Juan Carlos University. CESCOM Compliance certified. Previously legal adviser in the European Parliament and Berliner Corcoran &amp; Rowe LLP, Washington D.C. Specializes in complex criminal proceedings, money laundering compliance, and internal investigations.</div><div class="team-socials"><a href="#" class="team-social" aria-label="LinkedIn" title="LinkedIn"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M20.5 2h-17A1.5 1.5 0 002 3.5v17A1.5 1.5 0 003.5 22h17a1.5 1.5 0 001.5-1.5v-17A1.5 1.5 0 0020.5 2zM8 19H5v-9h3zM6.5 8.25A1.75 1.75 0 118.5 6.5a1.78 1.78 0 01-2 1.75zM19 19h-3v-4.74c0-1.42-.6-1.93-1.38-1.93A1.74 1.74 0 0013 14.19a.66.66 0 000 .14V19h-3v-9h2.9v1.3a3.11 3.11 0 012.7-1.4c1.55 0 3.36.86 3.36 3.66z"/></svg></a></div></div>
</div>"""

html = html[:team_start] + new_team + html[team_end:]

# Deploy to server
with open('/var/www/verdiscan/whitepaper/index.html', 'w') as f:
    f.write(html)

# Also copy to git repo
with open('/opt/verdis-chain-rust/web/whitepaper/index.html', 'w') as f:
    f.write(html)

# Verify
with open('/var/www/verdiscan/whitepaper/index.html', 'r') as f:
    content = f.read()

checks = [
    ('Inter' in content, 'Inter font'),
    ('#16a34a' in content, 'Correct green'),
    ('og:title' in content, 'OG tags'),
    ('Dorian Jean' in content, 'Dorian Jean'),
    ('Mark Jamestown' in content, 'Mark Jamestown'),
    ('Elizabeth Jefferson' in content, 'Elizabeth Jefferson'),
    ('Rojs Gordons' in content, 'Rojs Gordons'),
    ('Maria' in content or 'María' in content, 'Maria Dolores'),
    ('Ignacio' in content, 'Ignacio'),
    ('25,000,000,000' in content, 'Ecosystem 25B'),
    ('15,000,000,000' in content, 'Treasury 15B'),
    ('3,000,000,000' in content, 'Seed 3B'),
    ('2,000,000,000' in content, 'Presale 2B'),
    ('5,000,000,000' in content, 'Team 5B'),
    ('caff33' not in content, 'No neon green'),
    ('Poppins' not in content.split('<style>')[1].split('</style>')[0][:500], 'Not Poppins-primary'),
    ('team-card' in content, 'Team cards exist'),
]
for ok, label in checks:
    print(f'{"OK" if ok else "FAIL"}: {label}')
