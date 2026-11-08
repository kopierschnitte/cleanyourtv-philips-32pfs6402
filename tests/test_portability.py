"""Publication portability contracts; no device connection required."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PortabilityTest(unittest.TestCase):
    def test_default_gradle_properties_do_not_pin_a_host_aapt2(self):
        properties = (ROOT / 'launcher/gradle.properties').read_text()
        self.assertNotRegex(properties, r'(?m)^android\.aapt2FromMavenOverride=.+')
    def test_source_only_export_omits_unadapted_device_installers(self):
        for name in ('build-and-install.sh', 'build-and-install.ps1'):
            self.assertFalse((ROOT / 'launcher' / name).exists(),
                             'Source-only preparation must not ship upstream-ID deployment automation')

    def test_java_contract_runner_uses_the_configured_jdk(self):
        import os
        import shutil
        import test_java_compat as compat
        java_home = os.environ.get('JAVA_HOME')
        executable = shutil.which('javac')
        self.assertTrue(java_home or executable, 'A JDK is required')
        expected = Path(java_home) / 'bin' if java_home else Path(executable).parent
        self.assertEqual(expected.resolve(), compat.JDK.resolve())

    def test_junit_runner_does_not_assume_an_adjacent_build_environment(self):
        runner = (ROOT / 'tests/test_upstream_regression.py').read_text()
        self.assertNotIn("'build-env'", runner)
        self.assertIn('os.pathsep', runner)


if __name__ == '__main__':
    unittest.main()
