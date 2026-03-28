# SPEC.md — FFXIV NLP Bridge Implementation Specification

## 1. Overview

Build a conversational natural language controller for FFXIVMinion. The player types plain English commands in-game (or via CLI/external tool). An LLM interprets the intent, asks for clarification when needed, and dispatches structured commands to the Lua addon for execution.

---

## 2. Conversation Flow

### 2.1 Core Interaction Model

```
Player: "Josephat, go mine ore outside Limsa Lominsa"
System: (determines: need to teleport to Limsa, move to mining area, start gather mode)
System: "I'll teleport to Limsa Lominsa Lower Decks, head to the mining nodes in Lower La Noscea, and start mining. Sound good?"
Player: "yes"
System: (queues: teleport → navigate → gather)
System: "On my way. Teleporting to Limsa Lominsa."
```

### 2.2 Response Types

The LLM returns one of:

| Type | When | Contains |
|------|------|----------|
| `execute` | Intent is clear, ready to act | One or more structured commands |
| `clarify` | Ambiguous or incomplete | A question for the player |
| `confirm` | Multi-step plan needs approval | Proposed plan + commands (held until confirmed) |
| `info` | Player asked a question, no action needed | Informational text |
| `refuse` | Request is impossible or nonsensical | Explanation of why |

### 2.3 Session State

- Each conversation session has a unique ID and message history.
- History is kept in memory (no persistence needed across service restarts).
- The LLM receives the full session history on each turn so it can reference prior context.
- Sessions expire after configurable idle timeout (default: 30 min).

---

## 3. Python Service Specification

### 3.1 New/Modified Endpoints

#### `POST /chat`
Primary conversational endpoint. Replaces `/command` as the main interface.

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
    {"task": "navigate", "params": {"destination": "Limsa Lominsa", "aetheryte": true}},
    {"task": "navigate", "params": {"destination": "Lower La Noscea"}},
    {"task": "gather", "params": {"node_type": "mining"}}
  ]
}
```

Or for a clarification:
```json
{
  "session_id": "abc123",
  "type": "clarify",
  "message": "There are mining nodes in both Lower La Noscea and Outer La Noscea near Limsa. Which area do you want?"
}
```

Or for immediate execution:
```json
{
  "session_id": "abc123",
  "type": "execute",
  "message": "Stopping the bot.",
  "commands": [
    {"command_id": "a1b2c3d4", "task": "stop", "params": {}}
  ]
}
```

#### `POST /command` (kept for backward compat)
Existing single-shot endpoint. Unchanged behavior.

#### `GET /chat/response/{session_id}` (optional, for Lua polling)
Lua addon polls this to get the latest chat message to display in-game.

**Response:**
```json
{
  "message": "Teleporting to Limsa Lominsa.",
  "status": "executing",
  "active_command": {"task": "navigate", "params": {"destination": "Limsa Lominsa", "aetheryte": true}}
}
```

#### Existing endpoints (unchanged)
- `GET /minion/pending` — Lua polls for next command
- `POST /minion/result` — Lua reports execution result
- `GET /minion/status` — Last known bot status
- `GET /health` — Health check

### 3.2 Conversation Manager

New module: `app/conversation.py`

Responsibilities:
- Create and track sessions (dict of session_id → message history)
- Append user and assistant messages to history
- Pass full history to LLM on each turn
- Parse LLM structured output into response types
- On `execute`: enqueue commands to CommandQueue
- On `confirm` + player says yes: enqueue the pending plan
- Session cleanup on timeout

### 3.3 LLM System Prompt Updates

The system prompt needs to be expanded to:
- Instruct the LLM to output structured JSON with a `type` field (execute/clarify/confirm/info/refuse)
- Provide FFXIV game knowledge (zone names, aetheryte names, gathering node types)
- Explain the available tasks and their parameters in detail
- Instruct the LLM to propose multi-step plans for complex requests
- Instruct the LLM to ask for clarification rather than guess when ambiguous

### 3.4 Game Knowledge Base

New module: `app/game_data.py`

Static data injected into the system prompt or available as LLM context:
- Major zone names and their connections
- Aetheryte locations and names
- Gathering node types by zone (mining, botany, fishing)
- Common item-to-gathering-type mappings

This does NOT need to be exhaustive. The LLM has general FFXIV knowledge from training. This data handles specifics the LLM might get wrong (exact aetheryte names, which zone connects to which).

### 3.5 Multi-Step Command Plans

New model: `CommandPlan`
- Ordered list of commands to execute sequentially
- Each command waits for the previous one's result before dispatching
- Plan-level status tracking (which step are we on, did any fail)

The CommandQueue needs to support:
- Enqueuing a plan (ordered sequence)
- Dispatching one command at a time
- Advancing to next step on success result
- Aborting remaining steps on failure

---

## 4. Game Knowledge Database

### 4.1 Why a Database

The LLM knows FFXIV conceptually from training data, but it doesn't know:
- What's in the player's inventory right now
- What crafting/gathering levels the character has
- Exact recipe ingredients and quantities
- Whether prerequisites are met for a given task
- Current market board prices or retainer inventory

Without this data, the LLM can only guess. With it, the system can have conversations like:

```
Player: "Craft me 5 mythril bangles"
System: (looks up recipe → checks inventory → checks skills)
System: "To craft 5 Mythril Bangles you need 15 Mythril Ingots and 5 Bomb Ash.
         You have 8 Mythril Ingots and 0 Bomb Ash in inventory.
         I'll need to gather or buy the missing materials.
         Your Goldsmith is level 42, which is high enough.
         Want me to start by gathering the missing materials?"
Player: "Yes, go for it"
System: (queues: buy/gather bomb ash → gather mythril ore → smelt ingots → craft bangles)
```

### 4.2 Data Categories

#### Tier 1 — Static Game Data (populated once, updated per patch)
Reference data that doesn't change during play.

| Data | Source | Update Frequency |
|------|--------|-----------------|
| Recipes (item → ingredients, quantities, required level, class) | XIVAPI / Teamcraft DB | Per game patch |
| Items (id, name, category, gather method) | XIVAPI | Per game patch |
| Zones (id, name, region, connected zones) | XIVAPI | Per game patch |
| Aetherytes (id, name, zone, cost) | XIVAPI | Per game patch |
| Gathering nodes (zone, type, items available, level required) | XIVAPI / Teamcraft | Per game patch |
| Class/job info (abbreviations, role, level caps) | XIVAPI | Per expansion |

#### Tier 2 — Character State (synced from game via Lua addon)
Data that changes during play. The Lua addon reports this back to the Python service.

| Data | Source | Update Frequency |
|------|--------|-----------------|
| Inventory contents | Lua → POST /minion/status | On change or periodic poll |
| Character levels per class/job | Lua → POST /minion/status | On change |
| Current location (zone, coords) | Lua → POST /minion/status | Every poll cycle |
| Gil balance | Lua → POST /minion/status | On change |
| Current buffs/status | Lua → POST /minion/status | Every poll cycle |
| Equipped gear | Lua → POST /minion/status | On change |

#### Tier 3 — Derived/Computed (calculated by Python service)
Feasibility analysis computed on demand.

| Data | Computed From | Purpose |
|------|--------------|---------|
| Recipe feasibility | Recipe + inventory + levels | "Can I craft this right now?" |
| Material shopping list | Recipe tree - inventory | "What's missing?" |
| Gathering plan | Missing materials + node locations | "Where do I go to get what I need?" |
| Optimal route | Current location + destinations | "What order should I do things?" |
| Prerequisite chain | Quest/level requirements | "What do I need to unlock first?" |

### 4.3 Database Choice

**SQLite** for initial implementation:
- Zero infrastructure — single file, ships with Python
- More than sufficient for the data volume (tens of thousands of items/recipes)
- Easy to populate from XIVAPI JSON dumps
- Easy to query from Python with SQLAlchemy or raw SQL
- Can migrate to PostgreSQL later if needed (unlikely)

### 4.4 Schema (high-level)

```sql
items (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT,
  is_craftable BOOLEAN,
  is_gatherable BOOLEAN,
  gather_type TEXT,  -- mining/botany/fishing/null
  description TEXT
)

recipes (
  id INTEGER PRIMARY KEY,
  result_item_id INTEGER REFERENCES items(id),
  result_quantity INTEGER,
  class_job TEXT,       -- GSM, ARM, BSM, etc.
  level_required INTEGER
)

recipe_ingredients (
  recipe_id INTEGER REFERENCES recipes(id),
  item_id INTEGER REFERENCES items(id),
  quantity INTEGER
)

zones (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  region TEXT
)

aetherytes (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  zone_id INTEGER REFERENCES zones(id)
)

gathering_nodes (
  id INTEGER PRIMARY KEY,
  zone_id INTEGER REFERENCES zones(id),
  type TEXT NOT NULL,  -- mining/botany/fishing
  level_required INTEGER
)

gathering_node_items (
  node_id INTEGER REFERENCES gathering_nodes(id),
  item_id INTEGER REFERENCES items(id)
)

-- Flexible store for live character data from Lua addon
character_state (
  key TEXT PRIMARY KEY,    -- e.g. "inventory:mythril_ingot", "level:gsm", "location:zone"
  value TEXT NOT NULL,     -- JSON-encoded
  updated_at TIMESTAMP
)
```

### 4.5 Data Population Strategy

**Static data (Tier 1):**
1. Download bulk data from XIVAPI (https://xivapi.com) or Teamcraft's GitHub data dumps
2. Parse and load into SQLite via a one-time import script (`scripts/import_game_data.py`)
3. Re-run import script after game patches

**Character state (Tier 2):**
1. Expand Lua addon's `get_bot_status()` to include inventory, class levels, etc.
2. Expand `/minion/result` or add new `POST /minion/sync` endpoint for bulk state updates
3. Python service writes to `character_state` table on receipt

**Derived data (Tier 3):**
Computed on-the-fly by the conversation manager when the LLM needs to reason about feasibility.

### 4.6 LLM Integration

The LLM does NOT query the database directly. Instead:

1. Player says "craft me some mythril bangles"
2. Conversation manager recognizes this involves crafting
3. Python service queries the DB: recipe lookup → inventory check → level check
4. Results are injected into the LLM context as structured facts:
   ```
   CONTEXT: The player asked to craft Mythril Bangles.
   Recipe: 3x Mythril Ingot, 1x Bomb Ash. Requires Goldsmith level 42.
   Inventory: 8x Mythril Ingot, 0x Bomb Ash.
   Character: Goldsmith level 45.
   Assessment: Missing 1x Bomb Ash. Crafting level is sufficient.
   ```
5. LLM generates a conversational response and plan based on these facts

This keeps the LLM doing what it's good at (natural language, planning) while the database handles what it's bad at (exact quantities, precise lookups).

### 4.7 Depth Decisions

How deep to go is a spectrum. Each level adds capability but also complexity:

| Depth Level | Capability | Effort |
|-------------|-----------|--------|
| **Level 0** (current) | LLM guesses from training data | Done |
| **Level 1** | Static recipe/item lookups, zone/aetheryte data | Medium — data import script + DB queries |
| **Level 2** | Live inventory/level awareness | High — Lua addon changes to report inventory, character state sync |
| **Level 3** | Multi-step dependency resolution (recursive recipe trees, "I need ingots which need ore which needs mining level 30") | High — tree traversal logic, planning algorithms |
| **Level 4** | Market board integration, retainer management, optimal buy-vs-gather decisions | Very high — additional API/addon integration |

**Recommendation:** Build Level 1 first (highest value-to-effort), then Level 2 when the Lua addon is mature enough to report inventory. Levels 3 and 4 are stretch goals.

---

## 5. Lua Addon Specification

### 5.1 In-Game GUI

New or extended in `nlp_bridge.lua`:

**Chat Window:**
- Resizable, movable window using `GUI:Begin` / `GUI:End`
- Text input field at bottom (`GUI:InputText`)
- Scrollable message history above (player messages + system responses)
- Submit on Enter key or button press
- Messages sent to Python service via `HttpRequest` POST to `/chat`
- Responses polled from `/chat/response/{session_id}` or received inline

**Status Indicator:**
- Small overlay or section showing current state: idle / executing / waiting for input
- Current task name if executing

### 5.2 Chat Communication Flow

1. Player types in the input box, hits Enter
2. Lua sends `POST /chat` with session_id + text
3. Lua polls `/chat/response/{session_id}` (or uses the POST response directly if sync)
4. Display response in chat window
5. If type is `clarify` or `confirm`, player types again → loop
6. If type is `execute`, commands flow through existing `/minion/pending` polling

**Note:** The `/chat` POST could return the response synchronously (simpler) but the LLM call may take 1-3 seconds. Options:
- **Option A (simpler):** Synchronous POST, Lua's HttpRequest handles the delay via async callback. Display "thinking..." while waiting.
- **Option B (more complex):** POST returns immediately with session_id, Lua polls for response. Better for very slow LLM calls.

Recommend **Option A** for initial implementation.

### 5.3 Task Handlers

Existing handlers are sufficient for Phase 1. Enhancements for later:
- Duration tracking (stop after N minutes)
- Sequential command execution awareness (report "step 2 of 3 complete")
- Richer status reporting back to Python service

### 5.4 Third-Party Addon API Readiness

The handler dispatch in Lua (`handlers.grind`, `handlers.navigate`, etc.) is the integration point. When a third-party API becomes available:
- Add a config flag: `NLPBridge.config.use_external_api = false`
- When true, route commands to the external addon's API instead of calling FFXIVMinion primitives directly
- No changes needed to Python service or conversation logic

---

## 6. Implementation Phases

### Phase 1: Conversational Core
**Goal:** Replace single-shot parsing with dialogue-capable conversation.

- [ ] `POST /chat` endpoint with session management
- [ ] Conversation manager with history tracking
- [ ] Updated LLM prompt supporting clarify/confirm/execute response types
- [ ] Structured output parsing for new response types
- [ ] Backward-compatible: `/command` still works as before
- [ ] CLI updated to support multi-turn conversation (optional)

### Phase 2: Game Knowledge Database (Level 1)
**Goal:** Give the system factual grounding so it stops guessing.

- [ ] SQLite database with schema from §4.4
- [ ] Data import script pulling from XIVAPI / Teamcraft data dumps
- [ ] Query layer: recipe lookup, item search, zone/aetheryte lookup
- [ ] Context injection: conversation manager queries DB and injects facts into LLM context
- [ ] Feasibility checks: "can this character craft this?" based on static data

### Phase 3: In-Game GUI
**Goal:** Type commands and see responses without leaving the game.

- [ ] Chat window with input field and message display
- [ ] HTTP communication to `/chat` endpoint
- [ ] Display clarification questions and accept follow-up input
- [ ] Status indicator (idle / thinking / executing)
- [ ] Basic styling and layout

### Phase 4: Multi-Step Plans
**Goal:** Complex commands that chain multiple actions.

- [ ] CommandPlan model and plan-aware queue
- [ ] LLM prompt updates for multi-step plan generation
- [ ] Plan confirmation flow (show plan → player approves → execute sequentially)
- [ ] Step-by-step progress reporting
- [ ] Failure handling (abort plan, retry step, skip step)

### Phase 5: Live Character State (Level 2)
**Goal:** System knows what you have and what you can do right now.

- [ ] Expand Lua `get_bot_status()` to report inventory, class levels, gil
- [ ] New `POST /minion/sync` endpoint for bulk state updates
- [ ] Character state stored in DB, queried during planning
- [ ] LLM context now includes live inventory/level data
- [ ] Dependency resolution: "you need X, which requires gathering Y"

### Phase 6: Polish & Advanced Features
**Goal:** Smarter, smoother experience.

- [ ] Session timeout and cleanup
- [ ] Recursive recipe tree resolution (Level 3 depth)
- [ ] Improved routing (optimal gather→craft→deliver sequences)
- [ ] Logging and observability improvements
- [ ] Error recovery options (retry/skip/abort per step)

### Phase 7: Third-Party Integration (when available)
**Goal:** Swap execution layer to use a more capable addon's API.

- [ ] Handler abstraction layer
- [ ] External API adapter
- [ ] Config-driven handler selection

---

## 7. Data Models

### New Models (app/models.py)

```python
class ChatRequest(BaseModel):
    session_id: str | None = None
    text: str

class ChatResponse(BaseModel):
    session_id: str
    type: Literal["execute", "clarify", "confirm", "info", "refuse"]
    message: str
    commands: list[MinionCommand] | None = None      # for type=execute
    pending_plan: list[MinionCommand] | None = None   # for type=confirm

class CommandPlan(BaseModel):
    plan_id: str
    commands: list[QueuedCommand]
    current_step: int = 0
    status: Literal["pending", "executing", "completed", "failed", "aborted"] = "pending"
```

### Existing Models (unchanged)
- `UserCommand`, `MinionCommand`, `CommandResponse`, `PendingCommand`, `ResultReport`

---

## 8. LLM Prompt Structure (Phase 1)

```
SYSTEM:
You are Josephat's command interpreter for FFXIVMinion. The player gives you
natural language instructions. You respond with structured JSON.

Your response MUST be valid JSON with this structure:
{
  "type": "execute" | "clarify" | "confirm" | "info" | "refuse",
  "message": "human-readable text shown to the player",
  "commands": [...]   // only when type=execute
  "plan": [...]       // only when type=confirm
}

Available tasks: [same task list as current, with expanded descriptions]

Rules:
- If the request is clear and simple, use type=execute with commands.
- If the request involves multiple steps, use type=confirm with a plan and
  explain what you'll do.
- If the request is ambiguous, use type=clarify and ask a specific question.
- If the player confirms a plan (says yes/ok/sure/etc), use type=execute.
- If asked a question about status or the game, use type=info.
- If the request is impossible, use type=refuse and explain why.

CONVERSATION HISTORY:
[injected per-session]

USER:
[player's latest message]
```

---

## 9. Open Questions

1. **Sync vs async chat response** — Option A (sync with async callback) is simpler. Revisit if LLM latency causes issues with HttpRequest timeouts in Lua.
2. **Plan confirmation UX** — Always confirm multi-step plans, or only for "big" ones (e.g., teleport involved)? Start with always-confirm, relax later.
3. **Error recovery** — If a mid-plan step fails, should the system auto-retry, ask the player, or abort? Start with abort + notify.
4. **Third-party addon API format** — Unknown until the developer provides it. Current handler abstraction should be flexible enough to adapt.
5. **Game data source** — XIVAPI vs Teamcraft GitHub dumps vs both? XIVAPI is a REST API (easy to query, may rate-limit). Teamcraft publishes JSON/CSV files on GitHub (bulk download, no rate limits, community-maintained). Likely Teamcraft dumps for bulk import, XIVAPI for spot lookups.
6. **Inventory reporting from Lua** — How much of the FFXIVMinion Lua API exposes inventory? Need to investigate what `Player` table fields are available. This determines whether Level 2 depth is feasible without the third-party addon.
7. **How deep on recipe trees?** — Flat (one level of ingredients) is straightforward. Recursive (ingredients that are themselves crafted from sub-ingredients) is much more useful but significantly more complex. Start flat, add recursion in Phase 6.
8. **Buy vs gather decisions** — When materials are missing, should the system default to gathering, or should it consider buying from vendors/market board? Gathering is simpler to implement. Market board integration is a Phase 6+ feature.
9. **Data staleness** — How often does character state need to sync? Every poll cycle (2s) is overkill for inventory. Probably: location every poll, inventory on demand or on change, levels on change.
