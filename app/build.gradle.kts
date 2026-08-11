plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.verdis.wallet"
    compileSdk = 34
    ndkVersion = ""

    defaultConfig {
        applicationId = "com.verdis.wallet"
        minSdk = 26
        targetSdk = 34
        versionCode = 4
        versionName = "2.2.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    // P0 fix: Load signing config from environment variables or local.properties
    val keystorePath = System.getenv("VERDIS_KEYSTORE_PATH") ?: "/opt/verdis-release.keystore"
    val keystorePassword = System.getenv("VERDIS_KEYSTORE_PASSWORD") ?: ""
    val keyAlias = System.getenv("VERDIS_KEY_ALIAS") ?: "verdis"
    val keyPassword = System.getenv("VERDIS_KEY_PASSWORD") ?: ""

    signingConfigs {
        create("release") {
            storeFile = file(keystorePath)
            storePassword = keystorePassword
            this.keyAlias = keyAlias
            this.keyPassword = keyPassword
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true  // P0 fix: Enable minification
            isShrinkResources = true  // P0 fix: Shrink resources
            signingConfig = signingConfigs.getByName("release")
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        viewBinding = true
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("androidx.cardview:cardview:1.0.0")
    implementation("androidx.recyclerview:recyclerview:1.3.2")
    implementation("androidx.biometric:biometric:1.1.0")
    implementation("androidx.fragment:fragment-ktx:1.6.2")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    implementation("org.bouncycastle:bcprov-jdk15to18:1.78.1")
    testImplementation("junit:junit:4.13.2")
}
