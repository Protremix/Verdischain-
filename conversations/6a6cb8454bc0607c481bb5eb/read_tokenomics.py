with open("tokenomics_text.txt") as f:
    tt = [line.strip() for line in f if line.strip()]

print("=== TOKENOMICS LINE BY LINE ===")
for i, line in enumerate(tt):
    print(f"{i:3d}: {line}")
