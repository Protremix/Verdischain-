import re
import os

pages = {
    "Homepage": "/var/www/verdiscan/index.html",
    "Sale": "/var/www/verdiscan/sale/index.html",
    "Tokenomics": "/var/www/verdiscan/tokenomics/index.html",
    "Whitepaper": "/var/www/verdiscan/whitepaper/index.html"
}

required_nav_items = ["Verdiscan", "DEX", "Whitepaper", "Wallet", "Sale", "Tokenomics", "Faucet"]
required_footer_items = ["Home", "Explorer", "DEX", "Whitepaper", "Wallet", "Sale", "Tokenomics", "Faucet", "Validators", "Eco", "Docs", "Governance", "GitHub"]

for name, path in pages.items():
    print("="*100)
    print(f"DETAILED AUDIT: {name} ({path})")
    print("="*100)
    
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # 1. LOGO
    print("\n--- 1. LOGO ---")
    nav_match = re.search(r'<(nav|header)[^>]*>(.*?)</\1>', html, re.DOTALL | re.IGNORECASE)
    nav_html = nav_match.group(0) if nav_match else ""
    logos_in_nav = re.findall(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', nav_html, re.IGNORECASE)
    all_logos = re.findall(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*logo[^>]*>', html, re.IGNORECASE)
    print(f"Logo in nav: {logos_in_nav}")
    print(f"All logo imgs: {all_logos}")

    # 2. FOOTER
    print("\n--- 2. FOOTER ---")
    footer_match = re.search(r'<footer[^>]*>(.*?)</footer>', html, re.DOTALL | re.IGNORECASE)
    if not footer_match:
        print("FOOTER MISSING!")
    else:
        f_html = footer_match.group(1)
        f_links = re.findall(r'<a[^>]+href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', f_html, re.DOTALL | re.IGNORECASE)
        f_link_dict = {}
        for href, text in f_links:
            clean_text = re.sub(r'<[^>]+>', '', text).strip()
            if clean_text:
                f_link_dict[clean_text] = href
        
        print("Footer links present:")
        for k, v in f_link_dict.items():
            print(f"  {k} -> {v}")
            
        missing_f = [item for item in required_footer_items if not any(item.lower() in k.lower() for k in f_link_dict.keys())]
        print(f"Missing required footer links (expected {required_footer_items}): {missing_f}")

    # 3. NAV
    print("\n--- 3. NAV ---")
    if not nav_match:
        print("NAV MISSING!")
    else:
        n_links = re.findall(r'<a[^>]+href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', nav_html, re.DOTALL | re.IGNORECASE)
        n_link_dict = {}
        for href, text in n_links:
            clean_text = re.sub(r'<[^>]+>', '', text).strip()
            if clean_text:
                n_link_dict[clean_text] = href
        
        print("Nav links present:")
        for k, v in n_link_dict.items():
            print(f"  {k} -> {v}")
            
        missing_n = [item for item in required_nav_items if not any(item.lower() in k.lower() for k in n_link_dict.keys())]
        print(f"Missing required nav links (expected {required_nav_items}): {missing_n}")

    # 4. TEXT & DATA
    print("\n--- 4. TEXT & DATA ---")
    # Ticker: look for instances of VERDIS used as ticker (not "Verdis Chain")
    # e.g., "100 VERDIS", "VERDIS token", "per VERDIS", "(VERDIS)"
    verdis_as_ticker = re.findall(r'(\b\d+\s*VERDIS\b|\bVERDIS\b\s*(?:token|price|tokens|coin|ticker|balance|powers|\(VRDX\)))', html, re.IGNORECASE)
    print(f"VERDIS used as ticker/token name: {verdis_as_ticker}")
    
    # Check all VERDIS vs VRDX occurrences
    verdis_all = re.findall(r'\bVERDIS\b', html)
    vrdx_all = re.findall(r'\bVRDX\b', html)
    print(f"Total 'VERDIS' word count: {len(verdis_all)}, Total 'VRDX' word count: {len(vrdx_all)}")

    # Check supply mentions
    supply_lines = [line.strip() for line in html.split('\n') if any(w in line.lower() for w in ['supply', '100b', '100 billion', '100,000,000,000'])]
    print("Supply lines:")
    for sl in supply_lines[:10]:
        print(f"  {sl[:120]}")

    # Check decimal mentions
    decimal_lines = [line.strip() for line in html.split('\n') if 'decimal' in line.lower()]
    print("Decimal lines:")
    for dl in decimal_lines[:10]:
        print(f"  {dl[:120]}")

    # Check links and broken links
    all_hrefs = re.findall(r'href=["\']([^"\']+)["\']', html, re.IGNORECASE)
    print(f"Total hrefs: {len(all_hrefs)}")
    internal_hrefs = [h for h in all_hrefs if h.startswith('/')]
    print(f"Internal links sample: {list(set(internal_hrefs))[:15]}")

    # 5. DESIGN
    print("\n--- 5. DESIGN ---")
    # CSS Variables
    style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL | re.IGNORECASE)
    style_text = "\n".join(style_blocks)
    
    bg1_match = re.findall(r'--bg-1\s*:\s*([^;}\n]+)', html)
    bg2_match = re.findall(r'--bg-2\s*:\s*([^;}\n]+)', html)
    accent_match = re.findall(r'--accent\s*:\s*([^;}\n]+)', html)
    print(f"CSS vars -> --bg-1: {bg1_match}, --bg-2: {bg2_match}, --accent: {accent_match}")

    # Check template signature or gradient-ui-ux reference / classes
    has_gradient_ui_ux = "gradient-ui-ux" in html or "gradient" in html
    print(f"Contains 'gradient-ui-ux' or 'gradient': {has_gradient_ui_ux}")

    # 3D floating UI cluster
    has_cluster = any(k in html.lower() for k in ['floating', 'cluster', '3d', 'hero-cluster', 'hero-ui'])
    print(f"Mentions 3D / floating / cluster / hero UI elements: {has_cluster}")

    # Hardcoded colors in styles
    hardcoded_hex = re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}\b', style_text)
    print(f"Hardcoded hex colors in <style> block count: {len(hardcoded_hex)} (Unique: {set(hardcoded_hex)})")

