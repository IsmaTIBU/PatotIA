# SCRIPT DE VERIFICACION - Usar en tu maquina local
import hashlib
import os

def verify_downloaded_model(model_path, hash_file_path):
    """Verifica un modelo descargado usando el archivo hash"""
    
    print("VERIFICANDO MODELO DESCARGADO")
    print("=" * 40)
    
    try:
        # Verificar que ambos archivos existen
        if not os.path.exists(model_path):
            print(f"ERROR: Archivo de modelo no encontrado: {model_path}")
            return False
            
        if not os.path.exists(hash_file_path):
            print(f"ERROR: Archivo de hash no encontrado: {hash_file_path}")
            return False
        
        # Leer hash original
        with open(hash_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            original_hash = None
            for line in lines:
                if line.startswith('MD5:'):
                    original_hash = line.split('MD5:')[1].strip()
                    break
        
        if not original_hash:
            print("ERROR: No se encontro hash MD5 en el archivo de verificacion")
            return False
        
        print(f"Verificando archivo: {model_path}")
        print(f"Usando hash de: {hash_file_path}")
        print(f"Hash esperado: {original_hash}")
        
        # Calcular hash del archivo descargado
        print("Calculando hash del archivo descargado...")
        with open(model_path, 'rb') as f:
            downloaded_hash = hashlib.md5(f.read()).hexdigest()
        
        print(f"Hash calculado: {downloaded_hash}")
        
        # Comparar
        if original_hash == downloaded_hash:
            print("SUCCESS: VERIFICACION EXITOSA - El archivo esta integro")
            return True
        else:
            print("ERROR: VERIFICACION FALLIDA - El archivo esta corrupto")
            print(f"   Hash original:    {original_hash}")
            print(f"   Hash descargado:  {downloaded_hash}")
            return False
            
    except Exception as e:
        print(f"ERROR verificando archivo: {e}")
        return False

def verify_model_interactive():
    """Version interactiva para usar desde la consola"""
    
    print("VERIFICADOR DE MODELOS INTERACTIVO")
    print("=" * 50)
    
    # Buscar archivos automaticamente
    current_dir = os.getcwd()
    pth_files = [f for f in os.listdir('.') if f.endswith('.pth')]
    hash_files = [f for f in os.listdir('.') if f.endswith('_hash.txt')]
    
    print(f"Directorio actual: {current_dir}")
    print(f"Archivos .pth encontrados: {pth_files}")
    print(f"Archivos *_hash.txt encontrados: {hash_files}")
    
    if not pth_files:
        print("No se encontraron archivos .pth en el directorio actual")
        return False
    
    if not hash_files:
        print("No se encontraron archivos _hash.txt en el directorio actual")
        return False
    
    # Si hay un solo par, usarlos automaticamente
    if len(pth_files) == 1 and len(hash_files) == 1:
        model_file = pth_files[0]
        hash_file = hash_files[0]
        print(f"Usando automaticamente: {model_file} y {hash_file}")
    else:
        # Permitir seleccion manual
        print("Multiples archivos encontrados. Selecciona:")
        for i, f in enumerate(pth_files):
            print(f"  {i+1}. {f}")
        
        try:
            choice = int(input("Selecciona el numero del archivo .pth: ")) - 1
            model_file = pth_files[choice]
        except (ValueError, IndexError):
            print("Seleccion invalida")
            return False
        
        # Buscar hash correspondiente
        base_name = model_file.replace('.pth', '')
        hash_file = base_name + '_hash.txt'
        
        if hash_file not in hash_files:
            print(f"No se encontro archivo hash correspondiente: {hash_file}")
            return False
    
    # Verificar
    return verify_downloaded_model(model_file, hash_file)

# EJEMPLO DE USO:
if __name__ == "__main__":
    print("Iniciando verificacion interactiva...")
    success = verify_model_interactive()
    
    if success:
        print("El modelo esta listo para usar!")
    else:
        print("El modelo necesita ser descargado nuevamente")
