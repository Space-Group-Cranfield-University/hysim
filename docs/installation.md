# Installation

HySim can be installed using the Python [wheel](https://pypi.org/project/wheel/) (found in the dist directory) which can be installed using [pip](https://pypi.org/project/pip/). This requires Python and pip to be installed locally. Pip is included in most cases with python installations.

## Requirements
- Python >= 3.9

You can check the currently installed version of python using the following command:

```console
python --version
```

To eliminate issues with the python path (especially on Windows) it is recommended to install HySim in a python virtual environment. This can be done using [venv](https://docs.python.org/3/tutorial/venv.html) which is included in the Python standard library, or another environment manager like [Anaconda](https://www.anaconda.com/).


## Simple Miniconda Install

Since HySim is in early development, software dependencies and version control can often cause problems as the program has not been thoroughly tested across various platforms and software versions. Miniconda is a lightweight and simple way to install and use the conda package manager. Conda provides an easy way of managing python virtual environments, allowing strict control of the python version and any dependencies.

To install Miniconda download and install it from [here](https://docs.conda.io/en/latest/miniconda.html).

Once installed, start anaconda prompt or a terminal of your choice. Create a new virtual environment for running HySim with the following command:

```console
conda create -n hysim_env python=3.9
```

You dont absolutely require an environment only for HySim, but it allows explicit control over the python version installed, reducing the likelyhood of issues. Once created you can activate the environment by typing:

```console
conda activate hysim_env
```

From here you can install HySim using the provided python wheel.


## Installing HySim

HySim can be installed with pip using the following github link:

```console
pip install git+https://github.com/Space-Group-Cranfield-University/hysim
```
Note the name of the wheel here is just an example. It will change between versions and platforms. To test the installation run:

```console
hysim --version
```
The output should show the currently installed version of HySim such as ```hysim 0.1.1```.
