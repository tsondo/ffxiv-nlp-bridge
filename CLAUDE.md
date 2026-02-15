# FFXIV NLP Bridge

Natural language command interface for FFXIVMinion bot.

## Architecture

```
[User] → POST /command → [Python Service (WSL)] → LLM parse → queue
                                ↑
[FFXIVMinion Lua Addon] → polls GET /minion/pending every ~2s
                         → executes command
                         → POST /minion/result
```

- **Python service** (`python_service/`): FastAPI server that parses English commands via LLM into structured JSON, queues them for the Lua addon.
- **Lua bridge** (`lua_bridge/`): FFXIVMinion addon that polls the Python service for commands and executes them via the bot's task system.

## Python Service Structure

```
python_service/
├── pyproject.toml
├── .env.example
└── app/
    ├── config.py          # Settings (NLP_BRIDGE_ env prefix), LLM provider selection
    ├── models.py          # Pydantic models for commands, responses, results
    ├── llm.py             # LLM backends (Claude, OpenAI-compatible) with shared system prompt
    ├── command_queue.py   # In-memory command queue (enqueue/dequeue/results)
    ├── main.py            # FastAPI: POST /command, GET /minion/pending, POST /minion/result, GET /minion/status
    └── cli.py             # CLI entry point: ffxiv-nlp "command text"
```

## Lua Addon Structure

```
lua_bridge/
├── module.def          # FFXIVMinion addon manifest
└── nlp_bridge.lua      # Polling loop + task handlers
```

Deploy by copying `lua_bridge/` to `MINIONAPP\Bots\FFXIVMinion64\LuaMods\NLPBridge\`.

## API Endpoints

- `POST /command` — Parse natural language, queue for Lua addon. Returns `{command_id, parsed_command}`.
- `GET /minion/pending` — Lua polls this. Returns next command or 204.
- `POST /minion/result` — Lua reports execution result.
- `GET /minion/status` — Last known bot status from Lua.
- `GET /health` — Service health check.

## LLM Provider Config

Set `NLP_BRIDGE_LLM_PROVIDER` to `claude` (default, uses Anthropic SDK) or `openai` (any OpenAI-compatible API: vLLM, ollama, llama.cpp, etc.). See `.env.example` for all options.

## Supported Task Types

grind, gather, fate, navigate, duty, craft, stop, status — defined in the LLM system prompt in `llm.py`.

## Current Status

- [x] Python service structure
- [x] LLM parsing with provider selection (Claude / OpenAI-compatible)
- [x] Command queue (polling architecture)
- [x] Polling API endpoints
- [x] CLI entry point
- [x] Lua addon with polling loop
- [x] Lua task handlers (grind, gather, fate, navigate, craft, stop, status)
- [ ] Duty finder integration (stub only)
- [ ] End-to-end testing with FFXIVMinion
