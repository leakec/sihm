project(SIHM_Project)
cmake_minimum_required(VERSION 3.12)

# Source Java files
FILE(GLOB SRC_JS_FILES src/*.js)

# Main target
add_custom_target(index_html ALL
    DEPENDS
        "${CMAKE_BINARY_DIR}/dist/index.html"
)

# Command to build index.html
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

# Command to build main.js
add_custom_command(
    OUTPUT
        "${CMAKE_BINARY_DIR}/dist/main.js"
    COMMAND
        ${CMAKE_COMMAND} -E copy_directory ${CMAKE_SOURCE_DIR}/src ${CMAKE_BINARY_DIR}/src
    COMMAND
        yarn webpack
    DEPENDS
        "${CMAKE_BINARY_DIR}/package.json"
    DEPENDS
        ${SRC_JS_FILES}
)

# Command to build package.json
add_custom_command(
    OUTPUT
        "${CMAKE_BINARY_DIR}/package.json"
    COMMAND
        yarn init -p -y
    COMMAND
        yarn add three webpack webpack-cli dat.gui
)
