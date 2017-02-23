
import platform
from conan.packager import ConanMultiPackager
from conans.tools import os_info

if __name__ == "__main__":
    builder = ConanMultiPackager(username="osechet", channel="stable")
    builder.add_common_builds()
    filtered_builds = []
    for settings, options in builder.builds:
        if settings["arch"] == "x86_64" and settings["build_type"] != "Debug":
            filtered_builds.append([settings, options])
    builder.builds = filtered_builds
    builder.run()
