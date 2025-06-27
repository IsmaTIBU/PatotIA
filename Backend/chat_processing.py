import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import math as m
import numpy as np
import sympy as sp
from src import generate_transformation_matrices, matrice_Tn, bras_rob_model3D, mgi, mgd, Jacob_geo, MDD
from src import dh, Liaisons

ai_instance = None  # Variable para guardar la referencia al AI

def set_ai_reference(ai):
    """Guardar referencia al AI para poder leer su log"""
    global ai_instance
    ai_instance = ai

def read_log():
    """Leer el log del AI"""
    if ai_instance:
        return ai_instance.get_log_for_processing()
    else:
        return []

def convert_with_numpy(value_str):
    """Evalúa expresiones que contienen np.pi, math, etc."""
    
    if not isinstance(value_str, str):
        return float(value_str)
    
    try:
        # Intentar conversión directa primero
        return float(value_str)
    except ValueError:
        # Si falla, evaluar como expresión Python
        try:
            # Evaluar con numpy y math disponibles
            result = eval(value_str, {"np": np, "math": m, "pi": np.pi})
            return float(result)
        except:
            print(f"❌ No se pudo convertir: {value_str}")
            return None
        
def verificar_angulos_en_logs():
    """
    Verifica si en los logs anteriores hay ángulos disponibles.
    Prioridad: log1 > log2 > log3 (más reciente a más antiguo)
    """
    if not ai_instance:
        return {'found': False, 'angles': {}, 'source_log': None, 'angular_unit': None}
    
    logs = ai_instance.get_log_for_processing()
    
    if not logs:
        return {'found': False, 'angles': {}, 'source_log': None, 'angular_unit': None}
    
    # Verificar logs en orden de prioridad (más reciente primero)
    for i, log_entry in enumerate(logs):
        if log_entry['error']:  # Saltar logs con errores
            continue
            
        prediction = log_entry['prediction']
        
        if not isinstance(prediction, dict) or 'parametros' not in prediction:
            continue
            
        parametros = prediction['parametros']
        angles_found = {}
        angular_unit = parametros.get('unidad_angular', 'grados')
        
        # Verificar q1, q2, q3
        for angle_key in ['q1', 'q2', 'q3']:
            if (angle_key in parametros and 
                parametros[angle_key] is not None and 
                parametros[angle_key] != ""):
                angles_found[angle_key] = parametros[angle_key]
        
        # Si encontramos los 3 ángulos, retornamos este log
        if len(angles_found) == 3:
            return {
                'found': True,
                'angles': angles_found,
                'source_log': i + 1,
                'angular_unit': angular_unit,
                'operation': prediction.get('operacion', 'unknown')
            }
    
    return {'found': False, 'angles': {}, 'source_log': None, 'angular_unit': None}

def verificar_coordenadas_en_logs():
    """
    Verifica si en los logs anteriores hay coordenadas disponibles.
    Prioridad: log1 > log2 > log3 (más reciente a más antiguo)
    
    Busca coordenadas en:
    - posicion_objetivo (de inverse kinematics)
    - posicion_efector (de simulation)
    - resultados de direct kinematics (si los guardáramos)
    """
    if not ai_instance:
        return {'found': False, 'coordinates': {}, 'source_log': None, 'position_unit': None}
    
    logs = ai_instance.get_log_for_processing()
    
    if not logs:
        return {'found': False, 'coordinates': {}, 'source_log': None, 'position_unit': None}
    
    # Verificar logs en orden de prioridad (más reciente primero)
    for i, log_entry in enumerate(logs):
        if log_entry['error']:  # Saltar logs con errores
            continue
            
        prediction = log_entry['prediction']
        
        if not isinstance(prediction, dict) or 'parametros' not in prediction:
            continue
            
        parametros = prediction['parametros']
        coordinates_found = {}
        position_unit = None
        coord_source = None
        
        # OPCIÓN 1: Buscar en posicion_objetivo (inverse kinematics)
        if 'posicion_objetivo' in parametros:
            pos_obj = parametros['posicion_objetivo']
            if (pos_obj.get('x') not in ["", None] and 
                pos_obj.get('y') not in ["", None] and 
                pos_obj.get('z') not in ["", None]):
                
                coordinates_found = {
                    'x': pos_obj['x'],
                    'y': pos_obj['y'], 
                    'z': pos_obj['z']
                }
                position_unit = pos_obj.get('unidad_posicion', 'mm')
                coord_source = 'posicion_objetivo'
        
        # OPCIÓN 2: Buscar en posicion_efector (simulation)
        elif 'posicion_efector' in parametros:
            pos_ef = parametros['posicion_efector']
            if (pos_ef.get('x') not in ["", None] and 
                pos_ef.get('y') not in ["", None] and 
                pos_ef.get('z') not in ["", None]):
                
                coordinates_found = {
                    'x': pos_ef['x'],
                    'y': pos_ef['y'],
                    'z': pos_ef['z']
                }
                position_unit = pos_ef.get('unidad_posicion', 'mm')
                coord_source = 'posicion_efector'
        
        # Si encontramos coordenadas completas, retornamos este log
        if len(coordinates_found) == 3:
            return {
                'found': True,
                'coordinates': coordinates_found,
                'source_log': i + 1,
                'position_unit': position_unit,
                'operation': prediction.get('operacion', 'unknown'),
                'coord_source': coord_source
            }
    
    return {'found': False, 'coordinates': {}, 'source_log': None, 'position_unit': None}
        
def matrices_dh(parametros):
    if (parametros["q1"] != "" and parametros["q1"] is not None and
        parametros["q2"] != "" and parametros["q2"] is not None and
        parametros["q3"] != "" and parametros["q3"] is not None):
    
        q1 = parametros["q1"] 
        q2 = parametros["q2"]
        q3 = parametros["q3"]
        
        q1 = convert_with_numpy(q1)
        q2 = convert_with_numpy(q2)
        q3 = convert_with_numpy(q3)
        
        if parametros["unidad_angular"] == "radianes":
            q1 = round(m.degrees(q1),2)
            q2 = round(m.degrees(q2),2)
            q3 = round(m.degrees(q3),2)

        q=[q1,q2,q3]

        transformation_matrices_show = generate_transformation_matrices(q, dh, round_p=(2, 1e-6))
        print("Translation matrix T01:\n", transformation_matrices_show[0])
        print("\nTranslation matrix T12:\n", transformation_matrices_show[1])
        print("\nTranslation matrix T23:\n", transformation_matrices_show[2])
        print("\nTranslation matrix T34:\n", transformation_matrices_show[3])

        print(f"\nTranslation matrix T0{len(dh['sigma_i'])} :")
        matrice_T0Tn = matrice_Tn(dh, q)
        matrice_T0Tn_rounded = np.round(matrice_T0Tn, decimals=0)
        print(matrice_T0Tn_rounded.astype(int))

    else:
        resultado_verificacion = verificar_angulos_en_logs()
        
        if resultado_verificacion['found']:

            angles_from_log = resultado_verificacion['angles']
            
            # Crear parámetros temporales con los ángulos del log
            temp_parametros = {
                'q1': angles_from_log['q1'],
                'q2': angles_from_log['q2'],
                'q3': angles_from_log['q3'],
                'unidad_angular': resultado_verificacion['angular_unit']}
            
            # print(temp_parametros,"\n")
            # Llamar recursivamente con los parámetros del log
            print(f"\nSorry I couldn't find any specified angles in your query\nSo I used the angles you talked about recently; q1={angles_from_log['q1']}°, q2={angles_from_log['q2']}°, q2={angles_from_log['q3']}°\nType 'help' or 'h' if you need some guidance\n")
            direct_kine(temp_parametros)
        else:
            print(f"\nSorry I couldn't find any specified angles in your present query or recent ones\nType 'help' or 'h' if you need some guidance\nOr re-phrase the sentence, remember that for the moment I'am a quite limited model, sorry for the inconvenience...\n")

def simulation(parametros):
    # CASO 1: Tenemos ángulos directamente
    if (parametros.get("q1", "") != "" and parametros.get("q1") is not None and
        parametros.get("q2", "") != "" and parametros.get("q2") is not None and
        parametros.get("q3", "") != "" and parametros.get("q3") is not None):
                
        q1 = convert_with_numpy(parametros["q1"])
        q2 = convert_with_numpy(parametros["q2"])
        q3 = convert_with_numpy(parametros["q3"])

        if parametros.get("unidad_angular") == "radianes":
            q1 = round(m.degrees(q1), 2)
            q2 = round(m.degrees(q2), 2)
            q3 = round(m.degrees(q3), 2)

        q = [q1, q2, q3]
        bras_rob_model3D(Liaisons, q)
        return  # ✅ IMPORTANTE: salir después de ejecutar
    
    # CASO 2: Tenemos coordenadas de posición del efector
    elif ("posicion_efector" in parametros and
          parametros["posicion_efector"].get("x", "") != "" and parametros["posicion_efector"]["x"] is not None and
          parametros["posicion_efector"].get("y", "") != "" and parametros["posicion_efector"]["y"] is not None and
          parametros["posicion_efector"].get("z", "") != "" and parametros["posicion_efector"]["z"] is not None):
        
        x = float(parametros["posicion_efector"]["x"])
        y = float(parametros["posicion_efector"]["y"])
        z = float(parametros["posicion_efector"]["z"])

        if parametros["posicion_efector"]["unidad_posicion"]=="cm":
            x=x/10
            y=y/10
            z=z/10
        
        if parametros["posicion_efector"]["unidad_posicion"]=="m":
            x=x/1000
            y=y/1000
            z=z/1000
                
        Xd = [x, y, z]
        sol = mgi(Xd, Liaisons)

        for i, solution in enumerate(sol):
            angles_deg = np.degrees(solution)
            print(f"  Solution {i+1}: {angles_deg}")
            bras_rob_model3D(Liaisons, angles_deg)
        return  # ✅ IMPORTANTE: salir después de ejecutar
    
    # CASO 3: No tenemos datos directos - buscar en logs
    else:
        resultado_verificacion_ang = verificar_angulos_en_logs()
        resultado_verificacion_coord = verificar_coordenadas_en_logs()
        
        # Subcase 3.1: Tenemos ambos - priorizar el más reciente
        if resultado_verificacion_ang['found'] and resultado_verificacion_coord['found']:
            if resultado_verificacion_ang["source_log"] <= resultado_verificacion_coord["source_log"]:
                # Ángulos son más recientes o iguales
                angles_from_log = resultado_verificacion_ang['angles']
                
                # ✅ CORRECCIÓN: Asegurar que temp_parametros cumpla las condiciones del CASO 1
                temp_parametros = {
                    'q1': angles_from_log['q1'],
                    'q2': angles_from_log['q2'],
                    'q3': angles_from_log['q3'],
                    'unidad_angular': resultado_verificacion_ang['angular_unit']
                }
                
                print(f"\nSorry I couldn't find any specified angles in your query\nSo I used the angles you talked about recently; q1={angles_from_log['q1']}°, q2={angles_from_log['q2']}°, q2={angles_from_log['q3']}°\nType 'help' or 'h' if you need some guidance\n")
                simulation(temp_parametros)
                
            else:
                # Coordenadas son más recientes
                coord_from_log = resultado_verificacion_coord['coordinates']
                
                # ✅ CORRECCIÓN: Asegurar que temp_parametros cumpla las condiciones del CASO 2
                temp_parametros = {
                    'posicion_efector': {
                        'x': coord_from_log['x'],
                        'y': coord_from_log['y'],
                        'z': coord_from_log['z'],
                        'unidad_posicion': resultado_verificacion_coord['position_unit']
                    }
                }
                
                print(f"\nSorry I couldn't find any specified coordinates in your query\nSo I used the ones you talked about recently; x={coord_from_log['x']}°, y={coord_from_log['y']}°, z={coord_from_log['z']}°\nType 'help' or 'h' if you need some guidance\n")
                simulation(temp_parametros)

        # Subcase 3.2: Solo tenemos ángulos
        elif resultado_verificacion_ang["found"] and not resultado_verificacion_coord["found"]:
            angles_from_log = resultado_verificacion_ang['angles']
            
            temp_parametros = {
                'q1': angles_from_log['q1'],
                'q2': angles_from_log['q2'],
                'q3': angles_from_log['q3'],
                'unidad_angular': resultado_verificacion_ang['angular_unit']
            }
            
            print(f"\nSorry I couldn't find any specified angles in your query\nSo I used the angles you talked about recently; q1={angles_from_log['q1']}°, q2={angles_from_log['q2']}°, q2={angles_from_log['q3']}°\nType 'help' or 'h' if you need some guidance\n")
            simulation(temp_parametros)

        # Subcase 3.3: Solo tenemos coordenadas
        elif not resultado_verificacion_ang["found"] and resultado_verificacion_coord["found"]:
            coord_from_log = resultado_verificacion_coord['coordinates']
            
            temp_parametros = {
                'posicion_efector': {
                    'x': coord_from_log['x'],
                    'y': coord_from_log['y'],
                    'z': coord_from_log['z'],
                    'unidad_posicion': resultado_verificacion_coord['position_unit']
                }
            }
            
            print(f"\nSorry I couldn't find any specified coordinates in your query\nSo I used the ones you talked about recently; x={coord_from_log['x']}°, y={coord_from_log['y']}°, z={coord_from_log['z']}°\nType 'help' or 'h' if you need some guidance\n")
            simulation(temp_parametros)

        # Subcase 3.4: No tenemos nada
        else:
            print(f"\nSorry, I couldn't find angles or coordinates in your query or recent history.")
            print("Type 'help' or 'h' for guidance on how to specify simulation parameters.")
            print("Or re-phrase the sentence, remember that for the moment I'am a quite limited model, sorry for the inconvenience...\n")
            return  # ✅ IMPORTANTE: salir sin recursión
        

def direct_kine(parametros):
    if (parametros["q1"] != "" and parametros["q1"] is not None and
        parametros["q2"] != "" and parametros["q2"] is not None and
        parametros["q3"] != "" and parametros["q3"] is not None):
        
        q1 = parametros["q1"] 
        q2 = parametros["q2"]
        q3 = parametros["q3"]
        
        q1 = convert_with_numpy(q1)
        q2 = convert_with_numpy(q2)
        q3 = convert_with_numpy(q3)
        
        if parametros["unidad_angular"] == "radianes":
            q1 = m.degrees(q1)
            q2 = m.degrees(q2)
            q3 = m.degrees(q3)

        q=[q1,q2,q3]

        Xd_mgd = mgd(q, Liaisons)
        x_mgd = round(Xd_mgd[0],2)
        y_mgd = round(Xd_mgd[1],2)
        z_mgd = round(Xd_mgd[2],2)
        print("\nCoordinates of the end effector with those joint angles:")  
        print("x=", x_mgd, "\ny=", y_mgd, "\nz=", z_mgd, "\n")
    
    else:
        resultado_verificacion = verificar_angulos_en_logs()
        
        if resultado_verificacion['found']:

            angles_from_log = resultado_verificacion['angles']
            
            # Crear parámetros temporales con los ángulos del log
            temp_parametros = {
                'q1': angles_from_log['q1'],
                'q2': angles_from_log['q2'],
                'q3': angles_from_log['q3'],
                'unidad_angular': resultado_verificacion['angular_unit']}
            
            # print(temp_parametros,"\n")
            # Llamar recursivamente con los parámetros del log
            print(f"\nSorry I couldn't find any specified angles in your query\nSo I used the angles you talked about recently; q1={angles_from_log['q1']}°, q2={angles_from_log['q2']}°, q2={angles_from_log['q3']}°\nType 'help' or 'h' if you need some guidance\n")
            direct_kine(temp_parametros)
        else:
            print(f"\nSorry I couldn't find any specified angles in your present query or recent ones\nType 'help' or 'h' if you need some guidance\nOr re-phrase the sentence, remember that for the moment I'am a quite limited model, sorry for the inconvenience...\n")

        

def invert_kine(parametros):
    if (parametros["posicion_objetivo"]["x"] != "" and parametros["posicion_objetivo"]["x"] is not None and
        parametros["posicion_objetivo"]["y"] != "" and parametros["posicion_objetivo"]["y"] is not None and
        parametros["posicion_objetivo"]["z"] != "" and parametros["posicion_objetivo"]["z"] is not None):
        
        
        x = float(parametros["posicion_objetivo"]["x"])
        y = float(parametros["posicion_objetivo"]["y"])
        z = float(parametros["posicion_objetivo"]["z"])

        if parametros["posicion_objetivo"]["unidad_posicion"]=="cm":
            x=x/10
            y=y/10
            z=z/10
        
        if parametros["posicion_objetivo"]["unidad_posicion"]=="m":
            x=x/1000
            y=y/1000
            z=z/1000
                
        Xd = [x, y, z]
        sol = mgi(Xd, Liaisons)

        print("Solutions in degrees ( °)")
        for i, solution in enumerate(sol):
            angles_deg = np.degrees(solution)
            angles_rounded = np.round(angles_deg, 2)
            print(f"  Solution {i+1}: {angles_rounded}")

    else:
        resultado_verificacion = verificar_coordenadas_en_logs()
        if resultado_verificacion['found']:

            coord_from_log = resultado_verificacion['coordinates']
            
            # Crear parámetros temporales con los ángulos del log
            temp_parametros = {'posicion_objetivo': {
                'x': coord_from_log['x'],
                'y': coord_from_log['y'],
                'z': coord_from_log['z'],
                'unidad_posicion': resultado_verificacion['position_unit'], }}
            
            # print(temp_parametros,"\n")
            # Llamar recursivamente con los parámetros del log
            print(f"\nSorry I couldn't find any specified coordinates in your query\nSo I used the ones you talked about recently; x={coord_from_log['x']}°, y={coord_from_log['y']}°, z={coord_from_log['z']}°\nType 'help' or 'h' if you need some guidance\n")
            invert_kine(temp_parametros)
        else:
            print(f"\nSorry I couldn't find any specified coordinates in your present query or recent ones\nType 'help' or 'h' if you need some guidance\nOr re-phrase the sentence, remember that for the moment I'am a quite limited model, sorry for the inconvenience...\n")


def jacobiano(parametros):
    if ((parametros["q1"] != "" and parametros["q1"] is not None and
        parametros["q2"] != "" and parametros["q2"] is not None and
        parametros["q3"] != "" and parametros["q3"] is not None) and
        (parametros["q1_dot"] != "" and parametros["q1_dot"] is not None and
         parametros["q2_dot"] != "" and parametros["q2_dot"] is not None and
         parametros["q3_dot"] != "" and parametros["q3_dot"] is not None)):
        
        q1 = parametros["q1"] 
        q2 = parametros["q2"]
        q3 = parametros["q3"]
        dq1 = parametros["q1_dot"] 
        dq2 = parametros["q2_dot"]
        dq3 = parametros["q3_dot"]
        
        q1 = convert_with_numpy(q1)
        q2 = convert_with_numpy(q2)
        q3 = convert_with_numpy(q3)
        dq1 = convert_with_numpy(dq1)
        dq2 = convert_with_numpy(dq2)
        dq3 = convert_with_numpy(dq3)
        
        if parametros["unidad_angular"] == "radianes":
            q1 = m.degrees(q1)
            q2 = m.degrees(q2)
            q3 = m.degrees(q3)

        q=[q1, q2, q3]
        
        transformation_matrices_calc = generate_transformation_matrices(q, dh, round_p=(5, 1e-6))
        J_geo = Jacob_geo(transformation_matrices_calc)
        print("\nGeometric Jacobian:")
        print(np.array2string(J_geo, formatter={'float_kind': lambda x: f"{x:7.1f}"}))

        dq = [dq1, dq2, dq3]
        dX = MDD(dq, J_geo)
        dX_vert = sp.Matrix(np.round(np.array(dX).reshape(-1, 1), 1))
        print("\nValues of the robot's linear and angular velocities for the requested configuration (", q[0], ",", q[1], ",", q[2], ") when applying dq1 =", dq1, ", dq2 =", dq2, ", dq3 =", dq3)
        sp.pprint(dX_vert)

    elif((parametros["q1"] != "" and parametros["q1"] is not None and
          parametros["q2"] != "" and parametros["q2"] is not None and
          parametros["q3"] != "" and parametros["q3"] is not None) and
        (parametros["q1_dot"] == "" or parametros["q1_dot"] is None and
         parametros["q2_dot"] == "" or parametros["q2_dot"] is None and
         parametros["q3_dot"] == "" or parametros["q3_dot"] is None)): 
        
        q1 = parametros["q1"] 
        q2 = parametros["q2"]
        q3 = parametros["q3"]

        q1 = convert_with_numpy(q1)
        q2 = convert_with_numpy(q2)
        q3 = convert_with_numpy(q3)

        if parametros["unidad_angular"] == "radianes":
            q1 = m.degrees(q1)
            q2 = m.degrees(q2)
            q3 = m.degrees(q3)

        q=[q1, q2, q3]
        
        transformation_matrices_calc = generate_transformation_matrices(q, dh, round_p=(5, 1e-6))
        J_geo = Jacob_geo(transformation_matrices_calc)
        print("\nJacobian:")
        print(np.array2string(J_geo, formatter={'float_kind': lambda x: f"{x:7.1f}"}))
        print("\nIf you would like to see the linear and angular velocities of the robot you must enter the joint velocities first.\nType 'help' or 'h' if you need some guidance\nOr re-phrase the sentence, remember that for the moment I'am a quite limited model, sorry for the inconvenience...\n")

    elif((parametros["q1"] == "" or parametros["q1"] is None and
          parametros["q2"] == "" or parametros["q2"] is None and
          parametros["q3"] == "" or parametros["q3"] is None) and
        ("q1_dot" in parametros or "q2_dot" in parametros or "q3_dot" in parametros)): 
        
        resultado_verificacion = verificar_angulos_en_logs()
        
        if resultado_verificacion['found']:

            angles_from_log = resultado_verificacion['angles']
            
            # Crear parámetros temporales con los ángulos del log
            temp_parametros = {
                'q1': angles_from_log['q1'],
                'q2': angles_from_log['q2'],
                'q3': angles_from_log['q3'],
                'unidad_angular': resultado_verificacion['angular_unit'], 
                'q1_dot': parametros["q1_dot"], 
                'q2_dot': parametros["q2_dot"], 
                'q3_dot': parametros["q3_dot"], 
                'unidad_velocidad': 'rad/s'}
            
            # print(temp_parametros,"\n")
            # Llamar recursivamente con los parámetros del log
            print(f"\nSorry I couldn't find any specified angles in your query\nSo I used the ones you talked about recently; q1={angles_from_log['q1']}°, q2={angles_from_log['q2']}°, q2={angles_from_log['q3']}°\nType 'help' or 'h' if you need some guidance\n")
            jacobiano(temp_parametros)
        
        else:
            print("Sorry, I couldn't find any angles specified nether in your query nor your most recent ones...\nRemember that to calculate de Jacobian to specify the angles is necessary\nType 'help' or 'h' if you need some guidance\nOr re-phrase the sentence, remember that for the moment I'am a quite limited model, sorry for the inconvenience...\n")

    else:
        resultado_verificacion = verificar_angulos_en_logs()
        
        if resultado_verificacion['found']:

            angles_from_log = resultado_verificacion['angles']
            
            # Crear parámetros temporales con los ángulos del log
            temp_parametros = {
                'q1': angles_from_log['q1'],
                'q2': angles_from_log['q2'],
                'q3': angles_from_log['q3'],
                'unidad_angular': resultado_verificacion['angular_unit'], 
                'q1_dot': "", 
                'q2_dot': "", 
                'q3_dot': "", 
                'unidad_velocidad': 'rad/s'}
            
            # print(temp_parametros,"\n")
            # Llamar recursivamente con los parámetros del log
            print(f"\nSorry I couldn't find any specified angles nor joint velocities in your query\nSo I used the angles you talked about recently; q1={angles_from_log['q1']}°, q2={angles_from_log['q2']}°, q2={angles_from_log['q3']}°\nType 'help' or 'h' if you need some guidance")
            jacobiano(temp_parametros)
        else:
            print(f"\nSorry I couldn't find any specified angles nor joint velocities in your present query or recent ones\nType 'help' or 'h' if you need some guidance\nOr re-phrase the sentence, remember that for the moment I'am a quite limited model, sorry for the inconvenience...\n")

def processing(prediction, error):

    if error:
        print(f"Error: {error}")
    else:
        # print("✅ Predicción obtenida:")
        print(prediction)
        operacion = prediction["operacion"]
        parametros = prediction["parametros"]
        
        if operacion == "matrices_transformacion":
            matrices_dh(parametros)
        
        if operacion == "simulacion_3d":
            simulation(parametros)
        
        if operacion == "cinematica_directa":
            direct_kine(parametros)

        if operacion == "cinematica_inversa":
            invert_kine(parametros)

        if operacion == "jacobiano":
            jacobiano(parametros)

if __name__=="__main__":
    from model_chat import RoboticsAI
    
    # Crear instancia del modelo
    ai = RoboticsAI()
    ai.load_model()

    # Obtener predicció    
    # user_input = "Calculate the robot's matrices with 20°, -65°, 78°"
    # user_input = "Calculate the robot's matrices with 0.2 rad, -pi/2 rad, 0.7 rad"
    # user_input = "Calculate the robot's matrices"
    
    # user_input = "Show me the robot with 20°, 65°, 78°"
    # user_input = " Simulate the robot end effector in the coordinates x=896, y=677 and z=-564 mm"
    # user_input = " Simulate it"

    # user_input = "Calculate de direct kinematics of the robot knowing that angle1=34, angle2=60, angle3=54 degrees"
    # user_input = "Calculate de direct kinematics of the robot knowing that angle1=0.2, angle2=-pi/3, angle3=0.7 in radians"
    # user_input = "Calculate the robot's position with 20°, -65°, 78°"
    # user_input = "Calculate the robot's coordinates"

    # user_input = "Calculate de inverse kinematics of the robot looking to obtain, x=-378, y=867 and z=786mm"
    # user_input = "Calculate de inverse kinematics"
    # user_input = "What is the configuration of the robot?"
    '''user_input = "What are the joint angles of the robot?"'''

    # user_input = "What's the jacobian of the robot when the angles are 20, 30, 45 degrees and all the speeds are 0.8 rad/s?"
    # user_input = "What's the jacobian of the robot when the angles are 20, 30, 45 degrees?"
    # user_input = "What's the jacobian of the robot when all the angles are 25 degrees?"
    # user_input = "Joint velocities are streaming at [0.8|2.4|1.6] radians per second, need jacobian analysis"
    '''user_input = "What's the jacobian of the robot when joint velocities are 0.8, -0.2 and 0.33 rad/s?"'''
    user_input = "What is the Jacobian?"

    '''CORREGIR LAS QUE VIENEN ASI'''
    prediction, error = ai.predict(user_input)
    processing(prediction, error)