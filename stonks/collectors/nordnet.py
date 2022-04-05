"""NordNet Collectors"""

from asyncio import sleep
from datetime import timedelta
from logging import getLogger

from .base import HTTPClientTask

LOG = getLogger(__name__)


class NordNetFunds(HTTPClientTask):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, name="NordNetFunds", interval=3600, **kwargs)

    async def collect(self):
        LOG.info("[%s] Collecting equity fund market prices", self.name)

        data_url = "https://www.nordnet.no/api/2/instrument_search/query/fundlist"
        login_url = "https://www.nordnet.no/api/2/login"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "client-id": "NEXT",
            "Connection": "keep-alive",
            "Host": "www.nordnet.no",
            "Referer": "https://www.nordnet.no/",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
        }

        # Get NextJS cookies
        async with self.session.get("https://www.nordnet.no/") as resp:
            resp.raise_for_status()
        # Do NextJS login GET
        async with self.session.get(login_url, headers=headers) as resp:
            resp.raise_for_status()
        # Actually start fetching data
        for p in self.portfolio.positions.values():
            if p.collector != "nordnet":
                continue

            instrument_uri = f"{data_url}?apply_filters=instrument_id={p.ticker}"
            async with self.session.get(instrument_uri, headers=headers) as resp:
                self.stats.messages += 1
                data = await resp.json()
                if data and data["results"]:
                    nav = data["results"][0]["price_info"]["last"]["price"]
                    await self.portfolio.update((p.ticker, nav), initial=self.initial)
                await sleep(0.5)

        LOG.info("[%s] Equity fund market values collected, sleeping for %s", self.name, timedelta(seconds=self.interval))
