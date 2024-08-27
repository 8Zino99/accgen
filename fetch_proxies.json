import requests

def fetch_proxies():
    url = "https://api.proxyscrape.com/v3/accounts/freebies/scraperapi/request"
    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': 'd2573568-f1c3-4738-88da-f9e1fb0ea714'  # Ersetze dies durch deinen echten API-Key
    }
    data = {
        "url": "https://books.toscrape.com/",
        "httpResponseBody": True
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        json_response = response.json()
        proxies = json_response.get('data', {}).get('httpResponseBody', '')
        if proxies:
            proxies = proxies.splitlines()
            with open('proxy.txt', 'w') as file:
                for proxy in proxies:
                    file.write(f"{proxy}\n")
            print("Proxies successfully written to proxy.txt.")
        else:
            print("No proxies found.")
    else:
        print(f"Failed to fetch proxies. Status code: {response.status_code}")

if __name__ == "__main__":
    fetch_proxies()
