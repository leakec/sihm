#pragma glslify: noise3 = require(glsl-noise/classic/3d)

varying vec3 pos;
uniform float time;

void main( void ) {

	// Normalized pixel coordinates (from 0 to 1)
    //vec2 uv = (gl_FragCoord.xy*2.-resolution.xy)/resolution.y;
    //vec2 uv = vUv;
    //vec2 uv = gl_FragCoord.xy / resolution.xy;

    float val = noise3(pos/5.0*(time+3.0));
    vec3 purple = vec3(0.62, 0.125, 0.941);

    gl_FragColor = vec4(val*purple, 1.0);
}
