cmake_minimum_required(VERSION 3.24)
project(linuxCLI-cmake)

find_package(Python3 COMPONENTS Interpreter Development)

function(add_python_wheel)
    add_custom_target(Wheel
            COMMAND ${PYTHON_EXECUTABLE} main.py 
            WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
endfunction()