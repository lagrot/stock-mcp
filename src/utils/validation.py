"""
Input validation utilities for stock symbols and queries.
"""

import re

# Standard ticker format (e.g., AAPL, TSLA, 005930.KS, NEWA-B.ST)
SYMBOL_REGEX = re.compile(r"^[A-Z0-9\.\-=]{1,15}$")


def validate_symbol(symbol: str) -> str:
    """
    Validate and normalize a stock ticker symbol.

    Returns the uppercase symbol if valid, raises ValueError otherwise.
    """
    if not symbol or not isinstance(symbol, str):
        raise ValueError("Symbol must be a non-empty string.")

    # Normalize
    symbol = symbol.strip().upper()

    if not SYMBOL_REGEX.match(symbol):
        raise ValueError(f"Invalid symbol format: {symbol}")

    return symbol


def validate_query(query: str) -> str:
    """Validate a search query string."""
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string.")

    query = query.strip()
    if len(query) < 1 or len(query) > 100:
        raise ValueError("Query must be between 1 and 100 characters.")

    return query
