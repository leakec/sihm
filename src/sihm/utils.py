from pathlib import Path
from typing import List, Union, Tuple, TypedDict, Optional, Any
import numpy as np
from numpy.typing import NDArray


def lerp(from_val: NDArray[Any], to_val: NDArray[Any], t: NDArray[Any]) -> NDArray[Any]:
    """
    Linearly interpolate (lerp).

    Parameters
    ----------
    from_val : NDArray[Any]
        From value in the lerp.
    to_val : NDArray[Any]
        To value in the lerp.
    t : NDArray[Any]
        The "t" value to use in the lerp.

    Returns
    -------
    NDArray[Any]
        Linearly interpolated values.
    """
    return (1.0 - t) * from_val + t * to_val


def inv_lerp(from_val: NDArray[Any], to_val: NDArray[Any], val: NDArray[Any]) -> NDArray[Any]:
    """
    Inverse lerp function.

    Parameters
    ----------
    from_val : NDArray[Any]
        From value in the inverse lerp.
    to_val : NDArray[Any]
        To value in the inverse lerp.
    val : NDArray[Any]
        The value to perform the inverse lerp on.

    Returns
    -------
    NDArray[Any]
        Array of the "t" values for the inverse lerp.
    """
    dark = (val - from_val) / (to_val - from_val)
    mask = from_val == to_val
    if np.any(mask):
        mask = np.isnan(dark)
        dark[mask] = np.broadcast_to(from_val, dark.shape)[mask]
    return dark


def remap(
    from_val_1: NDArray[Any],
    from_val_2: NDArray[Any],
    to_val_1: NDArray[Any],
    to_val_2: NDArray[Any],
    val: NDArray[Any],
) -> NDArray[Any]:
    """
    Remap function. Takes a range from from_val_1 to from_val_2 and maps it to
    to_val_1 to to_val_2.

    Parameters
    ----------
    from_val_1 : NDArray[Any]
        Lower portion of the values to map from.
    from_val_2 : NDArray[Any]
        Upper portion of the values to map from.
    to_val_1 : NDArray[Any]
        Lower portion of the values to map to.
    to_val_2 : NDArray[Any]
        Upper portion of the values to map to.
    val : NDArray[Any]
        The values to remap.

    Returns
    -------
    NDArray[Any]
        Remapped values.
    """
    return lerp(to_val_1, to_val_2, inv_lerp(from_val_1, from_val_2, val))


class ImageLoc(TypedDict):
    """
    Determines the location of the 6 images in the skybox image.
    Imagine the sky box broken into 12 segments number from left to right
    and top to bottom. These 12 segments are zero indexed. For example,
    the upper left segemnt is 0, and the right-most middle segment is 7.

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


def create_normal_map(
    input_mesh: Path,
    output_mesh: Path,
    output_normal_map: Path,
    input_high_poly_mesh: Optional[Path] = None,
    extrusion: float = 0.1,
):
    """
    Creates a normal map for a low-poly mesh in Blender using a high-poly mesh. If
    no high-poly mesh is provided, then Blender's shade-smooth is used as the high-
    poly mesh.

    Parameters
    ----------
    input_mesh: Path
        Path to input mesh file.
    output_mesh: Path
        Path to output mesh file.
    output_normal_map: Path
        Path to the output normal map.
    input_high_poly_mesh: Optional[Path]
        Path to the high poly mesh file.
    extrusion: float
        Extrusion distance used.
    """

    import bpy

    # Setup blender
    context = bpy.context
    scene = context.scene
    vl = context.view_layer

    # Import low-poly mesh
    imported_object = bpy.ops.import_scene.obj(
        filepath=str(input_mesh.resolve())
    )  # ,global_clight_size=0.5)
    low_poly_obj = bpy.context.selected_objects[0]
    vl.objects.active = low_poly_obj
    low_poly_obj.select_set(True)

    # Select all faces in a mesh
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action="SELECT")

    # Create UV coordinates using smart_project
    bpy.ops.uv.smart_project()

    # Deselect all faces
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.editmode_toggle()

    # Add image texture to material
    mat = bpy.context.active_object.material_slots[0].material
    mat.use_nodes = True
    material_output = mat.node_tree.nodes.get("Material Output")
    principled_BSDF = mat.node_tree.nodes.get("Principled BSDF")

    name = output_normal_map.name
    bpy.ops.image.new(name=name, width=1024, height=1024, alpha=False)
    tex_image = bpy.data.images[name]
    tex_node = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex_node.image = tex_image

    # Deselect low-poly mesh
    low_poly_obj.select_set(False)

    # Import second file
    if input_high_poly_mesh:
        imported_object = bpy.ops.import_scene.obj(
            filepath=str(input_high_poly_mesh.resolve())
        )  # ,global_clight_size=0.5)
        high_poly_obj = bpy.context.selected_objects[0]
        vl.objects.active = high_poly_obj
        high_poly_obj.select_set(True)

        # Select all faces in a mesh
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="SELECT")

        # Create UV coordinates using smart_project
        bpy.ops.uv.smart_project()

        # Deselect
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.editmode_toggle()

    else:
        # Copy object
        vl.objects.active = low_poly_obj
        low_poly_obj.select_set(True)

        high_poly_obj = low_poly_obj.copy()
        high_poly_obj.data = low_poly_obj.data.copy()
        bpy.context.collection.objects.link(high_poly_obj)

        low_poly_obj.select_set(False)

        # Set shading to smooth
        vl.objects.active = high_poly_obj
        high_poly_obj.select_set(True)
        bpy.ops.object.shade_smooth()

    # Bake texture to image
    bpy.context.scene.render.engine = "CYCLES"
    high_poly_obj.select_set(True)
    vl.objects.active = low_poly_obj
    bpy.ops.object.bake(
        type="NORMAL",
        use_selected_to_active=True,
        filepath=str(output_normal_map.resolve()),
        cage_extrusion=extrusion,
    )

    # Export mesh and image
    vl.objects.active = low_poly_obj
    low_poly_obj.select_set(True)
    bpy.ops.export_scene.obj(filepath=str(output_mesh.resolve()), use_selection=True)

    tex_image.save(filepath=str(output_normal_map.resolve()))
