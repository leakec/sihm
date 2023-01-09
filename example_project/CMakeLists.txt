project(SIHM_Project)
cmake_minimum_required(VERSION 3.12)

FILE(GLOB SRC_JS_FILES src/*.js)

add_custom_target(my_target
    DEPENDS
        "${CMAKE_BINARY_DIR}/dist/index.html"
)

#add_custom_target(${CMAKE_BINARY_DIR}/dist/index.html
#    DEPENDS
#        "${CMAKE_BINARY_DIR}/dist/main.js"
#)
#add_custom_target(${CMAKE_BINARY_DIR}/dist/index.html
#    DEPENDS
#        "${CMAKE_BINARY_DIR}/dist/main.js"
#)

#add_custom_target(${CMAKE_BINARY_DIR}/dist/main.js
#    DEPENDS
#        "${CMAKE_BINARY_DIR}/package.json"
#    DEPENDS
#        ${SRC_JS_FILES}
#)

add_custom_command(
    OUTPUT
        "${CMAKE_BINARY_DIR}/dist/index.html"
    COMMAND
        ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_SOURCE_DIR}/dist/make_standalone.py ${CMAKE_BINARY_DIR}/dist 
    COMMAND
        ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_SOURCE_DIR}/dist/html_dependent_on_java.html ${CMAKE_BINARY_DIR}/dist 
    COMMAND
        cd ${CMAKE_BINARY_DIR}/dist && python make_standalone.py
    DEPENDS
        "${CMAKE_BINARY_DIR}/dist/main.js"
)

add_custom_command(
    OUTPUT
        "${CMAKE_BINARY_DIR}/package.json"
    COMMAND
        yarn init -p -y
    COMMAND
        yarn add three webpack webpack-cli canvas-sketch canvas-sketch-util glsl-noise glslify glslify-loader
)

add_custom_command(
    OUTPUT
        "${CMAKE_BINARY_DIR}/dist/main.js"
    COMMAND
        ${CMAKE_COMMAND} -E make_directory ${CMAKE_BINARY_DIR}/src
    COMMAND
        ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_SOURCE_DIR}/src/*.js ${CMAKE_BINARY_DIR}/src
    COMMAND
        yarn webpack
    DEPENDS
        "${CMAKE_BINARY_DIR}/package.json"
    DEPENDS
        ${SRC_JS_FILES}
)
