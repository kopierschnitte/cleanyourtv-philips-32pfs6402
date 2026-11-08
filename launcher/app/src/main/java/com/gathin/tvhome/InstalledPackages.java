package com.gathin.tvhome;

import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;

import java.util.HashMap;
import java.util.Map;

/** API25-safe inventory. A count alone misses replacing one package with another, and updates. */
final class InstalledPackages {
    private InstalledPackages() { }

    static Map<String, String> read(PackageManager pm) {
        Map<String, String> state = new HashMap<>();
        for (PackageInfo info : pm.getInstalledPackages(0)) {
            state.put(info.packageName, info.versionCode + ":" + info.lastUpdateTime + ":"
                    + (info.applicationInfo != null && info.applicationInfo.enabled));
        }
        return state;
    }
}
