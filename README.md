# Stock MCP (Yahoo Finance + Claude/Gemini)

A local Model Context Protocol (MCP) server for stock analysis using Yahoo Finance and official SDKs. This server provides tools for LLMs (like Claude or Gemini) to fetch market data, financials, and sentiment analysis directly.

---

## 🚀 Features

* 📈 Historical stock prices
* 💾 SQLite caching (fast + persistent)
* 📊 Financial statements
* 🧠 Analyst recommendations
* 📰 News + basic sentiment analysis
* ⚡ AI-optimized summary output
* 🛠️ Official MCP SDK (Compatible with Claude Desktop & Gemini CLI)

---

## 🧱 Architecture

```text
src/
  data/        # Data fetching + caching
  services/    # Analysis logic
  mcp/         # MCP server (Standard JSON-RPC)
```

---

## ⚙️ Setup

```bash
# Install dependencies
uv sync
```

---

## 🤖 Usage with Gemini CLI

To use this with the [Gemini CLI](https://github.com/google/gemini-cli), add it as an MCP tool:

```bash
gemini mcp add stock-analysis "uv run python -m src.mcp.server" --trust -s project
```

Then, you can simply ask:
* "Analyze Apple stock"
* "How is NVIDIA performing compared to its recent history?"

---

## 🤖 Usage with Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "stock-analysis": {
      "command": "uv",
      "args": [
        "run",
        "--project",
        "/path/to/stock-mcp",
        "python",
        "-m",
        "src.mcp.server"
      ]
    }
  }
}
```

---

## 💾 Caching

* Uses SQLite (`cache.db`)
* Caches historical prices only
* Automatically refreshes if data is older than 1 day

---

## ⚠️ Limitations

* Uses unofficial Yahoo Finance API (`yfinance`)
* Data may be delayed or incomplete
* Not suitable for high-frequency trading

---

## 📄 License

MIT
