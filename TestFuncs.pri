win32: PROJECTS_PATH = C:/Projects
unix:  PROJECTS_PATH = /home/user/Projects

INCLUDEPATH += \
    $$PWD \
    $$PROJECTS_PATH/uccbase/uccCore/include \

HEADERS += \
    $$PWD/pch.h \
    $$PROJECTS_PATH/uccbase/uccCore/include/ucc/core/ucTypes.h \
    $$PROJECTS_PATH/uccbase/uccCore/include/ucc/core/ucMisc.h \

unix: {
LIBS += -lpthread  \
        -ldl \
        -lldap \
        -llber \
        -lkrb5 \
        -lresolv \
}
