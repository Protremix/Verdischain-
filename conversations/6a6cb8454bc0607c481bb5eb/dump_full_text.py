from bs4 import BeautifulSoup

with open("whitepaper.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Print readable text section by section
for i, section in enumerate(soup.find_all(['section', 'div', 'header', 'footer']), 1):
    # Select main top-level containers
    sec_id = section.get('id', '')
    sec_class = ' '.join(section.get('class', []))
    if sec_id or 'section' in sec_class or 'hero' in sec_class or 'footer' in sec_class:
        print(f"\n==================== CONTAINER: id='{sec_id}' class='{sec_class}' ====================")
        text = section.get_text(separator=' ', strip=True)
        # Avoid printing huge duplicated text from parent elements by checking direct depth or limiting
        print(text[:1500] + ("..." if len(text) > 1500 else ""))

