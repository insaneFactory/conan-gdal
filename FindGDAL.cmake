#
# FindGDAL
# ---------
#
# Wrapper for FindGDAL that adds imported targets.
#
# Imported targets
# ^^^^^^^^^^^^^^^^
#
# This module defines the following :prop_tgt:`IMPORTED` targets:
#
# ``GDAL::GDAL``
#   The GDAL library, if found
#
#
# Result variables
# ^^^^^^^^^^^^^^^^
#
# This module will set the following variables in your project:
#
# ``GDAL_FOUND``
#   Found the GDAL library
# ``GDAL_INCLUDE_DIRS``
#   the directory containing the GDAL headers
# ``GDAL_SHARE_DIR``
#   the directory containing the GDAL data
#
# The library variables below are set as normal variables.  These
# contain debug/optimized keywords when a debugging library is found.
#
# ``GDAL_LIBRARIES``
#   The GDAL library
#
# Cache variables
# ^^^^^^^^^^^^^^^
#
# The following cache variables may also be set:
#
# ``GDAL_ROOT_DIR``
#   The root directory of the GDAL installation (may also be
#   set as an environment variable)
#
# The following :prop_tgt:`IMPORTED` targets are also defined:
#
#   GDAL::GDAL        - Target for the whole GDAL library
#

# On OSX, we don't want frameworks libraries
set(CMAKE_FIND_FRAMEWORK "NEVER")

find_path(GDAL_INCLUDE_DIR gdal.h
  HINTS
    ENV GDAL_DIR
    ENV GDAL_ROOT
  PATH_SUFFIXES
     include/gdal
     include/GDAL
     include
  PATHS
    #   ~/Library/Frameworks/gdal.framework/Headers
    #   /Library/Frameworks/gdal.framework/Headers
      /sw # Fink
      /opt/local # DarwinPorts
      /opt/csw # Blastwave
      /opt
)

if(UNIX)
    # Use gdal-config to obtain the library version (this should hopefully
    # allow us to -lgdal1.x.y where x.y are correct version)
    # For some reason, libgdal development packages do not contain
    # libgdal.so...
    find_program(GDAL_CONFIG gdal-config
        HINTS
          ENV GDAL_DIR
          ENV GDAL_ROOT
        PATH_SUFFIXES bin
        PATHS
            /sw # Fink
            /opt/local # DarwinPorts
            /opt/csw # Blastwave
            /opt
    )

    if(GDAL_CONFIG)
        exec_program(${GDAL_CONFIG} ARGS --libs OUTPUT_VARIABLE GDAL_CONFIG_LIBS)
        if(GDAL_CONFIG_LIBS)
            string(REGEX MATCHALL "-l[^ ]+" _gdal_dashl ${GDAL_CONFIG_LIBS})
            string(REPLACE "-l" "" _gdal_lib "${_gdal_dashl}")
            string(REGEX MATCHALL "-L[^ ]+" _gdal_dashL ${GDAL_CONFIG_LIBS})
            string(REPLACE "-L" "" _gdal_libpath "${_gdal_dashL}")
        endif()
    endif()
endif()

find_library(GDAL_LIBRARY
  NAMES ${_gdal_lib} gdal gdal_i gdal1.5.0 gdal1.4.0 gdal1.3.2 GDAL
  HINTS
     ENV GDAL_DIR
     ENV GDAL_ROOT
     ${_gdal_libpath}
  PATH_SUFFIXES lib
  PATHS
    /sw
    /opt/local
    /opt/csw
    /opt
    /usr/freeware
)

include(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GDAL DEFAULT_MSG GDAL_LIBRARY GDAL_INCLUDE_DIR)

set(GDAL_LIBRARIES ${GDAL_LIBRARY})
set(GDAL_INCLUDE_DIRS ${GDAL_INCLUDE_DIR})

if(GDAL_FOUND)
    mark_as_advanced(GDAL_CONFIG)
    mark_as_advanced(GDAL_INCLUDE_DIR)
    mark_as_advanced(GDAL_LIBRARY)

    find_path(GDAL_SHARE_DIR gdal_datum.csv
        HINTS
            $ENV{GDAL_ROOT_DIR}
            ${GDAL_ROOT_DIR}
        PATH_SUFFIXES
            data
            share/gdal
    )
    mark_as_advanced(GDAL_SHARE_DIR)

    if(NOT GDAL_SHARE_DIR)
        message(FATAL_ERROR "GDAL_SHARE_DIR not found.")
    endif()

    include(CMakeFindDependencyMacro)
    find_dependency(ZLIB)
    find_dependency(Threads)

    if(NOT TARGET GDAL::GDAL)
        add_library(GDAL::GDAL UNKNOWN IMPORTED)
        if(GDAL_INCLUDE_DIRS)
            set_target_properties(GDAL::GDAL PROPERTIES
                INTERFACE_INCLUDE_DIRECTORIES "${GDAL_INCLUDE_DIRS}")
        endif()
        if(EXISTS "${GDAL_LIBRARY}")
            set_target_properties(GDAL::GDAL PROPERTIES
                IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
                IMPORTED_LOCATION "${GDAL_LIBRARY}")
        endif()

        list(APPEND _deps
            "${ZLIB_LIBRARIES}"
            "Threads::Threads"
            "${CMAKE_DL_LIBS}"
        )
        set_target_properties(GDAL::GDAL PROPERTIES
                              INTERFACE_LINK_LIBRARIES "${_deps}")
    endif()
endif()

if(WIN32)
    get_filename_component(_root_dir ${GDAL_INCLUDE_DIR} DIRECTORY)
    file(GLOB GDAL_DLL ${_root_dir}/bin/*.dll)
endif(WIN32)
