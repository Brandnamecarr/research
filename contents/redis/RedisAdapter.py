import redis
import json
import platform
import os

class RedisAdapter:

    # configs
    configMap = {}

    # osCompatibility 
    # bool to determine if we're in a redis-friendly OS
    osCompatibility = False

    # Redis Client
    client = None

    def __init__(self, configFile='configs.json'):
        self.readConfig(configFile)

        self.initClient()

    # reads config file
    def readConfig(self, configFile):

        with open(configFile, 'r') as file:
            data = json.load(file)

            if data is not None:
                self.configMap = data

        file.close()
        print(self.configMap)
    
    # return configMap
    def availableStreams(self):
        return self.configMap['Stream Names']
    
    # create the connection to redis 
    def initClient(self):
        ip = self.configMap['IP']
        port = self.configMap['Port']

        try:
            self.client = redis.Redis(host=ip, port=port)
            print('done')
        except Exception as e:
            print('error occurred')
            print(e)

    # 1. Get all streams (assumes keys with type 'stream')
    def get_all_streams(self):
        keys = self.client.keys('*')
        return [key.decode() for key in keys if self.client.type(key) == b'stream']

    # 2. Get all messages in a stream
    def get_all_messages(self, stream_name):
        return self.client.xrange(stream_name)

    # 3. Add an entry to a stream
    def add_entry(self, stream_name, data: dict):
        return self.client.xadd(stream_name, data)

    # 4. Delete a stream
    def delete_stream(self, stream_name):
        return self.client.delete(stream_name)
