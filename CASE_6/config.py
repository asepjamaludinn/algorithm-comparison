
ALGORITHMS    = ["ECC", "ELGAMAL_DH"]
# Level_1: ECC-256R1 / DH-1024
# Level_2: ECC-384R1 / DH-2048
# Level_3: ECC-521R1 / DH-3072
KEY_LEVELS    = ["Level_1", "Level_2", "Level_3"] 
PAYLOAD_SIZES = [50, 100, 150, 200, 250]
NUM_SAMPLES   = 100
MQTT_TOPIC    = "project2/case6"

BROKER_ADDRESS = "4764d0cbcff340b6baaca73bade03783.s1.eu.hivemq.cloud"
PORT           = 8883
USERNAME       = "case6"  
PASSWORD       = "KeamananKomunikasiData1"  

# File Paths
SHARED_KEYS_FILE = "shared_keys.pkl"
PUBLISHER_CSV    = "publisher_computational_delay.csv"
SUBSCRIBER_CSV   = "subscriber_eval_delay.csv"