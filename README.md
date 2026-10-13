# Midway for Android

Native Android shell (Kotlin) around the Midway web app in `app/src/main/assets/index.html`.

- Meet halfway, Nearby pair and Settings all run from the bundled page.
- "Use my location" asks for Android's location permission.
- Directions links open in the Google Maps app.
- Saved places, names and your API key stay on the phone (WebView storage).

## Get the APK

**GitHub Actions (no Android Studio needed)**
1. Create a new GitHub repo and push this folder to its `main` branch.
2. Open the repo's **Actions** tab. The *Build APK* run starts by itself (or press *Run workflow*).
3. When it finishes, download the **midway-apk** artifact, unzip it and copy `app-debug.apk` to your phone.
4. Open it on the phone and allow "install unknown apps" for your file manager or browser when asked.

**Android Studio**
Open this folder, wait for Gradle sync, plug in your phone (USB debugging on) and press **Run**.

## API key

Paste the key on first launch, or change it later in the Settings tab.
If the key has *Website* restrictions, add this referrer:

```
https://appassets.androidplatform.net/*
```

The key needs Maps JavaScript API, Places API (New) and Routes API enabled.

## Updating the web app

Replace `app/src/main/assets/index.html` with a newer `midway.html` and rebuild.
Bump `versionCode` in `app/build.gradle.kts` so the phone accepts it as an update.

## Debugging

Debug builds allow WebView inspection: with the phone plugged in, open `chrome://inspect` in desktop Chrome.

## Versions

Gradle 8.14.3 · Android Gradle Plugin 8.10.1 · Kotlin 2.0.21 · compileSdk/targetSdk 35 · minSdk 26 (Android 8.0+).
