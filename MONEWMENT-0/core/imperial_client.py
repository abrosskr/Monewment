import os
import httpx
from httpx import HTTPStatusError, RequestError
from core.logger import logger
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

class ZombieFencingError(Exception):
    pass

class ImperialClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ImperialClient, cls).__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        fencing_token = os.getenv("FENCING_TOKEN", "")
        entity_id = os.getenv("ENTITY_ID", "")
        
        headers = {
            "X-Fencing-Token": fencing_token,
            "X-Entity-ID": entity_id
        }
        self.client = httpx.AsyncClient(headers=headers)

    def _check_seppuku(self, response: httpx.Response):
        if response.status_code == 402:
            logger.critical("SEPUKKU INITIATED")
            os._exit(1)
        
        try:
            data = response.json()
            if isinstance(data, dict) and data.get("KILL_ORDER") is True:
                logger.critical("SEPUKKU INITIATED")
                os._exit(1)
        except Exception:
            pass

    def _check_soft_isolation(self, response: httpx.Response):
        if response.status_code in (401, 403, 409):
            raise ZombieFencingError(f"Zombie/Fencing Blocked: HTTP {response.status_code}")

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type((HTTPStatusError, RequestError))
    )
    async def request(self, method: str, url: str, **kwargs):
        response = await self.client.request(method, url, **kwargs)
        
        self._check_seppuku(response)
        self._check_soft_isolation(response)
        
        if response.status_code in (500, 502, 503, 504):
            response.raise_for_status()
            
        return response

    async def get(self, url: str, **kwargs):
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs):
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs):
        return await self.request("PUT", url, **kwargs)

    async def patch(self, url: str, **kwargs):
        return await self.request("PATCH", url, **kwargs)

    async def delete(self, url: str, **kwargs):
        return await self.request("DELETE", url, **kwargs)