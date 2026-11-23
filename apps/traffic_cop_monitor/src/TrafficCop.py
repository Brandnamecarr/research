from .CopLocation import CopLocation
from datetime import datetime, timezone
from uuid import uuid4
import json
    
class TrafficCop:

    cop_location: CopLocation = None
    timestamp: datetime = None
    cop_id: str = None
    isActive: bool = False

    def __init__(self, data):
        keys = ['latitude', 'longitude', 'timestamp', 'cop_id']

        if 'data' in data:
            data = data['data']

        if all(k in data for k in keys):
            self.cop_location = CopLocation(float(data['latitude']), float(data['longitude']))
            self.convertTimestamp(data['timestamp'])
            self.cop_id = str(data['cop_id'])
            self.isActive = True
        else:
            print("Insufficient data to initialize TrafficCop object.")
    
    def convertTimestamp(self, value: int):
        seconds = value / 1000.0
        tempTimestamp = datetime.fromtimestamp(seconds, tz=timezone.utc)
        self.timestamp = tempTimestamp.isoformat()
        print('Converted timestamp:', self.timestamp)
        
    def asDict(self) -> dict:
        return {
            'cop_id': self.cop_id,
            'latitude': self.cop_location.latitude if self.cop_location else None,
            'longitude': self.cop_location.longitude if self.cop_location else None,
            'timestamp': self.timestamp if self.timestamp else None
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
    