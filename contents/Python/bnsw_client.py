import requests
import json

def make_post_req():
    response = requests.post("http://127.0.0.1:5000/user", json={"name": "Brandon", "age": 14})

    data = response.json()
    print(data)
    print(response.text)

def make_get_req():
    response = requests.get("http://127.0.0.1:5000/")
    data = response.json()
    print(data)

make_post_req()
# make_get_req()