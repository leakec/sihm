from pathlib import Path
from typing import List, Union, Tuple, TypedDict


class ImageLoc(TypedDict):
    """
    Determines the location of the 6 images in the skybox image.
    Imagine the sky box broken into 12 segments number from left to right
    and top to bottom. These 12 segments are zero indexed. For example,
    the upper left segemnt is 0, and the right-most middle segment is 8.

    Parameters
    ----------
    l : int
        Left image.
    r : int
        Right image.
    f : int
        Front image.
    b : int
        Back image.
    u : int
        Up (top) image.
    d : int
        Down (bottom) image.
    """

    l: int
    r: int
    f: int
    b: int
    u: int
    d: int


img_loc_default = ImageLoc(l=4, r=6, f=5, b=7, u=1, d=9)


def create_skybox(img_file: Path, img_loc: ImageLoc = img_loc_default) -> None:
    """
    Create the 6 images needed for a ThreeJS skybox from one large image.

    In ThreeJS:
    * right = +x
    * left = -x
    * up = +y
    * down = -y
    * front = +z
    * back = -z
    ThreeJS uses a right-handed coordiante systems where as other systems use a left-handed
    system. Therefore, you may need to flip the positive and negative x-axes.

    Parameters
    ----------
    img_file : Path
        Path to the large image.
    img_loc : ImageLoc
        ImageLoc that defines the location of the 6 images in the larger image.
    """

    # Open image
    from PIL import Image

    img = Image.open(img_file)

    # Get width/height of 6 smaller images
    width, height = img.size
    width /= 4
    height /= 3
    if width != height:
        print(f"WARNING: Skybox image is {img_file} will not produce square skybox images.")

    # Variables used for naming smaller images
    stem = img_file.stem
    img_file_str = str(img_file.resolve()).rsplit(stem, 1)

    # Crop out smaller images
    for k, v in img_loc.items():
        crop_file = Path((stem + "_" + k).join(img_file_str))
        col = v % 4
        row = int((v - col) / 4)

        crop = img.crop((width * col, row * height, width * (col + 1), (row + 1) * height))
        crop.save(crop_file)


def add_texture_coords_to_mesh(input_file: Path, output_file: Path):
    """
    Adds texture coordinates to the input OBJ file and exports it as an output OBJ file.

    Parameters
    ----------
    input_file : Path
        Path to input mesh file.
    output_file : Path
        Path to the output mesh file.
    """

    import bpy

    context = bpy.context
    scene = context.scene
    vl = context.view_layer

    imported_object = bpy.ops.import_scene.obj(
        filepath=str(input_file.resolve())
    )  # ,global_clight_size=0.5)
    obj = bpy.context.selected_objects[0]  ####<--Fix
    vl.objects.active = obj
    obj.select_set(True)
    uv = obj.data.uv_layers.get("UVMap")
    if not uv:
        uv = obj.data.uv_layers.new(name="UVMap")
    uv.active = True
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action="SELECT")  # for all faces
    bpy.ops.uv.smart_project(angle_limit=45, island_margin=0.02)
    bpy.ops.object.editmode_toggle()

    bpy.ops.export_scene.obj(filepath=str(output_file.resolve()), use_selection=True)

    obj.select_set(False)


def clean_mesh(input_file: Path, output_file: Path):
    """
    Cleans mesh using blender by removing doubles and recalculating normals.

    Parameters
    ----------
    input_file : Path
        Path to input mesh file.
    output_file : Path
        Path to the output mesh file.
    """

    import bpy

    # Setup
    context = bpy.context
    scene = context.scene
    vl = context.view_layer

    # Import
    imported_object = bpy.ops.import_scene.obj(
        filepath=str(input_file.resolve())
    )  # ,global_clight_size=0.5)
    obj = bpy.context.selected_objects[0]  ####<--Fix
    vl.objects.active = obj
    obj.select_set(True)

    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles()
    bpy.ops.mesh.normals_make_consistent()
    bpy.ops.object.editmode_toggle()

    # Export
    bpy.ops.export_scene.obj(filepath=str(output_file.resolve()), use_selection=True)

    obj.select_set(False)
