
import os
from conans import ConanFile, CMake

# This easily allows to copy the package in other user or channel
CHANNEL = os.getenv("CONAN_CHANNEL", "stable")
USERNAME = os.getenv("CONAN_USERNAME", "osechet")

class GdalTestConan(ConanFile):
    """ GDAL Conan package test """

    requires = "Gdal/2.1.3@%s/%s" % (USERNAME, CHANNEL)
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "virtualenv"

    def build(self):
        cmake = CMake(self.settings)
        self.run('cmake "%s" %s' % (self.conanfile_directory, cmake.command_line))
        self.run("cmake --build . %s" % cmake.build_config)

    def test(self):
        if self.settings.os == "Windows":
            self.run("activate && %s %s" % (os.sep.join([".", "bin", "helloworld"]), "conan"))
        else:
            self.run("%s %s" % (os.sep.join([".", "bin", "helloworld"]), "conan"))
