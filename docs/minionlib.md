# MinionLib Lua Documentation

> Source: https://wiki.mmominion.com/doku.php?id=minionlib
> Last modified: 2021/04/30

The minionlib library holds the core functionality on which all bots run. To use it in your addon, set the dependency in your `module.def`:

```ini
[Module]
Name=YourAddon
Dependencies=minionlib
Version=1
Files=myluacode.lua
Enabled=1
```

---

## Minion Menu

The Minion Menu is the main menu used to access all settings and addons. 3rd-party developers can add custom options.

### Structure

The menu has 3 layers: **Components**, **Members**, and **Submembers**.

**Component Headers** (required properties):
- `expanded` (*bool*)
- `name` (*string*)
- `id` (*string*)
- `texture` (*string*, optional)

**Members** (displayed below component headers):
- `name` (*string*, required)
- `id` (*string*, required)
- `texture` (*string*, optional)
- `tooltip` (*string*, optional)
- `onClick` (*function*, optional)
- `sort` (*bool*, optional)

**Submembers** (displayed to the right, grow vertically):
- Sorted alphabetically if parent member has `sort = true`
- `name` (*string*, required)
- `id` (*string*, required)
- `texture` (*string*, optional)
- `tooltip` (*string*, optional)
- `onClick` (*function*, optional)

### Menu API

```lua
ml_gui.ui_mgr:AddComponent(table component)
ml_gui.ui_mgr:AddMember(table member, string componentid)
ml_gui.ui_mgr:AddSubMember(table submember, string componentid, string memberid)
```

### Example

```lua
local ffxiv_mainmenu = {
    header = {
        id = "FFXIVMINION##MENU_HEADER",
        expanded = false,
        name = "FFXIVMinion",
        texture = GetStartupPath().."\\GUI\\UI_Textures\\ffxiv_shiny.png"
    },
    members = {}
}

ml_gui.ui_mgr:AddComponent(ffxiv_mainmenu)

ml_gui.ui_mgr:AddMember({
    id = "FFXIVMINION##MENU_DEV1",
    name = "Dev1",
    onClick = function() Dev.GUI.open = not Dev.GUI.open end,
    tooltip = "Open the Dev monitor."
}, "FFXIVMINION##MENU_HEADER")

ml_gui.ui_mgr:AddMember({
    id = "FFXIVMINION##MENU_DEV5",
    name = "Dev5",
    onClick = function() Dev.GUI.open = not Dev.GUI.open end,
    sort = true
}, "FFXIVMINION##MENU_HEADER")

ml_gui.ui_mgr:AddSubMember({
    id = "FFXIVMINION##DEV_1",
    name = "DevA",
    onClick = function() Dev.GUI.open = not Dev.GUI.open end,
    tooltip = "Open the Dev monitor."
}, "FFXIVMINION##MENU_HEADER", "FFXIVMINION##MENU_DEV5")
```

---

## Utility Functions

### General

### `d(...)`
- Prints variable or function result to console.

### `stacktrace()`
- Prints current call stack to console.

### `Exit()`
- Closes the current game instance.

### `ml_debug(string str)`
- Prints to console when `gEnableLog == "1"`.

### `ml_error(string str)`
- Prints to console.

### `ml_log(string str)`
- Adds string to the statusbar line shown on each pulse.

### `Now()`
- Returns tickcount from `ml_global_information.Now`.

### `RegisterEventHandler(string event, function handler, string customName)`
- Registers a local handler to an event.

### `Reload()`
- Returns *bool*. Reloads all lua modules.

### `TimeSince(integer previousTime)`
- Returns *integer* `ml_global_information.Now - previousTime`.

### `Unload()`
- Returns *bool*. Tries to unload the bot.

### `QueueEvent(string eventname, string args, ...)`
- Queues and fires an event with 1-n string arguments.
- Use `RegisterEventHandler("eventname", handlerfunc)` to handle it.
- Requires at least 1 argument, even if blank: `QueueEvent("some event", "")`

---

### File I/O

> **Use double backslashes for all paths!** Example: `FolderExists("c:\\minionapp\\ILikeBeer\\Folder")`

### `GetStartupPath()` → *string*
- Filepath to the root bot folder.

### `GetLuaModsPath()` → *string*
- Filepath to `MinionApp/Bots/xxxx/LuaMods` folder.

### `FileExists(string fullpathtofile)` → *bool*

### `FileLoad(string fullpathtofile)` → *variant*
- Loads a file saved with FileSave.

### `FileSave(string fullpathtofile, variant data)` → *bool*
- Can take a lua table; saves the whole structure in human-readable format.

### `FileWrite(string fullpathtofile, string data)` → *bool*

### `FileWrite(string fullpathtofile, string data, bool append)` → *bool*
- If 3rd arg is true, appends data to end of file.

### `FileDelete(string fullpathtofile)` → *bool*
### `FileIsValidImage(string fullpathtofile)` → *bool*
### `FileSize(string fullpathtofile)` → *number*
### `FolderExists(string fullpathtofolder)` → *bool*
### `FolderCreate(string fullpathtofolder)` → *bool*
### `FolderDelete(string fullpathtofolder)` → *bool*

### `FolderList(string fullpathtofolder, string pattern, bool includeFolders)` → *table*
- Pattern is normal regex in double brackets: `[[(.*).lua$]]`
- Returns table of all files in directory.

---

### String Extensions

Usage: `string.contains(arg, arg2)`

### `string.contains(string arg, string arg2)` → *bool*
### `string.empty(string arg)` → *bool* — true if type is string and length is 0
### `string.ends(string arg, string arg2)` → *bool*
### `string.split(string arg, string separator)` → *iterator*
```lua
for item in string.split(mystring, ",") do ... end
```
### `string.starts(string arg, string arg2)` → *bool*
### `string.toboolean(string arg)` → *bool*
### `string.totable(string arg, string separator)` → *table*
### `string.trim(string arg, int num)` → *string* — trims by num characters
### `string.valid(string arg)` → *bool* — true if arg is type string
### `string.hash(string arg)` → *number* — MD5 encoded number

---

### Table Extensions

Usage: `table.valid(arg)`

### `table.clear(table arg)` — sets all values to nil
### `table.contains(table tbl, value)` → *bool*
### `table.deepcopy(table arg, bool skipMetaTable)` → *table*
### `table.deepcompare(table t1, table t2, bool ignore_metatable)` → *bool*
### `table.delete(table tbl, variant object)` → *bool*
### `table.find(table tbl, value)` → *number* or nil — returns key position
### `table.invert(table arg)` → *table* — keys become values
### `table.merge(table t1, table t2, bool keepexistingentries)` → *table*
- Without keepexistingentries, t1 keys are overwritten by t2. With it, t2 values are just inserted.

### `table.pairsbykeys(table t1, function sort)` → *iterator*
```lua
for key, value in table.pairsbykeys(mytable) do ... end
```

### `table.pairsbyvalue(table t1, function sort)` → *iterator*
### `table.print(table arg)` — prints content line by line to console
### `table.randomvalue(table arg)` → random value from table
### `table.shallowcopy(table arg)` → *table*
### `table.size(table arg)` → *number* — returns 0 if not a table
### `table.valid(table arg)` → *bool* — true if valid table with at least 1 entry

---

### Math Extensions

Usage: `math.distance3d(...)`

### `math.angle(table heading1, table heading2)` → *number*
- Shortest angle between two headings (tables with x,y,z). Result: 0-180 degrees.

### `math.approxequal(number num1, number num2)` → *bool*
### `math.crossproduct(table pos1, table pos2)` → *table*
### `math.distance2d(number x, number y, number x1, number y1)` → *number*
### `math.distance3d(table pos1, table pos2)` → *number*
### `math.distance3d(number x, number y, number z, number x1, number y1, number z1)` → *number*
### `math.distancepointline(table p1, table p2, table p3)` → *number*
- First two points define the line, third is the point to measure distance from.

### `math.magnitude(table pos)` → *number*
### `math.round(number num, integer decimals)` → *number*
### `math.randomize(integer int)` → *integer*
- Takes percentage 0-100, returns random number near that value.

---

### Navigation

### `PathDistance(table posTable)` → *number*
```lua
PathDistance(NavigationManager:GetPath(myPos.x, myPos.y, myPos.z, p.x, p.y, p.z))
```

---

## HTTPRequest

Asynchronous HTTP calls via `HttpRequest(params)`.

### Example

```lua
function SendHttpRequest()
    local function success(str, header, statuscode)
        d("HTTP Request: success.")
        d("HTTP Result Header: " .. tostring(header))
        d("HTTP Result StatusCode: " .. tostring(statuscode))

        local data = json.decode(str)
        if data then
            d("HTTP Request: data valid.")
            d(data)
        end

        local function HeadersTable(header)
            if type(header) == "string" and #header > 0 then
                header = string.match(header, ".?%c(.*)")
                local tbl = {}
                for w in header:gmatch("[^%c]+") do
                    local k, v = string.match(w, "(.*): (.*)")
                    tbl[k] = v
                end
                table.print(tbl)
                return tbl
            end
        end

        header = HeadersTable(header)
    end

    local function failed(error, header, statuscode)
        d("HTTP Failed Error: " .. error)
        d("HTTP Failed Header: " .. header)
        d("HTTP Failed StatusCode: " .. tostring(statuscode))
    end

    local params = {
        host = "api.guildwars2.com",
        path = "/v2/currencies?ids=1",
        port = 443,
        method = "GET",  -- "GET","POST","PUT","DELETE"
        https = true,
        onsuccess = success,
        onfailure = failed,
        getheaders = true,
        body = "",       -- optional
        headers = {},    -- optional
    }

    HttpRequest(params)
end
```

### HttpRequest Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `host` | string | Hostname |
| `path` | string | URL path |
| `port` | number | Port number |
| `method` | string | "GET", "POST", "PUT", "DELETE" |
| `https` | bool | Use HTTPS |
| `onsuccess` | function | Callback: `function(str, header, statuscode)` |
| `onfailure` | function | Callback: `function(error, header, statuscode)` |
| `getheaders` | bool | Return headers (optional) |
| `body` | string | Request body (optional) |
| `headers` | table | Request headers (optional) |
