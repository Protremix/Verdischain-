import re

# Fix 1: VerdisApi.kt - Add consent: true to purchaseIdo
with open("/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/VerdisApi.kt", "r") as f:
    api_content = f.read()

old_purchase = '''    suspend fun purchaseIdo(address: String, asset: String, usdAmount: Double): Boolean {
        val body = gson.toJson(mapOf("address" to address, "asset" to asset, "amount" to usdAmount))
        val r = post("/api/ido/purchase", body) ?: return false
        return try { JsonParser.parseString(r).asJsonObject.get("success")?.asBoolean ?: false } catch (e: Exception) { false }
    }'''

new_purchase = '''    suspend fun purchaseIdo(address: String, asset: String, usdAmount: Double): Boolean {
        val body = gson.toJson(mapOf(
            "address" to address,
            "asset" to asset,
            "amount" to usdAmount.toString(),
            "consent" to true
        ))
        val r = post("/api/ido/purchase", body) ?: return false
        return try { JsonParser.parseString(r).asJsonObject.get("success")?.asBoolean ?: false } catch (e: Exception) { false }
    }'''

if old_purchase in api_content:
    api_content = api_content.replace(old_purchase, new_purchase)
    print("Fix 1: Added consent:true to purchaseIdo")
else:
    print("ERROR: Could not find purchaseIdo function")

with open("/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/VerdisApi.kt", "w") as f:
    f.write(api_content)

# Fix 2: build.gradle - Remove Material Components dependency, bump version
with open("/opt/verdis-wallet-native/app/build.gradle", "r") as f:
    gradle = f.read()

# Remove Material dependency
gradle = gradle.replace('    implementation("com.google.android.material:material:1.11.0")\n', '')
print("Fix 2: Removed Material Components dependency")

# Bump version
gradle = gradle.replace('versionCode 5', 'versionCode 6')
gradle = gradle.replace('versionName = "2.5.0"', 'versionName = "2.5.1"')
print("Fix 3: Bumped version to 2.5.1 (code 6)")

with open("/opt/verdis-wallet-native/app/build.gradle", "w") as f:
    f.write(gradle)

# Fix 3: IdoFragment.kt - Fix the null check on getIdoInfo (empty map is not null)
with open("/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/IdoFragment.kt", "r") as f:
    ido_content = f.read()

# Replace "if (r != null)" with "if (r.isNotEmpty())" since getIdoInfo returns emptyMap() not null
ido_content = ido_content.replace("if (r != null) {", "if (r.isNotEmpty()) {")
print("Fix 4: Fixed IDO info null check (empty map != null)")

with open("/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/IdoFragment.kt", "w") as f:
    f.write(ido_content)

print("\nAll source fixes applied. Ready to build.")
