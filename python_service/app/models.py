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


