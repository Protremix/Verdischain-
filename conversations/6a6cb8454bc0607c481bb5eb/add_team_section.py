#!/usr/bin/env python3
"""Add team section to whitepaper.html on the Verdis Chain server."""

TEAM_HTML = """
  <!-- TEAM SECTION -->
  <section id="team" class="page-section" style="background: #ffffff; border-top: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0;">
    <div class="section-header reveal">
      <span class="section-tag">Leadership</span>
      <h2 class="section-title">The Verdischain Team</h2>
      <p class="section-desc">A multidisciplinary team combining blockchain engineering, environmental industry expertise, product strategy, and legal compliance.</p>
    </div>

    <div style="max-width: 1000px; margin: 0 auto; display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px;">

      <!-- CEO -->
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 28px; transition: transform 0.2s ease-out, box-shadow 0.2s ease-out;" class="reveal">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div style="width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg, #00a86b, #00ff88); display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 700; color: #fff;">DJ</div>
          <div>
            <h3 style="font-size: 18px; font-weight: 700; color: #0f172a; margin: 0;">Dorian Jean</h3>
            <span style="font-size: 13px; color: #00a86b; font-weight: 600;">CEO &amp; Founder</span>
          </div>
        </div>
        <p style="font-size: 14px; line-height: 1.6; color: #475569; margin: 0;">CEO of Verdischain and owner of Shilat18 Ltd, specializing in recycling of eco-products. With 10+ years in the eco-products and recycling industry, Dorian brings practical knowledge of sustainable technologies, circular-economy principles, and environmentally focused business development. Leads strategic direction, business development, partnerships, and ecosystem expansion.</p>
      </div>

      <!-- CTO -->
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 28px; transition: transform 0.2s ease-out, box-shadow 0.2s ease-out;" class="reveal">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div style="width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg, #0066cc, #00aaff); display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 700; color: #fff;">MJ</div>
          <div>
            <h3 style="font-size: 18px; font-weight: 700; color: #0f172a; margin: 0;">Mark Jamestown</h3>
            <span style="font-size: 13px; color: #00a86b; font-weight: 600;">CTO / Lead Blockchain Engineer</span>
          </div>
        </div>
        <p style="font-size: 14px; line-height: 1.6; color: #475569; margin: 0;">Responsible for blockchain architecture, Substrate runtime development, consensus, security, infrastructure, and core protocol development. Leads the technical development of the Verdischain Layer-1 architecture and the engineering direction of the blockchain protocol.</p>
      </div>

      <!-- Head of Product -->
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 28px; transition: transform 0.2s ease-out, box-shadow 0.2s ease-out;" class="reveal">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div style="width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg, #8b5cf6, #a78bfa); display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 700; color: #fff;">EJ</div>
          <div>
            <h3 style="font-size: 18px; font-weight: 700; color: #0f172a; margin: 0;">Elizabeth Jefferson</h3>
            <span style="font-size: 13px; color: #00a86b; font-weight: 600;">Head of Product</span>
          </div>
        </div>
        <p style="font-size: 14px; line-height: 1.6; color: #475569; margin: 0;">Responsible for product strategy, ecosystem development, wallet, explorer, and user experience. Oversees Verdischain user-facing products and ecosystem services, with a focus on creating accessible tools for users, developers, validators, and ecosystem participants.</p>
      </div>

      <!-- Community & Marketing -->
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 28px; transition: transform 0.2s ease-out, box-shadow 0.2s ease-out;" class="reveal">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div style="width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg, #f59e0b, #fbbf24); display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 700; color: #fff;">RG</div>
          <div>
            <h3 style="font-size: 18px; font-weight: 700; color: #0f172a; margin: 0;">Rojs Gordons</h3>
            <span style="font-size: 13px; color: #00a86b; font-weight: 600;">Community &amp; Marketing</span>
          </div>
        </div>
        <p style="font-size: 14px; line-height: 1.6; color: #475569; margin: 0;">Responsible for community growth, communications, marketing, and ecosystem partnerships. Leads community and communications strategy, focusing on ecosystem awareness, developer outreach, community development, strategic communications, and partnerships.</p>
      </div>

      <!-- Legal Counsel -->
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 28px; transition: transform 0.2s ease-out, box-shadow 0.2s ease-out; grid-column: 1 / -1;" class="reveal">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div style="width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg, #64748b, #94a3b8); display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 700; color: #fff;">MM</div>
          <div>
            <h3 style="font-size: 18px; font-weight: 700; color: #0f172a; margin: 0;">Maria Dolores Marquez de Prado</h3>
            <span style="font-size: 13px; color: #00a86b; font-weight: 600;">Legal Counsel</span>
          </div>
        </div>
        <p style="font-size: 14px; line-height: 1.6; color: #475569; margin: 0;">Advises Verdischain on corporate structure, blockchain regulatory matters, token-related legal considerations, and commercial agreements. Graduated in Law from the Complutense University of Madrid, entered the Judicial Career through competitive examination, and subsequently joined the Fiscal Career. Served as a prosecutor in the Provincial Court of Guipuzcoa before joining the Prosecutor's Office of the National Court, where she remained for 17+ years. In 1999, appointed Prosecutor of the Supreme Court until 2007. Specializes in civil proceedings concerning breaches of honour and criminal defence of cases involving insult and slander. Author of publications on substantive and procedural criminal law.</p>
      </div>

      <!-- Legal & Compliance Advisor -->
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 28px; transition: transform 0.2s ease-out, box-shadow 0.2s ease-out; grid-column: 1 / -1;" class="reveal">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div style="width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg, #475569, #64748b); display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 700; color: #fff;">IM</div>
          <div>
            <h3 style="font-size: 18px; font-weight: 700; color: #0f172a; margin: 0;">Ignacio Martinez-Arrieta</h3>
            <span style="font-size: 13px; color: #00a86b; font-weight: 600;">Legal &amp; Compliance Advisor</span>
          </div>
        </div>
        <p style="font-size: 14px; line-height: 1.6; color: #475569; margin: 0;">Member of the Madrid Bar Association since 2010. Graduated in Law from the Complutense University of Madrid and the University of Paris 1 Pantheon-Sorbonne in Spanish-French Law. Completed a Master's in European Union Law (Competition Law) at the Institut d'Etudes Europeennes (ULB) in Brussels, and a Master's in Economic Criminal Law at Rey Juan Carlos University. Holds CESCOM Compliance certification and is a member of ASCOM's Registry of Compliance Experts. Previously worked as legal adviser in the European Parliament and in the Economic Criminal Law department of Berliner Corcoran &amp; Rowe LLP in Washington, D.C. Specializes in representing legal entities in complex criminal proceedings, money laundering offences, compliance programs, and internal investigations.</p>
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

print("Team section added to whitepaper successfully")
