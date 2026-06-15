import paho.mqtt.client as mqtt
import time
import string
import random
import csv
import pickle
import ssl
import config
import crypto_utils
from cryptography.hazmat.primitives import serialization

class MQTTPublisher:
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Publisher_Node")
        self.client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)
        self.client.username_pw_set(config.USERNAME, config.PASSWORD)
        self.private_keys_store = {}
        self.public_keys_store = {} # Menyimpan public key di memori untuk Fase 2

    def connect(self):
        print(f"\n[*] Menghubungkan ke broker {config.BROKER_ADDRESS}...")
        self.client.connect(config.BROKER_ADDRESS, config.PORT)
        self.client.loop_start()

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    def generate_payload(self, size_in_bytes):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=size_in_bytes)).encode('utf-8')

    def share_keys(self):
        with open(config.SHARED_KEYS_FILE, "wb") as f:
            pickle.dump(self.private_keys_store, f)

    def run_experiment(self):
        # ====================================================================
        # FASE 1: PEMBANGKITAN SELURUH KUNCI (PRE-COMPUTATION)
        # ====================================================================
        print("[*] FASE 1: Membangkitkan seluruh kunci kriptografi...")
        for algo in config.ALGORITHMS:
            for key_size in config.KEY_SIZES:
                print(f"    -> Membuat kunci {algo} {key_size}-bit (Mohon tunggu)...")
                
                if algo == "RSA":
                    priv_key, pub_key = crypto_utils.generate_rsa_keys(key_size)
                    pem_priv = priv_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.TraditionalOpenSSL,
                        encryption_algorithm=serialization.NoEncryption()
                    )
                    self.private_keys_store[f"{algo}_{key_size}"] = pem_priv
                else:
                    priv_key, pub_key = crypto_utils.generate_elgamal_keys(key_size)
                    self.private_keys_store[f"{algo}_{key_size}"] = priv_key
                
                # Simpan public key di RAM untuk enkripsi nanti
                self.public_keys_store[f"{algo}_{key_size}"] = pub_key

        self.share_keys()
        print("[*] File shared_keys.pkl berhasil diperbarui dengan seluruh kunci!")

        # ====================================================================
        # FASE 2: EKSEKUSI PENGIRIMAN PESAN
        # ====================================================================
        print("\n[*] FASE 2: Memulai pengujian dan pengiriman pesan...")
        self.connect()

        with open(config.PUBLISHER_CSV, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Algorithm", "Key_Size", "Payload_Size", "Sample_Num", "Encrypt_Delay_sec"])

            for algo in config.ALGORITHMS:
                for key_size in config.KEY_SIZES:
                    print(f"\n[+] Mengeksekusi pengiriman untuk {algo} {key_size}-bit...")
                    
                    # Ambil public key dari memori yang sudah dibuat di Fase 1
                    pub_key = self.public_keys_store[f"{algo}_{key_size}"]
                    
                    for size in config.PAYLOAD_SIZES:
                        print(f"    -> Mengirim {config.NUM_SAMPLES} sampel ({size} bytes)...")
                        
                        for i in range(config.NUM_SAMPLES):
                            plaintext = self.generate_payload(size)
                            
                            start_encrypt = time.perf_counter()
                            if algo == "RSA":
                                ciphertext = crypto_utils.encrypt_rsa(plaintext, pub_key)
                            else:
                                ciphertext = crypto_utils.encrypt_elgamal(plaintext, pub_key)
                            end_encrypt = time.perf_counter()
                            
                            encrypt_delay = end_encrypt - start_encrypt
                            writer.writerow([algo, key_size, size, i+1, encrypt_delay])
                            
                            send_time = time.time()
                            header = f"{algo}|{key_size}|{send_time}|".encode('utf-8')
                            payload_to_send = header + ciphertext
                            
                            self.client.publish(config.MQTT_TOPIC, payload_to_send)
                            time.sleep(0.5) 

        self.disconnect()
        print(f"\n[*] Seluruh pengujian selesai. Data tersimpan di '{config.PUBLISHER_CSV}'")

if __name__ == "__main__":
    publisher = MQTTPublisher()
    publisher.run_experiment()