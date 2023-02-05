#pragma glslify: noise = require('glsl-noise/simplex/3d')

uniform float time;

void main () {
    float my_noise = noise(vec3(time,time,0));
    gl_FragColor = vec4(my_noise, my_noise, my_noise ,1);
}
