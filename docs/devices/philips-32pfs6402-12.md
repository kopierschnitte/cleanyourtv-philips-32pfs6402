# DRAFT — Philips 32PFS6402/12: Android 7.1 Home handover and limited debloat observations

> **Device-observation draft for the separate Philips port's documentation; not an accepted upstream report. The planned main-project contribution is a SHOWCASE entry, not this port report or a lower-minSdk code PR.**
> One unit: Home/reboot tests recorded on 7 November 2026; power/screenshot follow-up on 8 November 2026. Not a several-day debloat list, a reference-launcher compatibility claim, or a general installation guide.

## Identify the tested unit

| Field | Tested value |
|---|---|
| Retail model | Philips **32PFS6402/12** |
| Android / API | **7.1.2 / 25** |
| Firmware | **QM164E.0.16.102.24** |
| Stock Home package | `com.google.android.leanbacklauncher` |
| Live TV package | `org.droidtv.zapster` |
| Replacement used in these tests | **local API25 port**, not the unmodified reference launcher |

The reference launcher requires API 26. This API 25 unit is outside that requirement. The local API25 port used compatibility changes as well as a different minimum SDK; its results do not validate the current reference build. No firmware flashing, root access or Android upgrade was used.

## Changes observed, not a recommended package list

Six earlier reversible debloat disables remained in place throughout the Home tests:

| Group | Packages read back as disabled |
|---|---|
| Google feedback | `com.google.android.feedback` |
| Philips analytics and logging | `org.droidtv.candeebug`, `org.droidtv.gel`, `org.droidtv.tv.frameworklogger` |
| Philips advertising and recommendations | `org.droidtv.nettvadvert`, `org.droidtv.nettvrecommender` |

Separately, after explicit owner approval, the **whole stock Google launcher package** was set to `disabled-user` for user 0. It was not uninstalled; its installation and data were retained. Disabling the whole package also disables its background components, not just its Home activity. The final disabled-package readback contained the six packages above plus that stock launcher.

A preceding attempt to change only the stock Home activity was refused with `SecurityException`. Merely assigning the replacement as Home while stock Home remained enabled had not achieved the handover. These are observations on this firmware, **not instructions to bypass the upstream Home guard**. No accessibility key filter, notification-listener helper or boot/power redirection was configured.

## Test matrix

“Readback” below means Android resolver, window/focus, package or power-state evidence, not a photograph of the panel.

| Check | Observed result | Boundary |
|---|---|---|
| Home resolver after handover | Selected the local API25 port | Not a test of the reference API 26 launcher |
| HOME from Live TV | Port reached foreground | Activity/focus check; not sustained tuner playback validation |
| HOME from Android Settings | Port reached foreground | Injected HOME with focus readback |
| HOME from Play Store | Port reached foreground | Store opening/return only; not downloads or streaming |
| HOME after force-stop of the port | Port restarted and reached foreground | Recovery check, not a performance benchmark |
| Physical remote HOME from deliberately opened Live TV | Owner confirmed success; subsequent focus readback showed the port without another injected HOME | One physical-button check, not every remote button |
| Rollback to stock Home | Original package `DEFAULT` state, stock resolver and actual HOME focus restored | Tested before switching back to the port |
| Full normal reboot | Restart independently verified; boot completion and reconnection confirmed | Not a mains-disconnect or repeated-reboot endurance test |
| Home assignment after reboot | Still selected the port; HOME opened it | Does not mean automatic boot into the launcher |
| ADB reconnection after reboot | Existing authorised ADB key worked without new pairing | No key material disclosed; not proof debugging was closed |
| Natural post-reboot foreground | Live TV in four focus samples over roughly 40 seconds | **Power-on target remains Live TV** |
| Standby entry | Android reported `Asleep` after an injected sleep key | Not a physical-remote standby-entry test |
| Earlier ADB wake attempt with `KEYCODE_WAKEUP` (224) | No `Awake` confirmation; ADB/control access later became unavailable | A successful key-command exit did not establish wake |
| Wake with ordinary remote | Owner confirmed waking the TV; `Awake`, port foreground and Home selection read back | One manual wake, not long-standby reliability |
| Power/capture follow-up, 8 November 2026 | From verified Asleep/OFF, injected `KEYCODE_POWER` (26) produced Awake/ON; HOME and screencap returned a valid 1280×720 PNG; `KEYCODE_SLEEP` (223) restored Asleep/OFF | One successful cycle, not proof of long-standby reliability or of a physical power-button test |
| Crash buffer at test end | Empty when queried | Not proof of crash-free everyday use |
| Ambilight software state after reboot | Relevant packages remained enabled; `org.droidtv.ambihue` process present | **No optical LED check or Ambilight measurement** |

## Capture and validation limits

Earlier screenshot attempts returned **zero bytes despite exit status 0**; those attempts remain failures. On 8 November 2026, a fresh attempt after verified POWER-key wake and HOME returned a real 1280×720 PNG of the launcher. Its Wi-Fi SSID is covered by an opaque black rectangle in the publication copy; no other pixels were edited. The unredacted original stays private. The image shows the existing pre-publication installation, not the newly renamed public application identity, which remains host-build-checked only. UI dumps are still not screenshots; this image is not an optical measurement of the physical panel, animations or Ambilight.

No complete physical HDMI picture/audio test across all inputs, sustained streaming-service playback test, multi-day household-use trial or before/after performance benchmark was completed. Opening Live TV or a sources menu does not establish that every input works. No speed, memory-saving, storage-saving or everyday-stability improvement is claimed.

Home selection survived the tested reboot, but the firmware still opened Live TV naturally. No additional autostart workaround was installed. The later POWER-key wake succeeded once, whereas `KEYCODE_WAKEUP` (224) did not; keep the ordinary remote available rather than assuming all ADB wake methods or long-standby cases work. These findings apply to one unit on the firmware above, not every Philips model with similar package names.

## Rollback principle and maintenance risk

Keep the original package-state record and an authorised recovery route before changing Home. The tested rollback restored the stock launcher's original `DEFAULT` package state, selected stock Home, and verified both resolver and actual HOME foreground. The port remained installed; the six earlier debloat disables were unchanged. Restoring Home and undoing debloat are separate operations: neither should blindly re-enable unrelated packages.

This draft supplies no blanket Home-guard override or copy-and-run handover sequence. Follow upstream safety policy and obtain separate approval for a stock-launcher package change. Confirm the replacement and the recovery route before any such change. Disabling is not uninstalling, and firmware/input/core services are not candidates merely because another model's list mentions them.

ADB was used for testing; this report does **not** establish that debugging was subsequently closed. At the end of authorised maintenance, disable debugging and revoke authorisations in accordance with upstream guidance, then verify closure. Do not publish credentials, raw device captures or backups.

## Why a separate port report plus SHOWCASE, not a core port or tested examples list?

The locally available upstream documentation and examples were checked for the exact retail model and firmware; no matching entry was found. Related Philips notes concern different models or firmware and are not interchangeable package lists.

Upstream routes old-Android launcher ports to a separate public project plus SHOWCASE. This predominantly port-related report therefore belongs with the port, not in a core-port PR. A separately justified device note is not the current proposal. A tested examples list requires packages actually disabled and lived with for several days; this session does not meet that requirement. No tested-list row, standalone main-repository device note or generated TV-table change is proposed here.

The reference launcher's API 26 requirement and Home-safety checks should remain unchanged. A lower-API port belongs in a separate project rather than a main-repository minimum-SDK reduction.

## Separate legacy alternative — not the build tested here

The public [cleanyourtv-legacy fork](https://github.com/johnsontsai11/cleanyourtv-legacy) is a separate alternative for review. A standalone upstream build from that fork **was not tested on this TV**. The local API25 port described here is a different build; none of the Home, reboot or remote results above can be attributed to that fork, and this note does not establish its compatibility.

## Evidence and publication boundary

This draft summarises the private Home test report, launcher result report, operation record, and the corresponding step, reboot, sleep/wake, manual-wake and final physical-Home readbacks. The final completion records take precedence over earlier intermediate Home limitations. Those private records are retained for owner review, **not attached or offered for public download**.

Only model, Android/API and firmware identification is included. The companion screenshot is an actual device capture with its Wi-Fi SSID redacted. No APK, signing material, ADB keys, raw logs, unredacted capture, household identifiers or private evidence locations are included. This report accompanies the separately published source port; no upstream submission or acceptance is implied.
