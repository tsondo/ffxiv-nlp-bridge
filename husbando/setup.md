These APIs allow your addon to access protected globals. Access requires a base key issued to your developer account.

Your base key must only exist inside your encrypted addon. Never expose it in plain text, logs, or pass it to any API function directly.
Token Management
Copy this block into your main addon file once. All scopes share one batch request per refresh cycle.

You should then pass this to your other files internally. Don't ever set these functions globally.

-- Paste once in your main addon file.
-- All GetHMToken calls share this state in the running file. You can put this in each file but its not optimal to do so.

-- SessionTokens is keyed by scope name, each entry holds { token, expires }
-- e.g. SessionTokens["DungeonMasterSettings"] = { token = "uuid", expires = 1234567890 }
local SessionTokens       = {}
local LastTokenCheck      = 0
local TokenRefreshPending = false

local function RefreshTokenBatch(baseKey)
    if TokenRefreshPending then return end
    TokenRefreshPending = true

    -- Collect old tokens to invalidate server-side
    local oldTokens = {}
    for scope, entry in pairs(SessionTokens) do
        if entry.token then
            oldTokens[#oldTokens + 1] = entry.token
        end
    end

    local Data = {
        ["action"]    = "getSessionTokenBatch",
        ["baseKey"]   = baseKey,
        ["oldTokens"] = oldTokens,
    }
    local Request = {
        ["host"]    = "husbandomax.com",
        ["path"]    = "/api/trialmanager",
        ["port"]    = 443,
        ["https"]   = true,
        ["method"]  = "POST",
        ["headers"] = { ["Content-Type"] = "application/json" },
        ["body"]    = HusbandoMaxJSON.encode(Data),
        ["onsuccess"] = function(content, header, statuscode)
            local ok, result = pcall(HusbandoMaxJSON.decode, content)
            if ok and result and result.tokens then
                -- result.tokens = { ["DungeonMasterSettings"] = { token="...", expires=... }, ... }
                for scope, entry in pairs(result.tokens) do
                    SessionTokens[scope] = { token = entry.token, expires = entry.expires }
                end
            end
            TokenRefreshPending = false
        end,
        ["onfailure"] = function(error, header, statuscode)
            TokenRefreshPending = false
        end,
    }
    HusbandoMax.Server.AddRequestToList("_99#py#Bd?42Sd^=jb-7BGh9wy%tNeqr=%cxfDKpE*uhC4c@4?", Request, 1)
    LastTokenCheck = HusbandoMax.ServerTime
end

-- Returns the current session token for a given scope.
-- baseKey: your permanent key — keep this inside your encrypted addon only
-- scope:   the API being accessed e.g. "DungeonMasterSettings"
local function GetHMToken(baseKey, scope)
    local now   = HusbandoMax.ServerTime
    local entry = SessionTokens[scope]
    if entry and entry.token and entry.expires and (entry.expires - 300) > now then
        return entry.token  -- Token valid with > 5 min remaining, no refresh needed
    end
    if LastTokenCheck + 60 > now then
        return entry and entry.token or nil  -- Rate limit: refresh attempted recently
    end
    RefreshTokenBatch(baseKey)  -- Token missing, expired, or expiring soon
    return entry and entry.token or nil  -- Return stale token if available while waiting
end
Call GetHMToken("YOUR_BASE_KEY", scope) at init to pre-warm the cache. Multiple scopes are fetched in a single request — no extra calls per scope.
