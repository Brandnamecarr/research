import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--name", help="Your name")
parser.add_argument("--verbose", action="store_true", help="Enable verbose mode")
args = parser.parse_args()

if args.verbose:
    print("Verbose mode is on.")
print(f"Hello, {args.name}!")
