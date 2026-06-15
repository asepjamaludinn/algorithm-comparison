from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from Crypto.Util.number import getPrime, inverse, bytes_to_long, long_to_bytes
import random

# RSA IMPLEMENTATION
def generate_rsa_keys(key_size):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    return private_key, private_key.public_key()

def encrypt_rsa(plaintext, public_key):
    key_size_bytes = public_key.key_size // 8
    chunk_size = key_size_bytes - 2 * hashes.SHA256().digest_size - 2 
    ciphertext = b""
    
    for i in range(0, len(plaintext), chunk_size):
        chunk = plaintext[i:i+chunk_size]
        ciphertext += public_key.encrypt(
            chunk,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
    return ciphertext

def decrypt_rsa(ciphertext, private_key):
    key_size_bytes = private_key.key_size // 8
    plaintext = b""
    
    for i in range(0, len(ciphertext), key_size_bytes):
        chunk = ciphertext[i:i+key_size_bytes]
        plaintext += private_key.decrypt(
            chunk,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
    return plaintext

# ELGAMAL IMPLEMENTATION 
def generate_elgamal_keys(key_size):
    p = getPrime(key_size)
    g = 2
    x = random.randint(1, p - 2)
    y = pow(g, x, p)
    return (p, g, x), (p, g, y)

def encrypt_elgamal(plaintext, public_key):
    p, g, y = public_key
    chunk_size = (p.bit_length() - 1) // 8
    ciphertext = b""
    kb = (p.bit_length() + 7) // 8
    
    for i in range(0, len(plaintext), chunk_size):
        chunk = plaintext[i:i+chunk_size]
        m = bytes_to_long(chunk)
        k = random.randint(1, p - 2)
        c1 = pow(g, k, p)
        c2 = (m * pow(y, k, p)) % p
        
    
        ciphertext += len(chunk).to_bytes(1, "big") 
        ciphertext += long_to_bytes(c1, kb)
        ciphertext += long_to_bytes(c2, kb)
        
    return ciphertext

def decrypt_elgamal(ciphertext, private_key):
    p, g, x = private_key
    kb = (p.bit_length() + 7) // 8
    block_size = 1 + (kb * 2) 
    plaintext = b""
    
    for i in range(0, len(ciphertext), block_size):
        block = ciphertext[i:i+block_size]
        
        original_chunk_len = block[0] 
        
        c1 = bytes_to_long(block[1:1+kb])
        c2 = bytes_to_long(block[1+kb:])
        
        s = pow(c1, x, p)
        m = (c2 * inverse(s, p)) % p
        
        plaintext += m.to_bytes(original_chunk_len, "big") 
        
    return plaintext