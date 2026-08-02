#!/usr/bin/env python3
"""
Extract whitepaper content from whitepaper.html and create a print-friendly PDF version.
"""
import re

with open("/opt/verdis/app/dist/web/whitepaper.html", "r") as f:
    content = f.read()

# Extract all section content
sections_html = re.findall(r'<section[^>]*class="section-block"[^>]*>(.*?)</section>', content, re.DOTALL)

# Extract the title/subtitle
title_match = re.search(r'<h1[^>]*>(.*?)</h1>', content)
title = title_match.group(1) if title_match else "Verdis Protocol Whitepaper"

subtitle_match = re.search(r'<p[^>]*class="hero-subtitle"[^>]*>(.*?)</p>', content)
subtitle = subtitle_match.group(1) if subtitle_match else ""

# Build print-friendly HTML
print_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Verdis Protocol Whitepaper v2.0</title>
<style>
@page {{
  margin: 2cm;
  size: A4;
}}
* {{
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}}
body {{
  font-family: 'Georgia', 'Times New Roman', serif;
  color: #1a1a1a;
  background: white;
  line-height: 1.6;
  font-size: 12pt;
}}
h1 {{
  font-size: 24pt;
  color: #006633;
  text-align: center;
  margin-bottom: 8pt;
  page-break-after: avoid;
}}
h2 {{
  font-size: 16pt;
  color: #006633;
  margin-top: 24pt;
  margin-bottom: 8pt;
  page-break-after: avoid;
  border-bottom: 1px solid #006633;
  padding-bottom: 4pt;
}}
h3 {{
  font-size: 13pt;
  color: #333;
  margin-top: 16pt;
  margin-bottom: 6pt;
  page-break-after: avoid;
}}
p {{
  margin-bottom: 8pt;
  text-align: justify;
}}
ul, ol {{
  margin-left: 20pt;
  margin-bottom: 8pt;
}}
li {{
  margin-bottom: 4pt;
}}
code {{
  font-family: 'Courier New', monospace;
  background: #f5f5f5;
  padding: 1pt 4pt;
  border-radius: 2pt;
  font-size: 10pt;
}}
pre {{
  font-family: 'Courier New', monospace;
  background: #f5f5f5;
  padding: 10pt;
  border-radius: 4pt;
  font-size: 9pt;
  line-height: 1.4;
  white-space: pre-wrap;
  overflow-wrap: break-word;
  margin-bottom: 12pt;
}}
table {{
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 12pt;
  font-size: 10pt;
}}
th {{
  background: #006633;
  color: white;
  padding: 6pt;
  text-align: left;
}}
td {{
  border: 1px solid #ddd;
  padding: 6pt;
}}
tr:nth-child(even) {{
  background: #f9f9f9;
}}
strong {{
  color: #1a1a1a;
}}
.section-badge {{
  display: inline-block;
  background: #006633;
  color: white;
  width: 24pt;
  height: 24pt;
  border-radius: 50%;
  text-align: center;
  line-height: 24pt;
  font-size: 11pt;
  font-weight: bold;
  margin-right: 8pt;
}}
.section-header {{
  page-break-before: auto;
}}
.glass-card {{
  page-break-inside: avoid;
}}
.stats-grid {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10pt;
  margin-bottom: 12pt;
}}
.stat-card {{
  border: 1px solid #ddd;
  padding: 8pt;
  border-radius: 4pt;
  text-align: center;
}}
.stat-value {{
  font-size: 16pt;
  font-weight: bold;
  color: #006633;
  display: block;
}}
.stat-label {{
  font-size: 9pt;
  color: #666;
  display: block;
}}
.timeline-item {{
  border-left: 3pt solid #006633;
  padding-left: 12pt;
  margin-bottom: 12pt;
}}
.timeline-date {{
  font-weight: bold;
  color: #006633;
  font-size: 10pt;
}}
.timeline-title {{
  font-weight: bold;
  font-size: 12pt;
  margin: 4pt 0;
}}
.timeline-body {{
  font-size: 10pt;
  color: #444;
}}
.tag-green {{ color: #006633; font-weight: bold; }}
.tag-yellow {{ color: #cc8800; font-weight: bold; }}
.tag-teal {{ color: #006699; font-weight: bold; }}
.tag-blue {{ color: #666; font-size: 9pt; }}
.tech-para {{ margin-bottom: 8pt; }}
.tech-subsec {{
  font-size: 12pt;
  font-weight: bold;
  color: #006633;
  margin-top: 14pt;
  margin-bottom: 6pt;
}}
.tech-code-block {{
  font-family: 'Courier New', monospace;
  background: #f5f5f5;
  padding: 10pt;
  border-radius: 4pt;
  font-size: 9pt;
  line-height: 1.4;
  white-space: pre-wrap;
  margin-bottom: 12pt;
}}
.tech-diagram {{
  font-family: 'Courier New', monospace;
  font-size: 7pt;
  line-height: 1.2;
  white-space: pre;
  background: #f9f9f9;
  padding: 8pt;
  border-radius: 4pt;
  margin-bottom: 12pt;
}}
.tech-table {{
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 12pt;
  font-size: 10pt;
}}
.tech-spec-table {{
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 12pt;
  font-size: 10pt;
}}
.cmt {{ color: #666; }}
.kw {{ color: #0066cc; font-weight: bold; }}
.fn {{ color: #cc0066; }}
.str {{ color: #006600; }}
.cover {{
  text-align: center;
  padding-top: 100pt;
  page-break-after: always;
}}
.cover h1 {{
  font-size: 32pt;
  margin-bottom: 12pt;
}}
.cover .subtitle {{
  font-size: 14pt;
  color: #666;
  margin-bottom: 40pt;
}}
.cover .meta {{
  font-size: 11pt;
  color: #999;
}}
</style>
</head>
<body>

<div class="cover">
  <h1>Verdis Protocol</h1>
  <p class="subtitle">The Net Carbon-Negative Layer-1 Blockchain</p>
  <p class="meta">Whitepaper v2.0 — August 2026<br>
  Chain ID 909 · DPoS Consensus · 100B VRDX Max Supply<br>
  verdischain.com</p>
</div>

"""

# Process each section
for i, section in enumerate(sections_html, 1):
    # Clean up section HTML for print
    clean = section
    
    # Convert tech-para to regular paragraphs
    clean = re.sub(r'class="tech-para"', 'class="tech-para"', clean)
    
    # Remove links that would be broken in print
    clean = re.sub(r'<a[^>]*href="[^"]*"[^>]*>(.*?)</a>', r'\1', clean)
    
    # Remove inline styles that use CSS variables (won't work in print)
    clean = re.sub(r'style="color:var\([^)]*\)[^"]*"', '', clean)
    
    # Keep the section content
    print_html += f'<section>\n{clean}\n</section>\n\n'

# Add footer
print_html += """
<div style="margin-top: 40pt; text-align: center; color: #999; font-size: 9pt; border-top: 1px solid #ddd; padding-top: 10pt;">
<p>© 2026 Verdis Chain · The First Fully Green Blockchain Ecosystem</p>
<p>verdischain.com · @Verdischain · @verdischain</p>
<p>Whitepaper v2.0 — All rights reserved</p>
</div>

</body>
</html>
"""

# Write print-friendly HTML
with open("/tmp/whitepaper-print.html", "w") as f:
    f.write(print_html)

print(f"Print HTML created: {len(print_html)} chars, {len(sections_html)} sections")
