# 🌐 Proxy & Web Server Implementation with QoS Analysis

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Networking](https://img.shields.io/badge/Socket-Programming-orange)
![Status](https://img.shields.io/badge/Status-Final%20Project-success)

> **Computer Networking Final Project:** Implementasi Web Server dan Proxy Server menggunakan Python Socket Programming yang dilengkapi dengan mekanisme *Caching*, *Multi-threading*, serta modul analisis *Quality of Service* (QoS).

## 📌 Deskripsi Proyek
Proyek ini membangun simulasi jaringan sederhana yang terdiri dari **Client**, **Proxy Server**, dan **Web Server**. Tujuan utamanya adalah mendemonstrasikan bagaimana protokol TCP (untuk HTTP) dan UDP bekerja di level socket, serta bagaimana Proxy menangani *request forwarding* dan *caching* untuk efisiensi jaringan.

Selain itu, sistem ini memiliki fitur **QoS Analyzer** untuk mengukur kualitas jaringan berdasarkan parameter:
* **Throughput** (Kecepatan transfer data)
* **Latency / RTT** (Waktu tunda)
* **Jitter** (Variasi kedatangan paket)
* **Packet Loss** (Persentase paket hilang)

## 🏗️ Arsitektur Sistem

Alur komunikasi data antar komponen adalah sebagai berikut:

```mermaid
graph LR
    User[Client / QoS Tester] -- Request (TCP/UDP) --> Proxy[Proxy Server]
    Proxy -- Check Cache (TCP Only) --> Proxy
    Proxy -- Cache Miss / Forward --> Web[Web Server]
    Web -- Response --> Proxy
    Proxy -- Save to Cache --> Proxy
    Proxy -- Response --> User
