#!/usr/bin/env python3
import requests
import base64
import json

data = {
    "url": "https://roblox.com",  # URL zur gewünschten Website
    "httpResponseBody": True
}

headers = {
    'Content-Type': 'application/json',
    'X-Api-Key': 'd2573568-f1c3-4738-88da-f9e1fb0ea714'  # Dein API-Key
}

try:
    response = requests.post('https://api.proxyscrape.com/v3/accounts/freebies/scraperapi/request', headers=headers, json=data)
    response.raise_for_status()  # Überprüft auf HTTP-Fehler
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    exit()

print(f"Response Status Code: {response.status_code}")

if response.status_code == 200:
    try:
        json_response = response.json()
        print("API Response Data:")
        print(json.dumps(json_response, indent=4))  # Zeigt die gesamte API-Antwort an
        if 'data' in json_response and 'httpResponseBody' in json_response['data']:
            print("Decoded HTML:")
            print(base64.b64decode(json_response['data']['httpResponseBody']).decode())
        else:
            print("No httpResponseBody in response data.")
    except (ValueError, KeyError) as e:
        print(f"Error parsing JSON response: {e}")
else:
    print(f"Error: {response.status_code}")
