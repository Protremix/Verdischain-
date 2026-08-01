import re

with open("/opt/verdis/app/dist/web/token-sale.html", "r") as f:
    content = f.read()

# 1. Replace executePurchase with real IDO API call
old_execute = """    function executePurchase() {
      const payInput = parseFloat(document.getElementById('payAmountInput').value) || 0;
      if (payInput <= 0) {
        alert('Please enter a valid contribution amount.');
        return;
      }

      const walletAddr = document.getElementById('walletAddressInput').value.trim();
      if (!walletAddr) {
        toggleWalletModal();
        return;
      }

      const totalUSD = payInput * assetPriceUSD;
      const baseVCO = Math.floor(totalUSD / vrsPriceUSD);
      const bonusVCO = Math.floor(baseVCO * 0.10);
      const totalVCO = baseVCO + bonusVCO;
      const trees = Math.floor(totalUSD / 100);

      document.getElementById('receiptTxHash').innerText = '0x' + Array.from({length: 8}, () => Math.floor(Math.random()*16).toString(16)).join('') + '...' + Array.from({length: 4}, () => Math.floor(Math.random()*16).toString(16)).join('');
      document.getElementById('receiptVrsAmount').innerText = totalVCO.toLocaleString() + ' VCO';
      document.getElementById('receiptTrees').innerText = '🌱 ' + trees.toLocaleString() + ' Trees Planted';

      document.getElementById('receiptModal').classList.add('active');
    }"""

new_execute = """    async function executePurchase() {
      const payInput = parseFloat(document.getElementById('payAmountInput').value) || 0;
      if (payInput <= 0) {
        alert('Please enter a valid contribution amount.');
        return;
      }

      let walletAddr = document.getElementById('walletAddressInput').value.trim();
      
      // Check for Verdis wallet in localStorage (shared with dashboard)
      if (!walletAddr) {
        const savedWallet = localStorage.getItem('verdis-wallet');
        if (savedWallet) {
          try {
            const w = JSON.parse(savedWallet);
            walletAddr = w.address;
            document.getElementById('walletAddressInput').value = walletAddr;
            userWalletAddress = walletAddr;
            walletConnected = true;
            document.getElementById('walletBtnText').innerText = walletAddr.substring(0, 6) + '...' + walletAddr.slice(-4);
            document.getElementById('walletStatusText').innerText = 'Connected to Verdis Wallet ✅';
          } catch(e) {}
        }
      }
      
      if (!walletAddr) {
        toggleWalletModal();
        return;
      }

      const totalUSD = payInput * assetPriceUSD;
      const baseVCO = Math.floor(totalUSD / vrsPriceUSD);
      const bonusVCO = Math.floor(baseVCO * 0.10);
      const totalVCO = baseVCO + bonusVCO;

      // Call the real IDO API
      try {
        const response = await fetch('https://verdischain.com/api/ido/purchase', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            address: walletAddr,
            amountVCO: totalVCO.toString()
          })
        });
        const result = await response.json();
        
        if (result.success) {
          // Show real transaction receipt
          document.getElementById('receiptTxHash').innerText = result.txId ? result.txId.substring(0, 12) + '...' : 'Confirmed';
          document.getElementById('receiptVrsAmount').innerText = result.amountVCO.toLocaleString() + ' VCO';
          document.getElementById('receiptTrees').innerText = '🌱 ' + Math.floor(totalUSD / 100).toLocaleString() + ' Trees Planted';
          document.getElementById('receiptModal').classList.add('active');
          
          // Update wallet balance in localStorage
          const savedWallet = localStorage.getItem('verdis-wallet');
          if (savedWallet) {
            try {
              const w = JSON.parse(savedWallet);
              w.balance = result.newBalance;
              localStorage.setItem('verdis-wallet', JSON.stringify(w));
            } catch(e) {}
          }
        } else {
          alert('Purchase failed: ' + (result.error || 'Unknown error'));
        }
      } catch(e) {
        alert('Network error: ' + e.message);
      }
    }"""

if old_execute in content:
    content = content.replace(old_execute, new_execute)
    print("Replaced executePurchase with real IDO API call")
else:
    print("WARNING: Could not find executePurchase")

# 2. Replace connectWallet with real wallet options
old_connect = """    function connectWallet(providerName) {
      walletConnected = true;
      userWalletAddress = '0x71C' + Math.random().toString(16).substring(2, 8) + '...8A9e';
      document.getElementById('walletBtnText').innerText = '0x71C...8A9e';
      document.getElementById('walletAddressInput').value = userWalletAddress;
      document.getElementById('walletStatusText').innerText = 'Connected via ' + providerName + ' ✅';
      toggleWalletModal();
    }"""

new_connect = """    function connectWallet(providerName) {
      if (providerName === 'Verdis') {
        // Check for existing Verdis wallet in localStorage
        const savedWallet = localStorage.getItem('verdis-wallet');
        if (savedWallet) {
          try {
            const w = JSON.parse(savedWallet);
            walletConnected = true;
            userWalletAddress = w.address;
            document.getElementById('walletBtnText').innerText = w.address.substring(0, 6) + '...' + w.address.slice(-4);
            document.getElementById('walletAddressInput').value = w.address;
            document.getElementById('walletStatusText').innerText = 'Connected to Verdis Wallet ✅';
            toggleWalletModal();
            return;
          } catch(e) {}
        }
        // No wallet found — create one via the API
        fetch('https://verdischain.com/api/wallet/create', {method: 'POST'})
          .then(r => r.json())
          .then(d => {
            if (d.address) {
              const newWallet = {address: d.address, privateKey: d.privateKey, publicKey: d.publicKey, balance: 0};
              localStorage.setItem('verdis-wallet', JSON.stringify(newWallet));
              walletConnected = true;
              userWalletAddress = d.address;
              document.getElementById('walletBtnText').innerText = d.address.substring(0, 6) + '...' + d.address.slice(-4);
              document.getElementById('walletAddressInput').value = d.address;
              document.getElementById('walletStatusText').innerText = 'New Verdis Wallet created! ✅ Save your key from the dashboard.';
              toggleWalletModal();
            }
          })
          .catch(e => alert('Failed to create wallet: ' + e.message));
      } else {
        // For MetaMask/Trust, just use the address input
        walletConnected = true;
        userWalletAddress = '0x71C' + Math.random().toString(16).substring(2, 8) + '...8A9e';
        document.getElementById('walletBtnText').innerText = '0x71C...8A9e';
        document.getElementById('walletAddressInput').value = userWalletAddress;
        document.getElementById('walletStatusText').innerText = 'Connected via ' + providerName + ' (enter address manually)';
        toggleWalletModal();
      }
    }"""

if old_connect in content:
    content = content.replace(old_connect, new_connect)
    print("Replaced connectWallet with real wallet integration")
else:
    print("WARNING: Could not find connectWallet")

# 3. Add auto-restore of wallet on page load
old_body_end = "</body>"
wallet_restore = """    // Auto-restore Verdis wallet from localStorage
    (function() {
      const savedWallet = localStorage.getItem('verdis-wallet');
      if (savedWallet) {
        try {
          const w = JSON.parse(savedWallet);
          walletConnected = true;
          userWalletAddress = w.address;
          const btn = document.getElementById('walletBtnText');
          const inp = document.getElementById('walletAddressInput');
          const status = document.getElementById('walletStatusText');
          if(btn) btn.innerText = w.address.substring(0, 6) + '...' + w.address.slice(-4);
          if(inp) inp.value = w.address;
          if(status) status.innerText = 'Verdis Wallet connected ✅';
        } catch(e) {}
      }
    })();
    </body>"""

# Only replace the LAST </body>
idx = content.rfind("</body>")
if idx > -1:
    content = content[:idx] + wallet_restore
    print("Added wallet auto-restore on page load")

with open("/opt/verdis/app/dist/web/token-sale.html", "w") as f:
    f.write(content)

print("Token sale page updated with real IDO integration")
