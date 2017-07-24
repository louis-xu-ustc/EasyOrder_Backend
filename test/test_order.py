import requests
import json

url = "http://localhost:9000/backend/order/"

data = {"twitterID": "3780616332", "dish": 1, "amount":2}

response = requests.post(url, data=json.dumps(data))
