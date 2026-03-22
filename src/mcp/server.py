from mcp.server.fastmcp import FastMCP
from src.services.stock_service import analyze_stock

# Initialize FastMCP server
mcp = FastMCP("Stock-MCP")

@mcp.tool()
def analyze_stock_tool(symbol: str, period: str = "3mo") -> dict:
    """
    Analyze a stock symbol for price trends, financials, and sentiment.
    
    Args:
        symbol: The stock ticker symbol (e.g., 'AAPL', 'TSLA').
        period: Historical data period (e.g., '1mo', '3mo', '1y'). Defaults to '3mo'.
    """
    # FastMCP will automatically handle JSON serialization of the returned dict
    return analyze_stock(symbol, period)

if __name__ == "__main__":
    mcp.run()
