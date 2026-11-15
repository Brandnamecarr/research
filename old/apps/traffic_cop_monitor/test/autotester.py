import json

# TODO Maybe
class autotester:
    testData = {}

    def __init__(self):
        pass

    def __del__(self):
        self.testData.clear()

    # loads test data from a json file
    def loadTestData(self, filepath:str):
        with open(filepath, 'r') as f:
            self.testData = json.load(f)
    
    def hasTestData(self) -> bool:
        if len(self.testData) > 0:
            return True
        return False
    


