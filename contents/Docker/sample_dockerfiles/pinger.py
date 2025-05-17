import requests
import argparse

'''
    Ping if we are pinging localhost or a different IP
    Port might be important too.
'''

parser = argparse.ArgumentParser()
parser.add_argument("--ip", type=str, help="IP Addr to be pinged, default localhost", default='127.0.0.1')
# parser.add_argument("--port", action="store_true", help="Enable verbose mode")
parser.add_argument("--port", type=int, default=5000, help="Port to be pinged, default 5000")
args = parser.parse_args()

try:
    if args.ip == "127.0.0.1":
        response = requests.get("http://localhost:5000")
        print(response.text)
    # response = requests.get(f"http://{args.ip}:{args.port}")

except Exception as e:
    print(f'An error occurred while pinging {args.ip}:{args.port}')
    print(e)


