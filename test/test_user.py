import requests
import json

url = "http://localhost:8000/backend/user/"

data = {"twitterID": "456", "name": "Bad"}

response = requests.post(url, data=json.dumps(data))
