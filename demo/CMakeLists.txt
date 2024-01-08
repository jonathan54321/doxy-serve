set(CMAKE_C_COMPILER clang)
set(CMAKE_CXX_COMPILER clang++)

cmake_minimum_required(VERSION 3.18)
set(APP_NAME "demo")
project("${APP_NAME}")

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -std=c++20 -Wno-multichar")


include_directories(
    "src"
)

set(SOURCES 
    src/main.cpp
    src/demo.cpp )

add_executable("${APP_NAME}" ${SOURCES})


include(FetchContent)
FetchContent_Declare(
  awesome-doxygen
  GIT_REPOSITORY https://github.com/jothepro/doxygen-awesome-css
  GIT_TAG v2.3.1
)
FetchContent_MakeAvailable(awesome-doxygen)

find_package(Doxygen)
set(DOXYGEN_INPUT_LIST 
    ${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/demo.h
    ${CMAKE_CURRENT_SOURCE_DIR}/src/demo.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/demo.cpp)
list(TRANSFORM DOXYGEN_INPUT_LIST PREPEND "                                " )
list(TRANSFORM DOXYGEN_INPUT_LIST APPEND " \\" )
string(REPLACE ";" "\n" DOXYGEN_INPUTS "${DOXYGEN_INPUT_LIST}")

set(DOXYGEN_OUTPUT_DIR ${CMAKE_CURRENT_BINARY_DIR}/docs/doxygen)
set(DOXYGEN_INDEX_FILE ${DOXYGEN_OUTPUT_DIR}/html/index.html)
set(DOXYGEN_HEADER_PATH ${CMAKE_CURRENT_SOURCE_DIR}/docs/header.html)
set(DOXYFILE_IN ${CMAKE_CURRENT_SOURCE_DIR}/docs/Doxyfile.in)
set(DOXYHEADER_IN ${CMAKE_CURRENT_SOURCE_DIR}/docs/header.html.in)
set(DOXYFILE_OUT ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile)
set(DOXYHEADER_OUT ${CMAKE_CURRENT_BINARY_DIR}/header.html)
set(DOXYGEN_CSS_FILE ${CMAKE_CURRENT_BINARY_DIR}/_deps/awesome-doxygen-src/doxygen-awesome.css)

if(NOT DEFINED APP_VERSION)
    set(APP_VERSION main)
endif()

configure_file(${DOXYFILE_IN} ${DOXYFILE_OUT} @ONLY)
configure_file(${DOXYHEADER_IN} ${DOXYHEADER_OUT} @ONLY)

file(MAKE_DIRECTORY ${DOXYGEN_OUTPUT_DIR}/html) 

add_custom_command(TARGET ${APP_NAME} 
                   POST_BUILD
                   COMMAND ${DOXYGEN_EXECUTABLE} ${DOXYFILE_OUT}
                   COMMAND zip -r ${CMAKE_CURRENT_BINARY_DIR}/html-${APP_VERSION}.zip .
                   WORKING_DIRECTORY ${DOXYGEN_OUTPUT_DIR}/html
                   MAIN_DEPENDENCY ${DOXYFILE_OUT} ${DOXYFILE_IN}
                   COMMENT "Generating docs...")
