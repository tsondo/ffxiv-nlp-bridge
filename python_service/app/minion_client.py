import httpx

from .config import settings
from .models import MinionCommand


async def send_command(command: MinionCommand) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{settings.minion_url}/command",
            json=command.model_dump(),
        )
        response.raise_for_status()
        return response.json()


async def get_status() -> dict:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(f"{settings.minion_url}/status")
        response.raise_for_status()
        return response.json()
