import json

with open('deep_report.json') as f:
    d = json.load(f)

print("=== BODY TEXT SAMPLE ===")
print(d['body_text'][:2000])

print("\n=== PALLETS MENTION ===")
text = d['body_text'].lower()
if 'pallet' in text:
    for line in d['body_text'].split('\n'):
        if 'pallet' in line.lower():
            print("  FOUND LINE:", line)
else:
    print("  NO PALLET MENTION FOUND IN BODY TEXT")

print("\n=== NAV ELEMENTS ===")
for nav in d['nav_elements']:
    print(nav['text'], "-->", nav['href'])

print("\n=== ALL LINKS ===")
unique_links = {}
for l in d['all_links']:
    unique_links[l['href']] = l['text']
for href, txt in unique_links.items():
    print(f"[{txt}] -> {href}")

print("\n=== CANVASES DESKTOP ===")
print(json.dumps(d['canvases_d'], indent=2))

print("\n=== CANVASES MOBILE ===")
print(json.dumps(d['canvases_m'], indent=2))

print("\n=== DESKTOP ERRORS & CONSOLE ===")
print("Errors:", d['d_errors'])
print("Console:", d['d_console'])

print("\n=== MOBILE ERRORS & CONSOLE ===")
print("Errors:", d['m_errors'])
print("Console:", d['m_console'])

