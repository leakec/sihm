# Import FreeCAD
FREECADPATH = "/usr/lib64/freecad/lib64"
import sys

sys.path.append(FREECADPATH)
import FreeCAD, Mesh
import click

options = {}

@click.group(
    name="cad",
    invoke_without_command=True,
    chain=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.option(
    "--export-obj/--no-export-obj",
    default=False,
    show_default=True,
    help="If true, then a new obj file will be exported.",
)
@click.option(
    "--export-urdf/--no-export-urdf",
    type=bool,
    default=False,
    show_default=True,
    help="If true, then a new urdf file will be exported.",
)
@click.pass_context
def cli(ctx, **kwargs):
    options.update(kwargs)

run = cli(standalone_mode=False)
if isinstance(run, int):
    import sys

    sys.exit(run)

# Load hollow_cylinder file
filename = "pendulum.FCStd"
f = FreeCAD.open(filename)

# Get spreadsheet
params = f.getObjectsByLabel("params")[0]

# Get parameters using spreadsheet
bob_radius = params.get("bob_radius")
shaft_height = params.get("shaft_height")
shaft_width = params.get("shaft_width")

# Export OBJ file
if options["export_obj"]:
    body = f.getObjectsByLabel("pendulum")[0]
    Mesh.export([body], "pendulum.obj")

# Export URDF file
if options["export_urdf"]:
    import jinja2
    env = jinja2.Environment()
    with open("double_pendulum.urdf.in","r") as temp:
        template = env.from_string(temp.read())

    shape = f.getObjectsByLabel("pendulum")[0].Shape
    i = shape.MatrixOfInertia
    ixx = i.A11
    ixy = i.A12
    ixz = i.A13
    iyy = i.A22
    iyz = i.A23
    izz = i.A33
    dark = shape.CenterOfMass
    b2cm = " ".join([str(dark.x), str(dark.y), str(dark.z)])
    m = shape.Mass
    joint_loc = -(shaft_height + bob_radius)

    with open("double_pendulum.urdf","w") as temp:
        temp.write(template.render(MASS=m, B2CM=b2cm, IXX=ixx, IXY=ixy, IXZ=ixz, IYY=iyy, IYZ=iyz, IZZ=izz, JOINT_LOC=joint_loc))

# Can use the command below to save the CAD part.
# We are not saving the CAD part here, as we don't want to overwrite
# the original in this case. That way, the next time this reg tests
# runs, it will have the same CAD part to use.
# f.save()

# Display message about visibilty
print("May need to toggle visibility of parts with spacebar when re-opening.")

