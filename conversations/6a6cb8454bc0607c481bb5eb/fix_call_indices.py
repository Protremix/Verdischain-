#!/usr/bin/env python3
"""Fix the call indices in the transactions page."""

TX_PATH = "/var/www/verdiscan/transactions/index.html"

with open(TX_PATH, "r") as f:
    html = f.read()

# Replace the callMap with correct indices from construct_runtime!
old_callmap = '''    var callMap = {
      "0,0": "system.remark", "0,1": "system.setHeapPages", "0,2": "system.setCode",
      "0,3": "system.setStorage", "0,4": "system.killStorage", "0,5": "system.killPrefix",
      "1,0": "timestamp.set",
      "2,0": "balances.transferAllowDeath", "2,1": "balances.setBalance",
      "2,2": "balances.forceTransfer", "2,3": "balances.transferKeepAlive", "2,4": "balances.transferAll",
      "10,0": "dpos.registerValidator", "10,1": "dpos.unregisterValidator",
      "10,2": "dpos.updateGreenScore", "10,3": "dpos.nominate", "10,5": "dpos.setValidatorName",
      "11,0": "ammDex.createPool", "11,1": "ammDex.addLiquidity",
      "11,2": "ammDex.removeLiquidity", "11,3": "ammDex.swap",
      "12,0": "eco.mintCarbonCredit", "12,1": "eco.createReforestProject",
      "12,2": "eco.logReforestation", "12,3": "eco.transferCarbonCredit",
      "6,0": "sudo.sudo",
    };'''

new_callmap = '''    var callMap = {
      "0,0": "system.remark", "0,1": "system.setHeapPages", "0,2": "system.setCode",
      "0,3": "system.setStorage", "0,4": "system.killStorage", "0,5": "system.killPrefix",
      "1,0": "timestamp.set",
      "4,0": "balances.transferAllowDeath", "4,1": "balances.setBalance",
      "4,2": "balances.forceTransfer", "4,3": "balances.transferKeepAlive", "4,4": "balances.transferAll",
      "6,0": "sudo.sudo",
      "30,0": "dpos.registerValidator", "30,1": "dpos.unregisterValidator",
      "30,2": "dpos.updateGreenScore", "30,3": "dpos.nominate", "30,5": "dpos.setValidatorName",
      "31,0": "ammDex.createPool", "31,1": "ammDex.addLiquidity",
      "31,2": "ammDex.removeLiquidity", "31,3": "ammDex.swap",
      "32,0": "eco.mintCarbonCredit", "32,1": "eco.createReforestProject",
      "32,2": "eco.logReforestation", "32,3": "eco.transferCarbonCredit",
    };'''

html = html.replace(old_callmap, new_callmap)

# Also fix the filter dropdown values
html = html.replace('value="balances.transferAllowDeath">balances.transferAllowDeath', 'value="balances.transferAllowDeath">balances.transferAllowDeath')
html = html.replace('value="balances.transferKeepAlive">balances.transferKeepAlive', 'value="balances.transferKeepAlive">balances.transferKeepAlive')

with open(TX_PATH, "w") as f:
    f.write(html)

print("Call indices fixed in transactions page")

# Also fix the explorer page's Tx Search tab
EXPLORER_PATH = "/var/www/verdiscan/explorer/index.html"
with open(EXPLORER_PATH, "r") as f:
    exp_html = f.read()

old_exp_callmap = '''    var callMap = {
      "0,0": ["system","remark"], "0,1": ["system","setHeapPages"],
      "0,2": ["system","setCode"], "0,3": ["system","setStorage"],
      "1,0": ["timestamp","set"],
      "2,0": ["balances","transferAllowDeath"], "2,1": ["balances","setBalance"],
      "2,3": ["balances","transferKeepAlive"], "2,4": ["balances","transferAll"],
      "10,0": ["dpos","registerValidator"], "10,1": ["dpos","unregisterValidator"],
      "10,2": ["dpos","updateGreenScore"], "10,5": ["dpos","setValidatorName"],
      "11,0": ["ammDex","createPool"], "11,1": ["ammDex","addLiquidity"],
      "11,2": ["ammDex","removeLiquidity"], "11,3": ["ammDex","swap"],
      "12,0": ["eco","mintCarbonCredit"], "12,1": ["eco","createReforestProject"],
      "12,2": ["eco","logReforestation"],
    };'''

new_exp_callmap = '''    var callMap = {
      "0,0": ["system","remark"], "0,1": ["system","setHeapPages"],
      "0,2": ["system","setCode"], "0,3": ["system","setStorage"],
      "1,0": ["timestamp","set"],
      "4,0": ["balances","transferAllowDeath"], "4,1": ["balances","setBalance"],
      "4,3": ["balances","transferKeepAlive"], "4,4": ["balances","transferAll"],
      "6,0": ["sudo","sudo"],
      "30,0": ["dpos","registerValidator"], "30,1": ["dpos","unregisterValidator"],
      "30,2": ["dpos","updateGreenScore"], "30,5": ["dpos","setValidatorName"],
      "31,0": ["ammDex","createPool"], "31,1": ["ammDex","addLiquidity"],
      "31,2": ["ammDex","removeLiquidity"], "31,3": ["ammDex","swap"],
      "32,0": ["eco","mintCarbonCredit"], "32,1": ["eco","createReforestProject"],
      "32,2": ["eco","logReforestation"],
    };'''

exp_html = exp_html.replace(old_exp_callmap, new_exp_callmap)

with open(EXPLORER_PATH, "w") as f:
    f.write(exp_html)

print("Call indices fixed in explorer page too")
