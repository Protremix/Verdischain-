#!/usr/bin/env python3
"""Inject new dashboard tabs and UI into the Verdis dashboard"""

with open('/opt/verdis/app/dist/public/dashboard.html', 'r') as f:
    html = f.read()

# 1. Find existing tab buttons and add new ones
# Look for the tab navigation section
old_tabs_end = '<!-- End Tab Navigation -->'
if old_tabs_end not in html:
    # Try to find the last tab button
    import re
    # Find all tab buttons to understand the pattern
    tabs = re.findall(r'<button[^>]*class="[^"]*tab[^"]*"[^>]*>.*?</button>', html, re.DOTALL)
    if tabs:
        last_tab = tabs[-1]
        print(f"Found {len(tabs)} existing tabs")
        print(f"Last tab: {last_tab[:80]}...")

# 2. Find the tab content sections
# Look for a marker to inject new content
inject_marker = '</div><!-- End Dashboard Content -->'
if inject_marker not in html:
    inject_marker = '</body>'
    print(f"Using </body> as injection point")
else:
    print(f"Found end of dashboard content marker")

# 3. Build the new tabs HTML
new_tabs_js = """
<!-- New Feature Tabs UI -->
<div id="governanceSection" class="dashboard-section" style="display:none;">
    <div class="glass-card" style="background:rgba(10,20,15,0.85);border:1px solid rgba(0,255,136,0.15);border-radius:16px;padding:24px;margin-bottom:20px;">
        <h2 style="color:#00ff88;font-size:20px;margin-bottom:16px;">🏛️ Governance</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:20px;">
            <div class="gov-stat" style="background:rgba(0,255,136,0.05);border-radius:12px;padding:16px;">
                <div style="color:#888;font-size:12px;">Active Proposals</div>
                <div id="govActiveCount" style="color:#00ff88;font-size:24px;font-weight:700;">0</div>
            </div>
            <div class="gov-stat" style="background:rgba(0,255,136,0.05);border-radius:12px;padding:16px;">
                <div style="color:#888;font-size:12px;">Total Votes</div>
                <div id="govTotalVotes" style="color:#00ff88;font-size:24px;font-weight:700;">0</div>
            </div>
            <div class="gov-stat" style="background:rgba(0,255,136,0.05);border-radius:12px;padding:16px;">
                <div style="color:#888;font-size:12px;">Quorum</div>
                <div id="govQuorum" style="color:#00ff88;font-size:24px;font-weight:700;">10%</div>
            </div>
            <div class="gov-stat" style="background:rgba(0,255,136,0.05);border-radius:12px;padding:16px;">
                <div style="color:#888;font-size:12px;">Pass Threshold</div>
                <div id="govThreshold" style="color:#00ff88;font-size:24px;font-weight:700;">66%</div>
            </div>
        </div>
        <h3 style="color:#ccc;font-size:14px;margin-bottom:12px;">Create Proposal</h3>
        <div style="display:flex;flex-direction:column;gap:8px;margin-bottom:20px;">
            <input id="govTitle" placeholder="Proposal title" style="background:rgba(0,0,0,0.4);border:1px solid rgba(0,255,136,0.2);border-radius:8px;padding:10px;color:#fff;font-size:14px;">
            <textarea id="govDesc" placeholder="Description" style="background:rgba(0,0,0,0.4);border:1px solid rgba(0,255,136,0.2);border-radius:8px;padding:10px;color:#fff;font-size:14px;min-height:60px;"></textarea>
            <select id="govType" style="background:rgba(0,0,0,0.4);border:1px solid rgba(0,255,136,0.2);border-radius:8px;padding:10px;color:#fff;font-size:14px;">
                <option value="parameter_change">Parameter Change</option>
                <option value="treasury_spend">Treasury Spend</option>
                <option value="upgrade">Protocol Upgrade</option>
                <option value="other">Other</option>
            </select>
            <button onclick="createGovProposal()" style="background:#00ff88;color:#000;border:none;border-radius:8px;padding:10px;font-weight:600;cursor:pointer;">Submit Proposal</button>
        </div>
        <div id="govProposalsList" style="display:flex;flex-direction:column;gap:12px;"></div>
    </div>
</div>

<div id="aiAgentsSection" class="dashboard-section" style="display:none;">
    <div class="glass-card" style="background:rgba(10,20,15,0.85);border:1px solid rgba(0,255,136,0.15);border-radius:16px;padding:24px;margin-bottom:20px;">
        <h2 style="color:#00ff88;font-size:20px;margin-bottom:16px;">🤖 AI Agent Registry</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:20px;">
            <div style="background:rgba(0,255,136,0.05);border-radius:12px;padding:16px;">
                <div style="color:#888;font-size:12px;">Total Agents</div>
                <div id="aiTotalAgents" style="color:#00ff88;font-size:24px;font-weight:700;">0</div>
            </div>
            <div style="background:rgba(0,255,136,0.05);border-radius:12px;padding:16px;">
                <div style="color:#888;font-size:12px;">Active Agents</div>
                <div id="aiActiveAgents" style="color:#00ff88;font-size:24px;font-weight:700;">0</div>
            </div>
            <div style="background:rgba(0,255,136,0.05);border-radius:12px;padding:16px;">
                <div style="color:#888;font-size:12px;">Fraud Alerts</div>
                <div id="aiFraudAlerts" style="color:#ff4444;font-size:24px;font-weight:700;">0</div>
            </div>
            <div style="background:rgba(0,255,136,0.05);border-radius:12px;padding:16px;">
                <div style="color:#888;font-size:12px;">Avg Trust Score</div>
                <div id="aiTrustScore" style="color:#00ff88;font-size:24px;font-weight:700;">0</div>
            </div>
        </div>
        <h3 style="color:#ccc;font-size:14px;margin-bottom:12px;">Register AI Agent</h3>
        <div style="display:flex;flex-direction:column;gap:8px;margin-bottom:20px;">
            <input id="aiAgentId" placeholder="Agent ID (e.g. trading-bot-1)" style="background:rgba(0,0,0,0.4);border:1px solid rgba(0,255,136,0.2);border-radius:8px;padding:10px;color:#fff;font-size:14px;">
            <input id="aiAgentName" placeholder="Agent name" style="background:rgba(0,0,0,0.4);border:1px solid rgba(0,255,136,0.2);border-radius:8px;padding:10px;color:#fff;font-size:14px;">
            <input id="aiAgentDesc" placeholder="Description" style="background:rgba(0,0,0,0.4);border:1px solid rgba(0,255,136,0.2);border-radius:8px;padding:10px;color:#fff;font-size:14px;">
            <button onclick="registerAIAgent()" style="background:#00ff88;color:#000;border:none;border-radius:8px;padding:10px;font-weight:600;cursor:pointer;">Register Agent</button>
        </div>
        <div id="aiAgentsList" style="display:flex;flex-direction:column;gap:12px;"></div>
    </div>
</div>

<div id="nameServiceSection" class="dashboard-section" style="display:none;">
    <div class="glass-card" style="background:rgba(10,20,15,0.85);border:1px solid rgba(0,255,136,0.15);border-radius:16px;padding:24px;margin-bottom:20px;">
        <h2 style="color:#00ff88;font-size:20px;margin-bottom:16px;">🌐 Name Service (VNS)</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:20px;">
            <div style="background:rgba(0,255,136,0.05);border-radius:12px;padding:16px;">
                <div style="color:#888;font-size:12px;">Registered Names</div>
                <div id="vnsTotalNames" style="color:#00ff88;font-size:24px;font-weight:700;">0</div>
            </div>
            <div style="background:rgba(0,255,136,0.05);border-radius:12px;padding:16px;">
                <div style="color:#888;font-size:12px;">Active Names</div>
                <div id="vnsActiveNames" style="color:#00ff88;font-size:24px;font-weight:700;">0</div>
            </div>
        </div>
        <h3 style="color:#ccc;font-size:14px;margin-bottom:12px;">Register Name</h3>
        <div style="display:flex;gap:8px;margin-bottom:20px;">
            <input id="vnsName" placeholder="yourname" style="flex:1;background:rgba(0,0,0,0.4);border:1px solid rgba(0,255,136,0.2);border-radius:8px;padding:10px;color:#fff;font-size:14px;">
            <span style="color:#888;padding:10px 0;font-size:14px;">.verdis</span>
            <button onclick="registerVNSName()" style="background:#00ff88;color:#000;border:none;border-radius:8px;padding:10px 20px;font-weight:600;cursor:pointer;">Register</button>
        </div>
        <div style="display:flex;gap:8px;margin-bottom:20px;">
            <input id="vnsResolve" placeholder="Resolve name..." style="flex:1;background:rgba(0,0,0,0.4);border:1px solid rgba(0,255,136,0.2);border-radius:8px;padding:10px;color:#fff;font-size:14px;">
            <button onclick="resolveVNSName()" style="background:rgba(0,255,136,0.15);color:#00ff88;border:1px solid rgba(0,255,136,0.3);border-radius:8px;padding:10px 20px;cursor:pointer;">Resolve</button>
        </div>
        <div id="vnsResult" style="margin-top:8px;"></div>
        <div id="vnsNamesList" style="display:flex;flex-direction:column;gap:8px;margin-top:16px;"></div>
    </div>
</div>

<div id="fraudSection" class="dashboard-section" style="display:none;">
    <div class="glass-card" style="background:rgba(10,20,15,0.85);border:1px solid rgba(0,255,136,0.15);border-radius:16px;padding:24px;margin-bottom:20px;">
        <h2 style="color:#00ff88;font-size:20px;margin-bottom:16px;">🛡️ Fraud Detection</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:20px;">
            <div style="background:rgba(0,255,136,0.05);border-radius:12px;padding:16px;">
                <div style="color:#888;font-size:12px;">Total Alerts</div>
                <div id="fraudTotalAlerts" style="color:#ff4444;font-size:24px;font-weight:700;">0</div>
            </div>
            <div style="background:rgba(0,255,136,0.05);border-radius:12px;padding:16px;">
                <div style="color:#888;font-size:12px;">Monitored Addresses</div>
                <div id="fraudMonitored" style="color:#00ff88;font-size:24px;font-weight:700;">0</div>
            </div>
            <div style="background:rgba(0,255,136,0.05);border-radius:12px;padding:16px;">
                <div style="color:#888;font-size:12px;">Blacklisted</div>
                <div id="fraudBlacklisted" style="color:#ff4444;font-size:24px;font-weight:700;">0</div>
            </div>
        </div>
        <h3 style="color:#ccc;font-size:14px;margin-bottom:12px;">Analyze Transaction</h3>
        <div style="display:flex;gap:8px;margin-bottom:20px;">
            <input id="fraudAddr" placeholder="Wallet address" style="flex:1;background:rgba(0,0,0,0.4);border:1px solid rgba(0,255,136,0.2);border-radius:8px;padding:10px;color:#fff;font-size:14px;">
            <input id="fraudAmount" placeholder="Amount" type="number" style="width:120px;background:rgba(0,0,0,0.4);border:1px solid rgba(0,255,136,0.2);border-radius:8px;padding:10px;color:#fff;font-size:14px;">
            <button onclick="analyzeFraud()" style="background:#00ff88;color:#000;border:none;border-radius:8px;padding:10px 20px;font-weight:600;cursor:pointer;">Analyze</button>
        </div>
        <div id="fraudAlertsList" style="display:flex;flex-direction:column;gap:8px;"></div>
    </div>
</div>

<div id="accountAbstractionSection" class="dashboard-section" style="display:none;">
    <div class="glass-card" style="background:rgba(10,20,15,0.85);border:1px solid rgba(0,255,136,0.15);border-radius:16px;padding:24px;margin-bottom:20px;">
        <h2 style="color:#00ff88;font-size:20px;margin-bottom:16px;">🔐 Account Abstraction</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:20px;">
            <div style="background:rgba(0,255,136,0.05);border-radius:12px;padding:16px;">
                <div style="color:#888;font-size:12px;">Smart Wallets</div>
                <div id="aaSmartWallets" style="color:#00ff88;font-size:24px;font-weight:700;">0</div>
            </div>
            <div style="background:rgba(0,255,136,0.05);border-radius:12px;padding:16px;">
                <div style="color:#888;font-size:12px;">Active Sessions</div>
                <div id="aaActiveSessions" style="color:#00ff88;font-size:24px;font-weight:700;">0</div>
            </div>
            <div style="background:rgba(0,255,136,0.05);border-radius:12px;padding:16px;">
                <div style="color:#888;font-size:12px;">Pending Recoveries</div>
                <div id="aaPendingRecoveries" style="color:#ff4444;font-size:24px;font-weight:700;">0</div>
            </div>
        </div>
        <h3 style="color:#ccc;font-size:14px;margin-bottom:12px;">Create Smart Wallet</h3>
        <div style="display:flex;flex-direction:column;gap:8px;margin-bottom:20px;">
            <input id="aaDailyLimit" placeholder="Daily spending limit (VRS)" type="number" style="background:rgba(0,0,0,0.4);border:1px solid rgba(0,255,136,0.2);border-radius:8px;padding:10px;color:#fff;font-size:14px;">
            <button onclick="createSmartWallet()" style="background:#00ff88;color:#000;border:none;border-radius:8px;padding:10px;font-weight:600;cursor:pointer;">Create Smart Wallet</button>
        </div>
        <div id="aaWalletsList" style="display:flex;flex-direction:column;gap:8px;"></div>
    </div>
</div>

<div id="tokenomicsSection" class="dashboard-section" style="display:none;">
    <div class="glass-card" style="background:rgba(10,20,15,0.85);border:1px solid rgba(0,255,136,0.15);border-radius:16px;padding:24px;margin-bottom:20px;">
        <h2 style="color:#00ff88;font-size:20px;margin-bottom:16px;">💰 Tokenomics</h2>
        <div id="tokenomicsData" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;"></div>
        <h3 style="color:#ccc;font-size:14px;margin:20px 0 12px;">Fee Distribution</h3>
        <div id="feeDistribution" style="display:flex;flex-direction:column;gap:8px;"></div>
    </div>
</div>

<script>
// === Governance Tab Functions ===
async function loadGovernance() {
    try {
        const [stats, proposals] = await Promise.all([
            fetch('/api/governance/stats').then(r => r.json()),
            fetch('/api/governance/proposals').then(r => r.json())
        ]);
        document.getElementById('govActiveCount').textContent = stats.active;
        document.getElementById('govTotalVotes').textContent = stats.totalVotes.toLocaleString();
        document.getElementById('govQuorum').textContent = stats.quorumPct + '%';
        document.getElementById('govThreshold').textContent = stats.thresholdPct + '%';
        
        const list = document.getElementById('govProposalsList');
        if (!proposals || proposals.length === 0) {
            list.innerHTML = '<p style="color:#888;text-align:center;padding:20px;">No proposals yet</p>';
            return;
        }
        list.innerHTML = proposals.map(p => `
            <div style="background:rgba(0,0,0,0.3);border:1px solid rgba(0,255,136,0.1);border-radius:12px;padding:16px;">
                <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:8px;">
                    <div>
                        <h4 style="color:#fff;font-size:15px;margin:0 0 4px;">#${p.id}: ${p.title}</h4>
                        <p style="color:#888;font-size:13px;margin:0;">${p.description}</p>
                    </div>
                    <span style="background:${p.status==='active'?'rgba(0,255,136,0.2)':'rgba(255,200,0,0.2)'};color:${p.status==='active'?'#00ff88':'#ffc800'};padding:4px 12px;border-radius:20px;font-size:11px;text-transform:uppercase;">${p.status}</span>
                </div>
                <div style="display:flex;gap:16px;margin-top:12px;font-size:13px;">
                    <span style="color:#00ff88;">✓ For: ${p.forVotes.toLocaleString()}</span>
                    <span style="color:#ff4444;">✗ Against: ${p.againstVotes.toLocaleString()}</span>
                    <span style="color:#888;">👥 ${p.voterCount} voters</span>
                </div>
                ${p.status === 'active' ? `
                    <div style="display:flex;gap:8px;margin-top:12px;">
                        <button onclick="voteOnProposal(${p.id}, 'for')" style="background:rgba(0,255,136,0.15);color:#00ff88;border:1px solid rgba(0,255,136,0.3);border-radius:6px;padding:6px 16px;cursor:pointer;font-size:13px;">Vote For</button>
                        <button onclick="voteOnProposal(${p.id}, 'against')" style="background:rgba(255,68,68,0.15);color:#ff4444;border:1px solid rgba(255,68,68,0.3);border-radius:6px;padding:6px 16px;cursor:pointer;font-size:13px;">Vote Against</button>
                    </div>
                ` : ''}
            </div>
        `).join('');
    } catch(e) { console.error('Governance load error:', e); }
}

async function createGovProposal() {
    const title = document.getElementById('govTitle').value;
    const desc = document.getElementById('govDesc').value;
    const type = document.getElementById('govType').value;
    const addr = localStorage.getItem('verdisWalletAddress') || '0x0bfef9eb91a36d4010367869aa1e1927d353a35b';
    if (!title || !desc) return alert('Title and description required');
    const res = await fetch('/api/governance/proposal/create', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ proposer: addr, title, description: desc, proposalType: type, actions: [] })
    }).then(r => r.json());
    if (res.success) { alert('Proposal created!'); loadGovernance(); }
    else alert('Error: ' + res.error);
}

async function voteOnProposal(id, vote) {
    const addr = localStorage.getItem('verdisWalletAddress') || '0x0bfef9eb91a36d4010367869aa1e1927d353a35b';
    const res = await fetch('/api/governance/vote', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ voter: addr, proposalId: id, vote })
    }).then(r => r.json());
    if (res.success) { alert('Vote cast! Power: ' + res.votingPower.toLocaleString()); loadGovernance(); }
    else alert('Error: ' + res.error);
}

// === AI Agents Tab Functions ===
async function loadAIAgents() {
    try {
        const stats = await fetch('/api/ai/stats').then(r => r.json());
        document.getElementById('aiTotalAgents').textContent = stats.totalAgents;
        document.getElementById('aiActiveAgents').textContent = stats.activeAgents;
        document.getElementById('aiFraudAlerts').textContent = stats.fraudAlerts;
        document.getElementById('aiTrustScore').textContent = Math.round(stats.avgTrustScore);
        document.getElementById('aiAgentsList').innerHTML = stats.totalAgents === 0 
            ? '<p style="color:#888;text-align:center;padding:20px;">No AI agents registered yet</p>' : '';
    } catch(e) { console.error('AI load error:', e); }
}

async function registerAIAgent() {
    const agentId = document.getElementById('aiAgentId').value;
    const name = document.getElementById('aiAgentName').value;
    const desc = document.getElementById('aiAgentDesc').value;
    const addr = localStorage.getItem('verdisWalletAddress') || '0x0bfef9eb91a36d4010367869aa1e1927d353a35b';
    if (!agentId) return alert('Agent ID required');
    const res = await fetch('/api/ai/agent/register', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ agentId, ownerAddress: addr, walletAddress: addr, metadata: { name, description: desc } })
    }).then(r => r.json());
    if (res.success) { alert('AI Agent registered!'); loadAIAgents(); }
    else alert('Error: ' + res.error);
}

// === Name Service Tab Functions ===
async function loadVNS() {
    try {
        const stats = await fetch('/api/vns/stats').then(r => r.json());
        document.getElementById('vnsTotalNames').textContent = stats.totalNames;
        document.getElementById('vnsActiveNames').textContent = stats.activeNames;
        document.getElementById('vnsNamesList').innerHTML = stats.totalNames === 0
            ? '<p style="color:#888;text-align:center;padding:20px;">No names registered yet</p>' : '';
    } catch(e) { console.error('VNS load error:', e); }
}

async function registerVNSName() {
    const name = document.getElementById('vnsName').value;
    const addr = localStorage.getItem('verdisWalletAddress') || '0x0bfef9eb91a36d4010367869aa1e1927d353a35b';
    if (!name) return alert('Name required');
    const res = await fetch('/api/vns/register', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ name, ownerAddress: addr })
    }).then(r => r.json());
    if (res.success) { alert('Name registered: ' + name + '.verdis'); loadVNS(); }
    else alert('Error: ' + res.error);
}

async function resolveVNSName() {
    const name = document.getElementById('vnsResolve').value;
    if (!name) return;
    const res = await fetch('/api/vns/resolve/' + name.replace('.verdis','')).then(r => r.json());
    document.getElementById('vnsResult').innerHTML = res.address 
        ? `<p style="color:#00ff88;">${name} → ${res.address}</p>`
        : `<p style="color:#ff4444;">Name not found</p>`;
}

// === Fraud Detection Tab Functions ===
async function loadFraud() {
    try {
        const stats = await fetch('/api/fraud/stats').then(r => r.json());
        document.getElementById('fraudTotalAlerts').textContent = stats.totalAlerts;
        document.getElementById('fraudMonitored').textContent = stats.monitoredAddresses;
        document.getElementById('fraudBlacklisted').textContent = stats.blacklistedAddresses;
        const alerts = await fetch('/api/fraud/alerts').then(r => r.json());
        const list = document.getElementById('fraudAlertsList');
        if (!alerts || alerts.length === 0) {
            list.innerHTML = '<p style="color:#888;text-align:center;padding:20px;">No fraud alerts</p>';
        } else {
            list.innerHTML = alerts.slice(0,10).map(a => `
                <div style="background:rgba(255,68,68,0.05);border:1px solid rgba(255,68,68,0.2);border-radius:8px;padding:12px;">
                    <span style="color:#ff4444;font-weight:600;">⚠ ${a.type}</span>
                    <span style="color:#888;font-size:12px;margin-left:8px;">${new Date(a.timestamp).toLocaleString()}</span>
                </div>
            `).join('');
        }
    } catch(e) { console.error('Fraud load error:', e); }
}

async function analyzeFraud() {
    const addr = document.getElementById('fraudAddr').value;
    const amount = parseFloat(document.getElementById('fraudAmount').value);
    if (!addr) return alert('Address required');
    const res = await fetch('/api/fraud/analyze', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ address: addr, amount })
    }).then(r => r.json());
    alert(res.isFraud ? '⚠ FRAUD DETECTED: ' + res.reasons.join(', ') : '✓ No fraud detected');
}

// === Account Abstraction Tab Functions ===
async function loadAA() {
    try {
        const stats = await fetch('/api/aa/stats').then(r => r.json());
        document.getElementById('aaSmartWallets').textContent = stats.totalSmartWallets;
        document.getElementById('aaActiveSessions').textContent = stats.activeSessions;
        document.getElementById('aaPendingRecoveries').textContent = stats.pendingRecoveries;
        document.getElementById('aaWalletsList').innerHTML = stats.totalSmartWallets === 0
            ? '<p style="color:#888;text-align:center;padding:20px;">No smart wallets created yet</p>' : '';
    } catch(e) { console.error('AA load error:', e); }
}

async function createSmartWallet() {
    const dailyLimit = parseFloat(document.getElementById('aaDailyLimit').value) || 10000;
    const addr = localStorage.getItem('verdisWalletAddress') || '0x0bfef9eb91a36d4010367869aa1e1927d353a35b';
    const res = await fetch('/api/aa/wallet/create', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ ownerAddress: addr, config: { dailyLimit, guardians: [] } })
    }).then(r => r.json());
    if (res.success) { alert('Smart wallet created!'); loadAA(); }
    else alert('Error: ' + res.error);
}

// === Tokenomics Tab Functions ===
async function loadTokenomics() {
    try {
        const data = await fetch('/api/tokenomics/info').then(r => r.json());
        const grid = document.getElementById('tokenomicsData');
        grid.innerHTML = `
            <div style="background:rgba(0,255,136,0.05);border-radius:12px;padding:16px;">
                <div style="color:#888;font-size:12px;">Fee Burn Rate</div>
                <div style="color:#00ff88;font-size:24px;font-weight:700;">${data.feeBurnRate * 100}%</div>
            </div>
            <div style="background:rgba(0,255,136,0.05);border-radius:12px;padding:16px;">
                <div style="color:#888;font-size:12px;">Treasury Balance</div>
                <div style="color:#00ff88;font-size:24px;font-weight:700;">${data.treasuryBalance.toLocaleString()} VRS</div>
            </div>
            <div style="background:rgba(0,255,136,0.05);border-radius:12px;padding:16px;">
                <div style="color:#888;font-size:12px;">Gas Abstraction</div>
                <div style="color:#00ff88;font-size:24px;font-weight:700;">${data.gasAbstractionEnabled ? 'Enabled' : 'Disabled'}</div>
            </div>
        `;
        const dist = data.rewardDistribution;
        document.getElementById('feeDistribution').innerHTML = `
            <div style="display:flex;justify-content:space-between;padding:8px 12px;background:rgba(0,255,136,0.05);border-radius:8px;">
                <span style="color:#888;">Block Producer Reward</span><span style="color:#00ff88;">${dist.producer * 100}%</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:8px 12px;background:rgba(0,255,136,0.05);border-radius:8px;">
                <span style="color:#888;">Voter Rewards</span><span style="color:#00ff88;">${dist.voters * 100}%</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:8px 12px;background:rgba(0,255,136,0.05);border-radius:8px;">
                <span style="color:#888;">Treasury Allocation</span><span style="color:#00ff88;">${dist.treasury * 100}%</span>
            </div>
        `;
    } catch(e) { console.error('Tokenomics load error:', e); }
}

// Load appropriate section when tab is clicked
function loadSectionData(sectionId) {
    switch(sectionId) {
        case 'governanceSection': loadGovernance(); break;
        case 'aiAgentsSection': loadAIAgents(); break;
        case 'nameServiceSection': loadVNS(); break;
        case 'fraudSection': loadFraud(); break;
        case 'accountAbstractionSection': loadAA(); break;
        case 'tokenomicsSection': loadTokenomics(); break;
    }
}
</script>
"""

# Inject before the closing body tag or end of dashboard content
if inject_marker in html:
    html = html.replace(inject_marker, new_tabs_js + '\n' + inject_marker)
    print("Injected new dashboard sections")
else:
    html = html.replace('</body>', new_tabs_js + '\n</body>')
    print("Injected before </body>")

with open('/opt/verdis/app/dist/public/dashboard.html', 'w') as f:
    f.write(html)
print("Dashboard updated with new feature tabs!")
