plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    namespace = "app.jim.wear"
    compileSdk = 34

    defaultConfig {
        applicationId = "app.jim.wear"
        // Wear OS 3 and up. Below that a watch app has to ship inside the
        // phone's APK and cannot talk to the network on its own, which is
        // the whole point of this surface: a wrist that can reach the
        // Guardian when the phone is in another room.
        minSdk = 30
        targetSdk = 34
        versionCode = 1004000
        versionName = "1.4.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    buildFeatures { compose = true }
}

dependencies {
    val composeBom = platform("androidx.compose:compose-bom:2024.09.02")
    implementation(composeBom)
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.activity:activity-compose:1.9.2")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.5")
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    // Wear's own Compose, not the phone's Material 3: a round screen wants
    // round components, and the phone's layouts do not fit a 45mm face.
    implementation("androidx.wear.compose:compose-material:1.4.0")
    implementation("androidx.wear.compose:compose-foundation:1.4.0")
    // `RemoteInputIntentHelper` — the platform's answer to how text gets
    // onto a watch. It offers the keyboard, handwriting and dictation
    // together; a hand-rolled TextField would offer only the worst of the
    // three, which on a 45mm screen is the difference between a sign-in
    // somebody completes and one they abandon.
    implementation("androidx.wear:wear-input:1.1.0")
    // The watch's own sensors, through the platform's health layer rather
    // than raw SensorManager: Health Services is what a Wear device exposes
    // heart rate through, and it handles the batching and the doze rules a
    // hand-rolled sensor loop gets wrong.
    implementation("androidx.health:health-services-client:1.0.0-rc02")
    implementation("com.google.guava:guava:33.3.0-android")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-guava:1.8.1")
    debugImplementation("androidx.compose.ui:ui-tooling")
}
