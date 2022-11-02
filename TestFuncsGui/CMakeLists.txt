cmake_minimum_required(VERSION 3.18)

project(TestFuncsGui LANGUAGES CXX C)

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

common_executable(TestFuncsGui)

target_compile_definitions(TestFuncsGui PRIVATE
    QT_DEPRECATED_WARNINGS
    DISABLE_VISUALIZER_EDITOR
)

# ==================================
#       Библиотеки
# ==================================
find_package(Qt5 COMPONENTS Core Gui Widgets REQUIRED)
find_package(nlohmann_json REQUIRED)
find_package(utf8cpp REQUIRED)
find_package(uccBase REQUIRED)
target_link_libraries(TestFuncsGui
    Qt5::Core
    Qt5::Gui
    Qt5::Widgets

    nlohmann_json::nlohmann_json
    utf8cpp::utf8cpp
    uccBase::uccBase
)
if(UNIX)
    target_link_libraries(TestFuncsGui
        -lresolv
    )
endif()

# ==================================
#  Подключение исходников TestFuncsGui
# ==================================
set(UI_FILES
    MainWindow.ui
)

target_include_directories(TestFuncsGui PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/../TestFuncsCommon
)

target_sources(TestFuncsGui PUBLIC
    #Headers
    ${CMAKE_CURRENT_SOURCE_DIR}/../TestFuncsCommon/pch.h
    ${CMAKE_CURRENT_SOURCE_DIR}/../TestFuncsCommon/ucPch.h
    MainWindow.h

    # Sources
    MainWindow.cpp
    main.cpp

    # UI Files
    ${UI_FILES}
)

set_ui_search_paths_for_target(TestFuncsGui UI_FILES ${UI_FILES})

source_group("Forms"
    FILES ${UI_FILES}
)
