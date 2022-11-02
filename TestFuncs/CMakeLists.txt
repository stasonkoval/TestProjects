cmake_minimum_required(VERSION 3.18)

project(TestFuncs LANGUAGES CXX C)

set(CONAN_FILE_PATH ${CMAKE_CURRENT_LIST_DIR}/.)
include($ENV{UCC_DIR}/../uccutils/cmake/common.cmake)

### C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
if(MSVC)
    string(APPEND CMAKE_CXX_FLAGS " /Zc:__cplusplus")
endif()

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

common_executable(TestFuncs)

target_compile_definitions(TestFuncs PRIVATE
    QT_DEPRECATED_WARNINGS
    DISABLE_VISUALIZER_EDITOR
)


# ==================================
#       Библиотеки
# ==================================
find_package(nlohmann_json REQUIRED)
find_package(utf8cpp REQUIRED)
find_package(uccBase REQUIRED)
target_link_libraries(TestFuncs
    nlohmann_json::nlohmann_json
    utf8cpp::utf8cpp
    uccBase::uccBase
)
if(UNIX)
    target_link_libraries(TestFuncs
        -lresolv
    )
endif()

# ==================================
#  Подключение исходников TestFuncs
# ==================================
target_include_directories(TestFuncs PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/../TestFuncsCommon
)

target_sources(TestFuncs PUBLIC
    #Headers
    ${CMAKE_CURRENT_SOURCE_DIR}/../TestFuncsCommon/pch.h
    ${CMAKE_CURRENT_SOURCE_DIR}/../TestFuncsCommon/ucPch.h

    # Sources
    main.cpp
)
