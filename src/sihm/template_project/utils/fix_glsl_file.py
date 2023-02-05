import click

options = {}

# Create click group
@click.group(
    name="fix_glsl_file",
    invoke_without_command=True,
    chain=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="GLSL file to fix.",
    required=True,
)
@click.pass_context
def cli(ctx, **kwargs):
    options.update(kwargs)


# Obtain GLSL file to change
run = cli(standalone_mode=False)
if isinstance(run, int):
    import sys

    sys.exit(run)

file = options["file"]

# Read in the original file
with open(file, "r") as f:
    lines = f.readlines()

# Find the line with "export const"
for k, line in enumerate(lines):
    if "export const" in line:
        ind = k
        break

# Move that line to the front
first_line = lines.pop(k)
lines.insert(0, first_line)

# Re-write the file
with open(file, "w") as f:
    f.write("".join(lines))
