import os
import re
from bs4 import BeautifulSoup

base_dir = "./verdiscan_audit/var/www/verdiscan"

pages = [
    ("1. Blog", "blog/index.html"),
    ("2. Developers", "developers/index.html"),
    ("3. Download", "download/index.html"),
    ("4. Contact", "contact/index.html"),
    ("5. Referral", "referral/index.html"),
    ("6. Incentives", "incentives/index.html"),
    ("7. Disclaimer", "legal/disclaimer.html"),
    ("8. Privacy", "legal/privacy.html"),
    ("9. Terms", "legal/terms.html"),
    ("10. 404", "404/index.html"),
    ("11. Token Sale", "token-sale/index.html"),
]

for name, rel_path in pages:
    filepath = os.path.join(base_dir, rel_path)
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    print(f"\n==================================================")
    print(f"PAGE DETAILS: {name}")
    print(f"==================================================")

    # Headings
    headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])]
    print(f"Headings (top 10): {headings[:10]}")

    # Specific text searches
    # 1. Supply
    supply_contexts = []
    for match in re.finditer(r'([^.\n]*?(?:supply|100b|100,000,000,000|650m|tokenomics)[^.\n]*?\.)', html, re.IGNORECASE):
        supply_contexts.append(match.group(1).strip())
    if supply_contexts:
        print(f"Supply/Tokenomics context snippets: {supply_contexts[:5]}")

    # 2. Decimals
    decimal_contexts = []
    for match in re.finditer(r'([^.\n]*?decimal[^.\n]*?\.)', html, re.IGNORECASE):
        decimal_contexts.append(match.group(1).strip())
    print(f"Decimals context snippets: {decimal_contexts}")

    # 3. Prices
    price_contexts = []
    for match in re.finditer(r'([^.\n]*?(?:\$\d+|\d+\s*USDT|price)[^.\n]*?\.)', html, re.IGNORECASE):
        price_contexts.append(match.group(1).strip())
        if len(price_contexts) >= 5:
            break
    print(f"Price context snippets: {price_contexts}")

    # 4. Token ticker / Symbol usage
    ticker_contexts = []
    for match in re.finditer(r'([^.\n]*?(?:VRDX|VERDIS)[^.\n]*?\.)', html):
        ticker_contexts.append(match.group(1).strip())
        if len(ticker_contexts) >= 5:
            break
    print(f"Ticker context snippets (top 5): {ticker_contexts}")

    # 5. Form action / APIs / JS
    forms = soup.find_all('form')
    form_info = [(f.get('action'), f.get('method')) for f in forms]
    print(f"Forms: {form_info}")

    scripts = soup.find_all('script')
    script_srcs = [s.get('src') for s in scripts if s.get('src')]
    inline_script_snippet = [s.get_text()[:100] for s in scripts if not s.get('src')]
    print(f"Script srcs: {script_srcs}")
    print(f"Inline scripts snippet count: {len(inline_script_snippet)}")

