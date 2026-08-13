import bs4

soup = bs4.BeautifulSoup(open("homepage.html").read(), 'html.parser')
for script in soup(["script", "style"]):
    script.decompose()

print("--- HOMEPAGE SECTIONS & HEADINGS ---")
for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'section', 'div'], class_=True):
    classes = " ".join(h.get('class', []))
    if any(k in classes for k in ['hero', 'section', 'card', 'stat', 'badge', 'feature', 'metric', 'banner', 'banner', 'footer', 'nav', 'token', 'sale', 'roadmap', 'faq']):
        text = h.get_text(" ", strip=True)
        if len(text) < 300:
            print(f"[{classes}] {text}")

