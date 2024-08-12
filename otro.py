import hmac
import hashlib
from itertools import product

def compute_hmac(key, data, hash_algo='sha256'):
    """Calcula el HMAC de los datos usando la clave y el algoritmo especificado."""
    return hmac.new(key, data, getattr(hashlib, hash_algo)).hexdigest()

def find_valid_key(partial_key, target_hmac, file_path, hash_algo='sha256'):
    """Encuentra la clave que produce el HMAC deseado para el archivo dado."""
    partial_key_bytes = bytes.fromhex(partial_key)
    file_data = open("C:/Users/mimoc/Downloads/original_list.pdf", 'rb').read()
    
    # Probar todas las combinaciones posibles para los bytes faltantes
    for missing_bytes in product(range(256), repeat=16):  # Cambiar 16 si conoces el tamaño exacto
        key = partial_key_bytes + bytes(missing_bytes)
        if compute_hmac(key, file_data, hash_algo) == target_hmac:
            return key.hex()
    return None

# Variables
partial_key = '4db29249ac44fe6ac69a7b1deecf18e85605bd021a2f4951c23b1ce6df'
target_hmac = 'e429cd6050a055e41e39f0407933630f26ab17288bb0ade7e2b2fced54d3ae4f'
file_path = 'original_list.pdf'

# Encontrar clave válida
valid_key = find_valid_key(partial_key, target_hmac, file_path)
if valid_key:
    print(f'Clave válida encontrada: {valid_key}')
else:
    print('No se encontró ninguna clave válida.')
