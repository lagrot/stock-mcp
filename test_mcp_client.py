"""
Final test client with increased buffer limit for large responses.
"""
import asyncio
import json
import sys

async def run_test():
    # Increase the limit to 1MB to handle large JSON responses from Yahoo Finance
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
        if not line: return None
        return json.loads(line)

    async def log_stderr():
        while True:
            line = await process.stderr.readline()
            if not line: break
            # Only print error-level logs from the server to keep output clean
            msg = line.decode().strip()
            if "ERROR" in msg or "exception" in msg.lower():
                print(f"SERVER_ERR: {msg}", file=sys.stderr)

    stderr_task = asyncio.create_task(log_stderr())

    try:
        print("1. Handshake...", end=" ", flush=True)
        await send({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05", "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        })
        init_res = await receive()
        print(f"OK ({init_res['result']['serverInfo']['name']})")

        await send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})

        print("2. Tool Call (AAPL)...", end=" ", flush=True)
        await send({
            "jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {
                "name": "analyze_stock_tool",
                "arguments": {"symbol": "AAPL", "period": "1mo"}
            }
        })
        
        call_res = await receive()
        if "error" in call_res:
            print(f"FAILED: {call_res['error']}")
        else:
            text = call_res["result"]["content"][0]["text"]
            data = json.loads(text)
            print(f"SUCCESS! Symbol: {data['symbol']}, Price: ${data['summary']['latest_close']}")

    finally:
        process.terminate()
        await process.wait()
        stderr_task.cancel()

if __name__ == "__main__":
    asyncio.run(run_test())
