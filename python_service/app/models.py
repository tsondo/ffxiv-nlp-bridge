from pydantic import BaseModel


class UserCommand(BaseModel):
    text: str


class MinionCommand(BaseModel):
    task: str
    params: dict = {}


class CommandResponse(BaseModel):
    success: bool
    interpreted_as: str
    command_id: str | None = None
    command: MinionCommand | None = None
    error: str | None = None


class PendingCommand(BaseModel):
    command_id: str
    task: str
    params: dict = {}


class ResultReport(BaseModel):
    command_id: str
    success: bool
    message: str = ""
    status: dict = {}
