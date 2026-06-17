import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display, Markdown

sns.set_theme(style="darkgrid", palette="deep")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 120

df_pub = pd.read_csv('publisher_computational_delay.csv')
df_sub = pd.read_csv('subscriber_eval_delay.csv')

sizes = [50, 100, 150, 200, 250]
assigned_sizes = []
for (algo, key), group in df_sub.groupby(['Algorithm', 'Key_Size'], sort=False):
    chunks = np.array_split(range(len(group)), 5)
    for i, chunk in enumerate(chunks):
        assigned_sizes.extend([sizes[i]] * len(chunk))

df_sub['Payload_Size'] = assigned_sizes
df_sub['Sample_Num'] = df_sub.groupby(['Algorithm', 'Key_Size', 'Payload_Size']).cumcount() + 1
df_pub_filtered = df_pub[df_pub['Sample_Num'].isin(df_sub['Sample_Num'])].copy()

df_merged = pd.merge(df_pub_filtered, df_sub, on=['Algorithm', 'Key_Size', 'Payload_Size', 'Sample_Num'])
df_merged['Total_Computational_Delay'] = df_merged['Encrypt_Delay_sec'] + df_merged['Decrypt_Delay_sec']

display(Markdown("**Status:** Preprocessing data selesai dan siap dianalisis."))
df_mean = df_merged.groupby(['Algorithm', 'Key_Size'])[['Encrypt_Delay_sec', 'Decrypt_Delay_sec', 'Total_Computational_Delay', 'Transmission_Delay_sec']].mean()
df_std = df_merged.groupby(['Algorithm', 'Key_Size'])[['Transmission_Delay_sec']].std()
df_summary = pd.concat([df_mean, df_std], axis=1).reset_index()
df_summary.columns = ['Algoritma', 'Level Keamanan', 'Komputasi Pub (s)', 'Komputasi Sub (s)', 'Total Komputasi (s)', 'Transmisi (s)', 'Jitter (s)']
display(df_summary)

df_ecc = df_merged[df_merged['Algorithm'] == 'ECC']
avg_comp_ecc = df_ecc.groupby(['Key_Size', 'Payload_Size'])['Total_Computational_Delay'].mean().reset_index()

plt.figure()
sns.lineplot(x="Payload_Size", y="Total_Computational_Delay", style="Key_Size", hue="Key_Size", markers=True, data=avg_comp_ecc, markersize=10, linewidth=2, palette="Blues_d")
plt.title("Pengaruh Ukuran Teks Terhadap Total Komputasi (ECC)\n(Fase Key Exchange + Enkripsi AES-GCM)", fontsize=14, fontweight='bold')
plt.xlabel("Ukuran Plaintext (Bytes)")
plt.ylabel("Waktu Komputasi (Detik)")
plt.xticks(sizes)
plt.legend(title="Level Keamanan", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
df_elgamal = df_merged[df_merged['Algorithm'] == 'ELGAMAL_DH']
avg_comp_elg = df_elgamal.groupby(['Key_Size', 'Payload_Size'])['Total_Computational_Delay'].mean().reset_index()

plt.figure()
sns.lineplot(x="Payload_Size", y="Total_Computational_Delay", style="Key_Size", hue="Key_Size", markers=True, data=avg_comp_elg, markersize=10, linewidth=2, palette="Oranges_d")
plt.title("Pengaruh Ukuran Teks Terhadap Total Komputasi (ElGamal DH)\n(Fase Key Exchange + Enkripsi AES-GCM)", fontsize=14, fontweight='bold')
plt.xlabel("Ukuran Plaintext (Bytes)")
plt.ylabel("Waktu Komputasi (Detik)")
plt.xticks(sizes)
plt.legend(title="Level Keamanan", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

avg_trans_ecc = df_ecc.groupby(['Key_Size', 'Payload_Size'])['Transmission_Delay_sec'].mean().reset_index()

plt.figure()
sns.lineplot(x="Payload_Size", y="Transmission_Delay_sec", style="Key_Size", hue="Key_Size", markers=True, data=avg_trans_ecc, markersize=10, linewidth=2, palette="Greens_d")
plt.title("Pengaruh Ukuran Teks Terhadap Transmission Delay (ECC)\n(Evaluasi Jaringan MQTT TLS)", fontsize=14, fontweight='bold')
plt.xlabel("Ukuran Plaintext (Bytes)")
plt.ylabel("Waktu Transmisi (Detik)")
plt.xticks(sizes)
plt.legend(title="Level Keamanan", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

avg_trans_elg = df_elgamal.groupby(['Key_Size', 'Payload_Size'])['Transmission_Delay_sec'].mean().reset_index()

plt.figure()
sns.lineplot(x="Payload_Size", y="Transmission_Delay_sec", style="Key_Size", hue="Key_Size", markers=True, data=avg_trans_elg, markersize=10, linewidth=2, palette="Reds_d")
plt.title("Pengaruh Ukuran Teks Terhadap Transmission Delay (ElGamal DH)\n(Evaluasi Jaringan MQTT TLS)", fontsize=14, fontweight='bold')
plt.xlabel("Ukuran Plaintext (Bytes)")
plt.ylabel("Waktu Transmisi (Detik)")
plt.xticks(sizes)
plt.legend(title="Level Keamanan", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()