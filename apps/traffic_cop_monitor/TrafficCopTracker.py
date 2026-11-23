''' python imports '''
from flask import Flask, jsonify, request
from flask_cors import CORS
from typing import Optional
import argparse
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from threading import Lock, Thread # maybe need to write to log file/thread safe
import sys
import json
import time
''' src imports '''
from src import TrafficCop, CopLocation, db
from test import BIT

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

    ''' BIT Stuff'''
    bitTestThread: Thread = None
    bitTimeout: int = 10

    ''' application variables'''
    initialized:bool = False
    activeCops = []
    copTimeout = 10  # in minutes
    copMonitorThread: Thread = None
    copActivityThread: Thread = None
    copActivityPollInterval: int = 60  # in seconds
    cop_activity_thread_timer: int = 30 # in seconds

    ''' test '''
    tester:BIT.autotester = None
    testData = {}

    def __init__(self, ip:Optional[str]='127.0.0.1', port:Optional[int]=5000, buildType:Optional[str]='debug'):
        self.ip = ip
        self.port = port
        self.buildType = buildType
        print(f"Initializing Traffic Cop Tracker App in {self.buildType} mode on {self.ip}:{self.port}")
        
        # parse config file
        self.readConfigFile('config.json')

        # get test data
        if buildType == 'debug':
            self.readTestData()
        
        # setup BIT
        self.tester = BIT.autotester()
        if not self.tester.hasTestData():
            print("No BIT test data loaded.")
            self.tester.loadTestData('config.json')

        # set app to initialized
        self.initialized = True

        # start active cop monitor thread
        self.copMonitorThread = Thread(target=self.monitorActiveCopsThread, daemon=True)
        
        # start copActivityThread
        self.copActivityThread = Thread(target=self.copActivityThreadFunc, daemon=True)
        self.copActivityThread.start()
    
    def __del__(self):
        if self.app is not None:
            self.app = None
        self.initialized = False
        # self.copMonitorThread.join()
    
    # read config file
    def readConfigFile(self, filepath:str):
        with open(filepath, 'r') as f:
            tempData = json.load(f)
            self.copTimeout = tempData.get('cop_timeout_value_minutes', 10)
            print(f"Config file read. Cop timeout set to {self.copTimeout} minutes.")
            self.copActivityPollInterval = tempData.get('active_cop_timeout_value_seconds', 60)
            print(f"Config file read. Active cop poll interval set to {self.copActivityPollInterval} seconds.")
            self.cop_activity_thread_timer = tempData.get('cop_activity_thread_timer', 60)
            print(f"Config file value read. Activity Thread Timer Set to: {self.cop_activity_thread_timer} seconds")

    # read test data from config.json
    def readTestData(self):
        with open('config.json', 'r') as f:
            self.testData = json.load(f)

            if self.testData is not None or self.testData != {}:
                print("Test data successfully read from config.json")
                # self.loadTestCops()
    
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
            print('DATA FROM deactivateCop request below:')
            print(data)
            cop_id = data.get('data', None)
            print(f"Got cop_id: {cop_id}")
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
        @self.app.route('/loadCops', methods=['GET', 'OPTIONS'])
        def sendCopsToUI():
            response = {
                "active_cops": len(self.activeCops),
            }
            cops_data = [cop.asDict() for cop in self.activeCops]
            response['cops'] = cops_data
            return jsonify(response), 200
        
        # get number of active cops
        @self.app.route('/isTheBlockHot', methods=['GET', 'OPTIONS'])
        def isTheBlockHot():
            num_active_cops = len(self.activeCops)
            response = {
                'active_cop_count': num_active_cops,
                'is_block_hot': num_active_cops > 0
            }
            return jsonify(response), 200
    
    # function to see if there are any active cops
    def hasActiveCops(self) -> bool:
        if len(self.activeCops) > 0:
            return True
        return False
    
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
    
    # thread function to monitor active cops
    def monitorActiveCopsThread(self):
        while self.initialized:
            print(f"Current active cop size: {len(self.activeCops)}")
            time.sleep(self.cop_activity_thread_timer)
    
    # thread function to change cop activity (EXPERIMENTAL)
    def copActivityThreadFunc(self):
        print('Starting cop activity thread function...')
        while self.initialized:
            print(f"len of activeCops: {len(self.activeCops)}")
            for cop in self.activeCops:
                if cop.isActiveCop():
                    print('copActivityThreadFunc: Checking cop:', cop.cop_id)
                    if self.timeoutInactiveCops(cop):
                        print('Timing out inactive cop:', cop.cop_id)
                        cop.deactivateCop()
                        self.activeCops.remove(cop)
                    else:
                        continue

            time.sleep(self.copActivityPollInterval)
    
    # helper to timeout the cops
    def timeoutInactiveCops(self, cop: TrafficCop) -> bool:
        current_time = datetime.now(timezone.utc)
        cop_timestamp = datetime.fromisoformat(cop.getTimestamp())
        if current_time - cop_timestamp > timedelta(minutes=self.copTimeout):
            return True
        return False
                

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