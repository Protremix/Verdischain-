from bs4 import BeautifulSoup
import re

with open("page1_api.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# Get text lines
text_lines = [line.strip() for line in soup.get_text().split("\n") if line.strip()]

print(f"Total non-empty text lines in Page 1: {len(text_lines)}")
for i, line in enumerate(text_lines):
    print(f"{i:03d}: {line}")
