import os
from typing import Dict, Any, Set, List, Union, Tuple
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

    _ending_boilerplate_p1 = """
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
"""

    _ending_boilerplate = (
        _ending_boilerplate_p1
        + """
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
    )
    _ending_boilerplate_stats = (
        _ending_boilerplate_p1
        + """
// Render Loop
var render = function () {
    // Render scene
    stats.begin();
    requestAnimationFrame(render);
    animate();
    renderer.render(scene, camera_per);
    stats.end();
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
    )

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
        self._extra_file_count: int = 0

        self._texture_dict = {}
        self._extra_texture_count: int = 0

        self._show_stats: bool = False
        self.extra_modules: Set[str] = set()
        self.glslify_files: Set[str] = set()

    def __del__(self) -> None:
        self._file.close()

    def _readData(self, cfg_file: Path) -> None:
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

    def _getThreeJSColor(
        self, color: Union[str, int, Tuple[float, float, float], List[float]]
    ) -> str:
        """
        Given a color in any ThreeJS form, return a string to put into a JS file.

        Parameters
        ----------
        color : Union[str, int, Tuple[float, float, float], List[float, float, float]]
            Color.

        Returns
        -------
        str:
            Color string.
        """
        if isinstance(color, list) or isinstance(color, tuple):
            if len(color) != 3:
                raise ValueError(
                    f"Expected color iterable to be of size 3, but got {len(color)} instead."
                )
            return ",".join(color)
        else:
            # Color
            import re

            regex = "^0x[A-Fa-f0-9]{6}$"
            pattern = re.compile(regex)
            if pattern.match(str(color)):
                # Hex number
                return str(color)
            else:
                return '"' + str(color) + '"'

    def _getImageURI(self, img_file: Path) -> str:
        """
        Reads the data from an image file and returns the associated URI.

        Parameters
        ----------
        img_file : Path
            Path to the image file

        Returns
        -------
        str
            Image URI.
        """

        import base64

        suffix = img_file.suffix[1:]
        with open(img_file, "rb") as f:
            encoded_string = base64.b64encode(f.read())
        return "data:image/" + suffix + ";base64," + encoded_string.decode("utf-8")

    def _readMtlFile(self, file: str) -> str:

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
                text[k] = pieces[0] + " " + self._getImageURI(img_file)

        return "".join(text)

    def _hashTexture(
        self, file: Union[str, Path, List[str], Tuple[str, ...], List[Path], Tuple[Path, ...]]
    ) -> str:
        """
        Turn the file or set of files into a hash (str) deterministically.

        Parameters
        ----------
        file : Union[str, Path, List[str], Tuple[str, ...], List[Path], Tuple[Path, ...]]
            File(s) to turn into a hash.

        Returns
        -------
        str
            Hash string.
        """

        def to_string(x: Union[str, Path]) -> str:
            if isinstance(x, str):
                return x
            else:
                return str(x.resolve())

        if isinstance(file, str) or isinstance(file, Path):
            # Single texture
            return to_string(file)
        else:
            # Cube texture
            if len(file) != 6:
                raise ValueError(f"Got {len(file)} texture files, but I expected 1 or 6.")
            files = [x for x in map(to_string, file)]
            files.sort()
            return "".join(files)

    def _addTexture(
        self, file: Union[str, Path, List[str], Tuple[str, ...], List[Path], Tuple[Path, ...]]
    ) -> str:
        """
        Add texture to scene. This supports regular textures and cube textures.

        Parameters
        ----------
        file : Union[str, Path, List[str], Tuple[str, ...], List[Path], Tuple[Path, ...]]
            File(s) that make up the texture.

        Returns
        -------
        str:
            Name of the JavaScript variable that holds the texture.
        """

        # Get unique str hash for this texture
        texture_hash = self._hashTexture(file)

        # Return if we have already turned this into a texture
        if texture_hash in self._texture_dict:
            return self._texture_dict[texture_hash]

        # Create texture if it does not exist
        name = f"SIHM_EXTRA_TEXTURE_{self._extra_texture_count}"

        if isinstance(file, str) or isinstance(file, Path):
            # Single texture
            self._extra_beginning_boilerplate.add(
                "const TEXTURE_LOADER = new THREE.TextureLoader();\n"
            )
            img_file = self._cfg_path.joinpath(Path(data))
            self._file.write(
                f'const {name} = TEXTURE_LOADER.load("{self._getImageURI(img_file)}");\n'
            )
        else:
            # Cube texture
            if len(file) != 6:
                raise ValueError(f"Got {len(file)} texture files, but I expected 1 or 6.")
            self._extra_beginning_boilerplate.add(
                "const CUBE_TEXTURE_LOADER = new THREE.CubeTextureLoader();\n"
            )
            self._file.write(f"const {name} = CUBE_TEXTURE_LOADER.load( [\n")
            for f in file:
                img_file = self._cfg_path.joinpath(Path(f))
                self._file.write(f'"{self._getImageURI(img_file)}", \n')
            self._file.write("] );\n")

        self._texture_dict[texture_hash] = name
        return name

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

    def _processSihmOptions(self):
        for k, v in self._data.get("SIHM", {}).items():
            if k == "show_stats":
                self._show_stats = v
            elif k == "extra_modules":
                if isinstance(v, list) or isinstance(v, tuple):
                    for val in v:
                        self.extra_modules.add(val)
                elif isinstance(v, str):
                    self.extra_modules.add(v)
                else:
                    raise ValueError(f"Not sure what to do with extra_modules argument {v}")
            else:
                print(f"WARNING: Encountered unknown option {k} in the SIHM section.")

        if self._show_stats:
            self._extra_imports.add('import Stats from "stats-js";\n')
            self._extra_beginning_boilerplate.add(
                "const stats = new Stats();\nstats.showPanel(0); // 0: fps, 1: ms, 2: mb, 3+: custom\ndocument.body.appendChild(stats.dom);\n"
            )
            self.extra_modules.add("stats-js")

    def _addSceneProp(self, prop: str, data: Any):
        if prop == "background":
            # Background property
            if isinstance(data, list) or isinstance(data, tuple):
                if len(data) == 6:
                    # Cube texture
                    texture_name = self._addTexture(data)
                    self._file.write(f"scene.{prop} = {texture_name};\n")
                else:
                    # Color
                    color = self._getThreeJSColor(data)
                    self._file.write(f"scene.{prop} = new THREE.Color({color});\n")
            elif "." in str(data):
                # Texture
                texture_name = self._addTexture(data)
                self._file.write(f"scene.{prop} = {texture_name};\n")
            else:
                # Color
                color = self._getThreeJSColor(data)
                self._file.write(f"scene.{prop} = new THREE.Color({color});\n")
        else:
            # All other properties
            self._file.write(f"scene.{prop} = {data};\n")

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

                    # Add glslify transform if necessray
                    if mat.get("USES_GLSLIFY", False):
                        self.extra_modules.add("glslify")
                        uses_glslify = True
                    else:
                        uses_glslify = False

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

                                if uses_glslify:
                                    self.glslify_files.add(js_name + ".js")

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

                                if uses_glslify:
                                    self.glslify_files.add(js_name + ".js")

                    else:
                        raise ValueError(
                            "Arguments to ShaderMaterial must be given as a dictionary."
                        )

                    mat_args = "{" + self._processArgs(args) + "}"

                elif mat["FUNCTION"] == "MeshLambertMaterial":
                    args = mat["ARGS"]
                    textures = [
                        "alphaMap",
                        "aoMap",
                        "bumpMap",
                        "displacementMap",
                        "emissiveMap",
                        "envMap",
                        "lightMap",
                        "map",
                        "normalMap",
                        "specularMap",
                    ]
                    colors = ["color"]
                    for k in args:
                        if k in textures:
                            args[k] = self._addTexture(args[k])
                        elif k in colors:
                            args[k] = self._getThreeJSColor(args[k])

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
                if mat and mat.get("FILE", None) is None:
                    # Material is created separately, need to combine
                    # TODO: Get this material to show up
                    # self._file.write(f"{name}.customDepthMaterial = {name}_material;\n")
                    # self._file.write(f"{name}.customDistanceMaterial = {name}_material;\n")
                    # self._file.write(f"{name}.material = {name}_material;\n")
                    pass

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

        # Process sihm options
        self._processSihmOptions()

        # Write beginning boilerplate
        self._file.write(self._imports)
        loc = self._file.tell()
        self._file.write(self._beginning_boilerplate)

        # Set scene properties
        for prop, data in self._data.get("SCENE", {}).items():
            self._addSceneProp(prop, data)

        # Create objects and animations
        for name, obj in self._data.get("OBJECTS", {}).items():
            self._createObject(name, obj, parent="scene")

        # Create lights
        for name, light in self._data.get("LIGHTS", {}).items():
            self._createLight(name, light, parent="scene")

        # Add in extra beginning boilerplate.
        # this must be done after calling _createObject, since
        # that is the function that adds this boilerplate.
        lines = "".join(self._extra_imports) + "".join(self._extra_beginning_boilerplate)
        self._append_to_file(loc, lines)
        self._file.seek(0, SEEK_END)

        # Write ending boilerplate
        if self._show_stats:
            self._file.write(self._ending_boilerplate_stats)
        else:
            self._file.write(self._ending_boilerplate)
