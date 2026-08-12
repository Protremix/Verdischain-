#!/usr/bin/env python3
"""Fix governance page: add Google Fonts link tag."""

with open('/var/www/verdiscan/governance/index.html', 'r') as f:
    content = f.read()

# Check if Google Fonts link already exists
if 'fonts.googleapis.com' in content:
    print('Google Fonts link already exists, no fix needed')
else:
    # Add Google Fonts preconnect and CSS link after the favicon link
    old_favicon = '<link rel="icon" href="/assets/favicon.ico" type="image/x-icon">'
    new_favicon = '''<link rel="icon" href="/assets/favicon.ico" type="image/x-icon">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">'''
    
    content = content.replace(old_favicon, new_favicon)
    
    with open('/var/www/verdiscan/governance/index.html', 'w') as f:
        f.write(content)
    print(f'Governance page fixed: added Google Fonts link ({len(content)} bytes)')
