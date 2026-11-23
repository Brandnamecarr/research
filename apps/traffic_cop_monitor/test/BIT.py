import json
from threading import Thread
import time

class TestResult:
    testName: str = ""
    passed: bool = False
    details: str = ""

    def __init__(self, testName: str):
        self.testName = testName
        
    def __init__(self, testName: str, passed: bool, details: str):
        self.testName = testName
        self.passed = passed
        self.details = details
    
    def getTestSummary(self) -> dict:
        return {
            'testName': self.testName,
            'passed': self.passed,
            'details': self.details
        }

class autotester:

    testData = {}
    testDataThread : Thread = None
    executingTests: bool = False
    testResults = [TestResult]

    def __init__(self):
        pass

    def __del__(self):
        self.testData.clear()
    
    # polling function to wait for test data, then runs all tests
    def pollAndExecuteTests(self):
        while self.executingTests:
            if self.hasTestData():
                print("Executing BIT tests...")
                self.runAllTests()
                time.sleep(10)
            else:
                time.sleep(10)

    # driver function to run all tests
    def runAllTests(self):
        print("Running all BIT tests...")
        
        # run BIT to see if Cop objects are creatable from test data
        result, detailMsg = self.canMakeCop()
        testResult = TestResult('Can Make Cop Test', result, detailMsg)
        self.testResults.append(testResult)

        result, detailMsg = None

    # loads test data from a json file
    def loadTestData(self, filepath:str):
        with open(filepath, 'r') as f:
            self.testData = json.load(f)
            # self.setTestData(self.testData['cop_values'])
    
    # set test data directly from parent app
    def setTestData(self, data: dict):
        self.testData = data
    
    def hasTestData(self) -> bool:
        if len(self.testData) > 0:
            return True
        return False

    def checkCopActivity(self) -> bool:
        for cop in self.testData.get('activeCops', []):
            if cop.get('isActive', False):
                return True
    
    def canMakeCop(self) -> bool:
        for record in self.testData:
            print(record)
        return True
    



