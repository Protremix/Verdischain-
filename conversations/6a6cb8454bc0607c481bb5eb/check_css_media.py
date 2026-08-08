from bs4 import BeautifulSoup

with open('page.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

styles = soup.find_all('style')
for s in styles:
    text = s.get_text()
    for line in text.split('}'):
        if '@media' in line or 'max-width' in line:
            print(line.strip())
            print("---")

