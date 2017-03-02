
import os
from conans import ConanFile, ConfigureEnvironment
from conans.tools import download, unzip

class GdalConan(ConanFile):
    name = "Gdal"
    version = "2.1.3"
    description = "GDAL is an open source X/MIT licensed translator library for raster and vector geospatial data formats."
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
        env = ConfigureEnvironment(self.deps_cpp_info, self.settings)
        config_args = ["--disable-static", "--enable-shared",
                       "--with-geos=yes", "--prefix %s" % self.package_folder]
        self.run("cd %s && %s ../%s/configure %s"
                 % (self.folder, env.command_line, self.folder, " ".join(config_args)))
        self.run("cd %s && %s make" % (self.folder, env.command_line))
        self.run("cd %s && %s make install" % (self.folder, env.command_line))

    def package(self):
        self.copy("FindGDAL.cmake", ".", ".")

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        if self.settings.build_type == "Debug":
            libname = "gdal"    # ?
        else:
            libname = "gdal"
        self.cpp_info.libs = [libname]
