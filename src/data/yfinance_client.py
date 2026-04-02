"""
Yahoo Finance API client with serialization helpers and caching.

This module handles all interactions with the yfinance library and the
local SQLite cache. It provides a clean API for fetching stock data,
financials, and market info, with automatic caching for historical prices.
"""

import asyncio
import datetime
import logging
from typing import Any

import httpx
import yfinance as yf

from src.data.cache import get_cached_history, init_db, save_history
from src.utils.exceptions import APIError, DataNotFoundError, RateLimitError
from src.utils.serialization import serialize_dict, serialize_records, serialize_value

# Constants
SEARCH_URL = "https://query2.finance.yahoo.com/v1/finance/search"
DEFAULT_USER_AGENT = "Mozilla/5.0"
CACHE_VALIDITY_DAYS = 1


# -----------------------------------------------------------------------------
# Core wrapper
# -----------------------------------------------------------------------------


def get_ticker(symbol: str) -> yf.Ticker:
    """Return a yfinance Ticker object for the given symbol."""
    return yf.Ticker(symbol)


# -----------------------------------------------------------------------------
# Data Fetchers
# -----------------------------------------------------------------------------


async def get_current_price(symbol: str) -> float:
    """
    Fetch the latest price for a symbol (e.g., 'USDSEK=X').

    Tries 'fast_info' first, falls back to 'history' if needed.
    """
    ticker = get_ticker(symbol)
    try:
        return ticker.fast_info["lastPrice"]
    except Exception as e:
        df = await asyncio.to_thread(ticker.history, period="1d")
        if df.empty:
            raise DataNotFoundError(f"Could not fetch price for {symbol}") from e
        return float(df["Close"].iloc[-1])


async def get_market_info(symbol: str) -> dict[str, Any]:
    """
    Fetch market state and last trading time for a symbol.
    """
    ticker = get_ticker(symbol)
    try:
        # ticker.info is more reliable than fast_info for metadata on some systems
        info = await asyncio.to_thread(lambda: ticker.info)
        return {
            "market_state": info.get("marketState", "CLOSED"),
            "last_trade_time": info.get("regularMarketTime"),
            "currency": info.get("currency", "USD"),
        }
    except Exception:
        return {"market_state": "CLOSED", "last_trade_time": None, "currency": "USD"}


async def get_dividend_data(symbol: str) -> dict[str, Any]:
    """
    Fetch dividend yield, rate, and history for a symbol.
    """
    ticker = get_ticker(symbol)
    try:
        info = await asyncio.to_thread(lambda: ticker.info)
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
        # Compare aware/naive dates safely
        if last_date.tzinfo:
            now = datetime.datetime.now(datetime.timezone.utc)
            # Ensure last_date is also UTC for comparison if it has tzinfo
            last_date = last_date.astimezone(datetime.timezone.utc)
        else:
            now = datetime.datetime.now()
        
        return (now - last_date).days < CACHE_VALIDITY_DAYS
    except (ValueError, TypeError):
        return False


async def _get_history_from_cache(symbol: str) -> list[dict[str, Any]] | None:
    """Attempt to retrieve valid historical data from the local cache."""
    cached = await asyncio.to_thread(get_cached_history, symbol)
    if not cached:
        return None

    last_date_str = cached[-1].get("Date")
    if last_date_str and _is_cache_fresh(last_date_str):
        return cached

    return None


async def _fetch_history_from_api(symbol: str, period: str) -> list[dict[str, Any]]:
    """Fetch fresh historical data from Yahoo Finance."""
    ticker = get_ticker(symbol)
    try:
        df = await asyncio.to_thread(ticker.history, period=period)
    except Exception as e:
        raise APIError(f"Failed to fetch data from Yahoo Finance: {e}")

    if df.empty:
        raise DataNotFoundError(f"No historical data available for symbol: {symbol}")

    # Reset index to include 'Date' as a column, then serialize
    records = df.reset_index().to_dict(orient="records")
    return serialize_records(records)


async def get_history(symbol: str, period: str = "3mo") -> list[dict[str, Any]]:
    """
    Fetch historical price data with SQLite caching.
    """
    await asyncio.to_thread(init_db)

    # 1. Try cache
    cached = await _get_history_from_cache(symbol)
    if cached:
        return cached

    # 2. Fetch fresh
    records = await _fetch_history_from_api(symbol, period)

    # 3. Update cache
    await asyncio.to_thread(save_history, symbol, records)

    return records


# -----------------------------------------------------------------------------
# Financials & News
# -----------------------------------------------------------------------------


async def get_financials(symbol: str) -> dict[str, Any]:
    """
    Fetch income statement and balance sheet data.
    """
    ticker = get_ticker(symbol)

    try:
        income_stmt = await asyncio.to_thread(lambda: ticker.financials)
        balance_sheet = await asyncio.to_thread(lambda: ticker.balance_sheet)
    except Exception:
        return {"income_statement": {}, "balance_sheet": {}}

    return {
        "income_statement": (
            serialize_dict(income_stmt.to_dict()) if not income_stmt.empty else {}
        ),
        "balance_sheet": (
            serialize_dict(balance_sheet.to_dict()) if not balance_sheet.empty else {}
        ),
    }


async def get_recommendations(symbol: str) -> list[dict[str, Any]]:
    """Fetch recent analyst recommendations (last 10)."""
    ticker = get_ticker(symbol)
    recs = await asyncio.to_thread(lambda: ticker.recommendations)

    if recs is None or recs.empty:
        return []

    records = recs.tail(10).reset_index().to_dict(orient="records")
    return serialize_records(records)


async def get_news(symbol: str) -> list[dict[str, Any]]:
    """Fetch recent news articles for the given symbol."""
    ticker = get_ticker(symbol)
    news = await asyncio.to_thread(lambda: ticker.news or [])

    return [{k: serialize_value(v) for k, v in item.items()} for item in news]


# -----------------------------------------------------------------------------
# Search
# -----------------------------------------------------------------------------


async def search_symbol(query: str) -> list[dict[str, Any]]:
    """
    Search for a stock ticker by company name or query.

    Uses Yahoo Finance's query API directly.
    """
    try:
        params = {"q": query, "quotesCount": 5}
        async with httpx.AsyncClient() as client:
            res = await client.get(
                SEARCH_URL,
                params=params,
                headers={"User-Agent": DEFAULT_USER_AGENT},
                timeout=10
            )
            if res.status_code == 429:
                raise RateLimitError("Rate limit exceeded for search API")
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
    except RateLimitError:
        raise
    except Exception as e:
        raise APIError(f"Search failed for {query}: {e}")

