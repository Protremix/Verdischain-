import re
from bs4 import BeautifulSoup

with open('page_source.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

text_content = soup.get_text()

print("=== SEARCHING TICKERS AND NAMES ===")
tickers = set(re.findall(r'\b[A-Z]{3,5}\b', text_content))
print("All uppercase 3-5 letter words/tickers found:", sorted(list(tickers)))

print("\n=== SPECIFIC TICKER MENTIONS ===")
for match in re.finditer(r'(.{0,30}(VRD|VRDX|VERDIS|Substrate|BABE|GRANDPA).{0,30})', text_content):
    print(match.group(0).strip())

print("\n=== PLACEHOLDER / HARDCODED DEMO TEXT ===")
placeholder_words = ['lorem', 'ipsum', 'todo', 'test', 'alex', 'vance', '0x7f', 'example', 'placeholder', 'demo']
for p in placeholder_words:
    matches = list(re.finditer(re.escape(p), text_content, re.IGNORECASE))
    if matches:
        print(f"Found placeholder word '{p}': {len(matches)} occurrences")
        for m in matches[:5]:
            start = max(0, m.start() - 30)
            end = min(len(text_content), m.end() + 30)
            print("  Context:", text_content[start:end].replace('\n', ' '))

