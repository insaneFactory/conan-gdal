
import os
from conans import ConanFile, ConfigureEnvironment
from conans.tools import download, unzip

class GdalConan(ConanFile):
    name = "Gdal"
    version = "2.1.1"
    settings = "os", "compiler", "build_type", "arch"
    folder = "gdal-%s" % version
    url = "http://www.gdal.org/"
    license = "LGPL"
    archive_name = "gdal-%s.tar.gz" % version
    src_url = "http://download.osgeo.org/gdal/%s/%s" % (version, archive_name)
    requires = ("Geos/3.4.2@studiofuga/testing")

    def source(self):
        download(self.src_url, self.archive_name)
        unzip(self.archive_name)
        os.unlink(self.archive_name)
        if self.settings.os != "Windows":
            self.run("chmod +x ./%s/configure" % self.folder)

    def build(self):
        #os.makedirs('build')
        env = ConfigureEnvironment(self.deps_cpp_info, self.settings)
        self.run("cd %s && %s ../%s/configure --disable-static --enable-shared --with-geos=yes"
                 % (self.folder, env.command_line, self.folder))
        self.run("cd %s && %s make" % (self.folder, env.command_line))

    def package(self):
        """ Define your conan structure: headers, libs and data. After building your
            project, this method is called to create a defined structure:
        """
        self.copy(pattern="*.h", dst="include", src="%s/include" % self.folder, keep_path=True)
        self.copy("*.lib", dst="lib", keep_path=False)
        # UNIX
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib*", dst="lib", keep_path=False)

    def package_info(self):
        if self.settings.build_type == "Debug":
            libname = "gdal"    # ?
        else:
            libname = "gdal"
        self.cpp_info.libs = [libname]
