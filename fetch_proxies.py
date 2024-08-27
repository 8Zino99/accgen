import requests
import base64

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
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raises HTTPError for bad responses
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return
    
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")

    try:
        json_response = response.json()
    except ValueError:
        print("Response is not in JSON format.")
        return

    if 'browserHtml' in json_response['data']:
        print(json_response['data']['browserHtml'])
    else:
        try:
            decoded_body = base64.b64decode(json_response['data']['httpResponseBody']).decode()
            print(decoded_body)
        except KeyError:
            print("Key 'httpResponseBody' not found in response data.")
        except (base64.binascii.Error, UnicodeDecodeError) as e:
            print(f"Error decoding base64 response: {e}")

if __name__ == "__main__":
    fetch_proxies()
