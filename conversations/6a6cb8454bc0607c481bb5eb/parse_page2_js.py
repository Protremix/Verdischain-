from bs4 import BeautifulSoup
import json
import re

with open("page2_api_docs.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

scripts = soup.find_all('script')
js_code = ""
for s in scripts:
    if s.string and "endpoints" in s.string:
        js_code = s.string

print(f"JS code length: {len(js_code)}")

# Save JS code to file for inspection
with open("page2_script.js", "w", encoding="utf-8") as f:
    f.write(js_code)

# How many endpoints are defined in the JS array?
endpoints_matches = re.findall(r"\{g:'([^']+)',n:'([^']+)',m:'([^']+)'", js_code)
print(f"Total endpoints defined in array: {len(endpoints_matches)}")

# Count by group
groups = {}
for g, n, m in endpoints_matches:
    groups[g] = groups.get(g, 0) + 1

print("\nEndpoint counts by group:")
for g, count in groups.items():
    print(f"  {g}: {count}")

print(f"Total count = {sum(groups.values())}")
