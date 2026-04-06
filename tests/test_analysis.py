import asyncio
import json
import pytest

@pytest.mark.asyncio
async def test_analyze_stock_tool():
    limit = 1024 * 1024
    process = await asyncio.create_subprocess_exec(
        "uv", "run", "python", "-m", "src.mcp.server",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        limit=limit
    )

    async def send(msg):
        process.stdin.write(json.dumps(msg).encode() + b"\n")
        await process.stdin.drain()

    async def receive():
        line = await process.stdout.readline()
        if not line:
            return None
        return json.loads(line)

    try:
        # Handshake
        await send({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0.0"},
            },
        })
        await receive()
        await send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})

        # Call Tool
        await send({
            "jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {"name": "yahoo_finance_analyze_stock", "arguments": {"symbol": "AAPL"}}
        })
        res = await receive()
        
        assert "result" in res
        data = json.loads(res["result"]["content"][0]["text"])
        assert "symbol" in data
        assert data["symbol"] == "AAPL"
        
    finally:
        process.terminate()
        await process.wait()
