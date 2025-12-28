import socket
import threading
import time

# --- KONFIGURASI PROXY ---
# GANTI IP INI DENGAN IP LAPTOP A (WEB SERVER) ANDA
TARGET_WEB_SERVER_IP = '127.0.0.1' 
TARGET_WEB_SERVER_PORT = 8000
TARGET_UDP_SERVER_PORT = 9000

PROXY_IP = '0.0.0.0'
PROXY_TCP_PORT = 8080
PROXY_UDP_PORT = 9090
BUFFER_SIZE = 4096

# Cache Sederhana (In-Memory)
# Format: { 'url': (response_data, timestamp) }
CACHE = {}
CACHE_LOCK = threading.Lock()

def log_proxy(protocol, src, dst, status, size, duration):
    print(f"[PROXY {protocol}] {src} -> {dst} | Status: {status} | Size: {size}B | Time: {duration:.4f}s")

# --- HANDLER TCP (HTTP Forwarding) ---
def handle_tcp_client(client_socket, client_addr):
    start_time = time.time()
    server_socket = None
    
    try:
        client_socket.settimeout(5) # Timeout Proxy-Client
        
        # 1. Terima Request dari Client
        request = client_socket.recv(BUFFER_SIZE)
        if not request:
            return

        # Ambil URL untuk key cache (sederhana)
        try:
            first_line = request.decode('utf-8', errors='ignore').split('\n')[0]
            url = first_line.split()[1]
        except:
            url = "UNKNOWN"

        # 2. Cek Cache
        with CACHE_LOCK:
            if url in CACHE:
                # Cache HIT
                log_proxy("TCP", client_addr, TARGET_WEB_SERVER_IP, "CACHE HIT", len(CACHE[url]), time.time() - start_time)
                client_socket.sendall(CACHE[url])
                return

        # Cache MISS -> Forward ke Web Server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.settimeout(5) # Timeout Proxy-Server
        
        try:
            server_socket.connect((TARGET_WEB_SERVER_IP, TARGET_WEB_SERVER_PORT))
            server_socket.sendall(request)
            
            # 3. Terima Response dari Web Server
            response = b""
            while True:
                chunk = server_socket.recv(BUFFER_SIZE)
                if not chunk:
                    break
                response += chunk
            
            # 4. Simpan ke Cache
            if response:
                with CACHE_LOCK:
                    CACHE[url] = response
                
                # 5. Kirim balik ke Client
                client_socket.sendall(response)
                log_proxy("TCP", client_addr, TARGET_WEB_SERVER_IP, "CACHE MISS / FORWARD", len(response), time.time() - start_time)
            
        except socket.timeout:
            # 504 Gateway Timeout
            error_msg = b"HTTP/1.1 504 Gateway Timeout\r\n\r\n"
            client_socket.sendall(error_msg)
            log_proxy("TCP", client_addr, TARGET_WEB_SERVER_IP, "504 TIMEOUT", 0, time.time() - start_time)
        except Exception as e:
            # 502 Bad Gateway
            error_msg = b"HTTP/1.1 502 Bad Gateway\r\n\r\n"
            client_socket.sendall(error_msg)
            log_proxy("TCP", client_addr, TARGET_WEB_SERVER_IP, f"502 ERROR: {e}", 0, time.time() - start_time)

    except Exception as e:
        print(f"[!] Error Proxy TCP: {e}")
    finally:
        if client_socket: client_socket.close()
        if server_socket: server_socket.close()

def start_tcp_proxy():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((PROXY_IP, PROXY_TCP_PORT))
    server.listen(10)
    print(f"[*] Proxy TCP berjalan di {PROXY_IP}:{PROXY_TCP_PORT}")

    while True:
        client, addr = server.accept()
        # Thread Pool sederhana bisa diimplementasikan dengan membatasi jumlah thread aktif
        # Di sini menggunakan thread per request untuk simplifikasi
        t = threading.Thread(target=handle_tcp_client, args=(client, addr))
        t.daemon = True
        t.start()

# --- HANDLER UDP (Packet Forwarding) ---
def handle_udp_packet(data, client_addr, proxy_udp_socket):
    """
    Fungsi untuk memproses satu paket UDP.
    Terima Client -> Kirim Server -> Terima Server -> Kirim Client
    Tanpa Retransmission.
    """
    start_time = time.time()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.settimeout(2) # Timeout pendek untuk UDP
    
    try:
        # Forward ke Web Server
        server_socket.sendto(data, (TARGET_WEB_SERVER_IP, TARGET_UDP_SERVER_PORT))
        
        # Terima balasan dari Web Server
        response, _ = server_socket.recvfrom(BUFFER_SIZE)
        
        # Forward balik ke Client
        proxy_udp_socket.sendto(response, client_addr)
        
        log_proxy("UDP", client_addr, TARGET_WEB_SERVER_IP, "FORWARDED", len(data), time.time() - start_time)
        
    except socket.timeout:
        log_proxy("UDP", client_addr, TARGET_WEB_SERVER_IP, "DROP (TIMEOUT)", len(data), time.time() - start_time)
    except Exception as e:
        print(f"[!] Error UDP Forward: {e}")
    finally:
        server_socket.close()

def start_udp_proxy():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((PROXY_IP, PROXY_UDP_PORT))
    print(f"[*] Proxy UDP berjalan di {PROXY_IP}:{PROXY_UDP_PORT}")

    while True:
        try:
            data, addr = server.recvfrom(BUFFER_SIZE)
            # Spawn thread untuk setiap paket agar non-blocking
            t = threading.Thread(target=handle_udp_packet, args=(data, addr, server))
            t.daemon = True
            t.start()
        except Exception as e:
            print(f"[!] Error Main UDP Proxy: {e}")

if __name__ == '__main__':
    # Jalankan Proxy TCP dan UDP
    t_tcp = threading.Thread(target=start_tcp_proxy)
    t_udp = threading.Thread(target=start_udp_proxy)
    
    t_tcp.start()
    t_udp.start()
    
    t_tcp.join()
    t_udp.join()