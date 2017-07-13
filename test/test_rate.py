import requests
import json

url = "http://localhost:8000/backend/rate/1/"

data = {"user": "456", "rate": 4}

response = requests.delete(url, data=json.dumps(data))
