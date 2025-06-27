from enum import Enum

class LOG_LEVEL(enum):
    DEBUG=0
    INFO=1
    ERROR=2

# logger class constructor
class Logger():
    
    owner: str # who initiated the logger class

    def __init__(self, who_made_me):
        self.owner = who_made_me 

    
