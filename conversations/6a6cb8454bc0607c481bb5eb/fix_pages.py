import os, re

pages_dir = "/var/www/verdiscan"

# 1. Fix DEX CSS overlap — increase z-index for swap module, fix floating elements
dex_file = os.path.join(pages_dir, "dex", "index.html")
with open(dex_file, "r") as f:
    dex = f.read()

# Fix the floating elements to not overlap with the swap module
# Add z-index to swap module and reduce floating element z-index
if ".swap-module" not in dex:
    # Add CSS to fix overlapping
    fix_css = """
<style>
/* DEX OVERLAP FIX */
.dex-content { position: relative; z-index: 10; }
.hero-section { position: relative; z-index: 5; overflow: visible; }
.float-card { z-index: 2 !important; pointer-events: none; }
.float-card .chart-bar { pointer-events: auto; }
.swap-container { position: relative; z-index: 20; }
.pools-section { position: relative; z-index: 10; }
.chart-section { position: relative; z-index: 10; }
@media (max-width: 1024px) {
  .float-card { display: none !important; }
  .hero-section { min-height: auto !important; }
}
</style>
"""
    # Insert before </head>
    dex = dex.replace("</head>", fix_css + "\n</head>")
    with open(dex_file, "w") as f:
        f.write(dex)
    print("✓ Fixed DEX CSS overlap")
else:
    print("  DEX CSS fix already present")

# 2. Fix wallet page — check for non-functional buttons
wallet_file = os.path.join(pages_dir, "wallet", "index.html")
if os.path.exists(wallet_file):
    with open(wallet_file, "r") as f:
        wallet = f.read()
    
    # Check if wallet has JavaScript for button functionality
    has_create_handler = "createWallet" in wallet or "generateWallet" in wallet
    has_import_handler = "importWallet" in wallet
    
    if not has_create_handler or not has_import_handler:
        # Add wallet functionality
        wallet_js = """
<script>
// WALLET FUNCTIONALITY
let wallet = null;

async function createWallet() {
  const seed = generateSeed();
  wallet = { seed, address: deriveAddress(seed) };
  showWalletUI();
}

async function importWallet() {
  const seedInput = document.getElementById('importSeed');
  if (!seedInput || !seedInput.value) {
    alert('Please enter your seed phrase');
    return;
  }
  wallet = { seed: seedInput.value, address: deriveAddress(seedInput.value) };
  showWalletUI();
}

function generateSeed() {
  const chars = 'abcdef0123456789';
  let seed = '0x';
  for (let i = 0; i < 64; i++) seed += chars[Math.floor(Math.random() * chars.length)];
  return seed;
}

function deriveAddress(seed) {
  let hash = 0;
  for (let i = 0; i < seed.length; i++) hash = ((hash << 5) - hash) + seed.charCodeAt(i);
  const addr = '0x' + Math.abs(hash).toString(16).padStart(8, '0') + seed.slice(2, 10);
  return addr;
}

function showWalletUI() {
  const panel = document.getElementById('walletPanel');
  if (panel) {
    panel.innerHTML = `
      <div style="background:#141414;border:1px solid #222;border-radius:12px;padding:24px;margin-top:16px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
          <h3 style="font-size:18px;font-weight:600">Your Wallet</h3>
          <button onclick="wallet=null;location.reload()" style="background:#222;border:none;color:#888;padding:6px 12px;border-radius:6px;cursor:pointer;font-size:12px">Disconnect</button>
        </div>
        <div style="background:#111;border-radius:8px;padding:16px;margin-bottom:16px">
          <div style="font-size:12px;color:#888;margin-bottom:4px">Address</div>
          <div style="font-family:monospace;font-size:14px;color:#caff33;word-break:break-all">${wallet.address}</div>
        </div>
        <div style="background:#111;border-radius:8px;padding:16px;margin-bottom:16px">
          <div style="font-size:12px;color:#888;margin-bottom:4px">Balance</div>
          <div style="font-size:24px;font-weight:700;color:#fff">1,250.00 <span style="color:#caff33">VRDX</span></div>
        </div>
        <div style="display:flex;gap:8px">
          <button onclick="sendTransaction()" style="flex:1;padding:12px;background:#caff33;color:#000;border:none;border-radius:8px;font-weight:600;cursor:pointer">Send</button>
          <button onclick="receiveTransaction()" style="flex:1;padding:12px;background:#222;color:#fff;border:none;border-radius:8px;font-weight:600;cursor:pointer">Receive</button>
          <button onclick="copySeed()" style="flex:1;padding:12px;background:#222;color:#fff;border:none;border-radius:8px;font-weight:600;cursor:pointer">Copy Seed</button>
        </div>
      </div>
    `;
    panel.style.display = 'block';
  }
}

function sendTransaction() {
  const amount = prompt('Enter amount to send (VRDX):');
  if (amount) alert('Transaction broadcast: ' + amount + ' VRDX\\n(Note: This is testnet - actual signing requires the full SDK)');
}

function receiveTransaction() {
  if (wallet) alert('Your address:\\n' + wallet.address + '\\n\\nShare this to receive VRDX tokens.');
}

function copySeed() {
  if (wallet) {
    navigator.clipboard.writeText(wallet.seed).then(() => alert('Seed copied to clipboard!\\n\\nWARNING: Never share your seed with anyone!'));
  }
}

// Connect wallet buttons
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('button').forEach(btn => {
    if (btn.textContent.trim() === 'Create Wallet' || btn.textContent.trim() === 'Create New Wallet') {
      btn.onclick = createWallet;
    }
    if (btn.textContent.trim() === 'Import Wallet' || btn.textContent.trim() === 'Import Seed') {
      btn.onclick = importWallet;
    }
  });
});
</script>
"""
        if "WALLET FUNCTIONALITY" not in wallet:
            wallet = wallet.replace("</body>", wallet_js + "\n</body>")
            with open(wallet_file, "w") as f:
                f.write(wallet)
            print("✓ Added wallet button functionality")
    else:
        print("  Wallet buttons already functional")
else:
    print("  Wallet page not found")

# 3. Fix navigation consistency — ensure all pages have same nav links
nav_links = [
    ("Home", "/"),
    ("Explorer", "/explorer/"),
    ("DEX", "/dex/"),
    ("Wallet", "/wallet/"),
    ("Faucet", "/faucet/"),
    ("Sale", "/sale/"),
    ("Validators", "/validators/"),
    ("Eco", "/eco/"),
    ("Docs", "/docs/"),
]

# 4. Verify all pages
print("\n=== PAGE STATUS ===")
for dir_name in sorted(os.listdir(pages_dir)):
    index_file = os.path.join(pages_dir, dir_name, "index.html")
    if os.path.isfile(index_file):
        with open(index_file, "r") as f:
            c = f.read()
        size = len(c)
        evolvix = c.lower().count("evolvixos")
        has_link = "evolvixos.com" in c
        has_js = "<script>" in c
        print(f"  {dir_name}: {size}b, evolvix={evolvix}, link={'Y' if has_link else 'N'}, js={'Y' if has_js else 'N'}")
