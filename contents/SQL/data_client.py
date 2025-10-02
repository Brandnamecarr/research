import requests

# const 
DATA_FACTORY_URL = "http://127.0.0.1:5000"

# Data Server URLs
GET_UUID_URL= DATA_FACTORY_URL + "/getData"

def get_uuid():
    response = requests.get(GET_UUID_URL)
    recv_data_ = response.json
    print(recv_data_['uuid'])

get_uuid()