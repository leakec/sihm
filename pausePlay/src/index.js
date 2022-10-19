import * as THREE from 'three';
// create a keyframe track (i.e. a timed sequence of keyframes) for each animated property
// Note: the keyframe track type should correspond to the type of the property being animated

// Create renderer
var renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize( window.innerWidth, window.innerHeight );
document.body.appendChild( renderer.domElement );

// Create scene
const scene = new THREE.Scene();

// Create camera
var camera = new THREE.PerspectiveCamera( 75, window.innerWidth/window.innerHeight, 0.1, 1000 );
camera.position.z = 4;

// Create geometry
const geometry = new THREE.SphereGeometry( 1, 30, 30 );
const material = new THREE.MeshBasicMaterial( { color: 0xffff00 } );
const sphere = new THREE.Mesh( geometry, material );

// Add geometry to scene
scene.add( sphere );

// POSITION
var positionKF = new THREE.VectorKeyframeTrack( '.position', [ 0, 1, 2 ], [ 0, 0, 0, 30, 0, 0, 0, 0, 0 ] );

// SCALE
var scaleKF = new THREE.VectorKeyframeTrack( '.scale', [ 0, 1, 2 ], [ 1, 1, 1, 2, 2, 2, 1, 1, 1 ] );

// ROTATION
// Rotation should be performed using quaternions, using a QuaternionKeyframeTrack
// Interpolating Euler angles (.rotation property) can be problematic and is currently not supported

// set up rotation about x axis
var xAxis = new THREE.Vector3( 1, 0, 0 );

var qInitial = new THREE.Quaternion().setFromAxisAngle( xAxis, 0 );
var qFinal = new THREE.Quaternion().setFromAxisAngle( xAxis, Math.PI );
var quaternionKF = new THREE.QuaternionKeyframeTrack( '.quaternion', [ 0, 1, 2 ], [ qInitial.x, qInitial.y, qInitial.z, qInitial.w, qFinal.x, qFinal.y, qFinal.z, qFinal.w, qInitial.x, qInitial.y, qInitial.z, qInitial.w ] );

// COLOR
var colorKF = new THREE.ColorKeyframeTrack( '.material.color', [ 0, 1, 2 ], [ 1, 0, 0, 0, 1, 0, 0, 0, 1 ], THREE.InterpolateDiscrete );

// OPACITY
var opacityKF = new THREE.NumberKeyframeTrack( '.material.opacity', [ 0, 1, 2 ], [ 1, 0, 1 ] );

// create an animation sequence with the tracks
// If a negative time value is passed, the duration will be calculated from the times of the passed tracks array
var clip = new THREE.AnimationClip( 'Action', 3, [ scaleKF, positionKF, quaternionKF, colorKF, opacityKF ] );

//TODO: Fix this
// setup the AnimationMixer
//var mixer = new THREE.AnimationMixer( mesh );
//
//// create a ClipAction and set it to play
//var clipAction = mixer.clipAction( clip );
//clipAction.play();
//
//const clock = new THREE.Clock();

// Render Loop
var render = function () {
  requestAnimationFrame( render );
//var delta = 0.75 * clock.getDelta();
//mixer.update( delta );
// Your animated code goes here
renderer.render(scene, camera);
};

render();
