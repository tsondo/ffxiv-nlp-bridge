# LuaComm Reference — API & Integration Guide

> External dependency maintained by collaborator. **Do not modify LuaComm source files.**
> This document covers everything needed to integrate with LuaComm from both Python (relay REST API) and Lua (client library).

---

## 1. System Overview

LuaComm is a cross-machine communication system for MMOMinion. It consists of three components:

| Component | Language | File | Purpose |
|-----------|----------|------|---------|
| **Relay Server** | PowerShell | `relay/relay.ps1` | HTTP message broker — routes commands between agents |
| **Lua Client** | Lua | `lua/luacomm.lua` | Agent-side library — register, send, receive, heartbeat |
| **LuaCommander** | Delphi | `LuaCommander/` | Desktop GUI — monitor agents, send commands, remote exec (optional) |

### How it works

1. The relay server runs on one machine on the LAN, listening on a configurable port (default `19850`).
2. Each agent (game instance) loads `luacomm.lua`, registers with the relay, and polls for commands on a frame-based interval.
3. Commanders (our Python service, LuaCommander GUI, or a Lua commander script) also register and send commands through the relay.
4. The relay queues commands per-agent. When an agent polls, it receives and consumes all pending commands.
5. Agents can send messages back (results, status reports) by targeting the commander's agent name.

### Network topology

```
                    ┌──────────────────────┐
                    │  LuaComm Relay       │
                    │  relay.ps1           │
                    │  Port 19850          │
                    └──┬────┬────┬────┬────┘
                       │    │    │    │
            ┌──────────┘    │    │    └──────────┐
            ▼               ▼    ▼               ▼
     ┌────────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐
     │ Python     │  │ Agent1   │  │ Agent2   │  │ Agent3      │
     │ "NLPBridge"│  │ "Tank1"  │  │ "Healer1"│  │ "DPS1"      │
     │ role:cmdr  │  │ role:tank│  │ role:heal│  │ role:dps    │
     └────────────┘  └──────────┘  └──────────┘  └─────────────┘
```

---

## 2. Relay Server REST API

Base URL: `http://<host>:<port>` (default port `19850`).

All responses are JSON with an `ok` boolean field. Errors include an `error` string.

### 2.1 POST /api/register

Register an agent with the relay. Creates a command queue for this agent.

**Request:**
```json
{
  "name": "NLPBridge",
  "role": "commander"
}
```

**Response (200):**
```json
{
  "ok": true,
  "name": "NLPBridge",
  "role": "commander"
}
```

**Error (400):**
```json
{
  "ok": false,
  "error": "missing 'name'"
}
```

**Notes:**
- `name` must be unique across all agents. Re-registering with the same name updates the existing entry.
- `role` is a free-form string. Convention: `"dps"`, `"tank"`, `"healer"`, `"commander"`, `"agent"`.
- Registration creates an empty command queue for the agent.

---

### 2.2 POST /api/send

Send a command to one or more agents.

**Request:**
```json
{
  "from": "NLPBridge",
  "to": "Tank1",
  "type": "grind",
  "data": {
    "duration": 30,
    "fates": true
  }
}
```

**Response (200):**
```json
{
  "ok": true,
  "id": 42,
  "delivered": ["Tank1"]
}
```

**Targeting modes (the `to` field):**

| Value | Behavior |
|-------|----------|
| `"AgentName"` | Deliver to that specific agent's queue |
| `"*"` | Broadcast to all agents except sender |
| `"role:dps"` | Deliver to all agents with `role == "dps"`, except sender |

**What gets queued (the command object):**
```json
{
  "id": 42,
  "from": "NLPBridge",
  "to": "Tank1",
  "type": "grind",
  "data": { "duration": 30, "fates": true },
  "timestamp": "2025-03-28T14:30:00.0000000+00:00"
}
```

**Notes:**
- `id` is a relay-assigned auto-incrementing integer.
- `delivered` lists which agent names actually received the command (i.e., had a queue). If the target agent isn't registered, `delivered` will be empty.
- `from` is included so receivers know who sent the command and can reply.
- `type` and `data` are opaque to the relay — it just queues them. The meaning is defined by sender and receiver.

---

### 2.3 GET /api/recv/\<name\>

Poll for pending commands. Returns all queued commands and clears the queue. Also acts as a heartbeat (updates `lastSeen`).

**Response (200):**
```json
{
  "ok": true,
  "commands": [
    {
      "id": 42,
      "from": "NLPBridge",
      "to": "Tank1",
      "type": "grind",
      "data": { "duration": 30 },
      "timestamp": "2025-03-28T14:30:00.0000000+00:00"
    }
  ]
}
```

**Notes:**
- Commands are consumed on poll — calling again returns an empty array until new commands arrive.
- If the agent was previously pruned (timed out), polling auto-re-registers it with `role = "agent"`.
- The `<name>` path segment must be URL-encoded if it contains special characters.

---

### 2.4 POST /api/heartbeat/\<name\>

Keep-alive signal. Updates `lastSeen` without polling commands.

**Response (200):**
```json
{ "ok": true }
```

**Error (404):** Agent not registered.
```json
{ "ok": false, "error": "unknown agent" }
```

**Notes:**
- Not strictly required if the agent is already polling via `/api/recv`, since polling also updates `lastSeen`.
- Useful for agents that want to stay alive without consuming commands.

---

### 2.5 GET /api/agents

List all registered agents with online/offline status.

**Response (200):**
```json
{
  "ok": true,
  "agents": [
    {
      "name": "Tank1",
      "role": "tank",
      "ip": "192.168.1.50",
      "lastSeen": "2025-03-28T14:30:00.0000000+00:00",
      "online": true
    },
    {
      "name": "DPS1",
      "role": "dps",
      "ip": "192.168.1.51",
      "lastSeen": "2025-03-28T14:25:00.0000000+00:00",
      "online": false
    }
  ]
}
```

**Notes:**
- `online` is computed as: `(now - lastSeen) < Timeout` (default timeout: 120 seconds).
- `ip` is the remote IP address from the registration/last request.

---

### 2.6 GET /api/status

Relay server statistics.

**Response (200):**
```json
{
  "ok": true,
  "uptime": 3600,
  "agentsTotal": 5,
  "agentsOnline": 3,
  "commandsTotal": 142,
  "commandsQueued": 2
}
```

| Field | Type | Description |
|-------|------|-------------|
| `uptime` | int | Seconds since server start |
| `agentsTotal` | int | Total registered agents (including offline) |
| `agentsOnline` | int | Agents with `lastSeen` within timeout |
| `commandsTotal` | int | Total commands ever sent (monotonic counter) |
| `commandsQueued` | int | Commands currently sitting in queues |

---

### 2.7 DELETE /api/agent/\<name\>

Manually unregister an agent and remove its queue.

**Response (200):**
```json
{ "ok": true }
```

---

### 2.8 GET /

Info endpoint. Returns plain text.

```
LuaComm Relay Server v1.0 | Agents: 5 | Commands: 142
```

---

## 3. Relay Server Configuration

The relay is started via `relay.ps1` (or `start_relay.bat`).

| Parameter | Default | Description |
|-----------|---------|-------------|
| `-Port` | `19850` | TCP port to listen on |
| `-Timeout` | `120` | Seconds before an agent is considered offline and pruned |

### First-time setup (Windows)

The relay uses `System.Net.HttpListener` which requires a URL reservation on non-admin accounts:

```powershell
# Run ONCE as Administrator:
netsh http add urlacl url=http://+:19850/ user=Everyone
```

Or run `start_relay.bat` as Administrator.

### Agent pruning

The relay prunes stale agents on every incoming request. When an agent's `lastSeen` exceeds the timeout, it is removed along with its command queue. If a pruned agent starts polling again, it is auto-re-registered with `role = "agent"`.

---

## 4. Lua Client API (`luacomm.lua`)

### 4.1 Loading

```lua
local LuaComm = loadfile(ml_global_information.path .. "\\LuaComm\\luacomm.lua")()
```

Returns a singleton table. All methods are called with `:` syntax.

### 4.2 Setup & Lifecycle

#### `LuaComm:setup(host, port, name, role)` → self

Initialize the communication system. Must be called before anything else.

| Param | Type | Description |
|-------|------|-------------|
| `host` | string | Relay server IP (e.g. `"192.168.1.100"`) |
| `port` | number | Relay port (default `19850`) |
| `name` | string | Unique agent name (e.g. `"Tank1"`) |
| `role` | string | Role tag: `"dps"`, `"tank"`, `"healer"`, `"commander"`, etc. Default: `"agent"` |

**Side effects:**
- Resets registration state.
- Determines temp directory for curl POST body files.
- Registers a built-in `"exec"` callback for remote code execution from LuaCommander.

#### `LuaComm:update()` → table (list of commands)

**Call this every frame/tick from your main loop.** Handles:
1. Auto-registration (if not yet registered).
2. Polling for commands at the configured frame interval.
3. Sending heartbeats at the configured frame interval.
4. Dispatching received commands to registered callbacks.

Returns the list of commands received this tick (same as `poll()`). Commands with registered callbacks are also dispatched automatically.

#### `LuaComm:register()` → bool

Manually register with the relay. Called automatically by `update()` if needed. Returns `true` on success.

### 4.3 Sending Commands

#### `LuaComm:send(target, cmdType, data)` → table|nil

Send a command to a specific agent.

| Param | Type | Description |
|-------|------|-------------|
| `target` | string | Agent name, `"*"` for broadcast, or `"role:dps"` for role targeting |
| `cmdType` | string | Command type string (e.g. `"grind"`, `"stop"`, `"status_report"`) |
| `data` | table | Command payload (optional, defaults to `{}`) |

Returns the relay response (`{ok=true, id=N, delivered={...}}`) or `nil` on failure.

#### `LuaComm:broadcast(cmdType, data)` → table|nil

Shorthand for `send("*", cmdType, data)`. Sends to all agents except self.

#### `LuaComm:sendToRole(role, cmdType, data)` → table|nil

Shorthand for `send("role:" .. role, cmdType, data)`. Sends to all agents with matching role, except self.

### 4.4 Receiving Commands

#### `LuaComm:on(cmdType, handler)` → self

Register a callback for a command type. The handler receives the full command object.

```lua
LuaComm:on("grind", function(cmd)
    -- cmd.type  = "grind"
    -- cmd.from  = "NLPBridge"
    -- cmd.to    = "Tank1"
    -- cmd.data  = { duration = 30 }
    -- cmd.id    = 42
    -- cmd.timestamp = "2025-03-28T14:30:00..."
end)
```

**Notes:**
- Only one handler per type. Setting a new handler replaces the old one.
- Callbacks are invoked by `update()` / `poll()` via `pcall` — errors are logged but don't crash.
- The built-in `"exec"` handler is registered by `setup()` and can be overridden.

#### `LuaComm:off(cmdType)` → self

Remove a callback for a command type.

#### `LuaComm:poll()` → table (list of commands)

Manually poll the relay for pending commands. Usually not needed — `update()` calls this automatically. Commands are consumed on poll.

Returns a list of command objects:
```lua
{
    { id = 42, from = "NLPBridge", to = "Tank1", type = "grind", data = {...}, timestamp = "..." },
    { id = 43, from = "NLPBridge", to = "*",     type = "stop",  data = {},    timestamp = "..." },
}
```

### 4.5 Agent Discovery

#### `LuaComm:agents()` → table (list of agent info)

Get all registered agents from the relay.

```lua
local agents = LuaComm:agents()
for _, a in ipairs(agents) do
    -- a.name, a.role, a.ip, a.online, a.lastSeen
end
```

#### `LuaComm:status()` → table|nil

Get relay server statistics (uptime, agent counts, command counts).

### 4.6 Configuration

#### `LuaComm:setDebug(enabled)` → self

Enable/disable verbose debug logging to the MMOMinion console via `d()`.

#### `LuaComm:setPollInterval(frames)` → self

Set how often `update()` polls for commands. Frame-based.

| Default | Approx. real time |
|---------|-------------------|
| `15` frames | ~0.5s at 30fps, ~0.23s at 65fps |

#### `LuaComm:setHeartbeatInterval(frames)` → self

Set how often `update()` sends heartbeats.

| Default | Approx. real time |
|---------|-------------------|
| `300` frames | ~10s at 30fps, ~4.6s at 65fps |

### 4.7 JSON Utility

LuaComm embeds a JSON encoder/decoder accessible as:

```lua
local json_string = LuaComm.JSON.encode({ key = "value", num = 42 })
local table = LuaComm.JSON.decode('{"key":"value","num":42}')
```

Supports: strings, numbers, booleans, null, nested objects/arrays. Does not require any external dependencies.

### 4.8 Internal Details

- HTTP is performed via `curl` (synchronous `io.popen`). The curl timeout is 2 seconds.
- POST bodies are written to a temp file (`%TEMP%\_luacomm_post.tmp`) to avoid shell escaping issues.
- Logging uses the MMOMinion `d()` function if available.

---

## 5. Command Object Schema

This is the shape of a command as it flows through the system. The relay creates it from a `/api/send` request and queues it for the target agent(s).

```
{
    "id":        integer   -- relay-assigned, auto-incrementing
    "from":      string    -- sender's agent name
    "to":        string    -- target (agent name, "*", or "role:xxx")
    "type":      string    -- command type (opaque to relay)
    "data":      object    -- command payload (opaque to relay)
    "timestamp": string    -- ISO 8601 datetime
}
```

The `type` and `data` fields have no meaning to the relay — it just routes them. Our project defines these types:

### Commands we send (Python → agent)

| type | data fields | Description |
|------|-------------|-------------|
| `grind` | `duration`, `fates` | Start grind mode |
| `gather` | `node_type`, `item` | Start gather mode |
| `fate` | `duration` | Start FATE farming |
| `navigate` | `destination`, `aetheryte` | Teleport or move |
| `craft` | `item`, `quantity` | Start crafting |
| `duty` | `duty_name`, `duty_type` | Queue for duty (stub) |
| `stop` | — | Stop all activity |
| `status` | — | Request status report |

### Messages agents send back (agent → Python)

| type | data fields | Description |
|------|-------------|-------------|
| `task_result` | `task`, `success`, `message`, `command_id` | Execution result |
| `status_report` | `name`, `role`, `mode`, `running`, `hp`, `pos`, `zone` | Agent state |
| `exec_result` | `success`, `error`, `agent` | Remote code execution result (LuaCommander) |

---

## 6. Built-in "exec" Handler

LuaComm registers a built-in handler for `type = "exec"` during `setup()`. This allows remote code execution from LuaCommander or any other commander:

**Send:**
```json
{
  "from": "LuaCommander",
  "to": "Agent1",
  "type": "exec",
  "data": { "code": "d('Hello from remote!')" }
}
```

The agent compiles and runs the code via `loadstring()` + `pcall()`. Results (success or error) are logged locally. The example `agent.lua` also sends an `exec_result` message back.

**Security note:** This executes arbitrary Lua code. It's designed for LAN/trusted environments only.

---

## 7. Integration Patterns

### 7.1 Python Service as Commander (our use case)

```python
import httpx

RELAY = "http://192.168.1.100:19850"
NAME = "NLPBridge"

# Register on startup
await client.post(f"{RELAY}/api/register", json={"name": NAME, "role": "commander"})

# Send a command to a specific agent
await client.post(f"{RELAY}/api/send", json={
    "from": NAME,
    "to": "Tank1",
    "type": "grind",
    "data": {"duration": 30}
})

# Send to all DPS
await client.post(f"{RELAY}/api/send", json={
    "from": NAME,
    "to": "role:dps",
    "type": "attack",
    "data": {"target": "Boss"}
})

# Broadcast stop to everyone
await client.post(f"{RELAY}/api/send", json={
    "from": NAME,
    "to": "*",
    "type": "stop",
    "data": {}
})

# Poll for results sent back to us
resp = await client.get(f"{RELAY}/api/recv/{NAME}")
commands = resp.json().get("commands", [])
for cmd in commands:
    if cmd["type"] == "task_result":
        # Handle execution result
    elif cmd["type"] == "status_report":
        # Cache agent state

# Heartbeat (run periodically)
await client.post(f"{RELAY}/api/heartbeat/{NAME}", json={})

# List online agents
resp = await client.get(f"{RELAY}/api/agents")
agents = resp.json().get("agents", [])
```

### 7.2 Lua Agent with NLP Task Handlers (our use case)

```lua
local LuaComm = loadfile(ml_global_information.path .. "\\LuaComm\\luacomm.lua")()
LuaComm:setup("192.168.1.100", 19850, Player.name or "Agent1", "dps")

LuaComm:on("grind", function(cmd)
    gBotMode = "grind"
    FFXIV_Common_BotRunning = true
    LuaComm:send(cmd.from, "task_result", {
        task = "grind", success = true, message = "Started grinding"
    })
end)

LuaComm:on("stop", function(cmd)
    FFXIV_Common_BotRunning = false
    LuaComm:send(cmd.from, "task_result", {
        task = "stop", success = true, message = "Stopped"
    })
end)

LuaComm:on("status", function(cmd)
    LuaComm:send(cmd.from, "status_report", {
        name = LuaComm._name,
        role = LuaComm._role,
        mode = gBotMode or "unknown",
        running = FFXIV_Common_BotRunning == true,
    })
end)

function NLPAgent_Pulse()
    LuaComm:update()
end
RegisterEventHandler("Gameloop.Update", NLPAgent_Pulse, "NLPAgent.Pulse")
```

---

## 8. Failure Modes & Edge Cases

| Scenario | Behavior |
|----------|----------|
| Relay is down | `send()`/`poll()` return `nil`. Curl times out after 2s. |
| Agent not registered | `/api/send` returns `delivered: []` — command is silently dropped. |
| Agent times out (no heartbeat/poll for 120s) | Relay prunes agent and its queue. Next poll auto-re-registers with `role = "agent"`. |
| Duplicate agent name | Second registration overwrites the first. Queue is preserved. |
| Send to non-existent role | `delivered: []` — no error, just no recipients. |
| Command sent while agent offline | Command is dropped (agent has no queue after pruning). |
| Very large `data` payload | No explicit limit in relay, but curl has practical limits. Keep payloads reasonable. |

---

## 9. LuaCommander (Desktop GUI)

LuaCommander is a Delphi VCL application that provides a graphical interface for managing agents. It's optional for our use case but useful for debugging.

### Features
- Agent list with online/offline status (polls `/api/agents`)
- Send commands to specific agents, roles, or broadcast
- Remote Lua code execution (sends `exec` commands)
- Command editor with categories
- Execution log viewer
- Settings: relay host/port, database connection, file sync

### Key Files
| File | Purpose |
|------|---------|
| `Source/Forms/uFrmMain.pas` | Main window — agent grid, command grid, execute button |
| `Source/Forms/uFrmCommandEditor.pas` | Create/edit stored commands |
| `Source/Forms/uFrmSettings.pas` | Relay + database configuration |
| `Source/Forms/uFrmLogViewer.pas` | Execution history |
| `Source/Services/uRelayClient.pas` | HTTP client wrapping relay API |
| `Source/Services/uSettingsManager.pas` | INI-based settings persistence |
| `Source/Services/uFileSyncService.pas` | File sync service |
| `Source/Models/uModels.pas` | Data models (TAgentInfo, TSendResult, etc.) |
| `Source/Utils/uConsts.pas` | Constants (ports, timeouts, colors) |

### Default Constants
| Constant | Value |
|----------|-------|
| `DEFAULT_RELAY_PORT` | `19850` |
| `DEFAULT_POLL_MS` | `3000` |
| `DEFAULT_CMD_NAME` | `"LuaCommander"` |
| `HTTP_CONNECT_TIMEOUT` | `3000` ms |
| `HTTP_RESPONSE_TIMEOUT` | `5000` ms |
| `AGENT_OFFLINE_THRESHOLD` | `30` s |
