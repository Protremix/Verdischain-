import os

pages_dir = "/var/www/verdiscan"
landing = os.path.join(pages_dir, "index.html")

# 1. Add EvolvixOS ecosystem section to landing page
with open(landing, "r") as f:
    content = f.read()

ecosystem_section = """
<!-- ECOSYSTEM SECTION -->
<section style="max-width:1280px;margin:0 auto 64px;padding:0 24px">
  <div style="text-align:center;margin-bottom:48px">
    <div style="display:inline-block;padding:6px 16px;background:rgba(99,102,241,0.1);border:1px solid #6366f1;border-radius:100px;font-size:13px;color:#818cf8;font-weight:600;margin-bottom:16px">One Ecosystem</div>
    <h2 style="font-family:'Space Grotesk',sans-serif;font-size:32px;font-weight:700;margin-bottom:12px;color:#fff">Powered by <span style="color:#818cf8">EvolvixOS</span></h2>
    <p style="color:#888;font-size:17px;max-width:640px;margin:0 auto">Verdis Chain is the blockchain layer of the EvolvixOS ecosystem — an AI Engineering Operating System that builds, deploys, and secures software autonomously.</p>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;max-width:960px;margin:0 auto">
    <div style="background:#141414;border:1px solid #222;border-radius:16px;padding:32px">
      <div style="font-size:32px;margin-bottom:12px">⛓️</div>
      <h3 style="font-size:20px;font-weight:600;margin-bottom:8px;color:#fff">Verdis Chain</h3>
      <p style="color:#888;font-size:14px;margin-bottom:16px">Eco-friendly Layer-1 blockchain with DPoS consensus, AMM DEX, EVM, and carbon credits. The trust and value layer.</p>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <span style="background:#111;padding:4px 12px;border-radius:6px;font-size:12px;color:#caff33">Rust + Substrate</span>
        <span style="background:#111;padding:4px 12px;border-radius:6px;font-size:12px;color:#caff33">DPoS</span>
        <span style="background:#111;padding:4px 12px;border-radius:6px;font-size:12px;color:#caff33">AMM DEX</span>
      </div>
    </div>
    <div style="background:#141414;border:1px solid #222;border-radius:16px;padding:32px">
      <div style="font-size:32px;margin-bottom:12px">🧠</div>
      <h3 style="font-size:20px;font-weight:600;margin-bottom:8px;color:#fff">EvolvixOS</h3>
      <p style="color:#888;font-size:14px;margin-bottom:16px">AI Engineering OS with 5 autonomous agents that design, build, deploy, and secure software 24/7. The intelligence layer.</p>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <span style="background:#111;padding:4px 12px;border-radius:6px;font-size:12px;color:#818cf8">GPT-4o Powered</span>
        <span style="background:#111;padding:4px 12px;border-radius:6px;font-size:12px;color:#818cf8">5 AI Agents</span>
        <span style="background:#111;padding:4px 12px;border-radius:6px;font-size:12px;color:#818cf8">Auto-Deploy</span>
      </div>
    </div>
  </div>
  <div style="text-align:center;margin-top:32px">
    <a href="https://evolvixos.com" target="_blank" style="display:inline-block;padding:14px 32px;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;border-radius:8px;font-weight:600;text-decoration:none;font-size:15px">Explore EvolvixOS →</a>
  </div>
</section>
"""

if "ECOSYSTEM SECTION" not in content:
    footer_pos = content.rfind("<footer")
    if footer_pos > 0:
        content = content[:footer_pos] + ecosystem_section + "\n" + content[footer_pos:]
        with open(landing, "w") as f:
            f.write(content)
        print("✓ Added EvolvixOS ecosystem section to landing page")
    else:
        print("⚠ Could not find footer")
else:
    print("  Ecosystem section already exists")

# 2. Add EvolvixOS link to all page footers
for dir_name in os.listdir(pages_dir):
    index_file = os.path.join(pages_dir, dir_name, "index.html")
    if not os.path.isfile(index_file):
        continue
    with open(index_file, "r") as f:
        page_content = f.read()
    
    if "evolvixos.com" not in page_content:
        if "github.com/Protremix/Verdischain-" in page_content:
            page_content = page_content.replace(
                'github.com/Protremix/Verdischain-">GitHub</a>',
                'github.com/Protremix/Verdischain-">GitHub</a><a href="https://evolvixos.com">EvolvixOS</a>'
            )
            with open(index_file, "w") as f:
                f.write(page_content)
            print(f"✓ Added EvolvixOS link to {dir_name}")
        else:
            page_content = page_content.replace(
                "</footer>",
                '<div style="margin-top:12px"><a href="https://evolvixos.com" style="color:#818cf8;text-decoration:none;font-size:14px">EvolvixOS — AI Engineering OS</a></div></footer>'
            )
            with open(index_file, "w") as f:
                f.write(page_content)
            print(f"✓ Added EvolvixOS link to {dir_name} (footer)")

# 3. Verify
print("\n=== VERIFICATION ===")
for dir_name in sorted(os.listdir(pages_dir)):
    index_file = os.path.join(pages_dir, dir_name, "index.html")
    if os.path.isfile(index_file):
        with open(index_file, "r") as f:
            c = f.read()
        count = c.lower().count("evolvixos")
        has_link = "evolvixos.com" in c
        print(f"  {dir_name}: {count} mentions, link={'yes' if has_link else 'no'}")
