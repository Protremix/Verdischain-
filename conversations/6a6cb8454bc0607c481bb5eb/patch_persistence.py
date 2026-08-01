#!/usr/bin/env python3
"""Patch persistence.js to save/restore AI Registry state"""

with open('/opt/verdis/app/dist/core/persistence.js') as f:
    content = f.read()

# Add AI Registry export to exportState
old_export_end = """        marketData: marketTracker ? marketTracker.exportData() : null,
    };
}"""

new_export_end = """        marketData: marketTracker ? marketTracker.exportData() : null,
        aiRegistry: aiRegistry ? aiRegistry.exportState() : null,
    };
}"""

if old_export_end in content:
    content = content.replace(old_export_end, new_export_end)
    print("1. Added AI Registry to exportState")
else:
    print("1. ERROR: export end not found")

# Update exportState function signature
old_export_sig = "function exportState(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker) {"
new_export_sig = "function exportState(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker, aiRegistry) {"
if old_export_sig in content:
    content = content.replace(old_export_sig, new_export_sig)
    print("2. Updated exportState signature")
else:
    print("2. ERROR: export signature not found")

# Update saveState function signature
old_save_sig = "function saveState(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker) {"
new_save_sig = "function saveState(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker, aiRegistry) {"
if old_save_sig in content:
    content = content.replace(old_save_sig, new_save_sig)
    print("3. Updated saveState signature")
else:
    print("3. ERROR: save signature not found")

# Update saveState call inside
old_save_call = "const state = exportState(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker);"
new_save_call = "const state = exportState(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker, aiRegistry);"
if old_save_call in content:
    content = content.replace(old_save_call, new_save_call)
    print("4. Updated saveState call")
else:
    print("4. ERROR: save call not found")

# Update startAutoSave signature
old_autosave = "function startAutoSave(blockchain, walletManager, ecoSystem, dex, contractManager, intervalMs = 30000, marketTracker) {"
new_autosave = "function startAutoSave(blockchain, walletManager, ecoSystem, dex, contractManager, intervalMs = 30000, marketTracker, aiRegistry) {"
if old_autosave in content:
    content = content.replace(old_autosave, new_autosave)
    print("5. Updated startAutoSave signature")
else:
    print("5. ERROR: autosave signature not found")

# Update autosave interval call
old_auto_call = "saveState(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker);"
new_auto_call = "saveState(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker, aiRegistry);"
if old_auto_call in content:
    content = content.replace(old_auto_call, new_auto_call)
    print("6. Updated autosave call")
else:
    print("6. ERROR: autosave call not found")

# Add AI Registry restore to restoreState
old_restore_end = """    console.log(`✅ State restored: ${state.chain.length} blocks, ${Object.keys(state.balances).length} balances, ${state.wallets.length} wallets, ${state.validators.length} validators, ${state.pools.length} DEX pools, ${state.contracts.length} contracts`);
}"""

new_restore_end = """    // Restore AI Registry
    if (state.aiRegistry && aiRegistry) {
        aiRegistry.importState(state.aiRegistry);
        console.log(`🤖 AI Registry restored: ${aiRegistry.getAllAgents().length} agents`);
    }
    console.log(`✅ State restored: ${state.chain.length} blocks, ${Object.keys(state.balances).length} balances, ${state.wallets.length} wallets, ${state.validators.length} validators, ${state.pools.length} DEX pools, ${state.contracts.length} contracts`);
}"""

if old_restore_end in content:
    content = content.replace(old_restore_end, new_restore_end)
    print("7. Added AI Registry restore")
else:
    print("7. ERROR: restore end not found")

# Update restoreState signature
old_restore_sig = "function restoreState(state, blockchain, walletManager, ecoSystem, dex, contractManager) {"
new_restore_sig = "function restoreState(state, blockchain, walletManager, ecoSystem, dex, contractManager, aiRegistry) {"
if old_restore_sig in content:
    content = content.replace(old_restore_sig, new_restore_sig)
    print("8. Updated restoreState signature")
else:
    print("8. ERROR: restore signature not found")

with open('/opt/verdis/app/dist/core/persistence.js', 'w') as f:
    f.write(content)
print("Persistence.js patched successfully!")
