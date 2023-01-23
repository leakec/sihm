import os
from typing import Dict, Any, Set, List, Union
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
        self._cfg_path = cfg_file.parents[0]
        self._readData(cfg_file)
        self._file = open(fileName, "w+")
        self._path = Path(fileName.replace("index.js", ""))
        self._extra_imports: Set[str] = set()
        self._extra_beginning_boilerplate: Set[str] = set()
        self._file_dict = {}
        self._extra_file_count = 0

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

    def _append_to_file(self, pos: int, text: str) -> None:
        """
        Append text to position in self._file.

        Parameters
        ----------
        pos : int
            Position in file.
        text : str
            Text to append.
        """

        curr_pos = self._file.tell()
        self._file.seek(pos)
        old_text = self._file.readlines()
        self._file.seek(pos)
        self._file.write(text)
        self._file.writelines(old_text)
        self._file.seek(curr_pos)

    def _readMtlFile(self, file: str) -> str:
        import base64

        """
        Reads the data of an MTL file, and embeds any images as base64.

        Parameters
        ----------
        file : str
            Name of the file to read.

        Returns
        -------
        str
            Text of the MTL file, with any images embedded as base64.
        """
        base = Path(file).parents[0]
        with open(file, "r") as f:
            text = f.readlines()
        for k, line in enumerate(text):
            if "map_" in line:
                pieces = line.split(" ")
                img_file = Path(os.path.join(base, pieces[1]))
                suffix = img_file.suffix[1:]
                with open(img_file, "rb") as f:
                    encoded_string = base64.b64encode(f.read())
                text[k] = (
                    pieces[0]
                    + " "
                    + "data:image/"
                    + suffix
                    + ";base64,"
                    + encoded_string.decode("utf-8")
                )

        return "".join(text)

    def _addExtraFile(self, file: Union[str, Path]) -> str:
        """
        Adds file to _file_dict if it does not exist. This entails
        creating a SIHM_EXTRA_FILE_*.js file that contains a single string
        SIHM_EXTRA_FILE* that contains the text of the file. This allows us
        to webpack everything in that file later on without any external
        resources. If an entry for this file already exits in _file_dict,
        then we just return that entry.

        Parameters
        ----------
        file : str
            Name of the file to add.

        Returns
        -------
        str
            Name of the SIHM_EXTRA_FILE_* variable name.
        """

        if file not in self._file_dict:
            name = f"SIHM_EXTRA_FILE_{self._extra_file_count}"
            name_js = f"{name}.js"
            new_file = os.path.join(self._path, name_js)
            self._file_dict[file] = name
            if Path(file).suffix[1:] == "mtl":
                # Handle material files seperately, as we may need to
                # embed images into them.
                text = self._readMtlFile(file)
            else:
                with open(file, "r") as f:
                    text = f.read()
            with open(new_file, "w") as f:
                f.write(f"export const {name} = `\n")
                f.write(text)
                f.write("\n`;")

            self._extra_file_count += 1

            return name
        else:
            return self._file_dict[file]

    def _writeMaterialFile(self):
        pass

    def _processArgs(self, args: Union[List[Any], Dict[Any, Any]]) -> str:
        """
        Take arguments and return them as a string ready to be passed into a JavaScript function.

        Parameters
        ----------
        args : Union[List[Any], Dict[Any, Any]]
            Function arguments in list or dictionary form.

        Returns
        -------
        str
            Arguments as a string ready to be passed into a JavaScript function.
        """
        if isinstance(args, dict):
            return ",".join([f"{k}: {v}" for k, v in args.items()])
        else:
            return ",".join([str(x) for x in args])

    def _createLight(self, name: str, light: Dict[Any, Any], parent="scene") -> None:
        if light.get("FUNCTION", None):
            light_args = self._processArgs(light["ARGS"])
            self._file.write(f"var {name}_light = new THREE.{light['FUNCTION']}({light_args});\n")
            self._file.write(f"{parent}.add({name}_light);\n")

            if light.get("POSITION", None):
                pos = self._processArgs(light["POSITION"])
                self._file.write(f"{name}_light.position.set({pos});\n")

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
        mat = obj.get("MATERIAL", None)

        # Material
        if mat:
            if mat.get("FILE", None):
                js_name = self._addExtraFile(
                    self._cfg_path.joinpath(Path(obj["MATERIAL"]["FILE"])).resolve()
                )
                self._extra_imports.add(
                    "import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader';\n"
                )
                self._extra_imports.add(
                    "import { MTLLoader } from 'three/examples/jsm/loaders/MTLLoader';\n"
                )
                self._extra_imports.add("import { " + js_name + " } from './" + js_name + "';\n")
                self._extra_beginning_boilerplate.add("const OBJ_LOADER = new OBJLoader();\n")
                self._extra_beginning_boilerplate.add("const MTL_LOADER = new MTLLoader();\n")
                self._file.write(f"OBJ_LOADER.setMaterials(MTL_LOADER.parse({js_name}));\n")

            elif mat.get("FUNCTION", None):

                # Setup function arguments
                if mat["FUNCTION"] == "ShaderMaterial":
                    # ShaderMaterial is a special case, since the user may point to files that store
                    # the vertex and fragment shader rather than passing in strings.
                    args = mat["ARGS"]
                    if isinstance(args, dict):
                        vs = args.get("vertexShader", None)
                        fs = args.get("fragmentShader", None)
                        if vs is not None:
                            if "main()" not in vs:
                                # User has given vertex shader as a file
                                # Add this to the list of known files and save as a java variable.
                                js_name = self._addExtraFile(
                                    self._cfg_path.joinpath(Path(vs)).resolve()
                                )
                                self._extra_imports.add(
                                    "import { " + js_name + " } from './" + js_name + "';\n"
                                )
                                args["vertexShader"] = js_name
                        if fs is not None:
                            if "main()" not in fs:
                                # User has given fragment shader as a file
                                # Add this to the list of known files and save as a java variable.
                                js_name = self._addExtraFile(
                                    self._cfg_path.joinpath(Path(fs)).resolve()
                                )
                                self._extra_imports.add(
                                    "import { " + js_name + " } from './" + js_name + "';\n"
                                )
                                args["fragmentShader"] = js_name
                    else:
                        raise ValueError(
                            "Arguments to ShaderMaterial must be given as a dictionary."
                        )
                    mat_args = "{" + self._processArgs(args) + "}"
                else:
                    mat_args = self._processArgs(mat["ARGS"])

                # Create material
                self._file.write(
                    f"var {name}_material = new THREE.{mat['FUNCTION']}({mat_args});\n"
                )

        # Geometry
        if geo:
            if geo.get("FUNCTION", None):
                geo_args = self._processArgs(geo["ARGS"])
                self._file.write(
                    f"var {name}_geometry = new THREE.{geo['FUNCTION']}({geo_args});\n"
                )

                # Object
                if mat:
                    self._file.write(
                        f"var {name} = new THREE.Mesh({name}_geometry, {name}_material);\n"
                    )
                else:
                    self._file.write(f"var {name} = new THREE.Mesh({name}_geometry);\n")

            elif geo.get("FILE", None):
                js_name = self._addExtraFile(self._cfg_path.joinpath(Path(geo["FILE"])).resolve())
                self._extra_imports.add(
                    "import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader';\n"
                )
                self._extra_imports.add("import { " + js_name + " } from './" + js_name + "';\n")
                self._extra_beginning_boilerplate.add("const OBJ_LOADER = new OBJLoader();\n")

                # Object
                self._file.write(f"var {name} = OBJ_LOADER.parse({js_name});\n")

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
                    if track == "quaternion":
                        self._file.write(
                            f"mixer.addKeyframeTrack(new THREE.QuaternionKeyframeTrack({name}_uuid + '.{track}', {dark}));\n"
                        )
                    else:
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
        from io import SEEK_END

        # Write beginning boilerplate
        self._file.write(self._imports)
        loc = self._file.tell()
        self._file.write(self._beginning_boilerplate)

        # Create objects and animations
        for name, obj in self._data["OBJECTS"].items():
            self._createObject(name, obj, parent="scene")

        # Create lights
        for name, light in self._data["LIGHTS"].items():
            self._createLight(name, light, parent="scene")

        # Add in extra beginning boilerplate.
        # this must be done after calling _createObject, since
        # that is the function that adds this boilerplate.
        lines = "".join(self._extra_imports) + "".join(self._extra_beginning_boilerplate)
        self._append_to_file(loc, lines)
        self._file.seek(0, SEEK_END)

        # Write ending boilerplate
        self._file.write(self._ending_boilerplate)
