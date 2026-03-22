"""
MCP Server implementation using FastMCP with robust logging and debug support.
"""

import argparse
import logging
import os
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

from src.services import stock_service

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------
LOG_FILE = "mcp_server.log"

def setup_logging(debug: bool = False):
    """Set up file-based logging."""
    level = logging.DEBUG if debug else logging.INFO
    
    if os.path.exists(LOG_FILE):
        try:
            os.remove(LOG_FILE)
        except OSError:
            pass

    logging.basicConfig(
        filename=LOG_FILE,
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    sys.stderr = open(LOG_FILE, "a", buffering=1)
    logging.info("MCP Server starting...")

# -----------------------------------------------------------------------------
# Server Setup
# -----------------------------------------------------------------------------
mcp = FastMCP("Stock-Analysis")

@mcp.tool()
def analyze_stock_tool(symbol: str, period: str = "3mo") -> dict[str, Any]:
    """
    Perform a comprehensive analysis of a stock ticker symbol.
    
    Returns recent price trends, volatility, key financials (Revenue, Net Income, 
    Margins), analyst recommendations, and news sentiment.
    
    Args:
        symbol: The ticker (e.g., 'AAPL', 'NVDA', 'VOLV-B.ST' for Volvo in Sweden).
        period: Time range (e.g., '1mo', '3mo', '1y').
    """
    logging.info(f"Tool call: analyze_stock_tool(symbol={symbol})")
    try:
        return stock_service.analyze_stock(symbol, period)
    except Exception as e:
        logging.error(f"Error in analyze_stock_tool: {str(e)}", exc_info=True)
        return {"error": str(e), "symbol": symbol}


@mcp.tool()
def get_market_overview_tool() -> dict[str, Any]:
    """
    Get a summary of major global indices, including the OMX Stockholm 30 (Sweden).
    
    Use this to get a pulse on the general market sentiment and performance.
    """
    logging.info("Tool call: get_market_overview_tool")
    try:
        return stock_service.get_market_overview()
    except Exception as e:
        logging.error(f"Error in get_market_overview_tool: {str(e)}", exc_info=True)
        return {"error": str(e)}

# -----------------------------------------------------------------------------
# Main Entry Point
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Stock Analysis MCP Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    setup_logging(debug=args.debug)

    try:
        logging.info("Running MCP server on stdio...")
        mcp.run()
    except Exception as e:
        logging.critical(f"Server crashed: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
