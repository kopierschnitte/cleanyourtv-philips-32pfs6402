"""Execute production Java against small contract doubles, NOT an Android VM.
API25 forbidden calls fail loudly in the doubles or bytecode checks.
"""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'launcher/app/src/main/java/com/gathin/tvhome'
if os.environ.get('JAVA_HOME'):
    JDK = Path(os.environ['JAVA_HOME']) / 'bin'
else:
    javac = shutil.which('javac')
    if not javac:
        raise RuntimeError('JDK 17 is required: set JAVA_HOME or put javac on PATH')
    JDK = Path(javac).parent


def run_java(files, harness, stubs=None):
    with tempfile.TemporaryDirectory(dir=ROOT / 'tests') as temp:
        folder = Path(temp)
        sources = []
        for name, content in (stubs or {}).items():
            path = folder / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            sources.append(str(path))
        path = folder / 'CompatProbe.java'
        path.write_text(harness)
        sources.append(str(path))
        sources += [str(SRC / name) for name in files if (SRC / name).exists()]
        result = subprocess.run([str(JDK / 'javac'), '-encoding', 'UTF-8', '-d', temp] + sources,
                                text=True, capture_output=True)
        if result.returncode:
            raise AssertionError('Java compilation failed:\n' + result.stdout + result.stderr)
        result = subprocess.run([str(JDK / 'java'), '-ea', '-Djava.io.tmpdir=' + temp, '-cp', temp,
                                 'com.gathin.tvhome.CompatProbe'], text=True, capture_output=True)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        return result.stdout

PM_STUBS = {
    'android/content/pm/ApplicationInfo.java': '''package android.content.pm;
public class ApplicationInfo { public boolean enabled = true; }''',
    'android/content/pm/PackageInfo.java': '''package android.content.pm;
public class PackageInfo { public String packageName; public int versionCode;
public long lastUpdateTime; public ApplicationInfo applicationInfo = new ApplicationInfo(); }''',
    'android/content/pm/PackageManager.java': '''package android.content.pm;
import java.util.*;
public class PackageManager { public List<PackageInfo> packages = new ArrayList<>();
public List<PackageInfo> getInstalledPackages(int flags) { return packages; } }''',
}

class JavaCompatTest(unittest.TestCase):
    def test_package_inventory_detects_equal_count_replacement_updates_and_enable_state(self):
        output = run_java(['InstalledPackages.java'], '''package com.gathin.tvhome;
import android.content.pm.*;
import java.lang.reflect.*;
import java.util.*;
public class CompatProbe {
 static Object snapshot(PackageManager pm) throws Exception {
   Class<?> c;
   try { c = Class.forName("com.gathin.tvhome.InstalledPackages"); }
   catch (ClassNotFoundException e) { throw new AssertionError("API25 package inventory missing", e); }
   Method m = c.getDeclaredMethod("read", PackageManager.class); m.setAccessible(true);
   return m.invoke(null, pm);
 }
 static PackageInfo pkg(String name) { PackageInfo p=new PackageInfo();p.packageName=name;return p; }
 public static void main(String[] args) throws Exception {
   PackageManager pm=new PackageManager(); PackageInfo a=pkg("a"), b=pkg("b");
   pm.packages=Arrays.asList(a,b); Object original=snapshot(pm);
   pm.packages=Arrays.asList(b,a); assert original.equals(snapshot(pm)) : "order must not rebuild";
   pm.packages=Arrays.asList(a,pkg("c")); assert !original.equals(snapshot(pm)) : "same-count replacement";
   pm.packages=Arrays.asList(a,b); b.versionCode++; assert !original.equals(snapshot(pm)) : "update";
   b.versionCode--; b.lastUpdateTime++; assert !original.equals(snapshot(pm)) : "same-version reinstall";
   b.lastUpdateTime--; b.applicationInfo.enabled=false;
   assert !original.equals(snapshot(pm)) : "disabled package";
   pm.packages=Collections.singletonList(a); assert !original.equals(snapshot(pm)) : "removed package";
   pm.packages=Arrays.asList(a,b,pkg("c")); assert !original.equals(snapshot(pm)) : "added package";
   System.out.println("package inventory behavior OK");
 }
}''', PM_STUBS)
        self.assertIn('behavior OK', output)

    def test_bundled_font_avoids_api26_resource_loader_and_system_family_stays_available(self):
        stubs = {
            'android/util/TypedValue.java': '''package android.util;
public class TypedValue { public CharSequence string; public int resourceId; }''',
            'android/graphics/Typeface.java': '''package android.graphics;
public class Typeface { public static final int NORMAL=0; public String name;
public Typeface(String n) { name=n; } public static Typeface create(String n,int s) { return new Typeface(n); } }''',
            'android/content/res/Resources.java': '''package android.content.res;
import android.util.TypedValue; import android.graphics.Typeface;
public class Resources { public String name="res/font/outfit.xml";
public void getValue(int id,TypedValue v,boolean resolve) { v.string=name;v.resourceId=42; }
public Typeface getFont(int id) { throw new AssertionError("Resources.getFont requires API26"); } }''',
            'android/content/Context.java': '''package android.content;
import android.content.res.Resources; public class Context { public Resources res=new Resources();
public Resources getResources() { return res; } }''',
            'androidx/core/content/res/ResourcesCompat.java': '''package androidx.core.content.res;
import android.content.Context; import android.graphics.Typeface;
public class ResourcesCompat { public static Typeface getFont(Context c,int id) {
if(id!=42) throw new AssertionError("wrong font resource");return new Typeface("bundled"); } }''',
        }
        self.assertIn('font behavior OK', run_java(['UiFont.java'], '''package com.gathin.tvhome;
import android.content.Context;
public class CompatProbe { public static void main(String[] args) {
Context c=new Context(); assert "bundled".equals(UiFont.get(c,1).name);
c.res.name="sans-serif"; assert "sans-serif".equals(UiFont.get(c,1).name);
System.out.println("font behavior OK"); } }''', stubs))

    def test_captions_read_utf8_without_nio_file_runtime(self):
        self.assertIn('caption behavior OK', run_java(['WallpaperCaptions.java'], r'''package com.gathin.tvhome;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.lang.reflect.*;
import java.util.*;
public class CompatProbe {
 public static void main(String[] args) throws Exception {
   URL location=CompatProbe.class.getProtectionDomain().getCodeSource().getLocation();
   try(URLClassLoader loader=new URLClassLoader(new URL[]{location},ClassLoader.getPlatformClassLoader()) {
     protected Class<?> loadClass(String name,boolean resolve) throws ClassNotFoundException {
       if(name.startsWith("java.nio.file.")) throw new ClassNotFoundException("API25 has no " + name);
       return super.loadClass(name,resolve);
     }
   }) {
     Class<?> captions=loader.loadClass("com.gathin.tvhome.WallpaperCaptions");
     Method read=captions.getDeclaredMethod("read",File.class); read.setAccessible(true);
     File dir=new File(System.getProperty("java.io.tmpdir"),"philips-32pfs6402-captions-"+System.nanoTime());
     assert dir.mkdir(); File file=new File(dir,"captions.txt");
     try {
       assert ((Map<?,?>)read.invoke(null,dir)).isEmpty() : "missing file";
       try(FileOutputStream out=new FileOutputStream(file)) {
         out.write("# Kommentar\r\nbild.jpg\tGrüße vom See\r\ninvalid\n".getBytes(StandardCharsets.UTF_8));
       }
       Map<?,?> names=(Map<?,?>)read.invoke(null,dir);
       assert names.size()==1 && "Grüße vom See".equals(names.get("bild.jpg")) : names;
       try(RandomAccessFile out=new RandomAccessFile(file,"rw")) { out.setLength(256*1024+1); }
       assert ((Map<?,?>)read.invoke(null,dir)).isEmpty() : "oversized input";
       assert ((Map<?,?>)read.invoke(null,new Object[]{null})).isEmpty() : "null folder";
     } finally { file.delete(); dir.delete(); }
   }
   System.out.println("caption behavior OK");
 }
}'''))

    def test_wallpaper_decode_keeps_drawable_software_bitmap_on_api25(self):
        # Execute the actual decode method, with graphics boundary doubles. Full Android
        # decoding/rendering is deliberately left to lint + the real TV smoke test.
        source = (SRC / 'WallpaperPlayer.java').read_text()
        start = source.index('    private Bitmap decode(File file) {')
        depth = 0
        begin = source.index('{', start)
        end = begin
        for end in range(begin, len(source)):
            depth += (source[end] == '{') - (source[end] == '}')
            if depth == 0:
                break
        method = source[start:end + 1]
        stubs = {
            'android/graphics/Bitmap.java': '''package android.graphics;
public class Bitmap { public enum Config { RGB_565, ARGB_8888, HARDWARE }
public boolean recycled; public Bitmap copy(Config config,boolean mutable) {
if(config==Config.HARDWARE) throw new AssertionError("hardware bitmap unavailable on API25"); return new Bitmap(); }
public void recycle() { recycled=true; } }''',
            'android/graphics/BitmapFactory.java': '''package android.graphics;
public class BitmapFactory { public static Bitmap last;
public static class Options { public boolean inJustDecodeBounds,inScaled,inMutable;
public int outWidth,outHeight,inSampleSize,inDensity,inTargetDensity; public Bitmap.Config inPreferredConfig; }
public static Bitmap decodeFile(String path,Options o) { if(o.inJustDecodeBounds) {
o.outWidth=1920; o.outHeight=1080; return null; } last=new Bitmap();return last; } }''',
            'android/graphics/Canvas.java': '''package android.graphics;
public class Canvas { public Canvas(Bitmap b) { if(b.recycled) throw new AssertionError("recycled"); }
public void drawColor(int color) {} }''',
        }
        harness = '''package com.gathin.tvhome;
import android.graphics.*; import java.io.File;
public class CompatProbe {
 int width=1280,height=720,dimColor=0;
 Bitmap.Config bitmapConfig=Bitmap.Config.RGB_565;
''' + method + '''
 public static void main(String[] args) {
  CompatProbe probe=new CompatProbe(); Bitmap bitmap=probe.decode(new File("image.jpg"));
  assert bitmap==BitmapFactory.last && !bitmap.recycled : "retain decoded software bitmap";
  probe.dimColor=0x80000000; bitmap=probe.decode(new File("image.jpg"));
  assert bitmap==BitmapFactory.last && !bitmap.recycled : "dimmed bitmap survives";
  System.out.println("software wallpaper behavior OK");
 }
}'''
        self.assertIn('software wallpaper behavior OK', run_java(['WallpaperSize.java'], harness, stubs))

if __name__ == '__main__':
    unittest.main()
