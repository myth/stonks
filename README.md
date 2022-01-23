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

Rename example config file:

```
mv example-config.json config.json
```

Add any additional entries in the config file, and then start the backend:

```
python main.py -c config.json
```

To run with a persitent history database (will write a daily close at `18:00` local time every day), use the `--db` flag:

```
python main.py -c config.json --db "history.db"
```

## Example config file

Format is `name`, `ticker`, `position`, `gav`, `cost`, `ccy`, `asset_type`

`gav` is initial cost per share in asset currency including broker fees, `cost` is initial cost in nok.

```
{
  "positions": [
    {
      "name": "Cash [NOK]",
      "ticker": "CASH_NOK",
      "volume": 10000,
      "price": 1,
      "cost": 10000,
      "currency": "NOK",
      "asset": "CASH"
    },
    {
      "name": "MOWI",
      "ticker": "MOWI_OSE",
      "volume": 10,
      "price": 200,
      "cost": 2000,
      "currency": "NOK",
      "asset": "EQUITY"
    },
    {
      "name": "DNB Teknologi A",
      "ticker": "DI_NOTEC_OSE",
      "volume": 10,
      "price": 2700,
      "cost": 27000,
      "currency": "NOK",
      "asset": "FUND"
    },
    {
      "name": "Lyxor Core MSCI World",
      "ticker": "LCUW.DE",
      "volume": 500,
      "price": 10,
      "cost": 50000,
      "currency": "EUR",
      "asset": "INDEX_ETF"
    }
  ]
}
```

Only `NOK`, `EUR`, `USD` and `SEK` as available currencies.


## Development and extensions

To develop the UI, use `npm start`.
Make sure backend is running (`python3 main.py -c config.json`).

To enable the simulation engine (creates random ticker events against the entries in your portfolio),
start the python application with the `-s` flag. Enable debugging with `-d` flag.