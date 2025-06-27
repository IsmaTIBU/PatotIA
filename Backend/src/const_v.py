import numpy as np

# Modified Denavit-Hartenberg parameters
dh = {}
dh["sigma_i"] = [0, 0, 0, 0]
dh["a_i_m1"] = [0, 150, 825, 735]
dh["alpha_i_m1"] = [0, np.pi / 2, 0, 0]
dh["r_i"] = [550, 0, 0, 0]

# Parameters for rounding
decimals = 2
threshold = 1e-7
round_p = (decimals, threshold)

# For 3D modeling of the robotic arm

"""In the lists, the parameters are defined in the following order: horizontal (X), vertical (Z), and depth (Y)."""
Liaisons = [
    [150, 550, 0],  # Joint 1
    [0, 825, 352],  # Joint 2
    [0, 735, 352],  # Joint 3
]
