
import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.tools import download, unzip

class GdalConan(ConanFile):
    """ Conan package for GDAL """

    name = "GDAL"
    version = "1.11.1"
    description = "GDAL - Geospatial Data Abstraction Library"
    url = "http://www.gdal.org/"
    license = "LGPL"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": True}
    requires = ("zlib/1.2.11@conan/stable", "sqlite3/3.27.1@bincrafters/stable")
    exports = ["LICENSE.md", "FindGDAL.cmake"]

    _folder = "gdal-%s" % version


    def source(self):
        archive_name = "gdal-%s.tar.gz" % self.version
        src_url = "http://download.osgeo.org/gdal/%s/%s" % (self.version, archive_name)

        download(src_url, archive_name)
        unzip(archive_name)
        os.unlink(archive_name)
        if self.settings.os != "Windows":
            self.run("chmod +x ./%s/configure" % self._folder)


    def build(self):
        self.run("mkdir -p %s" % self.package_folder)
        self.run("cp %s/FindGDAL.cmake %s/" % (self.source_folder, self.package_folder))

        config_args = ["--with-geos=yes"]
        if self.options.shared:
            config_args += ["--disable-static", "--enable-shared"]
        else:
            config_args += [
                "--without-ld-shared", "--disable-shared", "--enable-static",
            ]

        # GDAL cannot be build in a separate build directory
        autotools = AutoToolsBuildEnvironment(self)
        with tools.environment_append(autotools.vars):
            self.run("cd %s && ./configure --prefix %s %s" % (os.path.join(self.source_folder, self._folder), self.package_folder, " ".join(config_args)))
            self.run("cd %s && make" % os.path.join(self.source_folder, self._folder))
            self.run("cd %s && make install" % os.path.join(self.source_folder, self._folder))


    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        if self.settings.build_type == "Debug":
            libname = "gdal"    # ?
        else:
            libname = "gdal"
        self.cpp_info.libs = [libname]
