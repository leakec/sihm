import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
//import { GUI } from 'dat.gui'
import { MyGui} from './gui'

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
camera.position.z = 25;

// Create geometry
const geometry = new THREE.SphereGeometry( 1, 30, 30 );
const material = new THREE.MeshBasicMaterial( { color: 0xffff00 } );
const sphere = new THREE.Mesh( geometry, material );

// Create controls
const controls = new OrbitControls( camera, renderer.domElement );

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
var clip = new THREE.AnimationClip( 'Action', -1, [ scaleKF, positionKF, quaternionKF, colorKF, opacityKF ] );
clip.resetDuration()

// setup the AnimationMixer
var mixer = new THREE.AnimationMixer( sphere );

// create a ClipAction and set it to play
var clipAction = mixer.clipAction( clip );
clipAction.play();

// Create basic video functions and variables
var paused = false;
function pause_play() {
	if (paused)
	{
		paused = false;
		clock.start();
		gui.play();
	} 
	else
	{
		paused = true;
		clock.stop();
		gui.pause();
	}
}
function set_time(value) {
	mixer.setTime(value);
}

// Create GUI
const gui = new MyGui()
gui.add_video_controls(pause_play, set_time, clip.duration)
//const gui = new GUI()
//const video_controls = gui.addFolder('Video controls')
//var pausePlay = video_controls.add({"Pause/Play": pause_play}, "Pause/Play");
//pausePlay.name("\u23F8")
//var time_slider = video_controls.add({"Time": time}, "Time", 0.0, clip.duration);
//time_slider.onChange(set_time);
//video_controls.open()


const clock = new THREE.Clock();

// Render Loop
var render = function () {
	// Render scene
	requestAnimationFrame( render );
	animate();
	renderer.render(scene, camera);
};

// Animation
function animate() {
	if (!paused)
	{
		// Update animation
		var delta = 0.75 * clock.getDelta();
		mixer.update( delta );
		gui.update_time(delta)
	}
}

controls.update()
render()
