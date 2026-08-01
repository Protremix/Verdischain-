#!/usr/bin/env python3
"""Update index.js persistence calls to pass new modules"""

with open('/opt/verdis/app/dist/index.js') as f:
    content = f.read()

# Update restoreState call
old = '(0, persistence_1.restoreState)(savedState, blockchain, walletManager, ecoSystem, dex, contractManager, aiRegistry);'
new = '(0, persistence_1.restoreState)(savedState, blockchain, walletManager, ecoSystem, dex, contractManager, aiRegistry, nameService, fraudDetection, accountAbstraction);'
if old in content:
    content = content.replace(old, new)
    print("1. Updated restoreState call")
else:
    print("1. ERROR: restore call not found")

# Update initial saveState call
old = '(0, persistence_1.saveState)(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker, aiRegistry);'
new = '(0, persistence_1.saveState)(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker, aiRegistry, nameService, fraudDetection, accountAbstraction);'
if old in content:
    content = content.replace(old, new, 1)
    print("2. Updated initial saveState call")
else:
    print("2. ERROR: initial save not found")

# Update block production saveState
old = '(0, persistence_1.saveState)(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker, aiRegistry);\n        // Record prices every 5 blocks'
new = '(0, persistence_1.saveState)(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker, aiRegistry, nameService, fraudDetection, accountAbstraction);\n        // Record prices every 5 blocks'
if old in content:
    content = content.replace(old, new)
    print("3. Updated block production saveState")
else:
    print("3. ERROR: block save not found")

# Update startAutoSave call
old = '(0, persistence_1.startAutoSave)(blockchain, walletManager, ecoSystem, dex, contractManager, 30000, marketTracker, aiRegistry);'
new = '(0, persistence_1.startAutoSave)(blockchain, walletManager, ecoSystem, dex, contractManager, 30000, marketTracker, aiRegistry, nameService, fraudDetection, accountAbstraction);'
if old in content:
    content = content.replace(old, new)
    print("4. Updated startAutoSave call")
else:
    print("4. ERROR: autosave not found")

with open('/opt/verdis/app/dist/index.js', 'w') as f:
    f.write(content)
print("index.js persistence calls updated!")
