# GPL Language Reference (official SDK documentation, transcribed)

**Source: the official "GPL (Game Play Language) Reference" PDF from the
Majesty SDK.** This is transcribed developer documentation, not
reverse-engineering — it is the highest-confidence source in this project
and **outranks our own inferred findings wherever the two disagree.**

Companion files, and how they differ in authority:
- **This file** — official signatures, parameters, return values, and
  documented semantics. Treat as ground truth.
- `.kiro/steering/gpl-reference.md` — our reverse-engineered notes on
  primitives the official docs *don't* cover, plus engine gotchas learned
  the hard way. Complementary, lower authority.
- `GPL_MODDING_GUIDE.md` / `GPL_QUEST_RULES_REFERENCE.md` — how the
  shipped game actually uses all of this.

**§0 below lists every place this document CORRECTED one of our prior
findings. Read it first if you have been working from those.**

---

## §0. Corrections this document forces on our prior findings

| Our claim | Official doc says | Impact |
|---|---|---|
| `$UpgradeAgentAttributes` may perform the whole tier transition including sprite | "**Copies the GPL attribute values from the agent's definition template into its local storage.** Usually called when a building upgrades to the next level." | **Attributes only — no appearance change.** See §0.1. |
| `$ChangeUnitType` is a character shape-shift tool, redundant for building upgrades | "Changes the type of a unit from one type to another… **This does not update any attributes on the unit to be exactly like the new unit type, only the appearance.**" | **Appearance only.** The two are complementary; a scripted upgrade needs BOTH. See §0.1. |
| `$RandomNumber(N)` returns `[0, N-1]`, hence the universal `+1` idiom | "Return a random number **from 0 up to and including** the input value." | Range is `[0, N]`, N+1 outcomes. See §0.2. |
| GPL "can't multiply by floats"; cause unknown | "The float type is in fact **a fixed-point numeric value**, max signed integer portion 2^23, **max precision 1/255**." Chosen so multiplayer clients can't desync on FPU rounding. | Root cause identified. See §0.3. |
| `"clear"` as a `$SpawnUnit` flag — what it clears was UNKNOWN (Ghidra item) | "If specified, **any units under the footprint of the new unit will be removed.** Useful when spawning buildings." | **Resolved. Close the Ghidra item.** |
| `$SetEffectorDirection` index→frame mapping UNKNOWN (Ghidra item) | "The direction of the effect. **0–31, with 0 being NORTH** and increasing values going clockwise around the agent." | **Resolved. Close the Ghidra item.** |
| `$SetBuildingLimit` semantics unknowable from source (zero call sites) | "**Limits all players** to no more than the specified number of buildings for the specified type. When the limit = 0 this has much the same effect as `DisableUnitType`. **Note that these limits are NOT enforced by SpawnUnit.**" | **Resolved.** Signature: `(string type, integer limit)`. |
| `$BuildingIsRecruiting`'s boolean contract unexplained | "Returns true if the building **is in the process of recruiting a new member.**" | **Resolved.** |
| Modifier named `$FindFirstMatchOnly` | The modifier is **`#FindFirstMatch`** | Naming fix. |
| Hero `Cost` has no GPL-readable attribute (inferred from a modder's failed search) | "**All engine-side attributes are integers only**" and "**GPL code cannot currently add any new engine-side attributes**"; no cost accessor appears anywhere in the official function list. | Negative **strengthened** — it is now an argument from a complete API list, not from absence of search results. |

### §0.1 The upgrade pair — this refutes advice given earlier in this project

The two primitives are **complementary halves**, and the official
descriptions say so explicitly:

- **`$ChangeUnitType(agent, string)`** — changes **appearance only**.
  "This does not update any attributes on the unit to be exactly like the
  new unit type, only the appearance." The previous type is saved to
  `#ATTRIB_OriginalType`, and `$RevertUnitType` undoes it.
- **`$UpgradeAgentAttributes(agent)`** — copies **GPL attribute values**
  from the agent's definition template into local storage. No appearance
  change.

**Therefore a GPL-scripted building upgrade needs BOTH calls**, and the
`Dwarfeh_AI` mod's `$ChangeUnitType` + `$UpgradeAgentAttributes` pairing
was correct all along. It also explains the mod author's crash note —
"the game will crash after a few seconds if `$UpgradeAgentAttributes`
isn't run after changing unit type" — precisely: appearance advanced to
the new type while attributes still described the old one.

**`GPL_MODDING_GUIDE.md` §2's recommendation to drop `$ChangeUnitType` and
call only `$basic_upgrade` is WRONG and is corrected there.** Dropping it
would leave the building showing its old tier art forever.

**Open question this sharpens rather than closes:** the *human* upgrade
path calls only `$UpgradeAgentAttributes` (inside `BuildingReachedMaxHP`)
and never `$ChangeUnitType`, yet the player's building visibly becomes its
new tier. So the engine must perform the appearance swap itself for
player-initiated upgrades. **That remains the Ghidra question** — now
better posed, because we know the GPL-visible half does not do it.

Note also: `$ChangeUnitType` is documented as valid for "**building and
vehicle units**." Shipped code calls it on heroes and monsters
(Gnome→GnomeChamp, hero→Dryad/Medusa/Minotaur, hero→Red_Bear), so
"vehicle" evidently means *any mobile agent*, consistent with `$Move`'s
`avoid_vehicles` modifier being described as "any other agent that is able
to move."

### §0.2 `$RandomNumber` is inclusive on both ends

`$RandomNumber(N)` yields `0..N` inclusive — **N+1 possible values**, not
N. Our §14 recorded `[0, N-1]` and explained the shipped `+1` idiom as
converting to a 1-based range. The idiom is real, but with the correct
range `$RandomNumber(2) + 1` yields **1, 2 or 3**, not 1-2. Any of our
notes that computed a probability from the wrong range should be
re-derived. Shipped comments themselves are inconsistent here (the
`Dwarfeh_AI` mod has `$RandomNumber(2) + 1` commented "Randomly choose
number 1-3" in one place and "1-2" in another) — the official doc settles
it.

### §0.3 Why float arithmetic misbehaves

`float` is **fixed-point**, not IEEE floating point: max signed integer
portion 2^23, precision 1/255. The documented reason is multiplayer
determinism — real FPUs would round differently across clients and desync
the simulation.

That is the root cause behind `GPL_MODDING_GUIDE.md` §14.6's observation
that `100 * 1.5` misbehaves while `100 * 3 / 2` works: 1/255 quantisation
makes some literals unrepresentable, so staging the operation as
integer-ish multiply-then-divide avoids the lossy intermediate. The 2^23
integer ceiling also explains why a compounding multiply overflows and
crashes — the mod's hardcoded `400000.0` clamp was conservative but
directionally right.

---

## §1. Language basics

- **Case-insensitive.** `begin` and `Begin` are equivalent.
- Statements end with `;`. Comments are `//` to end of line.
- **Keywords:** `and`, `begin`, `break`, `continue`, `declare`, `define`,
  `else`, `end`, `expression`, `false`, `foreach`, `function`, `if`,
  `prototype`, `return`, `true`, `while`.
  *(The PDF prints "prototypep", evidently a typo for `prototype`.)*

### Types

| Type | Notes |
|---|---|
| `boolean` | true / false |
| `coordinate` | X/Y map point. Directly comparable for equality. Extract with `$GetX`/`$GetY`. |
| `float` | **Fixed-point** — integer portion max 2^23, precision 1/255. See §0.3. |
| `integer` | Signed, range 2^31. |
| `list` | Single-dimensional; members may be any intrinsic type. **1-based indexing.** |
| `string` | Character string. |
| `agent` | A GPL struct of predefined attributes plus a link to a game-world object. Shape defined by a `prototype` (analogous to a C++ struct); prototypes instantiate as predefined agent types in a GPL data file. |
| `agentref` | A *reference* to an agent, not the agent. Also called an Agent Number. |
| `function` | A named code block with optional params and return type. |

### Function syntax

```gpl
function FunctionName(Function Parameters) is [Function Return Type]
declare
    Local FunctionValues
begin
    Function Body
end
```

Call or reference a function by prefixing `$`: `$HelloRogue(theRogue);`

### Expressions (named constants)

```gpl
// Number of heroes that have to die before a Graveyard is created
expression #Graveyard_limit 15
```

Used as `if (palace's "num_deceased_heroes" >= #Graveyard_limit)`. The
base game defines many in `globals.gpl` / `mx_globals.gpl`.

**Critically, expressions resolve at LOAD time, not compile time, and are
not validated as pre-defined.** That is deliberate: it lets external data
supply values. **The attribute system uses this** — any expression whose
name starts with `ATTRIB_` has that prefix stripped and the value replaced
with the matching engine attribute's ID at bytecode load. So
`#ATTRIB_FirstStageBuilt` becomes the engine's FirstStageBuilt ID.

---

## §2. Agent attributes vs Unit attributes — two different systems

**GPL-side agent attributes.** Defined by the agent's prototype, with
starting values from its definition. Accessed with the possessive
operator:

```gpl
iDeceasedHeroes = palace's "num_deceased_heroes";
palace's "num_deceased_heroes" = iDeceasedHeroes;
```

**An error is raised if you access an attribute the agent does not have.**
Guard with `$HasAttribute` when unsure:

```gpl
if ($HasAttribute("num_deceased_heroes", palace))
    begin
        iDeceasedHeroes = palace's "num_deceased_heroes";
    end
```

Add ad-hoc attributes with `$AddAttribute`, remove with
`$RemoveAttribute`:

```gpl
AIRootAgent = $RetrieveAgent ( "GplAIRoot" );
$AddAttribute(AIRootAgent, "MyNewAttribute", "integer", 500);
```

**Engine-side unit attributes.** Every displayed agent is bound to an
engine object called a **Unit**, which owns the displayed image, animation,
movement and UI aspects. Unit attributes hold state both sides need — HP,
experience level, sight range, and so on. Accessed only via
`$GetAttribute`/`$SetAttribute`, referenced as `#ATTRIB_Name`.

Two hard constraints, both stated outright:
- **All engine-side attributes are integers only.**
- **GPL cannot add new engine-side attributes.** (GPL-side attributes are
  the flexible ones — simpler syntax, any GPL type.)

```gpl
$setattribute ( thisagent, #ATTRIB_Intelligence, 10 );
myIntelligence = $getattribute( thisagent, #ATTRIB_Intelligence );
```

---

## §3. Built-in function reference

Functions defined in C++ by the engine and exposed to GPL. Called exactly
like GPL-defined functions. Parameters are listed in order; `(opt)` marks
optional ones.

**Coverage note:** this is the complete alphabetical list from the official
PDF (~150 entries). If a primitive our research found is *absent* here —
e.g. `$Freeze_Unit`, `$Control_Monster`, `$PerformAction`-adjacent helpers,
`$ListCompleted`, `$List_Attribs`, `$RemoveAllBuildingLimits` variants
beyond those listed — it is either a GPL library function defined in the
shipped `.gpl` tree rather than an engine primitive, or an undocumented
primitive. See `.kiro/steering/gpl-reference.md` for those.

### Attributes and data

| Function | Params | Returns | Notes |
|---|---|---|---|
| `AddAttribute` | agent, string name, string type, value *(opt default)* | boolean | False if already present (then nothing is done). |
| `RemoveAttribute` | agent, string name | — | Safe to call if absent. |
| `HasAttribute` | **string name, agent** | boolean | Note the argument order: name first. |
| `GetAttribute` | agent, integer attribID | integer | Engine-side attribute. |
| `SetAttribute` | agent, integer attribID, integer value | — | Engine-side attribute. |
| `AdjustAttribute` | agent, integer attribID, integer delta | — | Adds delta to current value. |
| `MagicalAdjustAttribute` | agent, integer attribID, integer delta | — | Also adjusts the attribute's **Magical counterpart**. |
| `UpgradeAgentAttributes` | agent | — | **Copies GPL attribute values from the agent's definition template into local storage.** Usually called when a building upgrades a level. **No appearance change** — see §0.1. |
| `GetPlayerData` | agent, string `"gold"` \| `"palace"` | integer \| agent | |
| `AdjustPlayerData` | agent, string `"gold"`, integer delta, string *(opt)* | — | Optional string = unit/building type the gold is buying, **statistics display only**, and requires the delta be negative. |
| `SetTreasuryValues` | integer check interval ms, integer warning threshold | — | |
| `IncrementStatCounter` | agent, string | — | **Only `"gutter"` is supported.** |

### Agent lifecycle and identity

| Function | Params | Returns | Notes |
|---|---|---|---|
| `CreateAgent` | string prototype, string *(opt)* unique name | agent | Normally unnecessary — agents are made for you with game objects. Useful for **detached agents as persistent variable storage**. |
| `DeleteAgent` | agent | — | Does **not** delete the bound unit. "Use with care" — only for cases where the unit cleans up after itself, such as some buildings. |
| `DeleteGamePiece` | agent | — | Deletes the game object associated with the agent. |
| `RetrieveAgent` | string name | agent | Usually used for the quest **root** agent (`"GplAIRoot"`). Can return `$NullAgent`. |
| `NullAgent` | — | agent | The global null agent, for comparisons and clearing fields. |
| `AgentNumber` | agent | agentRef | Use when storing an agent reference inside another agent's attribute. |
| `IsValidGamePiece` | agent | boolean | |
| `ChangeUnitType` | agent, string new type | — | **Appearance only** — "does not update any attributes". Original type kept in `#ATTRIB_OriginalType`. Documented for "building and vehicle units". See §0.1. |
| `RevertUnitType` | agent | — | Only valid after `ChangeUnitType`. |
| `SpawnUnit` | agent spawner, string type, coordinate *(opt)*, integer player *(opt)*, string *(opt)* options, list *(opt)* attrib ID/value pairs | agent | Options: **`override`** (ignore Lair data, force the type), **`maxhp`** (start at max HP — *for a building this means the first stage will be built*), **`clear`** (**remove any units under the new unit's footprint** — useful for buildings). Default owner/location are the spawner's. |
| `SpawnGraveyard` | agent building, string `"graveyard"`, coordinate *(opt)* | — | Only `"graveyard"` supported. Defaults near the building's exit point. |
| `SetUnitPlayerNumber` | agent, integer player | — | |
| `GetUnitPlayerNumber` | agent | integer | |
| `UnitsAreSamePlayer` | agent, agent | boolean | |
| `UnitIsLocalPlayer` | agent | boolean | |
| `UnitIsOffmapLair` | agent | boolean | |
| `SetPalace` | agent, integer player | — | Sets the building used as that player's Palace. |
| `SetParent` | agent child, agent parent | — | Behavior depends on parent type: a **building** (usually a guild) makes the child a guild member; a **Reward Flag** makes the child chase it. **An agent can have both kinds of parent at once.** |
| `GetParent` | agent | agent | The Guild/spawner parent. Does **not** return Reward Flag parents. |
| `GetFlag` | agent | agent | The **Reward Flag** parent specifically. |
| `Parent` | agent | agentRef | Parent (building or reward flag), or -1. |
| `GetContainerAgent` | agent | agentRef | Parent that owns the agent — typically used to find what an effect agent is attached to. -1 if none. |
| `SpecifyName` | agent, string | — | String is a key in the scenario's text table. |
| `SpecifyIntent` | agent, integer \| string | — | Integer = index into the built-in intent string table; string = key in the scenario's text table. |

### Movement, position, geometry

| Function | Params | Returns | Notes |
|---|---|---|---|
| `Move` | agent, coordinate \| agent dest, string modifier | — | Modifiers: `add_waypoint` (queue instead of replace), `loop` (queue and loop back to the first destination), `avoid_vehicles` (avoid anything that can move), `avoid_buildings`, `avoid_everything`. Buffer distances come from the agent's buffer zone. |
| `StopMoving` | agent | — | Stops and **clears the movement queue**. |
| `IsMoving` | agent | boolean | |
| `HasWayPoints` | agent | boolean | |
| `GetNextWayPoint` | agent | coordinate | The waypoint being moved toward, or the current position if not moving. |
| `TeleportToPoint` | agent, integer distance, coordinate dest | — | Jumps *toward* the destination by `distance`; final spot chosen by a "best location" method. |
| `TeleportToUnit` | agent, integer distance, agent target, integer casting range | — | Buildings resolve to their 'door'. The range argument prevents closing too far onto an enemy. |
| `IsAdjacent` | agent, agent | boolean | True at distance ≤ 1 between **footprint areas** on the path grid. |
| `DistanceBetweenAgents` | agent, agent | integer | World coordinates, measured **from closest footprint edges**. |
| `DistanceBetweenCoords` | coordinate, coordinate | integer | |
| `PathCost` | coordinate from, coordinate to, string collision, boolean *out* canFindPath, agent *(opt)* | float | Collision options: `check_buildings`, `check_static_units`, `check_all_units`. Without an agent it assumes an "average" unit. |
| `LocationOf` | agent | coordinate | |
| `MakeCoord` | integer x, integer y | coordinate | |
| `GetX` / `GetY` | coordinate | integer | |
| `GetBoardExtents` | — | coordinate | Map size as an x/y pair. |
| `RandomCoord` | agent \| coordinate centre, integer *(opt)* min, integer max | coordinate | **Radii are rectangular, not circular.** Two-arg form implies min 0. |
| `GetEntranceLoc` | agent building | coordinate | The building's "entrance". |
| `GetNearestHiddenCoord` | agent, coordinate *out* | boolean | Nearest coord not revealed to that agent's player. |
| `Sqrt` | float | float | **Low precision.** |

### Buildings, occupancy, hiding

| Function | Params | Returns | Notes |
|---|---|---|---|
| `Hide` | agent, agent building, integer *(opt)* flags | — | **Alias: `EnterBuilding`.** Flags: 0 = walk there, 1 = teleport inside. |
| `Unhide` | agent, coordinate *(opt)* | — | **Alias: `ExitBuilding`.** Optional appear-at location. |
| `IsHidden` | agent | boolean | An agent is hidden while inside a building. |
| `InsideBuilding` | agent | boolean | |
| `IsEnteringBuilding` | agent | boolean | Has an order to enter. |
| `GetBuildingContainer` | agent | agent | The building the agent is inside, else a null agent. |
| `GetBuildingContents` | agent building | list | Agents inside. |
| `BuildingIsRecruiting` | agent building | boolean | **True while the building is in the process of recruiting a new member.** |
| `CancelGuildMembership` | agent | — | Removes the agent from its guild's **engine-side** list. **You must still unlink the GPL side yourself** (e.g. remove it from its `home`'s member list). |
| `EnchantWizTower` | agent | — | Enchant the supplied Wizard Tower. |
| `SetHallFlag` | agent | — | Sets the special monster effector if any player has this agent's unit type selected. **Specific to the Hall Of Champions.** Agent must belong to the Monster player. |

### Build restrictions

| Function | Params | Returns | Notes |
|---|---|---|---|
| `DisableUnitType` | string type | — | Prevents the type from appearing in the quest; limits what the player can **build/recruit**. |
| `EnableUnitType` | string type | — | Inverse. |
| `SetBuildingLimit` | string type, integer limit | — | **Limits ALL players** to that many buildings of the type. `limit = 0` ≈ `DisableUnitType`. **NOT enforced by `SpawnUnit`.** |
| `RemoveBuildingLimit` | string type | — | Removes limits set by `SetBuildingLimit` **or by the player in the Build Tree Editor** — which players get in **freestyle games only**. |
| `RemoveAllBuildingLimits` | — | — | All types at once, same two sources. |

### Lists

| Function | Params | Returns | Notes |
|---|---|---|---|
| `ListObjects` | agent origin, string unitType, integer radius, list *out*, integer *(opt)* modifiers… | integer size | Radius in **pixels**; `-1` = whole map. Type examples: `"monster"`, `"hero"`, `"building"`, `"rewardflag"`, `"lair"`. **Results are sorted nearest→furthest.** Modifiers below. |
| `ListSize` | list | integer | |
| `ListMember` | list, integer index | any | **1-based**; valid indexes 1..N. |
| `RemoveListMember` | list, integer index | — | 1-based. |
| `ClearList` | list | — | |
| `AddLists` | list, list, … | list | Merges two or more into a new list. |
| `Concatenate` | any, any, … | list | Wraps its arguments into a list. |
| `ListTitles` | list, string title | list | Returns members whose `title` matches. **`title` == the unit type.** Source list unmodified. |
| `RemoveTitles` | list, string title | list | Same match, but **also removes them from the source list**. Returns the removed ones. |
| `ListPalaces` | — | list | All palaces on the map. |
| `FillSpecialLairList` | agent lair, list *out* | integer | Fills the list with the unit types the lair spawns (list cleared first); returns the count. *(The PDF's prose for this entry duplicates `RemoveTitles`' description — evidently a copy-paste error. The parameter/return tables are as given here.)* |

**`ListObjects` modifiers** (each specified individually):

| Modifier | Meaning |
|---|---|
| `#NoHiddenMap` | Search all object lists, not just the searching agent's visibility list. |
| `#MyPlayer` | Only objects matching the supplied agent's player ID. |
| `#NotMyPlayer` | Only objects **not** matching it. |
| `#InsideOtherUnits` | Allow units inside other units (e.g. heroes inside a building). |
| `#RewardFlags` | Search reward flags; **ignores the passed unitType** and implies `#InsideOtherUnits`. |
| `#CheckTitles` | Filter by `title`. **The comparison string must immediately follow.** Mutually exclusive with `#CheckSubTypes`. |
| `#CheckSubTypes` | Filter by `SubType`, same immediately-following-string rule. Mutually exclusive with `#CheckTitles`. |
| `#FindFirstMatch` | Fill the list with only the first unit found — **not necessarily the nearest.** |

```gpl
$ListObjects (Palace, "Hero", -1, NotMyHeroes, #NoHiddenMap,
              #InsideOtherUnits, #NotMyPlayer);
```

### Threads

| Function | Params | Returns | Notes |
|---|---|---|---|
| `NewThread` | function, integer interval ms, … | — | **Repeating**: called every N ms, extra args passed through. |
| `RunThread` | function, integer delay ms, … | — | **One-shot**: called once in N ms. If already running, **the timer is reset**. |
| `RunThreadOnce` | function, integer delay ms, … | — | Like `RunThread`, except **if the thread already ran and is suspended it will not be resumed.** |
| `SetThreadInterval` | function, integer ms | — | Change an existing thread's interval. |
| `SuspendThread` | function | — | Pair with `ResumeThread`. |
| `ResumeThread` | function | — | |
| `KillThread` | function | — | |
| `IsRunning` | function | boolean | **True even if the thread is suspended.** |
| `ValidFunction` | function | boolean | |
| `LookupFunction` | string name | function | Resolve a function by name; may return NullFunction. |
| `Halt` | — | — | Stop GPL processing. |

**Timing caveat, stated officially:** "GPL code execution is done on a
frame based execution budget, so the thread's execution interval will be
approximate." Never rely on exact ms.

### Effects, visuals, sound, music

| Function | Params | Returns | Notes |
|---|---|---|---|
| `CreateEffector` | agent, string effect, integer duration ms, integer *(opt)* float-up number, string *(opt)* option | — | Effect types come from the **Overlay Descriptions**. If the effect already exists, **its duration is just extended**. Options: `after` (call the effect's DeathScript on completion), `infinite`. |
| `CheckEffector` | agent, string effect | boolean | |
| `DeleteEffector` | agent, string effect | — | |
| `DeleteAllEffectors` | agent | — | Removes all effectors on the bound game object. |
| `SetEffectorDirection` | agent, string effect, integer direction | — | **0–31, 0 = NORTH, increasing clockwise.** |
| `CreateMissile` | string missile type, agent firer, coordinate \| agentref target | — | Missile types from the Overlay Descriptions. |
| `CreateSpellUnit` | agent caster, string spell | — | For spells with a persistent agent that applies effects to nearby enemies. |
| `SetSpellUnitTimeout` | agent spell, integer ms | — | After which the spell agent is destroyed. |
| `PerformAction` | agent, string action, agent \| coordinate target | — | Actions come from the Actions definitions. |
| `SetDrawEffects` | agent, string palette, integer transparency | — | Palette: `red`, `gray`, `green`. Transparency 1–9. |
| `ClearDrawEffects` | agent | — | |
| `FadeIn` / `FadeOut` | agent, integer ms per step | — | **10 discrete steps**, so 100 ⇒ a 1-second fade. |
| `TurnOnSpeedTrail` | agent, integer clones, integer *(opt)* ms | — | |
| `TurnOffSpeedTrail` | agent | — | |
| `HasSpeedTrail` | agent | boolean | |
| `StartEarthquakeSpell` | agent, integer min shake px, integer max shake px, integer *(opt)* ms | — | Absent or `-1` duration ⇒ infinite; stop with `StopEarthquakeSpell`. |
| `StopEarthquakeSpell` | agent | — | |
| `PlaySound` | three overloads — see below | — | |
| `PlayMusic` | integer track | — | |
| `LastMusicTrack` | — | integer | |
| `SetStoppedMusicCallback` | string function name | — | **WARNING (official):** the callback **must not change game state** — it won't run on machines with sound disabled and fires at different times when track lengths differ per client. Multiplayer desync hazard. |

**`PlaySound` overloads:**
1. `(agent, string soundPhase, float (opt) distanceModifier)` — uses the sound description native to that agent type.
2. `(agent, string soundDescription, string soundPhase, float (opt) distanceModifier)`
3. `(string soundDescription, string soundPhase, integer (opt) player)` — only that player hears it.

Distance modifier adjusts apparent emission range, in world coordinates.

### UI, minimap, messaging, map reveal

| Function | Params | Returns | Notes |
|---|---|---|---|
| `LocalChatMessage` | integer player, integer \| string stringID, agent *(opt)* | — | Status line messages — "used primarily to display events such as a building being completed or upgraded." Integer = indexed base-game string; string = key into the quest's string table. |
| `MessageFlag` | coordinate \| agent, integer \| string stringID | — | Places a message flag on the map. |
| `IsMessageFlagPresent` | integer \| string stringID | boolean | True while it's on the map and **not yet dismissed by the player**. |
| `MiniMapAnimation` | coordinate \| agent, string beacon | — | Beacon definitions provided by the game: **`event_beacon`, `hero_death`, `treasure_find`.** |
| `CombatSignal` | agent | — | Signals combat; **flashes on the minimap.** |
| `ShowMinimap` | agent, boolean | — | Show/hide that agent on the minimap. |
| `RevealArea` | agent, coordinate, integer radius | — | `-1` radius reveals the whole map. |
| `RevealWholeMap` | integer player | — | |
| `SetShareReveal` | integer player, boolean | — | Share revealed map with teammates. **Team member must be one of the first four players.** |
| `FadeIn`/`FadeOut` | *(see effects)* | | |
| `PlaceRewardFlag` | agent target, integer offering player, integer amount | agent | Returns the flag agent if it could be created. |
| `ClearFlag` | agent | — | Stops the agent chasing any Reward Flags. |

### Teams, victory, quest setup

| Function | Params | Returns | Notes |
|---|---|---|---|
| `GetPlayerTeamNumber` | agent | integer | |
| `SetPlayerTeamNumber` | agent, integer team | — | **All team members see the same map area.** |
| `NewTeamNumber` | — | integer | A team number not in use by any player. |
| `NeutralTeamNumber` | — | integer | The neutral team number. |
| `DeclareVictory` | agent \| integer player, coordinate \| agent *(opt)* | — | Optional look-at target; defaults to the player's Palace. |
| `DeclareLoss` | agent \| integer player | — | |
| `GetVictoryConditionIndex` | — | integer | The victory goal index chosen in setup. Consumed by `SetVictoryCondition` in `Victory_Conditions.gpl` / `MX_Victory_Conditions.gpl`. |
| `GetVictoryConditionModifier` | — | integer | The victory goal **modifier** — a second setup value alongside the index. |
| `GetSpecialEvent1Script` | — | string | Registered script function name for special event 1 **at the current difficulty level**. |
| `GetSpecialEvent2Script` | — | string | Same for event 2. |
| `DwarvesVoice_SetOperative` | integer 0\|1 | — | Toggles the periodic "Dwarves are available to join" announcement. |
| `ElvesVoice_SetOperative` | integer 0\|1 | — | Elf equivalent. |
| `ReRandom` | integer seed | — | Sets the RNG seed. |
| `RandomNumber` | integer N | integer | **0 to N inclusive** — see §0.2. |

### Spells and inventory

| Function | Params | Returns | Notes |
|---|---|---|---|
| `CastSpell` | agent caster, string spell, agent \| coordinate target | — | Target may be the caster itself. |
| `LearnSpell` | agent, string spell, boolean *(opt)* | — | Optional flag shows/hides the spell in the interface. |
| `ForgetSpell` | agent, string spell | — | |
| `IsSpellAvailable` | agent, string spell, boolean *(opt)* skipTimeout | boolean | Checks knowledge, **experience level**, and optionally timeout. |
| `GetBestSpell` | agent, integer listID | string | Lists: 1 attack (`#List_Attack`), 2 combat utility (`#List_Combat_Utility`), 3 other (`#List_Other`). **May return `"nothing"`.** |
| `GetSpellAttribute` | string spell, string attribute | integer | Attributes: `effector_duration`, `timeout_duration`, `character_level`, `spell_rank`. |
| `CreateNewInventoryItem` | integer itemType, agent recipient, boolean *(opt)* allowDuplicates | — | Duplicates default to false. |
| `DeleteInventoryItem` | integer itemType, agent | — | |
| `TransferInventoryItem` | integer itemType, agent from, agent to | — | |
| `AgentHasInventoryItem` | integer itemID, agent | boolean | **Pass `-1` in a variable** to match any Quest item; the variable is filled with the found ID. |
| `CountInventoryItem` | integer itemID | integer | |
| `FindInventoryItem` | integer itemID | agent | Holder, or null. |
| `GetInventoryItems` | agent | list | Item IDs. |
| `IsInventoryItem` | integer \| string | boolean | |
| `CanDropInventoryItem` | integer \| string | boolean | |
| `GetInventoryItemAgentType` | integer \| string | string | Agent type to use while dropped on the map — passable to `SpawnUnit`. |
| `GetInventoryItemDropType` | integer \| string | integer | **0** = don't drop, **1** = drop when removed from map (stays on the hero through its gravestone state, drops when the gravestone goes), **2** = drop immediately on death. |
| `MakeInventoryAttribute` | integer itemID | integer | Converts an item index into an attribute ID. |

### Death and resurrection

| Function | Params | Returns | Notes |
|---|---|---|---|
| `ClearEngineDeathFlags` | agent | — | Clears 'dead' marking — called when resurrecting. **Does not unhide the unit or reconnect actions/tasks**; that's on you. |

### Debugging

| Function | Params | Returns | Notes |
|---|---|---|---|
| `DebugOut` | string | — | To the debug log. |
| `BreakPoint` | boolean \| integer | — | Breaks into the GPL debugger; a `true` boolean stops execution. |
| `NoDebugMessages` | — | — | Turns off debug messaging. |
