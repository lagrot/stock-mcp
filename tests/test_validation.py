import pytest
from src.utils.validation import validate_symbol, validate_query

def test_validate_symbol_valid():
    assert validate_symbol("aapl") == "AAPL"
    assert validate_symbol("newa-b.st") == "NEWA-B.ST"
    assert validate_symbol("005930.KS") == "005930.KS"
    assert validate_symbol(" TSLA ") == "TSLA"

def test_validate_symbol_invalid():
    with pytest.raises(ValueError, match="Invalid symbol format"):
        validate_symbol("AAPL!")
    with pytest.raises(ValueError, match="Invalid symbol format"):
        validate_symbol("A" * 16)
    with pytest.raises(ValueError, match="Symbol must be a non-empty string"):
        validate_symbol("")
    with pytest.raises(ValueError, match="Symbol must be a non-empty string"):
        validate_symbol(None)

def test_validate_query_valid():
    assert validate_query("Apple Inc") == "Apple Inc"
    assert validate_query("  Microsoft  ") == "Microsoft"

def test_validate_query_invalid():
    with pytest.raises(ValueError, match="Query must be between 1 and 100 characters"):
        validate_query("a" * 101)
    with pytest.raises(ValueError, match="Query must be a non-empty string"):
        validate_query("")
