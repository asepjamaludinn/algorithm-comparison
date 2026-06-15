import paho.mqtt.client as mqtt
import time
import csv
import pickle
import os
import ssl
import config
import crypto_utils
from cryptography.hazmat.primitives import serialization

class MQTTSubscriber:
    def __init__(self):
        self.private_keys = {}
        self.csv_file = None
        self.csv_writer = None
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Subscriber_Node")
        self.client.on_message = self.on_message
        self.client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)
        self.client.username_pw_set(config.USERNAME, config.PASSWORD)

    def load_shared_keys(self):
        print(f"[*] Menunggu Publisher membagikan file kunci ({config.SHARED_KEYS_FILE})...")
        while not os.path.exists(config.SHARED_KEYS_FILE):
            time.sleep(1)
        with open(config.SHARED_KEYS_FILE, "rb") as f:
            self.private_keys = pickle.load(f)

    def init_csv(self):
        self.csv_file = open(config.SUBSCRIBER_CSV, mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(["Algorithm", "Key_Size", "Transmission_Delay_sec", "Decrypt_Delay_sec"])

    def on_message(self, client, userdata, message):
        receive_time = time.time()
        raw_payload = message.payload
        
        try:
            parts = raw_payload.split(b'|', 3)
            algo = parts[0].decode('utf-8')
            key_size = int(parts[1].decode('utf-8'))
            send_time = float(parts[2].decode('utf-8'))
            ciphertext = parts[3]
            
            transmission_delay = receive_time - send_time
            raw_priv_key = self.private_keys[f"{algo}_{key_size}"]
            
            start_decrypt = time.perf_counter()
            if algo == "RSA":
                priv_key = serialization.load_pem_private_key(raw_priv_key, password=None)
                crypto_utils.decrypt_rsa(ciphertext, priv_key)
            else:
                priv_key = raw_priv_key
                crypto_utils.decrypt_elgamal(ciphertext, priv_key)
            end_decrypt = time.perf_counter()
            
            decrypt_delay = end_decrypt - start_decrypt
            self.csv_writer.writerow([algo, key_size, transmission_delay, decrypt_delay])
            print(f"[{algo} - {key_size} bit] Trans. Delay: {transmission_delay:.5f}s | Decrypt Delay: {decrypt_delay:.5f}s")
            
        except Exception as e:
            print(f"[!] Error memproses pesan: {e}")

    def run(self):
        self.load_shared_keys()
        self.init_csv()
        
        print(f"[*] Menghubungkan ke broker {config.BROKER_ADDRESS}...")
        self.client.connect(config.BROKER_ADDRESS, config.PORT)
        self.client.subscribe(config.MQTT_TOPIC)

        print("[*] Subscriber aktif. Menunggu pesan pengujian...")
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print(f"\n[*] Menutup Subscriber dan menyimpan data ke '{config.SUBSCRIBER_CSV}'.")
            self.csv_file.close()

if __name__ == "__main__":
    subscriber = MQTTSubscriber()
    subscriber.run()