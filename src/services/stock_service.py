"""
Core business logic for stock analysis.
"""

from typing import Any

from src.data import yfinance_client as yf_client


def analyze_stock(symbol: str, period: str = "3mo") -> dict[str, Any]:
    """
    Perform a comprehensive analysis of a stock symbol.
    
    Returns a structured summary designed for LLM consumption.
    """
    history = yf_client.get_history(symbol, period)
    financials = yf_client.get_financials(symbol)
    recommendations = yf_client.get_recommendations(symbol)
    news = yf_client.get_news(symbol)

    # Extract price and volume data
    closes = [row["Close"] for row in history if "Close" in row]
    volumes = [row.get("Volume", 0) for row in history]

    if not closes:
        raise ValueError(f"No price data available for {symbol}")

    latest_close = closes[-1]
    first_close = closes[0]

    # --- Calculations ---
    price_change = latest_close - first_close
    price_change_pct = (price_change / first_close) * 100
    trend = "up" if price_change > 0 else "down"
    avg_volume = sum(volumes) / len(volumes) if volumes else 0

    # Volatility (Average daily absolute return)
    returns = []
    for i in range(1, len(closes)):
        prev, curr = closes[i - 1], closes[i]
        returns.append((curr - prev) / prev)
    volatility = sum(abs(r) for r in returns) / len(returns) if returns else 0

    # --- Sentiment Analysis (Basic) ---
    positive_keywords = {"gain", "growth", "beat", "strong", "upgrade", "success"}
    negative_keywords = {"loss", "drop", "weak", "downgrade", "miss", "failure"}

    sentiment_score = 0
    for article in news:
        title = article.get("title", "").lower()
        if any(k in title for k in positive_keywords):
            sentiment_score += 1
        if any(k in title for k in negative_keywords):
            sentiment_score -= 1

    news_sentiment = (
        "positive" if sentiment_score > 0 else "negative" if sentiment_score < 0 else "neutral"
    )

    analyst_summary = {
        "total_recommendations": len(recommendations),
        "recent": recommendations[:3],
    }

    return {
        "symbol": symbol.upper(),
        "summary": {
            "latest_close": round(latest_close, 2),
            "price_change": round(price_change, 2),
            "price_change_percent": round(price_change_pct, 2),
            "trend": trend,
            "average_volume": int(avg_volume),
            "volatility_score": round(volatility, 4),
            "news_sentiment": news_sentiment,
        },
        "history_tail": history[-10:],
        "analyst_summary": analyst_summary,
        "top_news": news[:5],
        "financials": financials,
    }
