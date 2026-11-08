# Android 7.1 / API25 compatibility notes

## Production differences from the reference launcher

The reference source is Gathin23/cleanyourtv commit `3f175120f9802ab4364f61d040db9aa78ec71493`.

- `launcher/app/build.gradle`: minSdk25, separate neutral application ID, Java-time core library desugaring and explicit AndroidX Core dependency for ResourcesCompat.
- `InstalledPackages.java`: a package inventory including name, version, update time and application-enabled state; independent of package order and total count.
- `MainActivity.java`: compare that inventory on return to Home and retain existing package broadcasts and Leanback discovery.
- `UiFont.java`: ResourcesCompat resource-font loading; system-family handling unchanged.
- `WallpaperCaptions.java`: bounded UTF-8 BufferedReader instead of java.nio.file.
- `WallpaperPlayer.java`: keep software bitmaps rather than requesting API26 hardware bitmaps.
- `config.xml`: Philips Live TV, German locale and discovered apps, without private favourites or automatic boot/power/key-filter changes.

## Portable tests

Run from this source root with JDK17 available through JAVA_HOME or PATH:

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
```

The small upstream-regression runner additionally requires JUNIT_JAR and HAMCREST_JAR environment variables pointing to JUnit4.13.2 and HamcrestCore1.3. The full Gradle unit suite resolves its own test dependencies normally:

```sh
cd launcher
./gradlew --no-daemon testReleaseUnitTest lintRelease assembleRelease
```

The Java compatibility probes exercise actual production helpers against small contract doubles. Captions are tested with a class loader that rejects java.nio.file; the bitmap probe executes an isolated production method against graphics doubles. These are deliberately not real Android-runtime or visual-font tests. Inventory tests cover replacement at equal count, version/update-time changes, application enable state and package ordering; independent component enable changes are not covered.

## Publication preparation

The publication identity and host-independent test paths were changed using failing contracts followed by passing runs. Private development logs are not included in this source archive. Local audit results belong outside the publication tree.

The original local port had device smoke tests on Philips32PFS6402/12, Android7.1.2, firmwareQM164E.0.16.102.24, including a separately approved Home package change and actual remote-button confirmation. The neutral export is a differently named application and has not itself been installed on that TV. No blanket API24 support, font-quality result, benchmark, complete HDMI compatibility or long-term reliability claim is made.
