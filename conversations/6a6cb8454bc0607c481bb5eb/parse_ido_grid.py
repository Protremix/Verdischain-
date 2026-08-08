from bs4 import BeautifulSoup

with open('page.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

ido_section = soup.find(text=lambda t: t and 'Investor Allocation Breakdown' in t)
if ido_section:
    parent = ido_section.find_parent('section') or ido_section.find_parent('div')
    print("IDO Section HTML:")
    print(parent.prettify())
else:
    print("IDO section heading not found")

