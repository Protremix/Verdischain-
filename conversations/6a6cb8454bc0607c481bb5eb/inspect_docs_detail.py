from bs4 import BeautifulSoup
import re

soup = BeautifulSoup(open("dumps/docs.html", "r", encoding="utf-8"), "html.parser")

print("=== DOCS METADATA & HEADERS ===")
print("Title:", soup.title.string if soup.title else None)

# Check Header & Nav
nav = soup.find('nav') or soup.find('header')
print("Nav HTML:", nav.prettify() if nav else "No nav found")

# Check H1 and title text
h1 = soup.find('h1')
print("H1 text:", repr(h1.get_text()) if h1 else "No H1")
print("H1 outerHTML:", h1 if h1 else "No H1")

# Check all sections and headings
sections = soup.find_all(class_='docs-section')
print(f"Total docs sections: {len(sections)}")

for sec in sections:
    sec_id = sec.get('id')
    h2 = sec.find('h2')
    h2_text = h2.get_text() if h2 else "NO H2"
    print(f"\nSection ID: '{sec_id}' | H2: '{h2_text}'")
    
    # Check text content for typos or numbers
    ps = sec.find_all(['p', 'li', 'td', 'code'])
    sec_text = " ".join([p.get_text() for p in ps])
    
    # Check code snippets
    codes = sec.find_all('code')
    for c in codes:
        code_str = c.get_text()
        # look for fake URLs or endpoints
        urls = re.findall(r'https?://[^\s\'"]+', code_str)
        if urls:
            print(f"  Code URLs: {urls}")

