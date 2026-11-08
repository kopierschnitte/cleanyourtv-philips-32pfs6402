# Philips 32PFS6402 Home — building the source port

Source-only compatibility port of Gathin23/cleanyourtv, based on commit `3f175120f9802ab4364f61d040db9aa78ec71493`. Not an official upstream release, firmware update or security update.

## Identity and scope

- Android 7.1 / API25 minimum; compile/target SDK34.
- Model-specific development application ID `org.philips32pfs6402.home`, version `3.4-Android7`; display name **Philips 32PFS6402 Home**.
- Java namespace `com.gathin.tvhome` is retained for upstream classes and protocol names.
- Philips LiveTV (`org.droidtv.zapster`), German locale and automatic Leanback app discovery; no owner/device names or fixed personal favourites.
- No INTERNET permission added; no automatic accessibility/notification grants or boot/power overrides enabled.

The original local build was exercised on Philips32PFS6402/12, Android7.1.2, firmwareQM164E.0.16.102.24. This preparation changes identity and test portability, not application Java logic. **The neutral build has not been installed on that TV.** Earlier device tests are not fresh device acceptance of this export. A different application ID installs separately and does not inherit another install's data or Home selection.

## Build

Install JDK17, Android SDK platform34 and build-tools34.0.0. Set JAVA_HOME and ANDROID_HOME (or ANDROID_SDK_ROOT) to your own installations. Do not commit local.properties. The wrapper selects Gradle8.9.

From this source root:

```sh
cd launcher
./gradlew --no-daemon testReleaseUnitTest lintRelease assembleRelease
```

On a supported x86-64 host, Android Gradle Plugin obtains normal AAPT2 automatically. Linux ARM64 may require a compatible native AAPT2 and its shared libraries. Configure those outside the checkout and pass your executable explicitly; no host override is stored here:

```sh
./gradlew --no-daemon -Pandroid.aapt2FromMavenOverride="$AAPT2" \
  testReleaseUnitTest lintRelease assembleRelease
```

AAPT2 is a builder-supplied path, not a bundled executable. Release currently uses the local Gradle debug signing configuration for development tests. No private key is supplied. Choose a secure release-signing policy before distributing production APKs. This archive supplies no APK, SDK/JDK or build cache.

## Additional tests

The primary JVM suite runs through Gradle above. Additional Python contracts require Python3, the same JDK and, for the small upstream-JUnit runner, JUNIT_JAR and HAMCREST_JAR environment variables pointing to existing JUnit4.13.2 and HamcrestCore1.3 JARs. Set them to your dependency files first; Gradle can populate its normal dependency cache.

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
```

JAVA_HOME is preferred; otherwise javac is found on PATH. Missing required JARs fail clearly. Java contract doubles are not an Android emulator or real-TV proof. See tests/PORTING-NOTES.md.

## Home and recovery boundaries

Do not disable stock Home until a replacement works on the exact device, explicit consent exists and a rollback is prepared. This source-only preparation deliberately omits the upstream build-and-install shell/PowerShell scripts: they require the full upstream tools tree and target a different application ID. They must not be reused blindly for this separately named app. No install, Home-takeover or recovery automation is supplied here. Follow reviewed upstream/legacy procedures only where they actually apply; never bypass their checks for other TVs.

On the tested Philips, system Home outranked normal apps. A separately authorised, reversible package change let the original local port retain Home across a full restart, and the user confirmed the real remote button. Android Shell refused a narrower single-activity change. This observation does not authorise automatic stock-launcher disabling.

Philips still started LiveTV naturally after restart. Earlier WAKEUP-key attempts did not confirm wake; a later POWER-key wake was verified as Awake/ON, followed by a real launcher PNG and confirmed Asleep/OFF after SLEEP. This one cycle does not prove long-standby reliability. See the linked device report for dates and variant boundaries. No several-day stability, complete HDMI/streaming or optical Ambilight result is claimed.

## Privacy and attribution

This source tree excludes device inventories, UI dumps, unredacted screenshots, private connection helpers, addresses, individual device/person names, keys and local logs. The linked actual launcher screenshot has its Wi-Fi SSID covered and metadata removed. Preserve LICENSE, launcher/FONT-LICENSE-OFL.txt and launcher/ICONS-LICENSE-FLUENT-EMOJI.txt, including public upstream authorship.

The source port and privacy-edited screenshot are provided on the `port/philips-32pfs6402-android7` branch of the separate upstream fork. No upstream pull request has been opened; a SHOWCASE listing is a separate contribution. Contributions to johnsontsai11/cleanyourtv-legacy still need separate small-patch review, not replacement of that project with this tree.
