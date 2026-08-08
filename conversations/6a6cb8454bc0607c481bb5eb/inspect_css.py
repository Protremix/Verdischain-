from bs4 import BeautifulSoup
import re

with open("whitepaper.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Get all style blocks
styles = [style.string for style in soup.find_all('style') if style.string]
full_css = "\n".join(styles)

print("Full CSS length:", len(full_css))

print("\n--- Font sizes in CSS ---")
# Regex for CSS blocks
blocks = re.findall(r'([^{]+)\{([^}]+)\}', full_css)
for sel, body in blocks:
    sel = sel.strip()
    if 'font-size' in body:
        fs_match = re.search(r'font-size:\s*([^;]+)', body)
        fs = fs_match.group(1).strip() if fs_match else ''
        if any(k in sel for k in ['hero', 'title', 'heading', 'h1', 'h2', 'h3', 'card', 'body', 'btn', 'nav', 'stat', 'badge']):
            print(f"  {sel} -> font-size: {fs}")

