import re

with open('/var/www/verdiscan/whitepaper/index.html', 'r') as f:
    html = f.read()

# Find and replace the entire dist-legend-grid block
start_marker = '<div class="dist-legend-grid">'
end_marker = '<!-- SECTION 3: VESTING SCHEDULE -->'

start_idx = html.find(start_marker)
end_idx = html.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print(f'ERROR: Could not find markers. start={start_idx}, end={end_idx}')
    exit(1)

new_legend = """<div class="dist-legend-grid">
        <div class="dist-item active" data-idx="0" onclick="selectDist(0, '25B VRDX', 'Ecosystem & Developer Grants')">
          <div class="dist-left">
            <div class="dist-color-dot" style="background:#caff33;"></div>
            <div>
              <div class="dist-name">Ecosystem & Developer Grants</div>
              <div class="dist-desc">Grants, Developer Funds, User Rewards</div>
            </div>
          </div>
          <div class="dist-right">
            <div class="dist-pct mono">25%</div>
            <div class="dist-amt mono">25,000,000,000</div>
          </div>
        </div>

        <div class="dist-item" data-idx="1" onclick="selectDist(1, '20B VRDX', 'PoS Staking Rewards')">
          <div class="dist-left">
            <div class="dist-color-dot" style="background:#00a86b;"></div>
            <div>
              <div class="dist-name">PoS Staking Rewards</div>
              <div class="dist-desc">DPoS Block Emission & Yield Incentives</div>
            </div>
          </div>
          <div class="dist-right">
            <div class="dist-pct mono">20%</div>
            <div class="dist-amt mono">20,000,000,000</div>
          </div>
        </div>

        <div class="dist-item" data-idx="2" onclick="selectDist(2, '15B VRDX', 'Treasury')">
          <div class="dist-left">
            <div class="dist-color-dot" style="background:#84fe87;"></div>
            <div>
              <div class="dist-name">Treasury</div>
              <div class="dist-desc">DAO-Governed Strategic Reserve</div>
            </div>
          </div>
          <div class="dist-right">
            <div class="dist-pct mono">15%</div>
            <div class="dist-amt mono">15,000,000,000</div>
          </div>
        </div>

        <div class="dist-item" data-idx="3" onclick="selectDist(3, '10B VRDX', 'Development')">
          <div class="dist-left">
            <div class="dist-color-dot" style="background:#ffbd2e;"></div>
            <div>
              <div class="dist-name">Development</div>
              <div class="dist-desc">Core Protocol & Tooling Engineering</div>
            </div>
          </div>
          <div class="dist-right">
            <div class="dist-pct mono">10%</div>
            <div class="dist-amt mono">10,000,000,000</div>
          </div>
        </div>

        <div class="dist-item" data-idx="4" onclick="selectDist(4, '10B VRDX', 'Liquidity')">
          <div class="dist-left">
            <div class="dist-color-dot" style="background:#3b82f6;"></div>
            <div>
              <div class="dist-name">Liquidity</div>
              <div class="dist-desc">DEX & Market Making Provision</div>
            </div>
          </div>
          <div class="dist-right">
            <div class="dist-pct mono">10%</div>
            <div class="dist-amt mono">10,000,000,000</div>
          </div>
        </div>

        <div class="dist-item" data-idx="5" onclick="selectDist(5, '5B VRDX', 'Community')">
          <div class="dist-left">
            <div class="dist-color-dot" style="background:#a855f7;"></div>
            <div>
              <div class="dist-name">Community</div>
              <div class="dist-desc">Airdrops, Campaigns & User Rewards</div>
            </div>
          </div>
          <div class="dist-right">
            <div class="dist-pct mono">5%</div>
            <div class="dist-amt mono">5,000,000,000</div>
          </div>
        </div>

        <div class="dist-item" data-idx="6" onclick="selectDist(6, '3B VRDX', 'Seed / Strategic')">
          <div class="dist-left">
            <div class="dist-color-dot" style="background:#ec4899;"></div>
            <div>
              <div class="dist-name">Seed / Strategic</div>
              <div class="dist-desc">Seed & Private Round Allocations</div>
            </div>
          </div>
          <div class="dist-right">
            <div class="dist-pct mono">3%</div>
            <div class="dist-amt mono">3,000,000,000</div>
          </div>
        </div>

        <div class="dist-item" data-idx="7" onclick="selectDist(7, '2B VRDX', 'Public Presale')">
          <div class="dist-left">
            <div class="dist-color-dot" style="background:#f97316;"></div>
            <div>
              <div class="dist-name">Public Presale</div>
              <div class="dist-desc">Public Round Allocation</div>
            </div>
          </div>
          <div class="dist-right">
            <div class="dist-pct mono">2%</div>
            <div class="dist-amt mono">2,000,000,000</div>
          </div>
        </div>

        <div class="dist-item" data-idx="8" onclick="selectDist(8, '5B VRDX', 'Team & Advisors')">
          <div class="dist-left">
            <div class="dist-color-dot" style="background:#6b7280;"></div>
            <div>
              <div class="dist-name">Team & Advisors</div>
              <div class="dist-desc">4-Year Vesting with 12-Month Cliff</div>
            </div>
          </div>
          <div class="dist-right">
            <div class="dist-pct mono">5%</div>
            <div class="dist-amt mono">5,000,000,000</div>
          </div>
        </div>
      </div>
    </div>
  </section>

  """

html = html[:start_idx] + new_legend + html[end_idx:]

# Fix vesting: Community & Eco 45B -> Ecosystem & Community 30B
html = html.replace('Community & Eco', 'Ecosystem & Community')
html = html.replace('45B VRDX', '30B VRDX')
html = html.replace('4,500,000,000 circulating', '3,000,000,000 circulating')

# Fix investor stat card
html = html.replace(
    '10,000,000,000</div>\n          <div class="stat-label">Investor Allocation',
    '12,000,000,000</div>\n          <div class="stat-label">Investor Allocation'
)

with open('/var/www/verdiscan/whitepaper/index.html', 'w') as f:
    f.write(html)

# Verify
with open('/var/www/verdiscan/whitepaper/index.html', 'r') as f:
    content = f.read()

checks = [
    ('25,000,000,000' in content, 'Ecosystem 25B'),
    ('15,000,000,000' in content, 'Treasury 15B'),
    ('3,000,000,000</div>' in content, 'Seed 3B'),
    ('2,000,000,000' in content, 'Presale 2B'),
    ('5,000,000,000</div>' in content, 'Team 5B'),
    ('30B VRDX' in content, 'Vesting Ecosystem 30B'),
    ('12,000,000,000' in content, 'Investor 12B stat'),
    ('21 Validator' in content, '21 validators'),
    ('0 tCO2e (testnet)' in content, 'carbon testnet'),
    ('45B' not in content, 'No old 45B'),
    ('210,000,000,000' not in content, 'No old 210B'),
    ('110,000,000,000' not in content, 'No old 110B'),
]
for ok, label in checks:
    print(f'{"OK" if ok else "FAIL"}: {label}')
