import socket

HOST = "0.0.0.0"  # localhost
PORT = 65432        # any port you like

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    print(f"Listening for UDP messages on {HOST}:{PORT}...")
    while True:
        data, addr = s.recvfrom(1024)
        print(f"Received from {addr}: {data.decode()}")
