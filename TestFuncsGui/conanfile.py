from conans import ConanFile
import os
from enum import Enum

class TestFuncsGuiConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = (
        "nlohmann_json/3.10.4",
        "utfcpp/3.2.1",
        "uccBase/[^0.4.52]"
    )
    generators = "cmake", "cmake_find_package"