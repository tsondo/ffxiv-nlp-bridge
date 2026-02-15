# FFXIV NLP Bridge

Natural language command interface for FFXIVMinion bot.

## Architecture

```
[User] -> [Python Service (WSL)] -> [HTTP] -> [Lua HTTP Server (Windows/FFXIVMinion)] -> [FFXIVMinion Tasks]
```

- **Python service** (`python_service/`): FastAPI server that parses English commands via LLM into structured JSON, then forwards to the Lua bridge.
- **Lua bridge** (not yet built): HTTP server running inside FFXIVMinion that receives JSON commands and executes bot tasks.

## Python Service Structure

```
python_service/
├── pyproject.toml
├── .env.example
└── app/
    ├── config.py          # Settings (NLP_BRIDGE_ env prefix), LLM provider selection
    ├── models.py          # Pydantic: UserCommand, MinionCommand, CommandResponse
    ├── llm.py             # LLM backends (Claude, OpenAI-compatible) with shared system prompt
    ├── minion_client.py   # HTTP client forwarding commands to Lua bridge
    ├── main.py            # FastAPI app: POST /command, GET /health
    └── cli.py             # CLI entry point: ffxiv-nlp "command text"
```

## LLM Provider Config

Set `NLP_BRIDGE_LLM_PROVIDER` to `claude` (default, uses Anthropic SDK) or `openai` (any OpenAI-compatible API: vLLM, ollama, llama.cpp, etc.). See `.env.example` for all options.

## Supported Task Types

grind, gather, fate, navigate, duty, craft, stop, status — defined in the LLM system prompt in `llm.py`.

## Current Status

- [x] Python service structure
- [x] LLM parsing with provider selection (Claude / OpenAI-compatible)
- [x] HTTP forwarding to Lua bridge
- [x] CLI entry point
- [ ] Lua HTTP server inside FFXIVMinion
- [ ] Lua command-to-task translation
- [ ] End-to-end testing
