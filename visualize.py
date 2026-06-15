import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. MEMBACA DATA MENTAH
# ==========================================
df_pub = pd.read_csv('publisher_computational_delay.csv')
df_sub = pd.read_csv('subscriber_eval_delay.csv')

# ==========================================
# 2. PENANGANAN PACKET LOSS & REKONSTRUKSI DATA
# ==========================================
sizes = [50, 100, 150, 200, 250]
assigned_sizes = []

for (algo, key), group in df_sub.groupby(['Algorithm', 'Key_Size'], sort=False):
    # Membagi baris yang selamat ke dalam 5 potongan (chunks)
    chunks = np.array_split(range(len(group)), 5)
    
    for i, chunk in enumerate(chunks):
        assigned_sizes.extend([sizes[i]] * len(chunk))

df_sub['Payload_Size'] = assigned_sizes

# ==========================================
# 3. PENGHITUNGAN RATA-RATA DARI SAMPEL
# ==========================================
avg_encrypt = df_pub.groupby(['Algorithm', 'Key_Size', 'Payload_Size'])['Encrypt_Delay_sec'].mean().reset_index()
avg_sub = df_sub.groupby(['Algorithm', 'Key_Size', 'Payload_Size'])[['Transmission_Delay_sec', 'Decrypt_Delay_sec']].mean().reset_index()

# Menggabungkan data Publisher (Enkripsi) dan Subscriber (Transmisi & Dekripsi)
df_final = pd.merge(avg_encrypt, avg_sub, on=['Algorithm', 'Key_Size', 'Payload_Size'])

# ==========================================
# 4. FUNGSI PEMBUATAN GRAFIK
# ==========================================
def create_line_chart(metric_col, title, ylabel, filename):
    plt.figure(figsize=(10, 6))
    
    colors = {'RSA': 'blue', 'ELGAMAL': 'red'}
    markers = {1024: 'o', 2048: 's', 3072: '^'}
    
    for algo in ['RSA', 'ELGAMAL']:
        for key in [1024, 2048, 3072]:
            subset = df_final[(df_final['Algorithm'] == algo) & (df_final['Key_Size'] == key)]
            if not subset.empty:
                label_name = f'{algo} ({key}-bit)'
                plt.plot(subset['Payload_Size'], subset[metric_col], 
                         marker=markers[key], color=colors[algo], 
                         linestyle='-', linewidth=2, markersize=8, label=label_name)
    
    plt.title(title, fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Ukuran Plaintext (Bytes)', fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.xticks([50, 100, 150, 200, 250])
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"[+] Grafik berhasil disimpan: {filename}")

# ==========================================
# 5. EKSEKUSI PEMBUATAN GRAFIK
# ==========================================
print("[*] Memulai proses visualisasi data...")

create_line_chart('Transmission_Delay_sec', 
                  'Pengaruh Ukuran Plaintext Terhadap Transmission Delay\n(RSA vs ElGamal)', 
                  'Waktu Transmisi (Detik)', 
                  'Grafik_1_Transmission_Delay.png')

create_line_chart('Encrypt_Delay_sec', 
                  'Pengaruh Ukuran Plaintext Terhadap Waktu Enkripsi\n(RSA vs ElGamal)', 
                  'Waktu Komputasi (Detik)', 
                  'Grafik_2_Encrypt_Delay.png')

create_line_chart('Decrypt_Delay_sec', 
                  'Pengaruh Ukuran Plaintext Terhadap Waktu Dekripsi\n(RSA vs ElGamal)', 
                  'Waktu Komputasi (Detik)', 
                  'Grafik_3_Decrypt_Delay.png')

print("[*] Selesai! Silakan cek folder Anda.")