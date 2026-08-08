with open("/tmp/sale_page.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    print(f"{i+1:4d}: {line}", end='')
