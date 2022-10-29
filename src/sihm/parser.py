from typing import Dict, Any, IO, Set
from pathlib import Path


class SihmParser:

    _imports = """
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import { MyGui } from "./gui";
import { MyMixer } from "./animator";
import { MyCamera } from "./camera";
"""

    _beginning_boilerplate = """
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

    def __init__(self, cfg_file: Path, fileName: str) -> None:
        """
        Initialize the parser.

        Parameters
        ----------
        cfg_file : Path
            Input config file.
        fileName : str
            Output file name.
        """
        self._readData(cfg_file)
        self._file = open(fileName, "w")
        self._extra_beginning_boilerplate: Set[str] = {}

    def __del__(self) -> None:
        self._file.close()

    def _readData(self, cfg_file: Path):
        """
        Read the data from a config file. The file exention is used to determine file type.
        Defaults to YAML if no extension is recognized.

        Parameters
        ----------
        cfg_file : Path
            Input config file.
        """

        ext = cfg_file.suffix
        if ext in [".ini", ".cfg"]:
            from configobj import ConfigObj

            self._data = ConfigObj(infile=cfg_file, file_error=True).dict()
        elif ext == ".json":
            import json

            with open(cfg_file, "r") as f:
                self._data = json.load(f)
        else:
            import yaml

            with open(cfg_file, "r") as f:
                self._data = yaml.load(f, Loader=yaml.FullLoader)

    def _createObject(self, name: str, obj: Dict[Any, Any], parent="scene") -> None:
        """
        Creates object and children.

        Parameters
        ----------
        name : str
            Name of the object.
        obj : Dict[Any, Any]
            Object data.
        parent : str
            Name of the object's parent in the scene graph.
        """

        self._file.write(f"// {name} object\n")
        geo = obj.get("GEOMETRY", None)
        if geo:
            # Geometry
            if geo.get("FUNCTION", None):
                geo_args = ",".join([str(x) for x in geo["ARGS"]])
                self._file.write(
                    f"var {name}_geometry = new THREE.{geo['FUNCTION']}({geo_args});\n"
                )

                # Material
                mat = obj["MATERIAL"]
                mat_args = ",".join([str(x) for x in mat["ARGS"]])
                self._file.write(
                    f"var {name}_material = new THREE.{mat['FUNCTION']}({mat_args});\n"
                )

                # Object
                self._file.write(
                    f"var {name} = new THREE.Mesh({name}_geometry, {name}_material);\n"
                )
            elif geo.get("FILE", None):
                # Object
                self._extra_beginning_boilerplate.add("const OBJ_LOADER = new OBJLoader();\n")
                self._file.write(
                    f"var {name} = new THREE.Mesh({name}_geometry, {name}_material);\n"
                )

            # Add object to parent and get uuid
            self._file.write(f'{name}.name = "{name}"\n')
            self._file.write(f"{parent}.add({name});\n")
            self._file.write(f"var {name}_uuid = {name}.uuid;\n\n")

            # Add object to followable objects
            self._file.write(f"followable_objects.push({name});\n\n")

            # Create animations
            anim = obj.get("ANIMATIONS", None)
            if anim:
                self._file.write(f"// {name} animations\n")
                for track, args in anim.items():
                    dark = ",".join([str(x) for x in args])
                    self._file.write(
                        f"mixer.addKeyframeTrack(new THREE.VectorKeyframeTrack({name}_uuid + '.{track}', {dark}));\n"
                    )
                self._file.write("\n")

        # Add children
        if obj.get("CHILDREN", None):
            for child_name, child_obj in obj["CHILDREN"].items():
                self._createObject(child_name, child_obj, parent=f"{name}")

    def write_file(self):
        """
        Write the JavaScript ThreeJS file.
        """

        # Write beginning boilerplate
        self._file.write(self._imports)
        for line in self._extra_beginning_boilerplate:
            self._file.write(line)
        self._file.write(self._beginning_boilerplate)

        # Create objects and animations
        for name, obj in self._data["OBJECTS"].items():
            self._createObject(name, obj, parent="scene")

        # Write ending boilerplate
        self._file.write(self._ending_boilerplate)
