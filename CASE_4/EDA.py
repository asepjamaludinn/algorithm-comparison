import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display, Markdown

# 1. PENGATURAN ESTETIKA & INISIALISASI
sns.set_theme(style="darkgrid", palette="deep")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 120 # Resolusi presentasi

# 2. DATA PREPROCESSING & MERGING
display(Markdown("### ⏳ 1. Memuat dan Memproses Data..."))
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

# Feature Engineering
df_merged['Total_Computational_Delay'] = df_merged['Encrypt_Delay_sec'] + df_merged['Decrypt_Delay_sec']
df_merged['Total_System_Delay'] = df_merged['Total_Computational_Delay'] + df_merged['Transmission_Delay_sec']

display(Markdown(f"**✅ Penggabungan selesai. Total sampel utuh: {len(df_merged)} baris.**\n"))

# 3. TABEL RINGKASAN STATISTIK
display(Markdown("---"))
display(Markdown("### 📊 2. Tabel Statistik Kinerja Sistem (Rata-rata & Jitter)"))

df_mean = df_merged.groupby(['Algorithm', 'Key_Size'])[['Encrypt_Delay_sec', 'Decrypt_Delay_sec', 'Total_Computational_Delay', 'Transmission_Delay_sec']].mean()
df_std = df_merged.groupby(['Algorithm', 'Key_Size'])[['Transmission_Delay_sec']].std()

df_summary = pd.concat([df_mean, df_std], axis=1).reset_index()
df_summary.columns = ['Algoritma', 'Ukuran Kunci', 'Rata-rata Enkripsi (s)', 'Rata-rata Dekripsi (s)', 'Total Komputasi (s)', 'Rata-rata Transmisi (s)', 'Jitter Transmisi (s)']

display(df_summary)

# 4. VISUALISASI 1: DISTRIBUSI TRANSMISI (VIOLIN PLOT)
display(Markdown("---"))
display(Markdown("### 📈 3. Analisis Distribusi Transmission Delay (Deteksi Outlier Jaringan)"))

plt.figure()
sns.violinplot(x="Key_Size", y="Transmission_Delay_sec", hue="Algorithm", data=df_merged, split=True, inner="quart", linewidth=1.5)
plt.title("Distribusi Transmission Delay (RSA vs ElGamal)\nMenganalisis Jitter pada Jaringan MQTT Publik", fontsize=14, fontweight='bold')
plt.xlabel("Ukuran Kunci (Bits)", fontsize=12)
plt.ylabel("Transmission Delay (Detik)", fontsize=12)
plt.legend(title="Algoritma", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# 5. VISUALISASI 2: SYSTEM BOTTLENECK (HEATMAP)
display(Markdown("---"))
display(Markdown("### 🌡️ 4. Heatmap Proporsi Beban Sistem"))

heatmap_data = df_merged.groupby(['Algorithm', 'Key_Size'])[['Encrypt_Delay_sec', 'Transmission_Delay_sec', 'Decrypt_Delay_sec']].mean()
heatmap_pct = heatmap_data.div(heatmap_data.sum(axis=1), axis=0) * 100
heatmap_pct.index = heatmap_pct.index.map(lambda x: f"{x[0]} ({x[1]}-bit)")

plt.figure()
sns.heatmap(heatmap_pct, annot=True, fmt=".1f", cmap="YlOrRd", cbar_kws={'label': 'Kontribusi Terhadap Total Delay (%)'})
plt.title("System Bottleneck Analysis: Rasio Beban Komputasi vs Jaringan", fontsize=14, fontweight='bold')
plt.ylabel("Skenario", fontsize=12)
plt.xlabel("Fase Pemrosesan", fontsize=12)
plt.tight_layout()
plt.show()

# 6. VISUALISASI 3: COMPUTATIONAL DELAY VS PAYLOAD SIZE
display(Markdown("---"))
display(Markdown("### 📉 5. Pengaruh Ukuran Plaintext Terhadap Total Computational Delay"))

avg_comp = df_merged.groupby(['Algorithm', 'Key_Size', 'Payload_Size'])['Total_Computational_Delay'].mean().reset_index()

plt.figure()
sns.lineplot(x="Payload_Size", y="Total_Computational_Delay", hue="Algorithm", style="Key_Size", markers=True, dashes=False, data=avg_comp, markersize=10, linewidth=2)
plt.title("Pengaruh Ukuran Plaintext Terhadap Total Computational Delay\n(Enkripsi + Dekripsi)", fontsize=14, fontweight='bold')
plt.xlabel("Ukuran Plaintext (Bytes)", fontsize=12)
plt.ylabel("Waktu Komputasi (Detik)", fontsize=12)
plt.xticks(sizes)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

# 7. VISUALISASI 4: TRANSMISSION DELAY VS PAYLOAD SIZE
display(Markdown("---"))
display(Markdown("### 📡 6. Pengaruh Ukuran Plaintext Terhadap Transmission Delay"))

avg_trans = df_merged.groupby(['Algorithm', 'Key_Size', 'Payload_Size'])['Transmission_Delay_sec'].mean().reset_index()

plt.figure()
sns.lineplot(x="Payload_Size", y="Transmission_Delay_sec", hue="Algorithm", style="Key_Size", markers=True, dashes=False, data=avg_trans, markersize=10, linewidth=2)
plt.title("Pengaruh Ukuran Plaintext Terhadap Transmission Delay\n(Mengukur Dampak Ciphertext Expansion di Jaringan Publik)", fontsize=14, fontweight='bold')
plt.xlabel("Ukuran Plaintext (Bytes)", fontsize=12)
plt.ylabel("Waktu Transmisi (Detik)", fontsize=12)
plt.xticks(sizes)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()