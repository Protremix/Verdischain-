#!/usr/bin/env python3
"""Fix dashboard: add proper tab buttons and align sections with the existing tab system"""

with open('/opt/verdis/app/dist/web/dashboard.html', 'r') as f:
    html = f.read()

# 1. Add new tab buttons after existing ones
old_tabs = '<div class="nav-tab" data-tab="monitoring">📈 Monitoring</div>'
new_tabs = '''<div class="nav-tab" data-tab="monitoring">📈 Monitoring</div>
<div class="nav-tab" data-tab="aiagents">🤖 AI Agents</div>
<div class="nav-tab" data-tab="nameservice">🌐 Names</div>
<div class="nav-tab" data-tab="fraud">🛡️ Fraud</div>
<div class="nav-tab" data-tab="aa">🔐 Smart Wallet</div>
<div class="nav-tab" data-tab="tokenomics">💰 Tokenomics</div>'''

if old_tabs in html:
    html = html.replace(old_tabs, new_tabs, 1)
    print("1. Added new tab buttons")
else:
    print("1. ERROR: tab not found")

# 2. Rename my injected sections to match the tab system
# governanceSection -> section-governance with class "section"
html = html.replace('id="governanceSection" class="dashboard-section" style="display:none;"',
                    'id="section-governance" class="section"')
html = html.replace('id="aiAgentsSection" class="dashboard-section" style="display:none;"',
                    'id="section-aiagents" class="section"')
html = html.replace('id="nameServiceSection" class="dashboard-section" style="display:none;"',
                    'id="section-nameservice" class="section"')
html = html.replace('id="fraudSection" class="dashboard-section" style="display:none;"',
                    'id="section-fraud" class="section"')
html = html.replace('id="accountAbstractionSection" class="dashboard-section" style="display:none;"',
                    'id="section-aa" class="section"')
html = html.replace('id="tokenomicsSection" class="dashboard-section" style="display:none;"',
                    'id="section-tokenomics" class="section"')
print("2. Renamed sections to match tab system")

# 3. Check if there's an existing governance section that conflicts
import re
# Count section-governance occurrences
gov_count = html.count('id="section-governance"')
if gov_count > 1:
    print(f"  WARNING: {gov_count} governance sections found — need to remove old one")

# 4. Update loadTabData function to handle new tabs
old_load = 'function loadTabData(t)'
if old_load in html:
    # Find the function body
    idx = html.index(old_load)
    # Find the end of the function (next function or closing)
    # Add new cases to loadTabData
    new_cases = '''
    // New tab data loaders
    if (t === 'aiagents') loadAIAgents();
    if (t === 'nameservice') loadVNS();
    if (t === 'fraud') loadFraud();
    if (t === 'aa') loadAA();
    if (t === 'tokenomics') loadTokenomics();
    // Governance already has its own loader, ensure it's called
    if (t === 'governance') loadGovernance();
'''
    # Insert after the function opening
    # Find the first { after loadTabData
    brace_idx = html.index('{', idx)
    html = html[:brace_idx+1] + new_cases + html[brace_idx+1:]
    print("3. Updated loadTabData with new tab loaders")
else:
    print("3. ERROR: loadTabData not found, trying alternate approach")
    # Add the loadSectionData calls to switchTab
    old_switch = "loadTabData(t)}"
    new_switch = """loadTabData(t)
    // Load new feature sections
    if(t==='governance')loadGovernance();
    if(t==='aiagents')loadAIAgents();
    if(t==='nameservice')loadVNS();
    if(t==='fraud')loadFraud();
    if(t==='aa')loadAA();
    if(t==='tokenomics')loadTokenomics();
    }"""
    if old_switch in html:
        html = html.replace(old_switch, new_switch)
        print("3. Added loaders to switchTab")

# 5. Fix any remaining VCO references in the dashboard
html = html.replace('VCO', 'VRS')
print("4. Replaced VCO with VRS in dashboard")

with open('/opt/verdis/app/dist/web/dashboard.html', 'w') as f:
    f.write(html)
print("Dashboard fixed!")
