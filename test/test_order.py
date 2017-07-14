import requests
import json

url = "http://localhost:8000/backend/order/"

data = {"twitterID": "123", "dish": 1, "amount":2}

response = requests.post(url, data=json.dumps(data))
