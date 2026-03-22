"""
MCP Server implementation using FastMCP.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from src.services.stock_service import analyze_stock

# Initialize FastMCP server with project name
mcp = FastMCP("Stock-Analysis")


@mcp.tool()
def analyze_stock_tool(symbol: str, period: str = "3mo") -> dict[str, Any]:
    """
    Perform a comprehensive analysis of a stock ticker symbol.
    
    Returns recent price trends, volatility, financial statements, analyst 
    recommendations, and basic news sentiment analysis.
    
    Args:
        symbol: The stock ticker symbol to analyze (e.g., 'AAPL', 'TSLA', 'MSFT').
        period: The historical time range to analyze (e.g., '1mo', '3mo', '1y', '5y').
    """
    # FastMCP handles JSON serialization automatically
    try:
        return analyze_stock(symbol, period)
    except Exception as e:
        # Return structured error for the LLM to handle
        return {"error": str(e), "symbol": symbol}


if __name__ == "__main__":
    mcp.run()
