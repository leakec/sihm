import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import { MyGui } from "./gui";
import { MyMixer } from "./animator";
import { MyCamera } from "./camera";

// Create renderer
var renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Create scene
const scene = new THREE.Scene();

// Create camera
var camera_per = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000,
);
camera_per.position.z = 25;

// Create geometry
const geometry = new THREE.SphereGeometry(1, 30, 30);
const geometry2 = new THREE.BoxGeometry(1, 1, 1, 4, 4, 4);
const material = new THREE.MeshBasicMaterial({
    color: 0xffff00,
    wireframe: true,
    wireframeLinewidth: 2,
});
const material2 = new THREE.MeshBasicMaterial({
    color: 0x00ff00,
    opacity: 0.5,
    reflectivity: 0.5,
    wireframe: true,
    wireframeLinewidth: 2,
});

const sphere = new THREE.Mesh(geometry, material);
sphere.name = "sphere";
const box = new THREE.Mesh(geometry2, material2);
box.name = "box";

// Create controls
const controls = new OrbitControls(camera_per, renderer.domElement);

// Add geometry to scene for anmiation
scene.add(sphere);
scene.add(box);

const camera = new MyCamera(scene, camera_per);

// Add geometry to camera
camera.addFollowableObjects([sphere, box]);

// Create instance of mixer
const mixer = new MyMixer(scene);

const box_uuid = box.uuid;
const sphere_uuid = sphere.uuid;

// POSITION
mixer.addKeyframeTrack(
    new THREE.VectorKeyframeTrack(
        box_uuid + ".position",
        [0, 1],
        [0, 0, 0, -1, 0, 0],
    ),
);
mixer.addKeyframeTrack(
    new THREE.VectorKeyframeTrack(
        sphere_uuid + ".position",
        [0, 1, 2],
        [0, 0, 0, 30, 0, 0, 0, 0, 0],
    ),
);

// SCALE
mixer.addKeyframeTrack(
    new THREE.VectorKeyframeTrack(
        sphere_uuid + ".scale",
        [0, 1, 2],
        [1, 1, 1, 2, 2, 2, 1, 1, 1],
    ),
);

// ROTATION
var yAxis = new THREE.Vector3(0, 1, 0);

var qInitial = new THREE.Quaternion().setFromAxisAngle(yAxis, 0);
var qFinal = new THREE.Quaternion().setFromAxisAngle(yAxis, Math.PI);
mixer.addKeyframeTrack(
    new THREE.QuaternionKeyframeTrack(
        box_uuid + ".quaternion",
        [0, 1, 2],
        [
            qInitial.x,
            qInitial.y,
            qInitial.z,
            qInitial.w,
            qFinal.x,
            qFinal.y,
            qFinal.z,
            qFinal.w,
            qInitial.x,
            qInitial.y,
            qInitial.z,
            qInitial.w,
        ],
    ),
);

// COLOR
mixer.addKeyframeTrack(
    new THREE.ColorKeyframeTrack(
        sphere_uuid + ".material.color",
        [0, 1, 2],
        [1, 0, 0, 0, 1, 0, 0, 0, 1],
        THREE.InterpolateDiscrete,
    ),
);

// OPACITY
mixer.addKeyframeTrack(
    new THREE.NumberKeyframeTrack(
        sphere_uuid + ".material.opacity",
        [0, 1, 2],
        [1, 0, 1],
    ),
);

// Lock the mixer (this generates the clip and clip action)
mixer.lock();

// Create basic video functions and variables
var paused = false;
function pause_play() {
    if (paused) {
        paused = false;
        clock.start();
        gui.play();
    } else {
        paused = true;
        clock.stop();
        gui.pause();
    }
}
function set_time(value) {
    mixer.setTime(value);
}

// Create GUI
const gui = new MyGui();
gui.addVideoControls(pause_play, set_time, mixer.clip_action);
gui.addCameraControls(camera);

const clock = new THREE.Clock();

// Render Loop
var render = function () {
    // Render scene
    requestAnimationFrame(render);
    animate();
    renderer.render(scene, camera_per);
};

//TESTING
//scene.traverse( function ( obj ) {
//
//	var s = '|___';
//
//	var obj2 = obj;
//
//	while ( obj2 !== scene ) {
//
//		s = '\t' + s;
//
//		obj2 = obj2.parent;
//
//	}
//
//	console.log( s + obj.name + ' <' + obj.type + '>' );
//
//} );
////box.add(camera.camera);
//scene.traverse( function ( obj ) {
//
//	var s = '|___';
//
//	var obj2 = obj;
//
//	while ( obj2 !== scene ) {
//
//		s = '\t' + s;
//
//		obj2 = obj2.parent;
//
//	}
//
//	console.log( s + obj.name + ' <' + obj.type + '>' );
//
//} );

// Animation
function animate() {
    if (!paused) {
        // Update animation
        var delta = clock.getDelta();
        mixer.update(delta);
        gui.update_time();
        camera.update();

		//TESTING
		//console.log("box: "+box.quaternion);

        // See: https://stemkoski.github.io/Three.js/Chase-Camera.html
        // See: http://stemkoski.github.io/Three.js/
    }
}

controls.update();
render();
