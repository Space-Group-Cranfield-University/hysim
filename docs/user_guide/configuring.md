# Configuring a Case

## Case Directory

Cases are configured using yaml files and by providing necessary user data in a case directory. Here is a typical directory structure:

!!! note

    Throughout the tutorial chevrons "<>" will be used to denote placeholders entries that help explain the format. These should be omitted from the actual configuration files. For example: `imaging_mode: <imaging mode>` shows there are several options for this entry. One such options would be `imaging_mode: multispectral`. 


```
case_directory
├───case_settings.yml
├───mission_parameters.yml
├───sensor
│   ├───film.spd
│   └───sensor.yml
└───target
    ├───parts.yml
    ├───materials
    │   ├───aluminium.spd
    │   └───sar_material.yml
    └───mesh
        ├───paz_antenna.ply
        ├───paz_antenna_rod.ply
        ├───paz_body.ply
        ├───paz_sar_array.ply
        └───paz_solar_panel.ply
```

The layout and naming convensions are not enforced however all files must be in the same parent directory (`case_directory` in the example). When running the code it must be done from the root of the case directory - in this case from within `case_directory`.

--------------------------

## File Types

HySim recognises several types of configuration and data files:

- **YAML** files are used to configure user inputs. These are edited manually between each case. Yaml files must start with `---`. HySim defines content through `<key>: <value>` pairs. These pairs are nestable through indentation. For detailed information on YAML format see [here](https://yaml.org/spec/1.2.2/).
- **SPD** files contain a spectral reflectance distribution consisting of a single measurement and wavelengths per line. The file must be tab delimited and formatted in utf-8. In the case of spd files used for wide multispectral (not hyperspectral) film bands, there can be multiple columns of data for each wavelength, each representing as band. For all other spectra only a single column is needed.
- **PLY** files are triangulated mesh formats containing a single component. Each component has a single material assigned to it. See section on preparing a target mesh for details.

--------------------------

## Configuration Files

There are four main configuration files required to run a case. Each file contains a **header** with the entry `file_type : <config type>` to differentiate between them:

- **Case Settings** - Choose renderer settings, logger settings and output formats. Header: `file_type: case_config`.
- **Mission Parameters** - Choose orbit position and attitude of target and chaser and the epoch. Header: `file_type: mission_config`.
- **Sensor Parameters** - Choose the Multispectral/Hyperspectral camera and film parameters. Header: `file_type: sensor_config`.
- **Parts** - List the components that make up the target model and assign materials to each. Header: `file_type: parts_config`.

There is also an additional optional configuration file for assigning user defined materials (`file_type: material_config`). This can be supplied alongside a .spd file containing the spectral reflectance for the material. The format directly corresponds to the desired [Mitsuba BSDF dictionary format](https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_bsdfs.html).


### Case Settings

The case settings file requires the following entries:


```yaml
mitsuba_variant: scalar_spectral
```
The mitsuba variant chosen should be a spectral type. The full list can be found [here](https://mitsuba.readthedocs.io/en/latest/src/key_topics/variants.html).

!!! note

    Currently the only supported variant in the pip installed version of the program is `scalar_spectral`. To use GPU variants you need to [compile mitsuba from source](https://mitsuba.readthedocs.io/en/latest/src/developer_guide/compiling.html).


```yaml
sampler:
  type: stratified
  sample_count: <integer> # Must be square number 
```
The sampler entry chooses the sample generator and sample count per pixel used by Mitsuba. Available samplers can be found [here](https://mitsuba.readthedocs.io/en/latest/src/generated/plugins_samplers.html). The sample count has restrictions based on the sampler used - for the stratified sampler it must be a square number. The Default is 4.



```yaml
integrator:
  type: path
  max_depth: -1 # -1 for infinite
```
The integrator refers to the render method used by Mitsuba to solve the light transport equation. It is recommended to use the path tracer method: `path`. The max depth refers to the longest path to be rendered (number of reflections). `max_depth: -1` sets infinite bounces for the best result at expense of computation time.  


```yaml
log: 
  save_case_log: True
  file_name: log_file
```
The log entry allows the user to save the console logs to a file. Set `save_case_log` to `True` or `False`. If true it will be saved to a log file using the file name given.

!!! warning
    
    Log file writing is yet to be implemented.


```yaml
output:
  - format: exr
    file_name: case_results.exr
```
The output entry sets the format and file name of the simulation results. Currently the following formats are supported:

| Format | Description |
|--------|-------------|
| `exr`  | Exports to [OpenEXR](https://openexr.readthedocs.io/en/latest/) Format |
| `png`  | Exports each band to a png file |

--------------------------


### Mission Parameters

Mission Parameter files must contain the following entries. The epoch for the image must be provided in the format above in utc time:

```yaml
datetime: "<mm/dd/yyyy hh:mm:ss utc>"
```
The epoch is used to calculate the position of the Sun relative to the scene and the position of the spacecraft when using TLE. The orbit position and attitude of the target are given in the following format:

```yaml
target:
  position_frame: <frame>
  position: <orbit position>  
  attitude: <attitude entry>
```
The format providing the target's orbit is selected using `position_frame`. The currently supported formats are:

| Format | Description |
|--------|-------------|
| `tle`  | Two Line Element Set |
| `kep`  | Keplerian Elements |
| `eci`  | Coordinates in Earth Centered Inertial |

Here are examples for defining the orbit of the ISS:

=== "TLE"
    
    Enter Two Line Element sets as a comma seperated list:

    ```yaml
    position: ["1 25544U 98067A   22356.59436905 -.00008932  00000-0 -15123-3 0  9998",
               "2 25544  51.6422 123.2511 0005530 175.6943 277.6446 15.49508690374406"]
    ```

=== "Keplerian"

    List of keplerian elements: `[a, e, i, raan, argp, M]`

    | Parameter | Description |
    |---------|-------------|
    | `a`     | Semi-major axis in km |
    | `e`     | Eccentricity |
    | `i`     | Inclination in radians |
    | `raan`  | Right ascension of the ascending node in radians |
    | `argp`  | Argument of periapsis in radians |
    | `M`     | Mean Anomaly at epoch in radians |

    Estimated ISS Elements at `12/22/2022 14:15:53 utc`:

    ```yaml
    position: [6796, 0.0005530, 0.9013, 2.1511, 3.0664, 4.8458]
    ```

=== "State Vectors"

    Enter orbit state vectors in ECI using a comma seperated list as `[x, y, z, vx, vy, vz]` in km and km/s.

    ISS coordinates at `12/22/2022 14:15:53 utc`:

    ```yaml
    position: [-3.31030328e+03, -2.63025234e+03,  5.32039652e+03,  4.41965326e+00, -6.24556750e+00, -3.43124216e-01]
    ```

!!! warning
    
    It can be difficult to line up keplerian elements or state vectors and TLE due to the errors in conversions and the propagation method. It is recommended you choose either Vectors and Keplerian **or** only TLE.

!!! warning

    If the orbit (or velocities) defined are too large then there may be problems with vertex positions defined in the mesh. This could be due to limitations in floating point precision and not an issue with the mesh.

The attitude of the target is given as Euler angles with respect to the LVLH frame in the following format: `attitude: [<x-axis>, <y-axis>, <z-axis>]`. Each rotation is in **radians**. The chaser uses the same inputs as the target:

```yaml
chaser:
  position_frame: <frame>
  position: <orbit position>
  attitude: <attitude entry>
```

For the chaser there is an option to set `attitude: lookat` which automatically determines the orientation of the spacecraft to look directly at the target.

--------------------------

### Sensor

The Sensor parameters are contained in the Sensor Config file. All sensors are defined as a [Mitsuba perspecive camera](https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_sensors.html#perspective-pinhole-camera-perspective) which assumes an infinitely small aperture. The following parameters can be provided to define the camera:

```yaml
camera:
  field_of_view: <degrees>
```

The hyperspectral film used in the camera is defined seperately. The resolution of the film is defined by the `film` entry (note that the field of view relates to the same axis as film width along the x axis):

```yaml
film:
  width: <pixels>
  height: <pixels>
```

There are two imaging modes available: `Hyperspectral` and `Multispectral`: 

- `Hyperspectral` mode creates many narrow bands based on a single sensitivity spectrum.
- `Multispectral` mode creates a single wide band per spectrum (passed to the program as a column of data).

Choosing these modes is done with the following entries:

```yaml
imaging_mode: <imaging mode>
spectrum_file: <path/to/spectrum/file.spd>
```

Here are examples of the spectrum file data for each imaging mode:

=== "Hyperspectral"

    ```text
    400	0.86
    401	0.91
    402	0.71 
    403	0.52
    404	0.24
    405	0.10
    406	0.06
    407	0.05
    408	0.04
    409	0.02
    410	0.01
    ```

    Using the data in the spd file, 9 narrow bands will be created for each wavelength interval of 1 nm. The sensitivity of each band will be linear between each sensitivity interval. For example band 0 will have a wavelength range from 400-401 nm and a film sensitivity of 0.86-0.01.


=== "Multispectral"

    ```text
    400	0.86 0.17 0.19 0.11 0.82
    401	0.91 0.26 0.17 0.02 0.71
    402	0.71 0.45 0.15 0.04 0.53
    403	0.52 0.53 0.23 0.06 0.42
    404	0.24 0.72 0.25 0.07 0.35
    405	0.10 0.80 0.17 0.08 0.30
    406	0.06 0.75 0.26 0.06 0.37
    407	0.05 0.68 0.36 0.15 0.35
    408	0.04 0.59 0.55 0.12 0.18
    409	0.02 0.34 0.73 0.13 0.03
    410	0.01 0.22 0.81 0.14 0.01
    ```
    Using the data in the spd file, 5 wide bands will be created using each column of film sensitivity data. For example band 0 will have a wavelength range of 400-410 nm and follow the sensitivity of curve of column 2.

------------------------------

### Parts

The parts file contains the `components` entry where the components that make up the target are listed:

```yaml
components:
  <part1 name>:
    file: <path/mesh1.ply>
    database_material: <material name>
  
  <part2 name>:
    file: <path/mesh2.ply>
    user_material: <material name>
```
The file provided should simply be the name of the part. The program searches for the file name in the case directory. There are two options for specifying materials:

| Format | Description |
|--------|-------------|
| `database_material`  | Chooses a material from the database. |
| `user_material`  | Parses entries in the optional `materials.yml` file for the name provided |


### Materials File

User defined materials are listed in the materials configuration. The format of each material relates directly to the a [Mitsuba BSDF](https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_bsdfs.html#bsdfs). The name of each material must match those assigned to a mesh component in the `parts_config` file. In the example below a material representing aluminium with diffuse (lambertian scattering) reflectance properties. The path to the reflectance data file from the root directory should be specified in the `filename` entry. Here is an example defining defuse aluminium with a spectrum file supplied by the user:

```yaml
---
# ========================================================================
# User Material Configuration File
# ========================================================================
# File type: specifies the type of configuration file to be interpreted by
# the program.
file_type: material_config

# Material configuration specifies a user BSDF in mitsubas dict format.
# best to refer to mitsubas documentation on BSDFs.
materials:
  # First indent: material name
  diffuse_aluminium:
    # Second indent: material type and its properties
    type: diffuse
    reflectance:
      type: spectrum
      # User specifies spectrum file.
      filename: target/materials/aluminium.spd
```



