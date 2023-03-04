project(SIHM_Project)
cmake_minimum_required(VERSION 3.17)

# Copying this so it doesn't stay in main directory
file(COPY cmake/CMakeGraphVizOptions.cmake DESTINATION ${CMAKE_BINARY_DIR})

# Source Java files
FILE(GLOB SRC_JS_FILES ${CMAKE_SOURCE_DIR}/src/*.js)

# Main target
add_custom_target(index_html ALL
    DEPENDS
        "${CMAKE_BINARY_DIR}/dist/index.html"
)

add_custom_target(base_yarn_pkg
    DEPENDS
        ${CMAKE_BINARY_DIR}/src
)

# Extra modules
set(EXTRA_MODULES "")

# Glslify files
set(GLSLIFY_FILES)

# Output glslify files
set(GLSLIFY_OUTPUT_FILES)

foreach(FILE ${GLSLIFY_FILES})
    add_custom_command(
        OUTPUT 
            ${CMAKE_BINARY_DIR}/src/${FILE}
        COMMAND
            ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_SOURCE_DIR}/src/${FILE} ${CMAKE_BINARY_DIR}/src/${FILE}
        COMMAND 
            ${CMAKE_BINARY_DIR}/node_modules/glslify/bin.js ${CMAKE_BINARY_DIR}/src/${FILE} -o ${CMAKE_BINARY_DIR}/src/${FILE}
        COMMAND 
            python ${CMAKE_SOURCE_DIR}/utils/fix_glsl_file.py -f ${CMAKE_BINARY_DIR}/src/${FILE}
        DEPENDS
            base_yarn_pkg
            ${CMAKE_SOURCE_DIR}/src/${FILE}
    )
    LIST(APPEND GLSLIFY_OUTPUT_FILES ${CMAKE_BINARY_DIR}/src/${FILE})
endforeach()

# Yarn package
add_custom_target(yarn_pkg
    DEPENDS
        ${GLSLIFY_OUTPUT_FILES}
)

add_dependencies(yarn_pkg base_yarn_pkg)

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
        yarn webpack
    DEPENDS
        yarn_pkg
    DEPENDS
        ${SRC_JS_FILES}
)

# Command to build base yarn package
add_custom_command(
    OUTPUT
        "${CMAKE_BINARY_DIR}/src"
    COMMAND
        ${CMAKE_COMMAND} -E copy_directory ${CMAKE_SOURCE_DIR}/src ${CMAKE_BINARY_DIR}/src
    COMMAND 
        ${CMAKE_COMMAND} -E remove -f ${GLSLIFY_OUTPUT_FILES} VERBATIM
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
        yarn add three webpack webpack-cli dat.gui ${EXTRA_MODULES} VERBATIM
)
