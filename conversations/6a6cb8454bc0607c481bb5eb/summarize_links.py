import json

urls = ["docs", "blog", "developers", "download", "status"]

for name in urls:
    with open(f"dumps/{name}_info.json") as f:
        data = json.load(f)
    
    print(f"\n=================== {name.upper()} LINKS SUMMARY ===================")
    print(f"Total links/buttons found: {len(data['links'])}")
    for idx, l in enumerate(data['links']):
        txt = l.get('text', '').replace('\n', ' ')
        href = l.get('href')
        tag = l.get('tag')
        print(f"[{idx+1}] <{tag}> Text: '{txt[:40]}' | href: {href}")

