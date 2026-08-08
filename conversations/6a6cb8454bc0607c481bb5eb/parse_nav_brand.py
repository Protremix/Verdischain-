from bs4 import BeautifulSoup

with open('page.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

nav_brand = soup.find('a', class_='nav-brand')
if nav_brand:
    print(nav_brand.prettify())

