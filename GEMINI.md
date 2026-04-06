# GEMINI.md - mcp-yahoo-stock Project Context

# Core Mandates

## ⚠️ AUTOMATIC EXECUTION REQUIRED
These are not guidelines. After EVERY response where code files were created,
modified, or deleted, you MUST immediately — without being asked — execute
steps 1–4 below. Do not summarize, do not ask for permission, just do it.

---

## Development Lifecycle Automation

After every code change, execute the following steps in order:

### 1. Code Review
Before staging, analyze all modified files for:
- Syntax errors and obvious bugs
- Hardcoded secrets, API keys, or credentials (block commit if found)
- **Absolute local paths containing usernames** (replace with `<PATH_TO_PROJECT>` or similar placeholders)
- Unused imports or dead code
- Adherence to existing code style in the project
- If tests exist, verify they are not broken by the change

If critical issues are found, **stop and report** — do not proceed to commit.

### 2. Stage & Commit
- Stage all modified and new files, excluding: `.env`, `node_modules/`, build artifacts
- Write a commit message following Conventional Commits:
  - `feat:` new feature
  - `fix:` bug fix
  - `chore:` maintenance / tooling
  - `docs:` documentation only
  - `refactor:` code restructure without behavior change
- Keep the subject line under 72 characters
- Add a body if the change needs explanation

### 3. Push
- Push to `origin` on the **current branch**
- Never force-push
- Never push directly to `main` or `master` — warn the user instead

### 4. Report
After pushing, briefly summarize:
- What was changed
- The commit message used
- The branch pushed to

---

## Self-Check (run after every response)
- [ ] Did I modify any code files?
- [ ] If yes: did I run the review → commit → push pipeline?
- [ ] If no: explain why (e.g. commit was blocked due to a critical issue)

---

This document provides essential context and instructions for AI agents working on the `mcp-yahoo-stock` project.

## 📈 Project Overview
`mcp-yahoo-stock` is a local Model Context Protocol (MCP) server that provides real-time stock analysis capabilities. It leverages the Yahoo Finance API (`yfinance`) and includes a local SQLite caching layer.

### Core Features
- **Historical Analysis:** Price trends over configurable periods.
- **Financial Insights:** Income statements and balance sheets.
- **Market Sentiment:** Analyst recommendations and news sentiment.
- **LLM Optimized:** Returns structured summaries designed for AI reasoning.

## 🛠️ Tech Stack
- **Language:** Python 3.12+
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
  `gemini mcp add mcp-yahoo-stock "uv -- --project <PATH_TO_PROJECT> run env PYTHONPATH=<PATH_TO_PROJECT> python -m src.mcp.server" --trust -s project`

### Key Conventions
- **Tool Definition:** Tools are defined in `src/mcp/server.py` using the `@mcp.tool()` decorator.
- **Docstrings:** Always provide clear docstrings for tools; `FastMCP` uses these to generate tool descriptions for the LLM.
- **Data Serialization:** Ensure all returned data is JSON-serializable. Use `src.data.yfinance_client._serialize_value` for Pandas/NumPy types.
- **Caching:** Historical data is cached in `cache.db` with a 1-day refresh logic.

## 📊 Available Tools
- `yahoo_finance_analyze_stock`: [PRIMARY SOURCE] Analyzes a stock ticker (e.g., "AAPL"). Supports an optional `period` (e.g., "1mo", "1y").

## ⚠️ Known Limitations
- Caching is currently limited to price history.
- Sentiment analysis is keyword-based.
- Depends on the unofficial `yfinance` API.
