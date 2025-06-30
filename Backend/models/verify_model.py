# SCRIPT DE VERIFICACION - Usar en tu maquina local
import hashlib
import os

def verify_downloaded_model(model_path, hash_file_path):
    """Verifica un modelo descargado usando el archivo hash"""
    
    print("VERIFYING LOADED MODEL")
    print("=" * 40)
    
    try:
        # Verificar que ambos archivos existen
        if not os.path.exists(model_path):
            print(f"ERROR: Model's file not found: {model_path}")
            return False
            
        if not os.path.exists(hash_file_path):
            print(f"ERROR: Hash file not found: {hash_file_path}")
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
            print("ERROR: Couldn't find MD5 file")
            return False
        
        print(f"Verifying file: {model_path}")
        print(f"Using hash: {hash_file_path}")
        print(f"Expected Hash: {original_hash}")
        
        # Calcular hash del archivo descargado
        print("Calculating the model's hash...")
        with open(model_path, 'rb') as f:
            downloaded_hash = hashlib.md5(f.read()).hexdigest()
        
        print(f"Calculated hash: {downloaded_hash}")
        
        # Comparar
        if original_hash == downloaded_hash:
            print("SUCCESS: SUCCESSFULL DOWNLOAD")
            return True
        else:
            print("ERROR: UNSUCCESSFULL VERIFICATION - file may be corrupted")
            print(f"   Original hash:    {original_hash}")
            print(f"   Downloaded hash:  {downloaded_hash}")
            return False
            
    except Exception as e:
        print(f"ERROR verifying file: {e}")
        return False

def verify_model_interactive():
    """Version interactiva para usar desde la consola"""
    
    print("MODEL VERIFYER")
    print("=" * 50)
    
    # Buscar archivos automaticamente
    current_dir = os.getcwd()
    pth_files = [f for f in os.listdir('.') if f.endswith('.pth')]
    hash_files = [f for f in os.listdir('.') if f.endswith('_hash.txt')]
    
    print(f"Present folder: {current_dir}")
    print(f".pth files found: {pth_files}")
    print(f"*_hash.txt files found: {hash_files}")
    
    if not pth_files:
        print("Couldn't find .pth files in the current directory")
        return False
    
    if not hash_files:
        print("Courldn't find _hash.txt in the current directory")
        return False
    
    # Si hay un solo par, usarlos automaticamente
    if len(pth_files) == 1 and len(hash_files) == 1:
        model_file = pth_files[0]
        hash_file = hash_files[0]
        print(f"Using: {model_file} and {hash_file}")
    else:
        # Permitir seleccion manual
        print("Multiple files found. Select:")
        for i, f in enumerate(pth_files):
            print(f"  {i+1}. {f}")
        
        try:
            choice = int(input("Select the .pth number file: ")) - 1
            model_file = pth_files[choice]
        except (ValueError, IndexError):
            print("Invalid selection")
            return False
        
        # Buscar hash correspondiente
        base_name = model_file.replace('.pth', '')
        hash_file = base_name + '_hash.txt'
        
        if hash_file not in hash_files:
            print(f"Couldn't find a corresponding hash file: {hash_file}")
            return False
    
    # Verificar
    return verify_downloaded_model(model_file, hash_file)

# EJEMPLO DE USO:
if __name__ == "__main__":
    print("\nInitiating verification...")
    success = verify_model_interactive()
    
    if success:
        print("Model is ready to use!n")
    else:
        print("Model needs to be downloaded again\n")
