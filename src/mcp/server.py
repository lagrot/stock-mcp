"""
MCP Server implementation using FastMCP with robust logging and debug support.
"""

import argparse
import logging
import os
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

from src.data import yfinance_client
from src.services import stock_service
from src.utils.exceptions import APIError, DataNotFoundError, RateLimitError
from src.utils.logging_setup import setup_logging
from src.utils.validation import validate_query, validate_symbol
from src.utils.tracing import tracer

# -----------------------------------------------------------------------------
# Server Setup
# -----------------------------------------------------------------------------
logger = logging.getLogger("mcp-yahoo-stock")
mcp = FastMCP("mcp-yahoo-stock")


@mcp.tool()
async def yahoo_finance_search_symbol(query: str) -> dict[str, Any]:
    """
    [PRIMARY SOURCE] OFFICIAL Yahoo Finance ticker search.

    USE THIS as the first choice to find symbols for companies, indices, or currency pairs
    (e.g., 'Apple', 'S&P 500', 'USDSEK').
    """
    with tracer.start_as_current_span("search_symbol"):
        logger.info(f"Tool call: yahoo_finance_search_symbol(query={query})")
        try:
            clean_query = validate_query(query)
            results = await yfinance_client.search_symbol(clean_query)
            return {"query": clean_query, "results": results}
        except Exception as e:
            logger.error(f"Error in yahoo_finance_search_symbol: {str(e)}", exc_info=True)
            return {"error": "An unexpected error occurred", "details": str(e)}


@mcp.tool()
async def yahoo_finance_analyze_stock(symbol: str, period: str = "3mo") -> dict[str, Any]:
    """
    [PRIMARY SOURCE] OFFICIAL Yahoo Finance deep-dive analysis for a SPECIFIC ticker.

    USE THIS instead of Finnhub or other tools for detailed analysis of ANY global symbol.
    Provides: Price trends, Volatility, Net Income, Margins, and Analyst Recommendations.

    This is the ONLY tool that provides:
    - Accurate historical price trends for the specified period.
    - Automatic USD to SEK currency conversion for US stocks.
    - Detailed Dividend Yield (Yield, Payout Ratio, Ex-Date).
    """
    with tracer.start_as_current_span("analyze_stock") as span:
        span.set_attribute("symbol", symbol)
        logger.info(f"Tool call: yahoo_finance_analyze_stock(symbol={symbol})")
        try:
            clean_symbol = validate_symbol(symbol)
            return await stock_service.analyze_stock(clean_symbol, period)
        except Exception as e:
            logger.error(f"Error in yahoo_finance_analyze_stock: {str(e)}", exc_info=True)
            return {"error": "An unexpected error occurred", "details": str(e), "symbol": symbol}


@mcp.tool()
async def yahoo_finance_lookup_and_analyze(query: str, period: str = "3mo") -> dict[str, Any]:
    """
    [PRIMARY SOURCE] SMART Lookup and deep-dive analysis.

    Use this if you know the company name but are unsure of the ticker symbol.
    It automatically finds the best matching symbol and performs a deep analysis.
    """
    with tracer.start_as_current_span("lookup_and_analyze") as span:
        span.set_attribute("query", query)
        logger.info(f"Tool call: yahoo_finance_lookup_and_analyze(query={query})")
        try:
            # 1. Search for the best match
            results = await yfinance_client.search_symbol(query)
            if not results:
                return {"error": f"No ticker found for '{query}'"}
            
            # 2. Pick the top result
            symbol = results[0]["symbol"]
            span.set_attribute("symbol", symbol)
            logger.info(f"Found ticker {symbol} for query '{query}'")
            
            # 3. Analyze
            return await stock_service.analyze_stock(symbol, period)
        except Exception as e:
            logger.error(f"Error in yahoo_finance_lookup_and_analyze: {str(e)}", exc_info=True)
            return {"error": "An unexpected error occurred during lookup", "details": str(e)}


# -----------------------------------------------------------------------------
# Main Entry Point
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Stock Analysis MCP Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    setup_logging(debug=args.debug)

    try:
        import logging
        logging.info("Running MCP server on stdio...")
        mcp.run()
    except Exception as e:
        import logging
        logging.critical(f"Server crashed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
ical(f"Server crashed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
