import json

with open('audit_results.json') as f:
    data = json.load(f)

print("--- NAV LINKS ---")
for n in data['nav_links']:
    print(n)

print("\n--- CANVAS DESKTOP ---")
print(json.dumps(data['canvas_desktop'], indent=2))

print("\n--- CANVAS MOBILE ---")
print(json.dumps(data['canvas_mobile'], indent=2))

print("\n--- HERO CARDS ---")
for c in data['hero_cards']:
    print(c)

print("\n--- CONSOLE LOGS DESKTOP ---")
for l in data['desktop_console']:
    print(l)

print("\n--- CONSOLE LOGS MOBILE ---")
for l in data['mobile_console']:
    print(l)

