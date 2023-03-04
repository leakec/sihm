uniform sampler2D utexture1;
varying vec2 vUv;

void main() {
  gl_FragColor = texture2D(utexture1, vUv);
}
