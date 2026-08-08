import re
from bs4 import BeautifulSoup

with open("page_content.html") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
style_tag = soup.find('style')
css = style_tag.string if style_tag else ""

print("=== CSS ANALYSIS ===")
print("CSS length:", len(css))

# Check for variables used vs defined
defined_vars = set(re.findall(r'(--[a-zA-Z0-9-]+)\s*:', css))
used_vars = set(re.findall(r'var\((--[a-zA-Z0-9-]+)\)', css))

print("Defined CSS Variables:", sorted(list(defined_vars)))
print("Used CSS Variables:", sorted(list(used_vars)))

missing_vars = used_vars - defined_vars
print("Missing CSS Variables (used but not defined):", missing_vars)

# Check classes defined in HTML vs CSS
html_classes = set()
for tag in soup.find_all(True):
    if tag.get('class'):
        for c in tag['class']:
            html_classes.add(c)

print("\nHTML Classes used:", sorted(list(html_classes)))

# Check for classes in HTML that have no CSS rules
css_classes = set(re.findall(r'\.([a-zA-Z0-9_-]+)', css))
print("Classes in CSS:", sorted(list(css_classes)))

missing_css_rules = html_classes - css_classes
print("\nHTML classes with no direct CSS class selector:", sorted(list(missing_css_rules)))

