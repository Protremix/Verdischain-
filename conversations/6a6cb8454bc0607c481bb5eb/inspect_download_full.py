from bs4 import BeautifulSoup
import json
import urllib.request
import urllib.parse
import ssl

html = open("dumps/download.html", "r", encoding="utf-8").read()
soup = BeautifulSoup(html, "html.parser")

print("=== DOWNLOAD PAGE ANALYSIS ===")

# Check all download links / buttons / binaries
links = soup.find_all('a')
print(f"Total links on Download page: {len(links)}")

for a in links:
    href = a.get('href')
    text = a.get_text(strip=True)
    if 'verdis' in text.lower() or 'download' in text.lower() or 'apk' in href.lower() or 'tar' in href.lower() or 'exe' in href.lower() or 'zip' in href.lower():
        print(f"Download Link: text='{text}' | href='{href}'")

# Check all versions, checksums, hashes, system requirements
print("\n--- CHECKSUMS, VERSIONS & FILE SIZES IN TEXT ---")
for el in soup.find_all(['div', 'p', 'code', 'span', 'li']):
    txt = el.get_text(strip=True)
    if any(k in txt for k in ['SHA-256', 'sha256', 'v1.', 'v2.', 'MB', 'GB', 'checksum', 'Checksum']):
        print(f"Text snippet: {txt[:120]}")

