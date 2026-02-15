"""In-memory command queue for the polling architecture.

The Lua addon polls GET /minion/pending to dequeue commands,
then reports results via POST /minion/result.
"""

import threading
import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Any


@dataclass
class QueuedCommand:
    command_id: str
    task: str
    params: dict = field(default_factory=dict)


class CommandQueue:
    def __init__(self):
        self._pending: deque[QueuedCommand] = deque()
        self._results: dict[str, dict] = {}
        self._bot_status: dict[str, Any] = {}
        self._lock = threading.Lock()

    def enqueue(self, task: str, params: dict) -> str:
        command_id = uuid.uuid4().hex[:8]
        cmd = QueuedCommand(command_id=command_id, task=task, params=params)
        with self._lock:
            self._pending.append(cmd)
        return command_id

    def dequeue(self) -> QueuedCommand | None:
        with self._lock:
            if self._pending:
                return self._pending.popleft()
            return None

    def report_result(self, command_id: str, result: dict) -> None:
        with self._lock:
            self._results[command_id] = result

    def get_result(self, command_id: str) -> dict | None:
        with self._lock:
            return self._results.get(command_id)

    def update_status(self, status: dict) -> None:
        with self._lock:
            self._bot_status = status

    def get_status(self) -> dict:
        with self._lock:
            return dict(self._bot_status)

    def pending_count(self) -> int:
        with self._lock:
            return len(self._pending)


command_queue = CommandQueue()
