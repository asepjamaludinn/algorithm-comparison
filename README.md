# Performance Evaluation of MQTT Protection: RSA vs ElGamal

Sebuah arsitektur pengujian performa keamanan (Security Performance Benchmarking) pada protokol komunikasi IoT (MQTT) yang membandingkan efisiensi algoritma kriptografi asimetris **RSA** dan **ElGamal**.

## Deskripsi Eksperimen

Proyek ini mengimplementasikan perlindungan data secara _End-to-End Encryption_ (E2EE) menggunakan RSA dan ElGamal yang dikirimkan melalui broker publik **HiveMQ Cloud** dengan proteksi lapisan transport (TLS Port 8883).

Sistem secara otomatis mengevaluasi dua metrik utama berdasarkan variasi ukuran kunci (1024, 2048, 3072 bit) dan ukuran _plaintext_ (50 hingga 250 bytes) dengan mengambil rata-rata dari 100 sampel pengujian:

1. **Computational Delay:** Waktu yang dihabiskan _node_ untuk melakukan proses enkripsi (sisi Publisher) dan dekripsi (sisi Subscriber).
2. **Transmission Delay:** Waktu tempuh _ciphertext_ dari titik pengiriman hingga diterima oleh _Subscriber_ melewati jaringan publik internet.

## Struktur Repositori

- `config.py` : File konfigurasi terpusat (kredensial broker, ukuran _payload_, parameter eksperimen).
- `crypto_utils.py` : Pustaka inti (_core library_) yang menangani logika enkripsi/dekripsi RSA dengan padding OAEP dan implementasi ElGamal dengan _Dynamic Padding_.
- `Publisher.py` : Skrip _node_ pengirim yang bertugas membangkitkan kunci (_Pre-computation Phase_), mengenkripsi, dan mengirim pesan.
- `Subscriber.py` : Skrip _node_ penerima yang memantau topik MQTT, mendekripsi pesan masuk, dan mencatat latensi jaringan.
- `EDA.py` : untuk melakukan _Exploratory Data Analysis_ (EDA) dan menghasilkan grafik visualisasi hasil pengujian menggunakan Pandas dan Seaborn.
- `requirements.txt` : Daftar dependensi pustaka Python yang dibutuhkan.

## Cara Menjalankan (_How to Run_)

**1. Persiapan Lingkungan (_Environment Setup_)**
Pastikan Python 3.x telah terinstal di sistem Anda. Instal seluruh pustaka yang dibutuhkan menggunakan perintah berikut:

```bash
pip install -r requirements.txt
```
