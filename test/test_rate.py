import requests
import json

url = "http://localhost:9000/backend/rate/1/"

data = {"user": "456", "rate": 4}

response = requests.put(url, data=json.dumps(data))
print response
