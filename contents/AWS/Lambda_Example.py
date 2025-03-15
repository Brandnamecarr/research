'''
    Demonstrates Lambda in action
'''

import requests
import json
from typing import Optional


class LambdaExample:

    config_file = "./aws_configs.json"
    function = None
    configs = {}
    lambda_params = {}
    data = Optional[dict]

    def __init__(self):
        self.Load()

    def Load(self):
        with open(self.config_file, 'r') as file:
            data = json.load(file)
            self.Parse(data)

    def Parse(self, data):
        self.configs = data['Lambda']
        
        self.function = self.configs['test_function_endpoint']
        print(f"Just set self.function to {self.function}")
    
    def SetParams(self, params: dict):
        if isinstance(params, dict) is False:
            return
        self.lambda_params = params

    def InvokeFunction(self):
        response = requests.post(self.function, json=self.lambda_params)
        print(f"Status Code: {response.status_code}")
        print(f"Body: {response.json()}")
        
lambda_example = LambdaExample()
lambda_example.InvokeFunction()