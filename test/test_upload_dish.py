import requests
import base64
import json

url = "http://localhost:9000/backend/dish/"
with open('test.jpeg', "rb") as image:
    encoded_string = base64.b64encode(image.read())

data = {"name": "My Meat C",
        "price": 50,
        "photo": encoded_string}

response = requests.post(url, data=json.dumps(data))
