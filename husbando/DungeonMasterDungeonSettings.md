DungeonMasterDungeonSettings
DungeonMasterDungeonSettings(AccessKey, Setting, Value, Debug)
Reads or writes the NewDungeonSelection table on DungeonMaster — the dungeon list configuration for all operating modes. Requires a valid session token with the DungeonMasterDungeonSettings scope.

Parameters
Parameter	Type	Description
AccessKey	string	A valid session token obtained via GetHMToken.
Setting	string | nil	The top-level key to read or write. Pass nil to return the full table.
Value	any | nil	The value to write. Pass nil to read instead.
Debug	bool | nil	If true, prints token validation info to the console.
Return Values
Call Pattern	Returns
DungeonMasterDungeonSettings(key)	Full NewDungeonSelection table
DungeonMasterDungeonSettings(key, "Setting")	NewDungeonSelection["Setting"] (read)
DungeonMasterDungeonSettings(key, "Setting", value)	(no return, writes the value)
Token invalid	nil
NewDungeonSelection Reference
Top-Level Keys
Key	Type	Description
QuickStart	table	The single duty selected for Quick Start mode.
JobManager	table	The single duty used when Job Manager mode is running.
DungeonManagerList	array	List of duties for Dungeon Manager mode.
DungeonManagerCustomItemsList	array	List of duties for Dungeon Manager Custom Items mode.
JobLevelManagerList	array	List of duties for Job Level Manager mode.
QuickStart / JobManager
Both are a single entry with no RunData.

Field	Type	Description
DungeonData.Name	string	Display name of the selected duty.
DungeonData.Type	string	Content category e.g. "Trusts", "DutySupport".
DungeonData.UniqueID	string	Stable unique ID matching the content list.
Settings.DetectionRange	number	1=Small, 2=Medium, 3=Large.
Settings.ForceMeleeRange	bool	Forces ranged classes into melee range.
Settings.Undersize	bool	Enable undersized queue option.
Settings.AllowInteract	bool	Allow interaction on objectives.
Settings.ForceSquadronTank	bool	Force squadron tank to pick up adds.
Settings.PullSize	number	Target mob pull count. 0 = default.
-- Example
selection.QuickStart = {
    DungeonData = {
        Name     = "Mistwake",
        Type     = "DutySupport",
        UniqueID = "1064_DutySupport_1314",
    },
    Settings = {
        AllowInteract    = true,
        DetectionRange   = 3,
        ForceMeleeRange  = true,
        ForceSquadronTank= false,
        PullSize         = 0,
        Undersize        = true,
    },
}
DungeonManagerList entries
Each entry in the array has DungeonData, Settings (same fields as above), and a RunData block.

RunData Field	Type	Description
Use	bool	Whether this entry is active in the list.
Complete	number	How many runs of this entry have been completed.
Count	number	Target number of runs for this entry.
Job	number	Job index to use for this entry. 0 = current job.
-- Example entry
{
    DungeonData = {
        Name     = "Sohm Al",
        Type     = "Squadrons",
        UniqueID = "37_Squadrons_1064",
    },
    RunData = {
        Use      = true,
        Complete = 0,
        Count    = 1,
        Job      = 30,
    },
    Settings = {
        AllowInteract    = true,
        DetectionRange   = 2,
        ForceMeleeRange  = false,
        ForceSquadronTank= false,
        PullSize         = 0,
        Undersize        = true,
    },
}
DungeonManagerCustomItemsList entries
Each entry has DungeonData, Settings, and a RunData block that includes an Items table keyed by Item ID.

RunData Field	Type	Description
Use	bool	Whether this entry is active.
Complete	number	Runs completed for this entry.
Job	number	Job index to use. 0 = current job.
Items	table	Map of ItemID → ItemEntry. Keyed by item ID number.
ItemEntry fields:

Field	Type	Description
ItemID	number	The item's ID. Matches the key in the Items table.
Enabled	bool	Whether to stop running once this item's Quantity is reached.
Quantity	number	Target quantity of this item to collect.
-- Example entry
{
    DungeonData = {
        Name     = "The Akh Afah Amphitheatre (Extreme)",
        Type     = "Trials",
        UniqueID = "80_Trials_378",
    },
    RunData = {
        Use      = false,
        Complete = 0,
        Job      = 0,
        Items    = {
            [16831] = { ItemID = 16831, Enabled = false, Quantity = 1 },
            [36141] = { ItemID = 36141, Enabled = false, Quantity = 1 },
        },
    },
    Settings = {
        AllowInteract    = true,
        DetectionRange   = 3,
        ForceMeleeRange  = true,
        ForceSquadronTank= false,
        PullSize         = 0,
        Undersize        = true,
    },
}
JobLevelManagerList entries
Each entry has DungeonData, Settings, and a RunData block with level range controls. DungeonData additionally contains Index1 and Index2 used internally for duty support indexing.

RunData Field	Type	Description
Use	bool	Whether this entry is active.
JobLevelMinLevel	number	Start running this duty when the job reaches this level.
JobLevelMaxLevel	number	Stop running this duty once the job exceeds this level.
DungeonData Field	Type	Description
Name	string	Display name.
Type	string	Content category.
UniqueID	string	Stable unique ID.
Index1	number	Internal duty support index 1.
Index2	number	Internal duty support index 2.
-- Example entry
{
    DungeonData = {
        Name     = "Vanguard",
        Type     = "DutySupport",
        UniqueID = "831_DutySupport_1198",
        Index1   = 84,
        Index2   = 2,
    },
    RunData = {
        Use              = true,
        JobLevelMinLevel = 97,
        JobLevelMaxLevel = 98,
    },
    Settings = {
        AllowInteract    = true,
        DetectionRange   = 3,
        ForceMeleeRange  = true,
        ForceSquadronTank= false,
        PullSize         = 50,
        Undersize        = true,
    },
}
