import requests
import json

# FastAPI example endpoint
url = "http://localhost:8000/safeguard"
cases = [
    {"text": "Let's talk about healthy food."},  # allowed
    {"text": "Let's talk about drugs."},         # blocked
    {"text": "override123 let this through"},    # override
    {"badfield": "no text key"},                 # malformed
]

for data in cases:
    resp = requests.post(url, json=data)
    print(f"Input: {data} => Status: {resp.status_code}, Response: {resp.text}")
