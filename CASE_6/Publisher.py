import paho.mqtt.client as mqtt
import time
import string
import random
import csv
import pickle
import ssl
import config
import crypto_utils

class MQTTPublisher:
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, f"Publisher_Node_Case6_{random.randint(1000,9999)}")
        self.client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)
        self.client.username_pw_set(config.USERNAME, config.PASSWORD)
        self.my_private_keys = {}
        self.subscriber_public_keys = {}

    def connect(self):
        print(f"\n[*] Menghubungkan ke broker {config.BROKER_ADDRESS}...")
        self.client.connect(config.BROKER_ADDRESS, config.PORT)
        self.client.loop_start()

    def generate_payload(self, size):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=size)).encode('utf-8')

    def run_experiment(self):
        print("[*] FASE 1: Simulasi Pertukaran Kunci DH (Pre-computation)...")
        shared_file_data = {'sub_priv': {}, 'pub_pub': {}}

        for algo in config.ALGORITHMS:
            for level in config.KEY_LEVELS:
                print(f"    -> Membangkitkan {algo} {level} untuk Publisher & Subscriber...")
                pub_priv, pub_pub = crypto_utils.generate_keypair(algo, level)
                sub_priv, sub_pub = crypto_utils.generate_keypair(algo, level)

                self.my_private_keys[f"{algo}_{level}"] = pub_priv
                self.subscriber_public_keys[f"{algo}_{level}"] = sub_pub

                shared_file_data['sub_priv'][f"{algo}_{level}"] = crypto_utils.serialize_private(sub_priv)
                shared_file_data['pub_pub'][f"{algo}_{level}"] = crypto_utils.serialize_public(pub_pub)

        with open(config.SHARED_KEYS_FILE, "wb") as f:
            pickle.dump(shared_file_data, f)
        print("[*] File shared_keys.pkl siap digunakan oleh Subscriber!")

        print("\n[*] FASE 2: Memulai pengujian dan pengiriman pesan hybrid...")
        self.connect()

        with open(config.PUBLISHER_CSV, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Algorithm", "Key_Size", "Payload_Size", "Sample_Num", "Encrypt_Delay_sec"])

            for algo in config.ALGORITHMS:
                for level in config.KEY_LEVELS:
                    print(f"\n[+] Eksekusi {algo} {level}...")
                    my_priv = self.my_private_keys[f"{algo}_{level}"]
                    peer_pub = self.subscriber_public_keys[f"{algo}_{level}"]

                    for size in config.PAYLOAD_SIZES:
                        print(f"    -> Mengirim {config.NUM_SAMPLES} sampel ({size} bytes)...")
                        for i in range(config.NUM_SAMPLES):
                            plaintext = self.generate_payload(size)

                            start_encrypt = time.perf_counter()
                           
                            shared_secret = crypto_utils.compute_shared_secret(algo, my_priv, peer_pub)
                        
                            aes_key = crypto_utils.derive_symmetric_key(shared_secret)
                         
                            ciphertext = crypto_utils.encrypt_payload(aes_key, plaintext)
                            end_encrypt = time.perf_counter()

                            encrypt_delay = end_encrypt - start_encrypt
                            writer.writerow([algo, level, size, i+1, encrypt_delay])

                            send_time = time.time()
                            header = f"{algo}|{level}|{send_time}|".encode('utf-8')
                            self.client.publish(config.MQTT_TOPIC, header + ciphertext)
                            time.sleep(0.5) 

        self.client.loop_stop()
        self.client.disconnect()
        print(f"\n[*] Selesai. Data tersimpan di '{config.PUBLISHER_CSV}'")

if __name__ == "__main__":
    MQTTPublisher().run_experiment()