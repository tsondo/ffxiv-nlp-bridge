DungeonMasterGetContentList
DungeonMasterGetContentList(AccessKey)
Returns a flat list of every duty entry in DungeonMaster's internal content database, including unlock state for the current character. Requires a valid session token with the DungeonMasterGetContentList scope.

Parameters
Parameter	Type	Description
AccessKey	string	A valid session token obtained via GetHMToken.
Returns
An array of tables, one entry per duty content row. Returns nil if the token is invalid.

Entry Fields
Field	Type	Description
UniqueID	string	Stable unique identifier. Format: "InstanceID_Type_DungeonID". Use this as your lookup key.
Name	string	Display name of the duty.
Type	string	Content category. e.g. "Dungeons", "Trials", "Raids", "Squadrons", "Trusts", "DutySupport", "Variant-Criterion".
SubCat	table	Array of category tag strings for this entry. e.g. {"ARR"}. May be empty.
DungeonID	number	Territory ID used inside the instance.
MapID	number	Territory ID used inside the instance.
InstanceID	number	Instance ID used for queueing.
Level	number	Required character level to enter.
Expansion	string	Expansion name. "ARR", "HW", "SB", "ShB", "EW", "DT".
Undersized	bool	Whether this entry supports the undersized party option.
IsUnlocked	bool	Whether this duty is currently unlocked on the logged-in character.
UnlockInfo	string	How to unlock this duty.
About	string	Short description of the duty.
Notes	string	Internal notes about bot behaviour in this duty.
NeedsArgus	bool	Whether Argus (mob avoidance) is required for this duty.
RecArgus	bool	Whether Argus is recommended but not strictly required.
ArgusNotes	string	Argus-specific notes for this duty.
OtherTag	any	Miscellaneous tag data. May be nil.
Example
local list = DungeonMasterGetContentList(token)

-- list[1] example value:
--{
--	About = "Dungeons ",
--	DungeonID = 1036,
--	Expansion = "ARR",
--	InstanceID = 4,
--	IsUnlocked = true,
--	Level = 15,
--	Name = "Sastasha",
--	Notes = "",
--	SubCat = 
--	{
--		"ARR",
--	},
--	Type = "Dungeons",
--	Undersized = false,
--	UniqueID = "4_Dungeons_1036",
--	UnlockInfo = "Dungeon_Master_ARR_Pack_1\nDungeon_Master_ARR_Pack\n",
--}
