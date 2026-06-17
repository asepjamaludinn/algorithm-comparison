# Performance Evaluation of Hybrid MQTT Protection: ECC vs ElGamal DH

Sebuah arsitektur pengujian performa keamanan (_Security Performance Benchmarking_) pada protokol komunikasi IoT (MQTT) yang membandingkan efisiensi algoritma pertukaran kunci (_Key Exchange_): **Elliptic Curve Cryptography (ECC)** dan **ElGamal Diffie-Hellman (Finite Field)**. Proyek ini merupakan pemenuhan evaluasi akhir mata kuliah Keamanan Komunikasi Data (Project-2: Case 6).

## Deskripsi Eksperimen

Karena Diffie-Hellman dirancang untuk pertukaran kunci dan bukan untuk mengenkripsi teks secara langsung, proyek ini mengimplementasikan skema **Kriptografi Hibrida**.

Sistem bekerja dengan alur berikut:

1. _Publisher_ dan _Subscriber_ melakukan pertukaran kunci publik menggunakan ECC atau ElGamal DH.
2. Kedua _node_ menyepakati kunci rahasia (_Shared Secret_).
3. _Shared Secret_ diturunkan menggunakan KDF (HKDF) menjadi kunci simetris murni.
4. Data _plaintext_ (berukuran 50 - 250 bytes) dienkripsi menggunakan algoritma simetris **AES-256-GCM** sebelum dikirim melalui broker publik **HiveMQ Cloud** (TLS Port 8883).

Sistem mengevaluasi dua metrik utama berdasarkan 3 level keamanan (_Key Size_) dari 100 sampel pengujian:

- **Computational Delay:** Waktu untuk fase _Key Exchange_ ditambah waktu enkripsi/dekripsi AES-GCM.
- **Transmission Delay:** Waktu tempuh _ciphertext_ melewati jaringan publik internet.

---

## Hasil Evaluasi

Berdasarkan ekstraksi data dari eksperimen pengiriman pesan, diperoleh ringkasan rata-rata performa sebagai berikut:

| Algoritma      | Level Keamanan | Komputasi Pub (s) | Komputasi Sub (s) | Total Komputasi (s) | Transmisi (s) | Jitter (s) |
| :------------- | :------------- | :---------------- | :---------------- | :------------------ | :------------ | :--------- |
| **ECC**        | Level_1        | 0.000216          | 0.000172          | 0.000388            | 0.320989      | 0.208695   |
| **ECC**        | Level_2        | 0.001124          | 0.000911          | 0.002035            | 0.295251      | 0.107994   |
| **ECC**        | Level_3        | 0.002086          | 0.002088          | 0.004174            | 0.340022      | 0.183650   |
| **ELGAMAL_DH** | Level_1        | 0.000464          | 0.000423          | 0.000887            | 4.756819      | 5.979816   |
| **ELGAMAL_DH** | Level_2        | 0.005635          | 0.005699          | 0.011334            | 0.498856      | 0.664226   |
| **ELGAMAL_DH** | Level_3        | 0.013284          | 0.011193          | 0.024477            | 0.369550      | 0.205692   |

## Visualisasi Data Eksperimen

Berikut adalah hasil ekstraksi data yang membandingkan performa kedua arsitektur:

**1. Pengaruh Ukuran Plaintext Terhadap Total Komputasi (ECC)** <br><img src="assets/Pengaruh_total%20komputasi%20ECC.png" width="800" alt="Komputasi ECC">

**2. Pengaruh Ukuran Plaintext Terhadap Total Komputasi (ElGamal DH)**
<br><img src="assets/Pengaruh_total%20komputasi%20Elgamal.png" width="800" alt="Komputasi ElGamal DH">

**3. Pengaruh Ukuran Plaintext Terhadap Transmission Delay (ECC)**
<br><img src="assets/Pengaruh_transmision%20delay%20ECC.png" width="800" alt="Transmisi ECC">

**4. Pengaruh Ukuran Plaintext Terhadap Transmission Delay (ElGamal DH)**
<br><img src="assets/Pengaruh_transmission%20delay%20Elgamal.png" width="800" alt="Transmisi ElGamal DH">

### Insight Utama (Key Findings)

1. **Superioritas Efisiensi Kurva Eliptik (ECC):** ECC terbukti jauh lebih optimal untuk _node_ sensor IoT. Pada level keamanan tertinggi (Level 3), komputasi ECC hanya memakan waktu ~0.004 detik, sementara operasi _Finite Field_ pada ElGamal DH membengkak secara eksponensial hingga ~0.024 detik.
2. **Kestabilan Kriptografi Hibrida:** Berdasarkan grafik komputasi, garis tren terlihat cenderung datar horizontal meskipun ukuran _plaintext_ bertambah dari 50 ke 250 bytes. Hal ini membuktikan bahwa beban komputasi terberat hanya terjadi pada fase awal (_Key Exchange_), sedangkan proses enkripsi data intinya menggunakan AES-GCM yang berkinerja sangat cepat.
3. **Interferensi Jaringan Publik (Jitter):** Evaluasi _Transmission Delay_ (terutama lonjakan ekstrem pada ElGamal Level 1) memvalidasi bahwa waktu transmisi pada arsitektur _Cloud MQTT_ sangat didominasi oleh fluktuasi latensi (_network congestion_) dan _overhead_ TLS, bukan oleh waktu komputasi kriptografinya itu sendiri.

## Struktur Repositori

- `config.py` : Konfigurasi terpusat (kredensial broker, ukuran _payload_, pemetaan _Key Level_).
- `crypto_utils.py` : Pustaka inti yang memuat logika _Hybrid Cryptography_ (ECC, ElGamal DH, HKDF, dan AES-GCM).
- `Publisher.py` & `Subscriber.py` : Skrip simulasi _node_ IoT terdistribusi yang menyimulasikan fase _Handshake_ dan pengiriman data.
- `EDA.ipynb` : _Jupyter Notebook_ untuk analisis statistik dan _rendering_ visualisasi grafik.
- `requirements.txt` : Daftar dependensi pustaka Python.

## Cara Menjalankan

**1. Persiapan Lingkungan**

```bash
pip install -r requirements.txt
```

2. Menjalankan Node Publisher (Terminal 1) - Tahap Pre-computation
   Jalankan Publisher terlebih dahulu. Skrip ini akan membangkitkan parameter matematika dan keypair untuk fase pertukaran kunci.

```bash
python Publisher.py
```

(Tunggu hingga muncul indikator FASE 2 bahwa "shared_keys.pkl" telah siap)

3. Menjalankan Node Subscriber (Terminal 2)
   Buka terminal baru dan jalankan Subscriber agar langsung terhubung dengan Broker dan merespons pesan Publisher.

```
python Subscriber.py
```
