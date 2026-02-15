"""CLI entry point for quick commands without running the server."""
import argparse
import asyncio
import json
import sys

import httpx


def main():
    parser = argparse.ArgumentParser(description="FFXIV NLP Bridge CLI")
    parser.add_argument("command", nargs="*", help="Natural language command")
    parser.add_argument(
        "--server", default="http://localhost:8000", help="Bridge server URL"
    )
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    text = " ".join(args.command)
    asyncio.run(send(text, args.server))


async def send(text: str, server: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(f"{server}/command", json={"text": text})
        data = resp.json()

    print(json.dumps(data, indent=2))
    if not data.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
