SRC_JS_FILES = $(wildcard src/*.js)

package.json : 
	yarn init -p -y
	yarn add three webpack webpack-cli dat.gui

dist/main.js: $(SRC_JS_FILES) package.json
	yarn webpack

dist/index.html : dist/main.js
	(cd dist; python make_standalone.py)

all : dist/index.html

clean : 
	rm -f dist/index.html dist/main.*
	rm -rf node_modules
	rm -f yarn.lock package.json
	rm -f $(CLEAN_JS_FILES)
	rm -f src/index.js
