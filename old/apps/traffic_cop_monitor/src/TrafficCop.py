from .CopLocation import CopLocation
from datetime import datetime
from uuid import uuid4
    
class TrafficCop:

    cop_location: CopLocation = None
    timestamp: datetime = None
    cop_id: str = None
    isActive: bool = False

    def __init__(self, data):
        keys = ['latitude', 'longitude', 'timestamp', 'cop_id']
        print(f"data: {data}")
        if all(k in data for k in keys):
            self.cop_location = CopLocation(data['latitude'], data['longitude'])
            self.timestamp = data['timestamp']
            self.cop_id = data['cop_id']
            self.isActive = True
        else:
            print("Insufficient data to initialize TrafficCop object.")
            return None
    
    def asDict(self) -> dict:
        return {
            'cop_id': self.cop_id,
            'latitude': self.cop_location.latitude if self.cop_location else None,
            'longitude': self.cop_location.longitude if self.cop_location else None,
            'timestamp': self.timestamp
        }

    def clearLocation(self):
        self.cop_location = None
    
    def getLocation(self) -> CopLocation:
        return self.cop_location

    def setTimestamp(self, timestamp: datetime):
        self.timestamp = timestamp
    
    def getTimestamp(self) -> datetime:
        return self.timestamp   

    def hasLocation(self) -> bool:
        return self.cop_location is not None

    def isActiveCop(self) -> bool:
        return self.isActive
    
    def deactivateCop(self):
        self.isActive = False
    