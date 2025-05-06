import json
import random

from typing import Optional
from urllib.parse import urlencode, urljoin

from src.logger import CustomLogger
from src.request_client import AsyncHttpClient
from src.web3_client import AsyncWeb3Account
from utils.request_utils import (get_set_login_cookie_headers, get_nonce_headers, parse_url_params,
                                 get_set_join_waiting_list_cookie_headers,
                                 get_set_follow_twitter_cookie_headers,
                                 get_set_write_twitter_handle_cookie_headers,
                                 get_set_get_invite_code_cookie_headers,
                                 get_set_write_invite_code_cookie_headers,
                                 get_set_discord_cookie_headers,
                                 GaCookie)
from utils.web3_utils import create_sign_message

class ChainOperaClient:
    def __init__(
            self,
            private_key: str,
            rpc_url: str,
            explorer_url: str,
            headers: dict,
            logger_id: int,
            proxy_url: Optional[str] = None,
            retry_attempts: int = 3,
            timeout_429: int = 60,
    ):
        self.decimal = 18

        self.http_client = AsyncHttpClient(
            base_url=None,
            proxy=proxy_url,
            retry_attempts=retry_attempts,
            timeout_429=timeout_429,
            _default=headers
        )
        self.web3_account = AsyncWeb3Account(private_key, rpc_url, explorer_url, proxy_url)
        self.proxy_url = proxy_url
        self.wallet_address = self.web3_account.get_wallet_address()
        self.logger = CustomLogger(id=logger_id).get_logger()
        self.ga_cookie = GaCookie()


    async def get_nonce(self, cookie) -> str:
        url = "https://chainopera.ai/userCenter/api/v1/wallet/getSIWEMessage"

        async with self.http_client as client:
            response = await client.post(
                url,
                headers=get_nonce_headers(cookie),
                data=json.dumps({"address": self.wallet_address})
            )
            return response["data"]["nonce"]

    async def login(self) -> None:
        url = "https://chainopera.ai/userCenter/api/v1/wallet/login"

        cookie = self.ga_cookie.generate_ga_cookie()

        nonce = await self.get_nonce(cookie)
        sign_msg = create_sign_message(self.wallet_address, nonce)
        sign_signature = await self.web3_account.sign_mess(sign_msg)

        payload = {
            "address": f"{self.wallet_address}",
            "signature": f"{sign_signature}",
            "messageToSign": f"{sign_msg}"
        }

        async with self.http_client as client:
            resp = await client.post(
                url,
                headers=get_set_login_cookie_headers(self.ga_cookie.generate_ga_cookie(), str(len(json.dumps(payload)))),
                data=json.dumps(payload)
            )
            return resp

    async def join_waiting_list(self, mail: str):
        url = "https://chainopera.ai/userCenter/api/v1/activity/joinTheWaitingList"

        roles = [
            "AI End User",
            "AI Coin Issuers",
            "AI Coin Traders",
            "AI Agent Developers",
            "AI Application Developers",
            "Data Contributors",
            "Data Annotators",
            "Model Developers",
            "GPU Providers"
        ]

        num_roles = random.randint(2, len(roles))
        selected_options = random.sample(roles, num_roles)
        role = ",".join(selected_options)

        payload = {
            "walletId": f"{self.wallet_address}",
            "information": {
                "email": f"{mail}",
                "role": role,
                "privacy": True
            }
        }

        async with self.http_client as client:
            resp = await client.post(
                url,
                headers=get_set_join_waiting_list_cookie_headers(self.ga_cookie.generate_ga_cookie(), str(len(json.dumps(payload)))),
                data=json.dumps(payload)
            )
            return resp

    async def follow_twitter(self) -> None:
        url = f"https://chainopera.ai/userCenter/api/v1/twitter/followTheTeam-v2?walletId={self.wallet_address}"

        async with self.http_client as client:
            resp = await client.get(
                url,
                headers=get_set_follow_twitter_cookie_headers(self.ga_cookie.generate_ga_cookie())
            )
            return resp

    async def write_twitter_handle(self, twitter_handle: str):
        url = "https://chainopera.ai/userCenter/api/v1/twitter/updateXUserName"

        payload = {
            "walletId": f"{self.wallet_address}",
            "userName": f"{twitter_handle}"
        }
        data = json.dumps(payload)

        async with self.http_client as client:
            resp = await client.post(
                url,
                headers=get_set_write_twitter_handle_cookie_headers(self.ga_cookie.generate_ga_cookie(), str(len(data))),
                data=data
            )
            return resp

    async def discord_oauth(self, discord_token: str) -> dict:
        oauth_params = {
            "client_id": "1283243979562811482",
            "response_type": "code",
            "redirect_uri": "https://chainopera.ai/quest",
            "scope": "identify"
        }

        base_url = "https://discord.com/"
        api_authorize_endpoint = "api/v9/oauth2/authorize"

        headers = {
            "Authorization": discord_token
        }

        json_data = {"permissions": 0, "authorize": True}

        authorize_url = (
            urljoin(base_url, api_authorize_endpoint) + "?" + urlencode(oauth_params)
        )

        async with self.http_client as client:
            resp = await client.post(
                authorize_url,
                json=json_data,
                headers=headers
            )

            redirect_url = resp["location"]
            query_params = parse_url_params(redirect_url)

            url = "https://chainopera.ai/userCenter/api/v1/discord/queryInviteUrl-v1"

            payload = {
                "walletId": self.wallet_address,
                "code": query_params["code"]
            }

            response = await client.post(
                url,
                headers=get_set_discord_cookie_headers(self.ga_cookie.generate_ga_cookie(), str(len(json.dumps(payload))), redirect_url),
                data=json.dumps(payload)
            )
            return response

    async def get_invite_code(self) -> str:
        url = "https://chainopera.ai/userCenter/api/v1/activity/inviteNewUser"

        payload = {
            "walletId": self.wallet_address
        }

        async with self.http_client as client:
            response = await client.post(
                url,
                headers=get_set_get_invite_code_cookie_headers(self.ga_cookie.generate_ga_cookie(), str(len(json.dumps(payload)))),
                data=json.dumps(payload)
            )
            invite_code = response["data"]
            return invite_code

    async def write_invite_code(self, invite_code: str) -> None:
        url = "https://chainopera.ai/userCenter/api/v1/activity/enterInviteCode"

        payload = {
            "code": invite_code,
            "walletId": f"{self.wallet_address}"
        }

        async with self.http_client as client:
            resp = await client.post(
                url,
                headers=get_set_write_invite_code_cookie_headers(cookie=self.ga_cookie.generate_ga_cookie(), content_length=str(len(json.dumps(payload)))),
                data=json.dumps(payload)
            )
            return resp
