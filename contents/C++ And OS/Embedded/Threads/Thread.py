import os
import time
from threading import Thread, Lock

class Thread:

    periodicity: float # how often the thread runs in ms
    cb_func_ = None # callback function 
    running_ = False
    shutdown_ = False
    __data: any = None 
    data_lock = None

    def __init__(self, periodicity=0, optional_callback=None):
        self.periodicty = periodicity
        self.cb_func_ = optional_callback
        self.data_lock = Lock()
    
    def Start(self):

        self.shutdown_ = False
        self.running_ = True

        while self.running_:
            if self.shutdown_ is True:
                self.running_ = False
                return 
            
            if(self.cb_func_):
                if self.__data__:
                    temp_data = self.GetData()
                    self.cb_func_(temp_data)
                    time.sleep(self.periodicity)
                else:
                    self.cb_func_
                    time.sleep(self.periodicity)
    
    def GetData(self):
        with self.data_lock:
            return self.__data
    
    def End(self):
        self.shutdown_ = True
        self.running_ = False

        