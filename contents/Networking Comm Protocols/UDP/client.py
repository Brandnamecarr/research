import socket
import sys
from time import sleep
import random as rd

HOST = "127.0.0.1"  # localhost
PORT = 65432        # must match the receiver's port

# if len(sys.argv) < 2:
#     print(f"Usage: python {sys.argv[0]} 'your message here'")
#     sys.exit(1)

# message = sys.argv[1]

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    while True:
        message = f"Hello, UDP Server! Random number: {rd.randint(1, 100)}"
        s.sendto(message.encode(), (HOST, PORT))
        print(f"Sent: {message}")
        sleep(2)
