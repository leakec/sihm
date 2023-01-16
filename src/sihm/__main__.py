#!/usr/bin/python

import os
import click
from typing import Any, Dict
from copy import deepcopy
from pathlib import Path


def main():

    options = {}
    output_type = ""
    cfg_file = ""

    def _get_default(cli) -> Dict[Any, Any]:
        """
        Gets default values from click.
        """
        default_dict = {}
        for cmd_name, cmd in cli.commands.items():
            default_dict[cmd_name] = {}
            for opt in cmd.params:
                default_dict[cmd_name][opt.name] = opt.default

        return default_dict

    def _merge_dict(d1: Dict[Any, Any], d2: Dict[Any, Any], copy: bool = True) -> Dict[Any, Any]:
        """
        Override the values in d1 with d2.
        """
        if copy:
            d3 = deepcopy(d1)
        else:
            d3 = d1
        for k, v in d2.items():
            if k in d3:
                if isinstance(v, dict):
                    d3[k] = _merge_dict(d3[k], d2[k], copy=False)
                else:
                    d3[k] = v
            else:
                d3[k] = v
        return d3

    def _add_options(cmd, opts):
        """
        Adds options to global options.
        """
        options[cmd] = opts

    def input_cb(ctx, opt, val) -> None:
        """
        Sets the input filename.
        """
        nonlocal cfg_file
        cfg_file = val

    def param_cb(ctx, opt, val):
        """
        Changes the parameter options.
        """
        nonlocal output_type
        output_type = val
        if val == "project":

            @cli.command
            @click.pass_context
            @click.option(
                "--dir",
                type=click.Path(exists=True, dir_okay=True, file_okay=False),
                default=".",
                show_default=True,
            )
            def params(ctx, **kwargs):
                _add_options("params", kwargs)

        else:

            @cli.command
            @click.pass_context
            @click.option(
                "--jobs",
                "-j",
                type=click.IntRange(min=1),
                default=1,
                show_default=True,
                help="Number of cores to use when building the project",
            )
            def params(ctx, **kwargs):
                _add_options("params", kwargs)

    @click.group(
        name="sihm",
        invoke_without_command=True,
        chain=True,
        context_settings={"help_option_names": ["-h", "--help"]},
    )
    @click.option(
        "--input",
        "-i",
        type=click.Path(exists=True, dir_okay=False, file_okay=True),
        help="Input configuration file.",
        required=True,
        callback=input_cb,
    )
    @click.option(
        "--output",
        type=click.Choice(["project", "html"]),
        help="sihm output type:\n\n project - Creates the yarn project used to compile the standalone HTML.\n\n html - Creates the standalone HTML file. The associated yarn project is created in a temporary directory.",
        default="html",
        show_default=True,
        callback=param_cb,
        is_eager=True,
    )
    @click.pass_context
    def cli(ctx, **kwargs):
        pass

    run = cli(standalone_mode=False)
    if isinstance(run, int):
        import sys

        sys.exit(run)
    else:
        default_opts = _get_default(cli)
        options = _merge_dict(default_opts, options)

    def _parse_file(cfg_file: Path, file_name: str):
        """
        Parse the file to create index.js

        Parameters
        ----------
        cfg_file : Path
            Input config file.
        fileName : str
            Output file name.
        """
        from sihm.parser import SihmParser

        parser = SihmParser(cfg_file, file_name)
        parser.write_file()

    def _make_project(directory: Path) -> None:
        """
        Create project that is ready to compile.

        directory: Path
            Directory where the project should be created.
        """
        from shutil import copytree
        import sihm

        if not os.path.exists(directory):
            os.makedirs(directory)
        sihm_path = Path(sihm.__file__)
        template_project = os.path.join(sihm_path.parents[0], "template_project")
        copytree(template_project, directory.absolute(), dirs_exist_ok=True)

        # Create path/file for index.js
        file_name = os.path.join(directory.absolute(), "src", "index.js")

        # Parse the cfg_file and create the index.js file
        _parse_file(Path(cfg_file), file_name)

    if output_type == "project":
        # If user wants the standalone project only
        project_dir = Path(options["params"]["dir"])
        _make_project(project_dir)
    else:
        import tempfile
        from shutil import copyfile

        # Get the name/location of the final HTML file
        dark = Path(cfg_file)
        html_file = dark.with_suffix(".html").resolve()

        # Create temporary directory for the project
        temp_dir = tempfile.TemporaryDirectory()

        # Create project
        project_dir = Path(temp_dir.name)
        _make_project(project_dir)

        # Compile the project
        curr_dir = os.getcwd()
        os.chdir(project_dir)
        if os.name == "nt":
            # Using windows
            os.system('cmake . -G "MinGW Makefiles"')
        else:
            os.system("cmake .")
        os.system(f"make all -j {options['params']['jobs']}")

        # Copy the file to its final location
        file_to_copy = Path(os.path.join("dist", "index.html"))
        copyfile(file_to_copy.resolve(), html_file)
        os.chdir(curr_dir)
