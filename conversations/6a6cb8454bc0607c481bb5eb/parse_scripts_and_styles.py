from bs4 import BeautifulSoup

with open('page.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print("=== INLINE SCRIPTS ===")
for i, script in enumerate(soup.find_all('script')):
    if script.string:
        print(f"--- Script {i} ---")
        print(script.string)
    elif script.get('src'):
        print(f"--- External Script {i}: {script.get('src')} ---")

print("\n=== INLINE STYLES ===")
for i, style in enumerate(soup.find_all('style')):
    if style.string:
        print(f"--- Style {i} (len: {len(style.string)}) ---")
        # print first 500 chars
        print(style.string[:500])
        print("...")

