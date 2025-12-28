import socket
import threading
import os
import time
from datetime import datetime

# --- KONFIGURASI WEB SERVER ---
SERVER_IP = '0.0.0.0'  # Mendengarkan di semua interface
TCP_PORT = 8000
UDP_PORT = 9000
BUFFER_SIZE = 4096
WWW_DIR = './www'      # Folder tempat file HTML disimpan

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_activity(protocol, client_ip, action, status, size, process_time):
    """Mencatat aktivitas server ke terminal."""
    print(f"[{get_timestamp()}] [{protocol}] Client: {client_ip} | {action} | {status} | Size: {size}B | Time: {process_time:.4f}s")

# --- HANDLER TCP (HTTP) ---
def handle_tcp_client(client_socket, client_address):
    """Worker thread untuk menangani setiap request HTTP."""
    start_time = time.time()
    try:
        client_socket.settimeout(10)  # Timeout koneksi
        request = client_socket.recv(BUFFER_SIZE).decode('utf-8', errors='ignore')
        
        if not request:
            client_socket.close()
            return

        # Parsing Request Line (misal: GET /index.html HTTP/1.1)
        lines = request.split('\n')
        request_line = lines[0].strip().split()
        method = request_line[0]
        path = request_line[1]

        if path == '/':
            path = '/index.html'
        
        # Mencegah Directory Traversal
        filename = path.lstrip('/')
        filepath = os.path.join(WWW_DIR, filename)

        response_header = ""
        response_body = b""
        status_code = ""

        if os.path.exists(filepath) and os.path.isfile(filepath):
            with open(filepath, 'rb') as f:
                response_body = f.read()
            
            status_code = "200 OK"
            response_header = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: text/html\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                f"Connection: close\r\n\r\n"
            )
        else:
            status_code = "404 Not Found"
            response_body = b"<h1>404 File Not Found</h1>"
            response_header = (
                f"HTTP/1.1 404 Not Found\r\n"
                f"Content-Type: text/html\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                f"Connection: close\r\n\r\n"
            )

        # Kirim Response
        client_socket.sendall(response_header.encode('utf-8') + response_body)
        
        process_time = time.time() - start_time
        log_activity("TCP", client_address[0], f"{method} {path}", status_code, len(response_body), process_time)

    except socket.timeout:
        print(f"[-] Koneksi timeout dari {client_address}")
    except Exception as e:
        print(f"[!] Error handling TCP client: {e}")
    finally:
        client_socket.close()

def start_tcp_server():
    """Menjalankan TCP Server (Acceptor Single-Thread)."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((SERVER_IP, TCP_PORT))
        server.listen(5)
        print(f"[*] Web Server TCP berjalan di port {TCP_PORT}")
        
        while True:
            # Acceptor (Single Thread)
            client_sock, client_addr = server.accept()
            # Worker (Multi Thread)
            worker = threading.Thread(target=handle_tcp_client, args=(client_sock, client_addr))
            worker.daemon = True
            worker.start()
            
    except Exception as e:
        print(f"[!] Gagal menjalankan TCP Server: {e}")
    finally:
        server.close()

# --- HANDLER UDP (ECHO) ---
def start_udp_server():
    """Menjalankan UDP Echo Server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        server.bind((SERVER_IP, UDP_PORT))
        print(f"[*] Web Server UDP (Echo) berjalan di port {UDP_PORT}")
        
        while True:
            # Terima paket
            data, addr = server.recvfrom(BUFFER_SIZE)
            start_time = time.time()
            
            # Echo balik ke pengirim
            server.sendto(data, addr)
            
            process_time = time.time() - start_time
            log_activity("UDP", addr[0], "ECHO", "OK", len(data), process_time)
            
    except Exception as e:
        print(f"[!] Gagal menjalankan UDP Server: {e}")
    finally:
        server.close()

if __name__ == '__main__':
    if not os.path.exists(WWW_DIR):
        os.makedirs(WWW_DIR)
        print(f"[!] Folder '{WWW_DIR}' dibuat. Silakan masukkan index.html.")

    # Jalankan TCP dan UDP secara paralel
    tcp_thread = threading.Thread(target=start_tcp_server)
    udp_thread = threading.Thread(target=start_udp_server)
    
    tcp_thread.start()
    udp_thread.start()
    
    tcp_thread.join()
    udp_thread.join()