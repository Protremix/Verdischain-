import json

with open('suite_results.json') as f:
    res = json.load(f)

print("=== PALLET OCCURRENCES ===")
for p in res['pallet_occurrences']:
    print(f"- Text: '{p['text']}' | Parent context: '{p['parentContext'][:120]}'")

print("\n=== TOP NAV DESKTOP ===")
for nav in res['top_nav_desktop']:
    print(f"[{nav['text']}] -> {nav['href']} (visible: {nav['visible']})")

print("\n=== TOP NAV MOBILE ===")
for nav in res['top_nav_mobile']:
    print(f"[{nav['text']}] -> {nav['href']} (visible: {nav['visible']})")

print("\n=== MOBILE CANVAS ===")
print(json.dumps(res['mobile_canvas'], indent=2))

print("\n=== LINK CHECKS ===")
for l in res['link_check']:
    print(f"[{l['status']}] {l['text']} --> {l['url']} (error: {l['error']})")

