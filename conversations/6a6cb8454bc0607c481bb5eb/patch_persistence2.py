#!/usr/bin/env python3
"""Add Name Service, Fraud Detection, and Account Abstraction to persistence"""

with open('/opt/verdis/app/dist/core/persistence.js') as f:
    content = f.read()

# Add to exportState
old_export = "aiRegistry: aiRegistry ? aiRegistry.exportState() : null,\n    };"
new_export = """aiRegistry: aiRegistry ? aiRegistry.exportState() : null,
        nameService: nameService ? nameService.exportState() : null,
        fraudDetection: fraudDetection ? fraudDetection.exportState() : null,
        accountAbstraction: accountAbstraction ? accountAbstraction.exportState() : null,
    };"""
if old_export in content:
    content = content.replace(old_export, new_export)
    print("1. Added to exportState")
else:
    print("1. ERROR: export pattern not found")

# Update exportState signature
old = "function exportState(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker, aiRegistry) {"
new = "function exportState(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker, aiRegistry, nameService, fraudDetection, accountAbstraction) {"
if old in content:
    content = content.replace(old, new)
    print("2. Updated exportState signature")
else:
    print("2. ERROR: export signature not found")

# Update saveState signature
old = "function saveState(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker, aiRegistry) {"
new = "function saveState(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker, aiRegistry, nameService, fraudDetection, accountAbstraction) {"
if old in content:
    content = content.replace(old, new)
    print("3. Updated saveState signature")
else:
    print("3. ERROR: save signature not found")

# Update saveState inner call
old = "const state = exportState(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker, aiRegistry);"
new = "const state = exportState(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker, aiRegistry, nameService, fraudDetection, accountAbstraction);"
if old in content:
    content = content.replace(old, new)
    print("4. Updated saveState call")
else:
    print("4. ERROR: save call not found")

# Update startAutoSave signature
old = "function startAutoSave(blockchain, walletManager, ecoSystem, dex, contractManager, intervalMs = 30000, marketTracker, aiRegistry) {"
new = "function startAutoSave(blockchain, walletManager, ecoSystem, dex, contractManager, intervalMs = 30000, marketTracker, aiRegistry, nameService, fraudDetection, accountAbstraction) {"
if old in content:
    content = content.replace(old, new)
    print("5. Updated startAutoSave signature")
else:
    print("5. ERROR: autosave signature not found")

# Update autosave inner call
old = "saveState(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker, aiRegistry);"
new = "saveState(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker, aiRegistry, nameService, fraudDetection, accountAbstraction);"
if old in content:
    content = content.replace(old, new)
    print("6. Updated autosave call")
else:
    print("6. ERROR: autosave call not found")

# Add restore for new modules
old_restore = """    // Restore AI Registry
    if (state.aiRegistry && aiRegistry) {
        aiRegistry.importState(state.aiRegistry);
        console.log(`🤖 AI Registry restored: ${aiRegistry.getAllAgents().length} agents`);
    }"""
new_restore = """    // Restore AI Registry
    if (state.aiRegistry && aiRegistry) {
        aiRegistry.importState(state.aiRegistry);
        console.log(`🤖 AI Registry restored: ${aiRegistry.getAllAgents().length} agents`);
    }
    // Restore Name Service
    if (state.nameService && nameService) {
        nameService.importState(state.nameService);
        console.log(`🌐 Name Service restored: ${nameService.getStats().totalNames} names`);
    }
    // Restore Fraud Detection
    if (state.fraudDetection && fraudDetection) {
        fraudDetection.importState(state.fraudDetection);
        console.log(`🛡️ Fraud Detection restored: ${fraudDetection.getStats().totalAlerts} alerts`);
    }
    // Restore Account Abstraction
    if (state.accountAbstraction && accountAbstraction) {
        accountAbstraction.importState(state.accountAbstraction);
        console.log(`🔐 Account Abstraction restored: ${accountAbstraction.getStats().totalSmartWallets} smart wallets`);
    }"""
if old_restore in content:
    content = content.replace(old_restore, new_restore)
    print("7. Added restore for new modules")
else:
    print("7. ERROR: restore pattern not found")

# Update restoreState signature
old = "function restoreState(state, blockchain, walletManager, ecoSystem, dex, contractManager, aiRegistry) {"
new = "function restoreState(state, blockchain, walletManager, ecoSystem, dex, contractManager, aiRegistry, nameService, fraudDetection, accountAbstraction) {"
if old in content:
    content = content.replace(old, new)
    print("8. Updated restoreState signature")
else:
    print("8. ERROR: restore signature not found")

with open('/opt/verdis/app/dist/core/persistence.js', 'w') as f:
    f.write(content)
print("Persistence patched!")
