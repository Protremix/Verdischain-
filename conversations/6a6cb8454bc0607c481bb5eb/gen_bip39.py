with open('/tmp/bip39_words.txt') as f:
    words = [w.strip() for w in f.readlines() if w.strip()]

lines = ["// BIP39 Standard English Word List (2048 words)",
         "const List<String> BIP39_WORDS = ["]
for w in words:
    lines.append('  "' + w + '",')
lines.append("];")

with open('/opt/verdis-wallet/mobile/lib/services/bip39_words.dart', 'w') as f:
    f.write('\n'.join(lines) + '\n')

print(f"Created bip39_words.dart with {len(words)} words")
