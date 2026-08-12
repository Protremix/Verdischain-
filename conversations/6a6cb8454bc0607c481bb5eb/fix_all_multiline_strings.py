#!/usr/bin/env python3
"""Fix multiline single-quoted strings in all Verdis Chain pages."""

import os, re, glob

fixed = []
for page_path in sorted(glob.glob('/var/www/verdiscan/*/index.html')):
    page_name = os.path.basename(os.path.dirname(page_path))
    with open(page_path, 'r') as f:
        content = f.read()
    
    original = content
    
    # Fix multiline strings in <script> blocks
    def fix_script(match):
        script = match.group(1)
        lines = script.split('\n')
        result = []
        in_single_quote = False
        for line in lines:
            if in_single_quote:
                stripped = line.lstrip()
                if result:
                    result[-1] = result[-1] + stripped
                else:
                    result.append(stripped)
                # Check if this line closes the quote
                temp = stripped.replace("\\'", "")
                if temp.count("'") % 2 == 1:
                    in_single_quote = False
            else:
                result.append(line)
                # Check if this line opens an unclosed single quote
                temp = line.replace("\\'", "")
                if temp.count("'") % 2 == 1:
                    in_single_quote = True
        return '<script>' + '\n'.join(result) + '</script>'
    
    content = re.sub(r'<script>(.*?)</script>', fix_script, content, flags=re.DOTALL)
    
    if content != original:
        with open(page_path, 'w') as f:
            f.write(content)
        fixed.append(page_name)

print("Fixed %d pages: %s" % (len(fixed), ", ".join(fixed)))
