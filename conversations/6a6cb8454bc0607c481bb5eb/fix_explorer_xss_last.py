#!/usr/bin/env python3
"""Fix last 2 unescaped patterns."""

PATH = "/var/www/verdiscan/explorer/index.html"

with open(PATH, "r") as f:
    h = f.read()

r = 0

# Line 2212: ext.signer in "From:" display
old = "From: '+ext.signer+'</div>'"
new = "From: '+escapeHtml(ext.signer)+'</div>'"
if old in h:
    h = h.replace(old, new)
    r += 1
    print("Fixed: ext.signer in From: display")

# Line 2211: ext.hash in "Hash:" display
old = "Hash: '+ext.hash+'</div>'"
new = "Hash: '+escapeHtml(ext.hash)+'</div>'"
if old in h:
    h = h.replace(old, new)
    r += 1
    print("Fixed: ext.hash in Hash: display")

with open(PATH, "w") as f:
    f.write(h)

print(f"Total: {r} fixes")
