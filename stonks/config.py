"""
Stonks config options
"""

from enum import Enum
from os.path import abspath, dirname, join
from logging import INFO

# General

LOG_LEVEL = INFO
LOG_FORMAT = "%(asctime)s.%(msecs)03d %(levelname)s %(message)s"
LOG_DATEFORMAT = "%Y-%m-%d %H:%M:%S"

# Wait at least N seconds before restarting a task
TASK_RESTART_MIN_WAIT_TIME: int = 10

# Types

class Asset(Enum):
    CASH: str = "Cash"
    EQUITY: str = "Equity"
    UNLISTED_EQUITY: str = "Unlisted Equity"
    FUND: str = "Mutual Fund"
    INDEX_FUND: str = "Index Fund"
    ETF: str = "ETF"
    INDEX_ETF: str = "Index ETF"
    FOREX: str = "Forex"


# Dashboard public root folder
PUB_ROOT = join(dirname(abspath(__file__)), "dashboard", "build")

# Formatting

PRECISION: int = 2

# Portfolio

# Wait 250 ms between processing cycle of the portfolio ticker buffer
PROCESSING_INTERVAL: float = 0.25
# Just some initial values for Forex rates
FOREX = [
    ("SEK", "SEK", 1.0),
    ("EUR", "EUR", 10.0),
    ("USD", "USD", 8.5),
]

# Testing

# Wait maximum N seconds before firing another ticker event
SIMULATOR_MAX_TICKER_INTERVAL: int = 1
