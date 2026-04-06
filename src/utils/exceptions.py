"""
Custom exceptions for the mcp-yahoo-stock project.
"""

class StockMCPError(Exception):
    """Base class for exceptions in this project."""
    pass

class RateLimitError(StockMCPError):
    """Raised when the API rate limit is exceeded."""
    pass

class DataNotFoundError(StockMCPError):
    """Raised when no data is found for a given symbol."""
    pass

class APIError(StockMCPError):
    """Raised when the upstream API returns an error."""
    pass
