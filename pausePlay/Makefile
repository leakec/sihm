SRC_JS_FILES = $(wildcard src/*.js)
SRC_TS_FILES = $(wildcard src/*.ts)
CLEAN_JS_FILES = $(SRC_TS_FILES:.ts=.js)
SRC_JS_FILES += $(CLEAN_JS_FILES)


%.js: %.ts package.json
	yarn tsc -t es6 $<

package.json : 
	yarn init -p -y
	yarn add three webpack webpack-cli dat.gui @types/three @types/dat.gui typescript

dist/main.js: package.json $(SRC_JS_FILES) $(SRC_TS_FILES)
	yarn webpack

dist/index.html : dist/main.js
	(cd dist; python make_standalone.py)

all : dist/index.html

clean : 
	rm -f dist/index.html dist/main.*
	rm -rf node_modules
	rm -f yarn.lock package.json
	rm -f $(CLEAN_JS_FILES)
