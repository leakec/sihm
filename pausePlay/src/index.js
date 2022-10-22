import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { MyGui} from './gui'
import { MyMixer } from './animator'

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
const geometry2 = new THREE.BoxGeometry( 1, 1, 1, 4, 4, 4);
const material = new THREE.MeshBasicMaterial( { color: 0xffff00 } );
const material2 = new THREE.MeshBasicMaterial( { color: 0xffff00 } );
const sphere = new THREE.Mesh( geometry, material , name="sphere");
const box = new THREE.Mesh( geometry2, material2 ,name="box");

// Create controls
const controls = new OrbitControls( camera, renderer.domElement );

// Add geometry to scene for anmiation
scene.add(sphere);
scene.add(box);

// Create instance of mixer
var mixer = new MyMixer(scene);

const box_uuid = box.uuid;
const sphere_uuid=sphere.uuid;

// POSITION
mixer.addKeyFrameTrack(new THREE.VectorKeyframeTrack( box_uuid+'.position', [ 0, 1], [ 0, 0, 0, -1, 0, 0] ));
mixer.addKeyFrameTrack(new THREE.VectorKeyframeTrack( sphere_uuid+'.position', [ 0, 1, 2 ], [ 0, 0, 0, 30, 0, 0, 0, 0, 0 ] ));

// SCALE
mixer.addKeyFrameTrack(new THREE.VectorKeyframeTrack( sphere_uuid+'.scale', [ 0, 1, 2 ], [ 1, 1, 1, 2, 2, 2, 1, 1, 1 ] ));

// ROTATION
var xAxis = new THREE.Vector3( 1, 0, 0 );

var qInitial = new THREE.Quaternion().setFromAxisAngle( xAxis, 0 );
var qFinal = new THREE.Quaternion().setFromAxisAngle( xAxis, Math.PI );
mixer.addKeyFrameTrack(new THREE.QuaternionKeyframeTrack( box_uuid+'.quaternion', [ 0, 1, 2 ], [ qInitial.x, qInitial.y, qInitial.z, qInitial.w, qFinal.x, qFinal.y, qFinal.z, qFinal.w, qInitial.x, qInitial.y, qInitial.z, qInitial.w ] ));

// COLOR
mixer.addKeyFrameTrack(new THREE.ColorKeyframeTrack( sphere_uuid+'.material.color', [ 0, 1, 2 ], [ 1, 0, 0, 0, 1, 0, 0, 0, 1 ], THREE.InterpolateDiscrete ));

// OPACITY
mixer.addKeyFrameTrack(new THREE.NumberKeyframeTrack( sphere_uuid + '.material.opacity', [ 0, 1, 2 ], [ 1, 0, 1 ] ));

// Lock the mixer (this generates the clip and clip action)
mixer.lock();

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
gui.add_video_controls(pause_play, set_time, mixer.clipAction)

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
		gui.update_time()
	}
}

controls.update()
render()
