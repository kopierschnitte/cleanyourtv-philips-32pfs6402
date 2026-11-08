"""Configuration contracts only; not Android runtime compatibility proof."""
import pathlib
import re
import unittest
import xml.etree.ElementTree as ET

APP = pathlib.Path(__file__).resolve().parents[1] / 'launcher/app'
ANDROID = '{http://schemas.android.com/apk/res/android}'

class PortConfigTest(unittest.TestCase):
    def test_api25_build_identity_and_desugaring(self):
        build = (APP / 'build.gradle').read_text()
        self.assertRegex(build, r'minSdk\s+25\b')
        self.assertRegex(build, r"applicationId\s+'org\.philips32pfs6402\.home'")
        self.assertRegex(build, r"versionName\s+'3\.4-Android7'")
        self.assertIn('coreLibraryDesugaringEnabled true', build)
        self.assertRegex(build, r"coreLibraryDesugaring\s+'com.android.tools:desugar_jdk_libs:2\.1\.5'")
        self.assertIn("implementation 'androidx.core:core:1.13.1'", build)

    def test_model_specific_application_label(self):
        manifest = ET.parse(APP / 'src/main/AndroidManifest.xml').getroot()
        self.assertEqual('@string/model_home_name',
                         manifest.find('application').attrib[ANDROID + 'label'])
        resources = ET.parse(APP / 'src/main/res/values/branding.xml').getroot()
        label = next(e for e in resources if e.attrib.get('name') == 'model_home_name')
        self.assertEqual('Philips 32PFS6402 Home', label.text)
        self.assertEqual('false', label.attrib.get('translatable'))

    def test_philips_defaults_discover_apps_without_vendor_favorites(self):
        root = ET.parse(APP / 'src/main/res/values/config.xml').getroot()
        values = {e.attrib.get('name'): e for e in root}
        self.assertEqual('org.droidtv.zapster', values['live_tv_package'].text)
        self.assertEqual('de-DE', values['locale'].text)
        self.assertEqual([], list(values['dock_apps']))
        self.assertEqual([], list(values['hidden_apps']))
        for name in ('boot_to_live_tv', 'open_on_start_choice', 'open_on_start_on_wake',
                     'power_on_home', 'power_on_home_always', 'restore_key_services', 'key_filter'):
            self.assertEqual('false', values[name].text, name)
        source = (APP / 'src/main/java/com/gathin/tvhome/MainActivity.java').read_text()
        self.assertIn('Intent.CATEGORY_LEANBACK_LAUNCHER', source)
        manifest = ET.parse(APP / 'src/main/AndroidManifest.xml').getroot()
        permissions = {e.attrib[ANDROID + 'name'] for e in manifest.findall('uses-permission')}
        self.assertNotIn('android.permission.INTERNET', permissions)

if __name__ == '__main__':
    unittest.main()
