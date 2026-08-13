#!/usr/bin/env python3
"""Add team section to whitepaper using EXISTING whitepaper CSS classes only."""

TEAM_HTML = """
  <!-- TEAM SECTION -->
  <section id="team" class="page-section" style="background: #ffffff; border-top: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0;">
    <div class="section-header reveal">
      <span class="section-tag">Leadership</span>
      <h2 class="section-title">The Verdischain Team</h2>
      <p class="section-desc">A multidisciplinary team combining blockchain engineering, environmental industry expertise, product strategy, and legal compliance.</p>
    </div>

    <div class="vesting-grid">
      <div class="vest-card reveal">
        <div class="vest-header">
          <span class="vest-title">Dorian Jean</span>
          <span class="vest-badge">CEO &amp; Founder</span>
        </div>
        <p class="vest-details">CEO of Verdischain and owner of Shilat18 Ltd, specializing in recycling of eco-products. With 10+ years in the eco-products and recycling industry, Dorian brings practical knowledge of sustainable technologies, circular-economy principles, and environmentally focused business development. Leads strategic direction, business development, partnerships, and ecosystem expansion.</p>
      </div>

      <div class="vest-card reveal">
        <div class="vest-header">
          <span class="vest-title">Mark Jamestown</span>
          <span class="vest-badge">CTO / Lead Engineer</span>
        </div>
        <p class="vest-details">Responsible for blockchain architecture, Substrate runtime development, consensus, security, infrastructure, and core protocol development. Leads the technical development of the Verdischain Layer-1 architecture and the engineering direction of the blockchain protocol.</p>
      </div>

      <div class="vest-card reveal">
        <div class="vest-header">
          <span class="vest-title">Elizabeth Jefferson</span>
          <span class="vest-badge">Head of Product</span>
        </div>
        <p class="vest-details">Responsible for product strategy, ecosystem development, wallet, explorer, and user experience. Oversees Verdischain user-facing products and ecosystem services, with a focus on creating accessible tools for users, developers, validators, and ecosystem participants.</p>
      </div>
    </div>

    <div class="vesting-grid" style="margin-top: 24px;">
      <div class="vest-card reveal">
        <div class="vest-header">
          <span class="vest-title">Rojs Gordons</span>
          <span class="vest-badge">Co-Founder &amp; Marketing</span>
        </div>
        <p class="vest-details">Responsible for community growth, communications, marketing, and ecosystem partnerships. Leads community and communications strategy, focusing on ecosystem awareness, developer outreach, community development, strategic communications, and partnerships.</p>
      </div>

      <div class="vest-card reveal">
        <div class="vest-header">
          <span class="vest-title">Maria Dolores Marquez de Prado</span>
          <span class="vest-badge">Legal Counsel</span>
        </div>
        <p class="vest-details">Advises Verdischain on corporate structure, blockchain regulatory matters, token-related legal considerations, and commercial agreements. Graduated in Law from the Complutense University of Madrid. Served as prosecutor in the Provincial Court of Guipuzcoa and the National Court for 17+ years. Appointed Prosecutor of the Supreme Court (1999-2007). Specializes in civil proceedings concerning breaches of honour and criminal defence of insult and slander cases. Author of publications on criminal law.</p>
      </div>

      <div class="vest-card reveal">
        <div class="vest-header">
          <span class="vest-title">Ignacio Martinez-Arrieta</span>
          <span class="vest-badge">Legal &amp; Compliance</span>
        </div>
        <p class="vest-details">Member of the Madrid Bar Association since 2010. Graduated in Law from the Complutense University of Madrid and University of Paris 1 Pantheon-Sorbonne. Master's in EU Law (Competition Law) from ULB Brussels, and Master's in Economic Criminal Law from Rey Juan Carlos University. CESCOM Compliance certified. Previously legal adviser in the European Parliament and Berliner Corcoran &amp; Rowe LLP, Washington D.C. Specializes in complex criminal proceedings, money laundering compliance, and internal investigations.</p>
      </div>
    </div>
  </section>

"""

with open("/opt/verdis-chain-rust/web/whitepaper.html", "r") as f:
    content = f.read()

cta_marker = "  <!-- CTA SECTION -->"
content = content.replace(cta_marker, TEAM_HTML + cta_marker)

with open("/opt/verdis-chain-rust/web/whitepaper.html", "w") as f:
    f.write(content)

print("Team section added using existing whitepaper CSS classes")
