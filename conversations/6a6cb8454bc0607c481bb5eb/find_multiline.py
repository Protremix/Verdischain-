#!/usr/bin/env python3
"""Find multiline single-quoted strings in explorer page."""
import re

with open('/var/www/verdiscan/explorer/index.html') as f:
    content = f.read()

scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
for i, s in enumerate(scripts):
    matches = list(re.finditer(r"'[^']*\n[^']*'", s))
    if matches:
        print("Script %d: %d multiline strings" % (i, len(matches)))
        for m in matches[:5]:
            start = max(0, m.start() - 40)
            end = min(len(s), m.end() + 40)
            print("  Context: ...%s..." % repr(s[start:end]))
