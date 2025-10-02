from CopLocation import CopLocation
from datetime import datetime
    
class TrafficCop:

    cop_location: CopLocation = None
    timestamp: datetime = None

    def __init__(self):
        pass

    def updateLocation(self, latitude: float, longitude: float):
        self.cop_location = CopLocation(latitude, longitude)
    
    def updateLocationObj(self, location: CopLocation):
        self.cop_location = location
    
    def clearLocation(self):
        self.cop_location = None
    
    def getLocation(self) -> CopLocation:
        return self.cop_location

    def setTimestamp(self, timestamp: datetime):
        self.timestamp = timestamp
    
    def getTimestamp(self) -> datetime:
        return self.timestamp   
    
    def initTimestamp(self):
        self.timestamp = datetime.now()

    def hasLocation(self) -> bool:
        return self.cop_location is not None
    