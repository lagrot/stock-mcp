import pytest
import datetime
from unittest.mock import MagicMock, patch, AsyncMock
import pandas as pd
from src.data import yfinance_client

@pytest.fixture
def mock_ticker():
    with patch("src.data.yfinance_client.yf.Ticker") as mock:
        yield mock

@pytest.mark.asyncio
async def test_get_current_price_fast_info(mock_ticker):
    # Mock fast_info success
    ticker_inst = mock_ticker.return_value
    ticker_inst.fast_info = {"lastPrice": 150.0}
    
    price = await yfinance_client.get_current_price("AAPL")
    assert price == 150.0

@pytest.mark.asyncio
async def test_get_current_price_fallback_to_history(mock_ticker):
    # Mock fast_info failure and history success
    ticker_inst = mock_ticker.return_value
    ticker_inst.fast_info = {} # Simulate missing key or error
    
    mock_df = pd.DataFrame({"Close": [145.0, 146.0]}, index=[pd.Timestamp.now(), pd.Timestamp.now()])
    ticker_inst.history.return_value = mock_df
    
    price = await yfinance_client.get_current_price("AAPL")
    assert price == 146.0

@pytest.mark.asyncio
async def test_search_symbol_success():
    mock_response = {
        "quotes": [
            {"symbol": "AAPL", "shortname": "Apple Inc.", "exchange": "NMS", "quoteType": "EQUITY"}
        ]
    }
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response,
            raise_for_status=lambda: None
        )
        
        results = await yfinance_client.search_symbol("Apple")
        assert len(results) == 1
        assert results[0]["symbol"] == "AAPL"
        assert results[0]["name"] == "Apple Inc."

@pytest.mark.asyncio
async def test_is_cache_fresh():
    # Fresh cache (within 1 day)
    fresh_date = (datetime.datetime.now() - datetime.timedelta(hours=12)).isoformat()
    assert yfinance_client._is_cache_fresh(fresh_date) is True
    
    # Stale cache (older than 1 day)
    stale_date = (datetime.datetime.now() - datetime.timedelta(days=2)).isoformat()
    assert yfinance_client._is_cache_fresh(stale_date) is False

    # Timezone-aware fresh date
    aware_fresh = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=12)).isoformat()
    assert yfinance_client._is_cache_fresh(aware_fresh) is True

@pytest.mark.asyncio
async def test_get_history_cache_hit():
    symbol = "AAPL"
    mock_cached_data = [{"Date": "2024-01-01", "Close": 150.0}]
    
    with patch("src.data.yfinance_client._get_history_from_cache", new_callable=AsyncMock) as mock_cache:
        mock_cache.return_value = mock_cached_data
        
        # Ensure we don't call the API if cache hits
        with patch("src.data.yfinance_client._fetch_history_from_api") as mock_api:
            history = await yfinance_client.get_history(symbol)
            assert history == mock_cached_data
            mock_api.assert_not_called()

@pytest.mark.asyncio
async def test_get_history_cache_miss_api_success():
    symbol = "AAPL"
    mock_api_data = [{"Date": "2024-01-01", "Close": 150.0}]
    
    with patch("src.data.yfinance_client._get_history_from_cache", new_callable=AsyncMock) as mock_cache:
        mock_cache.return_value = None # Cache miss
        
        with patch("src.data.yfinance_client._fetch_history_from_api", new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_api_data
            
            with patch("src.data.yfinance_client.save_history") as mock_save:
                history = await yfinance_client.get_history(symbol)
                
                assert history == mock_api_data
                mock_api.assert_called_once()
                # Verify it attempted to save to cache
                assert mock_save.called
