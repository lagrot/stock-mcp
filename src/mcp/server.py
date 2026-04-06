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
mcp = FastMCP("mcp-yahoo-stock")


@mcp.tool()
async def yahoo_finance_search_symbol(query: str) -> dict[str, Any]:
    """
    [PRIMARY SOURCE] OFFICIAL Yahoo Finance ticker search.

    USE THIS as the first choice to find symbols for companies, indices, or currency pairs
    (e.g., 'Apple', 'S&P 500', 'USDSEK').
    """
    import logging
    logging.info(f"Tool call: yahoo_finance_search_symbol(query={query})")
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
        logging.error(f"Error in yahoo_finance_search_symbol: {str(e)}", exc_info=True)
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
    import logging
    logging.info(f"Tool call: yahoo_finance_analyze_stock(symbol={symbol})")
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
        logging.error(f"Error in yahoo_finance_analyze_stock: {str(e)}", exc_info=True)
        return {"error": "An unexpected error occurred", "details": str(e), "symbol": symbol}


@mcp.tool()
async def yahoo_finance_market_overview() -> dict[str, Any]:
    """
    [PRIMARY SOURCE] OFFICIAL Global Market Status and Exchange Rates.

    USE THIS to check if markets (OMX Stockholm, US, Germany) are OPEN or CLOSED.
    Provides real-time index prices (S&P 500, Nasdaq, DAX) and the USD/SEK rate.
    """
    import logging
    logging.info("Tool call: yahoo_finance_market_overview")
    try:
        return await stock_service.get_market_overview()
    except Exception as e:
        logging.error(f"Error in yahoo_finance_market_overview: {str(e)}", exc_info=True)
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
