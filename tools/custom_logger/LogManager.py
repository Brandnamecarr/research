from Logger import Logger
from LoggerConfig import LoggerConfig

# global variables
use_std_out_ = False

def debug(message : str):
    if use_std_out_:
        print(f"LogManager::debug() -> {message}")

class LogManager():
    loggers: dict = {}
    loggerConfigFilename: str = "LoggerConfig.json"
    loggerConfig: LoggerConfig = None

    def __init__(self, configFile: str):
        if configFile == "":
            return None
        debug(f"LogManager::LogManager() -> initializing LogManager with config file: {configFile}")
        self.loggerConfigFilename = configFile

        self.loggerConfig = LoggerConfig(self.loggerConfigFilename)

        try:
            with open(configFile, 'r') as file:
                config_json = file.read()
                if not self.loggerConfig.parseAndLoadManagerConfig(config_json):
                    debug("LogManager::LogManager() -> Failed to parse and load logger configuration.")
        except FileNotFoundError as e:
            debug(f"LogManager::LogManager() -> Configuration file not found: {e}")
        
        global use_std_out_
        use_std_out_ = self.loggerConfig.use_std_out
    
    def __del__(self):
        self.stopAll()
        debug("LogManager::LogManager() -> LogManager instance destroyed.")

    @staticmethod
    def start(component_name: str) -> Logger:
        if component_name in LogManager.loggers:
            return LogManager.loggers[component_name]
        
        componentLoggerConfig = LogManager.loggerConfig.parseAndLoadComponentConfig(component_name)
        if componentLoggerConfig is None:
            debug(f"LogManager::start() -> No configuration found for component: {component_name}")
            return None
        new_logger = Logger(component_name) 
        debug(f"LogManager::start() -> starting logger for component: {component_name}")
        if new_logger.create_log_file():
            LogManager.loggers[component_name] = new_logger
            debug(f"LogManager::start() -> logger for component: {component_name} started successfully")
            return new_logger
        
        return None

    def stop(self, component_name: str) -> bool:
        if component_name in self.loggers:
            del self.loggers[component_name]
            debug(f"LogManager::stop() -> stopped logger for component: {component_name}")
            return True
        return False
    
    def stopAll(self) -> bool:
        try:
            for logger in self.loggers.values():
                del logger
            self.loggers.clear()
            debug("LogManager::stopAll() -> stopped all loggers")
        except Exception as e:
            debug(f"LogManager::stopAll() -> Exception occurred while stopping all loggers: {e}")
            return False
        return True

    def getActiveLoggers(self) -> dict:
        return self.loggers
    
    def hasComponentLogger(self, component_name: str) -> bool:
        return component_name in self.loggers
    