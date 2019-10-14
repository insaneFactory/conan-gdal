import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools, VisualStudioBuildEnvironment

class GdalConan(ConanFile):
    name = "gdal"
    version = "2.4.2"
    description = "GDAL - Geospatial Data Abstraction Library"
    url = "http://www.gdal.org/"
    license = "LGPL"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
	    "fPIC": [True, False]
    }
    default_options = {
        "shared": True,
        "fPIC": True
    }
    requires = (
        "zlib/1.2.11@conan/stable",
        "sqlite3/3.29.0@bincrafters/stable"
    )
    exports = ["LICENSE.md", "FindGDAL.cmake"]
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
		name = "osgearth"
        tools.get("{0}/{1}-{2}.tar.gz".format(self.download_prefix, name, self.version))
        extracted_dir = "{}-{}-".format(name, name) + self.version

    def source(self):
        archive_name = "gdal-%s" % self.version
        tools.get("http://download.osgeo.org/gdal/{0}/{1}.tar.gz".format(self.version, archive_name))
        os.rename(archive_name, self._source_subfolder)

        if self.settings.os != "Windows":
            self.run("chmod +x ./%s/configure" % self._source_subfolder)

    def _build_autotools(self):
        config_args = ["--with-geos=yes"]
        if self.options.shared:
            config_args += ["--disable-static", "--enable-shared"]
        else:
            config_args += [
                "--without-ld-shared", "--disable-shared", "--enable-static",
            ]

        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(self._source_subfolder):
            autotools.configure(args=config_args)
            autotools.make()
            autotools.install()

        self.run("cp %s/FindGDAL.cmake %s/" % (self.source_folder, self.package_folder))
        
    def _build_vs(self):
        versions = {
            "14": "1900",
            "15": "1910",
            "16": "1920"
        }
        vsver = versions.get(self.settings.compiler.version, None)
        
        args = "GDAL_HOME=" + self.package_folder
        if vsver is not None:
            args += " MSVC_VER=%s" % vsver
        if self.settings.build_type == "Debug":
            args += " DEBUG=1"
        if self.settings.arch == "x86_64":
            args += " WIN64=1"
        if not self.options.shared:
            args += " DLLBUILD=0"
        
        env_build = VisualStudioBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            vcvars = tools.vcvars_command(self.settings)
            self.run("%s && nmake -f makefile.vc %s" % (vcvars, args))
            self.run("%s && nmake -f makefile.vc %s install" % (vcvars, args))
        
    def build(self):
        if self.settings.compiler == "Visual Studio":
            self._build_vs()
        else:
            self._build_autotools()

    def package_info(self):
        self.cpp_info.libs = ["gdal"]
