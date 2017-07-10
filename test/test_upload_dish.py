import requests
import base64
import json

url = "http://localhost:8000/backend/dish/"
with open('test.jpeg', "rb") as image:
    encoded_string = base64.b64encode(image.read())

data = {"name": "My Pizza A",
        "price": 20,
        "rate": 3.5,
        "rateNum": 1,
        "photo": encoded_string}

response = requests.post(url, data=json.dumps(data))
