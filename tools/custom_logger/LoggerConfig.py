import json
from enums import LOG_LEVEL

class LoggerConfig():
    configFile = None
    log_level_ = LOG_LEVEL.UNINITIALIZED
    config = None
    file_extension_ = None
    log_directory_ = None
    use_std_out = False

    def __init__(self, configFile: str):

        self.configFile = configFile
        self.parseAndLoadManagerConfig(self.configFile)

    def parseAndLoadManagerConfig(self, config_json: str) -> bool:
        try:
            self.config = json.loads(config_json)
            if "LoggerManager" in self.config:
                manager_config = self.config["LoggerManager"]
                if "file_extension" in manager_config:
                    self.file_extension_ = manager_config["file_extension"]
                else:
                    self.file_extension_ = ".log"
                
                if "log_directory" in manager_config:
                    self.log_directory_ = manager_config["log_directory"]
                else:
                    self.log_directory_ = "."
                
                if "use_std_out" in manager_config:
                    self.use_std_out = bool(manager_config["use_std_out"])
                
                if self.file_extension_ is not None and self.log_directory_ is not None:
                    return True
            return False
        
        except json.JSONDecodeError as e:
            print(f"LoggerConfig::parseAndLoadManagerConfig() -> JSON Decode Error: {e}")
            return False
    
    # returns service-level config for a given component
    def parseAndLoadComponentConfig(self, component_name: str) -> dict:
        if self.config is None or component_name not in self.config:
            return None
        
        component_config = self.config[component_name]
        return component_config