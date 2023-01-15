# Standalone Interactive HTML Movie (SIHM)

**A highly-portable, interactive way to visualize your simulations.**

[**Summary**](#summary) | [**Examples**](https://leakec.github.io/sihm) | [**Installation guide**](#installation)

## Summary

This package provides `sihm`, a command-line tool that takes as input a YAML file that defines geometry and properties of that geometry&mdash;position, velocity, color, etc.&mdash;vs. time and turns it into a standalone, interactive HTML movie.

-   The output is a movie in the sense that the trajectories vs. time are fixed. You'll be able to pause, play, rewind, loop, etc. as a movie would.
-   The output is interactive because you can move the camera around while the video is playing (or paused). You can also "attach" the camera to an object and follow that object around the sim.
-   The output is a standalone HTML file, i.e., it is the only file you will need to run the interactive movie.
-   HTML was selected because it is extermely portable. The output should work anywhere: Linux, Mac, Windows, your cell phone, etc.

## Examples

Examples of `sihm`'s output can be found [here](https://leakec.github.io/sihm).

## Installation

### Linux

-   `pip install sihm`
-   Install the appropriate package&mdash;`rpm` or `deb`, depending on you OS&mdash; from the latest release.

### Mac / Windows

-   Install the system dependencies
    -   yarn
    -   nodejs >= 16
    -   cmake
-   Install the python package: `pip install sihm`
-   If you want tab completion on Mac, then copy the appropriate file from the `bin` folder into the appropriate spot. Tab completion is available for `bash` and `zsh`.
