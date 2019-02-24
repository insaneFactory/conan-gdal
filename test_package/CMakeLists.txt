project(helloworld)
cmake_minimum_required(VERSION 2.8.12)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(GDAL REQUIRED)

add_executable(helloworld main.cpp)

if(NOT BUILD_SHARED_LIBS)
    list(APPEND additional_libs sqlite3)
endif()
target_link_libraries(helloworld
    PUBLIC
    GDAL::GDAL
    sqlite3
)
