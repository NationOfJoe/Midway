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
If the key has *Website* restrictions, add these referrers (the first is the
Android app, the second the web version on GitHub Pages):

```
https://appassets.androidplatform.net/*
https://nationofjoe.github.io/Midway/*
```

The key needs Maps JavaScript API, Places API (New) and Routes API enabled.

## Web apps

On the web the page is published twice, each locked to one feature by a flag on its
`<html>` tag (the Android app has no flag and keeps both tabs):

- `data-app="Meet"`: **Midway**, meet halfway.
- `data-app="Pair"`: **Nearby Pair**, a place with another kind of place a short walk away.

Both share the API key and saved places when served from the same site. The Pages build
writes them to `meet/` and `pair/`.

### Offering a shared key

A host can let visitors search without their own key by adding two tags to the page's `<head>`:

```html
<meta name="midway-shared-key" content="AIza…">
<meta name="midway-quota-url" content="/apps/midway-quota/quota.cgi">
```

Before each search on the shared key the page asks `web/quota.cgi` (a small Python CGI) for
permission. It knows the most each search can cost in each Google SKU and stops at 90% of the
monthly free allowance, with no single day using more than a quarter of that. Usage is kept
in `private/midway-usage.json`, two folders above the script. A key the visitor saves in
Settings always takes priority and is not counted. Keep the key itself out of this repo.

Per search, at most: Midway 78 journey-time elements and 3 place searches (plus 8 parking
searches when someone drives); Nearby Pair 9 place searches and 80 walking elements
("Find both"), or 1 search and 20 elements ("I have a place").

## Updating the web app

Replace `app/src/main/assets/index.html` with a newer `midway.html` and rebuild.
Bump `versionCode` in `app/build.gradle.kts` so the phone accepts it as an update.

## Debugging

Debug builds allow WebView inspection: with the phone plugged in, open `chrome://inspect` in desktop Chrome.

## Versions

Gradle 8.14.3 · Android Gradle Plugin 8.10.1 · Kotlin 2.0.21 · compileSdk/targetSdk 35 · minSdk 26 (Android 8.0+).
