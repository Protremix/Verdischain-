#!/usr/bin/env python3
"""Add governance to persistence module"""

with open('/opt/verdis/app/dist/core/persistence.js') as f:
    content = f.read()

# 1. Add governance to export
old_export = "        accountAbstraction: accountAbstraction ? accountAbstraction.exportState() : null,\n    };"
new_export = "        accountAbstraction: accountAbstraction ? accountAbstraction.exportState() : null,\n        governance: governance ? governance.exportState() : null,\n    };"
if old_export in content:
    content = content.replace(old_export, new_export)
    print("1. Added governance to state export")
else:
    print("1. ERROR: export not found")

# 2. Add governance to import
old_import = """    // Restore Account Abstraction
    if (state.accountAbstraction && accountAbstraction) {
        accountAbstraction.importState(state.accountAbstraction);
        console.log(`🔐 Account Abstraction restored: ${accountAbstraction.getStats().totalSmartWallets} smart wallets`);
    }"""
new_import = """    // Restore Account Abstraction
    if (state.accountAbstraction && accountAbstraction) {
        accountAbstraction.importState(state.accountAbstraction);
        console.log(`🔐 Account Abstraction restored: ${accountAbstraction.getStats().totalSmartWallets} smart wallets`);
    }
    // Restore Governance
    if (state.governance && governance) {
        governance.importState(state.governance);
        console.log(`🏛️ Governance restored: ${governance.getStats().totalProposals} proposals`);
    }"""
if old_import in content:
    content = content.replace(old_import, new_import)
    print("2. Added governance to state import")
else:
    print("2. ERROR: import not found")

with open('/opt/verdis/app/dist/core/persistence.js', 'w') as f:
    f.write(content)
print("Persistence updated for governance!")
