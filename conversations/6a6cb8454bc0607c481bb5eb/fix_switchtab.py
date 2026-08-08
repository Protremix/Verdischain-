#!/usr/bin/env python3
"""Fix switchTab overrides in Verdiscan explorer."""

EXP_PATH = "/var/www/verdiscan/explorer/index.html"

with open(EXP_PATH, "r") as f:
    html = f.read()

# 1. Remove my broken override (the last origSwitchTab block for prices)
my_override = """
var origSwitchTab = switchTab;
switchTab = function(tab) {
  origSwitchTab(tab);
  if (tab === "prices") {
    loadPricesTab();
  }
};
"""
if my_override in html:
    html = html.replace(my_override, "")
    print("Removed my broken override")

# 2. Add prices handler to the original switchTab function
old_gov = "if (t==='governance') loadGovernance();"
new_line = old_gov + "\n  if (t==='prices') loadPricesTab();"
# Check if it's already there
switchtab_section = html.split("function switchTab")[1].split("\n}")[0] if "function switchTab" in html else ""
if "prices" not in switchtab_section:
    html = html.replace(old_gov, new_line)
    print("Added prices handler to switchTab")

# 3. Fix the second origSwitchTab override (portfolio) by using a different var name
# Find all occurrences of "var origSwitchTab = switchTab;"
occurrences = []
start = 0
while True:
    idx = html.find("var origSwitchTab = switchTab;\nswitchTab = function(t) {", start)
    if idx == -1:
        break
    occurrences.append(idx)
    start = idx + 1

print(f"Found {len(occurrences)} origSwitchTab overrides")

if len(occurrences) >= 2:
    # Fix the second one by renaming origSwitchTab to origSwitchTab2
    second_idx = occurrences[1]
    # Find the end of the second block (next "};")
    block_end = html.find("};", second_idx)
    if block_end > 0:
        block = html[second_idx:block_end+2]
        fixed_block = block.replace("origSwitchTab", "origSwitchTab2")
        html = html[:second_idx] + fixed_block + html[block_end+2:]
        print("Fixed second override (renamed to origSwitchTab2)")

with open(EXP_PATH, "w") as f:
    f.write(html)
print(f"File saved: {len(html)} bytes")
