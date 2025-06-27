import os
import time

class Thread:

    periodicity: float # how often the thread runs in ms
    cb_func_ = None # callback function 
    running_ = False
    shutdown_ = False

    def __init__(self, periodicity=0, optional_callback=None):
        self.periodicty = periodicity
        self.cb_func_ = optional_callback
    
    def Start(self):

        self.shutdown_ = False
        self.running_ = True

        while running_:
            if self.shutdown_ is True:
                self.running_ = False
                return 
            
            if(self.cb_func_):
                self.cb_func_
                time.sleep(self.periodicity)
    
    def End(self):
        self.shutdown_ = True
        self.running_ = False

        