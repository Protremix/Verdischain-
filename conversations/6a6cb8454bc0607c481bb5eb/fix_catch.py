with open('/opt/verdis/app/dist/web/dashboard.html', 'r') as f:
    content = f.read()

# Find the catch block in loadSale and make it show the error
old = "  } catch(e) { console.warn('IDO info load failed', e); }"
new = "  } catch(e) {\n    console.warn('IDO info load failed', e);\n    var ee=document.getElementById('idoCurrentStage');\n    if(ee) ee.textContent='Error: '+e.message;\n  }"

if old in content:
    content = content.replace(old, new)
    print('Added visible error output to catch block')
else:
    # Try finding it with different whitespace
    idx = content.find("IDO info load failed")
    if idx >= 0:
        print(f'Found at position {idx}')
        print(f'Context: {repr(content[idx-60:idx+80])}')
        # Manual replacement
        start = content.rfind('} catch', 0, idx)
        end = content.find('}', idx)
        if start >= 0 and end >= 0:
            old_block = content[start:end+1]
            new_block = "} catch(e) {\n    console.warn('IDO info load failed', e);\n    var ee=document.getElementById('idoCurrentStage');\n    if(ee) ee.textContent='Error: '+e.message;\n  }"
            content = content[:start] + new_block + content[end+1:]
            print('Replaced via manual method')
    else:
        print('Could not find catch block at all')

with open('/opt/verdis/app/dist/web/dashboard.html', 'w') as f:
    f.write(content)
print('Saved')
