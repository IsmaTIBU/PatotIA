import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from .matrice_tn import *
from .const_v import *
from .modele_differentiel import *




def plot_3d_trajectory(positions, A, B, time):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(positions[:, 0], positions[:, 1], positions[:, 2], label="Operational trajectory", color='b')
    ax.scatter(A[0], A[1], A[2], color='g', label="Point A (Start)")
    ax.scatter(B[0], B[1], B[2], color='r', label="Point B (End)")
    ax.set_title("3D trajectory")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.legend()
    plt.show()

def plot_lois_de_mouvement(time, s, vitesse, acceleration, t1, t2, t3, t4):
    plt.figure()
    plt.plot(time, s, label="s(t)")
    plt.plot(time, vitesse, label="s'(t)")
    plt.plot(time, acceleration, label="s''(t)", color='r')
    for t_transition, label in zip([t1, t2, t3, t4], ['t1', 't2', 't3', 't4']):
        plt.axvline(x=t_transition, color='r', linestyle='--', label=label)
    plt.title("Temporal motion laws")
    plt.xlabel("Time (s)")
    plt.ylabel("Value")
    plt.legend()
    plt.grid()
    plt.show()

def plot_trajectoires_operationnelles(time, positions, t1, t2, t3, t4):
    plt.figure()
    plt.plot(time, positions[:, 0], label="x(t)")
    plt.plot(time, positions[:, 1], label="y(t)")
    plt.plot(time, positions[:, 2], label="z(t)")
    for t_transition, label in zip([t1, t2, t3, t4], ['t1', 't2', 't3', 't4']):
        plt.axvline(x=t_transition, color='r', linestyle='--', label=label)
    plt.title("Operational trajectory")
    plt.xlabel("Time (s)")
    plt.ylabel("Coordinates")
    plt.legend()
    plt.grid()
    plt.show()

def plot_vitesses_operationnelles(time, xp, yp, zp, t1, t2, t3, t4):
    plt.figure()
    plt.plot(time, xp, label="x'(t)")
    plt.plot(time, yp, label="y'(t)")
    plt.plot(time, zp, label="z'(t)")
    for t_transition, label in zip([t1, t2, t3, t4], ['t1', 't2', 't3', 't4']):
        plt.axvline(x=t_transition, color='r', linestyle='--', label=label)
    plt.title("Operational velocities")
    plt.xlabel("Time (s)")
    plt.ylabel("Velocities (mm/s)")
    plt.legend()
    plt.grid()
    plt.show()

def plot_accelerations_operationnelles(time, xpp, ypp, zpp, t1, t2, t3, t4):
    plt.figure()
    plt.plot(time, xpp, label="x''(t)")
    plt.plot(time, ypp, label="y''(t)")
    plt.plot(time, zpp, label="z''(t)")
    for t_transition, label in zip([t1, t2, t3, t4], ['t1', 't2', 't3', 't4']):
        plt.axvline(x=t_transition, color='r', linestyle='--', label=label)
    plt.title("Operational accelerations")
    plt.xlabel("Time (s)")
    plt.ylabel("Accelerations (mm/s²)")
    plt.legend()
    plt.grid()
    plt.show()

def plot_profils_articulaires(time, q, t1, t2, t3, t4):
    plt.figure()
    plt.plot(time, q[:, 0], label="q1(t)")
    plt.plot(time, q[:, 1], label="q2(t)")
    plt.plot(time, q[:, 2], label="q3(t)")
    for t_transition, label in zip([t1, t2, t3, t4], ['t1', 't2', 't3', 't4']):
        plt.axvline(x=t_transition, color='r', linestyle='--', label=label)
    plt.title("Joint trajectories")
    plt.xlabel("Time (s)")
    plt.ylabel("Angles (°)")
    plt.legend()
    plt.grid()
    plt.show()

def plot_vitesses_articulaires(time, qp, t1, t2, t3, t4):
    plt.figure()
    markers = ['o', 's', 'x', '^', 'v', '*']  # Liste de marqueurs
    for joint in range(qp.shape[1]):
        plt.plot(
            time,
            qp[:, joint],
            label=f"q{joint + 1}'(t)",
            marker=markers[joint % len(markers)],  # Marqueur cyclique
            markevery=50  # Ajouter des marqueurs tous les 50 points
        )
    for t_transition, label in zip([t1, t2, t3, t4], ['t1', 't2', 't3', 't4']):
        plt.axvline(x=t_transition, color='r', linestyle='--', label=label)
    plt.title("Joint velocities")
    plt.xlabel("Time (s)")
    plt.ylabel("Joint velocities (rad/s)")
    plt.legend()
    plt.grid()
    plt.show()

def traj(A, B, V1, V2,K, Debug=False):
    """
    Génère une trajectoire circulaire dans R^3 entre deux points A et B.
    Args:
        A (np.ndarray): Point de départ [x, y, z].
        B (np.ndarray): Point d'arrivée [x, y, z].
        V1 (float): Vitesse initiale.
        V2 (float): Vitesse finale.
        Debug (bool): Affiche les détails pour le débogage.
    Returns:
        tuple: (q, qp, positions) Trajectoires articulaires, vitesses et positions opérationnelles.
    """


    if Debug:
        print(f"A = {A} B = {B} V1 = {V1} V2 = {V2}")

    # Vecteur directeur AB et point médian
    center_y = (A[1] + B[1]) / 2
    center_z = (A[2] + B[2]) / 2
    ray = np.sqrt((B[1] - center_y) ** 2 + (B[2] - center_z) ** 2)

    # Assurer que le cercle est dans le plan ZY

    # Base locale pour le plan ZY
    u = np.array([0, 0, 1])  # Direction dans Z
    v = np.array([0, 1, 0])  # Direction dans Y






    # Temps de transition
    t1 = V1 / K
    #t2 = t1 + (np.pi * ray - (V1 ** 2 / (2 * K))) / V1
    t2 =(    (np.pi * ray) + V1*t1/2 - V1*(V2-V1)/K - ((V2-V1)/2)*((V2-V1)/K)   )/V1#o
    t3 = t2 + (V2 - V1) / K
    t4 = t3 + (np.pi * ray - (V2 ** 2 / (2 * K))) / V2
    tf = t4 + V2 / K











    # Génération du temps

    dt = 5/1000
    N = int (tf/dt)
    time = np.linspace(0, tf, N)
    vitesse = np.piecewise(
        time,
        [time < t1, (time >= t1) & (time < t2), (time >= t2) & (time < t3), (time >= t3) & (time < t4), time >= t4],
        [lambda t: K * t,
         lambda t: V1,
         lambda t: V1 + K * (t - t2),#modif o
         lambda t: V2,
         lambda t: V2 - K * (t - t4)]#modif o
    )

    acceleration = np.piecewise(
        time,
        [time < t1, (time >= t1) & (time < t2), (time >= t2) & (time < t3), (time >= t3) & (time < t4), time >= t4],
        [K,  # Accélération
         0,  # Vitesse constante
         K,  # Accélération
         0,  # Vitesse constante
         -K]  # Décélération
    )






    # print(f"ACCEL = {acceleration}")
    s = np.cumsum(vitesse * (time[1] - time[0]))

    # Calcul de l'angle initial
    theta0 = np.arctan2(A[2] - center_z, A[1] - center_y)

    theta = s / ray + theta0

    positions = np.array([
        np.full_like(theta, A[0]),  # x constant
        center_y + ray * np.cos(theta),  # y
        center_z + ray * np.sin(theta)  # z
    ]).T

    # Conversion articulaire et vitesses
    q, qp, xp, yp, zp = [], [], [], [], []

    # Calcul des vitesses opérationnelles
    delta_t = time[1:] - time[:-1]
    velocities = (positions[1:, :] - positions[:-1, :]) / delta_t[:, np.newaxis]

    # Interpolation pour aligner les vitesses avec les positions
    interp_vel_x = interp1d(time[:-1], velocities[:, 0], kind='linear', fill_value="extrapolate")
    interp_vel_y = interp1d(time[:-1], velocities[:, 1], kind='linear', fill_value="extrapolate")
    interp_vel_z = interp1d(time[:-1], velocities[:, 2], kind='linear', fill_value="extrapolate")

    xp = interp_vel_x(time)
    yp = interp_vel_y(time)
    zp = interp_vel_z(time)

    # Calcul des accélérations opérationnelles
    try:
        acc_x = np.gradient(xp, time)
        acc_y = np.gradient(yp, time)
        acc_z = np.gradient(zp, time)
    except Exception as e:
        print(f"Erreur lors du calcul des gradients : {e}")
        acc_x, acc_y, acc_z = np.zeros_like(xp), np.zeros_like(yp), np.zeros_like(zp)

    # Vérifiez que acc_x, acc_y, acc_z ont la même taille que time
    if len(acc_x) != len(time):
        print(f"Dimensions mismatch detected: acc_x({len(acc_x)}) != time({len(time)})")
        time_adjusted = np.linspace(0, tf, len(acc_x))
    else:
        time_adjusted = time

    # Interpolation pour aligner les accélérations avec le vecteur temps original
    interp_acc_x = interp1d(time_adjusted, acc_x, kind='linear', fill_value="extrapolate")
    interp_acc_y = interp1d(time_adjusted, acc_y, kind='linear', fill_value="extrapolate")
    interp_acc_z = interp1d(time_adjusted, acc_z, kind='linear', fill_value="extrapolate")

    # Appliquer l'interpolation pour xpp, ypp et zpp
    xpp = interp_acc_x(time)
    ypp = interp_acc_y(time)
    zpp = interp_acc_z(time)
    if Debug:
        print(f"Initial position {positions[0]} Final position {positions[-1]}")
    prev_q = None  # Variable pour stocker la configuration précédente

    for i, X in enumerate(positions):
        solutions = mgi(X, Liaisons)
        if solutions:
            if prev_q is None:
                # Si aucune configuration précédente, choisir arbitrairement la première solution
                q_i = solutions[1]
            else:
                # Calculer les variations pour chaque solution
                variations = [np.linalg.norm(np.array(solution) - np.array(prev_q)) for solution in solutions]
                min_index = np.argmin(variations)  # Index de la solution avec la moindre variation
                q_i = solutions[min_index]

            q.append(q_i)

            # Mise à jour de la configuration précédente
            prev_q = q_i

            # Calcul de la matrice Jacobienne pour la configuration courante
            T_matrices = generate_transformation_matrices(q_i, dh)
            J = Jacob_geo(T_matrices)
            J_translation = J[:3, :]  # Jacobienne translationnelle

            # Calcul des vitesses opérationnelles et articulaires
            v_operational = np.array([xp[i], yp[i], zp[i]])
            qp_i = MDI(v_operational, J_translation)  # Vitesses articulaires
            qp.append(qp_i)

            # Calcul des accélérations opérationnelles
            acc_operational = np.array([xpp[i], ypp[i], zpp[i]])
            # print(acc_operational)

        else:
            print(f"Erreur : MGI échoué pour X={X}")
            q.append(None)
            qp.append(None)


    # Convertir les listes en tableaux numpy
    q = np.array(q)
    qp = np.array(qp)

    if Debug:
        plot_3d_trajectory(positions, A, B, time)
        plot_lois_de_mouvement(time, s, vitesse, acceleration, t1, t2, t3, t4)
        plot_trajectoires_operationnelles(time, positions, t1, t2, t3, t4)
        plot_vitesses_operationnelles(time, xp, yp, zp, t1, t2, t3, t4)
        plot_accelerations_operationnelles(time, xpp, ypp, zpp, t1, t2, t3, t4)
        plot_profils_articulaires(time, q, t1, t2, t3, t4)
        plot_vitesses_articulaires(time, qp, t1, t2, t3, t4)
    return q, qp, positions, delta_t[0]





def est_point_atteignable(point):
    """
    Vérifie si un point est atteignable par le robot en fonction de son espace opérationnel.

    Args:
        point (tuple): Coordonnées (x, y, z) du point à vérifier.

    Returns:
        bool: True si le point est atteignable, False sinon.
        str: Message expliquant la raison si le point n'est pas atteignable.
    """
    x, y, z = point

    # Extraire les longueurs des liaisons depuis le dictionnaire
    longueur_bras = sum([np.linalg.norm(liaison) for liaison in Liaisons])  # Norme 3D de chaque liaison
    z_min = min([liaison[1] for liaison in Liaisons])  # Hauteur minimale
    z_max = max([liaison[1] for liaison in Liaisons]) + longueur_bras  # Hauteur maximale atteignable
    rayon_max = longueur_bras  # Rayon maximum atteint en projection 2D (xy)

    # Calcul de la distance en projection 2D
    rayon_xy = np.sqrt(x ** 2 + y ** 2)

    # Vérifier les contraintes
    if z < z_min or z > z_max:
        return False, f"The point is out of vertical limits : {z_min} <= z <= {z_max}."
    if rayon_xy > rayon_max:
        return False, f"The point is outside the maximum reachable radius in the XY plane : r <= {rayon_max}."

    # Vérifier avec MGI
    solutions = mgi(np.array([x, y, z]), Liaisons)
    if not solutions:
        return False, "The Inverse Kinematics did not find any solution to reach this point."

    return True, "The point is reachable."
