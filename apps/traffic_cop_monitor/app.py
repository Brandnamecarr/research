from flask import Flask, jsonify, request
from typing import Optional

class TrafficCopTracker:

    app = Flask("Traffic Cop Monitor")

    def __init__(self, build_type='debug', port: Optional[int]=5000):
        print('in constructor')
        print(build_type)
        print(port)