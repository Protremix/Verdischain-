#!/usr/bin/env python3
"""Fix the broken faucet JS - template literal inside regular string"""

with open('/var/www/verdiscan/faucet/index.html', 'r') as f:
    lines = f.readlines()

fixed = False
for i, line in enumerate(lines):
    if 'addHistory(addr, selectedToken' in line and 'alert' in line:
        # Replace the broken line with two proper lines
        lines[i] = "      addHistory(addr, selectedToken, selectedToken === 'VRDX' ? 100 : 50, data.tx_hash || 'pending');\n"
        # Insert the alert on the next line using string concatenation
        lines.insert(i+1, "      alert('Success! ' + (selectedToken === 'VRDX' ? '100 VRDX' : '50 cVRDX') + ' sent to ' + addr.slice(0, 16) + '...\\n\\nTx Hash: ' + (data.tx_hash || 'pending').toString().slice(0, 20) + '...');\n")
        fixed = True
        print(f'Fixed broken line at line {i+1}')
        break

if fixed:
    with open('/var/www/verdiscan/faucet/index.html', 'w') as f:
        f.writelines(lines)
    print('Faucet JS fixed successfully')
else:
    # Try alternate search
    for i, line in enumerate(lines):
        if 'addHistory' in line and 'alert' in line:
            print(f'Found at line {i+1}: {line[:200]}')
    print('Could not auto-fix - showing relevant lines for manual review')
