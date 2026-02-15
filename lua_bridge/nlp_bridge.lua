--[[
  NLPBridge - Natural language command bridge for FFXIVMinion.
  Polls the Python NLP service for parsed commands and executes them.
]]

NLPBridge = {}
NLPBridge.version = "1.0"
NLPBridge.config = {
    host = "192.168.1.137",
    port = 8000,
    poll_interval = 2000,  -- ms between polls
    enabled = true,
}

-- State
local last_poll = 0
local polling = false  -- guards against overlapping requests

--------------------------------------------------------------------------------
-- Logging
--------------------------------------------------------------------------------

local function log(msg)
    d("[NLPBridge] " .. tostring(msg))
end

local function log_error(msg)
    d("[NLPBridge ERROR] " .. tostring(msg))
end

--------------------------------------------------------------------------------
-- HTTP helpers
--------------------------------------------------------------------------------

local function api_url(path)
    return NLPBridge.config.host, path, NLPBridge.config.port
end

local function post_result(command_id, success, message, status_info)
    local body = json.encode({
        command_id = command_id,
        success = success,
        message = message or "",
        status = status_info or {},
    })

    local host, path, port = api_url("/minion/result")
    HttpRequest({
        host = host,
        path = path,
        port = port,
        method = "POST",
        body = body,
        headers = { ["Content-Type"] = "application/json" },
        onsuccess = function() end,
        onfailure = function(err)
            log_error("Failed to post result: " .. tostring(err))
        end,
    })
end

local function get_bot_status()
    local status = {
        mode = gBotMode or "unknown",
        running = FFXIV_Common_BotRunning == true,
    }

    if Player then
        status.player = {
            name = Player.name or "",
            level = Player.level or 0,
            job = Player.job or 0,
            hp_percent = Player.hp and Player.hp.percent or 0,
            map_id = Player.localmapid or 0,
        }
        if Player.pos then
            status.pos = {
                x = Player.pos.x or 0,
                y = Player.pos.y or 0,
                z = Player.pos.z or 0,
            }
        end
    end

    return status
end

--------------------------------------------------------------------------------
-- Task handlers
--------------------------------------------------------------------------------

local handlers = {}

function handlers.grind(params, command_id)
    log("Starting grind mode")

    if params.target then
        -- Can't easily set target filter from Lua, but log intent
        log("Target preference: " .. tostring(params.target))
    end

    ffxivminion.SetMode("grindMode")

    if not FFXIV_Common_BotRunning then
        ml_global_information.ToggleRun()
    end

    post_result(command_id, true, "Grind mode started", get_bot_status())
end

function handlers.gather(params, command_id)
    log("Starting gather mode")

    if params.node_type then
        log("Node type: " .. tostring(params.node_type))
    end
    if params.item then
        log("Item: " .. tostring(params.item))
    end

    ffxivminion.SetMode("gatherMode")

    if not FFXIV_Common_BotRunning then
        ml_global_information.ToggleRun()
    end

    post_result(command_id, true, "Gather mode started", get_bot_status())
end

function handlers.fate(params, command_id)
    log("Starting FATE grinding")

    -- FATE mode is grind mode with FATE settings
    gGrindDoFates = true
    gGrindFatesOnly = true
    gGrindDoBattleFates = true
    gGrindDoBossFates = true

    ffxivminion.SetMode("grindMode")

    if not FFXIV_Common_BotRunning then
        ml_global_information.ToggleRun()
    end

    post_result(command_id, true, "FATE grind started", get_bot_status())
end

function handlers.navigate(params, command_id)
    local dest = params.destination or ""
    log("Navigating to: " .. dest)

    if params.aetheryte then
        -- Use teleport task for aetheryte destinations
        local task = ffxiv_task_teleport.Create()
        if task then
            task.destName = dest
            ml_task_hub:Add(task.Create(), IMMEDIATE_GOAL, TP_IMMEDIATE)
            post_result(command_id, true, "Teleporting to " .. dest, get_bot_status())
        else
            post_result(command_id, false, "Failed to create teleport task")
        end
    else
        -- Use movetomap for general navigation
        local task = ffxiv_task_movetomap.Create()
        if task then
            task.destName = dest
            ml_task_hub:Add(task.Create(), IMMEDIATE_GOAL, TP_IMMEDIATE)
            post_result(command_id, true, "Moving to " .. dest, get_bot_status())
        else
            post_result(command_id, false, "Failed to create move task")
        end
    end
end

function handlers.duty(params, command_id)
    local duty_name = params.duty_name or ""
    log("Duty: " .. duty_name)

    -- Duty finder integration varies by FFXIVMinion version
    -- For now, report as accepted but note limitations
    post_result(command_id, false,
        "Duty finder not yet implemented. Duty: " .. duty_name,
        get_bot_status())
end

function handlers.craft(params, command_id)
    local recipe = params.recipe or ""
    local count = params.count or 1
    log("Crafting: " .. recipe .. " x" .. tostring(count))

    ffxivminion.SetMode("craftMode")

    if not FFXIV_Common_BotRunning then
        ml_global_information.ToggleRun()
    end

    post_result(command_id, true,
        "Craft mode started: " .. recipe .. " x" .. tostring(count),
        get_bot_status())
end

function handlers.stop(params, command_id)
    log("Stopping bot")

    if FFXIV_Common_BotRunning then
        ml_global_information.ToggleRun()
    end

    post_result(command_id, true, "Bot stopped", get_bot_status())
end

function handlers.status(params, command_id)
    local status = get_bot_status()
    log("Status: mode=" .. tostring(status.mode) .. " running=" .. tostring(status.running))
    post_result(command_id, true, "Status report", status)
end

--------------------------------------------------------------------------------
-- Command dispatch
--------------------------------------------------------------------------------

local function handle_command(data)
    local command_id = data.command_id
    local task = data.task
    local params = data.params or {}

    log("Received command " .. tostring(command_id) .. ": " .. tostring(task))

    local handler = handlers[task]
    if handler then
        local ok, err = pcall(handler, params, command_id)
        if not ok then
            log_error("Handler error for " .. task .. ": " .. tostring(err))
            post_result(command_id, false, "Execution error: " .. tostring(err))
        end
    else
        log_error("Unknown task type: " .. tostring(task))
        post_result(command_id, false, "Unknown task type: " .. tostring(task))
    end
end

--------------------------------------------------------------------------------
-- Polling loop
--------------------------------------------------------------------------------

local function poll()
    if polling then return end
    polling = true

    local host, path, port = api_url("/minion/pending")
    HttpRequest({
        host = host,
        path = path,
        port = port,
        method = "GET",
        onsuccess = function(body, headers, status_code)
            polling = false
            if status_code == 204 or not body or body == "" then
                return  -- no pending commands
            end

            local ok, data = pcall(json.decode, body)
            if ok and data and data.command_id then
                handle_command(data)
            elseif not ok then
                log_error("Failed to decode response: " .. tostring(data))
            end
        end,
        onfailure = function(err)
            polling = false
            -- Silently ignore connection failures (service might be down)
        end,
    })
end

--------------------------------------------------------------------------------
-- Update loop (called by FFXIVMinion main loop)
--------------------------------------------------------------------------------

function NLPBridge.OnUpdate()
    if not NLPBridge.config.enabled then return end

    local now = Now()
    if TimeSince(last_poll) < NLPBridge.config.poll_interval then
        return
    end
    last_poll = now

    poll()
end

--------------------------------------------------------------------------------
-- Init
--------------------------------------------------------------------------------

function NLPBridge.Init()
    log("NLPBridge v" .. NLPBridge.version .. " loaded")
    log("Polling " .. NLPBridge.config.host .. ":" .. NLPBridge.config.port)

    -- Register update handler
    RegisterEventHandler("Gameloop.Update", NLPBridge.OnUpdate, "NLPBridge.OnUpdate")
end

-- Auto-init on load
NLPBridge.Init()
