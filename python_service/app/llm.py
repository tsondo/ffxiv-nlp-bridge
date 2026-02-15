import json
from abc import ABC, abstractmethod

import anthropic
from openai import AsyncOpenAI

from .config import LLMProvider, settings
from .models import MinionCommand

SYSTEM_PROMPT = """You are a command parser for FFXIVMinion, a bot for Final Fantasy XIV.
Convert the user's natural language command into a structured JSON command.

Available tasks:
- grind: Kill mobs in current area. Params: target (mob name, optional), duration (minutes, optional)
- gather: Gather resources. Params: node_type (mining/botany/fishing), item (item name, optional)
- fate: Complete FATEs in current area. Params: duration (minutes, optional)
- navigate: Move to a location. Params: destination (area/coords), aetheryte (bool, use teleport)
- duty: Queue/run a duty. Params: duty_name, undersized (bool)
- craft: Craft items. Params: recipe (item name), count (number)
- stop: Stop current task. No params.
- status: Get current bot status. No params.

Respond with ONLY valid JSON: {"task": "task_name", "params": {...}}
If the command is unclear, use your best judgment. If completely unrelated to FFXIV, respond:
{"task": "unknown", "params": {"original": "the user text"}}"""


def _extract_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(raw)


class LLMBackend(ABC):
    @abstractmethod
    async def complete(self, user_text: str) -> MinionCommand: ...


class ClaudeBackend(LLMBackend):
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.llm_api_key or None)

    async def complete(self, user_text: str) -> MinionCommand:
        response = await self.client.messages.create(
            model=settings.resolved_model,
            max_tokens=256,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_text}],
            temperature=0,
        )
        raw = response.content[0].text
        parsed = _extract_json(raw)
        return MinionCommand(task=parsed["task"], params=parsed.get("params", {}))


class OpenAICompatBackend(LLMBackend):
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.llm_api_key or "unused",
            base_url=settings.resolved_base_url,
        )

    async def complete(self, user_text: str) -> MinionCommand:
        response = await self.client.chat.completions.create(
            model=settings.resolved_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            temperature=0,
            max_tokens=256,
        )
        raw = response.choices[0].message.content.strip()
        parsed = _extract_json(raw)
        return MinionCommand(task=parsed["task"], params=parsed.get("params", {}))


_BACKENDS: dict[LLMProvider, type[LLMBackend]] = {
    LLMProvider.CLAUDE: ClaudeBackend,
    LLMProvider.OPENAI_COMPAT: OpenAICompatBackend,
}

_backend: LLMBackend | None = None


def get_backend() -> LLMBackend:
    global _backend
    if _backend is None:
        _backend = _BACKENDS[settings.llm_provider]()
    return _backend


async def parse_command(text: str) -> MinionCommand:
    return await get_backend().complete(text)
