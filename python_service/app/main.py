import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from .command_queue import command_queue
from .llm import parse_command
from .models import (
    CommandResponse,
    PendingCommand,
    ResultReport,
    UserCommand,
)

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

    command_id = command_queue.enqueue(command.task, command.params)
    log.info("Queued command %s: %s", command_id, command.task)

    return CommandResponse(
        success=True,
        interpreted_as=command.task,
        command_id=command_id,
        command=command,
    )


@app.get("/minion/pending")
async def get_pending():
    """Lua addon polls this to get the next queued command."""
    cmd = command_queue.dequeue()
    if cmd is None:
        return JSONResponse(status_code=204, content=None)
    log.info("Dispatching command %s: %s", cmd.command_id, cmd.task)
    return PendingCommand(
        command_id=cmd.command_id,
        task=cmd.task,
        params=cmd.params,
    )


@app.post("/minion/result")
async def report_result(report: ResultReport):
    """Lua addon reports execution results here."""
    log.info("Result for %s: success=%s %s", report.command_id, report.success, report.message)
    command_queue.report_result(report.command_id, report.model_dump())
    if report.status:
        command_queue.update_status(report.status)
    return {"ok": True}


@app.get("/minion/status")
async def get_status():
    """Returns the last known bot status reported by the Lua addon."""
    status = command_queue.get_status()
    status["pending_commands"] = command_queue.pending_count()
    return status


@app.get("/health")
async def health():
    return {"status": "ok"}
