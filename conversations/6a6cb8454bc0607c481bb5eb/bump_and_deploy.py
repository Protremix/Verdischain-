import re, shutil, os

# 1. Bump pubspec.yaml
with open("/opt/verdis-wallet/mobile/pubspec.yaml") as f:
    content = f.read()
content = content.replace("version: 1.4.3+8", "version: 1.5.0+9")
with open("/opt/verdis-wallet/mobile/pubspec.yaml", "w") as f:
    f.write(content)
print("pubspec.yaml bumped to 1.5.0+9")

# 2. Bump build.gradle
path = "/opt/verdis-wallet/mobile/android/app/build.gradle"
with open(path) as f:
    content = f.read()
content = re.sub(r"versionCode \d+", "versionCode 9", content)
content = re.sub(r'versionName "[^"]+"', 'versionName "1.5.0"', content)
with open(path, "w") as f:
    f.write(content)
print("build.gradle: versionCode 9, versionName 1.5.0")

# 3. Copy APK to download location
shutil.copy(
    "/opt/verdis-wallet/mobile/build/app/outputs/flutter-apk/app-release.apk",
    "/var/www/verdiscan/wallet/verdis-wallet.apk",
)
size = os.path.getsize("/var/www/verdiscan/wallet/verdis-wallet.apk")
print("APK deployed: " + str(round(size / 1024 / 1024, 1)) + " MB")

# 4. Update web wallet download text
with open("/var/www/verdiscan/wallet/index.html") as f:
    content = f.read()
content = content.replace("v1.4.3", "v1.5.0")
content = content.replace("28.9MB", "29.7MB")
with open("/var/www/verdiscan/wallet/index.html", "w") as f:
    f.write(content)
print("Web wallet download text updated to v1.5.0 / 29.7MB")
