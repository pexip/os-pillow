Index: b/setup.py
===================================================================
--- a/setup.py
+++ b/setup.py
@@ -15,7 +15,13 @@ import struct
 import sys
 
 from distutils.command.build_ext import build_ext
-from distutils import sysconfig
+try:
+    import sysconfig
+    host_platform = sysconfig.get_platform()
+except:
+    from distutils import sysconfig
+    host_platform = sys.platform
+
 from setuptools import Extension, setup, find_packages
 
 # monkey patch import hook. Even though flake8 says it's not used, it is.
@@ -146,6 +152,38 @@ class pil_build_ext(build_ext):
             if getattr(self, 'enable_%s' % x):
                 self.feature.required.append(x)
 
+    def add_gcc_paths(self):
+        gcc = sysconfig.get_config_var('CC')
+        tmpfile = os.path.join(self.build_temp, 'gccpaths')
+        if not os.path.exists(self.build_temp):
+            os.makedirs(self.build_temp)
+        ret = os.system('%s -E -v - </dev/null 2>%s 1>/dev/null' % (gcc, tmpfile))
+        is_gcc = False
+        in_incdirs = False
+        inc_dirs = []
+        lib_dirs = []
+        try:
+            if ret >> 8 == 0:
+                with open(tmpfile) as fp:
+                    for line in fp.readlines():
+                        if line.startswith("gcc version"):
+                            is_gcc = True
+                        elif line.startswith("#include <...>"):
+                            in_incdirs = True
+                        elif line.startswith("End of search list"):
+                            in_incdirs = False
+                        elif is_gcc and line.startswith("LIBRARY_PATH"):
+                            for d in line.strip().split("=")[1].split(":"):
+                                d = os.path.normpath(d)
+                                if '/gcc/' not in d:
+                                    _add_directory(self.compiler.library_dirs,
+                                                   d)
+                        elif is_gcc and in_incdirs and '/gcc/' not in line:
+                            _add_directory(self.compiler.include_dirs,
+                                           line.strip())
+        finally:
+            os.unlink(tmpfile)
+
     def build_extensions(self):
 
         global TCL_ROOT
@@ -194,12 +232,12 @@ class pil_build_ext(build_ext):
         #
         # add platform directories
 
-        if sys.platform == "cygwin":
+        if host_platform == "cygwin":
             # pythonX.Y.dll.a is in the /usr/lib/pythonX.Y/config directory
             _add_directory(library_dirs, os.path.join(
                 "/usr/lib", "python%s" % sys.version[:3], "config"))
 
-        elif sys.platform == "darwin":
+        elif host_platform == "darwin":
             # attempt to make sure we pick freetype2 over other versions
             _add_directory(include_dirs, "/sw/include/freetype2")
             _add_directory(include_dirs, "/sw/lib/freetype2/include")
@@ -239,13 +277,13 @@ class pil_build_ext(build_ext):
                 _add_directory(library_dirs, "/usr/X11/lib")
                 _add_directory(include_dirs, "/usr/X11/include")
 
-        elif sys.platform.startswith("linux"):
+        elif host_platform.startswith("linux"):
             self.add_multiarch_paths()
 
-        elif sys.platform.startswith("gnu"):
+        elif host_platform.startswith("gnu"):
             self.add_multiarch_paths()
 
-        elif sys.platform.startswith("netbsd"):
+        elif host_platform.startswith("netbsd"):
                     _add_directory(library_dirs, "/usr/pkg/lib")
                     _add_directory(include_dirs, "/usr/pkg/include")
 
@@ -298,7 +336,7 @@ class pil_build_ext(build_ext):
 
         # on Windows, look for the OpenJPEG libraries in the location that
         # the official installer puts them
-        if sys.platform == "win32":
+        if host_platform == "win32":
             program_files = os.environ.get('ProgramFiles', '')
             best_version = (0, 0)
             best_path = None
@@ -332,7 +370,7 @@ class pil_build_ext(build_ext):
             if _find_include_file(self, "zlib.h"):
                 if _find_library_file(self, "z"):
                     feature.zlib = "z"
-                elif (sys.platform == "win32" and
+                elif (host_platform == "win32" and
                         _find_library_file(self, "zlib")):
                     feature.zlib = "zlib"  # alternative name
 
@@ -341,7 +379,7 @@ class pil_build_ext(build_ext):
                 if _find_library_file(self, "jpeg"):
                     feature.jpeg = "jpeg"
                 elif (
-                        sys.platform == "win32" and
+                        host_platform == "win32" and
                         _find_library_file(self, "libjpeg")):
                     feature.jpeg = "libjpeg"  # alternative name
 
@@ -378,9 +416,9 @@ class pil_build_ext(build_ext):
         if feature.want('tiff'):
             if _find_library_file(self, "tiff"):
                 feature.tiff = "tiff"
-            if sys.platform == "win32" and _find_library_file(self, "libtiff"):
+            if host_platform == "win32" and _find_library_file(self, "libtiff"):
                 feature.tiff = "libtiff"
-            if (sys.platform == "darwin" and
+            if (host_platform == "darwin" and
                     _find_library_file(self, "libtiff")):
                 feature.tiff = "libtiff"
 
@@ -467,7 +505,7 @@ class pil_build_ext(build_ext):
         if feature.jpeg2000:
             libs.append(feature.jpeg2000)
             defs.append(("HAVE_OPENJPEG", None))
-            if sys.platform == "win32":
+            if host_platform == "win32":
                 defs.append(("OPJ_STATIC", None))
         if feature.zlib:
             libs.append(feature.zlib)
@@ -475,7 +513,7 @@ class pil_build_ext(build_ext):
         if feature.tiff:
             libs.append(feature.tiff)
             defs.append(("HAVE_LIBTIFF", None))
-        if sys.platform == "win32":
+        if host_platform == "win32":
             libs.extend(["kernel32", "user32", "gdi32"])
         if struct.unpack("h", "\0\1".encode('ascii'))[0] == 1:
             defs.append(("WORDS_BIGENDIAN", None))
@@ -500,7 +538,7 @@ class pil_build_ext(build_ext):
 
         if os.path.isfile("_imagingcms.c") and feature.lcms:
             extra = []
-            if sys.platform == "win32":
+            if host_platform == "win32":
                 extra.extend(["user32", "gdi32"])
             exts.append(Extension(
                 "PIL._imagingcms",
@@ -519,7 +557,7 @@ class pil_build_ext(build_ext):
             exts.append(Extension(
                 "PIL._webp", ["_webp.c"], libraries=libs, define_macros=defs))
 
-        if sys.platform == "darwin":
+        if host_platform == "darwin":
             # locate Tcl/Tk frameworks
             frameworks = []
             framework_roots = [
@@ -573,7 +611,7 @@ class pil_build_ext(build_ext):
         print("-" * 68)
         print("version      Pillow %s" % PILLOW_VERSION)
         v = sys.version.split("[")
-        print("platform     %s %s" % (sys.platform, v[0].strip()))
+        print("platform     %s %s" % (host_platform, v[0].strip()))
         for v in v[1:]:
             print("             [%s" % v.strip())
         print("-" * 68)
