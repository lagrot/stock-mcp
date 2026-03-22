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
  mcp/         # MCP server (Standard JSON-RPC 2.0)
```

---

## ⚙️ Setup

```bash
# Install dependencies
uv sync
```

---

## 🧪 Standalone Testing (WSL / Linux)

### Option A: Automated (Recommended)
Use the included test script which handles the complex MCP handshake automatically:
```bash
uv run python tests/test_mcp_client.py
```

### Option B: Manual (Raw JSON-RPC)
Since we use the official protocol, you must perform a "handshake" before calling tools. Run the server:
`uv run python -m src.mcp.server`

Then, paste these **three messages** in order:

**1. Initialize (The Handshake)**
```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}
```

**2. Initialized Notification**
```json
{"jsonrpc":"2.0","method":"notifications/initialized"}
```

**3. Call the Tool**
```json
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"analyze_stock_tool","arguments":{"symbol":"AAPL"}}}
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

## 💾 Caching & Database

* **SQLite:** This project uses a local SQLite database (`cache.db`) for caching. You **do not** need to install SQLite on your system manually; it is included in the Python standard library.
* **Logic:** Caches historical prices only and refreshes data older than 1 day.

---

## 🛠️ Development

This project uses **Ruff** for linting and formatting.

```bash
# Check for issues
uv run ruff check .

# Fix and format
uv run ruff check --fix .
uv run ruff format .
```

---

## 🩺 Troubleshooting & Logging

This server logs all activity to `mcp_server.log` in the project root. This is the best place to check if the server is failing to connect to your LLM.

### Checking logs in real-time (WSL/Linux):
```bash
tail -f mcp_server.log
```

### Enable Debug Mode
To enable more verbose logging, update your MCP configuration to include the `--debug` flag:

**Gemini CLI:**
```bash
gemini mcp add stock-analysis "uv run python -m src.mcp.server --debug" --trust -s project
```

**Claude Desktop:**
```json
{
  "mcpServers": {
    "stock-analysis": {
      "command": "uv",
      "args": ["run", "--project", "/path/to/stock-mcp", "python", "-m", "src.mcp.server", "--debug"]
    }
  }
}
```

---

## 📄 License

MIT
