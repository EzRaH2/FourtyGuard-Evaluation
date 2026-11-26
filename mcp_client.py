
import asyncio
import json
import os
import traceback

import httpx
from dotenv import load_dotenv
from mcp.client.streamable_http import streamable_http_client
from mcp.client.session import ClientSession


# ============================================================
# 1. CONFIGURATION
# ============================================================

load_dotenv()

API_KEY = os.getenv("FORTYGUARD_API_KEY")
MCP_URL = "https://tos-mcp.app.fortyguard.com/mcp"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
}

TEST_PARAMETERS = {
    "sat": {
        "latitude": 38.359224,
        "longitude": -81.623467,
    },
    "date_time": {
        "start_date": "2024-07-15",
        "filter_type": 3,
    },
    "granularity": 100,
}

EXPECTED_COST = 14400


# ============================================================
# 2. HELPERS
# ============================================================

def print_result(result):
    if hasattr(result, "model_dump"):
        print(json.dumps(
            result.model_dump(),
            indent=2,
            default=str
        ))
    else:
        print(result)


def check_tool_error(result):
    if getattr(result, "isError", False):
        print("\nWARNING: MCP tool returned an error.")
        print_result(result)
        return True
    return False


# ============================================================
# 3. MAIN
# ============================================================

async def main():

    if not API_KEY:
        print("ERROR: FORTYGUARD_API_KEY was not found.")
        return

    print("=" * 65)
    print("FORTYGUARD - SATELLITE SEGMENTATION TEST")
    print("=" * 65)

    print("\nTEST PARAMETERS:")
    print(json.dumps(TEST_PARAMETERS, indent=2))

    print(f"\nExpected cost: {EXPECTED_COST:,} Credits")

    print("\nThis test will:")
    print("- Segment satellite imagery into land-cover classes")
    print("- Use Charleston, West Virginia coordinates")
    print("- Request imagery for July 15, 2024")
    print("- Use a 100-meter imagery buffer")
    print(f"- Spend approximately {EXPECTED_COST:,} Credits")

    confirmation = input(
        "\nType YES to authorize this specific operation: "
    ).strip()

    if confirmation != "YES":
        print("\nOperation cancelled. No satellite request was sent.")
        return

    print("\nConnecting to FortyGuard MCP...")

    try:
        async with httpx.AsyncClient(
            headers=HEADERS,
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
                    print("Connected successfully.")

                    # Balance before
                    print("\nChecking credit balance BEFORE operation...")

                    balance_before = await session.call_tool(
                        "credit_balance",
                        {}
                    )

                    print("\nBALANCE BEFORE:")
                    print_result(balance_before)

                    if check_tool_error(balance_before):
                        print("Cannot continue: balance check failed.")
                        return

                    # Satellite operation
                    print("\n" + "=" * 65)
                    print("EXECUTING SATELLITE REQUEST")
                    print("=" * 65)

                    result = await session.call_tool(
                        "satellite",
                        TEST_PARAMETERS
                    )

                    print("\nSATELLITE RESULT:")
                    print_result(result)

                    operation_failed = check_tool_error(result)

                    # Balance after
                    print("\nChecking credit balance AFTER operation...")

                    balance_after = await session.call_tool(
                        "credit_balance",
                        {}
                    )

                    print("\nBALANCE AFTER:")
                    print_result(balance_after)

                    # Summary
                    print("\n" + "=" * 65)
                    print("SATELLITE TEST FINISHED")
                    print("=" * 65)

                    print("\nOperation: satellite")
                    print(f"Expected cost: {EXPECTED_COST:,} Credits")

                    if operation_failed:
                        print("Status: Tool returned an error.")
                    else:
                        print("Status: Request completed without MCP tool error.")

                    print("\nSave the output for evaluation_notes.md.")

    except Exception as e:
        print("\nERROR DURING MCP EXECUTION:")
        print(str(e))
        print("\nFULL TRACEBACK:")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
