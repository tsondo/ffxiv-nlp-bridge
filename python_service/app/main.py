import logging

from fastapi import FastAPI, HTTPException

from .llm import parse_command
from .models import CommandResponse, UserCommand

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = FastAPI(title="FFXIV NLP Bridge")


@app.post("/command", response_model=CommandResponse)
async def handle_command(user_cmd: UserCommand):
    log.info("Received: %s", user_cmd.text)

    try:
        command = await parse_command(user_cmd.text)
    except Exception as e:
        log.error("LLM parse failed: %s", e)
        raise HTTPException(status_code=422, detail=f"Failed to parse command: {e}")

    log.info("Parsed: %s", command)

    if command.task == "unknown":
        return CommandResponse(
            success=False,
            interpreted_as="unknown",
            command=command,
            error="Could not interpret as an FFXIV command",
        )

    return CommandResponse(
        success=True,
        interpreted_as=command.task,
        command=command,
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
