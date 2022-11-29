from sgp4.api import Satrec
import spiceypy as spice

kernel = "kernels\\meta_kernel.tm"
spice.furnsh(kernel)


# tle = [
#     "1 31698U 07026A   22231.61861684  .00000322  00000-0  18542-4 0  9993",
#     "2 31698  97.4459 238.3233 0001614  90.5035  18.2186 15.19148756841708",
# ]

tle = [
    "1 47933U 21022B   22231.59772040  .00000413  00000-0  44540-4 0  9996",
    "2 47933  97.6877 130.4910 0018971 330.4982  29.5198 14.93458057 76895",
]

second_epoch = spice.str2et("09/06/2022 15:30:00 utc")

jd = 2459829.14583

# ======================================================
# Test sgp4

satellite = Satrec.twoline2rv(tle[0], tle[1])
e, r, v = satellite.sgp4(jd, 0.0)
print("\n")
print(f"Sgp4 position: {r}")
print(f"Sgp4 velocity: {v}")
print("\n")

# ======================================================
# Test Spice Toolbox

tle[0] += "\x00"

[_, tle_elements] = spice.getelm(1957, len(tle[0]), tle)
geoph_data_list = ["J2", "J3", "J4", "KE", "QO", "SO", "ER", "AE"]
geophs = [
    float(spice.bodvrd("EARTH", geoph_data, 1)[1])
    for geoph_data in geoph_data_list
]

state_vectors = spice.evsgp4(second_epoch, geophs, tle_elements)

print(f"Spiceypy result: {state_vectors}")
print("\n")


# =======================================================
# Check relative distance

def calculate_relative_distance(p1, p2):
    return (
        (p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2
    ) ** (0.5)


target = [-1588.5814808844007, -6685.071887790887, -496.88254813664855]
chaser = [4541.476389764929, -2047.1242116769597, 4876.253098917813]

relative_distance = calculate_relative_distance(target, chaser)
print(f"Relative Distance: {relative_distance}")
