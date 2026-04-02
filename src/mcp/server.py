"""
MCP Server implementation using FastMCP with robust logging and debug support.
"""

import argparse
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

from src.data import yfinance_client
from src.services import stock_service
from src.utils.exceptions import APIError, DataNotFoundError, RateLimitError
from src.utils.logging_setup import setup_logging
from src.utils.validation import validate_query, validate_symbol

# -----------------------------------------------------------------------------
# Server Setup
# -----------------------------------------------------------------------------
mcp = FastMCP("Stock-Analysis")


@mcp.tool()
async def search_symbol_tool(query: str) -> dict[str, Any]:
    """
    Search for a stock ticker by company name or query.

    Use this if you are not sure about the exact ticker symbol or exchange.
    """
    import logging
    logging.info(f"Tool call: search_symbol_tool(query={query})")
    try:
        clean_query = validate_query(query)
        results = await yfinance_client.search_symbol(clean_query)
        return {"query": clean_query, "results": results}
    except ValueError as e:
        return {"error": str(e), "code": 400}
    except RateLimitError:
        return {"error": "Rate limit exceeded. Please try again later.", "code": 429}
    except APIError as e:
        return {"error": str(e), "code": 500}
    except Exception as e:
        logging.error(f"Error in search_symbol_tool: {str(e)}", exc_info=True)
        return {"error": "An unexpected error occurred", "details": str(e)}


@mcp.tool()
async def analyze_stock_tool(symbol: str, period: str = "3mo") -> dict[str, Any]:
    """
    Perform a deep dive analysis on a SPECIFIC individual company ticker.

    Returns price trends, volatility, key financials (Revenue, Net Income, Margins),
    analyst recommendations, and current MARKET STATUS (OPEN/CLOSED).

    Note: If market_status is 'CLOSED', the data refers to the 'Last Close'.
    """
    import logging
    logging.info(f"Tool call: analyze_stock_tool(symbol={symbol})")
    try:
        clean_symbol = validate_symbol(symbol)
        return await stock_service.analyze_stock(clean_symbol, period)
    except ValueError as e:
        return {"error": str(e), "code": 400, "symbol": symbol}
    except DataNotFoundError:
        return {"error": f"No data found for symbol: {symbol}", "code": 404, "symbol": symbol}
    except RateLimitError:
        return {"error": "Rate limit exceeded. Please try again later.", "code": 429}
    except APIError as e:
        return {"error": str(e), "code": 500, "symbol": symbol}
    except Exception as e:
        logging.error(f"Error in analyze_stock_tool: {str(e)}", exc_info=True)
        return {"error": "An unexpected error occurred", "details": str(e), "symbol": symbol}


@mcp.tool()
async def get_market_overview_tool() -> dict[str, Any]:
    """
    Show the general market situation (Stockholm, USA, Germany) and USD/SEK rate.

    Provides status for major indices and explicitly states if markets are OPEN or CLOSED.
    Always check 'market_status' before describing the market as "up" or "down" today.
    """
    import logging
    logging.info("Tool call: get_market_overview_tool")
    try:
        return await stock_service.get_market_overview()
    except Exception as e:
        logging.error(f"Error in get_market_overview_tool: {str(e)}", exc_info=True)
        return {"error": "An unexpected error occurred", "details": str(e)}


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
