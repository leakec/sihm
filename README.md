# Standalone Interactive HTML Movie (SIHM)

**This repository is under construction. Please check back soon :)**

## Summary
Create a command-line tool that takes a YAML file (will support other types in the future) that defines geometry and properties of that geometry&mdash;position, velocity, color, etc.&mdash;vs. time and turns it into a standalone, interactive HTML movie. 
* It's a movie in the sense that the trajectories vs. time are fixed. You'll be able to pause, play, rewind, loop, etc. as a movie would. 
* It's interactive in the sense that you can move the camera around while the video is playing (or paused). You can also "attach" the camera to an object and follow that object around the sim.
* It's standalone in the sense that the output HTML file will be standalone, i.e., it is the only thing you will need to run the interactive movie.
* It's HTML because that will make it easily portable to anywhere, Linux, Mac, Windows, Phones, etc.

## Current status
* Check the issues for what I'm currently working on.

# Developing


## Dependencies
Keeping track of current dependencies here:

### System
* yarn
* nodejs
* make

### Python
Nothing but the base package so far.
