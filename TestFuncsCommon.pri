INCLUDEPATH += $$PWD

HEADERS += \
    $$PWD/pch.h \
    $$PWD/ucPch.h \

unix: {
LIBS += -lpthread  \
        -ldl \
        -lldap \
        -llber \
        -lkrb5 \
        -lresolv \
}
