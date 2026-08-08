from bs4 import BeautifulSoup

with open("dex_page.html") as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

scripts = soup.find_all('script')
for i, s in enumerate(scripts):
    print(f"=== SCRIPT {i} ===")
    if s.get('src'):
        print("SRC:", s.get('src'))
    else:
        print(s.text)
