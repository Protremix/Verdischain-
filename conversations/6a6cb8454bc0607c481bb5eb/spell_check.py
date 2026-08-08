from bs4 import BeautifulSoup
import re

with open("/tmp/sale_page.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

text = soup.get_text()

# Check for specific suspicious words or typos
words = re.findall(r'\b[A-Za-z]+\b', text)
print(f"Total words: {len(words)}")

# Look for common typos or double spaces or weird punctuation
print("\n--- Checking for potential typos or punctuation issues ---")
for line in text.split('\n'):
    line_clean = line.strip()
    if line_clean:
        if '  ' in line_clean:
            print("Double space:", line_clean)
        # check for uncapitalized sentences or oddities
