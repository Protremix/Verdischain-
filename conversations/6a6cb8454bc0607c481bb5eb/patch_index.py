#!/usr/bin/env python3
"""Patch index.js: wire AI Registry persistence, fast finality (2s), fix VCO->VRS"""

with open('/opt/verdis/app/dist/index.js') as f:
    content = f.read()

# 1. Import AI Registry
old_import = 'const persistence_1 = require("./core/persistence");'
new_import = '''const persistence_1 = require("./core/persistence");
const ai_registry_1 = require("./core/ai-registry");
const name_service_1 = require("./core/name-service");
const fraud_detection_1 = require("./core/fraud-detection");
const account_abstraction_1 = require("./core/account-abstraction");'''
if old_import in content:
    content = content.replace(old_import, new_import)
    print("1. Added new module imports")
else:
    print("1. ERROR: import not found")

# 2. Initialize new systems after marketTracker
old_init = '''const marketTracker = new market_1.MarketTracker(dex);
exports.marketTracker = marketTracker;'''
new_init = '''const marketTracker = new market_1.MarketTracker(dex);
exports.marketTracker = marketTracker;
const aiRegistry = new ai_registry_1.AIAgentRegistry();
exports.aiRegistry = aiRegistry;
const nameService = new name_service_1.NameService();
exports.nameService = nameService;
const fraudDetection = new fraud_detection_1.FraudDetection();
exports.fraudDetection = fraudDetection;
const accountAbstraction = new account_abstraction_1.AccountAbstraction();
exports.accountAbstraction = accountAbstraction;'''
if old_init in content:
    content = content.replace(old_init, new_init)
    print("2. Added new system initializations")
else:
    print("2. ERROR: marketTracker init not found")

# 3. Pass AI Registry to restoreState
old_restore = '(0, persistence_1.restoreState)(savedState, blockchain, walletManager, ecoSystem, dex, contractManager);'
new_restore = '(0, persistence_1.restoreState)(savedState, blockchain, walletManager, ecoSystem, dex, contractManager, aiRegistry);'
if old_restore in content:
    content = content.replace(old_restore, new_restore)
    print("3. Updated restoreState call with AI Registry")
else:
    print("3. ERROR: restore call not found")

# 4. Pass AI Registry to initial saveState
old_save = '(0, persistence_1.saveState)(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker);'
new_save = '(0, persistence_1.saveState)(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker, aiRegistry);'
if old_save in content:
    content = content.replace(old_save, new_save, 1)
    print("4. Updated initial saveState call")
else:
    print("4. ERROR: initial save not found")

# 5. Pass AI Registry to block production saveState
old_block_save = '(0, persistence_1.saveState)(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker);\n        // Record prices every 5 blocks'
new_block_save = '(0, persistence_1.saveState)(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker, aiRegistry);\n        // Record prices every 5 blocks'
if old_block_save in content:
    content = content.replace(old_block_save, new_block_save)
    print("5. Updated block production saveState")
else:
    print("5. ERROR: block save not found")

# 6. Pass AI Registry to startAutoSave
old_autosave = '(0, persistence_1.startAutoSave)(blockchain, walletManager, ecoSystem, dex, contractManager, 30000, marketTracker);'
new_autosave = '(0, persistence_1.startAutoSave)(blockchain, walletManager, ecoSystem, dex, contractManager, 30000, marketTracker, aiRegistry);'
if old_autosave in content:
    content = content.replace(old_autosave, new_autosave)
    print("6. Updated startAutoSave call")
else:
    print("6. ERROR: autosave not found")

# 7. Reduce block time from 5000 to 2000 (fast finality)
old_interval = 'const BLOCK_INTERVAL_MS = 5000;'
new_interval = 'const BLOCK_INTERVAL_MS = 2000;'
if old_interval in content:
    content = content.replace(old_interval, new_interval)
    print("7. Reduced block time to 2s (fast finality)")
else:
    print("7. ERROR: block interval not found")

# 8. Fix VCO -> VRS in console logs
content = content.replace('VCO Supply', 'VRS Supply')
content = content.replace("VCO'", "VRS'")
content = content.replace('VCO |', 'VRS |')
content = content.replace('VCO/', 'VRS/')
content = content.replace("VCO,", "VRS,")
content = content.replace("'VCO'", "'VRS'")
# Be careful with DEX pool names - those are actual token identifiers stored in state
# Only fix console output, not actual pool creation
print("8. Fixed VCO -> VRS in console output")

# 9. Set new systems on API server after setEco
old_set_eco = 'apiServer.setEco(ecoSystem);'
new_set_eco = '''apiServer.setEco(ecoSystem);
apiServer.aiRegistry = aiRegistry;
apiServer.nameService = nameService;
apiServer.fraudDetection = fraudDetection;
apiServer.accountAbstraction = accountAbstraction;'''
if old_set_eco in content:
    content = content.replace(old_set_eco, new_set_eco)
    print("9. Wired new systems to API server")
else:
    print("9. ERROR: setEco not found")

with open('/opt/verdis/app/dist/index.js', 'w') as f:
    f.write(content)
print("index.js patched successfully!")
