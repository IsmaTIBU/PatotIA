import numpy as np


def matrice_Tim1_Ti(qi, ai_m1, alphai_m1, ri, Debug=False):
    """
    Computes the DH transformation matrix between two successive joints.

    Arguments:
        qi: Joint angle i (in radians).
        ai_m1: Length between joint axes (in mm).
        alphai_m1: Angle between z_{i-1} and z_i axes (in radians).
        ri: Offset along z_i (in mm).
        Debug: If True, displays intermediate steps for debugging.

    Returns:
        4x4 DH transformation matrix.
    """
    matrix_res = np.zeros((4, 4))

    # Compute coefficients
    matrix_res[0, 0] = np.cos(qi)
    matrix_res[0, 1] = -np.sin(qi)
    matrix_res[0, 2] = 0
    matrix_res[0, 3] = ai_m1

    matrix_res[1, 0] = np.sin(qi) * np.cos(alphai_m1)
    matrix_res[1, 1] = np.cos(qi) * np.cos(alphai_m1)
    matrix_res[1, 2] = -np.sin(alphai_m1)
    matrix_res[1, 3] = -ri * np.sin(alphai_m1)

    matrix_res[2, 0] = np.sin(qi) * np.sin(alphai_m1)
    matrix_res[2, 1] = np.cos(qi) * np.sin(alphai_m1)
    matrix_res[2, 2] = np.cos(alphai_m1)
    matrix_res[2, 3] = ri * np.cos(alphai_m1)

    matrix_res[3, 0] = 0
    matrix_res[3, 1] = 0
    matrix_res[3, 2] = 0
    matrix_res[3, 3] = 1

    if Debug:
        print(f"Debug matrice_Tim1_Ti:")
        print(f"  qi (rad) = {qi}, ai_m1 = {ai_m1}, alphai_m1 (rad) = {alphai_m1}, ri = {ri}")
        print(f"  Transformation matrix T_i-1,i:\n{matrix_res}")

    return matrix_res

def generate_transformation_matrices(q, dh, round_p=False, Debug=False):
    """
    Generates a list of transformation matrices T(i, i+1) from DH parameters.

    Arguments:
        dh: Dictionary containing DH parameters (a_i_m1, alpha_i_m1, r_i).
        q: List of joint angles (in radians).
        round_p: Tuple (number of decimals, threshold for rounding to 0).
        Debug: If True, displays intermediate steps for debugging.

    Returns:
        List of 4x4 transformation matrices T(i, i+1).
    """
    transformation_matrices = []

    # Local copy of q to avoid side effects
    q_local = q.copy()
    q_local.append(0)  # Add a fixed angle for the final joint
    q_local = np.radians(q_local)

    if Debug:
        print("\n--- Start of generate_transformation_matrices ---")
        print(f"Initial q: {q}")
        print(f"Local q with fixed angle: {q_local}")
        print(f"DH Parameters: {dh}")

    for i in range(len(dh['a_i_m1'])):
        t_i_ip1 = matrice_Tim1_Ti(
            q_local[i],
            dh['a_i_m1'][i],
            dh['alpha_i_m1'][i],
            dh['r_i'][i],
            Debug=Debug
        )

        if round_p:
            t_i_ip1 = np.round(t_i_ip1, round_p[0])
            t_i_ip1[np.abs(t_i_ip1) < round_p[1]] = 0

        if Debug:
            print(f"\nTransformation matrix T_{i},{i+1} calculated:\n{t_i_ip1}")

        transformation_matrices.append(t_i_ip1)

    if Debug:
        print("\n--- End of generate_transformation_matrices ---")
        print(f"Generated matrices list:")
        for i, T in enumerate(transformation_matrices):
            print(f"Matrix T_{i},{i+1}:\n{T}")

    return transformation_matrices

def matrice_Tn(dh, q, Debug=False):
    """
    Computes the T0,n matrix using DH parameters and angles q.

    Arguments:
        dh: Dictionary containing DH parameters.
        q: List of joint angles (in radians).
        Debug: If True, displays intermediate steps for debugging.

    Returns:
        T0,n matrix (4x4).
    """
    # Local copy of q to avoid side effects
    q_local = q.copy()
    q_local.append(0)  # Add a fixed angle for the final joint
    q_local = np.radians(q_local)

    nbliaison = len(dh['a_i_m1'])
    result_matrix = np.eye(4)

    if Debug:
        print("\n--- Start of matrice_Tn ---")
        print(f"Provided q: {q}")
        print(f"Local q with fixed angle: {q_local}")
        print(f"DH Parameters: {dh}")

    for i in range(nbliaison):
        mat_temp = matrice_Tim1_Ti(q_local[i], dh['a_i_m1'][i], dh['alpha_i_m1'][i], dh['r_i'][i], Debug=Debug)
        result_matrix = np.dot(result_matrix, mat_temp)

        if Debug:
            print(f"\nT0,{i+1} matrix after multiplication:\n{result_matrix}")

    if Debug:
        print("\n--- End of matrice_Tn ---")
        print(f"Final T0,n matrix:\n{result_matrix}")

    return result_matrix

def xy_Ot(result_matrix):
    """
    Extracts (x, y, z) coordinates from a T(0,n) matrix.
    """
    return result_matrix[:3, -1]

def mgd(q, Liaisons, Debug=False):
    """
    Computes the operational coordinates (x, y, z) for a given configuration.

    Arguments:
        q: List of joint angles in degrees (q1, q2, q3).
        Liaisons: List of link dimensions [horizontal, vertical, depth].
        Debug: If True, displays intermediate steps for debugging.

    Returns:
        np.array: Operational coordinates [x, y, z].
    """
    # Input validation
    assert len(q) == 3, "The angle list `q` must contain exactly 3 elements."
    assert len(Liaisons) == 3, "`Liaisons` must contain exactly 3 links."
    for liaison in Liaisons:
        assert len(liaison) == 3, "Each link must be defined by 3 parameters: [horizontal, vertical, depth]."

    # Link dimensions
    L1, L2, L3 = Liaisons

    # Joint angles in radians
    teta1, teta2, teta3 = np.radians(q)

    # Horizontal contributions
    x1 = L1[0] * np.cos(teta1)
    x2 = L2[2] * np.cos(teta1 + np.pi / 2)
    x3 = L2[1] * np.cos(teta1) * np.cos(teta2)
    x4 = L3[2] * np.cos(teta1 - np.pi / 2)
    x5 = L3[1] * np.cos(teta1) * np.cos(teta3 + teta2)

    # Vertical contributions
    y1 = L1[0] * np.sin(teta1)
    y2 = L2[2] * np.sin(teta1 + np.pi / 2)
    y3 = L2[1] * np.sin(teta1) * np.cos(teta2)
    y4 = L3[2] * np.sin(teta1 - np.pi / 2)
    y5 = L3[1] * np.sin(teta1) * np.cos(teta3 + teta2)

    # Height contributions
    z1 = L1[1]
    z2 = L2[1] * np.sin(teta2)
    z3 = L3[1] * np.sin(teta3 + teta2)

    # Final coordinates
    x = x1 + x2 + x3 + x4 + x5
    y = y1 + y2 + y3 + y4 + y5
    z = z1 + z2 + z3

    if Debug:
        print(f"Debug MGD:")
        print(f"  Angles (radians): teta1={teta1}, teta2={teta2}, teta3={teta3}")
        print(f"  Contributions X: {x1}, {x2}, {x3}, {x4}, {x5}")
        print(f"  Contributions Y: {y1}, {y2}, {y3}, {y4}, {y5}")
        print(f"  Contributions Z: {z1}, {z2}, {z3}")
        print(f"  Final coordinates: X={x}, Y={y}, Z={z}")

    return np.array([x, y, z], dtype=np.float64)

def mgi(Xd, Liaisons, Debug=False):
    """
    Computes joint angles to achieve a target configuration.
    """
    x, y, z = Xd
    L1 = Liaisons[0]  # [horizontal, vertical, depth]
    L2 = Liaisons[1]
    L3 = Liaisons[2]
    solutions = []

    def compute_solutions(q1):
        """
        Compute potential solutions for a given q1.
        """
        X = L2[1]
        Y = L3[1]
        Z1 = np.cos(q1) * x + np.sin(q1) * y - L1[0]
        Z2 = z - L1[1]

        if Debug:
            print(f"Debug: Z1={Z1}, Z2={Z2}, X={X}, Y={Y}")

        # Compute q3
        c3 = (Z1 ** 2 + Z2 ** 2 - X ** 2 - Y ** 2) / (2 * X * Y)
        if c3 < -1 or c3 > 1:
            return []  # No valid solution
        c3 = np.clip(c3, -1, 1)

        q31 = np.arctan2(np.sqrt(1 - c3 ** 2), c3)
        q32 = np.arctan2(-np.sqrt(1 - c3 ** 2), c3)

        if Debug:
            print(f"Debug: c3={c3}, q31={q31}, q32={q32}")

        # Compute q2
        B1 = X + Y * c3
        B21 = Y * np.sin(q31)
        B22 = Y * np.sin(q32)

        s21 = (B1 * Z2 - B21 * Z1) / (B1 ** 2 + B21 ** 2)
        c21 = (B1 * Z1 + B21 * Z2) / (B1 ** 2 + B21 ** 2)
        q21 = np.arctan2(s21, c21)

        s22 = (B1 * Z2 - B22 * Z1) / (B1 ** 2 + B22 ** 2)
        c22 = (B1 * Z1 + B22 * Z2) / (B1 ** 2 + B22 ** 2)
        q22 = np.arctan2(s22, c22)

        if Debug:
            print(f"Debug: q21={q21}, q22={q22}")

        return [[q1, q21, q31], [q1, q22, q32]]

    q1_1 = np.arctan2(y, x)
    solutions.extend(compute_solutions(q1_1))
    q1_2 = q1_1 - np.pi
    solutions.extend(compute_solutions(q1_2))

    return solutions

def verifier_solutions(Xd, Liaisons):
    """
    Verify all possible angle combinations using the mgi function.
    """
    solutions = mgi(Xd, Liaisons)

    print("\nPossible angle values to achieve the desired configuration Xd:", Xd)
    for i, sol in enumerate(solutions):
        print(f"Solution {i + 1} (in degrees): {np.round(np.degrees(sol), 2)}")

    for i, q in enumerate(np.degrees(solutions)):
        Xd_mgd = mgd(q, Liaisons)
        Xd_mgd = np.round(Xd_mgd, 3)
        error = np.linalg.norm(Xd_mgd - Xd)

        print(f"\nVerification of solution {i + 1}:")
        print(f"Angles (in degrees): {np.round((q), 2)}")
        print(f"Coordinates obtained by MGD: {Xd_mgd}")
        print(f"Error compared to the desired position: {np.round(error, 6)}")

        if error < 0.1:
            print("Result: Correct!")
        else:
            print("Result: Incorrect")
