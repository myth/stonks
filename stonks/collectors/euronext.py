"""Euronext Collectors"""

from logging import getLogger

from .base import HTTPClientTask

LOG = getLogger(__name__)


class EuronextFunds(HTTPClientTask):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, name="EuronextFunds", interval=3600, **kwargs)

    async def collect(self):
        LOG.info("[%s] Collecting equity fund market prices", self.name)

        url = "https://www.oslobors.no/ob/servlets/components"
        url += "?type=ranking&source=feed.omff.FUNDS&ranking=%2BSECURITYNAME&limit=2000&offset=0"
        url += "&columns=ITEM%2C+SECURITYNAME%2C+PRICE%2C+TIME%2C&cutoffAtZero=false"
        url += "&channel=5ce3190cd4a87c8aebb2261d88a95c70"
        headers = {"User-Agent": "curl/7.68.0"}

        async with self.session.get(url, headers=headers) as resp:
            self.stats.messages += 1
            updates = []
            data = await resp.json()

            for row in data["rows"]:
                ticker = row["key"]
                if ticker in self.portfolio:
                    nav = row["values"]["PRICE"]
                    updates.append((ticker, nav))

            await self.portfolio.update(updates, initial=self.initial)

        LOG.info("[%s] Equity fund market values collected, sleeping for 1 hour", self.name)


class EuronextForex(HTTPClientTask):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, name="EuronextForex", interval=300, **kwargs)

    async def collect(self):
        LOG.info(f"[{self.name}] Collecting exchange rates")
        url = "https://live.euronext.com/ajax/awlBlockFactory/detailedQuote"
        headers = {"User-Agent": "curl/7.68.0", "Content-Type": "application/x-www-form-urlencoded"}

        payload = [f"isinmicArray%5B%5D={f}NOKFLIT.WFORX" for f in self.portfolio.exchange_rates.rates_by_ticker]
        payload = "&".join(payload)

        async with self.session.post(url, data=payload, headers=headers) as resp:
            data = await resp.json()
            self.stats.messages += 1
            data = data["detailedQuotes"]
            updates = []

            for forex in self.portfolio.exchange_rates.rates_by_ticker:
                last = float(data[f"{forex}NOKFLIT.WFORX"]["lastPrice"])
                updates.append((forex, last))

            await self.portfolio.update(updates, initial=self.initial)

        LOG.info("[%s] Exchange rates collected, sleeping for 5 minutes", self.name)
