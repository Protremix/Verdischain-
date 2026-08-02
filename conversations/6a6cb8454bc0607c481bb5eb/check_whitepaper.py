import re

with open('/opt/verdis/app/dist/web/whitepaper.html', 'r') as f:
    content = f.read()

# Find all section numbers and titles
sections = re.findall(r'section-(\d+).*?section-title">(.*?)<', content)
print(f'Total sections: {len(sections)}')

for i, (num, title) in enumerate(sections):
    # Get section content
    start = content.find(f'section-{num}"')
    if i + 1 < len(sections):
        end = content.find(f'section-{sections[i+1][0]}"')
    else:
        end = len(content)
    
    if start >= 0 and end > start:
        section_text = content[start:end]
        garbled = re.findall(r'andwithbyet|witheewith|inandt|etowith|ineandean|tforandand', section_text)
        if garbled:
            print(f'  Section {num}: {title} — GARBLED ({len(garbled)} instances)')
        else:
            print(f'  Section {num}: {title} — OK')
