/*
 * Copyright 2024 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
import java.util.Properties

plugins {
    alias(libs.plugins.android.application)
}

// Release signing, from local.properties (gitignored) or environment variables:
//   release.storeFile=/home/you/keys/photodashplus.jks      RELEASE_STORE_FILE
//   release.storePassword=...                                RELEASE_STORE_PASSWORD
//   release.keyAlias=photodashplus                           RELEASE_KEY_ALIAS
//   release.keyPassword=... (defaults to the store password) RELEASE_KEY_PASSWORD
val localProps = Properties().apply {
    rootProject.file("local.properties").takeIf { it.exists() }?.inputStream()?.use { load(it) }
}
fun signingValue(prop: String, env: String): String? = localProps.getProperty(prop) ?: System.getenv(env)
val releaseStore = signingValue("release.storeFile", "RELEASE_STORE_FILE")
val releaseStorePassword = signingValue("release.storePassword", "RELEASE_STORE_PASSWORD")
val releaseSigningReady = releaseStore != null && releaseStorePassword != null

android {
    enableKotlin = false
    namespace = "com.alexankitty.photodashplus"
    compileSdk = 37

    defaultConfig {
        applicationId = "com.alexankitty.photodashplus"
        minSdk = 34
        targetSdk = 37
        versionCode = 1
        versionName = "1.0.0"
    }

    signingConfigs {
        if (releaseSigningReady) {
            create("release") {
                storeFile = file(releaseStore!!)
                storePassword = releaseStorePassword
                keyAlias = signingValue("release.keyAlias", "RELEASE_KEY_ALIAS") ?: "photodashplus"
                keyPassword = signingValue("release.keyPassword", "RELEASE_KEY_PASSWORD") ?: releaseStorePassword
            }
        }
    }

    buildTypes {
        debug {
            isMinifyEnabled = true
        }
        release {
            isMinifyEnabled = true
            // Ensure shrink resources is false, to avoid potential for them
            // being removed.
            isShrinkResources = false

            signingConfig = signingConfigs.findByName("release")
        }
    }
}

// Fail loudly instead of quietly producing an unsigned (uninstallable) release APK.
tasks.matching { it.name == "assembleRelease" || it.name == "bundleRelease" }.configureEach {
    doFirst {
        if (!releaseSigningReady) {
            throw GradleException(
                "Release signing isn't configured: set release.storeFile and release.storePassword in " +
                    "local.properties, or RELEASE_STORE_FILE and RELEASE_STORE_PASSWORD in the environment."
            )
        }
    }
}
