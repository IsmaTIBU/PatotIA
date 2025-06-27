from .trajectory_generation import *
from .modele_differentiel import *
from .Robot_repr import bras_rob_model3D


# Display each transformation matrix to track the calculation and store the matrices in a list

def main_analyse():
    qu = float(input("Joint angle q1 in degrees:\n"))
    qd = float(input("Joint angle q2 in degrees:\n"))
    qt = float(input("Joint angle q3 in degrees:\n"))

    q = [qu, qd, qt]

    transformation_matrices_calc = generate_transformation_matrices(q, dh, round_p=(5, 1e-6))
    transformation_matrices_show = generate_transformation_matrices(q, dh, round_p=(2, 1e-6))
    print("Translation matrix T01:\n", transformation_matrices_show[0])
    print("\nTranslation matrix T12:\n", transformation_matrices_show[1])
    print("\nTranslation matrix T23:\n", transformation_matrices_show[2])
    print("\nTranslation matrix T34:\n", transformation_matrices_show[3])

    # Calculate the complete transformation T(0,4)
    print(f"\nTranslation matrix T0{len(dh['sigma_i'])} :")
    matrice_T0Tn = matrice_Tn(dh, q)
    matrice_T0Tn_rounded = np.round(matrice_T0Tn, decimals=0)
    print(matrice_T0Tn_rounded.astype(int))

    # For this project, Z0 represents the vertical axis and Y0 the depth axis
    print("\nFinal coordinates using matrix T(0,n) in terms of X0,Y0,Z0:\n", xy_Ot(matrice_T0Tn))
    rep = int(input("Would you like to verify these values with a 3D simulation of the arm? \n(1) for 'yes', (2) for 'no':"))
    if rep == 1:
        bras_rob_model3D(Liaisons, q)
    else:
        pass

    print("\nCoordinates (x, y, z) in mm based on the angles in the q list:")
    Xd_mgd = mgd(q, Liaisons)
    x_mgd = Xd_mgd[0]
    y_mgd = Xd_mgd[1]
    z_mgd = Xd_mgd[2]
    print("x calculated by MGD:", x_mgd, "\ny calculated by MGD:", y_mgd, "\nz calculated by MGD:", z_mgd, "\n")
    rep = int(input(
        "Would you like to verify these values by using them as end-effector coordinates and applying MGI to find the initial angles? \n(1) for 'yes', (2) for 'no, I'll input other values', (3) for 'no, I'll continue':"))
    if rep == 1:
        verifier_solutions(Xd_mgd, Liaisons)
        Rep = int(input("Would you like a representation of the arm's position for each given configuration?\n(1) for 'yes', (2) for 'no'"))
        if Rep == 1:
            sol = mgi(Xd_mgd, Liaisons)
            for i, solution in enumerate(sol):  # Iterate over each solution
                bras_rob_model3D(Liaisons, np.degrees(solution))  # Convert to degrees before passing
            else:
                pass
    elif rep == 2:
        print("Please input the desired coordinates to reach")
        x_mgi = float(input("End-effector x coordinate:\n"))
        y_mgi = float(input("End-effector y coordinate:\n"))
        z_mgi = float(input("End-effector z coordinate:\n"))
        Xd = [x_mgi, y_mgi, z_mgi]
        verifier_solutions(Xd, Liaisons)
        Rep = int(input(
            "Would you like a representation of the arm's position for each given configuration?\n(1) for 'yes', (2) for 'no'"))
        if Rep == 1:
            sol = mgi(Xd, Liaisons)
            for i, solution in enumerate(sol):  # Iterate over each solution
                bras_rob_model3D(Liaisons, np.degrees(solution))  # Convert to degrees before passing
            else:
                pass
    else:
        pass

    # Calculate geometric Jacobian
    REP = int(
        input(
            f"Would you like to calculate the robot's Jacobian for the initial configuration ({q[0]}, {q[1]}, {q[2]})? \n(1) for 'yes', (2) for 'no': "
        )
    )
    if REP == 1:
        J_geo = Jacob_geo(transformation_matrices_calc)
        print("\nGeometric Jacobian:")
        print(np.array2string(J_geo, formatter={'float_kind': lambda x: f"{x:7.1f}"}))

        # Calculate analytical Jacobian
        # Matrices in analytical form
        # Jacob_an = Jacob_analytique(q)
        # print("\nAnalytical Jacobian:")
        # sp.pprint(Jacob_an)

        # MDD for dq1=0.1, dq2=0.2, dq3=0.3 applied to the initial position q1=0, q2=0, q3=0
        print("\nPlease input the joint velocities you'd like to apply to the robot:")
        dq1 = float(input("dq1:\n"))
        dq2 = float(input("dq2:\n"))
        dq3 = float(input("dq3:\n"))
        dq = [dq1, dq2, dq3]
        dX = MDD(dq, J_geo)
        dX_vert = sp.Matrix(np.round(np.array(dX).reshape(-1, 1), 1))
        print("\nValues of the robot's linear and angular velocities for the requested configuration (", q[0], ",", q[1], ",", q[2], ") when applying dq1 =", dq1, ", dq2 =", dq2, ", dq3 =", dq3)
        sp.pprint(dX_vert)
        # Verification using MDI inverting the Jacobian
        rep = int(
            input(
                "Would you like to verify these values by using them as the robot's linear and angular velocities? \n(1) for 'yes', (2) for 'no, I'll input other values', (3) for 'no, I'll continue':"))
        if rep == 1:
            dq = MDI(dX, J_geo)
            dq_vert = np.array(dq).reshape(-1, 1)
            print(
                "\nGEOMETRIC calculation of the robot's joint velocities for its initial position when applying dx =",
                dX[0], ", dy=",
                dX[1], ", dz=", dX[2], ", wx=", dX[3], ", wy=", dX[4], ", wz=", dX[5])
            print(dq_vert)
        elif rep == 2:
            print("\nPlease input the following 6 values")
            dx = float(input("dx="))
            dy = float(input("dy="))
            dz = float(input("dz="))
            wx = float(input("wx="))
            wy = float(input("wy="))
            wz = float(input("wz="))
            dX = [dx, dy, dz, wx, wy, wz]
            dq = MDI(dX, J_geo)
            dq_vert = np.array(dq).reshape(-1, 1)
            print(
                "\nGEOMETRIC calculation of the robot's joint velocities for its initial position when applying dx =",
                dx, ", dy=",
                dy, ", dz=", dz, ", wx=", wx, ", wy=", wy, ", wz=", wz)
            print(dq_vert)
        else:
            pass
        print("\n")
    else:
        pass
