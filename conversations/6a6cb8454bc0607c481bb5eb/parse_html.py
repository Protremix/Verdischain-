from bs4 import BeautifulSoup
import json

with open("dex_page.html") as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print("=== SCRIPTS ON PAGE ===")
scripts = soup.find_all('script')
for i, s in enumerate(scripts):
    src = s.get('src')
    if src:
        print(f"Script {i} src: {src}")
    else:
        print(f"Script {i} inline (length {len(s.text)}):")
        print(s.text[:500])
        print("...")

print("\n=== SECTIONS & TABS ===")
tabs = soup.find_all(class_=['tab-btn', 'tab-content', 'dex-tab', 'tab-pane'])
for t in tabs:
    print(t.get('id'), t.get('class'), t.text[:100].strip())

print("\n=== MAIN DEX CONTAINERS ===")
containers = soup.find_all(class_=['dex-container', 'dex-grid', 'dex-card', 'card', 'dex-section', 'section'])
for c in containers:
    print(c.get('id'), c.get('class'))

