# SPEC.md — FFXIV NLP Bridge Implementation Specification

## 1. Overview

Build a conversational natural language controller for FFXIVMinion. The player types plain English commands in-game (or via CLI/external tool). An LLM interprets the intent, asks for clarification when needed, and dispatches structured commands through the LuaComm relay to one or more game agents for execution.

### 1.1 Integration with LuaComm

LuaComm is an external library maintained by a collaborator. It provides the entire multi-agent communication layer:

| Component | What it does | We use it for |
|-----------|-------------|---------------|
| **relay.ps1** | PowerShell HTTP message broker | Command routing, agent queues, heartbeats |
| **luacomm.lua** | Lua client library | Agent registration, polling, callbacks |
| **LuaCommander** | Delphi desktop GUI | Debugging, manual commands (optional) |

**Boundary rule:** We do not modify LuaComm code. We code against its REST API and Lua API as documented. Bugs in LuaComm are fixed upstream by the maintainer.

### 1.2 What we replaced

The original architecture had a custom command queue and polling endpoints. LuaComm replaces all of that:

| Old component | Replaced by |
|---------------|-------------|
| `command_queue.py` | Relay's per-agent queues |
| `GET /minion/pending` | Relay `GET /api/recv/<name>` |
| `POST /minion/result` | `LuaComm:send(commander, "result", {...})` |
| `GET /minion/status` | `LuaComm:send(commander, "status_report", {...})` |
| JSON encode/decode in nlp_bridge.lua | LuaComm's embedded JSON library |
| HTTP polling loop in nlp_bridge.lua | `LuaComm:update()` |

---

## 2. Conversation Flow

### 2.1 Core Interaction Model

```
Player: "Josephat, go mine ore outside Limsa Lominsa"
System: (determines: need to teleport to Limsa, move to mining area, start gather mode)
System: "I'll teleport to Limsa Lominsa Lower Decks, head to the mining nodes in
         Lower La Noscea, and start mining. Sound good?"
Player: "yes"
System: (sends commands through relay to agent "Josephat":
         teleport → navigate → gather)
System: "On my way. Teleporting to Limsa Lominsa."
```

### 2.2 Multi-Agent Interaction Model

```
Player: "Have all DPS attack the boss, and healers focus on Tank1"
System: (sends to role:dps → attack {target: "Boss"})
        (sends to role:healer → heal {target: "Tank1"})
System: "Sent attack orders to DPS and heal orders to healers."
```

### 2.3 Response Types

The LLM returns one of:

| Type | When | Contains |
|------|------|----------|
| `execute` | Intent is clear, ready to act | One or more structured commands with targets |
| `clarify` | Ambiguous or incomplete | A question for the player |
| `confirm` | Multi-step plan needs approval | Proposed plan + commands (held until confirmed) |
| `info` | Player asked a question, no action needed | Informational text |
| `refuse` | Request is impossible or nonsensical | Explanation of why |

### 2.4 Session State

- Each conversation session has a unique ID and message history.
- History is kept in memory (no persistence needed across service restarts).
- The LLM receives the full session history on each turn so it can reference prior context.
- Sessions expire after configurable idle timeout (default: 30 min).

---

## 3. Python Service Specification

### 3.1 Relay Client (`relay_client.py`)

New module that wraps LuaComm relay HTTP API. The Python service registers as a commander agent and sends/receives through the relay.

```python
class RelayClient:
    """HTTP client for the LuaComm relay server."""

    def __init__(self, host: str, port: int, name: str):
        self.base_url = f"http://{host}:{port}"
        self.name = name
        self._registered = False

    async def register(self) -> bool:
        """POST /api/register — register as commander agent."""

    async def send(self, target: str, cmd_type: str, data: dict) -> dict:
        """POST /api/send — send command to a specific agent."""

    async def send_to_role(self, role: str, cmd_type: str, data: dict) -> dict:
        """POST /api/send with to='role:<role>'."""

    async def broadcast(self, cmd_type: str, data: dict) -> dict:
        """POST /api/send with to='*'."""

    async def poll(self) -> list[dict]:
        """GET /api/recv/<name> — poll for messages sent back to us."""

    async def heartbeat(self) -> bool:
        """POST /api/heartbeat/<name>."""

    async def get_agents(self) -> list[dict]:
        """GET /api/agents — list online agents and their roles."""
```

The relay client runs a background task for heartbeats and polling for incoming messages (results, status reports from agents).

### 3.2 Endpoints

#### `POST /chat`
Primary conversational endpoint.

**Request:**
```json
{
  "session_id": "optional-existing-session-id",
  "text": "go mine ore outside Limsa Lominsa"
}
```

**Response:**
```json
{
  "session_id": "abc123",
  "type": "confirm",
  "message": "I'll teleport to Limsa Lominsa, head to Lower La Noscea, and start mining. Sound good?",
  "pending_plan": [
    {"target": "Josephat", "task": "navigate", "params": {"destination": "Limsa Lominsa", "aetheryte": true}},
    {"target": "Josephat", "task": "navigate", "params": {"destination": "Lower La Noscea"}},
    {"target": "Josephat", "task": "gather", "params": {"node_type": "mining"}}
  ]
}
```

For immediate execution:
```json
{
  "session_id": "abc123",
  "type": "execute",
  "message": "Stopping the bot.",
  "commands": [
    {"target": "*", "task": "stop", "params": {}}
  ]
}
```

When `type=execute`, the service immediately sends each command through the relay client to the appropriate target.

#### `POST /command` (backward compatibility)
Single-shot endpoint. Parses text, sends through relay, returns result. No session state.

#### `GET /agents`
Proxies the relay's agent list. Returns which toons are online and their roles.

```json
{
  "agents": [
    {"name": "Josephat", "role": "dps", "online": true},
    {"name": "Healer1", "role": "healer", "online": true}
  ]
}
```

#### `GET /health`
Service health check. Includes relay connectivity status.

### 3.3 Command Routing Logic

When the LLM produces commands, the Python service maps targets to relay calls:

| LLM output target | Relay call |
|-------------------|------------|
| Specific name (e.g. `"Josephat"`) | `relay.send("Josephat", task, data)` |
| Role (e.g. `"all DPS"`) | `relay.send_to_role("dps", task, data)` |
| Everyone / broadcast | `relay.broadcast(task, data)` |
| No target specified | Send to default agent (configurable) or clarify |

### 3.4 Result Handling

Agents send results back to the commander via LuaComm messaging. The relay client's poll loop receives these and routes them:

- **`task_result`** — Execution success/failure for a specific command. Stored by command ID for session tracking.
- **`status_report`** — Agent state (HP, location, mode). Cached per-agent for context injection into LLM.

---

## 4. Lua Agent Specification

### 4.1 Agent Addon Structure

```
lua_bridge/
├── module.def          # FFXIVMinion addon manifest
└── nlp_agent.lua       # LuaComm agent with NLP task handlers
```

Deployed to `MINIONAPP\Bots\FFXIVMinion64\LuaMods\NLPBridge\`.

LuaComm's `luacomm.lua` must be available at the path configured in the loadfile call (typically `ml_global_information.path .. "\\LuaComm\\luacomm.lua"`).

### 4.2 Agent Script Pattern

```lua
local LuaComm = loadfile(ml_global_information.path .. "\\LuaComm\\luacomm.lua")()

local RELAY_IP   = "192.168.1.100"  -- relay server IP
local RELAY_PORT = 19850
local MY_NAME    = Player.name or "Agent1"  -- use character name
local MY_ROLE    = "dps"                     -- configurable per toon

LuaComm:setup(RELAY_IP, RELAY_PORT, MY_NAME, MY_ROLE)

-- Register task handlers
LuaComm:on("grind",    function(cmd) handle_grind(cmd.data, cmd.from) end)
LuaComm:on("gather",   function(cmd) handle_gather(cmd.data, cmd.from) end)
LuaComm:on("fate",     function(cmd) handle_fate(cmd.data, cmd.from) end)
LuaComm:on("navigate", function(cmd) handle_navigate(cmd.data, cmd.from) end)
LuaComm:on("craft",    function(cmd) handle_craft(cmd.data, cmd.from) end)
LuaComm:on("duty",     function(cmd) handle_duty(cmd.data, cmd.from) end)
LuaComm:on("stop",     function(cmd) handle_stop(cmd.data, cmd.from) end)
LuaComm:on("status",   function(cmd) handle_status(cmd.data, cmd.from) end)

-- Main loop
function NLPAgent_Pulse()
    LuaComm:update()
end

RegisterEventHandler("Gameloop.Update", NLPAgent_Pulse, "NLPAgent.Pulse")
```

### 4.3 Task Handlers

Each handler executes the command via the FFXIVMinion API, then sends a result back to the commander:

```lua
function handle_grind(params, commander)
    local duration = params.duration or 0
    local do_fates = params.fates or false

    -- Set FFXIVMinion mode
    gBotMode = "grind"
    FFXIV_Common_BotRunning = true
    -- ... configure grind settings ...

    LuaComm:send(commander, "task_result", {
        task = "grind",
        success = true,
        message = "Started grinding" .. (duration > 0 and (" for " .. duration .. " min") or ""),
    })
end
```

### 4.4 Status Reporting

On receiving a `status` command (or periodically), the agent reports its state:

```lua
function handle_status(params, commander)
    LuaComm:send(commander, "status_report", {
        name = MY_NAME,
        role = MY_ROLE,
        mode = gBotMode or "unknown",
        running = FFXIV_Common_BotRunning == true,
        hp = Player.hp and Player.hp.percent or 0,
        pos = Player.pos and { x = Player.pos.x, y = Player.pos.y, z = Player.pos.z } or nil,
        zone = Player.localmapid or 0,
    })
end
```

---

## 5. Game Knowledge Database

### 5.1 Data Tiers

#### Tier 1 — Static Game Data (populated from XIVAPI / Teamcraft)

| Data | Purpose |
|------|---------|
| Items (name, category, craftable, gatherable) | "What is iron ore?" |
| Recipes (ingredients, class, level) | "What do I need to craft iron ingots?" |
| Zones & aetherytes | "Where is Limsa Lominsa?" |
| Gathering nodes (zone, type, items, level) | "Where can I mine iron ore?" |

#### Tier 2 — Live Character State (reported by agents via LuaComm)

| Data | Reported via | Update frequency |
|------|-------------|-----------------|
| Current location | `status_report` | On request or periodic |
| HP, class, level | `status_report` | On request or periodic |
| Inventory contents | `status_report` (extended) | On change or on demand |
| Gil balance | `status_report` (extended) | On change |

#### Tier 3 — Derived/Computed

| Data | Computed from | Purpose |
|------|--------------|---------|
| Recipe feasibility | Recipe + inventory + levels | "Can I craft this?" |
| Material shopping list | Recipe tree − inventory | "What's missing?" |
| Gathering plan | Missing materials + node locations | "Where to get what I need" |

### 5.2 Database

**SQLite** — single file, ships with Python, sufficient for the data volume.

```sql
items (id, name, category, is_craftable, is_gatherable, gather_type, description)
recipes (id, result_item_id, result_quantity, class_job, level_required)
recipe_ingredients (recipe_id, item_id, quantity)
zones (id, name, region)
aetherytes (id, name, zone_id)
gathering_nodes (id, zone_id, type, level_required)
gathering_node_items (node_id, item_id)
character_state (key, value, updated_at)  -- flexible KV for live agent data
```

### 5.3 Data Population

1. Download bulk data from Teamcraft GitHub dumps (preferred) or XIVAPI
2. Parse and load via `scripts/import_game_data.py`
3. Re-run on game patches to update

---

## 6. Phased Implementation Plan

### Phase 1: LuaComm Integration
**Goal:** Replace the custom queue/polling layer with LuaComm relay.

- [ ] `relay_client.py` — async HTTP client for LuaComm relay
- [ ] Register Python service as commander on relay startup
- [ ] Background tasks: heartbeat loop, result polling loop
- [ ] Update `POST /command` to route through relay instead of internal queue
- [ ] `nlp_agent.lua` — LuaComm-based agent with task handlers (port logic from nlp_bridge.lua)
- [ ] Result handling: agents send `task_result` back, Python service receives via poll
- [ ] `GET /agents` endpoint proxying relay agent list
- [ ] Remove deprecated: `command_queue.py`, `/minion/*` endpoints, old `nlp_bridge.lua`
- [ ] Update config: relay host/port/commander name in `.env`

### Phase 2: Conversational Chat
**Goal:** Move from single-shot commands to multi-turn dialogue.

- [ ] `POST /chat` endpoint with session management
- [ ] Conversation manager with history tracking
- [ ] Updated LLM prompt supporting clarify/confirm/execute response types
- [ ] Structured output parsing for new response types
- [ ] Multi-agent targeting in LLM output (specific agent, role, broadcast)
- [ ] Backward-compatible: `/command` still works as before
- [ ] CLI updated to support multi-turn conversation (optional)

### Phase 3: Game Knowledge Database
**Goal:** Give the system factual grounding so it stops guessing.

- [ ] SQLite database with schema from §5.2
- [ ] Data import script pulling from XIVAPI / Teamcraft data dumps
- [ ] Query layer: recipe lookup, item search, zone/aetheryte lookup
- [ ] Context injection: conversation manager queries DB and injects facts into LLM context
- [ ] Feasibility checks: "can this character craft this?" based on static data

### Phase 4: In-Game GUI
**Goal:** Type commands and see responses without leaving the game.

- [ ] Chat window with input field and message display
- [ ] Communication to `/chat` endpoint (via LuaComm relay or direct HTTP)
- [ ] Display clarification questions and accept follow-up input
- [ ] Status indicator (idle / thinking / executing)
- [ ] Agent status panel (who's online, what they're doing)

### Phase 5: Multi-Step Plans
**Goal:** Complex commands that chain multiple actions.

- [ ] CommandPlan model with ordered steps and per-step targets
- [ ] LLM prompt updates for multi-step plan generation
- [ ] Plan confirmation flow (show plan → player approves → execute sequentially)
- [ ] Step-by-step progress reporting via LuaComm result messages
- [ ] Failure handling (abort plan, retry step, skip step)

### Phase 6: Live Character State
**Goal:** System knows what each agent has and can do right now.

- [ ] Extended `status_report` with inventory, class levels, gil
- [ ] Character state cached per-agent in Python service
- [ ] LLM context includes live data from all agents
- [ ] Dependency resolution: "Josephat needs X, which requires gathering Y"
- [ ] Cross-agent planning: "Agent1 gathers, Agent2 crafts"

### Phase 7: Polish & Advanced Features
**Goal:** Smarter, smoother experience.

- [ ] Session timeout and cleanup
- [ ] Recursive recipe tree resolution
- [ ] Optimal routing (gather → craft → deliver sequences)
- [ ] Cross-agent task coordination (parallel execution)
- [ ] Logging and observability improvements
- [ ] Error recovery options (retry/skip/abort per step)

---

## 7. Data Models

### New/Modified Models (`app/models.py`)

```python
class ChatRequest(BaseModel):
    session_id: str | None = None
    text: str

class ChatResponse(BaseModel):
    session_id: str
    type: Literal["execute", "clarify", "confirm", "info", "refuse"]
    message: str
    commands: list[RelayCommand] | None = None
    pending_plan: list[RelayCommand] | None = None

class RelayCommand(BaseModel):
    """A command to be sent through the LuaComm relay."""
    target: str                    # agent name, "role:<role>", or "*"
    task: str                      # grind, gather, navigate, etc.
    params: dict = {}

class CommandPlan(BaseModel):
    plan_id: str
    commands: list[RelayCommand]
    current_step: int = 0
    status: Literal["pending", "executing", "completed", "failed", "aborted"] = "pending"

class AgentInfo(BaseModel):
    name: str
    role: str
    online: bool
```

### Kept from original (for `/command` backward compat)
- `UserCommand`, `MinionCommand`, `CommandResponse`

---

## 8. LLM Prompt Structure

```
SYSTEM:
You are the command interpreter for an FFXIV multiboxing setup. The player gives
you natural language instructions. You respond with structured JSON.

Your response MUST be valid JSON with this structure:
{
  "type": "execute" | "clarify" | "confirm" | "info" | "refuse",
  "message": "human-readable text shown to the player",
  "commands": [...]   // only when type=execute
  "plan": [...]       // only when type=confirm
}

Each command in commands/plan has:
{
  "target": "<agent name>" | "role:<role>" | "*",
  "task": "<task type>",
  "params": { ... }
}

Available agents: [injected from relay agent list]
Available tasks: grind, gather, fate, navigate, duty, craft, stop, status

Rules:
- If the request names a specific character, target that agent.
- If the request says "all DPS" or "healers", use role targeting.
- If the request says "everyone" or doesn't specify, use "*" (broadcast).
- If only one agent is online and no target specified, send to that agent.
- If the request is clear and simple, use type=execute with commands.
- If the request involves multiple steps, use type=confirm with a plan.
- If the request is ambiguous, use type=clarify and ask a specific question.
- If the player confirms a plan (yes/ok/sure/etc), use type=execute.
- If asked a question about status or the game, use type=info.
- If the request is impossible, use type=refuse and explain why.

CONVERSATION HISTORY:
[injected per-session]

ONLINE AGENTS:
[injected from relay]

USER:
[player's latest message]
```

---

## 9. LuaComm API Reference (for our code)

### Relay REST API (used by Python relay_client.py)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/register` | POST | Register agent `{name, role}` |
| `/api/send` | POST | Send command `{from, to, type, data}` |
| `/api/recv/<name>` | GET | Poll for pending commands |
| `/api/heartbeat/<name>` | POST | Keep-alive |
| `/api/agents` | GET | List all agents with online status |
| `/api/status` | GET | Relay server stats |

### Lua Client API (used by nlp_agent.lua)

| Method | Purpose |
|--------|---------|
| `LuaComm:setup(host, port, name, role)` | Initialize |
| `LuaComm:update()` | Poll + heartbeat + dispatch (call every frame) |
| `LuaComm:on(type, handler)` | Register callback for command type |
| `LuaComm:send(target, type, data)` | Send to specific agent |
| `LuaComm:broadcast(type, data)` | Send to all agents |
| `LuaComm:sendToRole(role, type, data)` | Send to agents with role |
| `LuaComm:agents()` | List known agents |

---

## 10. Open Questions

1. **Agent auto-naming** — Should the Lua agent use `Player.name` automatically, or require manual config? Auto is convenient but `Player` might not be available at load time.
2. **Chat via relay vs direct** — Should the in-game GUI POST directly to the Python service, or route chat messages through the relay? Direct is simpler; relay is more consistent with the architecture.
3. **Plan confirmation UX** — Always confirm multi-step plans, or only for "big" ones? Start with always-confirm.
4. **Error recovery** — If a mid-plan step fails, should the system auto-retry, ask the player, or abort? Start with abort + notify.
5. **Game data source** — Teamcraft GitHub dumps for bulk import, XIVAPI for spot lookups.
6. **Cross-agent state** — How does the Python service know Agent1's inventory vs Agent2's? Each agent's `status_report` includes their name; cache per-agent.
7. **Relay availability** — If the relay goes down, should the Python service queue commands locally and retry? Or just fail fast? Start with fail fast + clear error message.
8. **LuaComm versioning** — As the friend updates LuaComm, how do we handle breaking changes? Pin to known-working version in our repo, update deliberately.
