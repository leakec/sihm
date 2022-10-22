import yaml

with open("test.yaml", "r") as f:
    data = yaml.safe_load(f)
_beginning_boilerplate = """
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

// Create controls
const controls = new OrbitControls( camera, renderer.domElement );

// Create instance of mixer
var mixer = new MyMixer(scene);
"""

_ending_boilerplate = """
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
"""

with open("test.js", "w") as f:
    f.write(_beginning_boilerplate)

    # Create objects and animations
    for name, obj in data["OBJECTS"].items():

        # Geometry
        f.write(f"// {name} object\n")
        geo = obj["GEOMETRY"]
        geo_args = ",".join([str(x) for x in geo["ARGS"]])
        f.write(f"var {name}_geometry = new THREE.{geo['FUNCTION']}({geo_args});\n")

        # Material
        mat = obj["MATERIAL"]
        mat_args = ",".join([str(x) for x in mat["ARGS"]])
        f.write(f"var {name}_material = new THREE.{mat['FUNCTION']}({mat_args});\n")

        # Object
        f.write(f"var {name} = new THREE.Mesh({name}_geometry, {name}_material);\n")
        f.write(f"scene.add({name});\n")
        f.write(f"var {name}_uuid = {name}.uuid;\n\n")

        # Create animations
        anim = obj.get("ANIMATIONS", None)
        if anim:
            f.write(f"// {name} animations\n")
        for track, args in anim.items():
            dark = ",".join([str(x) for x in args])
            f.write(
                f"mixer.addKeyframeTrack(new THREE.VectorKeyframeTrack({name}_uuid + '.{track}', {dark}));\n"
            )
        if anim:
            f.write("\n")

    f.write(_ending_boilerplate)
