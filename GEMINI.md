# GEMINI.md - Stock MCP Project Context

This document provides essential context and instructions for AI agents working on the `stock-mcp` project.

## 📈 Project Overview
`stock-mcp` is a local Model Context Protocol (MCP) server that provides real-time stock analysis capabilities. It leverages the Yahoo Finance API (`yfinance`) and includes a local SQLite caching layer.

### Core Features
- **Historical Analysis:** Price trends over configurable periods.
- **Financial Insights:** Income statements and balance sheets.
- **Market Sentiment:** Analyst recommendations and news sentiment.
- **LLM Optimized:** Returns structured summaries designed for AI reasoning.

## 🛠️ Tech Stack
- **Language:** Python 3.10+
- **Environment:** [uv](https://github.com/astral-sh/uv)
- **Data Source:** `yfinance`
- **Caching:** `sqlite3`
- **MCP Framework:** `FastMCP` (via official `mcp` Python SDK)

## 🧱 Architecture
- **`src/data/`**: Data fetching (`yfinance_client.py`) and persistence (`cache.py`).
- **`src/services/`**: Business logic and data analysis (`stock_service.py`).
- **`src/mcp/`**: Standard MCP server implementation (`server.py`) using `FastMCP`.

## ⚙️ Development Guide

### Setup
```bash
uv sync
```

### Running/Registering the Server
The server uses the official MCP Stdio transport.
- **Test locally:** `uv run python -m src.mcp.server`
- **Register with Gemini CLI:** 
  `gemini mcp add stock-analysis "uv run python -m src.mcp.server" --trust -s project`

### Key Conventions
- **Tool Definition:** Tools are defined in `src/mcp/server.py` using the `@mcp.tool()` decorator.
- **Docstrings:** Always provide clear docstrings for tools; `FastMCP` uses these to generate tool descriptions for the LLM.
- **Data Serialization:** Ensure all returned data is JSON-serializable. Use `src.data.yfinance_client._serialize_value` for Pandas/NumPy types.
- **Caching:** Historical data is cached in `cache.db` with a 1-day refresh logic.

## 📊 Available Tools
- `analyze_stock_tool`: Analyzes a stock ticker (e.g., "AAPL"). Supports an optional `period` (e.g., "1mo", "1y").

## ⚠️ Known Limitations
- Caching is currently limited to price history.
- Sentiment analysis is keyword-based.
- Depends on the unofficial `yfinance` API.
