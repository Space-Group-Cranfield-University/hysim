# Running a Case

## Command Line Interface

Currently HySim has a very simple user interface. To produce a list of all available commands type:

```console
hysim --help
```

To check HySim is installed with the latest version use the command:

```console
hysim --version
```

Once the case is configured use the following command to run the simulator:

```console
hysim run
```
After running the case there you should see console output detailing each step in the simulation and a status bar for the render. Here is an example of the console output:

```console
 INFO     Running Simulation Case
 INFO     Getting user inputs from configuration files
 INFO     Calculating scene geometry from orbit data
 INFO     Building scene
 INFO     Relative distance to target: 84535.82m
 INFO     Loading scene into Mitsuba
 INFO     Scene assembled successfully
 INFO     Running Mitsuba


Rendering [==========================================================================================] (10.8s, ETA: 0ms)

 INFO     Render complete
 INFO     Exporting results as EXR File
 INFO     Exporting results as PNG files
```

Once it is finished the results should be written to a file of the type specified in the case settings file.

## Recommended Post Processing Software

When using EXR it can be useful to interpret results and export spectra from regions of the image. [Spectral Viewer](https://mrf-devteam.gitlab.io/spectral-viewer/) is a free Open Source spectral image viewer for all platforms that supports OpenEXR format. 