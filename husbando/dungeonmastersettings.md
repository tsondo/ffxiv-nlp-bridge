DungeonMasterSettings
DungeonMasterSettings(AccessKey, Setting, Value, Debug)
Reads or writes settings on the DungeonMaster addon. Requires a valid session token with the DungeonMasterSettings scope.

Parameters
Parameter	Type	Description
AccessKey	string	A valid session token obtained via GetHMToken.
Setting	string | nil	The GUIData key to read or write. Pass nil to return the full state.
Value	any | nil	The value to write. Pass nil to read instead.
Debug	bool | nil	If true, prints token validation info to the console.
Return Values
Call Pattern	Returns
DungeonMasterSettings(key)	GUIData table
DungeonMasterSettings(key, "Setting")	GUIData["Setting"] (read)
DungeonMasterSettings(key, "Setting", value)	(no return, writes the value)
Token invalid	nil
GUIData Reference
Core
Key	Type	Default	Description
Enable	bool	false	Enables or disables the addon.
StatusMessage	string	""	Current status text shown in the UI. Read-only.
DutyManagerType	number	1	Operating mode. 1 = Quick Start, 2 = Dungeon Manager, 3 = Job Manager, 4 = Quest Assist Mode, 5 = Dungeon Manager Custom Items.
JobToUse	number	0	Job index to use in Quick Start / Quest Assist modes. 0 = current job.
LogLevel	number	1	Debug output verbosity. 1 = minimal, 3 = verbose. Set to 3 when making bug reports.
OldTabs	bool	false	Use the legacy vertical tab layout instead of the compact icon tabs.
RunsComplete	number	0	Total runs completed this session. Read-only.
Dungeon Options
These are global default values. Each dungeon entry in NewDungeonSelection has its own Settings block that overrides these on a per-dungeon basis. See DungeonMasterDungeonSettings to modify per-dungeon settings.

| Key | Type | Default | Description |

|-----|------|---------|-------------| | DetectionRange | number | 2 | Mob and loot detection radius. 1 = Small (faster), 2 = Medium, 3 = Large (more XP). | | ForceMeleeRange | bool | false | Forces ranged classes to attack at melee range. Useful in certain dungeons. | | Undersize | bool | false | [Dungeons / Trials / Raids] Enable undersized party option in queue settings. | | AllowInteract | bool | true | [Dungeons / Trials / Raids] Allow interaction on objectives. At least one party member must have this on. | | ForceSquadronTank | bool | false | [Squadrons] Forces the squadron tank NPC to taunt adds targeting other party members. | | PullSize | number | 0 | Attempt to pull up to this many mobs before engaging. 0 = pull normally. Not supported in every dungeon. |

Dungeon Manager Mode
Key	Type	Default	Description
DisableAfterList	bool	false	Disables the addon when the Dungeon Manager list is fully completed.
DisableAfterList2	bool	false	Disables the addon when the Custom Items list is fully completed.
SelectRandomFromDungeonManager	bool	false	Picks entries randomly from the Dungeon Manager list instead of in order.
Run Controls
Key	Type	Default	Description
RunsBeforeStopping	number	0	Stop the addon after this many runs. 0 = run indefinitely.
RunsBeforeRest	number	0	Enter rest state after this many runs. 0 = never rest.
RestTime	number	0	How many minutes to rest before resuming.
LeaveAfter	bool	false	Automatically leave the instance after a specific objective is complete.
LeaveAfterObjective	number	0	Which objective index triggers the early leave.
Settings Tab
Key	Type	Default	Description
RunExchange	bool	false	Hooks into the Exchange addon and runs it when safe.
RunRetainers	bool	false	Hooks into the Retainers addon and runs it when safe.
SetRecGear	bool	false	Automatically equips recommended gear before each queue.
SaveGearSet	bool	false	Saves the gearset linked to your gearset manager selection.
CurrentFood	number	0	Item ID of the food to eat before runs. 0 = no food.
UseSpiritbondPotion	bool	false	Uses the best spiritbond potion available in inventory.
AutoSwapDuty	bool	false	[Trusts / Squadrons] Auto-selects the best dungeon based on current level. Quick Start only.
BypassFailedQueue	bool	false	Bypasses the stop-on-failed-queue safety logic.
RepairAtValue	number	50	Repair gear when durability drops below this percentage. Range: 20–90.
MinPartySize	number	1	Will not queue unless party size is at or above this value. Range: 1–8.
MaxQueueDelay	number	10	Maximum random delay in seconds before each queue attempt.
MinQueueDelay	number	5	Minimum random delay in seconds before each queue attempt.
NewCombatHandler	bool	false	Use the new experimental combat handler.
Loot
Key	Type	Default	Description
LootMode	number	1	1 = Loot All, 2 = Last Boss + Materia, 3 = Last Boss Only, 4 = None.
PartyLeaderLootRule	number	1	Assigns loot rolling rules to the party when you are party leader.
IgnoreTrashLoot	bool	false	Attempts to skip chests containing only potions or trash items.
AllowChestInteraction	bool	true	Allows opening treasure chests. At least one player must have this on or nothing gets looted.
ForcePassLoot	bool	false	Automatically passes on all loot rolls.
Trusts / Squadrons
Key	Type	Default	Description
SetNPCs	bool	false	Sets NPCs before entering a Trust dungeon.
NPCsUsed	table	{Tank=1,Healer=1,DPS1=1,DPS2=2}	Selected NPC indexes for each role in Trusts.
SetSquadronNPC	bool	false	Sets squadron NPCs before entering. All four role names below must be filled.
TankSquadronNPC	string	"Please Set NPC Name"	Exact name of the squadron tank NPC.
HealerSquadronNPC	string	"Please Set NPC Name"	Exact name of the squadron healer NPC.
DPS1SquadronNPC	string	"Please Set NPC Name"	Exact name of the first squadron DPS NPC.
DPS2SquadronNPC	string	"Please Set NPC Name"	Exact name of the second squadron DPS NPC.
Positionals
Key	Type	Default	Description
DoPositionals	bool	false	[BETA] Attempts positional attacks for melee classes.
AFK / House
Key	Type	Default	Description
TrustsAFKLocation	number	1	AFK location index when queueing for Trusts.
DungeonAFKLocation	number	1	AFK location index when queueing for standard dungeons.
HouseSet	number	1	Which saved house entry to use.
EnterHouse	bool	false	Automatically enters the configured house when nearby.
HouseHasMender	bool	false	Whether the house contains an NPC mender for gear repairs.
HouseData	table	{}	Saved house door data. Set via the in-game "Set Door" button. Fields: ID, ContentID, MapID, TerrID, PlaceName, POS {x,y,z}.
Example
-- Read the current duty manager type
local mode = DungeonMasterSettings(token, "DutyManagerType")

-- Switch to Dungeon Manager mode
DungeonMasterSettings(token, "DutyManagerType", 2)
