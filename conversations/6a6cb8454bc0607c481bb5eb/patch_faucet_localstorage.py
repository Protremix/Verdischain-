#!/usr/bin/env python3
"""Patch faucet to save tx to localStorage (shared with wallet)."""

with open('/var/www/verdiscan/faucet/index.html', 'r') as f:
    content = f.read()

# Add localStorage save right after the success alert in the faucet request
old = """      addHistory(addr, selectedToken, selectedToken === 'VRDX' ? 100 : 50, data.tx_hash || 'pending');
      alert('Success! ' + (selectedToken === 'VRDX' ? '100 VRDX' : '50 cVRDX') + ' sent to ' + addr.slice(0, 16) + '...\\n\\nTx Hash: ' + (data.tx_hash || 'pending').toString().slice(0, 20) + '...');"""

new = """      addHistory(addr, selectedToken, selectedToken === 'VRDX' ? 100 : 50, data.tx_hash || 'pending');
      // Save to shared localStorage for wallet history
      try {
        const history = JSON.parse(localStorage.getItem('verdis_tx_history') || '[]');
        history.push({
          hash: data.tx_hash || '',
          block: data.block_number || 0,
          type: 'received',
          signer: 'Faucet',
          dest: addr,
          method: 'Faucet Drip',
          value: (selectedToken === 'VRDX' ? '100.0000' : '50.0000') + ' ' + selectedToken
        });
        history.sort((a, b) => (b.block || 0) - (a.block || 0));
        if (history.length > 100) history.length = 100;
        localStorage.setItem('verdis_tx_history', JSON.stringify(history));
      } catch(e) {}
      alert('Success! ' + (selectedToken === 'VRDX' ? '100 VRDX' : '50 cVRDX') + ' sent to ' + addr.slice(0, 16) + '...\\n\\nTx Hash: ' + (data.tx_hash || 'pending').toString().slice(0, 20) + '...');"""

if old in content:
    content = content.replace(old, new, 1)
    with open('/var/www/verdiscan/faucet/index.html', 'w') as f:
        f.write(content)
    print("FAUCET PATCHED: Now saves tx to shared localStorage")
else:
    print("NOT FOUND: Could not locate faucet success handler")
