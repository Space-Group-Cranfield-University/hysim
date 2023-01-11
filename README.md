# HySim

Welcome to HySim, The Hyperspectral Space-to-Space Imaging Simulator. HySim is an imaging simulation tool designed for space-based proximity operations that involve hyperspectral and multispectral sensors. The program generates physics based renders of the space environment and resulting hyperspectral data given mission parameters as inputs.

The latest version supports the following features:

- Quasi-static scene definition (Single locations of target and imager spacecraft)
- Orbit locations from TLE, Keplerian Elements and Orbit State Vectors.
- Support for PLY mesh files.
- Multiple component target models.
- Database of diffuse spacecraft material spectrums.
- User defined Hyperspectral and Multispectral sensors.

HySim is largely based around the [Mitsuba 3](https://mitsuba.readthedocs.io/en/stable/#) render engine which is used to render the scenes. In the current version of the code only the base version of Mitsuba is used, therefore any limitations in Mitsuba are also applied to HySim. For advanced use cases it is best for a user to familiarise themselves with Mitsuba

## Requirements
- Python >= 3.8

## Installing HySim

HySim is currently available as a Python [wheel](https://pypi.org/project/wheel/) which can be installed using pip. This requires Python and pip to be installed locally.

To eliminate issues with the python path (especially on Windows) it is recommended to install HySim in a python virtual environment. This can be done using [venv](https://docs.python.org/3/tutorial/venv.html) which is included in the Python standard library, or another environment manager like [Anaconda](https://www.anaconda.com/).

You can check to see if python and pip are installed from the command line:

```console
> python --version
Python 3.9.15
> pip --version
pip 22.3.1

```

HySim can be installed with pip using the wheel included in the project deliverables. After navigating to the directory containing the wheel and install using:

```console
> pip install hysim.whl
```
Note the name of the wheel here is just an example. To test the installation run:

```console
> hysim --version
```
The output should show the currently installed version of HySim such as ```hysim 0.1.0```.
