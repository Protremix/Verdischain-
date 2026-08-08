from bs4 import BeautifulSoup
import re

with open('page.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

for s in soup(['script', 'style']):
    s.extract()

text = soup.get_text()
# Split sentences
sentences = [s.strip() for s in re.split(r'[.\n]', text) if s.strip()]

print(f"Total sentence fragments: {len(sentences)}")
for s in sentences:
    # Print sentences containing common grammar/spelling targets or unusual words
    words = re.findall(r'\b[A-Za-z]+\b', s)
    # Check for duplicate words
    for i in range(len(words)-1):
        if words[i].lower() == words[i+1].lower() and len(words[i]) > 1:
            print(f"DUPLICATE WORD in: '{s}' -> '{words[i]} {words[i+1]}'")

