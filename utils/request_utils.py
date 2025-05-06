from urllib.parse import urlparse, parse_qs
from enum import Enum
from random import choice
import time
import random
import string

class ImpersonateOs(Enum):
    MACOS = "macOS"
    WINDOWS = "Windows"

    @classmethod
    def from_str(cls, s: str) -> 'ImpersonateOs':
        return cls(s)

    def to_str(self) -> str:
        return self.value

    def user_agent_os(self) -> str:
        if self == ImpersonateOs.MACOS:
            return "(Macintosh; Intel Mac OS X 10_15_7)"
        elif self == ImpersonateOs.WINDOWS:
            return "(Windows NT 10.0; Win64; x64)"

    @classmethod
    def random(cls) -> 'ImpersonateOs':
        return choice(list(cls))


class Impersonate(Enum):
    CHROME_120 = "120.0.0.0"
    CHROME_123 = "123.0.0.0"
    CHROME_124 = "124.0.0.0"
    CHROME_126 = "126.0.0.0"
    CHROME_127 = "127.0.0.0"
    CHROME_128 = "128.0.0.0"
    CHROME_129 = "129.0.0.0"
    CHROME_130 = "130.0.0.0"
    CHROME_131 = "131.0.0.0"

    @classmethod
    def from_str(cls, s: str) -> 'Impersonate':
        return cls(s)

    def to_str(self) -> str:
        return self.value

    def ua(self) -> str:
        ua_mapping = {
            Impersonate.CHROME_120: '"Chromium";v="120", "Google Chrome";v="120", "Not?A_Brand";v="99"',
            Impersonate.CHROME_123: '"Google Chrome";v="123", "Not;A=Brand";v="8", "Chromium";v="123"',
            Impersonate.CHROME_124: '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            Impersonate.CHROME_126: '"Chromium";v="126", "Google Chrome";v="126", "Not-A.Brand";v="99"',
            Impersonate.CHROME_127: '"Not/A)Brand";v="8", "Chromium";v="127", "Google Chrome";v="127"',
            Impersonate.CHROME_128: '"Chromium";v="128", "Google Chrome";v="128", "Not?A_Brand";v="99"',
            Impersonate.CHROME_129: '"Google Chrome";v="129", "Chromium";v="129", "Not_A Brand\";v="24"',
            Impersonate.CHROME_130: '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            Impersonate.CHROME_131: '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand\";v="24"'
        }
        return ua_mapping[self]

    def user_agent(self, os: ImpersonateOs) -> str:
        user_agent_os = os.user_agent_os()
        version = self.to_str()
        return f"Mozilla/5.0 {user_agent_os} AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"

    def headers(self, os: ImpersonateOs) -> dict:
        return {
            "User-Agent": self.user_agent(os),
            "sec-ch-ua": self.ua(),
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": f'"{os.to_str()}"'
        }

    @classmethod
    def random(cls) -> 'Impersonate':
        return choice(list(cls))

class GaCookie:
    def __init__(self):
        self._id1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        self._id2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        self.user_id = ''.join(random.choices(string.digits, k=10))
        self.random_counter1 = random.randint(1, 3)
        self.random_counter2 = random.randint(1, 3)

    def _generate_ga_resource_cookie(self):
        timestamp = str(int(time.time()))

        ga_cookie = f"_ga=GA1.1.{self.user_id}.{timestamp}"

        version = "GS1.1"

        ga_resource_cookie = f"{version}.{timestamp}.{self.random_counter1}.{self.random_counter2}.{timestamp}.0.0.0"
        return f"{ga_cookie}; _ga_{self._id1}={ga_resource_cookie}; _ga_{self._id2}={ga_resource_cookie}"

    def generate_ga_cookie(self):
        return self._generate_ga_resource_cookie()

def generate_random_impersonation() -> tuple[ImpersonateOs, Impersonate]:
    random_os = ImpersonateOs.random()
    random_version = Impersonate.random()
    return random_os, random_version

def get_nonce_headers(cookie: str):
    return {
        "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Host": "chainopera.ai",
            "Origin": "https://chainopera.ai",
            "Referer": "https://chainopera.ai/quest/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Cookie": cookie
    }


def parse_url_params(url: str) -> dict:
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return {k: v[0] for k, v in params.items()}


def get_set_login_cookie_headers(cookie: str, length: str) -> dict:
    return {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
        "Connection": "keep-alive",
        "Content-Length": length,
        "Content-Type": "application/json",
        "Host": "chainopera.ai",
        "Origin": "https://chainopera.ai",
        "Referer": "https://chainopera.ai/quest/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cookie": cookie
    }

def get_set_join_waiting_list_cookie_headers(cookie: str, content_length: str) -> dict:
    return {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
        "Connection": "keep-alive",
        "Content-Length": content_length,
        "Content-Type": "application/json",
        "Host": "chainopera.ai",
        "Origin": "https://chainopera.ai",
        "Referer": "https://chainopera.ai/quest/join-waiting-list",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cookie": cookie
    }

def get_set_follow_twitter_cookie_headers(cookie: str) -> dict:
    return {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Host": "chainopera.ai",
        "Referer": "https://chainopera.ai/quest/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cookie": cookie
    }

def get_set_write_twitter_handle_cookie_headers(cookie: str, content_length: str) -> dict:
    return {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
        "Connection": "keep-alive",
        "Content-Length": content_length,
        "Content-Type": "application/json",
        "Host": "chainopera.ai",
        "Origin": "https://chainopera.ai",
        "Referer": "https://chainopera.ai/quest/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cookie": cookie
    }

def get_set_get_invite_code_cookie_headers(cookie: str, content_length: str) -> dict:
    return {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
        "Connection": "keep-alive",
        "Content-Length": content_length,
        "Content-Type": "application/json",
        "Host": "chainopera.ai",
        "Origin": "https://chainopera.ai",
        "Referer": "https://chainopera.ai/quest/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cookie": cookie
    }

def get_set_write_invite_code_cookie_headers(cookie: str, content_length: str) -> dict:
    return {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
        "Connection": "keep-alive",
        "Content-Length": content_length,
        "Content-Type": "application/json",
        "Host": "chainopera.ai",
        "Origin": "https://chainopera.ai",
        "Referer": "https://chainopera.ai/quest/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cookie": cookie
    }

def get_set_discord_cookie_headers(cookie: str, content_length: str, referer: str) -> dict:
    return {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
        "Connection": "keep-alive",
        "Content-Length": content_length,
        "Content-Type": "application/json",
        "Host": "chainopera.ai",
        "Origin": "https://chainopera.ai",
        "Referer": referer,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cookie": cookie
    }