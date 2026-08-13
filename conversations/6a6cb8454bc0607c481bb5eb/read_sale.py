with open("sale_text.txt") as f:
    st = [line.strip() for line in f if line.strip()]

print("=== SALE LINE BY LINE ===")
for i, line in enumerate(st):
    print(f"{i:3d}: {line}")
