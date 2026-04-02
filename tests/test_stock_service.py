import pytest
from src.services import stock_service

def test_extract_financial_metrics_success():
    mock_financials = {
        "income_statement": {
            "2023-12-31": {
                "Total Revenue": 1000,
                "Net Income": 200
            },
            "2022-12-31": {
                "Total Revenue": 800,
                "Net Income": 150
            }
        }
    }
    
    metrics = stock_service._extract_financial_metrics(mock_financials)
    assert metrics["revenue"] == 1000
    assert metrics["net_income"] == 200
    assert metrics["profit_margin_pct"] == 20.0

def test_extract_financial_metrics_empty():
    metrics = stock_service._extract_financial_metrics({})
    assert metrics["revenue"] is None
    assert metrics["net_income"] is None
    assert metrics["profit_margin_pct"] is None

def test_extract_financial_metrics_missing_keys():
    mock_financials = {
        "income_statement": {
            "2023-12-31": {
                "Some Other Key": 1000
            }
        }
    }
    metrics = stock_service._extract_financial_metrics(mock_financials)
    assert metrics["revenue"] is None
    assert metrics["net_income"] is None
