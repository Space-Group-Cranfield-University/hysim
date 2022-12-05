KPL/MK

   This is the meta-kernel used to load the necessary kernels
   to get planetary ephemeris

   The names and contents of the kernels referenced by this
   meta-kernel are as follows:

   File name                   Contents
   --------------------------  -----------------------------
   naif0008.tls                Generic LSK
   981005_PLTEPH-DE405S.bsp    Solar System Ephemeris


   \begindata
   KERNELS_TO_LOAD = ( 'kernels/naif0012.tls',
                       'kernels/de440s.bsp',
                       'kernels/geophysical.ker')
   \begintext