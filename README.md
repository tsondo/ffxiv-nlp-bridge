# FFXIV NLP Bridge

Talk to FFXIVMinion in plain English. Type things like "go grind for 30 minutes" or "gather some iron ore" and the bot figures out what to do.

## How It Works

```
You: "go grind for 30 minutes"
  |
  v
Python service (parses your text with an LLM)
  |
  v
{ "task": "grind", "params": { "duration": 30 } }
  |
  v
FFXIVMinion Lua addon (picks up the command and runs it)
```

The Python service runs on your PC (or WSL) and uses an LLM to turn your words into structured commands. The Lua addon runs inside FFXIVMinion, polls the Python service for new commands every couple seconds, and executes them.

## Quick Start

### 1. Install the Python service

```bash
cd python_service
pip install -e .
```

### 2. Configure your LLM

Copy `.env.example` to `.env` and pick a provider:

**Option A: Local model (vLLM, ollama, llama.cpp)**
```bash
NLP_BRIDGE_LLM_PROVIDER=openai
NLP_BRIDGE_LLM_BASE_URL=http://localhost:8080/v1
NLP_BRIDGE_LLM_MODEL=your-model-name
NLP_BRIDGE_LLM_API_KEY=unused
```

**Option B: Claude API**
```bash
NLP_BRIDGE_LLM_PROVIDER=claude
NLP_BRIDGE_LLM_API_KEY=sk-ant-...
```

### 3. Start the service

```bash
cd python_service
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Install the Lua addon

Copy the `lua_bridge/` folder into your FFXIVMinion LuaMods directory:

```
MINIONAPP\Bots\FFXIVMinion64\LuaMods\NLPBridge\
  module.def
  nlp_bridge.lua
```

Edit the `host` in `nlp_bridge.lua` to point to your Python service (e.g. your WSL IP).

Reload Lua in FFXIVMinion and the addon starts polling automatically.

### 5. Send a command

```bash
# Via curl
curl -X POST http://localhost:8000/command \
  -H "Content-Type: application/json" \
  -d '{"text": "go grind for 30 minutes"}'

# Or use the CLI
ffxiv-nlp go grind for 30 minutes
```

## What You Can Say

| Command | What it does |
|---|---|
| "grind for 30 minutes" | Starts grind mode with a duration |
| "gather iron ore" | Switches to gather mode (mining) |
| "do FATEs for a while" | Grind mode with FATEs enabled |
| "teleport to Limsa Lominsa" | Navigates via aetheryte |
| "craft 10 iron ingots" | Switches to craft mode |
| "stop" | Stops the bot |
| "status" | Reports current bot state |

The LLM is flexible -- you don't need exact phrasing. It interprets your intent and maps it to the right task.

## API

| Endpoint | Method | Description |
|---|---|---|
| `/command` | POST | Send a natural language command. Returns the parsed result and a `command_id`. |
| `/minion/pending` | GET | Lua addon polls this. Returns next queued command or 204 if empty. |
| `/minion/result` | POST | Lua addon reports execution results here. |
| `/minion/status` | GET | Returns the last known bot status (mode, running, player info). |
| `/health` | GET | Service health check. |

## Project Structure

```
python_service/          # FastAPI + LLM parsing
  app/
    main.py              # API endpoints
    llm.py               # LLM backends (Claude / OpenAI-compatible)
    command_queue.py      # In-memory command queue
    models.py            # Request/response models
    config.py            # Settings (NLP_BRIDGE_ env prefix)
    cli.py               # CLI entry point

lua_bridge/              # FFXIVMinion addon
  module.def             # Addon manifest
  nlp_bridge.lua         # Polling loop + task handlers
```

## Requirements

- Python 3.10+
- An LLM (local via vLLM/ollama/llama.cpp, or Claude API)
- FFXIVMinion (for the Lua addon)
