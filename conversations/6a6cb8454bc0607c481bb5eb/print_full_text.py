from bs4 import BeautifulSoup

with open('page.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

# Remove script and style tags
for tag in soup(['script', 'style']):
    tag.extract()

text = soup.get_text(separator='\n')
lines = [line.strip() for line in text.splitlines() if line.strip()]
print("\n".join(lines))
