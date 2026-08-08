from bs4 import BeautifulSoup

with open('faucet.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

styles = soup.find_all('style')
print(f"Total style tags: {len(styles)}")
for i, s in enumerate(styles):
    print(f"=== STYLE {i+1} ===")
    print(s.string)
