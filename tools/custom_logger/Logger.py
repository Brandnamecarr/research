from enum import Enum
from datetime import datetime
import os
from threading import Thread, Lock
from queue import Queue
from LoggerConfig import LoggerConfig
from enums import LOG_LEVEL

def debug(message: str):
    print(f"Logger::debug() -> {message}")

# logger class constructor
class Logger():

    component_name: str = ""    # who initiated the logger class
    log_filename: str = ""      # contains the name of the log file
    log_file = None             # log file object 

    # vars for async writing
    writer_thread_ = None
    writer_thread_lock_ = Lock()
    messages_queue_ = Queue()

    # logger specific configurations
    log_level_ = LOG_LEVEL.UNINITIALIZED
    use_std_out_ = False
    log_directory_ = "."
    file_extension_ = ".log"

    
    def __init__(self, component_name: str, loggerConfig: LoggerConfig = None):
        if component_name == "":
            return None
        self.component_name = component_name
        debug(f"Logger::Logger() -> initializing logger for component: {self.component_name}")

        self.log_filename = f"{self.component_name}.log"
        
        self.writer_thread_ = Thread(target=self.processLogQueue)
        debug(f"Logger::Logger() -> starting writer thread for component: {self.component_name}")
        self.writer_thread_.start()
    
    def __del__(self):
        if self.log_file:
            with self.writer_thread_lock_:
                self.log_file.close()
        self.messages_queue_.put(None)
        self.writer_thread_.join()
        debug(f"Logger::__del__() -> destroyed logger for component: {self.component_name}")
    
    # create the file
    def create_log_file(self) -> bool:

        if os.path.exists(self.log_filename):
            debug(f"Logger::create_log_file() -> log file already exists: {self.log_filename}")
            return False
        debug(f"Logger::create_log_file() -> creating log file: {self.log_filename}")
        try:
            self.log_file = open(self.log_filename, 'w')
            debug(f"Logger::create_log_file() -> log file created successfully: {self.log_filename}")
            return True
        
        except Exception as e:
            print(f"Logger::create_log_file() -> an error occurred while creating the log file")
            print(f"{e}")
            return False
    
    def processLogQueue(self):
        while True and len(self.messages_queue_.queue) > 0:
            debug("Logger::processLogQueue() -> processing log queue")
            message = self.messages_queue_.get()
            if message is None:
                debug("Logger::processLogQueue() -> exiting log writer thread")
                break
            with self.writer_thread_lock_:
                self.log_file.write(message)
                self.log_file.flush()
            self.messages_queue_.task_done()

    def get_current_time(self):
        return datetime.now().strftime("%H:%M:%S.") + f"{datetime.now().microsecond // 1000:03d}"

    def debug(self, message) -> bool:
        if len(message) > 0:
            timestamp = self.get_current_time()
            formatted_message = f"[{timestamp}] [DEBUG] {message}\n"
            with self.writer_thread_lock_:
                self.log_file.write(formatted_message)
                debug(f"Logger::debug() -> wrote debug message to log file: {formatted_message.strip()}")
                self.log_file.flush()
            return True
        return False

    def error(self, message) -> bool:
        if len(message) > 0:
            timestamp = self.get_current_time()
            formatted_message = f"[{timestamp}] [ERROR] {message}\n"
            with self.writer_thread_lock_:
                self.log_file.write(formatted_message)
                debug(f"Logger::error() -> wrote error message to log file: {formatted_message.strip()}")
                self.log_file.flush()
            return True
        return False

    def info(self, message) -> bool:
        if len(message) > 0:
            timestamp = self.get_current_time()
            formatted_message = f"[{timestamp}] [INFO] {message}\n"
            with self.writer_thread_lock_:
                self.log_file.write(formatted_message)
                debug(f"Logger::info() -> wrote info message to log file: {formatted_message.strip()}")
                self.log_file.flush()
            return True
        return False