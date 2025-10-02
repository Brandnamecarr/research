
class CopLocation:

    latitude: float = 0.0
    longitude: float = 0.0

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
    
    def getPosition(self) -> tuple:
        return (self.latitude, self.longitude)
    
    def hasPosition(self) -> bool:
        return self.latitude != 0.0 and self.longitude != 0.0
    
    def clearPosition(self):
        self.latitude = 0.0
        self.longitude = 0.0
    
    # dummy string representation of latitude and longitude 
    def __str__(self) -> str:
        return f"({self.latitude}, {self.longitude})"
    