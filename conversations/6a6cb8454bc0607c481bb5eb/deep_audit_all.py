from bs4 import BeautifulSoup
import json
import urllib.request
import urllib.parse
import re

pages = ["docs", "blog", "developers", "download", "status"]

def analyze_page(name):
    print(f"\n==================================================")
    print(f"       DEEP AUDIT FOR: {name.upper()}")
    print(f"==================================================")
    
    with open(f"dumps/{name}.html", "r", encoding="utf-8") as f:
        html = f.read()
    with open(f"dumps/{name}.txt", "r", encoding="utf-8") as f:
        text = f.read()
    with open(f"dumps/{name}_info.json", "r", encoding="utf-8") as f:
        info = json.load(f)

    soup = BeautifulSoup(html, "html.parser")
    
    print(f"Page Title: {info['title']}")
    print(f"Console Logs: {info['logs']}")
    print(f"Failed Requests: {info['failed_requests']}")
    
    # 1. Text Analysis (Search for common typos, weird strings, double words)
    typos = []
    text_lines = text.split('\n')
    for line_num, line in enumerate(text_lines):
        line_clean = line.strip()
        if not line_clean:
            continue
        # check double words like "the the", "in in", etc.
        m = re.search(r'\b([a-zA-A]{2,})\s+\1\b', line_clean, re.IGNORECASE)
        if m:
            typos.append(f"Repeated word '{m.group(0)}' in line: {line_clean}")
            
    print(f"\n--- POTENTIAL TYPOS & REPEATED WORDS ({len(typos)}) ---")
    for t in typos:
        print("  *", t)

    # 2. Extract code blocks & technical claims
    print("\n--- CODE BLOCKS & EXTERNAL LINKS ---")
    code_blocks = soup.find_all(['code', 'pre'])
    print(f"Found {len(code_blocks)} code/pre tags.")
    
    # 3. Inspect Navigation & Footer links
    nav_links = soup.select('nav a, header a')
    footer_links = soup.select('footer a')
    print(f"Header/Nav Links: {len(nav_links)}, Footer Links: {len(footer_links)}")

for p in pages:
    analyze_page(p)

