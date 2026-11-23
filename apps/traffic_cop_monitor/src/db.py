# acts as the json database for the cops
import json
from threading import Lock
from queue import Queue
import os
from uuid import uuid4

class TrafficCopInst:

    filename: str = "../cops_db.json"
    dbData: dict = {}
    instQueue : Queue = Queue()
    
    def __init__(self, filename:str = None):
        if filename:
            self.filename = filename
    
    def loadRecords(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}
    
    def saveRecords(self):
        with Lock():
            with open(self.filename, 'w') as f:
                json.dump(self.dbData, f, indent=4)
    
    # add cop record to the DB
    def pushToDb(self, data):
        # TODO: Validate data
        data['entry_id'] = str(uuid4())
        self.instQueue.put(data)
    
    # load record by entry_id from the db
    def loadRecordById(self, entry):
        if entry in self.dbData:
            return self.dbData[entry]
        return None