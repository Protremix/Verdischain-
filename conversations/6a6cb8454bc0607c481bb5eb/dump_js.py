from bs4 import BeautifulSoup

with open("whitepaper.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

scripts = soup.find_all('script')
print(f"Total <script> tags: {len(scripts)}")

for i, script in enumerate(scripts, 1):
    src = script.get('src')
    print(f"\n--- SCRIPT {i} (src={src}) ---")
    if script.string:
        print(script.string[:2000])

