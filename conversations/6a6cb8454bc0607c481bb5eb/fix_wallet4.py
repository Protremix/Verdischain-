
# Fix: Move IDO methods inside companion object (before its closing brace at line 908)
with open("/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/VerdisApi.kt", "r") as f:
    lines = f.readlines()

# Find the line "        }" followed by "    }" which closes swap() then companion object
# Look for the pattern: line with just "        }" then line with "    }"
# This is the swap function close + companion object close
swap_close_idx = None
comp_close_idx = None
for i in range(len(lines) - 1):
    if lines[i].strip() == "}" and lines[i+1].strip() == "}" and i > 890 and i < 920:
        # Check if line before has "return executeSwap" 
        if i > 0 and "executeSwap" in lines[i-1]:
            swap_close_idx = i
            comp_close_idx = i + 1
            print(f"Found swap close at line {i+1}, companion close at line {i+2}")
            break

if comp_close_idx is None:
    # Alternative: find "    }" that's followed by a blank line and "    suspend fun getIdoInfo"
    for i in range(len(lines) - 2):
        if lines[i].strip() == "}" and "getIdoInfo" in lines[i+2]:
            comp_close_idx = i
            print(f"Found companion close at line {i+1} (before getIdoInfo)")
            break

if comp_close_idx is None:
    print("ERROR: Could not find companion object closing brace")
    exit(1)

# Remove the IDO methods that are currently OUTSIDE companion object (between comp_close and instance wrappers)
# Find the instance wrappers line
instance_wrappers_idx = None
for i in range(len(lines)):
    if "Instance method wrappers" in lines[i]:
        instance_wrappers_idx = i
        break

print(f"Instance wrappers at line {instance_wrappers_idx + 1}")

# Remove lines between comp_close_idx+1 and instance_wrappers_idx that contain IDO methods
# But keep the instance wrappers themselves
new_lines = []
skip_until = None
for i, line in enumerate(lines):
    if skip_until is not None and i < skip_until:
        if "getIdoInfo" in line or "purchaseIdoTokens" in line or "executeGet" in line or "executePost" in line or "gson.fromJson" in line:
            continue  # Skip these lines
        if "withContext" in line or "try {" in line or "} catch" in line:
            continue
        if line.strip() == "" or line.strip() == "}":
            continue
    new_lines.append(line)

# Now find the companion closing brace in new_lines and insert IDO methods before it
# Re-find the companion close
comp_close_new = None
for i in range(len(new_lines) - 1):
    if new_lines[i].strip() == "}" and i > 890:
        # Check if next non-empty line has getIdoInfo or Instance method
        for j in range(i+1, min(i+5, len(new_lines))):
            if "getIdoInfo" in new_lines[j] or "Instance method" in new_lines[j]:
                comp_close_new = i
                break
        if comp_close_new:
            break

if comp_close_new is None:
    print("ERROR: Could not find companion close in new lines")
    exit(1)

print(f"Companion close in new lines at index {comp_close_new}: {new_lines[comp_close_new].rstrip()}")

# Insert IDO methods BEFORE the companion closing brace
ido_methods = [
    "\n",
    "        suspend fun getIdoInfo(): IdoInfo? = withContext(Dispatchers.IO) {\n",
    "            try {\n",
    "                val response = executeGet(\"/api/ido/info\")\n",
    "                gson.fromJson(response, IdoInfo::class.java)\n",
    "            } catch (e: Exception) { null }\n",
    "        }\n",
    "\n",
    "        suspend fun purchaseIdoTokens(address: String, amountVCO: Double): IdoPurchaseResult? = withContext(Dispatchers.IO) {\n",
    "            try {\n",
    "                val body = gson.toJson(mapOf(\n",
    "                    \"address\" to address,\n",
    "                    \"amountVCO\" to amountVCO.toString()\n",
    "                ))\n",
    "                val response = executePost(\"/api/ido/purchase\", body)\n",
    "                gson.fromJson(response, IdoPurchaseResult::class.java)\n",
    "            } catch (e: Exception) { null }\n",
    "        }\n",
]

for j, method_line in enumerate(ido_methods):
    new_lines.insert(comp_close_new + j, method_line)

content = "".join(new_lines)

# Ensure instance wrappers exist
if "Companion.getIdoInfo()" not in content:
    content = content.replace(
        "suspend fun getBalance(address: String): BalanceResponse = Companion.getBalance(address)",
        "suspend fun getBalance(address: String): BalanceResponse = Companion.getBalance(address)\n    suspend fun getIdoInfo(): IdoInfo? = Companion.getIdoInfo()\n    suspend fun purchaseIdoTokens(address: String, amountVCO: Double): IdoPurchaseResult? = Companion.purchaseIdoTokens(address, amountVCO)"
    )

with open("/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/VerdisApi.kt", "w") as f:
    f.write(content)

print("Fixed: IDO methods now properly inside companion object")
