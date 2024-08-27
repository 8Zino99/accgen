import requests

def fetch_proxies():
    url = "https://api.proxyscrape.com/v2/account/datacenter_shared/proxy-list?auth=nhuyjukilompnbvfrtyuui&type=getproxies&country[]=all&protocol=http&format=normal&status=all"
    response = requests.get(url)

    if response.status_code == 200:
        proxies = response.text.splitlines()
        with open('proxy.txt', 'w') as file:
            for proxy in proxies:
                file.write(f"{proxy}\n")
        print("Proxies successfully written to proxy.txt.")
    else:
        print(f"Failed to fetch proxies. Status code: {response.status_code}")

if __name__ == "__main__":
    fetch_proxies()
