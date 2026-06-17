from cryptography.hazmat.primitives.asymmetric import ec, dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization
import os

# Memetakan level keamanan setara
ecc_curves = {
    "Level_1": ec.SECP256R1(),
    "Level_2": ec.SECP384R1(),
    "Level_3": ec.SECP521R1(),
}

dh_key_sizes = {
    "Level_1": 1024,
    "Level_2": 2048,
    "Level_3": 3072,
}

# Menyimpan parameter DH di memori agar tidak perlu dihitung berulang kali
_dh_parameters = {}

def get_dh_parameters(level):
    if level not in _dh_parameters:
        print(f"   [!] Membangkitkan parameter DH {dh_key_sizes[level]}-bit (Bisa memakan waktu beberapa menit)...")
        _dh_parameters[level] = dh.generate_parameters(generator=2, key_size=dh_key_sizes[level])
    return _dh_parameters[level]

def generate_keypair(algo, level):
    if algo == "ECC":
        priv_key = ec.generate_private_key(ecc_curves[level])
        pub_key = priv_key.public_key()
    else:
        params = get_dh_parameters(level)
        priv_key = params.generate_private_key()
        pub_key = priv_key.public_key()
    return priv_key, pub_key

def compute_shared_secret(algo, my_priv_key, peer_pub_key):
    if algo == "ECC":
        return my_priv_key.exchange(ec.ECDH(), peer_pub_key)
    else:
        return my_priv_key.exchange(peer_pub_key)

def derive_symmetric_key(shared_secret):
    # Menggunakan HKDF untuk mengubah Shared Secret menjadi kunci AES 256-bit murni
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b'mqtt_case6_exchange').derive(shared_secret)

def encrypt_payload(symmetric_key, plaintext):
    aesgcm = AESGCM(symmetric_key)
    nonce = os.urandom(12) # GCM membutuhkan 12 bytes nonce unik
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return nonce + ciphertext

def decrypt_payload(symmetric_key, payload):
    nonce = payload[:12]
    ciphertext = payload[12:]
    aesgcm = AESGCM(symmetric_key)
    return aesgcm.decrypt(nonce, ciphertext, None)

# --- FUNGSI SERIALISASI UNTUK PICKLE ---
def serialize_private(priv_key):
    return priv_key.private_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()
    )

def serialize_public(pub_key):
    return pub_key.public_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def deserialize_private(pem_data):
    return serialization.load_pem_private_key(pem_data, password=None)

def deserialize_public(pem_data):
    return serialization.load_pem_public_key(pem_data)