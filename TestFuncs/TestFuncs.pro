include($(UCC_DIR)/../uccutils/common.pri)

TARGET = TestFuncs
TEMPLATE = app
DESTDIR = $$UCC_BIN_PATH

QT -= gui
QT -= core

CONFIG += c++17 console
CONFIG -= app_bundle

# ==============================
#       Интеграция с conan
# ==============================
CONAN_INSTALL_PATH=$$OUT_PWD
include ($(UCC_DIR)/../uccutils/Dependencies/Dependencies.pri)
conan_link_libraries(nlohmann_json, utfcpp, uccBase)


# ==============================
#           Исходники
# ==============================
include($$PWD/../TestFuncsCommon.pri)

SOURCES += \
        main.cpp \


