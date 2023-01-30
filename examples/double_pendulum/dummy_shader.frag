#pragma glslify: noise = require('glsl-noise/simplex/3d')

void main () {
    gl_FragColor = vec4(noise(1),1);
}
