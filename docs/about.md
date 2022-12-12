# About HySim

Welcome to HySim, The Hyperspectral Space-to-Space Imaging Simulator! HySim is an imaging simulation tool designed for space-based proximity operations that involve hyperspectral and multispectral sensors. Using the open-source physically based renderer Mitsuba 3, the program generates realistic simulations of the space environment and resulting hyperspectral data given mission parameters as inputs.

HySim provides support for a quasi-static definition of a scene where positions in orbit are already known. The lighting conditions given relative positions of the Earth and Sun are established using a known position of a sensor and a target spacecraft at a given epoch.

The user can provide a series of triangulated mesh files that make up components of a target spacecraft and choose from a list of space materials (or provide their own). Images of the target are then generated in chosen spectral bands for a user define sensor.

## Licence

Licence

## Source Code

Link to github

## Mitsuba Physically Based Renderer

HySim is largely based around the Mitsuba 3 render engine which is used to render the scenes. In the current version of the code only the base version of Mitsuba is used, therefore any limitations in Mitsuba are also applied to HySim.

For advanced use cases it is best for a user to familiarise themselves with [Mitsuba](https://mitsuba.readthedocs.io/en/stable/#).