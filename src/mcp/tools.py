from src.services.stock_service import analyze_stock


def yahoo_finance_analyze_stock(args: dict):
    symbol = args.get("symbol")
    period = args.get("period", "3mo")

    if not symbol:
        return {"error": "Missing symbol"}

    try:
        data = analyze_stock(symbol, period)
        return {"result": data}
    except Exception as e:
        return {"error": str(e)}
