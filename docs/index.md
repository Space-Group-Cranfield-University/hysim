# Introduction

Welcome to HySim, The Hyperspectral Space-to-Space Imaging Simulator. HySim is an imaging simulation tool designed by [Cranfield University](https://www.cranfield.ac.uk/) for space-based proximity operations that involve hyperspectral and multispectral sensors. The program generates physics based renders of the space environment and resulting hyperspectral data given mission parameters as inputs.

The latest version supports the following features:

- Quasi-static scene definition (Single locations of target and imager spacecraft)
- Earth orbit based scene generation from TLE, Keplerian Elements and Orbit State Vectors.
- Support for PLY mesh files.
- Multiple component target models.
- Database of diffuse spacecraft material spectrums.
- User defined Hyperspectral and Multispectral sensors.

HySim is largely based around the [Mitsuba 3](https://mitsuba.readthedocs.io/en/stable/#) render engine which is used to render the scenes. In the current version of the code only the base version of Mitsuba is used, therefore any limitations in Mitsuba are also applied to HySim. For advanced use cases it is best for a user to familiarise themselves with Mitsuba.

## Authors
- **Cameron Leslie**, Research Assistant: <cameron.f.leslie@cranfield.ac.uk> (alt: <cameron-leslie@outlook.com>)
- **Samuel Rowling**, Research Assistant: <samuel.rowling@protonmail.com>
- **Dr. Leonard Felicetti**, Lecturer in Space Engineering: <leonard.felicetti@cranfield.ac.uk>
- **Prof. Stephen Hobbs**, Professor of Space Sensing and Systems: <s.e.hobbs@cranfield.ac.uk>

## Dependencies

Hysim uses the following packages:

- Mitsuba (Version => 3.1)
- NumPy (Version => 1.23)
- PyYAML (Version => 6.0)
- SpiceyPy (Version => 5.1.2)
- imageio (Version => 2.23.0)

<!-- ## Citation

If citing HySim please use the following:

```bib
@software{hysim2022,
    title = {HySim Software},
    author = {Stephen Hobbs and Leonard Felicetti and Cameron Leslie and Samuel Rowling},
    version = {0.1.0},
    year = 2022,
}
``` -->


