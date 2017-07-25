import requests
import base64
import json

url = "http://localhost:9000/backend/dish/7/"
response = requests.delete(url)
print response.content
