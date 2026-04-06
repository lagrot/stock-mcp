"""
Test client to debug missing dividends for New Wave Group.
"""
import asyncio
import json


async def run_test():
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

        print("\n--- Testing Stock Analysis (NEWA-B.ST) ---")
        await send({
            "jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {"name": "yahoo_finance_analyze_stock", "arguments": {"symbol": "NEWA-B.ST"}}
        })
        
        res = await receive()
        if "error" in res:
            print(f"Error: {res['error']}")
        else:
            data = json.loads(res["result"]["content"][0]["text"])
            print(f"Symbol: {data['symbol']}")
            # Print the entire dividends object to see exactly what we are getting
            print(f"Dividend Data: {json.dumps(data.get('dividends'), indent=2)}")

    finally:
        process.terminate()
        await process.wait()

if __name__ == "__main__":
    asyncio.run(run_test())
