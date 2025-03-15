import boto3
import json
from datetime import datetime
import boto3.dynamodb
import boto3.dynamodb.conditions
from botocore.exceptions import ClientError
import DynamoDBException
from enum import Enum

# enum to represent the status of the table
class TableStatus(Enum):
    ACTIVE = 0
    CREATING = 1
    UPDATING = 2
    DELETING = 3
    UNKNOWN = 4


class DynamoDBAdapter:

    config_filename = 'aws_configs.json'
    ConfigData = {}
    client = None
    resource = None
    region = None
    table_name_ = '' # represents the table name being modified
    table_status_ = TableStatus.UNKNOWN 

    def __init__(self, table_name_='') -> None:
        self.LoadConfig()
        
        # init the resource object
        try:
            self.resource = boto3.resource(service_name='dynamodb', region_name=self.region) # Functionality
        except:
            print('DynamoDBAdapter::init() -> error intializing dynamodb resource object')

        # init the client object
        try:
            self.client = boto3.client('dynamodb') # API
            print('DynamoDBAdapter::init() -> successfully intialized dynamodb client')
        except:
            print('DynamoDBAdapter::init() -> something wrong with self.client initialization')

        self.table_name_ = table_name_
        self.CheckTableStatus()

    # reads the config file: 1st step in init
    # gives data to ParseConfigData
    def LoadConfig(self):
        configFile = open(self.config_filename, 'r')

        data = json.load(configFile)

        self.ParseConfigData(data)

    # Parses the Config data sent by LoadConfig()
    def ParseConfigData(self, data: dict):
        
        credentials = data['AWS']

        self.ConfigData['aws_access_key'] = credentials['aws_access_key']
        self.ConfigData['aws_secret_key'] = credentials['aws_secret_key']

        dynamodb = data['dynamodb']

        self.ConfigData['Resource'] = dynamodb['Resource']
        self.resource = self.ConfigData['Resource']

        self.ConfigData['Region'] = dynamodb['Region']
        self.region = self.ConfigData['Region']

        print(f'self.region = {self.region}')
        print(f"self.resource: {self.resource} --- type {type(self.resource)}")
    
    '''
        Creates a table based on 'table_name_'
    '''
    def CreateTable(self):
        # Create a table with UUID as the primary key
        table = self.resource.create_table(
            TableName = self.table_name_,
            KeySchema = 
            [
                {'AttributeName': 'EmailAddress', 'KeyType': 'HASH'},  # Partition Key
            ],
            AttributeDefinitions = 
            [
                {'AttributeName': 'EmailAddress', 'AttributeType': 'S'},  # String
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        table.meta.client.get_waiter('table_exists').wait(TableName=self.table_name_)


    '''
        Checks the status of the DynamoDB Table
        Status:
            - ACTIVE
            - CREATING
            - UPDATING
            - DELETING
    '''
    def CheckTableStatus(self) -> bool:
        try:
            response = self.client.describe_table(TableName=self.table_name_)
            if response['Table']['TableStatus'] == 'ACTIVE':
                self.table_status_ = TableStatus.ACTIVE
                return True
            else:
                self.table_status_ = TableStatus.UNKNOWN
                return False

        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print('table not found')
                self.table_status_ = TableStatus.UNKNOWN
                return False
            else:
                print('something else went wrong')
                self.table_status_ = TableStatus.UNKNOWN
                return False

    def emplace(self, data: dict) -> bool:
        print('DynamoDBAdapter::emplace() -> top of function call')
        if self.table_status_ is not TableStatus.ACTIVE:
            print('DynamoDBAdapter::emplace() -> self.table_status_ is not in an active state!')
            return False
        else:
            if isinstance(data, dict):
                try:
                    table = self.resource.Table(self.table_name_)
                    response = table.put_item(Item=data)
                    print('successfully inserted item into table')
                    return True
                except Exception as e:
                    print(f"Error occurred inside emplace() -> {e}")
                    return False
            else:
                print('Error inserting item -> data is not a dict instead is type ', type(data))
                return False
    
    def query_items(self, key_value):
        response = None

        if self.table_status_ == TableStatus.ACTIVE:
            table = self.resource.Table(self.table_name_)

            try:
                response = table.query(KeyConditionExpression=boto3.dynamodb.conditions.Key('EmailAddress').eq(key_value))
                print('Retrieved items from query')
                return response.get('Items', [])
            except:
                print('Error retrieving value from Table')

dbAdpt = DynamoDBAdapter('People') # give it the new parameter.

# experiment with resource
item = {
    'EmailAddress' : 'EllieGonzalez@outlook.com',
    'RandomKey' : 5
}

response = dbAdpt.query_items('temp@outlook.com') 
print(type(response))
