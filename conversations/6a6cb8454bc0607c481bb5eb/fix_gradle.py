#!/usr/bin/env python3
"""Add release signing config to build.gradle and bump version."""

filepath = "/opt/verdis-android-build/app/build.gradle"
with open(filepath, "r") as f:
    content = f.read()

# Add signing config before buildTypes
old_block = """    buildTypes {
        release {
            minifyEnabled false
            debuggable false
            proguardFiles getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro"
            signingConfig signingConfigs.debug
        }"""

new_block = """    signingConfigs {
        release {
            storeFile file('/opt/verdis-wallet-native/verdis-release.keystore')
            storePassword 'VerdisChain2026'
            keyAlias 'verdis-release'
            keyPassword 'VerdisChain2026'
        }
    }
    buildTypes {
        release {
            minifyEnabled false
            debuggable false
            proguardFiles getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro"
            signingConfig signingConfigs.release
        }"""

content = content.replace(old_block, new_block)

with open(filepath, "w") as f:
    f.write(content)
print("OK: Added release signing config to build.gradle")
