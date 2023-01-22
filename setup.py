import sys
from os import path
from setuptools import setup, Extension, find_packages
from setuptools.command.build_py import build_py as _build_py
from glob import glob

# Get long description
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Get version info
version_dict = {}
with open("src/sihm/version.py") as f:
    exec(f.read(), version_dict)
    version = version_dict["__version__"]

# Custom build options to include swig Python files
class build_py(_build_py):
    def run(self):
        self.run_command("build_ext")
        super(build_py, self).run()


# Setup
setup(
    name="sihm",
    version=version,
    author="Carl Leake",
    author_email="leakec57@gmail.com",
    description="Standalone Interactive HTML Movie (SIHM).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leakec/sihm.git",
    license="MIT",
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"": ["src/sihm/py.typed"]},
    entry_points={"console_scripts": ["sihm=sihm.__main__:main"]},
    include_package_data=True,
    install_requires=[
        "click",
        "pyyaml",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering",
        "Topic :: Education",
    ],
)
