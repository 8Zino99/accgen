import json
import time
import random
import string
import base64
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

def load_proxy(self):
    global proxy
    try:
        with open("proxy.txt", "r") as file:
            proxy_list = file.readlines()
        if not proxy_list:
            loguru.logger.error("proxy.txt is empty, fill it with proxies.")
            exit()
        proxy = random.choice(proxy_list).strip()
        self.session.proxies = {
            "http": "http://" + proxy,
            "https": "http://" + proxy,
        }
    except FileNotFoundError:
        loguru.logger.error("proxy.txt file not found. Please make sure it exists.")
        exit()

def generate_random_string(length: int) -> str:
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

class RobloxGen:
    def __init__(self):
        self.session = requests.Session()
        self.setup_headers()
        load_proxy(self)
        self.account_passw = generate_random_string(12)
        self.capbypass_key = settings_json.get("capbypass_key", "your_capbypass_key")
        self.captcha_api_key = "71bab0e1aef21a9f100fb9298cc7bd43"  # 2Captcha API key

    def setup_headers(self):
        self.session.headers.update({
            'accept': '*/*',
            'accept-language': 'en-GB,en;q=0.9',
            'cache-control': 'no-cache',
            'origin': 'https://www.roblox.com',
            'pragma': 'no-cache',
            'referer': 'https://www.roblox.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        })

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
        captcha_id = self.start_captcha(captcha_data)
        solution = self.get_captcha_solution(captcha_id)
        return solution

    def start_captcha(self, captcha_data):
        response = requests.post(
            "http://2captcha.com/in.php",
            data={
                "key": self.captcha_api_key,
                "method": "base64",
                "body": captcha_data,
                "json": 1
            }
        )
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 1:
                return result.get('request')
            else:
                loguru.logger.error("Failed to start captcha solving.")
                return ""
        else:
            loguru.logger.error(f"2Captcha request failed with status code: {response.status_code}")
            return ""

    def get_captcha_solution(self, captcha_id):
        while True:
            response = requests.get(
                f"http://2captcha.com/res.php?key={self.captcha_api_key}&action=get&id={captcha_id}&json=1"
            )
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 1:
                    return result.get('request')
                elif result.get('request') == 'CAPCHA_NOT_READY':
                    time.sleep(5)
                else:
                    loguru.logger.error(f"Captcha solving failed with message: {result.get('request')}")
                    return ""
            else:
                loguru.logger.error(f"2Captcha request failed with status code: {response.status_code}")
                return ""

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
                resp = self.session.post("https://accountsettings.roblox.com/v1/email/resend-verification")
                if resp.status_code == 200:
                    loguru.logger.info(f"[{self.userid}] Sent email verification!")
        return self.userid

def send_to_discord(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(webhook_url, files=files)
    if response.status_code == 204:
        loguru.logger.info("File sent to Discord successfully!")
    else:
        loguru.logger.error(f"Failed to send file to Discord. Status code: {response.status_code}")

def generate():
    account = RobloxGen()
    user_id = account.generate_account()
    if user_id:
        with open("accgen.txt", "a") as f:
            f.write(f"{account.nickname}:{account.account_passw}\n")

if __name__ == "__main__":
    settings_json = load_settings()
    webhook_url = input("Enter your Discord webhook URL: ").strip()
    try:
        total_generate_count = int(input("How many accounts do you want to generate? ").strip())
    except ValueError:
        loguru.logger.error("Invalid number of accounts. Please enter a valid integer.")
        exit()

    with ThreadPoolExecutor(max_workers=settings_json.get("thread_count", 4)) as executor:
        for _ in range(total_generate_count):
            executor.submit(generate)

    send_to_discord("accgen.txt")
