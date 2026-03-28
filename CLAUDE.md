# FFXIV NLP Bridge

Natural language command interface for FFXIVMinion bot — talk to your character like an NPC companion.

## Vision

The player opens a text box (in-game or external) and types something like:

> "Josephat, go mine ore outside Limsa Lominsa"

The system either executes the request or asks clarifying questions until it knows exactly what to do. The interaction should feel like giving orders to an intelligent companion, not filling out a form.

## Design Principles

1. **Conversational, not transactional.** The LLM maintains context across a session. It can ask follow-up questions, remember what you said earlier, and chain multi-step plans.
2. **Graceful degradation.** If the system can't do something, it says so clearly rather than guessing wrong.
3. **Build on LuaComm, don't reinvent it.** Multi-agent communication, relay infrastructure, agent registration, heartbeats, and message routing are handled by LuaComm. We are a consumer of that system, not a replacement.
4. **Minimal Lua complexity.** Keep the addon thin: register LuaComm handlers for each task type, execute commands via the FFXIVMinion API, report results back. All intelligence lives in the Python service / LLM.
5. **Swappable execution layer.** Task handlers are isolated so that if a third-party addon API becomes available, we replace our handlers with API calls to theirs — no changes to the Python service, conversation logic, or relay infrastructure.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  In-Game GUI (Lua)                                  │
│  - Text input box for natural language              │
│  - Chat-style display for responses & clarifications│
│  - Command status indicators                        │
└──────────────┬──────────────────────────────────────┘
               │ POST /chat (via LuaComm relay or direct)
               ▼
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
│  Relay Client                                       │
│  - Registered as "commander" agent on LuaComm relay │
│  - Sends parsed commands via POST /api/send         │
│  - Receives results back via LuaComm messaging      │
│                                                     │
│  Game Knowledge                                     │
│  - Zone/aetheryte mappings                          │
│  - Gathering node locations & types                 │
│  - Task prerequisites & constraints                 │
└──────────────┬──────────────────────────────────────┘
               │ POST /api/send (to relay)
               ▼
┌─────────────────────────────────────────────────────┐
│  LuaComm Relay (PowerShell, runs on LAN)            │
│  - Agent registration & heartbeats                  │
│  - Per-agent command queues                         │
│  - Broadcast / role-based / targeted routing        │
│  - Agent discovery (who's online, roles)            │
│  (Maintained by friend — treat as external dep)     │
└──────────────┬──────────────────────────────────────┘
               │ GET /api/recv/<name> (agents poll)
               ▼
┌─────────────────────────────────────────────────────┐
│  Lua Agents (one per toon, runs in FFXIVMinion)     │
│  - LuaComm client: register, poll, heartbeat        │
│  - LuaComm:on() handlers for each task type         │
│  - Execute commands via FFXIVMinion API             │
│  - Send results back via LuaComm:send()             │
│  - Replaceable with third-party addon API calls     │
└─────────────────────────────────────────────────────┘
```

### What LuaComm provides (external dependency)

- **relay.ps1** — PowerShell HTTP relay server with agent registration, heartbeats, message queuing, broadcast/role-based routing
- **luacomm.lua** — Lua client library with JSON encode/decode, HTTP polling, callback-based command dispatch (`LuaComm:on()`), agent discovery
- **LuaCommander** — Delphi desktop GUI for monitoring agents, sending commands, remote code execution (optional, for debugging)
- **examples/** — Reference agent and commander scripts

We do not modify LuaComm code. If bugs exist there, the friend fixes them. We code against its API as documented.

## Current State

### Working
- Python service structure (FastAPI)
- LLM parsing with provider selection (Claude / OpenAI-compatible)
- CLI entry point (`ffxiv-nlp "command text"`)

### Deprecated (replaced by LuaComm)
- `command_queue.py` — replaced by LuaComm relay's per-agent queues
- `/minion/pending`, `/minion/result`, `/minion/status` endpoints — replaced by relay communication
- `nlp_bridge.lua` polling loop and HTTP helpers — replaced by LuaComm client

### Not Yet Built
- Relay client in Python service (register as commander, send commands via `/api/send`, poll for results)
- Lua agent addon using LuaComm (task handlers registered with `LuaComm:on()`)
- Conversational dialogue (clarification/confirmation flow via `/chat` endpoint)
- Game knowledge database (recipes, items, zones, aetherytes)
- Character state sync (inventory, levels reported via LuaComm messages)
- Feasibility reasoning ("can I craft this? what's missing?")
- In-game GUI with text input and chat display
- Multi-step command chaining (e.g., teleport → move → gather)
- Session/conversation state management
- Multi-agent coordination (send different tasks to different toons by role)

## Project Structure

```
python_service/
├── pyproject.toml
├── .env.example
└── app/
    ├── config.py          # Settings (NLP_BRIDGE_ env prefix), LLM provider selection
    ├── models.py          # Pydantic models for commands, responses, results
    ├── llm.py             # LLM backends (Claude, OpenAI-compatible) with system prompt
    ├── relay_client.py    # (NEW) HTTP client for LuaComm relay: register, send, poll, heartbeat
    ├── main.py            # FastAPI: POST /chat, POST /command (compat), GET /health
    ├── cli.py             # CLI entry point
    ├── conversation.py    # (PLANNED) Session manager, chat history, response routing
    ├── game_data.py       # (PLANNED) DB queries: recipes, items, zones, feasibility checks
    └── db.py              # (PLANNED) SQLite connection, schema, migrations

lua/                       # LuaComm library (external, do not modify)
├── luacomm.lua

relay/                     # LuaComm relay server (external, do not modify)
├── relay.ps1
├── start_relay.bat

LuaCommander/              # Delphi desktop GUI (external, do not modify)
├── ...

examples/                  # LuaComm example scripts (external, reference only)
├── agent.lua
├── commander.lua

lua_bridge/                # Our FFXIVMinion addon (uses LuaComm)
├── module.def             # FFXIVMinion addon manifest
└── nlp_agent.lua          # LuaComm agent + task handlers

docs/
├── minionlib.md           # MinionLib Lua API reference
├── argus_docs.md          # Argus drawing/detection library reference
├── gui_api.md             # GUI API reference for in-game UI
└── SPEC.md                # Detailed implementation specification

scripts/
├── import_game_data.py    # (PLANNED) Bulk import from XIVAPI / Teamcraft dumps

data/
├── game.db                # (PLANNED) SQLite database

sample/
└── firstAddon/            # Reference: minimal FFXIVMinion addon with GUI
```

## LLM Provider Config

Set `NLP_BRIDGE_LLM_PROVIDER` to `claude` (default) or `openai` (any OpenAI-compatible API: vLLM, ollama, llama.cpp, etc.). See `.env.example` for all options.

## LuaComm Relay Config

The Python service needs to know the relay server address to send commands. Set via environment:
```
NLP_BRIDGE_RELAY_HOST=192.168.1.100
NLP_BRIDGE_RELAY_PORT=19850
NLP_BRIDGE_COMMANDER_NAME=NLPBridge
```

## Supported Task Types

grind, gather, fate, navigate, duty, craft, stop, status — defined in the LLM system prompt in `llm.py`.

## Multi-Agent Targeting

Because LuaComm supports targeted, role-based, and broadcast messaging, the NLP layer can dispatch commands to specific toons:

- `"Josephat, go mine ore"` → `LuaComm:send("Josephat", "gather", {...})`
- `"all DPS attack the boss"` → relay sends to `role:dps`
- `"everyone stop"` → relay broadcasts to `*`

The LLM parses the target from natural language and the relay client routes accordingly.

## Key Dependencies

- **Python**: FastAPI, Anthropic SDK, OpenAI SDK, httpx, pydantic-settings
- **Lua**: LuaComm (relay client), minionlib (FFXIVMinion core)
- **External**: LuaComm relay server (PowerShell), LuaCommander (Delphi, optional)
- **Docs reference**: `docs/gui_api.md` for in-game UI, `docs/minionlib.md` for core Lua APIs
