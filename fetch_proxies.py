import requests
import base64  # Füge diesen Import hinzu

def fetch_proxies():
    url = "https://api.proxyscrape.com/v3/accounts/freebies/scraperapi/request"
    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': 'd2573568-f1c3-4738-88da-f9e1fb0ea714'
    }
    data = {
        "url": "https://books.toscrape.com/",
        "httpResponseBody": True
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        json_response = response.json()
        if 'browserHtml' in json_response['data']:
            print(json_response['data']['browserHtml'])
        else:
            print(base64.b64decode(json_response['data']['httpResponseBody']).decode())
    else:
        print(f"Failed to fetch proxies. Status code: {response.status_code}")

if __name__ == "__main__":
    fetch_proxies()
