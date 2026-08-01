#!/usr/bin/env python3
import re, sys

with open("/tmp/whitepaper.html", errors="replace") as f:
    html = f.read()

for i in range(16, 21):
    sid = "section-" + str(i)
    start = html.find('id="' + sid + '"')
    if start == -1:
        print("Section " + str(i) + ": NOT FOUND")
        continue
    h2_start = html.find("<h2", start)
    h2_end = html.find("</h2>", h2_start) + 5
    title = re.sub(r"<[^>]+>", "", html[h2_start:h2_end]).strip()
    
    next_id = 'id="section-' + str(i+1) + '"'
    next_sec = html.find(next_id, h2_end)
    if next_sec == -1:
        next_sec = len(html)
    content_html = html[h2_end:next_sec]
    content_text = re.sub(r"<[^>]+>", "", content_html).strip()
    
    print("\n=== Section " + str(i) + ": " + title + " ===")
    print("Text length: " + str(len(content_text)) + " chars")
    print(content_text[:1200])
    print("...")
