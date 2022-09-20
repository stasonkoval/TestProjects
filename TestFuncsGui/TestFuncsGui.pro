include($(UCC_DIR)/../uccutils/common.pri)

TARGET = TestFuncsGui
TEMPLATE = app
DESTDIR = $$UCC_BIN_PATH

QT += core gui widgets
CONFIG += c++17

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

HEADERS += \
    MainWindow.h

SOURCES += \
    main.cpp \
    MainWindow.cpp

FORMS += \
    MainWindow.ui



