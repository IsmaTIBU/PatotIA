from .trajectory_generation import *
from .modele_differentiel import *

# Afficher chaque matrice de transformation pour suivre le calcul et enregistrer dans une liste les matrices


Xd = [800, 0, 600]


qu=float(input("Angle de liaison q1 en degrée :\n"))
qd=float(input("Angle de liaison q2 en degrée :\n"))
qt=float(input("Angle de liaison q3 en degrée :\n"))


q = [qu,qd,qt]

V1 = float(input("Vitesse 1 :\n"))  # Vitesse 1 (par exemple 10 )
V2 = float(input("Vitesse 2 :\n"))  # Vitesse 2 (par exemple 20 )


transformation_matrices = generate_transformation_matrices(q,dh, round_p=(2, 1e-6))
print("Matrice de translation T01:\n",transformation_matrices[0])
print("\nMatrice de translation T12:\n",transformation_matrices[1])
print("\nMatrice de translation T23:\n",transformation_matrices[2])
print("\nMatrice de translation T34:\n",transformation_matrices[3])

# Calcul de la transformation complète T(0,4)
print(f"\nMatrice de translation T0{len(dh['sigma_i'])} :")
matrice_T0Tn = matrice_Tn(dh,q)
matrice_T0Tn_rounded = np.round(matrice_T0Tn, decimals=0)
print(matrice_T0Tn_rounded.astype(int))

# Pour ce TP Z0 représente l'axe vertical et Y0 celui de la profondeur
print("\nCoordonnées finales grace a matrice T(0,n) en fonction de X0,Y0,Z0:\n", xy_Ot(matrice_T0Tn))
print("\nCoordonnées (x, y, z) en mm en fonction des angles de la liste q:")
Xd_mgd = mgd(q, Liaisons)
x_mgd = Xd_mgd[0]
y_mgd = Xd_mgd[1]
z_mgd = Xd_mgd[2]
ray = round(np.sqrt(x_mgd ** 2 + y_mgd ** 2 + z_mgd ** 2), 2)

verifier_solutions(Xd, Liaisons)

# Calcule de Jacobienne geometrique
J_geo = Jacob_geo(transformation_matrices)
print("\nJacobienne geométrique:")
print(np.array2string(J_geo, formatter={'float_kind': lambda x: f"{x:7.1f}"}))
# Calcule de Jacobienne analytique
# Matrices sous forme analytique
Jacob_an = Jacob_analytique()
print("\nJacobienne analytique:")
sp.pprint(Jacob_an)


# MDD pour dq1=0.1, dq2=0.2, dq3=0.3 appliqué à la position initiale q1=0, q2=0 et q3=0
dq = [0.1, 0.3, 0.2]
dX = MDD(dq, J_geo)
dX_vert = sp.Matrix(np.round(np.array(dX).reshape(-1, 1), 1))

print("\nValeurs des vitesses linéaires et angulaires du robot pour sa position initiale lorsqu'on applique dq1 =",
      dq[0], ", dq2 =", dq[1], ", dq3 =", dq[2])
sp.pprint(dX_vert)
# Verification en utilisant MDI inversant la Jacobienne
dq = MDI(dX, J_geo)
dq_vert = np.array(dq).reshape(-1, 1)
print("\nCalcul GEOMETRIQUE des valeurs des vitesses articulaires du robot pour sa position initiale lorsqu'on applique dx =", dX[0], ", dy=",
      dX[1], ", dz=", dX[2], ", wx=", dX[3], ", wy=", dX[4], ", wz=", dX[5])
print(dq_vert)

print("\n")
# Genération de trajectoire
# Test génération de trajectoire


A = np.array([0, 500, 600])  # Ajusté pour respecter z_min
B = np.array([0, 500, 900])  # Ajusté pour respecter z_min

result_a, message_a = est_point_atteignable(A)
result_b, message_b = est_point_atteignable(B)

print(f"Point A: {message_a}")
print(f"Point B: {message_b}")

(q, qp, pos, delta) = traj(A, B, V1, V2, Debug=True)
