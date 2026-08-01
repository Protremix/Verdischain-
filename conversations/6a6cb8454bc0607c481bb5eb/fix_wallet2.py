
# Fix VerdisApi.kt - properly place IDO methods inside companion object
with open("/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/VerdisApi.kt", "r") as f:
    lines = f.readlines()

# Find companion object start
comp_start = None
for i, line in enumerate(lines):
    if "companion object" in line:
        comp_start = i
        break

if comp_start is None:
    print("ERROR: companion object not found")
    exit(1)

# Find companion object end by counting braces (accounting for the opening { on the companion line)
depth = 1  # Start at 1 for the opening brace on the companion object line
comp_end = None
for i in range(comp_start + 1, len(lines)):
    depth += lines[i].count("{") - lines[i].count("}")
    if depth == 0:
        comp_end = i
        break

if comp_end is None:
    print("ERROR: companion object end not found")
    exit(1)

print(f"Companion object: lines {comp_start+1} to {comp_end+1}")
print(f"Closing line: {lines[comp_end].rstrip()}")

# Remove existing IDO methods that are OUTSIDE companion object (between comp_end and end of file)
new_lines = []
for i, line in enumerate(lines):
    # Skip lines that are the misplaced IDO methods (after companion closes, before instance wrappers)
    if i > comp_end and ("getIdoInfo" in line or "purchaseIdoTokens" in line):
        # Skip these lines - they're the misplaced methods
        continue
    new_lines.append(line)

# Now insert IDO methods BEFORE the companion object closing brace
# Find the closing brace line in new_lines
comp_close_idx = None
depth = 1
for i in range(comp_start + 1, len(new_lines)):
    depth += new_lines[i].count("{") - new_lines[i].count("}")
    if depth == 0:
        comp_close_idx = i
        break

print(f"Companion closes at new line index {comp_close_idx}: {new_lines[comp_close_idx].rstrip()}")

# Insert IDO methods before the closing brace
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

# Insert before the closing brace line
for j, method_line in enumerate(ido_methods):
    new_lines.insert(comp_close_idx + j, method_line)

# Also ensure instance method wrappers exist
content = "".join(new_lines)
if "Companion.getIdoInfo()" not in content:
    content = content.replace(
        "suspend fun getBalance(address: String): BalanceResponse = Companion.getBalance(address)",
        "suspend fun getBalance(address: String): BalanceResponse = Companion.getBalance(address)\n    suspend fun getIdoInfo(): IdoInfo? = Companion.getIdoInfo()\n    suspend fun purchaseIdoTokens(address: String, amountVCO: Double): IdoPurchaseResult? = Companion.purchaseIdoTokens(address, amountVCO)"
    )

with open("/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/VerdisApi.kt", "w") as f:
    f.write(content)

print("VerdisApi.kt fixed - IDO methods properly inside companion object")
