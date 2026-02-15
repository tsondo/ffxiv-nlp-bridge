from pydantic import BaseModel


class UserCommand(BaseModel):
    text: str


class MinionCommand(BaseModel):
    task: str
    params: dict = {}


class CommandResponse(BaseModel):
    success: bool
    interpreted_as: str
    command: MinionCommand | None = None
    error: str | None = None
    minion_response: dict | None = None
