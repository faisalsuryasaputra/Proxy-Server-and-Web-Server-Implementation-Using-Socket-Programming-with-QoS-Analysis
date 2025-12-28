import socket
import time
import threading
import statistics

# --- KONFIGURASI DEFAULT ---
TARGET_IP = '127.0.0.1' # Bisa IP Proxy atau IP Web Server langsung
TARGET_HTTP_PORT = 8080 # Port TCP (Proxy)
TARGET_UDP_PORT = 9090  # Port UDP (Proxy)

BUFFER_SIZE = 4096

def print_menu():
    print("\n--- CLIENT & QoS TESTER ---")
    print(f"Target Saat Ini: {TARGET_IP} (TCP:{TARGET_HTTP_PORT}, UDP:{TARGET_UDP_PORT})")
    print("1. Set IP/Port Target")
    print("2. Request HTTP (TCP)")
    print("3. Uji QoS UDP (Latency, Jitter, Packet Loss)")
    print("4. Simulasi Multi-Client (5 Paralel)")
    print("5. Mode Browser (Info)")
    print("0. Keluar")

def set_target():
    global TARGET_IP, TARGET_HTTP_PORT, TARGET_UDP_PORT
    TARGET_IP = input("Masukkan IP Target (Proxy/Server): ")
    TARGET_HTTP_PORT = int(input("Masukkan Port TCP (default 8080/8000): "))
    TARGET_UDP_PORT = int(input("Masukkan Port UDP (default 9090/9000): "))

# --- MODE 1: TCP HTTP Request ---
def tcp_request(show_output=True):
    try:
        start_time = time.time()
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5)
        client.connect((TARGET_IP, TARGET_HTTP_PORT))
        
        request = "GET /index.html HTTP/1.1\r\nHost: {}\r\n\r\n".format(TARGET_IP)
        client.send(request.encode())
        
        response = b""
        while True:
            chunk = client.recv(BUFFER_SIZE)
            if not chunk: break
            response += chunk
            
        duration = time.time() - start_time
        client.close()
        
        if show_output:
            print(f"\n[TCP] Response diterima ({len(response)} bytes) dalam {duration:.4f}s")
            print("-" * 20)
            print(response.decode('utf-8', errors='ignore')[:500]) # Print 500 chars pertama
            print("-" * 20)
        
        return len(response), duration
    except Exception as e:
        if show_output: print(f"[!] TCP Error: {e}")
        return 0, 0

# --- MODE 2: UDP QoS Test ---
def udp_qos_test(packet_count=20, packet_size=128, interval=0.1):
    print(f"\n[Mulai Uji QoS] Kirim {packet_count} paket, size {packet_size} bytes...")
    
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(2) # Timeout tunggu echo
    
    latencies = []
    lost_packets = 0
    bytes_received = 0
    
    start_test_time = time.time()
    
    for i in range(packet_count):
        msg = f"PKT-{i}".ljust(packet_size).encode() # Padding payload
        send_time = time.time()
        
        try:
            client.sendto(msg, (TARGET_IP, TARGET_UDP_PORT))
            data, _ = client.recvfrom(BUFFER_SIZE)
            recv_time = time.time()
            
            rtt = (recv_time - send_time) * 1000 # miliseconds
            latencies.append(rtt)
            bytes_received += len(data)
            print(f"Packet {i}: Reply received, RTT={rtt:.2f}ms")
            
        except socket.timeout:
            print(f"Packet {i}: Lost/Timeout")
            lost_packets += 1
        except Exception as e:
            print(f"Packet {i}: Error {e}")
            lost_packets += 1
            
        time.sleep(interval)
        
    total_time = time.time() - start_test_time
    
    # --- HITUNG QOS ---
    # 1. Throughput (bps) = (Total Data / Total Waktu) * 8
    throughput = (bytes_received * 8) / total_time if total_time > 0 else 0
    
    # 2. Packet Loss (%)
    loss_percent = (lost_packets / packet_count) * 100
    
    # 3. Average Latency
    avg_latency = statistics.mean(latencies) if latencies else 0
    
    # 4. Jitter (Variasi delay) = Rata-rata selisih latensi berturut-turut
    jitter = 0
    if len(latencies) > 1:
        diffs = [abs(latencies[i] - latencies[i-1]) for i in range(1, len(latencies))]
        jitter = statistics.mean(diffs)
        
    print("\n=== HASIL ANALISIS QoS ===")
    print(f"Total Packets : {packet_count}")
    print(f"Received      : {packet_count - lost_packets}")
    print(f"Lost          : {lost_packets} ({loss_percent:.2f}%)")
    print(f"Throughput    : {throughput:.2f} bps")
    print(f"Avg Latency   : {avg_latency:.2f} ms")
    print(f"Jitter        : {jitter:.2f} ms")
    print("==========================")
    
    # Simpan ke CSV
    with open("qos_result.csv", "a") as f:
        f.write(f"{datetime.now()},{packet_count},{loss_percent},{throughput},{avg_latency},{jitter}\n")
    print("[Info] Hasil disimpan ke qos_result.csv")
    client.close()

# --- MODE 3: Multi-Client ---
def multi_client_simulation():
    print("\n[Multi-Client] Menjalankan 5 client paralel...")
    threads = []
    results = []
    
    def run_single_client(cid):
        size, duration = tcp_request(show_output=False)
        if size > 0:
            print(f"Client-{cid}: Sukses ({size} bytes, {duration:.2f}s)")
        else:
            print(f"Client-{cid}: Gagal")

    for i in range(5):
        t = threading.Thread(target=run_single_client, args=(i+1,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
    print("[Multi-Client] Selesai.")

from datetime import datetime

if __name__ == '__main__':
    while True:
        print_menu()
        choice = input("Pilih menu: ")
        
        if choice == '1':
            set_target()
        elif choice == '2':
            tcp_request()
        elif choice == '3':
            try:
                pc = int(input("Jumlah Paket (default 20): ") or 20)
                sz = int(input("Ukuran Paket (default 128): ") or 128)
                udp_qos_test(pc, sz)
            except ValueError:
                print("Input tidak valid")
        elif choice == '4':
            multi_client_simulation()
        elif choice == '5':
            print("\n[Mode Browser]")
            print(f"Silakan buka browser Anda dan kunjungi: http://{TARGET_IP}:{TARGET_HTTP_PORT}/index.html")
            print("Cek log di Proxy Server dan Web Server untuk melihat request masuk.")
        elif choice == '0':
            print("Keluar.")
            break
        else:
            print("Pilihan salah.")