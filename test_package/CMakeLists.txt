project(helloworld)
cmake_minimum_required(VERSION 2.8.12)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(GDAL REQUIRED)

add_executable(helloworld main.cpp)
target_include_directories(helloworld
    PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}
    ${GDAL_INCLUDE_DIR}
)
target_link_libraries(helloworld
    PUBLIC
    ${GDAL_LIBRARY}
)
