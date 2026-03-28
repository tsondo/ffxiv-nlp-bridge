# FFXIV NLP Bridge

Natural language command interface for FFXIVMinion bot — talk to your character like an NPC companion.

## Vision

The player opens a text box (in-game or external) and types something like:

> "Josephat, go mine ore outside Limsa Lominsa"

The system either executes the request or asks clarifying questions until it knows exactly what to do. The interaction should feel like giving orders to an intelligent companion, not filling out a form.

## Design Principles

1. **Conversational, not transactional.** The LLM maintains context across a session. It can ask follow-up questions, remember what you said earlier, and chain multi-step plans.
2. **Graceful degradation.** If the system can't do something, it says so clearly rather than guessing wrong.
3. **Swappable execution layer.** The Lua side is written so that if a third-party addon API becomes available, we replace our task handlers with API calls to theirs — no changes to the Python service or conversation logic.
4. **Minimal Lua complexity.** Keep the addon thin: receive commands, execute them, report results. All intelligence lives in the Python service / LLM.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  In-Game GUI (Lua)                                  │
│  - Text input box for natural language              │
│  - Chat-style display for responses & clarifications│
│  - Command status indicators                        │
└──────────────┬──────────────────────▲───────────────┘
               │ POST /chat           │ poll GET /chat/response
               ▼                      │
┌─────────────────────────────────────────────────────┐
│  Python Service (FastAPI, runs on WSL/localhost)     │
│                                                     │
│  Conversation Manager                               │
│  - Maintains per-session chat history               │
│  - Routes LLM output: command vs. clarification     │
│                                                     │
│  LLM Layer                                          │
│  - System prompt with FFXIV/Minion knowledge        │
│  - Structured output: command OR question            │
│  - Provider-agnostic (Claude / OpenAI-compat)       │
│                                                     │
│  Command Queue                                      │
│  - Validated commands queued for Lua pickup          │
│  - Multi-step plan support (ordered command chains)  │
│                                                     │
│  Game Knowledge                                     │
│  - Zone/aetheryte mappings                          │
│  - Gathering node locations & types                 │
│  - Task prerequisites & constraints                 │
└──────────────┬──────────────────────▲───────────────┘
               │ GET /minion/pending  │ POST /minion/result
               ▼                      │
┌─────────────────────────────────────────────────────┐
│  Lua Task Handlers                                  │
│  - Execute commands via FFXIVMinion API             │
│  - Report success/failure back to Python service    │
│  - Replaceable with third-party addon API calls     │
└─────────────────────────────────────────────────────┘
```

## Current State

### Working
- Python service structure (FastAPI)
- LLM parsing with provider selection (Claude / OpenAI-compatible)
- Command queue with polling architecture
- Polling API endpoints (pending, result, status)
- CLI entry point
- Lua addon with polling loop
- Lua task handlers (grind, gather, fate, navigate, craft, stop, status)

### Not Yet Built
- Conversational dialogue (clarification/confirmation flow)
- Game knowledge database (recipes, items, zones, aetherytes)
- Character state sync (inventory, levels from Lua → Python)
- Feasibility reasoning ("can I craft this? what's missing?")
- In-game GUI with text input and chat display
- Multi-step command chaining (e.g., teleport → move → gather)
- Session/conversation state management
- Duty finder integration (stub only in Lua)
- End-to-end testing with FFXIVMinion

## Project Structure

```
python_service/
├── pyproject.toml
├── .env.example
└── app/
    ├── config.py          # Settings (NLP_BRIDGE_ env prefix), LLM provider selection
    ├── models.py          # Pydantic models for commands, responses, results
    ├── llm.py             # LLM backends (Claude, OpenAI-compatible) with system prompt
    ├── command_queue.py   # In-memory command queue (enqueue/dequeue/results)
    ├── main.py            # FastAPI endpoints
    ├── cli.py             # CLI entry point
    ├── conversation.py    # (PLANNED) Session manager, chat history, response routing
    ├── game_data.py       # (PLANNED) DB queries: recipes, items, zones, feasibility checks
    └── db.py              # (PLANNED) SQLite connection, schema, migrations

scripts/
├── import_game_data.py    # (PLANNED) Bulk import from XIVAPI / Teamcraft dumps

data/
├── game.db                # (PLANNED) SQLite database for static game data + character state

lua_bridge/
├── module.def             # FFXIVMinion addon manifest
└── nlp_bridge.lua         # Polling loop + task handlers

docs/
├── minionlib.md           # MinionLib Lua API reference
├── argus_docs.md          # Argus drawing/detection library reference
├── gui_api.md             # GUI API reference for in-game UI
└── SPEC.md                # Detailed implementation specification

sample/
└── firstAddon/            # Reference: minimal FFXIVMinion addon with GUI
```

## LLM Provider Config

Set `NLP_BRIDGE_LLM_PROVIDER` to `claude` (default) or `openai` (any OpenAI-compatible API: vLLM, ollama, llama.cpp, etc.). See `.env.example` for all options.

## Supported Task Types

grind, gather, fate, navigate, duty, craft, stop, status — defined in the LLM system prompt in `llm.py`.

## Key Dependencies

- **Python**: FastAPI, Anthropic SDK, OpenAI SDK, httpx, pydantic-settings
- **Lua**: minionlib (FFXIVMinion core), HttpRequest (built-in async HTTP)
- **Docs reference**: `docs/gui_api.md` for in-game UI, `docs/minionlib.md` for core Lua APIs
