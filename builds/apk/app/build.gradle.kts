// SOVEREIGN — :app module build script (Android application).
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "ai.sovereign.orchestrator"
    compileSdk = 34

    defaultConfig {
        applicationId = "ai.sovereign.orchestrator"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "0.1.0"
    }

    buildTypes {
        release {
            // The debug key is used by default; see README.md for signing
            // a production keystore via signingConfigs.
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    // AppCompat: dark theme + backwards-compatible UI widgets.
    implementation("androidx.appcompat:appcompat:1.6.1")
    // Activity KTX: lifecycle-aware activity extensions.
    implementation("androidx.activity:activity-ktx:1.8.2")
    // AndroidX WebKit: modern WebView APIs for the dashboard shell.
    implementation("androidx.webkit:webkit:1.9.0")
}
