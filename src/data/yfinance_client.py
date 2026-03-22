"""
Yahoo Finance API client with serialization helpers and caching.

This module handles all interactions with the yfinance library and the
local SQLite cache. It provides a clean API for fetching stock data,
financials, and market info, with automatic caching for historical prices.
"""

import datetime
import logging
from typing import Any, Optional

import requests
import yfinance as yf

from src.data.cache import get_cached_history, init_db, save_history

# Constants
SEARCH_URL = "https://query2.finance.yahoo.com/v1/finance/search"
DEFAULT_USER_AGENT = "Mozilla/5.0"
CACHE_VALIDITY_DAYS = 1


# -----------------------------------------------------------------------------
# Serialization Helpers
# -----------------------------------------------------------------------------


def _serialize_value(value: Any) -> Any:
    """
    Convert pandas/numpy types into JSON-safe values.

    This ensures compatibility with the MCP JSON-RPC protocol.
    """
    try:
        # pandas Timestamp → ISO string
        if hasattr(value, "isoformat"):
            return value.isoformat()

        # numpy types → native Python
        if hasattr(value, "item"):
            return value.item()

    except Exception:
        pass

    return value


def _serialize_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Serialize a list of dictionaries for JSON compatibility."""
    return [{k: _serialize_value(v) for k, v in row.items()} for row in records]


def _serialize_dict(data: dict[Any, dict[Any, Any]]) -> dict[str, dict[str, Any]]:
    """
    Serialize nested dictionaries (used for financial statements).

    Handles non-string keys and complex values found in pandas outputs.
    """
    serialized: dict[str, dict[str, Any]] = {}

    for outer_key, inner_dict in data.items():
        safe_outer_key = str(outer_key)
        serialized[safe_outer_key] = {}

        for inner_key, value in inner_dict.items():
            # Convert Timestamp keys → string
            if hasattr(inner_key, "isoformat"):
                safe_inner_key = inner_key.isoformat()
            else:
                safe_inner_key = str(inner_key)
            serialized[safe_outer_key][safe_inner_key] = _serialize_value(value)

    return serialized


# -----------------------------------------------------------------------------
# Core wrapper
# -----------------------------------------------------------------------------


def get_ticker(symbol: str) -> yf.Ticker:
    """Return a yfinance Ticker object for the given symbol."""
    return yf.Ticker(symbol)


# -----------------------------------------------------------------------------
# Data Fetchers
# -----------------------------------------------------------------------------


def get_current_price(symbol: str) -> float:
    """
    Fetch the latest price for a symbol (e.g., 'USDSEK=X').

    Tries 'fast_info' first, falls back to 'history' if needed.
    """
    ticker = get_ticker(symbol)
    try:
        return ticker.fast_info["lastPrice"]
    except Exception:
        df = ticker.history(period="1d")
        if df.empty:
            raise ValueError(f"Could not fetch price for {symbol}")
        return float(df["Close"].iloc[-1])


def get_market_info(symbol: str) -> dict[str, Any]:
    """
    Fetch market state and last trading time for a symbol.

    Returns:
        dict: Contains 'market_state' (OPEN/CLOSED), 'last_trade_time' (ISO),
              and 'currency'.
    """
    ticker = get_ticker(symbol)
    try:
        # ticker.info is more reliable than fast_info for metadata on some systems
        info = ticker.info
        return {
            "market_state": info.get("marketState", "CLOSED"),
            "last_trade_time": info.get("regularMarketTime"),
            "currency": info.get("currency", "USD"),
        }
    except Exception:
        return {"market_state": "CLOSED", "last_trade_time": None, "currency": "USD"}


def get_dividend_data(symbol: str) -> dict[str, Any]:
    """
    Fetch dividend yield, rate, and history for a symbol.

    Returns empty dict if data is unavailable.
    """
    ticker = get_ticker(symbol)
    try:
        info = ticker.info
        return {
            "yield": info.get("dividendYield"),
            "rate": info.get("dividendRate"),
            "payout_ratio": info.get("payoutRatio"),
            "ex_dividend_date": info.get("exDividendDate"),
            "five_year_avg_yield": info.get("fiveYearAvgDividendYield"),
        }
    except Exception:
        return {}


# -----------------------------------------------------------------------------
# Historical Data (with Caching)
# -----------------------------------------------------------------------------


def _is_cache_fresh(last_date_str: str) -> bool:
    """Check if the cached data is fresh enough (less than 1 day old)."""
    try:
        last_date = datetime.datetime.fromisoformat(last_date_str)
        # Compare aware/naive dates safely by making 'now' aware if needed
        now = (
            datetime.datetime.now(last_date.tzinfo)
            if last_date.tzinfo
            else datetime.datetime.now()
        )
        return (now - last_date).days < CACHE_VALIDITY_DAYS
    except (ValueError, TypeError):
        return False


def _get_history_from_cache(symbol: str) -> Optional[list[dict[str, Any]]]:
    """Attempt to retrieve valid historical data from the local cache."""
    cached = get_cached_history(symbol)
    if not cached:
        return None

    last_date_str = cached[-1].get("Date")
    if last_date_str and _is_cache_fresh(last_date_str):
        return cached

    return None


def _fetch_history_from_api(symbol: str, period: str) -> list[dict[str, Any]]:
    """Fetch fresh historical data from Yahoo Finance."""
    ticker = get_ticker(symbol)
    df = ticker.history(period=period)

    if df.empty:
        raise ValueError(f"No historical data available for symbol: {symbol}")

    # Reset index to include 'Date' as a column, then serialize
    records = df.reset_index().to_dict(orient="records")
    return _serialize_records(records)


def get_history(symbol: str, period: str = "3mo") -> list[dict[str, Any]]:
    """
    Fetch historical price data with SQLite caching.

    Orchestrates the cache check and API fetch. Refreshes automatically
    if the cached data is older than 1 day.
    """
    init_db()

    # 1. Try cache
    cached = _get_history_from_cache(symbol)
    if cached:
        return cached

    # 2. Fetch fresh
    records = _fetch_history_from_api(symbol, period)

    # 3. Update cache
    save_history(symbol, records)

    return records


# -----------------------------------------------------------------------------
# Financials & News
# -----------------------------------------------------------------------------


def get_financials(symbol: str) -> dict[str, Any]:
    """
    Fetch income statement and balance sheet data.

    Returns empty dicts if fundamentals are missing (common for indices).
    """
    ticker = get_ticker(symbol)

    try:
        income_stmt = ticker.financials
        balance_sheet = ticker.balance_sheet
    except Exception:
        # Indices and some small caps don't have fundamentals
        return {"income_statement": {}, "balance_sheet": {}}

    return {
        "income_statement": (
            _serialize_dict(income_stmt.to_dict()) if not income_stmt.empty else {}
        ),
        "balance_sheet": (
            _serialize_dict(balance_sheet.to_dict()) if not balance_sheet.empty else {}
        ),
    }


def get_recommendations(symbol: str) -> list[dict[str, Any]]:
    """Fetch recent analyst recommendations (last 10)."""
    ticker = get_ticker(symbol)
    recs = ticker.recommendations

    if recs is None or recs.empty:
        return []

    records = recs.tail(10).reset_index().to_dict(orient="records")
    return _serialize_records(records)


def get_news(symbol: str) -> list[dict[str, Any]]:
    """Fetch recent news articles for the given symbol."""
    ticker = get_ticker(symbol)
    news = ticker.news or []

    return [{k: _serialize_value(v) for k, v in item.items()} for item in news]


# -----------------------------------------------------------------------------
# Search
# -----------------------------------------------------------------------------


def search_symbol(query: str) -> list[dict[str, Any]]:
    """
    Search for a stock ticker by company name or query.

    Uses Yahoo Finance's query API directly.
    """
    try:
        url = f"{SEARCH_URL}?q={query}&quotesCount=5"
        res = requests.get(
            url, headers={"User-Agent": DEFAULT_USER_AGENT}, timeout=10
        )
        res.raise_for_status()
        data = res.json()

        results = []
        for quote in data.get("quotes", []):
            results.append(
                {
                    "symbol": quote.get("symbol"),
                    "name": quote.get("shortname") or quote.get("longname"),
                    "exchange": quote.get("exchange"),
                    "type": quote.get("quoteType"),
                }
            )
        return results
    except Exception as e:
        logging.error(f"Search failed for {query}: {e}")
        return []
