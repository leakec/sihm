#pragma glslify: noise3 = require(glsl-noise/classic/3d)

uniform float time;
varying vec2 vUv;
uniform sampler2D utexture1;

void main() {
    
    vec3 pHat = normalize(position);
    vec3 v = vec3(pHat.x + time * 0.5,
                  pHat.y + time * 0.3,
                  pHat.z + time * 0.8);
    float val = 10.0 + noise3(v) * 2.0;
    vec3 pNew = pHat*val;
    gl_Position = projectionMatrix * modelViewMatrix * vec4( pNew, 1.0 );

    vUv = uv;
}
