import json
import time
import random
import requests
from datetime import datetime, timezone
from random_username.generate import generate_username
from concurrent.futures import ThreadPoolExecutor
import loguru

def load_settings():
    try:
        with open("settings.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        loguru.logger.error("settings.json file not found. Please make sure it exists.")
        exit()

# Load settings
settings_json = load_settings()

# Input Webhook URL and number of accounts
webhook_url = input("Enter your Discord webhook URL: ").strip()
try:
    total_generate_count = int(input("How many accounts do you want to generate? ").strip())
except ValueError:
    loguru.logger.error("Invalid number of accounts. Please enter a valid integer.")
    exit()

class RobloxGen:
    def __init__(self):
        self.session = requests.Session()
        self.setup_headers()
        self.load_proxy()
        self.account_passw = self.generate_random_string(12)
        self.capbypass_key = settings_json.get("capbypass_key", "your_capbypass_key")

    def setup_headers(self):
        self.session.headers.update({
            'accept': '*/*',
            'accept-language': 'en-GB,en;q=0.9',
            'cache-control': 'no-cache',
            'origin': 'https://www.roblox.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.roblox.com/',
            'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        })

    def load_proxy(self):
        try:
            with open("proxy.txt", "r") as file:
                proxy_list = file.readlines()
            if not proxy_list:
                loguru.logger.error("proxy.txt is empty, fill it with proxies.")
                exit()
            self.proxy = random.choice(proxy_list).strip()
            self.session.proxies = {
                "http": "http://" + self.proxy,
                "https": "http://" + self.proxy,
            }
        except FileNotFoundError:
            loguru.logger.error("proxy.txt file not found. Please make sure it exists.")
            exit()

    def generate_random_string(self, length):
        return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=length))

    def get_csrf(self):
        response = self.session.get("https://www.roblox.com/home")
        self.csrf_token = response.text.split('"csrf-token" data-token="')[1].split('"')[0]
        self.session.headers["x-csrf-token"] = self.csrf_token

    def get_cookies(self):
        self.session.get('https://www.roblox.com/timg/rbx')
        self.session.cookies.update({"RBXcb": "RBXViralAcquisition=true&RBXSource=true&GoogleAnalytics=true"})
        params = {'name': 'ResourcePerformance_Loaded_funcaptcha_Computer', 'value': '2'}
        self.session.post('https://www.roblox.com/game/report-stats', params=params)

    def generate_birthday(self):
        return datetime(
            random.randint(1990, 2006),
            random.randint(1, 12),
            random.randint(1, 28),
            21,
            tzinfo=timezone.utc,
        ).isoformat(timespec="milliseconds").replace("+00:00", "Z")

    def verify_username(self):
        self.session.headers.update({
            "authority": "auth.roblox.com",
            "accept": "application/json, text/plain, */*"
        })
        self.birthdate = self.generate_birthday()
        nickname = generate_username(1)[0] + str(random.randint(10, 99))
        response = self.session.get(
            f"https://auth.roblox.com/v1/validators/username?Username={nickname}&Birthday={self.birthdate}"
        )
        try:
            self.nickname = random.choice(response.json()["suggestedUsernames"])
        except KeyError:
            self.nickname = nickname

    def signup_request(self):
        json_data = {
            "username": self.nickname,
            "password": self.account_passw,
            "birthday": self.birthdate,
            "gender": 2,
            "isTosAgreementBoxChecked": True,
            "agreementIds": [
                "adf95b84-cd26-4a2e-9960-68183ebd6393",
                "91b2d276-92ca-485f-b50d-c3952804cfd6",
            ],
            "secureAuthenticationIntent": {
                "clientPublicKey": "roblox sucks",
                "clientEpochTimestamp": str(time.time()).split(".")[0],
                "serverNonce": self.serverNonce,
                "saiSignature": "lol",
            },
        }
        return self.session.post("https://auth.roblox.com/v2/signup", json=json_data)

    def solve_captcha(self, captcha_data):
        # Placeholder function for Captcha solving using the capbypass_key
        # Implement your captcha solving logic here
        return "dummy_captcha_solution"

    def generate_account(self):
        self.session.headers["authority"] = "apis.roblox.com"
        response = self.session.get("https://apis.roblox.com/hba-service/v1/getServerNonce")
        self.serverNonce = response.text.split('"')[1]
        self.session.headers["authority"] = "auth.roblox.com"
        response = self.signup_request()

        if "Token Validation Failed" in response.text:
            self.session.headers["x-csrf-token"] = self.session.headers.get("x-csrf-token", "")
            response = self.signup_request()
        if response.status_code == 429:
            loguru.logger.error("IP rate limit, retrying...")
            return ""

        captcha_data = response.headers.get("rblx-challenge-metadata", "")
        captcha_solution = self.solve_captcha(captcha_data)
        if not captcha_solution:
            return ""

        json_data = {
            "challengeId": "dummy_challenge_id",
            "challengeType": "captcha",
            "challengeMetadata": json.dumps({
                "unifiedCaptchaId": "dummy_id",
                "captchaToken": captcha_solution,
                "actionType": "Signup",
            }),
        }
        self.session.post("https://apis.roblox.com/challenge/v1/continue", json=json_data)

        self.session.headers.update({
            "rblx-challenge-id": "dummy_id",
            "rblx-challenge-type": "captcha",
            "rblx-challenge-metadata": base64.b64encode(
                json.dumps({
                    "unifiedCaptchaId": "dummy_id",
                    "captchaToken": captcha_solution,
                    "actionType": "Signup",
                }).encode()
            ).decode()
        })

        resp = self.signup_request()
        try:
            cookie = resp.cookies[".ROBLOSECURITY"]
        except KeyError:
            loguru.logger.error("Captcha solving failed.")
            return ""

        self.userid = resp.json().get("userId", "")
        loguru.logger.info(f"[https://www.roblox.com/users/{self.userid}] Account created!")

        self.get_csrf()
        self.session.headers["authority"] = "accountsettings.roblox.com"

        json_data = {"emailAddress": "example@example.com"}
        response = self.session.post("https://accountsettings.roblox.com/v1/email", json=json_data)
        if response.status_code == 200:
            loguru.logger.info(f"[{self.userid}] Mail set as {self.mail}")

            if settings_json.get("verify_mail", False):
                loguru.logger.info(f"[{self.mail}] Mail verification skipped.")
            else:
                loguru.logger.warning(f"[{self.mail}] Mail verification skipping...")

        else:
            loguru.logger.error(f"[{self.mail}] Can't set mail! {response.text}")

        loguru.logger.success(f"[{self.mail}] Account saved into txt!")
        with open("accgen.txt", "a") as f:
            f.write(f"{self.nickname}:{self.account_passw}:{self.mail}:{self.mailpassword}:{cookie}\n")

def generate():
    while True:
        try:
            gen = RobloxGen()
            gen.get_csrf()
            gen.get_cookies()
            gen.verify_username()
            gen.generate_account()
            break
        except KeyError as E:
            loguru.logger.error(f"{E}, retrying.")
            pass
        except Exception as E:
            loguru.logger.error(E)
            break

def send_to_discord(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(webhook_url, files=files)
    if response.status_code == 204:
        loguru.logger.info("File sent to Discord successfully!")
    else:
        loguru.logger.error(f"Failed to send file to Discord. Status code: {response.status_code}")

with ThreadPoolExecutor(max_workers=settings_json.get("thread_count", 4)) as executor:
    for _ in range(total_generate_count):
        executor.submit(generate)

send_to_discord("accgen.txt")
