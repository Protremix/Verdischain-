import re

with open('/var/www/verdiscan/whitepaper/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add improvement items 09-12 after item 08
improve_08_end = html.find('</div>\n</div>\n</div>\n</section>\n\n<section id="tokenomics"')
if improve_08_end == -1:
    # Try to find the end of the improve list
    improve_08_pos = html.find('Mainnet Launch & Global Reforestation')
    if improve_08_pos > 0:
        # Find the closing </div></div></div></section> after this
        improve_08_end = html.find('</div>\n</div>\n</div>\n</section>', improve_08_pos)

if improve_08_end > 0:
    new_improvements = """<div class="improve-item"><div class="improve-num">09</div><div class="improve-content"><div class="improve-title">Decentralized Identity &amp; Green Certificates</div><div class="improve-desc">Implement on-chain decentralized identity (DID) for green energy producers, reforestation projects, and carbon auditors. Each entity receives a verifiable on-chain credential linking their real-world certifications to their blockchain identity, enabling trustless verification of green claims.</div></div></div>
<div class="improve-item"><div class="improve-num">10</div><div class="improve-content"><div class="improve-title">Layer-2 ZK Rollup Scaling</div><div class="improve-desc">Deploy a ZK rollup for high-throughput microtransactions: carbon credit micro-offsets, IoT sensor data logging, and real-time energy trading. The rollup batches thousands of transactions off-chain and posts a single ZK proof on-chain, achieving 10,000+ TPS while inheriting Layer-1 security.</div></div></div>
<div class="improve-item"><div class="improve-num">11</div><div class="improve-content"><div class="improve-title">AI-Powered Autonomous Carbon Verification</div><div class="improve-desc">Integrate satellite imagery analysis, IoT sensor networks, and AI models via EvolvixOS to autonomously verify reforestation progress and carbon sequestration in real time. Eliminate manual auditing by publishing AI-verified carbon data directly on-chain with cryptographic proof of analysis.</div></div></div>
<div class="improve-item"><div class="improve-num">12</div><div class="improve-content"><div class="improve-title">Global Green Finance Integration</div><div class="improve-desc">Enable carbon-backed stablecoins, green bonds, and ESG-compliant DeFi instruments. Partner with institutional carbon registries (Verra, Gold Standard) for cross-platform credit interoperability. Position VRDX as the settlement layer for the global green economy.</div></div></div>
<div class="improve-item"><div class="improve-num">13</div><div class="improve-content"><div class="improve-title">IoT &amp; Oracle Network</div><div class="improve-desc">Deploy decentralized oracle nodes connected to IoT sensors monitoring air quality, soil health, tree growth, and energy production. Real-time environmental data feeds directly into carbon credit calculations and green validator scoring, creating a verifiable chain of custody from sensor to blockchain.</div></div></div>
<div class="improve-item"><div class="improve-num">14</div><div class="improve-content"><div class="improve-title">Developer Ecosystem &amp; Grant Program</div><div class="improve-desc">Launch a 5B VRDX developer grant program funded from the ecosystem allocation. Support third-party teams building DeFi protocols, NFT marketplaces, supply chain trackers, and green energy apps on Verdis Chain. Provide open-source SDKs, technical documentation, and deployment grants up to 500K VRDX per project.</div></div></div>
"""
    html = html[:improve_08_end] + new_improvements + html[improve_08_end:]
    print("Added improvement items 09-14")
else:
    print("WARN: Could not find improvement list end")

# 2. Add Phases 6-12 to the Token Release Roadmap
# Find Phase 5 and add after it
phase5_pos = html.find('Phase 5 • 2027 – 2030')
if phase5_pos == -1:
    phase5_pos = html.find('Phase 5')

if phase5_pos > 0:
    # Find the closing of Phase 5's rm-item
    phase5_end = html.find('</div>\n</div>\n</div>\n</div>\n</section>', phase5_pos)
    if phase5_end == -1:
        # Find the </div></section> that closes the roadmap section
        phase5_end = html.find('</div>\n</section>', phase5_pos)

    if phase5_end > 0:
        new_phases = """<div class="rm-item"><div class="rm-dot"></div><div class="rm-content"><div class="rm-phase">Phase 6 • 2030 – 2032</div><div class="rm-title">AI-Powered Autonomous Governance</div><div class="rm-desc">EvolvixOS AI models analyze on-chain proposals, simulate economic impact, and provide governance recommendations to VRDX holders. Implementation of quadratic voting with AI-generated proposal summaries. DAO transitions to hybrid human-AI governance model with automated parameter optimization.</div></div></div>
<div class="rm-item"><div class="rm-dot"></div><div class="rm-content"><div class="rm-phase">Phase 7 • 2030 – 2033</div><div class="rm-title">Cross-Chain Carbon Credit Protocol</div><div class="rm-desc">Carbon credits minted on Verdis Chain become tradeable across all IBC-connected chains (Polkadot, Cosmos, Ethereum, BSC). Standardized cross-chain carbon credit format with unified retirement verification. <span class="mono">100M+ tCO2e</span> annual offset capacity.</div></div></div>
<div class="rm-item"><div class="rm-dot"></div><div class="rm-content"><div class="rm-phase">Phase 8 • 2031 – 2034</div><div class="rm-title">ZK Rollup &amp; 10,000+ TPS Scaling</div><div class="rm-desc">Production deployment of Verdis ZK rollup for high-throughput microtransactions. Real-time IoT sensor data logging, carbon credit micro-offsets, and energy trading at <span class="mono">10,000+ TPS</span> while inheriting Layer-1 security. Sub-cent transaction fees for green micropayments.</div></div></div>
<div class="rm-item"><div class="rm-dot"></div><div class="rm-content"><div class="rm-phase">Phase 9 • 2032 – 2035</div><div class="rm-title">Decentralized Identity &amp; Green Certification Network</div><div class="rm-desc">On-chain DID system for green energy producers, reforestation projects, carbon auditors, and ESG verifiers. W3C-compliant verifiable credentials linked to real-world certifications. Partnerships with Verra, Gold Standard, and EU ETS for cross-platform carbon credit interoperability.</div></div></div>
<div class="rm-item"><div class="rm-dot"></div><div class="rm-content"><div class="rm-phase">Phase 10 • 2033 – 2036</div><div class="rm-title">Global Green Finance Infrastructure</div><div class="rm-desc">Carbon-backed stablecoins, green bonds, and ESG-compliant DeFi instruments built natively on Verdis Chain. Institutional-grade carbon registry integration. VRDX positioned as the settlement layer for the <span class="mono">$50T+</span> global green economy. Central bank digital currency (CBDC) pilots for green stimulus programs.</div></div></div>
<div class="rm-item"><div class="rm-dot"></div><div class="rm-content"><div class="rm-phase">Phase 11 • 2034 – 2037</div><div class="rm-title">Planetary Carbon Dashboard</div><div class="rm-desc">Real-time global carbon footprint dashboard powered by IoT sensors, satellite imagery, and AI analysis via EvolvixOS. Every tonne of CO2 offset on Verdis Chain is traceable from source to retirement. Public API for governments, NGOs, and corporations to verify environmental claims transparently.</div></div></div>
<div class="rm-item"><div class="rm-dot"></div><div class="rm-content"><div class="rm-phase">Phase 12 • 2035 – 2040</div><div class="rm-title">Carbon-Negative Planet</div><div class="rm-desc">Final vision: Verdis Chain retires <span class="mono">1B+ tCO2e</span> cumulative carbon offsets. 500+ validators across 50+ countries, all powered by 100% renewable energy. The protocol becomes the global trust layer for environmental accountability. Blockchain technology transitions from environmental liability to environmental solution.</div></div></div>
"""
        html = html[:phase5_end] + new_phases + html[phase5_end:]
        print("Added roadmap Phases 6-12")
    else:
        print("WARN: Could not find Phase 5 end position")
else:
    print("WARN: Could not find Phase 5")

# 3. Update the story timeline to add more future milestones
story_q3_pos = html.find('Q3 2026</div><div class="story-tl-title">Security Audit')
if story_q3_pos > 0:
    story_q3_end = html.find('</div></div>', story_q3_pos + 100)
    if story_q3_end > 0:
        new_timeline = """</div></div>
<div class="story-tl-item"><div class="story-tl-dot"></div><div class="story-tl-date">Q4 2026</div><div class="story-tl-title">Mainnet Launch &amp; TGE</div><div class="story-tl-desc">Production mainnet genesis with 21 active validators, full tokenomics activated, VRDX TGE with 8B circulating supply. DAO governance assumes treasury control.</div></div>
<div class="story-tl-item"><div class="story-tl-dot"></div><div class="story-tl-date">2027 – 2028</div><div class="story-tl-title">Cross-Chain Expansion</div><div class="story-tl-desc">IBC bridges to Polkadot, Cosmos, Ethereum. Carbon credit marketplace launch. 100+ active validators. First 1M tCO2e retired on-chain.</div></div>
<div class="story-tl-item"><div class="story-tl-dot"></div><div class="story-tl-date">2029 – 2030</div><div class="story-tl-title">ZK Rollup &amp; AI Governance</div><div class="story-tl-desc">10,000+ TPS ZK rollup deployed. AI-powered autonomous governance via EvolvixOS. 10M+ tCO2e cumulative offsets. Global reforestation partnerships across 20+ countries.</div></div>
<div class="story-tl-item"><div class="story-tl-dot"></div><div class="story-tl-date">2030 – 2035</div><div class="story-tl-title">Global Green Finance Layer</div><div class="story-tl-desc">Carbon-backed stablecoins, green bonds, ESG DeFi. Institutional integration with Verra and Gold Standard. 100M+ tCO2e annual offset capacity. VRDX as global green settlement layer.</div></div>
<div class="story-tl-item"><div class="story-tl-dot"></div><div class="story-tl-date">2035 – 2040</div><div class="story-tl-title">Carbon-Negative Planet</div><div class="story-tl-desc">1B+ tCO2e cumulative carbon retired. 500+ validators in 50+ countries on 100% renewable energy. Verdis Chain becomes the global trust layer for environmental accountability.</div></div>
"""
        # Find the actual end of the Q3 2026 item
        q3_item_end = html.find('</div></div>', story_q3_pos)
        # Find the next item or the closing of the timeline
        q3_next = html.find('<div class="story-tl-item">', q3_item_end + 10)
        if q3_next > 0:
            html = html[:q3_item_end + 7] + new_timeline + html[q3_next:]
            print("Added future story timeline milestones")
        else:
            print("WARN: Could not find story timeline insertion point")

# 4. Update the hero roadmap floating card to show more future items
html = html.replace(
    '<span class="wp-roadmap-text">Q3 2026 — Eco</span>',
    '<span class="wp-roadmap-text">Q4 2026 — Mainnet</span>'
)
# Add a 4th roadmap item in the floating card
html = html.replace(
    '<span class="wp-roadmap-text">Q4 2026 — Mainnet</span></div></div>',
    '<span class="wp-roadmap-text">Q4 2026 — Mainnet</span></div><div class="wp-roadmap-item"><div class="wp-roadmap-dot"></div><span class="wp-roadmap-text">2030 — Global Scale</span></div></div>'
)
print("Updated hero roadmap floating card")

# Write files
with open('/var/www/verdiscan/whitepaper/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('/opt/verdis-chain-rust/web/whitepaper/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# Verify
with open('/var/www/verdiscan/whitepaper/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

checks = [
    ('Phase 6' in content, 'Phase 6: AI Autonomous Governance'),
    ('Phase 7' in content, 'Phase 7: Cross-Chain Carbon Credits'),
    ('Phase 8' in content, 'Phase 8: ZK Rollup 10K TPS'),
    ('Phase 9' in content, 'Phase 9: DID & Green Certification'),
    ('Phase 10' in content, 'Phase 10: Global Green Finance'),
    ('Phase 11' in content, 'Phase 11: Planetary Carbon Dashboard'),
    ('Phase 12' in content, 'Phase 12: Carbon-Negative Planet'),
    ('Decentralized Identity' in content, 'Improvement: DID'),
    ('ZK Rollup Scaling' in content, 'Improvement: ZK Rollup'),
    ('Autonomous Carbon Verification' in content, 'Improvement: AI Carbon Verification'),
    ('Global Green Finance Integration' in content, 'Improvement: Green Finance'),
    ('IoT &amp; Oracle Network' in content, 'Improvement: IoT Oracles'),
    ('Developer Ecosystem' in content, 'Improvement: Dev Grants'),
    ('Q4 2026' in content, 'Story: Q4 2026 Mainnet'),
    ('2030 – 2035' in content, 'Story: 2030 Global Green Finance'),
    ('2035 – 2040' in content, 'Story: 2035 Carbon-Negative Planet'),
    ('Carbon-Negative Planet' in content, 'Vision: Carbon-Negative Planet'),
    ('1B+ tCO2e' in content, 'Vision: 1B tCO2e target'),
]
for ok, label in checks:
    print('OK' if ok else 'FAIL', ':', label)

print(f'\nTotal: {len(content)} bytes')
print(f'Roadmap phases: {content.count("rm-item")}')
print(f'Improvement items: {content.count("improve-item")}')
print(f'Story timeline items: {content.count("story-tl-item")}')
