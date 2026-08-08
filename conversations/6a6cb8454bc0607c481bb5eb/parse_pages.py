import os
import re
import json
import httpx
from bs4 import BeautifulSoup

urls = {
    "page1_api": "https://verdischain.com/api/?nocache=50024",
    "page2_api_docs": "https://verdischain.com/api/docs/?nocache=50025",
    "page3_validator": "https://verdischain.com/validator/?nocache=50026",
    "page3_validators": "https://verdischain.com/validators/?nocache=50027"
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

for key, url in urls.items():
    r = httpx.get(url, headers=headers, follow_redirects=True)
    with open(f"{key}.html", "w", encoding="utf-8") as f:
        f.write(r.text)
    
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Extract links
    links = []
    for a in soup.find_all('a', href=True):
        links.append({'text': a.get_text(strip=True), 'href': a['href']})
    
    # Extract buttons
    buttons = [b.get_text(strip=True) for b in soup.find_all(['button', 'input'])]

    # Save details
    with open(f"{key}_parsed.json", "w", encoding="utf-8") as f:
        json.dump({
            'url': url,
            'title': soup.title.string if soup.title else None,
            'meta_description': soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={'name': 'description'}) else None,
            'links': links,
            'text': soup.get_text(separator='\n')
        }, f, indent=2, ensure_ascii=False)

print("Parsed all pages successfully.")
