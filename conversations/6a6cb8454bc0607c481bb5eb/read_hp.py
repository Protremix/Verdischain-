with open("homepage_text.txt") as f:
    hp = [line.strip() for line in f if line.strip()]

print("=== HOMEPAGE LINE BY LINE ===")
for i, line in enumerate(hp):
    print(f"{i:3d}: {line}")
