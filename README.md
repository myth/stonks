Stonks
====

Live portfolio dashboard for my equities, mutual funds and ETFs. Spare time project that polls various sites
or connects via WebSockets to show a merged view of my assets from different platforms.

<p align="center">
  <img src="https://i.imgur.com/7jfOFcJ.png" />
</p>

Uses Finansavisen, EuroNext, and YahooFinance as collectors. Finansavisen collector connects via WebSockets
and consumes ticker information with 15min delay and realtime OSEBX index data. EuroNext has two collectors,
one for forex and one for mutual funds. Mutual funds are only settled one per day, so it has a 1 hour polling interval

<p align="center">
  <img src="https://i.imgur.com/y9wrF8l.png" />
</p>

## Install

Dashboard requires NodeJS and npm/yarn.

### Backend

Install using poetry

```
poetry shell
poetry update
```

Install using pip

```
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```

### Dashboard

```
cd stonks/dashboard
npm i
npm run build
```

## Run

```
python main.py -c config.json
```

## Example config file

Format is `name`, `ticker`, `position`, `gav`, `cost`, `ccy`, `asset_type`

`gav` is initial cost per share in asset currency including broker fees, `cost` is initial cost in nok.

```
{
  "positions": [
    ["Cash [NOK]", "CASH_NOK", 1000, 1, 1000, "NOK", "CASH"],
    ["MOWI", "MOWI_OSE", 10, 250, 2500, "NOK", "EQUITY"],
    ["DNB Teknologi A", "DI_NOTEC_OSE", 10, 2000, 20000, "NOK", "FUND"],
    ["Lyxor Core MSCI World", "LCUW.DE", 100, 13, 13000, "EUR", "INDEX_ETF"],
    ["iShares Core S&P 500", "SXR8.DE", 10, 350, 35000, "EUR", "INDEX_ETF"]
  ]
}
```

Only `NOK`, `EUR`, `USD` and `SEK` as available currencies.


## Development and extensions

To develop the UI, use `npm start`.
Make sure backend is running (`python3 main.py -c config.json`).

To enable the simulation engine (creates random ticker events against the entries in your portfolio),
start the python application with the `-s` flag. Enable debugging with `-d` flag.