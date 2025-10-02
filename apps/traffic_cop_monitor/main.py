import argparse
import json
from app import TrafficCopTracker

def print_usage(self):
    options = " COMMAND OPTIONS: \n --build <build type> \n --port <port app should be run on>"
    print(options)

class AppRunner:
    app: TrafficCopTracker
    port: int = 5000
    build: str = 'debug'

    def __init__(self):
        config = self.readConfig('config.json')
        print(config)
        self.app = TrafficCopTracker()

    def readConfig(self, path: str) -> dict:
        with open(path, 'r') as f:
            config = json.load(f)
        return config




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Configure app based on what you need\n\n TODO: Add more Configs")

    # add arguments:
    parser.add_argument('--h', required=False, help='Print Options')
    parser.add_argument('--build', type=str.lower, choices=['debug', 'release'], required=False, default='debug', help='Build in Debug or Release' )
    parser.add_argument('--port', type=int, default=5000, required=False, help='Port the app should run on. Default = 5000')

    application = None
    args = parser.parse_args()

    if args.h:
        print_usage()
    if args.build == 'debug':
        application = AppRunner()
    elif args.build == 'release':
        application = AppRunner(args.build, args.port)