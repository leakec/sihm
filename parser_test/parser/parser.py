import yaml

with open("test.yaml", "r") as f:
    data = yaml.safe_load(f)
_beginning_boilerplate = """
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

// Create controls
const controls = new OrbitControls(camera_per, renderer.domElement);

// Create instance of mixer
const mixer = new MyMixer(scene);

// Add camera
const camera = new MyCamera(scene, camera_per);

// Followable objects
var followable_objects = [];

"""

_ending_boilerplate = """
// Add geometry to camera
camera.addFollowableObjects(followable_objects);

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

// Create GUI
const gui = new MyGui();
gui.addVideoControls(pause_play, mixer);
gui.addCameraControls(camera);

const clock = new THREE.Clock();

// Render Loop
var render = function () {
    // Render scene
    requestAnimationFrame(render);
    animate();
    renderer.render(scene, camera_per);
};

// Animation
function animate() {
    if (!paused) {
        // Update animation
        var delta = clock.getDelta();
        mixer.update(delta);
        gui.updateTime();
        camera.update();
    }
}

controls.update();
render();
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
        f.write(f'{name}.name = "{name}"\n')
        f.write(f"scene.add({name});\n")
        f.write(f"var {name}_uuid = {name}.uuid;\n\n")

        # Add objects to followable objects
        f.write(f"followable_objects.push({name});\n\n")

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
