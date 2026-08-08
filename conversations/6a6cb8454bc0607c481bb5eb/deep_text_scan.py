import re
from bs4 import BeautifulSoup

with open("whitepaper.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Extract clean paragraphs and text
text_blocks = []
for p in soup.find_all(['p', 'td', 'th', 'li', 'span', 'div']):
    # Only get leaf or near-leaf elements to get distinct sentences
    if len(p.find_all(['p', 'div'])) == 0:
        t = p.get_text().strip()
        if t and len(t) > 5:
            text_blocks.append(t)

print(f"Total text elements extracted: {len(text_blocks)}")

# Search for typos / spelling issues / grammar / strange phrasing
# Common blockchain/tech typos, missing words, punctuation errors, duplicated words

print("\n=== SEARCHING FOR TYPOS & GRAMMAR ISSUES ===")
for b in text_blocks:
    # double spaces or weird punctuation
    if re.search(r'\b(\w+)\s+\1\b', b, re.IGNORECASE):
        print("DUPLICATE WORD:", b)
    if re.search(r'\s[,.\?!]', b):
        print("SPACE BEFORE PUNCTUATION:", b)
    if '  ' in b:
        print("DOUBLE SPACE:", b)

