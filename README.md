# Proxy-Server-and-Web-Server-Implementation-Using-Socket-Programming-with-QoS-Analysis
# 🌐 Proxy & Web Server with QoS Analysis (Socket Programming)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Networking](https://img.shields.io/badge/Topic-Socket%20Programming-orange)
![Status](https://img.shields.io/badge/Status-Completed-success)

> **Final Project Computer Networking:** Implementasi Web Server, Proxy Server dengan mekanisme Caching, dan Client Tester untuk analisis Quality of Service (QoS) menggunakan Python raw socket.

## 📌 Gambaran Umum

Proyek ini mendemonstrasikan komunikasi jaringan antar tiga entitas utama: **Client**, **Proxy Server**, dan **Web Server**. Sistem dibangun menggunakan pustaka standar `socket` dan `threading` di Python untuk menangani koneksi TCP (HTTP) dan UDP secara *consecutive* (paralel).

Selain komunikasi data dasar, proyek ini dilengkapi dengan modul pengujian **Quality of Service (QoS)** untuk mengukur performa jaringan berdasarkan parameter Throughput, Latency, Jitter, dan Packet Loss.

## 🏗️ Arsitektur Sistem

Alur komunikasi data dalam sistem ini adalah sebagai berikut:

```mermaid
graph LR
    A[Client / QoS Tester] -- Request --> B(Proxy Server)
    B -- Check Cache --> B
    B -- Cache Miss / UDP Forward --> C[Web Server]
    C -- Response --> B
    B -- Save Cache & Forward --> A
✨ Fitur Utama
1. Web Server (server.py)
Multi-threaded TCP/HTTP Server: Mampu melayani multiple request file HTML secara bersamaan.
UDP Echo Server: Menerima paket UDP dan mengirimkannya kembali (untuk pengujian Latency/RTT).
Directory Serving: Menyajikan file statis dari folder ./www.
2. Proxy Server (proxy.py)
HTTP Caching (In-Memory): Menyimpan respon HTTP untuk request yang sama guna mempercepat waktu respon dan mengurangi beban server.
Transparan Forwarding: Meneruskan paket TCP dan UDP dari Client ke Server jika data tidak ada di cache.
Concurrent Handling: Menggunakan threading untuk menangani banyak klien sekaligus.
3. Client & QoS Tester (client.py)
Mode Browser: Mengambil konten web via TCP.
QoS Analyzer (UDP): Mengirim burst packet untuk menghitung metrik jaringan.
Multi-Client Simulation: Mensimulasikan beban trafik dengan menjalankan multiple thread klien secara paralel.
📊 Analisis QoS (Quality of Service)
Modul Client melakukan perhitungan metrik jaringan secara real-time:

Metrik	Deskripsi	Implementasi
Throughput	Kecepatan transfer data efektif.	(Total Bytes * 8) / Total Time
Packet Loss	Persentase paket yang hilang.	(Lost Packets / Total Sent) * 100%
Latency (RTT)	Waktu putar-balik paket.	Selisih waktu kirim dan terima (ms).
Jitter	Variasi dalam delay paket.	Rata-rata selisih latensi antar paket berturut-turut.
📂 Struktur File
Plaintext
.
├── server.py       # Script Web Server (TCP & UDP)
├── proxy.py        # Script Proxy Server (Caching & Forwarding)
├── client.py       # Script Client & QoS Tester
├── qos_result.csv  # Log hasil pengujian QoS (Generated)
└── www/            # Folder konten web
    └── index.html  # File HTML sampel
🚀 Cara Menjalankan
Prasyarat
Python 3.x
(Opsional) Wireshark untuk validasi paket.
Langkah 1: Persiapan Konten
Buat folder www dan file index.html sederhana:

Bash
mkdir www
echo "<h1>Halo dari Web Server Socket!</h1>" > www/index.html
Langkah 2: Jalankan Web Server
Buka terminal baru dan jalankan:

Bash
python server.py
# Server berjalan di port 8000 (TCP) dan 9000 (UDP)
Langkah 3: Jalankan Proxy Server
Buka terminal baru. Penting: Pastikan konfigurasi IP di proxy.py (TARGET_WEB_SERVER_IP) sesuai dengan IP tempat server.py berjalan (default 127.0.0.1).

Bash
python proxy.py
# Proxy berjalan di port 8080 (TCP) dan 9090 (UDP)
Langkah 4: Jalankan Client / Tester
Buka terminal baru:

Bash
python client.py
Ikuti menu interaktif:
Pilih 1 untuk set IP Proxy (jika perlu).
Pilih 2 untuk tes Request HTTP (cek apakah Cache berfungsi).
Pilih 3 untuk pengujian QoS UDP.
Pilih 4 untuk simulasi Multi-Client.
👥 Kredit
Dibuat oleh Faisal Surya Saputra Mahasiswa Informatika - Telkom University
