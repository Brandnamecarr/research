from Logger import Logger

class LogManager():
    loggers: dict = {}

    @staticmethod
    def start(component_name: str) -> Logger:
        if component_name in LogManager.loggers:
            return LogManager.loggers[component_name]
        
        new_logger = Logger(component_name)
        if new_logger.create_log_file():
            LogManager.loggers[component_name] = new_logger
            return new_logger
        
        return None

    def stop(self, component_name: str) -> bool:
        if component_name in self.loggers:
            del self.loggers[component_name]
            return True
        return False

    def getActiveLoggers(self) -> dict:
        return self.loggers
    
    def hasComponentLogger(self, component_name: str) -> bool:
        return component_name in self.loggers
    