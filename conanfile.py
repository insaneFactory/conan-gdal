
import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.tools import download, unzip

class GdalConan(ConanFile):
    """ Conan package for GDAL """

    name = "Gdal"
    version = "2.1.3"
    description = "Conan package for GDAL"
    settings = "os", "compiler", "build_type", "arch"
    folder = "gdal-%s" % version
    url = "http://www.gdal.org/"
    license = "LGPL"
    exports = ["FindGDAL.cmake"]
    archive_name = "gdal-%s.tar.gz" % version
    src_url = "http://download.osgeo.org/gdal/%s/%s" % (version, archive_name)

    def source(self):
        download(self.src_url, self.archive_name)
        unzip(self.archive_name)
        os.unlink(self.archive_name)
        if self.settings.os != "Windows":
            self.run("chmod +x ./%s/configure" % self.folder)

    def build(self):
        env_build = AutoToolsBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            config_args = ["--disable-static", "--enable-shared",
                           "--with-geos=yes", "--prefix %s" % self.package_folder]
            self.run("cd %s && ./configure %s"
                     % (self.folder, " ".join(config_args)))
            self.run("cd %s && make" % (self.folder))
            self.run("cd %s && make install" % (self.folder))

    def package(self):
        self.copy("FindGDAL.cmake", ".", ".")

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        if self.settings.build_type == "Debug":
            libname = "gdal"    # ?
        else:
            libname = "gdal"
        self.cpp_info.libs = [libname]
