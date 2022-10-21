SRC_JS_FILES = $(wildcard src/*.js)
SRC_TS_FILES = $(wildcard src/*.ts)

package.json : 
	yarn init -p -y
	yarn add three webpack webpack-cli dat.gui

dist/main.js: $(SRC_JS_FILES) $(SRC_TS_FILES) package.json
	yarn webpack

dist/index.html : dist/main.js
	(cd dist; python make_standalone.py)

all : dist/index.html

clean : 
	rm -f dist/index.html dist/main.*
	rm -rf node_modules
	rm -f yarn.lock package.json
