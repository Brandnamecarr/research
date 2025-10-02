import redis
import json

class RedisAdapter:

    configFile = ''
    configMap = {}

    def __init__(self, configFile):
        self.configFile = configFile
        self.readConfig()

    def readConfig(self):

        with open(self.configFile, 'r') as file:
            data = json.load(file)

            if data is not None:
                self.configMap = data

        file.close()
        print(self.configMap)

r = RedisAdapter('./configs.json')