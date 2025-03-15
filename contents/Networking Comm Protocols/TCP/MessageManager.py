import socket
import json

class MessageManager:
    IP = None
    

    def __init__(self):

    def ParseAndLoadConfigs(self):
        data = open('./MessageManager.json', 'r')
        
        data = json.load(data)