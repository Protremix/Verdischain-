import json

with open("audit_summary.json", "r") as f:
    data = json.load(f)

for item in data:
    print("==================================================")
    print(f"PAGE: {item['path']} ({item['title']})")
    print(f"External Scripts: {item['external_scripts']}")
    print(f"Fetches: {item['fetches']}")
    print(f"XHRs: {item['xhrs']}")
    print(f"WebSockets: {item['wss']}")
    print(f"API Vars: {item['api_vars']}")
    print(f"URLs in Script: {item['urls_in_script']}")
    print(f"Hardcoded Notes: {item['hardcoded_notes']}")
