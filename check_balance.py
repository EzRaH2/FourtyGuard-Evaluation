
import asyncio
import os
import json

import httpx
from dotenv import load_dotenv
from mcp.client.streamable_http import streamable_http_client
from mcp.client.session import ClientSession

load_dotenv()

API_KEY = os.getenv("FORTYGUARD_API_KEY")
MCP_URL = "https://tos-mcp.app.fortyguard.com/mcp"

async def main():

    if not API_KEY:
        print("ERROR: API key not found.")
        return

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    async with httpx.AsyncClient(
        headers=headers,
        timeout=httpx.Timeout(30, read=300)
    ) as http_client:

        async with streamable_http_client(
            MCP_URL,
            http_client=http_client
        ) as (read_stream, write_stream):

            async with ClientSession(
                read_stream,
                write_stream
            ) as session:

                await session.initialize()

                result = await session.call_tool(
                    "credit_balance",
                    {}
                )

                print("\nCURRENT CREDIT BALANCE")
                print("=" * 50)

                if hasattr(result, "model_dump"):
                    print(json.dumps(
                        result.model_dump(),
                        indent=2,
                        default=str
                    ))
                else:
                    print(result)

if __name__ == "__main__":
    asyncio.run(main())
