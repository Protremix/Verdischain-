from bs4 import BeautifulSoup
import re

def parse_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
        
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text, soup

for fname in ['homepage.html', 'sale.html', 'tokenomics.html']:
    text, soup = parse_html(fname)
    print(f"=== {fname} ===")
    print(f"Title: {soup.title.string if soup.title else 'No title'}")
    print("Sample text (first 1000 chars):")
    print(text[:1000])
    print("\n" + "="*50 + "\n")
