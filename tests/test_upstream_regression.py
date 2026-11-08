"""Small upstream JVM regression suite; full suite also runs through Gradle."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest
from test_java_compat import JDK

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'launcher/app'


class UpstreamRegressionTest(unittest.TestCase):
    def test_upstream_caption_and_wallpaper_size_contracts(self):
        jars = [Path(os.environ[name]) for name in ('JUNIT_JAR', 'HAMCREST_JAR')
                if os.environ.get(name)]
        self.assertEqual(2, len(jars), 'Set JUNIT_JAR and HAMCREST_JAR, or use the Gradle test task')
        for jar in jars:
            self.assertTrue(jar.is_file(), 'Missing JUnit dependency: ' + str(jar))
        names = ['WallpaperCaptions', 'WallpaperSize']
        sources = [APP / ('src/main/java/com/gathin/tvhome/' + n + '.java') for n in names]
        sources += [APP / ('src/test/java/com/gathin/tvhome/' + n + 'Test.java') for n in names]
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests') as temp:
            cp = os.pathsep.join(map(str, jars))
            compiled = subprocess.run([str(JDK / 'javac'), '-encoding', 'UTF-8', '-cp', cp,
                                       '-d', temp] + list(map(str, sources)), text=True, capture_output=True)
            self.assertEqual(0, compiled.returncode, compiled.stdout + compiled.stderr)
            result = subprocess.run([str(JDK / 'java'), '-Djava.io.tmpdir=' + temp,
                                     '-cp', temp + os.pathsep + cp, 'org.junit.runner.JUnitCore'] +
                                    ['com.gathin.tvhome.' + n + 'Test' for n in names],
                                    text=True, capture_output=True)
            print(result.stdout, end='')
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

if __name__ == '__main__':
    unittest.main()
