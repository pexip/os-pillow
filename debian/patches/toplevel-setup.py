Index: b/setup.py
===================================================================
--- a/setup.py
+++ b/setup.py
@@ -17,7 +17,13 @@ import sys
 import subprocess
 
 from distutils.command.build_ext import build_ext
-from distutils import sysconfig
+try:
+    import sysconfig
+    host_platform = sysconfig.get_platform()
+except:
+    from distutils import sysconfig
+    host_platform = host_platform
+
 from setuptools import Extension, setup, find_packages
 
 # monkey patch import hook. Even though flake8 says it's not used, it is.
@@ -187,6 +193,38 @@ class pil_build_ext(build_ext):
                 _dbg('Requiring %s', x)
                 self.feature.required.add(x)
 
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
 
         library_dirs = []
@@ -258,13 +296,13 @@ class pil_build_ext(build_ext):
         if self.disable_platform_guessing:
             pass
 
-        elif sys.platform == "cygwin":
+        elif host_platform == "cygwin":
             # pythonX.Y.dll.a is in the /usr/lib/pythonX.Y/config directory
             _add_directory(library_dirs,
                            os.path.join("/usr/lib", "python%s" %
                                         sys.version[:3], "config"))
 
-        elif sys.platform == "darwin":
+        elif host_platform == "darwin":
             # attempt to make sure we pick freetype2 over other versions
             _add_directory(include_dirs, "/sw/include/freetype2")
             _add_directory(include_dirs, "/sw/lib/freetype2/include")
@@ -302,21 +340,21 @@ class pil_build_ext(build_ext):
                 _add_directory(library_dirs, "/usr/X11/lib")
                 _add_directory(include_dirs, "/usr/X11/include")
 
-        elif sys.platform.startswith("linux"):
+        elif host_platform.startswith("linux"):
                 self.add_multiarch_paths()
 
-        elif sys.platform.startswith("gnu"):
+        elif host_platform.startswith("gnu"):
             self.add_multiarch_paths()
 
-        elif sys.platform.startswith("freebsd"):
+        elif host_platform.startswith("freebsd"):
             _add_directory(library_dirs, "/usr/local/lib")
             _add_directory(include_dirs, "/usr/local/include")
 
-        elif sys.platform.startswith("netbsd"):
+        elif host_platform.startswith("netbsd"):
             _add_directory(library_dirs, "/usr/pkg/lib")
             _add_directory(include_dirs, "/usr/pkg/include")
 
-        elif sys.platform.startswith("sunos5"):
+        elif host_platform.startswith("sunos5"):
             _add_directory(library_dirs, "/opt/local/lib")
             _add_directory(include_dirs, "/opt/local/include")
 
@@ -334,7 +372,7 @@ class pil_build_ext(build_ext):
 
         # on Windows, look for the OpenJPEG libraries in the location that
         # the official installer puts them
-        if sys.platform == "win32":
+        if host_platform == "win32":
             program_files = os.environ.get('ProgramFiles', '')
             best_version = (0, 0)
             best_path = None
@@ -368,7 +406,7 @@ class pil_build_ext(build_ext):
             if _find_include_file(self, "zlib.h"):
                 if _find_library_file(self, "z"):
                     feature.zlib = "z"
-                elif (sys.platform == "win32" and
+                elif (host_platform == "win32" and
                       _find_library_file(self, "zlib")):
                     feature.zlib = "zlib"  # alternative name
 
@@ -377,7 +415,7 @@ class pil_build_ext(build_ext):
             if _find_include_file(self, "jpeglib.h"):
                 if _find_library_file(self, "jpeg"):
                     feature.jpeg = "jpeg"
-                elif (sys.platform == "win32" and
+                elif (host_platform == "win32" and
                       _find_library_file(self, "libjpeg")):
                     feature.jpeg = "libjpeg"  # alternative name
 
@@ -428,9 +466,9 @@ class pil_build_ext(build_ext):
             if _find_include_file(self, 'tiff.h'):
                 if _find_library_file(self, "tiff"):
                     feature.tiff = "tiff"
-                if sys.platform == "win32" and _find_library_file(self, "libtiff"):
+                if host_platform == "win32" and _find_library_file(self, "libtiff"):
                     feature.tiff = "libtiff"
-                if (sys.platform == "darwin" and
+                if (host_platform == "darwin" and
                         _find_library_file(self, "libtiff")):
                     feature.tiff = "libtiff"
 
@@ -511,7 +549,7 @@ class pil_build_ext(build_ext):
         if feature.jpeg2000:
             libs.append(feature.jpeg2000)
             defs.append(("HAVE_OPENJPEG", None))
-            if sys.platform == "win32":
+            if host_platform == "win32":
                 defs.append(("OPJ_STATIC", None))
         if feature.zlib:
             libs.append(feature.zlib)
@@ -522,7 +560,7 @@ class pil_build_ext(build_ext):
         if feature.tiff:
             libs.append(feature.tiff)
             defs.append(("HAVE_LIBTIFF", None))
-        if sys.platform == "win32":
+        if host_platform == "win32":
             libs.extend(["kernel32", "user32", "gdi32"])
         if struct.unpack("h", "\0\1".encode('ascii'))[0] == 1:
             defs.append(("WORDS_BIGENDIAN", None))
@@ -542,7 +580,7 @@ class pil_build_ext(build_ext):
 
         if feature.lcms:
             extra = []
-            if sys.platform == "win32":
+            if host_platform == "win32":
                 extra.extend(["user32", "gdi32"])
             exts.append(Extension("PIL._imagingcms",
                                   ["_imagingcms.c"],
@@ -562,7 +600,7 @@ class pil_build_ext(build_ext):
                                   libraries=libs,
                                   define_macros=defs))
 
-        tk_libs = ['psapi'] if sys.platform == 'win32' else []
+        tk_libs = ['psapi'] if host_platform == 'win32' else []
         exts.append(Extension("PIL._imagingtk",
                               ["_imagingtk.c", "Tk/tkImaging.c"],
                               include_dirs=['Tk'],
@@ -592,7 +630,7 @@ class pil_build_ext(build_ext):
         print("-" * 68)
         print("version      Pillow %s" % PILLOW_VERSION)
         v = sys.version.split("[")
-        print("platform     %s %s" % (sys.platform, v[0].strip()))
+        print("platform     %s %s" % (host_platform, v[0].strip()))
         for v in v[1:]:
             print("             [%s" % v.strip())
         print("-" * 68)
