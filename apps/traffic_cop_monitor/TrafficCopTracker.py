''' python imports '''
from flask import Flask, jsonify, request
from flask_cors import CORS
from typing import Optional
import argparse
from datetime import datetime
from uuid import uuid4
from threading import Lock, Thread # maybe need to write to log file/thread safe
import sys
import json
''' src imports '''
from src import TrafficCop, CopLocation
# from test import autotester

################################ CLASS #################################
''' class definition '''
class TrafficCopTracker:

    ''' networking & build variables '''
    ip: str = '127.0.0.1'
    port:int = 5000
    buildType:str = 'debug'

    ''' flask app '''
    app:Flask = Flask(__name__)
    CORS(app)

    ''' application variables'''
    initialized:bool = False
    activeCops = []

    ''' test '''
    # tester:autotester = None
    testData = {}

    def __init__(self, ip:Optional[str]='127.0.0.1', port:Optional[int]=5000, buildType:Optional[str]='debug'):
        self.ip = ip
        self.port = port
        self.buildType = buildType
        print(f"Initializing Traffic Cop Tracker App in {self.buildType} mode on {self.ip}:{self.port}")
        
        # get test data
        self.readTestData()
        
        # set app to initialized
        self.initialized = True
    
    def __del__(self):
        if self.app is not None:
            self.app = None
        self.initialized = False
    
    # read test data from config.json
    def readTestData(self):
        with open('config.json', 'r') as f:
            self.testData = json.load(f)

            if self.testData is not None or self.testData != {}:
                print("Test data successfully read from config.json")
                self.loadTestCops()
    
    # make cop objects from test data
    def loadTestCops(self):
        copValues = self.testData.get('cop_values')
        for cop in copValues.keys():
            trafficCop = TrafficCop.TrafficCop(copValues[cop])
            self.activeCops.append(trafficCop)

    # routes and functions get defined in here
    def _register_routes(self):

        @self.app.route('/', methods=['GET'])
        def home():
            ip = request.remote_addr
            return jsonify(ip), 200
        
        # echo route for testing
        @self.app.route('/echo', methods=['POST'])
        def echo():
            data = request.get_json()
            data['message'] = f"Echo from Traffic Cop Tracker at {datetime.now()}"
            return jsonify(data), 200

        # receive cop location
        @self.app.route('/report_location', methods=['POST'])
        def reportLocation():
            data = request.get_json()
            print('Received location data:', data)
            trafficCop = TrafficCop.TrafficCop(data)
            self.activeCops.append(trafficCop)
            response = {
                'status message': 'Location received',
                'active_cop_size': len(self.activeCops)
            }
            return jsonify(response), 200
        
        # set cop status to deactivated
        @self.app.route('/deactivate_cop', methods=['POST'])
        def deactivateCop():
            data = request.get_json()
            cop_id = data.get('cop_id', None)
            if cop_id is None:
                return jsonify({"error": "cop_id is required"}), 400
            # find cop by ID and deactivate
            traffic_cop = self.findCopById(cop_id)
            if traffic_cop is None:
                return jsonify({"error": f"Cop with ID {cop_id} not found"}), 404
            traffic_cop.deactivateCop()
            self.activeCops.remove(traffic_cop)
            return jsonify({"status": f"Cop {cop_id} deactivated"}), 200
    
        # get all active cops
        @self.app.route('/loadCops', methods=['GET'])
        def sendCopsToUI():
            cops_data = [cop.asDict() for cop in self.activeCops]
            return jsonify(cops_data), 200
    
    # finds a cop by their ID
    # if not found, returns None
    def findCopById(self, cop_id: str) -> TrafficCop:
        for cop in self.activeCops:
            if cop.cop_id == cop_id:
                return cop
        return None
    
    # checks if app is initialized
    def isInitialized(self) -> bool:
        if self.initialized:
            return True
        return False
    
    # starts the flask app on specified IP and port
    def start(self):
        if not self.initialized:
            return
        else:
            self._register_routes()
            self.app.run(host=self.ip, port=self.port, debug=(self.buildType=='debug'))

################################# END OF CLASS #################################

# if the -h flag is provided, print usage, then exit.
def print_usage(self):
    options = " COMMAND OPTIONS: \n --build <build type> \n --port <port app should be run on>"
    print(options)

if __name__ == '__main__':
    application = None

    parser = argparse.ArgumentParser(description="Configure app based on what you need\n\n TODO: Add more Configs")

    # add arguments:
    parser.add_argument('--h', required=False, help='Print Options')
    parser.add_argument('--ip', type=str, default='127.0.0.1', required=False)
    parser.add_argument('--build', type=str.lower, choices=['debug', 'release'], required=False, default='debug', help='Build in Debug or Release' )
    parser.add_argument('--port', type=int, default=5000, required=False, help='Port the app should run on. Default = 5000')

    
    args = parser.parse_args()
    if args.h:
        print_usage()
        sys.exit(0)
    if args.build == 'debug':
        application = TrafficCopTracker()
    elif args.build == 'release':
        application = TrafficCopTracker(args.ip, args.port, args.build)

    if application.isInitialized():
        application.start()
        # sys.exit(0)