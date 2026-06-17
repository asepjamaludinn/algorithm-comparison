import paho.mqtt.client as mqtt
import time
import csv
import pickle
import os
import ssl
import config
import crypto_utils
import random

class MQTTSubscriber:
    def __init__(self):
        self.my_private_keys = {}
        self.publisher_public_keys = {}
        self.csv_file = None
        self.csv_writer = None
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, f"Subscriber_Node_Case6_{random.randint(1000,9999)}")
        self.client.on_message = self.on_message
        self.client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)
        self.client.username_pw_set(config.USERNAME, config.PASSWORD)

    def load_shared_keys(self):
        print(f"[*] Menunggu Publisher membagikan file kunci ({config.SHARED_KEYS_FILE})...")
        while not os.path.exists(config.SHARED_KEYS_FILE):
            time.sleep(1)
        with open(config.SHARED_KEYS_FILE, "rb") as f:
            data = pickle.load(f)
            for k, v in data['sub_priv'].items():
                self.my_private_keys[k] = crypto_utils.deserialize_private(v)
            for k, v in data['pub_pub'].items():
                self.publisher_public_keys[k] = crypto_utils.deserialize_public(v)

    def on_message(self, client, userdata, message):
        receive_time = time.time()
        try:
            parts = message.payload.split(b'|', 3)
            algo = parts[0].decode('utf-8')
            level = parts[1].decode('utf-8')
            send_time = float(parts[2].decode('utf-8'))
            ciphertext = parts[3]
            
            transmission_delay = receive_time - send_time
            
            start_decrypt = time.perf_counter()
           
            shared_secret = crypto_utils.compute_shared_secret(algo, self.my_private_keys[f"{algo}_{level}"], self.publisher_public_keys[f"{algo}_{level}"])
          
            aes_key = crypto_utils.derive_symmetric_key(shared_secret)
          
            plaintext = crypto_utils.decrypt_payload(aes_key, ciphertext)
            end_decrypt = time.perf_counter()
            
            decrypt_delay = end_decrypt - start_decrypt
            self.csv_writer.writerow([algo, level, transmission_delay, decrypt_delay])
            print(f"[{algo} - {level}] Trans: {transmission_delay:.4f}s | Decrypt: {decrypt_delay:.4f}s")
            
        except Exception as e:
            print(f"[!] Error: {e}")

    def run(self):
        self.load_shared_keys()
        self.csv_file = open(config.SUBSCRIBER_CSV, mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(["Algorithm", "Key_Size", "Transmission_Delay_sec", "Decrypt_Delay_sec"])
        
        print(f"[*] Terhubung ke {config.BROKER_ADDRESS}...")
        self.client.connect(config.BROKER_ADDRESS, config.PORT)
        self.client.subscribe(config.MQTT_TOPIC)

        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            self.csv_file.close()

if __name__ == "__main__":
    MQTTSubscriber().run()