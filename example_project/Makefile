package.json : 
	yarn init -p -y
	yarn add three webpack webpack-cli canvas-sketch canvas-sketch-util glsl-noise glslify glslify-loader

dist/main.js: src/index.js package.json
	yarn webpack

dist/index.html : dist/main.js
	(cd dist; python make_standalone.py)

all : dist/index.html

clean : 
	rm -f dist/index.html dist/main.*
	rm -rf node_modules
	rm -f yarn.lock package.json
