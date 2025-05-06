import json
import asyncio

from better_proxy import Proxy
from curl_cffi.requests.errors import RequestsError
from curl_cffi.requests import AsyncSession, HttpMethod


class AsyncHttpClient(AsyncSession):
    DEFAULT_TIMEOUT = 60

    def __init__(
            self,
            _default: dict,
            base_url: str | None = None,
            proxy: str | None = None,
            retry_attempts: int = 2,
            timeout_429: int = 30,
            headers: dict[str, str] | None = None,
            **kwargs,
    ):
        self._default = _default

        if headers:
            self._default.update(headers)

        super().__init__(
            base_url=base_url,
            proxy=proxy,
            verify=False,
            allow_redirects=True,
            trust_env=True,
            **kwargs,
        )
        self.timeout_429 = timeout_429
        self.retry_attempts = retry_attempts
        self._proxy = Proxy.from_str(proxy).as_url if proxy else None

    async def _make_request(
            self,
            url: str,
            method: HttpMethod = "GET",
            return_raw_response: bool = False,
            fetch_response: bool = True,
            retry_429: int | None = None,
            **kwargs,
    ):
        retry_429 = retry_429 or self.retry_attempts

        if 'headers' in kwargs:
            headers = self._default.copy()
            headers.update(kwargs['headers'])
            kwargs['headers'] = headers
        else:
            kwargs['headers'] = self._default.copy()

        try:
            response = await self.request(method, url, **kwargs)
        except RequestsError as e:
            err_msg = str(e)
            if "This may be a libcurl error" in err_msg:
                err_msg = err_msg.split("This may be a libcurl error")[0].strip()
            raise Exception(err_msg) from e

        if response.status_code == 429 and retry_429 > 0:
            await asyncio.sleep(self.timeout_429)
            return await self._make_request(
                url, method, return_raw_response, fetch_response, retry_429=retry_429 - 1, **kwargs
            )

        if response.status_code == 404:
            return {
                "status_code": response.status_code,
                "headers": response.headers,
                "body": response.text,
            }

        if not (200 <= response.status_code < 400):
            raise Exception(f"HTTP Error {response.status_code}: {response.text}")

        if not fetch_response:
            return {"headers": response.headers}

        try:
            return response.json() if not return_raw_response else response
        except json.JSONDecodeError:
            return {"headers": response.headers, "body": response.text}

    async def get(
            self,
            url: str,
            return_raw_response: bool = False,
            fetch_response: bool = True,
            **kwargs,
    ):
        return await self._make_request(
            url,
            method="GET",
            return_raw_response=return_raw_response,
            fetch_response=fetch_response,
            **kwargs,
        )

    async def post(
            self,
            url: str,
            return_raw_response: bool = False,
            fetch_response: bool = True,
            **kwargs,
    ):
        return await self._make_request(
            url,
            method="POST",
            return_raw_response=return_raw_response,
            fetch_response=fetch_response,
            **kwargs,
        )

    async def put(
            self,
            url: str,
            return_raw_response: bool = False,
            fetch_response: bool = True,
            **kwargs,
    ):
        return await self._make_request(
            url,
            method="PUT",
            return_raw_response=return_raw_response,
            fetch_response=fetch_response,
            **kwargs,
        )

    async def patch(
            self,
            url: str,
            return_raw_response: bool = False,
            fetch_response: bool = True,
            **kwargs,
    ):
        return await self._make_request(
            url,
            method="PATCH",
            return_raw_response=return_raw_response,
            fetch_response=fetch_response,
            **kwargs,
        )

    async def delete(
            self,
            url: str,
            return_raw_response: bool = False,
            fetch_response: bool = True,
            **kwargs,
    ):
        return await self._make_request(
            url,
            method="DELETE",
            return_raw_response=return_raw_response,
            fetch_response=fetch_response,
            **kwargs,
        )
