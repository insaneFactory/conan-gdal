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
        "sqlite3/3.29.0@bincrafters/stable",
		"libjpeg/9c@bincrafters/stable",
        "openjpeg/2.3.1@bincrafters/stable",
		"libpng/1.6.34@bincrafters/stable",
		"libxml2/2.9.8@bincrafters/stable",
		"libtiff/4.0.9@bincrafters/stable",
		"libgeotiff/1.4.2@insanefactory/stable",
        "giflib/5.1.4@bincrafters/stable",
		"proj4/5.2.0@insanefactory/stable",
        "geos/3.8.0@insanefactory/stable"
    )
    exports = ["LICENSE.md", "FindGDAL.cmake"]
    #generators = "pkg_config"
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        archive_name = "gdal-%s" % self.version
        tools.get("http://download.osgeo.org/gdal/{0}/{1}.tar.gz".format(self.version, archive_name))
        os.rename(archive_name, self._source_subfolder)

        if self.settings.os != "Windows":
            self.run("chmod +x ./%s/configure" % self._source_subfolder)

    def _build_autotools(self):
        # Args
        config_args = [
            "--with-libz",
            "--with-sqlite3",
            "--with-jpeg",
            "--with-openjpeg",
            "--with-png",
            "--with-xml2",
            "--with-libtiff",
            "--with-geotiff",
            "--with-gif",
            "--with-proj",
            "--with-proj5-api=no",
            "--with-geos"
        ]

        if self.options.shared:
            config_args.append("--disable-static")
            config_args.append("--enable-shared")
        else:
            #config_args.append("--without-ld-shared")
            config_args.append("--disable-shared")
            config_args.append("--enable-static")

        # LD_LIBRARY_PATH
        ld_library_path = ":".join(self.deps_cpp_info.lib_paths)
        env_ld_library_path = tools.get_env("LD_LIBRARY_PATH")
        if env_ld_library_path is not None and len(env_ld_library_path) > 0:
            ld_library_path += ":" + env_ld_library_path

        autotools = AutoToolsBuildEnvironment(self)
        autotools_vars = autotools.vars
        if "LD_LIBRARY_PATH" in autotools_vars and len(autotools_vars["LD_LIBRARY_PATH"]) > 0:
            ld_library_path += ":" + autotools_vars["LD_LIBRARY_PATH"]
        autotools_vars["LD_LIBRARY_PATH"] = ld_library_path

        # Build
        with tools.chdir(self._source_subfolder):
            autotools.configure(args=config_args, vars=autotools_vars)
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
