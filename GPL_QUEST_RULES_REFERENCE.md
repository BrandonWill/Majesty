# Majesty Gold HD — Quest Rules Reference (GPL `Rules/`)

Companion to `GPL_MODDING_GUIDE.md` (gameplay systems) and
`CAM_MODDING_GUIDE.md` (binary asset formats). **This file covers the
quest-scripting layer**: everything in `SDK/OriginalQuests/GPL/Rules/`
and `GPLMx/Rules/` — all 15 files, read in full.

**Evidence basis is unchanged from `GPL_MODDING_GUIDE.md`:** every claim
cites the GPL/XML/`.dat`/CAM source it was verified against, and anything
unconfirmed is marked **UNVERIFIED**/**UNKNOWN** rather than guessed.

## How this file is organised (read this first)

Content is grouped by **what you are trying to do**, but each subsection
keeps the number it was originally written under (`§16.1`, `§21.4` …).
That is deliberate: several hundred internal cross-references point at
those numbers, and they are stable search anchors. **The numbers are
identifiers, not reading order** — a chapter may contain `§22.4` before
`§17.4`.

**Resolving a bare `§N` reference:** `§16`-`§22` are in THIS file.
`§1`-`§15` are in **`GPL_MODDING_GUIDE.md`** (the gameplay-systems
guide) — the text below refers to them unqualified because both sets
were originally one document. Nothing was renumbered, so those
references still resolve; they just resolve into the other file.

Subsection numbers encode which source file the finding came from:

| Prefix | Source file |
|---|---|
| §16.x | `construction_rules.gpl`, `victory_conditions.gpl` (+ mx twins) |
| §17.x | `Demo.gpl`, `Random_Events.gpl`, `Special_Events.gpl` |
| §18.x | `Quest_Actives.gpl` (+ mx twin) |
| §19.x | `GPLMx/Rules/Quests_1.gpl` |
| §20.x | `GPLMx/Rules/Quests_2.gpl` |
| §21.x | `GPLMx/Rules/Quests_3.gpl` |
| §22.x | `epic_quest_scripts.gpl` (+ mx twin) |

## Task index — "I want to …"

| Goal | See |
|---|---|
| Gate a building behind a prerequisite / restrict where it can be built | §16.1 |
| Add or change a victory condition | §16.2, 16.3, 21.3 |
| Declare victory or loss, or keep playing after a win | §19.5, 21.5, 22.4 |
| Make a quest end on a boss dying | §19.5, 21.5, 19.10 |
| Restrict what the player can build in a quest | §17.1, 16.1 |
| Unlock something mid-quest | §22.6 |
| Run a timed sequence of quest events | §19.3, 17.4 |
| Add a random or recurring world event | §17.2, 17.3, 17.7 |
| Make difficulty scale with progress or elapsed time | §21.4, 21.8, 22.3 |
| Tune how fast lairs spawn | §19.7, 22.7 |
| Spawn monsters with custom AI behavior | §19.6, 21.6 |
| Spawn an elite or pre-levelled NPC / army | §19.9, 20.3, 20.7 |
| Give a hero or monster quest-specific behavior | §18.2, 18.3, 18.4, 18.6 |
| Make an NPC follow, escort, or be captured | §18.5, 18.3 |
| Make a building act on a timer / attack | §18.7, 20.6 |
| Respawn something after it dies | §18.8, 19.10 |
| Convert an enemy unit or building to the player | §20.4, 18.9, 20.7 |
| Set up a new team / three-way faction war | §19.8, 20.7 |
| Start a quest from scratch (minimal working template) | §17.1, 19.1 |
| Hide, park, or despawn an agent | §20.2, 18.9 |
| Find agents with $ListObjects (and why a query misses things) | §20.2, 18.10 |
| Add custom music | §19.4 |
| Show the player a message, beacon, or sign | §22.5, 17.5 |
| Build an AI opponent kingdom | §21.6 |
| Look up a primitive, constant, or helper function | §17.5, 18.10, 22.2, 22.6 |
| Check whether a mechanism works in base game or expansion only | §17.0-22.0 |
| See what is already known so I don't re-read a file | the Research Provenance chapter |

## Contents

1. **Quest Lifecycle and Structure** — How a quest starts, what threads it runs, and how staged events are paced.
   §17.1, §19.1, §21.2, §19.3, §17.4, §22.4
2. **Victory, Loss and Objectives** — Declaring wins and losses, polling patterns, graded outcomes, objective messaging.
   §16.2, §16.3, §19.5, §20.5, §21.3, §21.5, §22.5
3. **Spawning, Difficulty and Pacing** — Event pools, spawn overrides, lair tuning, and difficulty that scales.
   §17.2, §17.3, §17.7, §19.6, §19.7, §19.9, §21.4, §21.8, §22.3, §22.7
4. **Agent Behavior and Custom AI** — Giving heroes, monsters and NPCs quest-specific behavior.
   §18.1, §18.2, §18.3, §18.4, §18.5, §18.6, §19.10, §20.3, §21.6, §21.7
5. **Buildings as Quest Agents** — Build gating, buildings that act on a timer, building death hooks, rescue/defection.
   §16.1, §18.7, §18.8, §20.4, §20.6
6. **Agent State, Type and Identity** — The `"type"` register, despawning, ownership changes, and quest-wide unit setup.
   §20.2, §18.9, §20.7, §19.8
7. **Primitive, Helper and Constant Reference** — Engine hooks, shared helper library, primitives and constants catalogued.
   §17.5, §18.10, §19.4, §22.2, §22.6
8. **Quest Inventory** — Every shipped quest, its entry function and the mechanisms it uses.
   §19.2, §20.1, §21.1, §22.1
9. **Base vs Expansion Availability** — Which files and mechanisms exist in base game vs the expansion only.
   §17.0, §18.0, §19.0, §20.0, §21.0, §22.0
10. **Research Provenance: What Is NOT New, Sources, and Open Questions** — Recombination lists (so no file needs re-reading) plus per-batch sources and UNVERIFIED items.
   §19.11, §20.8, §21.9, §22.9, §16.4, §17.6, §18.11, §19.12, §20.9, §21.10, §22.8

---

## Chapter 1: Quest Lifecycle and Structure

How a quest starts, what threads it runs, and how staged events are paced.

### 17.1 `Demo.gpl` — the canonical quest-init template

One `Rules/` file, six functions, and it is the tersest complete example
of "everything a quest entry function does." `VAMPIRIC_REVENGE()` is the
quest's engine entry point (the function a `.q` file's pattern name
resolves to — see `.kiro/steering/majesty-modding.md`'s Q-file notes).

**`mx_Demo.gpl` is byte-identical to `Demo.gpl`** except for one extra
blank line before `Function Give_Victory`. Same six functions, same
`$disableunittype` list, same constants, same everything. Read both in
full to confirm; there is no expansion-only Demo content to trace. So
every finding below applies identically to base and expansion.

#### Quest-scoped build-menu gating: the full `$disableunittype` pattern

Confirms and extends the earlier finding in
`TODO-New-Building-Requirements.md` §4. All 22 calls are in one
uninterrupted block at the top of `VAMPIRIC_REVENGE()`, grouped by
authored comment, immediately after `$RevealArea`:

| Comment group | Targets |
|---|---|
| `// No level 3 Palace` | `Palace3` |
| `//No temples` | `Temple_Agrela1`, `Temple_Dauros1`, `Temple_Fervus1`, `Temple_Krypta1`, `Temple_Krolm`, `Temple_Helia1`, `Temple_Lunord1` |
| `//No level 3's of applicable buildings` | `Wizards_guild3`, `Blacksmith3`, `Marketplace3`, `Guardhouse2` |
| `//No other races` | `Elven_bungalow`, `Dwarven_settlement`, `Gnome_hovel` |
| `//No Rogues` | `Rogues_Guild1` |
| `//Disable some support buildings` | `Inn`, `Trading_Post`, `Statue`, `Library1` |
| `//Disable Level 3 buildings` | `Fairgrounds`, `Royal_Gardens`, `Ballista_Tower` |

Four reusable rules fall out of the target names, all confirmed against
`M_Buildings.xml` naming as used elsewhere in this guide:

1. **The argument is a unit-type *name string*, and tier suffixes
   matter.** `Temple_Agrela1` (tier 1) disables the temple family at its
   entry tier; `Wizards_guild3`/`Blacksmith3`/`Marketplace3` disable only
   the top tier while leaving 1 and 2 buildable; `Guardhouse2` blocks the
   upgrade but not the base guardhouse. `Temple_Krolm` has no digit
   because Krolm's temple has no tiers. So **the same primitive does both
   "remove a building entirely" and "cap an upgrade chain," purely by
   which tier name you pass.**
2. **Disabling tier 1 of a chain is how you remove a whole family** —
   the demo never disables `Temple_Agrela2`/`3`, relying on tier 1 being
   unbuildable to make the rest unreachable. That is an assumption about
   upgrade-chain reachability, not an engine guarantee this file proves;
   **UNVERIFIED** whether `$disableunittype("Temple_Agrela1")` alone also
   blocks a tier-2 temple that somehow already exists from being
   upgraded.
3. **Race/guild gating is just building gating.** "No other races" and
   "No Rogues" are not a separate faction switch — they're
   `$disableunittype` on the one guild building that recruits that class
   (`Elven_bungalow`, `Dwarven_settlement`, `Gnome_hovel`,
   `Rogues_Guild1`). This is the reusable recipe for "this quest has no
   class X."
4. **Timing: quest-init only.** All 22 calls run once, synchronously,
   inside the entry function, before any thread is armed.

**Re-enable: verified absent in this file.** Grepped the whole `.gpl`
tree for `enableunittype` — `Demo.gpl` and `mx_Demo.gpl` contain zero
matches (also confirmed by reading both files end to end). The earlier
research's claim holds exactly. The two real base-game re-enable sites
are elsewhere and are worth knowing as the contrast case:

- `GPL/Rules/epic_quest_scripts.gpl` line 125 —
  `$enableunittype("fairgrounds")` fired from a quest-flag-guarded
  condition, paired with `$messageflag(palace,#message_barren_fairground)`
  as the player prompt.
- `GPL/Building_Deaths.gpl` line 696 —
  `$Enableunittype("Dwarven_Settlement")` fired from a *building death
  script*, i.e. an unlock triggered by an object dying rather than by a
  polling check.

So the general pattern is: **disable at init, re-enable from whatever
callback observes the unlock condition** (a polled victory/event thread,
or a death script). Nothing enforces symmetry — a quest that never
re-enables is normal and shipped.

#### Retargeting existing map objects instead of spawning new ones

`VAMPIRIC_REVENGE()` mutates three kinds of pre-placed map object, and
this is the most transferable technique in the file because it needs no
new art, no XML, and no new unit types:

```gpl
$ListObjects (Palace, "Lair", -1, Lairs, #NoHiddenMap);

Castles = $ListTitles (Lairs, "Dark_Castle");
Lair = $ListMember (Castles, 1);
Lair's "IGDeathScript" = $Demo_Dark_Castle_Death;   // per-instance death hook

Dens = $ListTitles (Lairs, "Animal_Den");
Foreach Lair in Dens do
    Lair's "Special_Spawn_Type" = "Giant_rat";      // per-instance spawn table
```

- **`agent's "IGDeathScript" = $SomeFunction` overrides one instance's
  death behavior.** Standard quest technique; `mx_Epic_Quest_Scripts.gpl`
  lines 4035-4045 wraps the list form of the same idea as
  `Setup_Multispawning_Lairs(list Lairs, integer Num_Spawns)`, which sets
  `Lair's "IGDeathScript" = $Lair_Multispawn_Death` plus a
  `"Multi_Spawn_Num"` data field the shared handler reads. **That is the
  pattern to copy for a parameterized death override: one shared handler
  function, per-instance parameters as extra attributes.**
- **`Lair's "Special_Spawn_Type" = "Giant_rat"` reskins what a lair
  produces** without touching lair XML. `Special_Events.gpl`'s
  `Wake_the_Hunters` (lines 754-795) shows the companion flag:
  `Lair's "Special_Spawn_Type" = "Rrongol"` **plus**
  `Lair's "Has_Special_Spawn" = True`. Demo sets only the type, not the
  flag. **UNVERIFIED** which behavior each field controls independently
  (a "guaranteed once" boss spawn vs. a substituted normal spawn type) —
  the two call sites disagree and neither file reads the fields back.
- **Signs are queried as object type `"color"`, not `"sign"`:**
  `$listobjects(palace,"color",-1,signs,#NoHiddenMap)` then
  `$listtitles(signs,"sign_wood")`. Then `$Post_Message(Sign,
  #sign_demo_asleep_dcastle)`. Non-obvious and easy to waste time on.
- **Treasure chests likewise are type `"special_item"`, title
  `"treasure_chest"`,** handed to the shared helper
  `$setup_starting_treasure(chests, 500, 500)` (defined in
  `epic_quest_scripts.gpl` / `mx_Epic_Quest_Scripts.gpl`, which just does
  `$adjustattribute(chest,#ATTRIB_gold, startgold + $randomnumber(randomgold))`
  per chest).

#### Three threads, three different scheduling shapes, one function

The tail of `VAMPIRIC_REVENGE()` is a compact catalogue of the thread
idioms §16.2 introduced, all three armed side by side:

```gpl
AIRootAgent's "VictoryCondition"  = $Vampiric_Victory;
$NewThread( AIRootAgent's "VictoryCondition", #VictoryCondition_callback_frequency );

AIRootagent's "victoryCondition2" = $vampiric_events;
$NewThread( AIRootAgent's "VictoryCondition2", 180000 );

AIRootAgent's "SpecialSpawnScript" = $Spawn_Paladin;
$RunThread (AIRootAgent's "SpecialSpawnScript", 400000 + $RandomNumber (200000), Palace);
```

- Slot 1 = the polled win check (4000 interval, §16.2's constant).
- Slot 2 = a **repeating slot reused as a sequential event chain** (see
  below).
- `"SpecialSpawnScript"` = a *third* named root-agent slot beyond the two
  §16.2 documented, used here for a one-shot `$RunThread` with a
  **randomized fire time** (`400000 + $RandomNumber(200000)`, i.e. ~6.7-10
  game minutes) and an explicit agent argument so the spawn happens
  relative to the Palace. Named root-agent slots are just attributes —
  a modder can add as many as needed; nothing engine-side enumerates
  them.

**`vampiric_events()` is the reusable "scripted event chain on one
repeating thread" idiom.** It is a flag cascade, not a scheduler:

```gpl
if (AIrootAgent's "Quest_flag_1" == FALSE)      // stage 1 … set flag_1 = TRUE
else if (AIrootAgent's "Quest_flag_2" == FALSE) // stage 2 … set flag_2 = TRUE
else if (AIrootAgent's "Quest_flag_3" == FALSE) // stage 3 … $KillThread(self), flag_3 = TRUE
```

Each 180000-tick tick fires exactly one stage, in order, and the final
stage kills its own thread. That gives you an ordered timeline with a
single timer and no per-stage bookkeeping. `Quest_Flag_4` is deliberately
*not* part of the cascade — it's used by the separate victory thread as a
"message already shown" latch, and the file documents the split in
comments (`//Quest Flag 1 - 3 are for scripted events` /
`//Quest Flag 4 is for the found Dark Castle message`). **Reusable
convention: partition the root agent's flag slots by owning thread and
say so in a comment, because nothing enforces it.**

#### Two-phase victory, and the "reveal-triggered message" latch

`Vampiric_Victory()` adds two mechanisms §16 didn't cover:

1. **Fog-of-war-sensitive querying is how you detect "the player has
   discovered X."** The same `$ListObjects(Palace,"Lair",...)` is issued
   twice in one function with *different* flags: once **without**
   `#NoHiddenMap` (line ~131) to test whether the Dark Castle is visible
   to the player, and once **with** `#NoHiddenMap` (line ~152) to test
   whether it still exists at all. Guarded by
   `AIRootAgent's "Quest_Flag_4"` so `$MessageFlag(Lair,
   #message_demo_found_dcastle)` fires exactly once. **This is the
   generic recipe for "notify the player the first time they see
   something": query without the fog filter, latch with a flag.**
2. **Delayed victory via a hand-off thread.** Rather than declaring
   victory inline, it kills its own poll, then
   `AIRootAgent's "UtilityScript" = $Give_Victory;` +
   `$RunThread (AIRootAgent's "UtilityScript", 5500, Palace)` — with the
   comment "Make sure to have the agent that is declared as victor run
   the thread." So `$declarevictory` is called by a 5.5-second one-shot
   *on the Palace*, letting `$PlaySound (Palace, "Victory_Theme",
   "Begin")` play first. `"UtilityScript"` is a fourth named root-agent
   slot. **Reusable: to give the player a beat before the end-of-game
   screen, hand off to a short `$RunThread` instead of returning.**

#### `Demo_Dark_Castle_Death` — the death-override handler contract

Signature `function Demo_Dark_Castle_Death(agent thisagent)`. It is
**not** engine-invoked; it is reached only because `VAMPIRIC_REVENGE()`
assigned it to `Lair's "IGDeathScript"`. Its body is the template for any
custom building/lair death, and the ordering is the point:

1. `$killthread(thisagent's "Spawn_function")` — stop the lair's own
   spawner first. (`"Spawn_function"` is a per-lair thread slot, distinct
   from the root-agent slots above.)
2. Gather + convert: `$ListObjects(ThisAgent,"Monster",-1,Monsters,
   #NoHiddenMap)`, then per monster `$createeffector(Monster,
   "teleport_effector", $GetSpellAttribute("teleport",
   "effector_duration"))` + `$TeleportToUnit(Monster, 50000, ThisAgent,
   0)` + `Monster's "BasicScript" = $Wandering`. Two reusable bits here:
   **`$GetSpellAttribute("<spell>","effector_duration")` reads a spell's
   own tuning data so a script-driven effect stays in sync with the
   spell's XML** instead of hardcoding a duration; and the exclusion
   guard is written as a *script-pointer comparison*,
   `If (Monster's "BasicScript" != $Rooted_Guardian)` — i.e. **you can
   identify a category of unit by which behavior function it runs**, no
   title list needed.
3. `$SpawnUnit (ThisAgent, "Vampire", "Override")` ×2 and `"Zombie"` ×5.
   The bare-string `"Override"` argument is the "ignore the normal spawn
   gating" flag (used the same way in `Undead_Horde`, 17.2).
4. **Then the four shipped loot/cleanup calls, in this order:**
   `$dropgoldinradius(thisagent,$getattribute(thisagent,#ATTRIB_gold))`,
   `$chance_drop_equip(thisagent)`, `$Drop_QItems(ThisAgent)`,
   `$building_death(thisagent)`. **`$building_death` last is the
   important part** — any custom `IGDeathScript` that forgets to call it
   is skipping the engine's normal building-death handling. Copy this
   tail verbatim.

`Spawn_Paladin(agent ThisAgent)` adds one more reusable primitive:
`$FarthestMapCorner(agent)` — "place this as far from that as possible,"
with a `$ListSize` guard so it falls back to the Palace if the reference
object is gone. Paired with `$concatenate(#ATTRIB_NumHealingPotions,2)`
to give the spawned hero starting inventory.

### 19.1 The quest skeleton — one template, four instances

Every quest in this file is the same five-part shape. This is the single
most transferable thing in the batch: it is a complete, working
"what does a quest script have to contain" answer.

```gpl
function MY_QUEST ()                      // (1) engine-invoked entry, nullary
declare
    agent Palace, AIRootAgent;
    list  Palaces;
begin
    AIRootAgent = $RetrieveAgent ("GPLAIRoot");
    AIRootAgent's "Quest_Number" = #QNumber_My_Quest;      // (2) global mode register
    Palaces = $ListPalaces ();
    Palace  = $ListMember (Palaces, 1);

    $Setup_Quest_Music (AIRootAgent);                      // (3) music state machine
    $DisableUnittype ("elven_bungalow");                   //     build restrictions
    // ... per-quest world setup: seed items, retitle lairs, set lair fields ...

    AIRootAgent's "VictoryCondition"  = $My_Quest_Victory;  // (4) the poll thread
    $NewThread (AIRootAgent's "VictoryCondition", #VictoryCondition_callback_frequency);

    AIRootAgent's "VictoryCondition2" = $My_Quest_Events;   //     the sequencer thread
    $NewThread (AIRootAgent's "VictoryCondition2", $Random_Time (240000));

    AIRootAgent's "UtilityScript" = $My_Quest_Time_Limit;   //     optional deadline
    $RunThread (AIRootAgent's "UtilityScript", 1800000);

    AIRootAgent's "Quest_Flag_1" = False;                   // (5) explicit flag init
    AIRootAgent's "Quest_Flag_2" = False;
    // ...
end
```

Three real instances, so the shape is confirmed rather than generalised
from one: `LEGENDARY_HEROES` (lines 8-121, all five parts including the
deadline), `VALE_SERPENTS` (lines 606-679, no deadline, 18 flags), and
`CLASH_EMPIRES` (lines 1465-1550, no deadline, plus the team-splitting
setup of 19.8). `DARKNESS_FALLS` (lines 1891-1970) is the fourth and
adds nothing structural.

Notes on each part, all confirmed against the source rather than assumed:

1. **The entry function is nullary and SHOUTY-CASED by convention only.**
   All four (`LEGENDARY_HEROES`, `VALE_SERPENTS`, `CLASH_EMPIRES`,
   `DARKNESS_FALLS`) take no arguments and return nothing, matching
   §17.5's `Freestyle()`/`VAMPIRIC_REVENGE()` engine-invoked entry-point
   test. Nothing in GPL calls them.
2. **`AIRootAgent's "Quest_Number"` is set first, before anything else
   that could branch on it** — §16.2's global quest-mode register.
   `#QNumber_Legendary_Heroes`, `#QNumber_Vale_Serpents`,
   `#QNumber_Clash_Empires`, `#Qnumber_Darkness_falls`. Shared hooks
   elsewhere read it to specialise themselves; a live example outside
   this file is `mx_war_party.gpl` line 139, which rolls a 50% chance to
   `$Make_Monster_Hunter` **only** when
   `AIRootAgent's "Quest_Number" == #QNumber_Clash_Empires`. **So a quest
   can change monster behavior globally without touching the quest file
   at all, just by existing as a `Quest_Number` some shared module tests
   for.**
3. **`$Setup_Quest_Music` is called in all four, always immediately after
   the palace lookup** (19.4).
4. **Two threads, distinct jobs, and the slot names are misleading.**
   `"VictoryCondition"` polls at `#VictoryCondition_callback_frequency`
   (`mx_Victory_Conditions.gpl` line 7 = **4000** ms; the adjacent
   comment says "once every 2 seconds" and is wrong).
   `"VictoryCondition2"` is *not* a second victory condition in any of
   the four quests — it is the staged-events sequencer (19.3), which
   reschedules itself. `"UtilityScript"` is the optional one-shot
   deadline (19.5).
5. **Flags are initialised explicitly to `False`, one line each, even
   when that is 18 consecutive lines** (`VALE_SERPENTS` lines 661-678).
   Not decorative: 19.3 depends on the sequencer finding a `False`.

### 21.2 The root agent's complete declared surface — two more script slots and five registers

§16-§20 discovered `AIRootAgent`'s fields one quest at a time. This batch
needed four of the previously-unseen ones, so the whole `prototype
AIRoot()` block was read in full (`GPLMx/mx_prototype.gpl` lines 15-97;
base twin `GPL/prototype.gpl` has the same block minus the mx additions —
`Permanent_Hostility` is present in base at line 58, `AI_Reward_Flags`
and `day_counter` were not found there). **There is no undocumented
magic left: the root agent is an ordinary prototype and this is all of
it.** Shipped comments verbatim:

| Field | Type | Shipped comment / use |
|---|---|---|
| `KickoffFunction` | function | (not used by this file) |
| `VictoryCondition`, `VictoryCondition2` | function | §16.2/§19.1 |
| **`SpecialSpawnScript`, `SpecialSpawnScript2`** | function | "These hold the functions (if any) that spawns a creature after a certain amount of time (Like Dirgo in Brashnard)" — **new to this guide**; all four quests here use them, and use them for anything, not just spawning |
| `UtilityScript` | function | §19.5e's deadline slot; here it is `TRADE_ROUTES`' endless 8-second strangleweed pump |
| `MusicScript`, `Track_Number` | function/int | §19.4 |
| `Lair_extra_Delay` | integer | "added onto a lair's spawnrate for every extra lair on a map … frequently overwritten on a per-quest basis in Epic_quest_scripts" |
| `Quest_Flag_1..20` | boolean | §19.1 — **20 of them**, not the 18 §19 happened to see |
| `Message_Check_1..5` | boolean | "Used to check whether to instantiate chained message flags in quests" — unused by this file, listed for completeness |
| `Lair_Delay_Override` | boolean | freestyle lair spawnrate floor |
| `end_coord` | coordinate | §19.5/§20.5b |
| `Quest_Number` | integer | §16.2; comment confirms **"0 if there is no Quest Running"** |
| `Survive_Limit` | integer | freestyle survive-time chunking, "if we don't break the v.c. into chunks, we can overflow the 2mil integer limit" — **an explicit statement that GPL integers top out around 2·10⁶** |
| **`Victory_Score`, `Defeat_Score`** | integer | "used to track victory / defeat scores in some missions. They are used on a quest by quest basis" — 21.3 and 21.8 |
| **`day_counter`** | integer | "keep track of how many days have elapsed in certain quests" — 21.8 |
| **`AI_Reward_Flags`** | list | "Used by the AI player in SIEGE quest" — 21.6b |
| **`Permanent_Hostility`** | boolean | "When this is TRUE, removing attack flags will no longer cause a kingdom to revert to the neutral team. They will be stuck as a hostile team permanently" — 21.6a |
| `Deathmatch_Rules` | boolean | "When this is TRUE, all the special deathmatch Mods will be enforced" — set by `mx_Victory_Conditions.gpl` line 93; `SIEGE` has a commented-out test toggle for it at line 1267 with the shipped warning "TODO: DO NOT LEAVE THIS DEATHMATCH FLAG ON!!!" |
| `Spawn_High_Level_Heroes` | boolean | "a special event script has been kicked off that makes heroes spawn at high levels" — pairs with §20.7's `High_Level_Hero_Birth` |

Two practical consequences, both confirmed by this file's usage:

- **The slot names carry no semantics.** `SIEGE` runs its caravan pump on
  `"VictoryCondition2"` and its AI brain on `"SpecialSpawnScript2"`;
  `TRADE_ROUTES` runs a strangleweed pump on `"UtilityScript"`. §19.1
  already noted `"VictoryCondition2"` being a sequencer; this file
  settles it — **there are six general-purpose function slots on the root
  agent and you may use any of them for anything.** The only real
  constraint is that a slot holds one function, so a quest is capped at
  six concurrent root-level threads unless it parks threads on other
  agents (which 21.4 and 21.7 both do).
- **A quest that wants a counter does not need a new field.** Both
  `SIEGE` and `FORTRESS_IXMIL` re-purpose `Victory_Score`/`Defeat_Score`;
  `FORTRESS_IXMIL` additionally documents its own encoding in a 12-line
  comment block (lines 2338-2352) because it uses **negative values as
  sentinels** (21.8).

### 19.3 The staged-events sequencer — the file's real workhorse

§17.4 catalogued three event-thread lifecycles (one-shot / staged /
repeating). This file uses a **fourth, more capable shape** that deserves
its own name because all four quests are built on it and nothing in §16-§18
documents it: a **self-pacing linear sequencer**, where one thread walks a
numbered flag chain and *sets its own next delay per stage*.

The canonical form, from `Vale_Serpents_Events` (lines 743-1070, 18
stages) — `Clash_Empires_Events` (1595-1848, 8 stages) and
`Darkness_Events` (2016-2216, 6 stages) are the same shape:

```gpl
Function Vale_Serpents_Events ()
Begin
    AIRootAgent = $RetrieveAgent ("GPLAIRoot");
    ...
    If (AIRootAgent's "Quest_Flag_1" == False)
        begin
            // ... stage 1 effects ...
            AIRootAgent's "Quest_Flag_1" = True;
            $SetThreadInterval (AIRootAgent's "VictoryCondition2", $random_time (60000));
        end
    Else if (AIRootAgent's "Quest_Flag_2" == False)
        begin
            // ... stage 2 effects ...
            AIRootAgent's "Quest_Flag_2" = True;
            $SetThreadInterval (AIRootAgent's "VictoryCondition2", 3000);
        end
    ...
    Else                                     // all flags consumed
        begin
            // ... endless-pressure fallback ...
            $SetThreadInterval (AIRootAgent's "VictoryCondition2", $random_time (200000));
        end
End
```

Five properties worth knowing before cloning it:

- **The `Else if` chain makes the flags a program counter, not a set of
  independent switches.** Exactly one stage fires per invocation, always
  the lowest un-consumed one. That is why 19.1's explicit `= False` init
  block matters, and why the flags must be numbered contiguously.
- **Each stage picks its own next interval.** Values in this file range
  from `3000` (a deliberate 3-second "and immediately after that…" beat,
  Vale stages 2 and 10) up to `$random_time (200000)`. **This is how the
  quests get dramatic pacing out of a single timer** — no additional
  threads, no per-stage bookkeeping.
- **The terminal `Else` is the difficulty ratchet.** Vale, Clash and
  Darkness all end in an unnumbered `Else` (or a final flag that is never
  set true) that spawns a wave and reschedules itself forever, so the
  quest keeps escalating after the script runs out of authored beats.
  Vale's fallback (lines 1050-1067) is the same roster as its stage 17.
- **Stage bodies are the only per-quest content.** Every stage is some
  combination of `$MessageFlag`, `$minimapanimation`,
  `$RevealArea`, `$SpawnUnit`, `$Play_Endgame_Music`, and a helper call —
  all already documented in §17 except the ones in 19.4/19.9.
- **`$random_time (N)`** (§17) is used for nearly every interval, so no
  two playthroughs get identical pacing; the handful of bare integers
  (`3000`) are the deliberate exceptions.

#### A second, different escalator: keyed off world state instead of a timer

`LH_Barrows_Death` (lines 447-600) is worth separating out because it is
the same escalation idea with **no thread at all** — it is an
`IGDeathScript` installed on six lairs (19.7), and it branches on *how
many of its own kind are left*:

```gpl
ListSize = $ListObjects (ThisAgent, "lair", -1, Barrows, #NoHiddenMap,
                         #CheckTitles, "AncientBarrow");
If (ListSize == 5) begin ... 2 Trolls per hero ... end
If (ListSize == 4) begin ... 1 GreaterGorgon per hero ... end
If (ListSize == 3) begin ... 3 Minotaurs per hero ... end
If (ListSize == 2) begin ... 24 PC-hunting goblins ... end
If (ListSize == 1) begin $Play_Endgame_Music (AIRootAgent); ... end
If (ListSize == 0) AIRootAgent's "End_Coord" = $LocationOf (ThisAgent);
$Lair_Death (ThisAgent);                      // then the normal behavior
```

Four reusable details: **the count is taken inside the dying lair's own
death script, so the lair being destroyed is still counted** (5 means
"this is the first of six"); **per-hero scaling** (`Foreach Hero in
Heroes` around the spawn, so the punishment tracks the player's actual
strength rather than a fixed number); **the last branch records
`End_Coord`** for the victory camera (19.5); and **the override ends by
calling the stock handler** `$Lair_Death (ThisAgent)`, which is the clean
way to add behavior to a death without reimplementing gold drops, item
drops and building teardown (see 19.7 for what that stock handler does).

#### Shipped bug: `=` where `==` was meant

`Darkness_Events` stages 6 and 7 are written

```gpl
Else if (AIRootAgent's "Quest_Flag_6" = True)     // line 2160, single '='
Else if (AIRootAgent's "Quest_Flag_7" = True)     // line 2192, single '='
```

while stages 2-5 in the same function correctly use `== False`. Both
lines compiled and shipped. **Do not copy this.** What the compiler
actually does with `=` in a condition — treat it as comparison, or
perform an assignment whose value is then tested — is **UNVERIFIED**; we
have no GPL grammar document that settles it (`SDK/Documentation/GPL
Reference.pdf` was noted as unreadable in §14). Either reading breaks the
intended behavior: as a comparison it tests `False == True` and the stage
never fires; as an assignment it evaluates truthy every time and stage 6
becomes an infinite loop that starves stage 7. Determining which happens
in the shipped game needs a test, not more source reading.

### 17.4 "Random event" vs. "special event": the actual mechanical difference

Not a naming distinction. Confirmed by reading both:

| | Random event (17.2) | Special event (17.3) |
|---|---|---|
| Unit of code | A bare function, any signature | A function with the fixed signature `(string AgentName)` |
| Owns a schedule? | **No** — the caller times it | **Yes** — it reschedules itself via `$SetThreadInterval` |
| Owns state? | **No** — stateless, fire-and-forget | **Yes** — up to 10 `Event_Flag_N` booleans on its own `EventAgent` |
| How it's chosen | GPL picks it: `$RandomNumber(N)+1` inside a tier dispatcher | **Engine picks it by name**: `$GetSpecialEvent1Script()` → `$LookupFunction` |
| Lifetime | Instantaneous | Whole game, until it `$KillThread`s itself |
| Where it runs | Any quest that calls it | Freestyle games only (`Freestyle()` is its only launch site) |
| How many at once | One per dispatch | Exactly two slots (`EventAgent1`, `EventAgent2`) |
| Player notification | `$messageflag(palace, #Message_*)` per branch | Mostly none (commented out in `Random_Disasters`); flavor delivered by `$minimapanimation`/`$revealarea` instead |

The two systems compose: `Random_Disasters` is a special event whose body
is a random-event dispatcher. **So the reusable framing is "special
event = a scheduled, stateful plugin; random event = a stateless effect
you can call from anywhere," and a new mod should generally write effects
as random-event-shaped functions and schedule them from one special-event-
shaped driver.**

### 22.4 `Freestyle()` in base form, the post-victory handoff, and what the second victory function is for

#### a) Base `Freestyle()` is three statements

Line 4084. Read in full, and it is worth quoting because §16.2 and §17
both discussed it from the mx side only:

```gpl
function Freestyle()
declare
    agent AIRootAgent;
begin
    AiRootAgent = $RetrieveAgent ("GplAiRoot");
    $SetUp_Freestyle_Music (AiRootAgent);
    $setvictorycondition();
end
```

That's it. **All freestyle behavior lives behind `$SetVictoryCondition`
(§16.2) and the lair/spawn defaults** — there is no freestyle-specific
world setup, no treasure, no events. The mx version (`mx_Epic_Quest_
Scripts.gpl` 4048-4109, read in full for the diff) adds exactly two
things on top of these three statements:

1. **The special-event kickoff pair** — §17.3/§17.7's
   `$GetSpecialEvent1Script`/`$GetSpecialEvent2Script` →
   `$CreateAgent("EventAgent","EventAgentN")` → `$LookupFunction` →
   `$NewThread(…, "EventAgentN")` → immediate first call. Already
   documented in §17; nothing new in the base-vs-mx comparison except
   that **base mode has no special events because base `Freestyle()`
   never asks for them**, which is a cleaner statement of §17.0's
   expansion-only finding than "the file only exists under `GPLMx`."
2. **A `$HasAttribute`-guarded write:**
   ```gpl
   if ( $HasAttribute ( "Lair_Delay_Override", AIRootAgent ))
       AIRootAgent's "Lair_Delay_Override" = TRUE;
   ```
   **This is feature detection, used to keep one source file compatible
   with two different root-agent prototypes.** `$HasAttribute(name,
   agent)` (note the argument order: name first) lets GPL ask whether a
   field exists before writing it. Useful pattern for any mod that wants
   to run in both modes against a field only one prototype declares. The
   shipped comment explains the field's purpose: freestyle needs a
   minimum time added to every lair's spawn rate "because there are times
   when there are no lairs onmap, but many offmap." Related to 22.7.

#### b) `rescue_keep_playing` — the minimal post-victory thread

Line 585. Four lines: find the palace, call `$Rescue_Buildings(palace)`.
Nothing else.

It exists because the rescue subsystem (§20.4, 22.2) is **driven by a
poll**, and `$declarevictory` is followed by `$KillThread` of that poll.
Without a replacement, a player who chose "keep playing" would find that
enemy outposts stopped defecting. So seven quests **reassign the same
`"VictoryCondition"` slot to `rescue_keep_playing` and re-thread it** at
the normal poll frequency, immediately after killing the real victory
poll — eight install sites in all: Holy Chalice (497 in
`Holy_Chalice_Victory`, 569 in `Holy_Chalice_Victory_2`), Crown (680),
Dark Forest (844), Slay the Dragon (1577), Tomb of the Dragon King (1720),
Liche Queen (2748), Slave Pits (3446).

**The reusable rule:** if any of your quest mechanisms is implemented as a
per-tick poll rather than an event hook, you need a stripped-down
post-victory thread carrying just that mechanism, and the cheapest place
to put it is the slot you just vacated. This is a distinct pattern from
§19.5d (threads *surviving* victory untouched) — here the thread is
deliberately *downgraded* to its still-needed part.

#### c) `*_victory2` / `*_Victory_2` is a deadline arbiter, not a second win condition

Four quests ship two victory functions. **In every case the second one is
a slow one-shot timer whose job is to decide the game if the first one
hasn't**, i.e. it is §19.5's `UtilityScript` deadline moved into the
`"VictoryCondition2"` slot. Confirmed by reading all four:

| Quest | Second fn (line) | Interval | Behavior when it fires |
|---|---|---|---|
| Holy Chalice | `Holy_Chalice_Victory_2` (535) | 1 800 000 | If `Quest_Flag_1` (chalice recovered) → kill both threads, `$declarevictory`, install `rescue_keep_playing`. Else → kill both threads, **`$declareloss`** |
| Deal with the Demon | `demon_victory2` (1311) | 1 200 000 | Same shape, gold test instead of a flag, **plus the tick-counting workaround (d)** |
| Elven Treachery | `Elven_victory2` (1897) | 1 800 000 | Same shape, gold test; `$declareloss` with no `$KillThread` first |
| Day of Reckoning | `DOR_Victory2` (1143) | 5 000 | **The exception** — not a deadline at all; a fast upkeep thread running `$Rescue_Buildings` + `$Rescue_pets` + the lightning harasser (22.6d) |

So the naming is a convention with one violation, and the mechanism is:
**duplicate the win test into a second function, add an `else` that calls
`$declareloss`, and thread it at the deadline interval.** The win test is
genuinely duplicated source in all three real cases — there is no shared
helper — which is why they read as "two victory functions."

`Slay the Dragon` is a fourth, different use of the same slot: see 22.6e.

#### d) A ~1 800 000 ms interval ceiling, and the tick-counting workaround

`demon_victory2` (1311-1330) opens with:

```gpl
if (AIRootAGent's "Quest_flag_1" == FALSE)
    begin
        // this is to get around the time limit of 1.8 million millseconds
        AIRootAgent's "Quest_flag_1" = TRUE;
    end
else
    // ... the real win/lose decision
```

The thread is installed at 1 200 000 ms, so burning the first firing gives
an effective 2 400 000 ms deadline. **`Holy_Chalice_Victory_2` carries the
identical block, commented out, with the identical comment** (lines
548-556) and an interval of exactly 1 800 000 — the ceiling value.
`Elven_victory2` also uses exactly 1 800 000.

**What is confirmed:** two independent shipped sites name 1 800 000 ms as
a limit, one actively works around it, and no shipped `$NewThread` /
`$RunThread` / `$SetThreadInterval` interval in this file exceeds
1 800 000. **What is not confirmed: that the engine actually enforces a
cap, or what it does when exceeded** (clamp, wrap, or never fire). That is
an engine-side question and the only evidence is the developers' own
comment. **UNVERIFIED** as an engine behavior — but the workaround itself
is a documented, shipped pattern and is the right thing to copy if you
need a deadline longer than ~30 minutes: **count firings in a flag rather
than lengthening the interval.**

---

## Chapter 2: Victory, Loss and Objectives

Declaring wins and losses, polling patterns, graded outcomes, objective messaging.

### 16.2 `SetVictoryCondition()` — the freestyle dropdown dispatcher

`victory_conditions.gpl` holds one dispatcher, four victory-condition
bodies, and two helpers. The dispatcher is called from exactly one place
in the shipped tree: `GPL/Rules/epic_quest_scripts.gpl` line 4095, inside
`function Freestyle()` ("This will be called at the start of any
Freestyle game"), immediately after `$SetUp_Freestyle_Music`. Mx mirror:
`mx_Epic_Quest_Scripts.gpl` line 4107. **Named epic quests never call it**
— they set up their own victory threads directly (see 16.3).

**Dispatch table — every `index ==` branch, in file order:**

| `index` | `Quest_Number` set | Handler assigned to `AIRootAgent's "VictoryCondition"` | Thread call | Uses modifier? |
|---|---|---|---|---|
| 2 | `#QNumber_Survive_Time` (502) | `$VictoryCondition_One` | `$RunThread(..., Time * 60 * 1000)` — one-shot, re-armed | yes, as **days** |
| 1 | `#QNumber_Gather_Gold` (503) | `$VictoryCondition_Two` | `$NewThread(..., 4000)` — polling | yes, as **gold** |
| 0 | `#QNumber_Eliminate_Enemies` (501) | `$VictoryCondition_Three` | `$NewThread(..., 4000)` — polling | no |
| 3 | `#QNumber_Last_Palace` (504) | `$VictoryCondition_four` | `$NewThread(..., 4000)` — polling | no |
| any other | — | nothing | nothing | — |

`#QNumber_*` values from `globals.gpl` lines 666-669 (identical in
`mx_Globals.gpl` 691-694). The poll interval is
`#VictoryCondition_callback_frequency` = 4000, declared at the top of
`victory_conditions.gpl` itself — note the comment says "once every 2
seconds" while the value is 4000, one more data point that GPL duration
units are not plain milliseconds at the rate the comments assume
(consistent with the unresolved tick-rate question in
`.kiro/steering/majesty-modding.md`).

**How the two exe-side inputs feed it:**

- `$GetVictoryConditionIndex()` — read once, first line of the function,
  into a local `integer index`. Per the function's own header comment it
  is the **zero-based position of the selection in the setup-menu
  dropdown**. It has exactly one call site in the entire SDK tree (this
  function) in each of base and mx.
- `$GetVictoryConditionModifier()` — the dropdown's companion numeric
  field. Called twice in the `index == 2` branch (once stored into
  `AIRootAgent's "Survive_Limit"`, once re-read for a `$DebugOut`), once
  in the `index == 1` `$DebugOut`, and once at the top of
  `VictoryCondition_Two` (`gold_goal = $GetVictoryConditionModifier()`).
  **Its unit is per-branch, decided by GPL, not by the engine:** the
  survive branch treats it as days (`Time * 60 * 1000`), the gold branch
  treats it as a raw gold threshold. Nothing type-checks this.
- **`AIRootAgent's "Quest_Number"` is the outbound half of the
  contract** — set here purely so other scripts can query which mode is
  running ("Set Quest_Number so units can querry it"). This is the same
  global-quest-mode register the epic quests use (`Monster_Births.gpl`
  lines 104-233 branch on it, `mx_LowLevel.gpl` line 86 reads it for a
  string-index lookup). Reusable pattern: one integer on the root agent
  as a global mode flag any script can read.

**Reusable mechanisms in the four bodies:**

1. **The re-armed long-timer idiom (`VictoryCondition_One`).** GPL
   `$RunThread` delays overflow on large values, so the survive-time
   condition chunks the wait: store the remainder in
   `AIRootAgent's "Survive_Limit"`, arm at most 20 units at a time
   (`Time = 20; Survive_Limit -= 20`), and have the handler re-arm
   itself until the remainder hits 0, then win. The chunking code is
   duplicated verbatim in the dispatcher and in the handler — copy both
   halves if reusing. **This is the documented workaround for
   long-duration timers in GPL** and generalizes to any multi-minute
   scheduled event, not just victory.
2. **Timer unit conversion:** `Time * 60 * 1000` — one "day" of the
   modifier is 60,000 GPL time units, i.e. game days are being treated
   as 60-second units here.
3. **`$KillThread(AIRootAgent's "VictoryCondition")` self-cancel.**
   Because the handler was stored on the root agent as a function
   pointer before threading, the handler can cancel its own poll loop by
   name (`VictoryCondition_Two`, `VictoryCondition_Three`). Storing a
   thread's entry function in a named attribute purely so it can be
   killed later is the general pattern; epic quests extend it to a
   second slot, `"VictoryCondition2"`.
4. **Win/lose broadcast helpers.** `victoryforall()` loops
   `$ListPalaces()` calling `$declarevictory(palace)` on each;
   `multiple_loss(list losers)` loops `$declareloss(loser)`. The gold
   branch composes them: `$DeclareVictory(richest)`, then
   `all_palaces -= richest_player` and `$multiple_loss(all_palaces)`.
   Note `$declarevictory` also takes an optional second argument used
   elsewhere as an end-of-game camera focus — accepted both as a stored
   coordinate (`epic_quest_scripts.gpl` line 4058,
   `AIRootAgent's "end_coord"`) and as an agent (`Quest_Actives.gpl`
   line 118, `$declarevictory(palace,thisagent)`).
5. **"Eliminate all enemies" is a five-list check, and the list choice
   is the interesting part** (`VictoryCondition_Three`). It requires all
   of `"lair"`, `"building"`, `"hero"`, `"Invisible"`, and
   `"camouflaged"` enemy lists to be empty, all with
   `#NotMyTeam, #NoHiddenMap` and (for the last three)
   `#InsideOtherUnits`. `"monster"` is deliberately commented out in both
   base and mx — roaming monsters don't block victory, lairs do. The
   `"Invisible"`/`"camouflaged"` pseudo-types exist precisely because a
   `"hero"` query misses them; **any "have I cleared the map" check a
   modder writes needs those two extra queries or it will hang on a
   hidden unit.** The function also opens with a defensive
   `$isvalidgamepiece` loop that pops dead palaces off the front of
   `$ListPalaces()` and returns early if none survive.
6. **Forced team-splitting for free-for-all (`index == 3`).** The
   dispatcher walks `$ListPalaces()` and, for every palace sharing team
   number with the first, assigns `$setplayerteamnumber(p2,
   $newteamnumber())`. Plus, if `AIRootAgent` has a `"Deathmatch_Rules"`
   attribute at all (`$HasAttribute` guard), it sets both
   `"Permanent_Hostility"` and `"Deathmatch_Rules"` to TRUE. This is the
   reusable "make everyone mutually hostile" recipe, and it is the same
   `"Deathmatch_Rules"` flag `CanIBuildThisBuilding` branches on in
   16.1 — one root-agent flag shared across unrelated rule systems.

**Base vs. expansion (`mx_Victory_Conditions.gpl`): effectively
identical, one real behavioural difference.** `SetVictoryCondition`,
`VictoryCondition_One`, `_Two`, `_Three`, `victoryforall` and
`multiple_loss` are line-for-line the same (same `#QNumber_*`, same 4000
frequency, same commented-out `"monster"` check). The single divergence:
**base `VictoryCondition_four` has an `else` branch that re-splits teams
on every poll** (repeating the dispatcher's `$setplayerteamnumber`
walk each 4000 ticks while more than one palace survives); **the mx
version drops the `else` entirely** — it only checks
`$listsize(all_palaces) == 1` and declares victory. So in the expansion,
team-splitting happens once at setup; in the base game it is re-applied
continuously. No new expansion-only victory condition exists — the
expansion added an `outpost` construction rule (16.1) but zero new
victory modes.

### 16.3 Can a modder add a NEW victory condition? Direct answer

**Yes for quest-driven victory; no for a new freestyle dropdown entry.**

*Yes, GPL-only, no exe change* — the shipped game already does this ~30
times. Named quests never touch `SetVictoryCondition`; they use the raw
pattern instead:

```gpl
AIRootAgent's "Quest_Number" = #QNumber_MyQuest;
AIRootAgent's "VictoryCondition" = $My_Victory_Check;
$NewThread( AIRootAgent's "VictoryCondition", #VictoryCondition_callback_frequency );
```

then inside the handler, `$declarevictory(palace)` /
`$declareloss(palace)` / `$KillThread(AIRootAgent's "VictoryCondition")`.
Confirmed at `epic_quest_scripts.gpl` lines 178, 652, 747 (which assigns
a wholly custom `$Dark_forest_victory`), 2711, and throughout
`GPLMx/Rules/Quests_1-3.gpl`. **`SDK/SpecialItemsExample/
SpecialItemsExample.gpl` line 56 does exactly this in shipped SDK
example code** (`$DeclareVictory(palace, AIRootAgent's "End_coord")`
then `$KillThread`), so it is a sanctioned modder path, not an internal
trick. A quest's own GPL entry function (the one the `.q` file names) is
free to skip `$setvictorycondition()` entirely and arm its own thread —
our own `QuestMapGenerator/GPL/default_quest.gpl` is the minimal
opposite case, calling `$setvictorycondition()` and nothing else.

**CORRECTION to the "not GPL-only" half below, found later (same pass
that produced §17.7): the victory dropdown's labels are ALSO CAM `STRT`
data, not exe-hardcoded.** `Data/gpltext.cam`'s `STRT` section has a
`GOAL` entry — 138 bytes, header count field = **4** — holding exactly
the four dropdown labels, in this table order:

| `GOAL` row | Label |
|---|---|
| 0 | `Survive for Specified Time` |
| 1 | `Acquire Specified Amount of Wealth` |
| 2 | `Eliminate all` |
| 3 | `Destroy all other players` |

Note this is the **base game's** `gpltext.cam` (not `mx_`), so unlike the
special-event registry (§17.7, expansion-only) the victory dropdown is a
base-game data table. Companion UI strings live in `textdata.cam`'s
`GMTX` table (`Survive specified time`, `Eliminate all foes`,
`Last Palace standing`, `Survive for %d days`, and the modifier prompt
`Enter the number of days to survive`) — so the dropdown label and the
in-game status/prompt text are separate strings in separate tables, and
they don't match word-for-word.

**What this changes:** relabeling a repurposed victory condition is
data-editable (override `GOAL` via a quest CAM, same confirmed
`STRT`-override path as §17.7), so the "the UI label will lie" caveat
below is fixable after all. **What it does NOT resolve, stated plainly:**
whether adding a 5th `GOAL` row makes a 5th dropdown entry appear and
causes `$GetVictoryConditionIndex()` to return 4 — the header carries an
explicit count field, which is encouraging, but the engine may still read
a fixed 4. **Also UNRESOLVED and worth care: the `GOAL` row order does
not obviously match the GPL branch indices.** `GOAL` row 0 is "Survive"
while §16.2's dispatcher handles survive at `index == 2`; if the index
were simply the row position these would agree, and they don't. So either
the displayed order differs from table order, or the index is not the row
position. **Use the function's own `$debugout(911,"victory condition
index:",index)` to establish the real mapping empirically before
repurposing a row** — this is exactly why that debug line matters.
Tracked as an in-game test in `TODO-GameTests.md`.

*Original finding, retained — the GPL-side half of it still stands* —
adding a **fifth selectable entry to the freestyle
setup menu's victory dropdown.** Adding `else if (index == 4)` to
`SetVictoryCondition` is trivial and compiles, but nothing can ever
produce a 4: the value comes from `$GetVictoryConditionIndex()`, an
engine primitive reporting the UI dropdown's selected row. The dropdown's
contents are not in GPL (no list of victory-condition labels exists in
any `.gpl` file), not in `M_*`/`MX_*` XML, and not in `.mqxml` — a grep
of every `.mqxml` in the workspace for `Victory` returns zero matches,
and `QuestMapGenerator`'s own `.q` format research documents the quest's
GPL entry function as the only quest-level hook, with no
victory-condition field. So the labels live exe/UI-side (presumably the
`.cam`/UI string data), and **inserting a new row is an exe/UI change,
not a data change.**

**What the function's "must be maintained in parallel with that list"
comment actually implies for moddability:** the coupling is
positional and one-directional. The engine hands over an anonymous
integer; the *meaning* of each integer lives entirely in this GPL
function. Consequences:

- **You can freely redefine what an existing dropdown row does** —
  swap `index == 1`'s body for any custom check and "Gather Gold" in the
  UI now runs your logic. The label will lie, but the mechanism is fully
  yours, with `$GetVictoryConditionModifier()` available as a
  player-settable integer parameter for free. This is the most practical
  route to a custom freestyle victory condition without exe work.
- **The dropdown order is a hardcoded contract you can't see from GPL.**
  Note the branch order in the file (2, 1, 0, 3) does not match dropdown
  order — the mapping is only discoverable by observing the UI or by
  reading the `$debugout(911,"victory condition index:",index)` the
  function helpfully emits on every freestyle start. Use that debug line
  to confirm which row is which before repurposing one.
- **Falling off the end is silent.** An unrecognized index sets no
  `Quest_Number`, assigns no handler, and starts no thread — the game
  runs with no victory condition at all rather than erroring. Any custom
  dispatcher should add a fallback branch.
- **UNVERIFIED:** what `$GetVictoryConditionIndex()` returns outside a
  freestyle game (a custom quest that calls `$setvictorycondition()`
  with no dropdown ever shown). Our own
  `QuestMapGenerator/rgs_format.py` warning (lines 1263-1268) asserts the
  default behaves as "destroy all enemy structures," which would mean
  index 0 — consistent, but that's a project-internal claim, not a
  source citation, and no default value appears anywhere in GPL.

### 19.5 Win/lose vocabulary: what this batch adds to §16.2

§16.2 already covers `SetVictoryCondition`, `$declarevictory` (including
its optional camera-focus second argument in both coordinate and agent
form), `$declareloss`, and the `$KillThread(AIRootAgent's
"VictoryCondition")` teardown. Five additions from this file:

**(a) `$IsTitleAlive (agent palace, string title) is boolean` — the
"named boss still standing?" test.** Defined in
`GPLMx/Rules/mx_Epic_Quest_Scripts.gpl` line 7 (base twin:
`GPL/Rules/epic_quest_scripts.gpl` line 7, same body — this helper *is*
available in base mode). Read in full:

```gpl
$ListObjects (palace, "monster",   -1, monsters, #NoHiddenMap);
$listobjects (palace, "invisible", -1, l2,       #nohiddenMap);
monsters = $addlists (monsters, l2);
monsters = $listtitles (monsters, title);
return ($listsize (monsters) > 0);
```

Three things that make it more than a convenience wrapper:

- **It unions the `"monster"` and `"invisible"` object classes**, so a boss
  that has hidden or phased itself still counts as alive. §16.2 made the
  same point about `"Invisible"`/`"camouflaged"` for captives — this is a
  second independent instance, and the reason a hand-rolled
  `$ListObjects(...,"monster",...)` check has a false-negative a modder
  will not see coming.
- **A gravestoned boss reads as NOT alive**, which is exactly what
  `Darkness_Victory` (line 2008) wants: its comment is "If both Styx and
  Stones are gravestones (or gone), then the player wins." The mechanism
  behind that is 19.10 — the bosses swap their own `"Type"` while dead.
- **Four other quests use it in preference to the obvious
  `$ListTitles`+`$ListSize`**, and in all four cases the `$ListSize`
  version is sitting right there commented out
  (`mx_Epic_Quest_Scripts.gpl` lines 818-819, 2686-2687, 3407-3408,
  3975-3976). Someone deliberately replaced the naive check everywhere.

**(b) Two-stage victory: a gate flag in front of the real test.**
`Darkness_Victory` will not even look at the bosses until all the lairs
are gone:

```gpl
If (AIRootAgent's "Quest_Flag_1" == False)
    begin
        // poll for zero "WightsTomb" lairs; when true, latch the flag
    end
Else
    begin
        If ($IsTitleAlive (Palace, "Styx") == False
            && $IsTitleAlive (Palace, "Stones") == False)
            $declarevictory (palace, AIRootAgent's "End_Coord");
    end
```

**The reusable shape for any multi-objective quest: one `Quest_Flag_N` per
completed objective, latched inside the victory poll itself, with the
later objectives' tests behind `Else`.** Note this costs nothing extra —
it reuses the same flag register the sequencer uses (19.3), just on the
other thread.

**(c) Loss by attrition of something you cannot build.** `VALE_SERPENTS`
is the sharpest design pattern in the file, and it is three lines in two
places. Setup disables the building:

```gpl
$DisableUnittype ("Elven_bungalow");                    // line 634
```

…while the victory poll makes losing all of them a defeat:

```gpl
If ($ListObjects (Palace, "building", -1, Bungs,
                  #CheckTitles, "Elven_Bungalow") == 0)
    $DeclareLoss (Palace);                              // lines 715-720
```

…and the sequencer is the *only* source of them (stages 4, 10, 13, 14
each `$SpawnUnit` one or two). **So "protect these, you can't make more"
is composed entirely out of already-documented primitives** — §16's
`$disableunittype` gate plus `$DeclareLoss` plus timed spawns — with no
new engine support. Worth calling out because a modder would reasonably
assume protect-the-object needed a dedicated mechanism.

**(d) `$declarevictory` does not end the script's world — quests keep
running after the win.** Both Vale and Clash *replace* their sequencer
with a new endless one at the moment of victory:

```gpl
$declarevictory (palace, AIRootAgent's "End_coord");
$KillThread (AIRootAgent's "VictoryCondition");
$KillThread (AIRootAgent's "VictoryCondition2");
AIRootAgent's "VictoryCondition2" = $Vale_Post_Victory_Events;   // line 733
$NewThread (AIRootAgent's "VictoryCondition2", $Random_Time (200000));
```

`Vale_Post_Victory_Events` (lines 1290-1360) and `clash_post_victory`
(lines 1853-1883) then spawn waves forever. **This is the mechanism behind
"keep playing after you win"** — the engine leaves GPL threads alive after
`$declarevictory`, so the *only* thing needed is to reuse the freed slot.
Vale's version rolls a uniform 1-5 over five hardcoded rosters
(§17.2's dispatcher shape); Clash's is a single unconditional wave.
**Also note both drop the `#force_*` artifice they used pre-victory** —
`Vale_Post_Victory_Events`' spawns pass only `#Monster_player`, so the
post-win monsters use their default AI.

**(e) `UtilityScript` as a hard deadline, and a punishment that is not a
loss.** §17 identified `"UtilityScript"` as a fourth named root-agent slot
(used there as a 5.5-second one-shot before `$declarevictory`).
`LEGENDARY_HEROES` uses it at the other end of the scale:

```gpl
AIRootAgent's "UtilityScript" = $Legendary_Heroes_Time_Limit;
$RunThread (AIRootAgent's "UtilityScript", 1800000);        // line 101
```

`$RunThread(fn, delay)` fires once after 1,800,000 ms. The handler
(lines 397-443) re-checks the win condition and, if unmet, does **not**
call `$DeclareLoss` — it fires `$MessageFlag (Palace,
#Message_LH_Earthquake_You_Lose)` and sets `AIRootAgent's
"Quest_Flag_10" = True`. That flag is read by the *victory* thread, which
then casts two `$CreateSpellUnit(building,"Earthquake",building)` per poll
on randomly chosen player buildings, forever (lines 288-330). **So the
generic recipe for a soft time limit is: one-shot `UtilityScript` sets a
flag; the already-running poll thread reads the flag and applies
escalating pressure.** The player can still win — 19.2's table lists no
loss condition for this quest because there genuinely isn't one.

**Two smaller items, both one-liners:**

- **`Palace's "heroes_to_upgrade" = 2`** (line 23, comment: "Palace is
  easy to upgrade to level 2") — a writable palace field, declared
  `integer heroes_to_upgrade; // how many heroes are needed to upgrade
  the palace` in `mx_prototype.gpl` lines 564 and 660. It is live, not
  decorative: `mx_Building_Births.gpl` line 1002 pushes it into the
  engine attribute with `$setattribute (thisagent,
  #ATTRIB_Upgrade_herosNeeded, thisagent's "heroes_to_upgrade")`, and
  line 154 shows the stock progression re-setting it to 4 when the palace
  reaches level 2. **This is the cleanest example in the batch of a
  quest retuning a core game rule with one assignment.**
- **`$PlaySound (palace, "<unit title>", "Taunt")`** — `Darkness_Events`
  makes the two named bosses taunt the player from off-screen (lines
  2027, 2100, 2163; one stage rolls 50/50 between them). Same three-arg
  `(agent, soundSetName, cueName)` form §17 documented for
  `$PlaySound (Palace, "Victory_Theme", "Begin")`; what's new is that the
  sound-set name here is a *unit type's* name, so a boss can speak
  without existing on the map yet.

**Case-sensitivity gotcha, worth knowing before it costs someone an
afternoon.** This file *writes* `AIRootAgent's "End_Coord"`
(`LH_Barrows_Death` line 597, `Darkness_Victory` line 2013 reads the same
casing) but *reads* `AIRootAgent's "End_coord"` in
`Legendary_Heroes_Victory` line 147 and `Vale_Serpents_Victory` line 723.
Since the shipped victory camera is presumably not broken, **attribute
name lookup is evidently case-insensitive** — consistent with GPL
identifiers generally (`$declarevictory`/`$DeclareVictory`,
`thisagent`/`ThisAgent` used interchangeably throughout). Flagged as
**UNVERIFIED** because it is inferred from "the shipped game works," not
from a grammar document or a test; a modder should still keep casing
consistent.

### 20.5 Poll-thread patterns: latch-on-appearance, and a victory camera that follows the boss

Two additions to §19.5's win/lose vocabulary, both from the polling side.

#### (a) Latch-on-appearance before testing disappearance

`Scions_victory` (lines 366-512) sequences a three-boss chain from a
single poll thread, and it uses **paired flags — one "this stage
happened," one "the spawn has been seen"** — rather than a flat chain:

| Outer gate | Inner gate | Test | Action |
|---|---|---|---|
| `Quest_flag_1 == FALSE` | — | enemy heroes `== 0` | spawn scion #2 + a 16-unit escort; latch `flag_1` |
| `quest_flag_2 == FALSE` | `quest_flag_3 == FALSE` | enemy heroes `== 1` | latch `flag_3` **only**; also converts every `#CheckSubtypes,"Animal"` monster with `$make_raider` |
| " | `quest_flag_3 == TRUE` | enemy heroes `== 0` | spawn 24 `Strangleweed` + scion #3; latch `flag_2` |
| `quest_flag_4 == FALSE` | `quest_flag_5 == FALSE` | enemy heroes `== 1` | latch `flag_5` only |
| " | `quest_flag_5 == TRUE` | enemy heroes `== 0` | `$declarevictory` |

**The reusable rule: when a poll advances on "count reached zero," never
test for zero immediately after spawning the thing that must be killed —
wait for the count to reach one first.** Two independent copies of the
guard in the same function, plus the commented-out code inside both
confirm-blocks (the level-up/retitle work was moved to the spawn site and
only the latch was left behind), say this was written deliberately. **Why
it's needed is an inference** — the obvious reason is that a freshly
`$SpawnUnit`ed agent may not be visible to `$ListObjects` on the very
next poll, which would make a bare `== 0` test fire the next stage
instantly and cascade the whole quest — but nothing in source states it,
so the *reason* is **UNVERIFIED** while the pattern itself is confirmed.

Note also **`quest_flag_4` is never set TRUE anywhere** — deliberate,
because that branch ends in victory, so it is the terminal stage of the
chain. Same trick §19.3 noted for a final flag that is never consumed.

#### (b) `end_coord` as a live tracker, not a death record

§19.5 found `End_Coord` written once, from a lair's death script. `VIGIL`
does the opposite — it refreshes the camera target on **every** poll for
as long as the boss lives (`Vigil_victory`, the `else` of the win test):

```gpl
if ($listsize(guys) == 0)                       // "Abomination" gone
    begin
        $declarevictory(palace,AIRootAgent's "end_coord");
        ...
    end
else
    AIRootAgent's "end_coord" = $locationof($Listmember(guys,1));
```

So on the poll where the boss dies, `end_coord` still holds the position
it occupied one poll earlier — **the victory camera lands where the boss
was, with no death hook on it at all.** `URBAN_RENEWAL` and `VIGIL` both
also seed `AIRootAgent's "end_coord" = $locationof(Palace)` in their
entry functions (lines 550 and 823), which is the defensive habit worth
copying: `$declarevictory(palace, <coord>)` then always has a valid
target even if the tracking branch never ran.

#### (c) Shipped defects in this file — do not copy

Listed because §19.3's `=`-vs-`==` bug already showed these do compile
and ship.

- **Wrong target in the peasant-revolt loop.** `urban_crime_spot_destroyed`
  line 763: `$adjustattribute(thisagent,#ATTRIB_ActionRateModifier,-300)`
  sits inside `foreach thing in things`, where every other line in the
  loop adjusts `thing`. It hits the **dying building** instead of the
  peasant, once per peasant. Near-certainly meant to be `thing`.
- **Two authored events that were never written.**
  `urban_guild_destroyed`'s `num == 9` branch (lines 673-679) is an empty
  `begin`/`end` holding only the comment "event 1 - they are mad now!!!
  they should all be forced to attack a player building!!!", and
  `urban_crime_spot_destroyed`'s `num == 2` branch (769-773) is an empty
  body under "another event!!!". Same category as §9's Zoo: shipped
  scaffolding with no behavior. `corrupt_peasant_home` line 645 is a
  third, smaller instance — the function ends on the bare comment "force
  the peasant to be corrupt" with nothing implementing it.
- **A debug call left in shipped code.** `URBAN_RENEWAL` line 569:
  `$debugout(911,$listsize(guilds),$listsize(bldgs))`. Worth noting for
  the *form* as much as the sloppiness: **two integer arguments and no
  string label**, so `$DebugOut`'s argument list is variadic and untyped,
  not only the `(channel, "label", agent)` shape prior sections showed.
- **Redundant `evaluationScript` write** after `$make_raider` (20.3c).

**And one thing that looks like a defect but isn't:** both `IGDeathScript`
handlers count their own kind *from inside the dying building's own death
script* (`$listobjects(thisagent,"building",…,#MyPlayer,#CheckSubtypes,
"Guild")`, then branch on 9 / 6 / 3 out of a stated 11), so the dying
building is still in the count. That is the same off-by-design property
§19.3 documented for `LH_Barrows_Death` — **now confirmed independently
on buildings, not inferred from the lair case.**

### 21.3 Externally-scored graded victory — the delivery-game pattern

`TRADE_ROUTES` is the only quest in §16-§21 whose outcome is **not**
computed by any thread it owns, and the wiring is worth copying whole
because it is the generic answer to "score an activity the player
performs repeatedly."

**The scorer lives in this file but is called from two other files.**
Confirmed by grep, three call sites, all outside `Quests_3.gpl`:

| Event | Call site | Effect |
|---|---|---|
| Caravan reaches a Marketplace | `GPLMx/TaskModules/Characters/Henchmen/mx_caravan.gpl` lines 82-87 (`Caravan_Go_Trade`) | `Victory_Score += 1` then `$CheckTradeVictory()` |
| Caravan dies | `GPLMx/mx_Hero_Deaths.gpl` lines 437-443 (`Caravan_Death`) | `Defeat_Score += 1` then `$CheckTradeVictory()` |
| Either, in `SIEGE` | same two functions, lines 89-96 / 445-452 | the **inverted** pair (`Defeat_Score` on arrival, `Victory_Score` on death) plus `$CheckSiegeMessage()` |

Both hooks are guarded by `if (AIRootAgent's "Quest_Number" ==
#QNumber_Trade_Routes)` / `#QNumber_Siege`. **This is §19.1's
`Quest_Number` mechanism used in the most useful possible way: a stock
unit's task module contains a permanently-installed, quest-gated
scoring hook, and the quest supplies the handler.** A mod adding its own
delivery quest either reuses `#QNumber_Trade_Routes` or adds a third
branch to those two stock functions.

**The grading table** (`CheckTradeVictory`, lines 319-518). It fires on
every score change but only acts at five totals, and at each total it
compares the *success* count against thresholds:

| `total` (win+loss) | Bands (`victory >=`) | Consequence |
|---|---|---|
| 5 | 5 / 3 / 1 / else | message `#Trade_Victory_1A..1D` + arm a **Moderate / Moderate / Minor / Helpful** random event |
| 11 | 10 / 6 / 4 / else | `2A..2D` + Major / Moderate / Minor / Helpful |
| 17 | 15 / 9 / 5 / else | `3A..3D` + Major / Major / Minor / Helpful |
| 23 | 20 / 12 / 6 / else | `4A..4D` + Major / Moderate / Helpful / **`$Trade_Routes_Defeat`** |
| 29 | ==29 / 25 / 15 / 8 / else | `5E`/`5A`/`5B` = **victory**, `5C`/`5D` = **defeat** |

Four reusable findings:

1. **The reward for doing badly is a *helpful* random event.** The
   dispatcher tiers §17.2 documented as difficulty flavour are used here
   as **rubber-banding**: `Trade_Routes_Helpful_Event` for a failing
   player, `..._Major_Event` for a dominant one. Same four functions, and
   the choice of which to arm *is* the difficulty adjustment.
2. **The event is armed by writing the poll slot, not by calling the
   function.** `AIRootAgent's "VictoryCondition2" = $Trade_Routes_
   Moderate_Event; $NewThread(…, $RandomNumber(45000)+15000)` — so the
   consequence lands 15-60 s after the checkpoint, and each tier function
   opens with `$KillThread(AIRootAgent's "VictoryCondition2")` to
   one-shot itself. **A one-shot delayed consequence needs no
   `$RunThread`; `$NewThread` + self-`$KillThread` is the idiom used
   here** (contrast §19.5e's `$RunThread`).
3. **A script slot's current *function value* is used as a latch.**
   Lines 351-352, verbatim:
   ```gpl
   if (( AIRootAgent's "VictoryCondition2" == $Trade_Routes_Defeat )
    || ( AIRootAgent's "VictoryCondition2" == $Trade_Routes_Victory ))
       return;
   ```
   **Function values are comparable with `==`, and this file uses that to
   ask "has the endgame already been scheduled?" without spending a
   `Quest_Flag`.** New: §14/§17.5 established function values can be
   stored, passed (§20.6c) and indirectly called; comparing two of them
   is a fourth capability. Cheap and self-documenting — worth copying for
   any "don't re-decide" guard.
4. **Victory and defeat are both just functions on that slot**, armed
   with a 15 s delay so the final message is readable before the screen
   changes (`$PlaySound(Palace,"Victory_Theme","Begin")` fires
   immediately, the `$DeclareVictory` 15 s later). `Trade_Routes_Victory`
   (line 288) then kills all four threads — **except** the strangleweed
   pump, with the shipped comment "The strangleweed script is NOT halted,
   it continues, just for the hell of it," which is an independent
   confirmation of §19.5d (threads survive `$DeclareVictory`).

**One smaller find in the same quest: a building's title changes when it
closes, and a victory test has to allow for it.** `Check_Market_Defeat`
(lines 269-284) unions two title queries:

```gpl
b1 = $RemoveTitles ( buildings, "Marketplace" );
b2 = $ListTitles  ( buildings, "Closed" );
buildings = $AddLists ( b1, b2 );
if ( $ListSize ( buildings ) < 1 ) $Trade_Routes_Defeat ();
```

The reason is spelled out in `mx_caravan.gpl` line 16, whose `Caravan_
Start` tests `(Target's "title" == "Marketplace") || (Target's "title" ==
"Closed")` with the comment "NOTE: The Marketplace can be closed, we will
still go there anyhow. This is primarily a fix for the Trade Routes
quest." **So `"Closed"` is a real live title value a Marketplace takes
on, i.e. the §20.2/§20.4 `"type"`-register trick applied to `"title"` by
the stock building code** — and any quest that counts a building type by
title has the same false-negative waiting for it. (Which stock function
performs the retitle was not traced — see 21.10.)

### 21.5 Victory declared from a death script, and how to tear down a hostile palace

Three of this file's four quests skip the poll thread entirely (21.0).
Two different shapes, both new relative to §16.2/§19.5/§20.5:

**(a) Death-script victory with an inline census.** `Spire_Death`
(1131-1175) and `Fortress_Death` (2885-2912) both end in
`$DeclareVictory`. `Spire_Death` is the interesting one because the object
being counted is the one that just died:

```gpl
AIRootAgent's "end_coord" = $LocationOf ( thisagent );
$ListObjects ( palace, "Lair", -1, spires, #CheckTitles, "SpireOfDeath", … );
newspires = spires;
$Force_Spire_Spawns ();        // parting volley
$Set_Spire_Levels ();          // retier survivors
$Lair_Death ( thisagent );     // ← stock handler FIRST, then count
foreach spire in spires do
    if ( $IsDead ( spire )) newspires -= spire;
if ( $ListSize ( newspires ) < 1 )
    begin
        $KillThread ( AIRootAgent's "SpecialSpawnScript" );
        $KillThread ( AIRootAgent's "SpecialSpawnScript2" );
        $DeclareVictory ( palace, AIRootAgent's "end_coord" );
    end
```

**The `$IsDead`-filter-after-query is mandatory here and it is the
mechanism that makes the count come out right.** §19.3/§20.5c established
that a dying agent is still returned by `$ListObjects` from inside its own
death script; §19.3's barrows relied on that (branching on 5 meaning "the
first of six"), whereas this file *cancels* it by filtering `$IsDead`.
**Both readings of the same fact are now confirmed, and the choice is
yours: leave the dying unit in the count and offset your thresholds, or
filter `$IsDead` and count survivors.** Filtering is the clearer option,
and note it works because `$Lair_Death` has already run — so `$IsDead`
returns TRUE for the current agent by the time the loop reaches it.
`Set_Spire_Levels` does the same filter for the same reason, which is a
second independent instance inside this file.

**(b) A hostile palace is not a normal building — tearing one down takes
six calls.** `Siege_Palace_Death` (2236-2264) is installed as the enemy
palace's `IGDeathScript` at quest setup (line 1275) with the shipped
rationale "This is overwritten onto the evil palace at the start of the
mission, to allow the normal data structure for the palace to be reusable
later on." Read in full:

```gpl
AIRootAgent's "Permanent_Hostility" = FALSE;      // 1. end the forced war
AIRootAgent's "End_Coord" = $LocationOf ( thisagent );
thisagent's "type" = "Dead";                      // 2. §20.2's register
$Dump_Contained_Units ( ThisAgent );              // 3. evict occupants
$performaction ( thisagent, "Become_Rubble", thisagent );   // 4. visual
gold = $getplayerdata ( thisagent, "gold" );      // 5. loot the treasury
$adjustplayerdata ( thisagent, "gold", 0 - gold );
$dropgoldeveryone ( thisagent, gold );
$deleteagent ( thisagent );                       // 6. remove
$Siege_Victory ();
```

Five reusable facts:

- **`$Dump_Contained_Units (agent)`** — GPL, `GPLMx/mx_Building_Deaths.gpl`
  line 158, with the shipped comment that names exactly why it exists:
  "It is used by the palace, as since it doesn't have an Occupants list,
  it needs to get its container contents another way." **So
  `$release_occupants` (§20.6c) does not work on a palace** — the
  commented-out `$release_occupants` on the next line of this very
  function is the author discovering that. Use `$Dump_Contained_Units`
  for palaces, `$release_occupants` for guilds.
- **`$PerformAction (building, "Become_Rubble", building)`** — a named
  action that turns a building into rubble, usable as a death visual
  independent of the stock `$building_death` teardown.
- **`$DropGoldEveryone (agent, amount)`** — new to this guide; a
  third gold-scatter primitive alongside §19.7's
  `$DropGoldInRadius(agent, amount)` (which `Fortress_Death` uses at line
  2905). Name implies every player shares the drop, which suits a
  captured treasury; the split rule is engine-side and **UNVERIFIED**.
  Note the treasury is **zeroed first** with
  `$AdjustPlayerData(thisagent, "gold", 0 - gold)` — so `$GetPlayerData`
  /`$AdjustPlayerData` (§5/§17.2) accept **any agent of that player**, not
  only the palace, which is also how `Enemy_Guild_Spawn` bills a guild
  (`$AdjustPlayerData(Guild, "gold", -600)`, line 1495).
- **`$DeleteAgent` vs `$DeleteGamePiece`**: this uses `$DeleteAgent` on a
  building it has already rubble-ised, where §18's treasure-chest note
  found the stock `Treasure_Chest_Death`'s `$DeleteAgent` commented out.
  Both exist; no behavioural difference was established in this batch
  (**UNVERIFIED**).
- **Killing a unit by setting negative HP.** `SiegeOutOfMoney` (2267) is
  two lines: `$SetAttribute (enemy_palace, #ATTRIB_HP, -50)`. §18 noted
  HP-zero as "kill cleanly, running the death script"; **-50 is used here
  for the same purpose on a palace**, i.e. the AI's surrender is
  implemented by making its palace die so the normal
  `IGDeathScript`-to-victory path runs. One primitive, one code path, no
  duplicate victory logic — worth copying as a discipline.

### 22.5 Sequential message flags — `$IsMessageFlagPresent` + the `Message_Check_N` registers

§17 documented `$MessageFlag` as fire-and-forget. This file adds the
missing half: **a way to queue tutorial messages so the next one only
appears after the player has dismissed the previous one.**

The primitive is **`$IsMessageFlagPresent(#message_id) is boolean`** —
asks whether a specific message flag is still on the map. Combined with a
dedicated root-agent boolean register per step, it gives a chain:

```gpl
If (AIRootAgent's "Message_Check_1" == False)              // bbc_victory 247
    begin
        If ($IsMessageFlagPresent (#message_bbc_intro) == False)
            begin
                buildings = $listtitles (buildings, "blacksmith");
                If ($ListSize (buildings) > 0)
                    begin
                        bldg = $listmember (buildings, 1);
                        $messageflag (bldg, #message_bbc_blacksmith);
                    end
                AIRootAgent's "Message_Check_1" = True;
            end
    end
Else
    begin
        If (AIRootAgent's "Message_Check_2" == False)      // ... nested, not chained
```

Two shipped instances: `bbc_victory` (247-320, four steps: intro →
blacksmith → guardhouse → inn → trading post) and `forsaken_victory`
(2209-2245, two steps). Both are in the **victory poll**, not an events
thread — the messages ride the same 4-second tick as the win test.

Points worth keeping, all from the source:

- **`Message_Check_N` are their own root-agent registers**, declared
  immediately after the `Quest_Flag_N` block in **`GPL/prototype.gpl` 42+**
  (`Message_Check_1..3`+) and **`GPLMx/mx_prototype.gpl` 59+**
  (`Message_Check_1..5`), with the shipped comment *"Used to check whether
  to instantiate chained message flags in quests"* — so this is a named,
  intended subsystem, not an ad hoc use of spare booleans, and the
  expansion widened it. Using them keeps the quest-flag namespace free for
  gameplay state. Note **neither quest initialises them** — unlike §19.1's
  explicit `False` init discipline for `Quest_Flag_N`.
- **The structure is nested `Else` blocks, not a flat `else if` chain**,
  which means each tick can only advance the chain by one step. Deliberate
  and correct here, but it is the opposite shape from §19.3's sequencer.
- **Each step guards on `$ListSize(buildings) > 0` before flagging** and
  sets its `Message_Check` register **regardless** — so if the player has
  no blacksmith when the intro is dismissed, that message is skipped
  permanently rather than deferred. That's a real design consequence of
  where the `Message_Check` write sits, not a bug.
- **A shipped copy-paste defect worth not repeating:**
  `forsaken_victory`'s step 2 tests `$IsMessageFlagPresent
  (#message_bbc_blacksmith)` — a *Bell, Book and Candle* message, in the
  Forsaken Lands quest (line 2230). Since that message is never posted in
  this quest, the test is always false and the step fires on the first tick
  after step 1, defeating the sequencing. Confirmed present in mx too.

---

## Chapter 3: Spawning, Difficulty and Pacing

Event pools, spawn overrides, lair tuning, and difficulty that scales.

### 17.2 `Random_Events.gpl` — a pool with no scheduler in it

**The headline structural finding: `Random_Events.gpl` contains no
scheduler, no selection logic, and no timer.** It is 14 standalone
functions, each tagged with a `// RANDOM_EVENT` comment on the line after
its signature, and nothing else — no dispatcher, no table, no
registration call. The scheduler and the weighting live entirely in the
*consumer*. Grepped every `$FunctionName` call site of all 14: exactly
two consumers exist, and they use the pool completely differently.

| Consumer | File | Shape |
|---|---|---|
| Trade Routes quest | `GPLMx/Rules/Quests_3.gpl` lines 525-673 | 4 tier dispatchers, chosen by player performance |
| `Random_Disasters` special event | `GPLMx/Rules/Special_Events.gpl` lines 63-115 | 1 flat dispatcher, self-rescheduling (see 17.3) |

The `// RANDOM_EVENT` comment tag is documentation only — grepped, nothing
reads it, no tool consumes it. It's the authors' own index marker.

#### The scheduler: `$NewThread` + immediate self-`$KillThread` = one-shot

`Quests_3.gpl` schedules an event by writing the tier dispatcher into the
root agent's `"VictoryCondition2"` slot and arming a repeating thread with
a randomized delay:

```gpl
AIRootAgent's "VictoryCondition2" = $Trade_Routes_Major_Event;
$NewThread ( AIRootAgent's "VictoryCondition2", ( $RandomNumber ( 45000 ) + 15000 ));
```

…and the very first two statements of every one of the four dispatchers
are:

```gpl
AIRootAgent = $RetrieveAgent ( "GplAIRoot" );
$KillThread ( AIRootAgent's "VictoryCondition2" );
```

**That is the reusable "fire once after a random delay" idiom on top of a
repeating primitive:** `$NewThread` is a repeating timer (§14), so the
handler cancels its own slot before doing any work. Confirmed in all four
dispatchers (`Trade_Routes_Helpful_Event`, `_Minor_Event`,
`_Moderate_Event`, `_Major_Event`). Note this deliberately reuses the
same `"VictoryCondition2"` slot §16.2 documented for secondary victory
threads — one slot, rearmed for a different handler each time, which is
why the self-kill is mandatory rather than stylistic.

Delay range `$RandomNumber(45000) + 15000` = 15000-60000 ticks, i.e. a
quarter-day to one full day on the 60000-per-day convention §16.2
derived.

#### The selection: uniform, unweighted, and tiered by *outcome*, not chance

Inside a dispatcher, selection is the plain idiom:

```gpl
number = $RandomNumber ( 3 ) + 1;
$Debugout ( 911, "Doing Event Helpful: ", number );
if ( number == 1 ) … else if ( number == 2 ) … else if ( number == 3 ) …
```

**There is no weighting anywhere in this system.** No probability table,
no chance rolls, no `$RandomNumber(100) < weight` gate (contrast §14's
decision-tree `chance` idiom). Every event within a tier is equally
likely. All four dispatchers have a commented-out empty
`// else if ( number == 4 )` stub, so the intended extension mechanism is
literally "add a branch and bump the `$RandomNumber` bound" — and getting
that bound wrong is a silent no-op, because an unmatched `number` falls
off the end of the `if`/`else` chain with nothing happening.

**Difficulty comes from *which pool* is entered, not from weights.**
`Quests_3.gpl` calls the tier dispatchers from a progress check that
compares the player's accumulated `victory` score against thresholds at
each `total` milestone (17, 23, 29): doing well selects
`$Trade_Routes_Major_Event` (the nastiest pool), doing badly selects
`$Trade_Routes_Helpful_Event` (the beneficial pool). **This is a rubber-
band difficulty mechanism implemented entirely with function-pointer
assignment**, and it's directly reusable: define N pools, pick the pool
from game state, pick the member uniformly.

Tier composition (from the four dispatchers):

- **Helpful** (3): `Healing_Wind`, `Found_Gold`, `Wandering_Heroes`
- **Minor** (3): `Housing_Boom`, `Bandit_Event`, `Plague_Event`
- **Moderate** (4): `Krypta_Curse`, `Undead_Horde`, `Earthquake_Event`,
  `Magical_Accident`
- **Major** (4): `Goblin_Blockade`, `Dragon_Raid`, `Treasury_Looted`,
  `Gorgon_Raid`

Every branch pairs the effect with a player notification:
`$messageflag ( palace, #Message_<EventName> )`. Those constants are a
contiguous block in `GPLMx/mx_defines.gpl` lines 227-244 (237-254), one
per event — **so adding a new event to the pool needs a new
`#Message_*` expression, and per §16.1's finding about
`CanIBuildThisBuilding`'s return codes, the string a message index
renders lives exe/`.cam`-side. Whether a brand-new index above 254
renders any text at all is UNVERIFIED** — safest route for a new event is
to reuse an existing index or ship no message flag.

`Magical_Accident` is the one event that returns `boolean`, and the
`Moderate` dispatcher respects it:
`if ( $Magical_Accident ( palace )) $messageflag (...)`. **Reusable
convention for a conditional event: return a boolean for "I actually did
something," and let the caller decide whether to notify.**

#### Catalog: what the 14 events actually do

Enough detail to write a new one. `palace` is always the target player's
palace; events taking no argument fetch it themselves via
`$GetPlayerOnePalace()` (which is single-player-only by name — the
`agent palace` parameter form is the multiplayer-safe one, and
`Random_Disasters` in 17.3 exploits exactly that).

| Function | Args | Mechanism |
|---|---|---|
| `Goblin_Blockade` | — | Loops markers 1-4 via `$GetMarker(count)`; `spawnpoint = $ClosestMapEdge(marker)`; spawns 11 goblins per marker (4 fighter, 4 archer, 2 priest, 1 `GoblinOverlord`) as `#monster_player` with `$concatenate(#ATTRIB_Artifice, #force_caravan_raider)` |
| `Dragon_Raid` | — | 3 iterations; each picks a random marker `$RandomNumber(4)+1`, spawns one `"Dragon"` at `$ClosestMapEdge(marker)` with `#force_caravan_raider`. (Header comment says "a pair of dragons"; the loop is `count <= 3` — comment is wrong, code spawns 3) |
| `Gorgon_Raid` | — | 5 × `"GreaterGorgon"` at `$RandomEdgeCoord($RandomNumber(4))` with `#force_PC_Hunter` |
| `Treasury_Looted` | `palace` | `gold = $GetPlayerData(palace,"gold")`; `gold = (gold * .75)`; `$AdjustPlayerData(palace,"gold",-gold)`. String-keyed player-data API; note the float literal `.75` assigned into an `integer` |
| `Plague_Event` | `palace` | `$listobjects(palace,"hero",500,heroes,#NoHiddenMap,#InsideOtherUnits)` — radius 500, so "nearest heroes"; per hero, guards on `#ATTRIB_HasEffectRatmanPlague < 1` and `hero's "subtype" != "undead"`, then `$SetAttribute(hero,#ATTRIB_HasEffectRatmanPlague,#Ratman_Plague_Generations)` + `$Ratman_Plague_Begin(hero,hero)`. **Reuses the monster spell's own begin-function as a quest effect** — the generations count is what makes it contagious |
| `Undead_Horde` | — | Lists own-player buildings, `$ListTitles` for `"graveyard"` and `"mausoleum"`, `$AddLists` them; spawns 1 vampire + 3 zombies + 2 skeletons **from each** as `#monster_player` `"override"`, and `$minimapanimation(building,"Event_beacon")`. Fallback if none: spawn the same set at `$RandomCoord(palace,800,1000)` (min/max radius form). **Enemy units erupting out of the player's own buildings is just `$SpawnUnit(playerBuilding, ..., #monster_player)`** |
| `Earthquake_Event` | `palace` | Picks a uniformly random own building, `$CreateSpellUnit(building,"Earthquake",building)` + beacon. **`$CreateSpellUnit(caster, "<spell>", target)` is the generic "make a spell happen with no hero casting it" primitive** |
| `Krypta_Curse` | `palace` | The `Wither` debuff — already documented in §14.2 (`$MagicalAdjustAttribute` for `#ATTRIB_strength`, plain `$AdjustAttribute` for the two rate modifiers); structurally the standard 2-effector (visible + timer-icon) + `HasEffect*` flag pattern, applied to every own hero except `"Priestess"` |
| `Found_Gold` | — | `$AdjustPlayerData(palace,"gold", $RandomNumber(2000)+1000)` |
| `Wandering_Heroes` | — | 4 free heroes (Barbarian/Ranger/Warrior/Healer) at `$FarthestMapEdge_OnMap(palace)` + beacon. **No player-number argument, so they spawn on the palace's side** — contrast every hostile event, which passes `#monster_player` |
| `Healing_Wind` | — | Regeneration buff on all own heroes: `$ListObjects(..., #CheckSubTypes, "hero", #MyPlayer, #NoHiddenMap, #InsideOtherUnits)`, then the 2-effector pattern (`Regeneration_elixer_effector` duration 0 + `Regeneration_elixer_icon` duration 120000) + `$AdjustAttribute(hero,#ATTRIB_HealingRateModifier,-3)` + `$SetAttribute(hero,#ATTRIB_HasEffectRegeneration,1)`. **Negative delta improves the rate** |
| `Magical_Accident` | `palace`, returns `boolean` | See below — the borrowed-caster workaround |
| `Bandit_Event` | — | 4 × `"Rogue"` as `#monster_player` at `$FarthestMapEdge_OnMap(palace)`, each passed through `$Advance_to_Level(rogue,3)`. **`$SpawnUnit` returns the spawned agent**, which is what makes post-spawn levelling possible |
| `Housing_Boom` | — | 5 × `$spawnunit(palace,"general_housing",palace,"MaxHP")`. **Spawning a *building* rather than a unit, at another agent's position, pre-completed via the `"MaxHP"` string flag** |

**`Magical_Accident`'s borrowed-caster workaround is the single most
reusable trick in this file**, and the authors flagged it themselves:

```gpl
// The following bit is a workaround to provide the meteor storm with a 'monster player'
// source so it will hit player units.
$ListObjects ( palace, "lair",    -1, build1, #NotMyPlayer, #NoHiddenMap );
$ListObjects ( palace, "monster", -1, build2, #NotMyPlayer, #NoHiddenMap );
buildings = $AddLists ( build1, build2 );

if ( $listsize ( buildings ) > 0 )
    begin
        caster = $ListMember ( buildings, 1 );
        $CreateSpellUnit ( caster, "Meteor_Storm", lab );
        $player_spell_attack ( lab, 150, 75 );
        ...
        return TRUE;
    end
return FALSE;
```

Two distinct lessons:

1. **`$CreateSpellUnit` resolves friend-or-foe from its caster argument,
   so a spell meant to hurt the player needs a hostile agent as caster.**
   There is no "neutral/environment" caster; the code grabs *any* enemy
   lair or monster on the map purely to borrow its allegiance. **And it
   returns `FALSE` doing nothing when the map has no enemies at all** —
   that is the actual reason the function is boolean, and it's a real
   failure mode a modder will hit on a cleared map.
2. **The visual and the damage are separate calls.**
   `$CreateSpellUnit(caster,"Meteor_Storm",lab)` produces the spell;
   `$player_spell_attack(lab, 150, 75)` applies the damage.
   `player_spell_attack(agent target, integer damage, integer
   damage_minimum)` is GPL-defined in `GPL/TaskModules/Subtasks/
   make_attack.gpl` line 490 (identical in `mx_make_attack.gpl` line 534),
   commented "this is a player cast spell attacking, not from an agent,
   but from a mouse-click," and it does `$notvalid` guard →
   `$react_player_spell(target)` → `$spellhit(target)` → on hit,
   `$spelldamage($nullagent(), target, damage, damage_minimum)`.
   **`$spelldamage` with `$nullagent()` as attacker is how you deal
   damage with no attributable source** — the generic environmental-damage
   path, available in base game too.

The target selection also shows the `$RemoveTitles` multi-filter idiom
§16.1 documented: `build1/build2/build3 = $RemoveTitles(buildings,
"Wizards_Guild"/"SorcerersAbode"/"Magic_Bazaar")` then `$AddLists` of all
three, with `else lab = palace` as fallback. **Union-of-several-titles is
three `$RemoveTitles` plus one `$AddLists`; there is no multi-title filter
primitive.**

#### Defensive-coding warnings from this file (read before copying)

These are real defects in shipped code, cited so nobody copies them:

- **`Plague_Event` mishandles the empty list.** `victims = 5` is set
  *before* the query, and only overwritten `if ($ListSize(heroes) > 0)`.
  With zero heroes in range it still runs `while (count < 5)` calling
  `$Listmember(heroes, count)` on an empty list. Also `while (count <
  victims)` with `count` starting at 1 processes members 1..victims-1,
  never the last one. Initialize your bound *from* the list and use `<=`.
- **`Bandit_Event` relies on an uninitialized local.** `integer num;` is
  never assigned before `while ( num < 4 )`. It evidently defaults to 0,
  but that is an implicit-zero-init assumption, **UNVERIFIED** as a
  language guarantee — assign it.
- **`Krypta_Curse` computes `herocount = $ListSize(heroes)` and never
  uses it**; harmless, but a sign the guard you want may be missing.
- Several event functions declare `list palaces;` / `agent palace;`
  locals they never use (`Treasury_Looted`, `Plague_Event`,
  `Gorgon_Raid`). Copy-paste residue, not a mechanism.

### 17.3 `Special_Events.gpl` — a freestyle-selectable, self-scheduling plugin framework

915 lines, 18 functions: **15 event entry points, all with the identical
signature `Function <Name> (string AgentName)`,** plus three helpers
(`Mausoleum_Random_Hero_Type`, `on_perimeter`, `goblin_clump`). Unlike
17.2's pool, this file *is* the framework — each event owns its own
schedule.

#### The launcher: engine-selected, string-named, dynamically bound

`mx_Epic_Quest_Scripts.gpl`'s `function Freestyle()` lines 4066-4104 is
the only launch site (grepped `EventScript` across the whole tree). The
block runs twice, once per event slot:

```gpl
EventString = $GetSpecialEvent1Script();
If (EventString != "None")
    begin
        $CreateAgent ( "EventAgent", "EventAgent1" );
        EventAgent1 = $RetrieveAgent ("EventAgent1");
        EventAgent1's "EventScript" = $LookupFunction (EventString);

        //As a workaround, we are passing the stringname of the agent to this
        //Because an agent w/o a unit can't run threads...
        $NewThread( EventAgent1's "EventScript", #VictoryCondition_callback_frequency, "EventAgent1" );
        //run immediately the first time.
        (EventAgent1's "EventScript")("EventAgent1");
    end
```

Six separately reusable mechanisms in eleven lines:

1. **`$GetSpecialEvent1Script()` / `$GetSpecialEvent2Script()` are engine
   primitives that return a GPL *function name as a string*.** Confirmed
   as engine-native by their presence in the compiler keyword list
   (`SDK/Extras/GPL User Define[d] Language template for Notepad++.xml`,
   `Keywords4`, listed beside `$DisableUnitType`/`$EnableUnitType`) and by
   having no `function Get...` definition anywhere in the `.gpl` corpus.
   **They are the outbound half of the freestyle setup menu's two
   "special event" dropdowns** — same architecture as
   `$GetVictoryConditionIndex()` in §16.2, except this one hands over a
   **name**, not an anonymous index. **That is a strictly better hook for
   modders:** the engine doesn't need to know your function exists, only
   that its name is selectable. **Originally recorded here as UNVERIFIED
   ("presumed an exe/UI change") — now RESOLVED, and the answer is much
   better than that guess: the registry is plain CAM string data in
   `DataMX/mx_gpltext.cam`. See §17.7.**
2. **`"None"` is the sentinel for "no event selected"** — a plain string
   compare, no magic index.
3. **`$LookupFunction(string) → function` turns a name into a callable
   pointer.** This is the reflection primitive that makes data-driven
   dispatch possible in GPL, and it is in the base-game keyword list
   too. Anything you can name in a string you can call.
4. **`$CreateAgent("<PrototypeName>", "<InstanceName>")` instantiates a
   unit-less agent purely as a state container.** `Prototype EventAgent`
   (`GPLMx/mx_prototype.gpl` line 1117) declares exactly
   `function EventScript;` plus `boolean Event_Flag_1` … `Event_Flag_10`.
   **That is your per-event scratch memory: one function-pointer slot and
   ten booleans, and nothing more.** Two instances exist
   (`"EventAgent1"`, `"EventAgent2"`), each with an independent flag set —
   which is why two special events can run simultaneously without
   colliding.
5. **The `string AgentName` parameter is a documented engine workaround,
   not a style choice.** The authors' own comment: "an agent w/o a unit
   can't run threads." So the thread is armed with the agent *name* as its
   argument, and every handler's first statement is
   `ThisAgent = $RetrieveAgent ( AgentName );`. **If you write GPL that
   threads off a `$CreateAgent`'d container agent, pass its name as a
   string and re-retrieve it inside — do not pass the agent.**
6. **`(EventAgent1's "EventScript")("EventAgent1")` is an indirect call
   through an attribute-held function pointer.** Used here to run the
   handler once immediately in addition to arming the repeating thread.
   Same syntax §12 noted for `(spell's "castSpell")( palace )`, confirming
   it generalizes.

The repeating interval is armed as `#VictoryCondition_callback_frequency`
(4000, §16.2) — but **no special event actually runs at 4000**, because
the first thing each handler does is rewrite its own interval. That is
the framework's core idiom:

#### `$SetThreadInterval` on your own slot = a self-scheduling state machine

Every event reschedules itself:

```gpl
$SetThreadInterval ( ThisAgent's "EventScript", $Random_Time ( 180000 ));
```

`$random_time(integer time)` is GPL-defined — and notably it lives in
`GPL/TaskModules/Buildings/Sewer_Graveyard.gpl` line 129 (identical in
`mx_Sewer_Graveyard.gpl` line 146), an odd home for a general utility:

```gpl
new_time = time - (time / 4);            // 75% of time
random_time = $randomnumber((time / 4)); // + 0..25%
return new_time + random_time;           // → 75%..100% of time
```

**So `$random_time(t)` jitters *downward* from `t`, it does not center on
it.** This independently re-confirms §16.2's 60000-ticks-per-game-day
finding from a second file: `$random_time(180000)` is commented "2 to 3
days" (135000-180000 = 2.25-3.0 days) and `$random_time(600000)` is
commented "7 to 10 days" (450000-600000 = 7.5-10 days). Both check out
exactly. Two files, same constant, arrived at independently.

Three distinct lifecycle shapes appear, and picking one is the main design
decision when writing a new special event:

**(a) One-shot setup, then retire.** Do the work on the first tick and
`$KillThread(ThisAgent's "EventScript")`. Used by `Respawning_Lairs`,
`Dead_Heroes`, `Wake_the_Hunters`, `Veteran_Heroes`, `treasure`. Cleanest
shape; note these get run twice-ish safely only because the kill happens
in the same invocation as the work.

**(b) Staged cascade with per-stage delays.** The `Event_Flag_N` ladder
from 17.1's `vampiric_events`, but with each stage *also* setting the next
delay:

```gpl
if (thisagent's "event_flag_1" == false)
    begin
        // first time through: set up, choose next delay, don't act yet
        $setthreadInterval(thisagent's "eventScript",$random_time(600000));
        thisagent's "event_flag_1" = True;
    end
else
if (thisagent's "event_flag_2" == false)
    begin
        ... act ...
        $killthread(thisagent's "EventScript");
        thisagent's "event_flag_2" = true;
    end
```

Used by `Dark_magics`, `goblin_attack`, `super_lairs`,
`Abomination_appear_event`, `Ritual_of_pain`. **`goblin_attack` shows the
looping variant: its final stage resets `event_flag_2`/`event_flag_3` back
to `FALSE` instead of setting a terminal flag, so the wave sequence
restarts** — an escalating-then-repeating wave pattern from four `if`
branches and no counters. (Its `event_flag_4` branch never sets its own
flag and the commented-out lines show the authors going back and forth on
it; the effect is that stage 4 repeats until the reset takes effect on the
next pass. Copy the structure, but set your flags deliberately.)

**(c) Indefinite repetition with a skip-first-tick guard.** Because
`Freestyle()` invokes the handler immediately, an event that should not
fire at t=0 wraps its whole body in a "not the first time" check:

```gpl
if ( Thisagent's "event_flag_9" == TRUE ) // Dont run on the first iteration.
    begin ... end
Thisagent's "event_flag_9" = TRUE;
$SetThreadInterval ( ThisAgent's "EventScript", $Random_Time (180000) );
```

Used by `Friendly_Heroes` (via `Event_Flag_1`), `Random_Disasters`,
`Crunch_All_You_Want`, `The_Hunters`, `Evil_Everywhere` (all via
`event_flag_9`). **`event_flag_9` is a de facto convention for
"initialized" — the last-but-one of the ten prototype booleans, kept out
of the way of the `1..4` stage flags.** Worth following.

`Random_Disasters` computes its interval from player count:
`delay = ( 360000 / $listsize ( palaces ))` then
`$SetThreadInterval(..., $RandomNumber(delay) + (delay/6))`. **Scaling an
event's frequency by number of players is a one-line change; note the
resulting per-player rate is constant while the global rate is not.** (The
function sets the interval twice — once inside the guard and once
unconditionally after it, so the inner call is dead. Harmless
redundancy.)

#### Catalog: the 15 special events

| Function | Lifecycle | What it does (reusable mechanism) |
|---|---|---|
| `Respawning_Lairs` | (a) one-shot | Delegates entirely to `$Setup_Respawning_Lairs(Palace)` (`epic_quest_scripts.gpl` line 3070 / `mx_` line 3039), which rewrites every lair's `"IGDeathScript"` to a respawn handler. **A whole rules change delivered by one shared setup call** |
| `Friendly_Heroes` | (c) repeat | Per palace: `$SpawnUnit(Palace, $Random_Hero_Type(Palace), $RandomEdgeCoord($randomnumber(4)), $GetUnitPlayerNumber(Palace))`. **`$GetUnitPlayerNumber(agent)` is the multiplayer-correct way to spawn "on the same side as X"** instead of hardcoding a player constant; `Random_Hero_Type` is defined in `GPLMx/TaskModules/Buildings/Embassy.gpl` line 226 |
| `Random_Disasters` | (c) repeat | Picks a **random palace** (`$Randomnumber($Listsize(palaces))+1`), then a uniform 1-4 over `Plague_Event`/`Earthquake_Event`/`Krypta_Curse`/`Magical_Accident` from 17.2 — all four of the pool functions that take an `agent palace` parameter. **This is why those four are parameterized and the other ten aren't: parameterized events are multiplayer-reusable, `$GetPlayerOnePalace()` ones are not.** All `$messageflag` calls are commented out here, so the same effect ships silent in freestyle and announced in the Trade Routes quest |
| `Crunch_All_You_Want` | (c) repeat | Uniform 1-4 wave flavor (Goblin / Ratman / Animal / Undead), each spawning ~11-15 units **× number of palaces** (`wave = $listsize(palaces)`), all `#Monster_player` with `#force_bomber`. Reschedules `$RandomNumber(90000)+120000` |
| `The_Hunters` | (c) repeat | Same shape, harder rosters (IceDragon / Evil_Oculus / vampire / GreaterGorgon), all `#force_PC_Hunter`. Reschedules `$RandomNumber(90000)+180000` after an initial `+360000`. **The two wave events are the same 90-line skeleton with the roster and artifice swapped — the cleanest thing in this file to clone** |
| `Dead_Heroes` | (a) one-shot | Per palace, find or spawn a `"Mausoleum"`, then 5× `$SpawnUnit(Mausoleum, $Mausoleum_Random_Hero_Type(Mausoleum))` → `Hero's "Type" = "Dead"` → `$advance_to_level(Hero, $RandomNumber(5)+10)` → `$SetAttribute(Hero,#ATTRIB_HP,0)` → `$Check_Mausoleum(Hero)` (`GPLMx/TaskModules/Buildings/Mausoleum.gpl` line 28). **Creating a pre-dead, pre-levelled, already-interred hero is: spawn → retype to `"Dead"` → level → zero HP → run the interment check.** Also note `$ListObjects(...) > 0` used as an inline conditional — the primitive returns the count |
| `Dark_magics` | (b) staged | Stage 1 spawns `"witch_king"` at `$RandomCoord(Palace,-1)`; stage 2 spawns `"Liche_queen"` at `$on_perimeter()` then kills the thread. One-off boss flavor |
| `goblin_attack` | (b) staged, looping | Escalating waves of `$goblin_clump(palace)` (2 → 4 → 6), then resets its own flags to loop |
| `super_lairs` | (b) staged, repeating | After the initial delay, for every live lair on the map: `Random = $RandomNumber(3)+1` then `$spawn(Lair)` that many times, guarded by `$isdead(lair) == FALSE`. **`$spawn(agent)` triggers a lair's *own* spawn behavior — the way to boost existing spawners without knowing what they spawn.** Also the only place in this file using the `(Counter) ++` increment form |
| `treasure` | (a) one-shot | `$setup_random_treasure(20 * $listsize(palaces), 30)` then kill. Player-count-scaled loot |
| `Abomination_appear_event` | (b) staged | Delay ~10-15 days, spawn one `"abomination"` at `$on_perimeter()`, kill thread |
| `Ritual_of_pain` | (b) staged, repeating | Uniform `$randomnumber(3)`: **0** = union monsters+heroes via `$addlists`, then 3× `$lightning_bolt_hit(randomMember)` (defined `GPL/TaskModules/Subtasks/Spells.gpl` line 269, "player cast spell - from wizard's guild"); **1** = union buildings+lairs, `$createspellunit(palace,"earthquake",target)`; **2** = *deliberately nothing* ("they were lucky!"). **An explicit empty branch is how you get "sometimes nothing happens" without a probability gate** |
| `Wake_the_Hunters` | (a) one-shot | Picks two distinct random lairs (removing the first from the list before the second draw — `Lairs -= Lair`, the reusable draw-without-replacement idiom) and sets `Lair's "Special_Spawn_Type"` + `Lair's "Has_Special_Spawn" = True` on each |
| `Evil_Everywhere` | (c) repeat | **Guards on the global spawn cap:** `If ($ListObjects (Palace, "Monster", -1, Monsters, #NoHiddenMap) < #Monster_Spawn_Cap)` — 85, `globals.gpl` line 47 / `mx_Globals.gpl` line 49, identical in both. Then a uniform 1-5 monster-pair table, spawned with `#force_overlay` (which triggers the `troll_spawn` effector, see below) at `$RandomCoord(Palace,-1)`. **Any repeating spawner you write should copy this cap check** |
| `Veteran_Heroes` | (a) one-shot | Two lines of substance: `AIRootAgent's "Spawn_High_Level_Heroes" = TRUE;` then kill thread. **A whole game-wide rules modifier as one boolean on the root agent, read later by unrelated recruitment code** — the cheapest possible "global modifier" mechanism, and the pattern to copy for any new one |

#### `#ATTRIB_Artifice` + `#force_*`: spawn-time AI behavior override

This recurs in nearly every event in 17.2 and 17.3 and is the highest-
value reusable primitive in this batch after the launcher itself. Call
form:

```gpl
$SpawnUnit ( marker, "Goblin_Fighter", spawnpoint, #monster_player,
             $concatenate ( #ATTRIB_Artifice, #force_caravan_raider ));
```

The consumer is `check_override_behavior(agent thisagent)`, called from
`monster_birth()` (`GPL/Monster_Births.gpl` lines 7-25, `mx_` equivalent
`mx_Monster_Births.gpl` line 148) with the comment "this will possibly
override a monsters scripts if its artifice has been set by
`$spawnunit`". It reads `$getattribute(thisagent,#ATTRIB_artifice)` and
dispatches to a `$make_*` function:

| Constant | Value | Handler | Available in |
|---|---|---|---|
| `#force_raider` | 1 | `$make_raider` | base + mx |
| `#force_overlay` | 2 | *(no `$make_*`; consumed separately by `troll_birth`, which does `$createeffector(thisagent,"troll_spawn",1)`)* | base + mx |
| `#force_guardian` | 3 | `$make_guardian` | base + mx |
| `#force_bomber` | 4 | `$make_bomber` | base + mx |
| `#Force_PC_Hunter` | 5 | `$make_PC_hunter` | **mx only** |
| `#Force_Wandering` | 6 | `$make_wandering` | **mx only** |
| `#Force_Caravan_Raider` | 7 | `$make_caravan_raider` | **mx only** |
| `#Force_Elf_Hunter` | 8 | `$make_elf_hunter` | **mx only** |
| `#force_Warparty` | 9 | `$make_war_party(thisagent,6)` | **mx only** |
| `#force_Monster_Hunter` | 10 | `$make_monster_hunter` | **mx only** |

Values from `GPL/globals.gpl` lines 820-823 (four constants) and
`GPLMx/mx_Globals.gpl` lines 845-854 (all ten) — **so six of the ten
behavior overrides are expansion-only**, matching 17.0's finding. Base
`Monster_Births.gpl`'s `check_override_behavior` handles only 1/3/4 (and
notably its `#force_bomber` branch is `if` rather than `else if`, so it
can be reached after the raider branch — same latent quirk survives in the
mx version for `#force_warparty`/`#force_Monster_Hunter`).

**Reusable takeaway:** `#ATTRIB_Artifice` is a *repurposed stat slot* —
the same attribute is a genuine skill stat on heroes
(`Purchase_Equipment.gpl` line 313 scales search distance by it,
`Steal.gpl` line 16 rolls against it, `Gambling_Hall.gpl` line 46 reads
it) but is overloaded as a behavior-selector enum on quest-spawned
monsters. Adding an eleventh behavior means adding an `expression
#force_X 11` and one `else if` branch in `check_override_behavior` —
pure GPL, no exe change, no XML. **That makes it the cleanest extension
point found in this batch.** The one caveat: on monsters, the artifice
stat's normal meaning is destroyed by this overloading, so don't force a
behavior on a monster whose XML relies on Artifice.

### 17.7 The special-event registry is CAM data — the framework is fully mod-addressable

**Resolved after Batch B's main pass, by extracting `DataMX/mx_gpltext.cam`
with `cam_reader.py`.** The reason no `.gpl`/XML/`.mqxml` search found the
event names is that the registry lives in a **CAM `STRT` string table**,
the same container/section type the SMNU panel research already covers.

`mx_gpltext.cam`'s `STRT` section holds **three parallel tables**, all
keyed by the same 4-character ID (`NONE`, then `EV01`-`EV15`) — the STRT
format is `<4-char key><payload>` per string, so the key is a prefix, not
a separate field:

| Entry | Purpose | Example row |
|---|---|---|
| `ENTX` | dropdown **label** | `EV02` + `Reinforcements` |
| `EDTX` | dropdown **description** | `EV02` + `At random intervals, different heroes enter the realm from the map edges.` |
| `EVSC` | the **binding**: a number + the GPL function name | `EV02` + `39 ` + `Friendly_Heroes` |

Full confirmed `EVSC` table (number, then function name), which is
exactly what `$GetSpecialEvent1Script()`/`$GetSpecialEvent2Script()`
resolve against:

| ID | Number | GPL function | Label (`ENTX`) |
|---|---|---|---|
| `NONE` | 0 | `none` | None |
| `EV01` | 60 | `Respawning_Lairs` | Respawning Lairs |
| `EV02` | 39 | `Friendly_Heroes` | Reinforcements |
| `EV03` | 45 | `Random_Disasters` | Random Disasters |
| `EV04` | 60 | `Crunch_All_You_Want` | Cannon Fodder |
| `EV05` | 70 | `The_Hunters` | The Hunters |
| `EV06` | 39 | `Dead_Heroes` | Dead Heroes |
| `EV07` | 95 | `Dark_magics` | Dark Magics |
| `EV08` | 70 | `Goblin_attack` | Goblin attack! |
| `EV09` | 70 | `Super_lairs` | Super Lairs |
| `EV10` | 39 | `Treasure` | Treasure |
| `EV11` | 75 | `Ritual_of_pain` | Ritual of Pain |
| `EV12` | 85 | `Abomination_appear_event` | Abomination |
| `EV13` | 80 | `Wake_the_Hunters` | Wake the Hunters |
| `EV14` | 70 | `Evil_Everywhere` | Evil Everywhere |
| `EV15` | 20 | `Veteran_Heroes` | Veteran Heroes |

**Three findings fall out of this immediately:**

1. **Label and function name are independent, confirmed by real
   mismatches.** `EV02`'s function is `Friendly_Heroes` but its label is
   "Reinforcements"; `EV04`'s function is `Crunch_All_You_Want` but its
   label is "Cannon Fodder". So the UI text is not derived from the
   function name — it's a separate authored string, which is precisely
   what makes repointing safe.
2. **Case tolerance is real in shipped data.** `EVSC` says
   `Goblin_attack`, `Super_lairs`, `Treasure`; the actual GPL definitions
   are `goblin_attack`, `super_lairs`, `treasure` (lowercase). Since
   these ship working, **`$LookupFunction` resolves function names
   case-insensitively** — confirmed by shipped-data mismatch rather than
   by documentation.
3. **The number is UNVERIFIED.** Values are 20/39/45/60/70/75/80/85/95,
   correlating loosely with how punishing each event is (`Veteran_Heroes`
   = 20, the only purely-beneficial one; `Dark_magics` = 95, boss
   spawns). Plausibly a difficulty/score modifier — the same shape as the
   `$GetVictoryConditionModifier()` companion value in §16.2 — but
   nothing in GPL reads it (`Freestyle()` only consumes the function
   name), so its consumer is engine-side. **Do not assume it's cosmetic.**

**Confirmed expansion-only at the data layer too**, independently of
§17.0's four GPL-side confirmations: base `Data/gpltext.cam` has **no
`EVSC`, `ENTX`, or `EDTX` entry at all** (its entry-tag list was dumped
in full — it has `EN01`-`EN15`, unrelated). So the registry appeared
with the expansion alongside the framework.

#### Why this upgrades §17.3's verdict

§17.3 concluded a new special event needs an exe/UI change. **That is now
wrong, and the correction matters:** the registry is CAM `STRT` data, and
this project has already confirmed (see `SMNUResearch/FUTURE_TODO.md`,
"Quest CAM Override Capability") that **`STRT` entries override
correctly from a quest `<CAM>` tag, last-loaded wins** — verified by a
real modder changing panel text. `smnu_compiler.py` +
`cam_writer.build_cam_from_sections()` in this repo can already build a
`STRT`-bearing CAM from scratch.

So the practical recipe for a **genuinely new special event, quest-
distributable, no exe patch**:

1. Write your event function with the framework signature
   `Function My_Event (string AgentName)`, following one of §17.3's three
   lifecycle shapes, and compile it into your mod's bytecode.
2. Override `mx_gpltext.cam`'s `EVSC` entry via your quest CAM, changing
   one row's function name to `My_Event` (keeping its `EVxx` key and
   number).
3. Override `ENTX`/`EDTX` for the same key so the dropdown label and
   description describe your event.

This repoints an existing row rather than adding a 16th. **Whether the
dropdown's row *count* is data-driven (i.e. whether adding an `EV16` row
to all three tables makes a 16th selectable entry appear) is
UNVERIFIED** — the engine may read a fixed count, or may enumerate the
table. That single question is now the only thing standing between this
framework and being a fully open-ended mod entry point, and it is
answerable by an in-game test rather than Ghidra: add an `EV16` row and
see whether it appears. Recorded as a game-test item.

**Method note:** extracted via `cam_reader.py` through
`utility/test_decoder.py` (this project's one trusted scratch script).
The `STRT` payload is a standard header + u32 offset table + NUL-
terminated strings, matching `SMNUResearch/findings`' documented STRT
format — so the existing STRT tooling reads and writes these tables
already, no new parser needed.

### 19.6 `#force_*` closed: the artifice table is pure GPL, and this file supplies two of its behaviors

§17 documented the *caller* side of `#ATTRIB_Artifice` + `#force_*`
(spawn-time AI override, dispatched by `check_override_behavior` during
`monster_birth`). This batch closes the loop, because **`Quests_1.gpl` is
where two of the behavior functions themselves live** — and following the
wiring end to end changes the practical verdict from "pick one of the
shipped behaviors" to "add your own."

**The full dispatch table**, read directly from
`GPLMx/mx_Monster_Births.gpl` lines 148-207 (`check_override_behavior`),
paired with `mx_Globals.gpl` lines 846-855:

| Constant | Value | Dispatches to | Installs (behavior fn) |
|---|---|---|---|
| `#force_raider` | 1 | `$make_raider` | — |
| `#force_overlay` | 2 | **nothing** | see below |
| `#force_guardian` | 3 | `$make_guardian` | — |
| `#force_bomber` | 4 | `$make_bomber` | — |
| `#Force_PC_Hunter` | 5 | `$make_PC_hunter` | `$PC_Hunter` + `$PC_Hunter_eval_enemies` |
| `#Force_Wandering` | 6 | `$make_wandering` | `$Wandering` + `$monster_eval_enemies` |
| `#Force_Caravan_Raider` | 7 | `$make_caravan_raider` | — |
| `#Force_Elf_Hunter` | 8 | `$make_elf_hunter` | **`$Elf_Hunter`** (this file, line 1332) + `$monster_eval_enemies` |
| `#force_warparty` | 9 | `$make_war_party(thisagent, 6)` | — (takes a second arg) |
| `#force_Monster_Hunter` | 10 | `$make_monster_hunter` | **`$Monster_Hunter`** (this file, line 2220) + `$PC_Hunter_eval_hostiles` |

**Four findings, each independently checked:**

**1. The `#force_*` → behavior mapping is ordinary, editable GPL — not an
engine table.** `check_override_behavior` is a plain GPL function in
`mx_Monster_Births.gpl` (base twin at `GPL/Monster_Births.gpl` line 28),
called from `monster_birth` line 33 with the shipped comment "this will
possibly override a monsters scripts if its artifice has been set by
`$spawnunit`". A mod that ships its own `Monster_Births` equivalent can
**add an eleventh `#force_*` value and its own behavior function with no
exe, XML, `.dat` or CAM change.** That is a materially bigger capability
than §17's framing implied, and it is confirmed by the shipped example:
`GPL/../SDK/Example/GPL/WrathOfKrolm.gpl` line 846 calls
`$check_override_behavior(thisagent)` from its own birth function, i.e.
the SDK's own sample mod already re-implements the caller.

**2. The installer functions are a three-line idiom, and the idiom is the
transferable part.** All of them, read verbatim
(`mx_Monster_Births.gpl` lines 824-880):

```gpl
function make_Elf_Hunter (agent ThisAgent)
Begin
    thisagent's "activeScript"     = $Elf_Hunter;
    thisagent's "basicScript"      = $Elf_Hunter;
    thisagent's "backscript"       = $Elf_Hunter;
    ThisAgent's "EvaluationScript" = $monster_eval_enemies;
    thisagent's "relentless"       = TRUE;
End
```

This is §18.2's swap idiom minus the stash step (a newborn monster has no
prior behavior worth saving) plus two extras worth naming:

- **`EvaluationScript` is chosen independently of the three behavior
  slots**, and the choice is meaningful: `$monster_eval_enemies` for the
  building-hunters, `$PC_Hunter_eval_enemies` for hero-hunters,
  `$PC_Hunter_eval_hostiles` for the monster-hunter. **So "what do I
  attack when something walks past me" is a separate, swappable decision
  from "what am I trying to do."**
- **`thisagent's "relentless" = TRUE`** — declared
  `boolean Relentless; // will the monster relentlessly pursue its
  target (ignore range cheking)` in `mx_prototype.gpl` line 225 (sic,
  typo shipped). Three of the four installers set it. `Quests_1.gpl` also
  sets it by hand on individually-scripted attackers
  (`Legendary_Heroes_Victory` lines 168-224: `SpawnAgent's "Relentless" =
  True` next to `SpawnAgent's "Target" = Hero` and `"ActiveScript" =
  $Monster_Attack_Object`). **That trio — `Target` + `Relentless` +
  `$Monster_Attack_Object` — is the minimum "this monster will chase that
  specific unit until one of them dies" recipe, and it needs no artifice
  value at all.**

**3. `#force_overlay` (2) is NOT a behavior override, and passing it is a
no-op for almost every unit.** `check_override_behavior` has no branch for
it. The only readers anywhere in the tree are `troll_birth`
(`mx_Monster_Births.gpl` line 239; base `Monster_Births.gpl` line 82),
which do:

```gpl
if ($getattribute(thisagent,#ATTRIB_artifice) == #force_overlay)
    $createeffector(thisagent,"troll_spawn",1);
```

i.e. `#force_overlay` means "**play the spawn-in visual effector**," a
purely cosmetic flag on an orthogonal axis to behavior. And
`Troll_Birth` is bound to exactly **one** unit type — grepped both
`Monster_Data.dat` (line 510) and `mx_Monster_Data.dat` (line 867), one
hit each, both the Troll. So of the nine `#force_overlay` spawns in
`LH_Barrows_Death` (lines 478-582), **the four Trolls get a spawn puff and
the five Minotaurs/GreaterGorgons get nothing at all.** Shipped code
passing a flag its target cannot read; harmless, but do not copy it as if
it did something.

**4. One structural quirk in the dispatcher.** The `else`-chain breaks
after `#Force_Elf_Hunter`: `#force_warparty` and `#force_Monster_Hunter`
are bare `if`s, not `else if` (lines 198 and 202). Harmless with distinct
integer values, but it means those two branches are evaluated on every
birth regardless of earlier matches — and if a modder adds an eleventh
value they should extend the `else` chain properly rather than copy the
tail.

#### The behavior-function template (`Elf_Hunter`, `Monster_Hunter`)

Both new behaviors in this file are the same two-state machine, and it is
the generic "custom monster AI" template. `Monster_Hunter` (lines
2220-2232, the short one) shows the skeleton:

```gpl
$ListObjects (ThisAgent, "Monster", -1, Monsters, #NotMyTeam);
If ($ListSize (Monsters) > 0)
    begin
        ThisAgent's "Target" = $ListMember (Monsters, 1);
        $performaction (thisagent, thisAgent's "Idle_action", ThisAgent's "Target");
        thisagent's "activescript" = $monster_attack_Object;   // hand off
    end
Else
    begin
        If ($IsMoving (ThisAgent) == FALSE)
            $Move (ThisAgent, $RandomCoord (ThisAgent, $getattribute (ThisAgent, #ATTRIB_SightRange)));
        Else
            if ($monster_cast_travel (thisagent) == FALSE)
                $monster_eval_enemies (thisagent);
    end
```

Three points: **`#NotMyTeam` is the filter that makes monster-vs-monster
work** (compare `#MyPlayer`/`#NotMyTeam` in §17's `$ListObjects` option
grammar) — no separate hostility system is involved; **the behavior hands
off to the stock `$monster_attack_Object` rather than implementing combat**;
and **the idle branch is the standard wander-and-look-around pair**
(`$RandomCoord` within sight range, then `$monster_cast_travel` /
`$monster_eval_enemies`), which is what keeps the unit responsive to
opportunistic targets while it searches.

`Elf_Hunter` (lines 1332-1462) is the longer, target-priority variant and
adds three reusable pieces:

- **Priority targeting by list concatenation.** It builds a preferred
  sub-list and puts it first, then always takes member 1:
  ```gpl
  Bungs     = $RemoveTitles (Buildings, "Elven_Bungalow");   // strips matches out
  Non_Bungs = Buildings;                                     // …so this is the remainder
  Targets   = $Addlists (Bungs, non_Bungs);
  ThisAgent's "Target" = $ListMember (Targets, 1);
  ```
  **This confirms the first half of §14's `$RemoveTitles` finding and
  contradicts the second half.** §14 concluded (correctly) that
  `$RemoveTitles(list,"X")` *returns the matching members*, but then said
  "it is `$ListTitles` that additionally strips the matches out of the
  source list." **Two call sites in this file show the stripping is
  `$RemoveTitles`' own side effect, not `$ListTitles`':** the
  `Non_Bungs = Buildings` line above is only correct if the bungalows are
  already gone from `Buildings` (otherwise the priority scheme is a no-op
  and every bungalow appears twice), and `Clash_Empires_Victory` line 1592
  calls `$RemoveTitles (Lairs, "Goblin_Watchtower");` **discarding the
  return value entirely** — comment "Towers don't spawn anything, so
  remove them", immediately followed by `Gob_Lairs = Lairs`. A call whose
  result is thrown away is only meaningful if it mutates its argument.
  Correction recorded here rather than by editing §14 (out of this
  batch's scope); flagged for a maintainer to fold in. Both halves agree
  on the practical rule: **`$RemoveTitles` returns the matches AND
  removes them, so one list can be partitioned by successive calls.**
  **Reusable takeaway: `$Addlists(preferred, rest)` + always taking member
  1 is how this codebase does target priority — there is no sort.**
- **Weapon-vs-spell selection before range checking.**
  `spell_name = $getbestspell (thisagent, #list_attack)`; the sentinel for
  "no spell" is the **string** `"nothing"`, and the range to compare
  against switches accordingly (`#ATTRIB_maxattackrange` for melee,
  `thisagent's "castingrange"` for casting).
- **A collateral-damage guard.** `if ($peasants_near (thisagent) == FALSE)`
  wraps the whole attack, so the raider will not swing while peasants are
  adjacent. Plus a 995/1000 roll choosing `Attack_Action` over
  `Idle_action` — a 0.5% flavor twitch, not a mechanic.

### 19.7 Lairs as quest content: the writable field set, and §17's open question resolved

The most modder-useful cluster in this batch. All four quests treat lairs
as their primary quest object, and between them they write six different
lair fields. Every one is a plain GPL-declared `prototype` field, read
directly from `GPLMx/mx_prototype.gpl` with the shipped comments verbatim:

| Field | Declared (mx_prototype.gpl) | Shipped comment | Written by |
|---|---|---|---|
| `Spawn_Type` | 344 / 398 | "Holds the type of monster the lair spawns" | read (not written) in this file — `$SpawnUnit (Lair, Lair's "Spawn_Type")` |
| `Special_Spawn_Type` | 344 / 398 | "Holds the 'special' monster to spawn when the Lair is destroyed" | `DARKNESS_FALLS` 1936, 1940 |
| `Has_Special_Spawn` | 353 / 402 | "This is set to TRUE if the lair wants to spawn its special spawn type instead of its lairdata special spawn list" | `DARKNESS_FALLS` 1937, 1941 |
| `Max_Simul_Spawns` | 349 / 405 | "Currently Used by the Goblin Fortress. Max number of Gobs it spawns at a time." | `CLASH_EMPIRES` 1508 |
| `Max_Stored_Spawns` | 350 / 406 | "Max number of spawns that the unit can store up … To dump on enemies that come up and whack it" | `CLASH_EMPIRES` 1509 |
| `History_Modifier` | 325 / 376 | "A counter that is incremented depending on a monster's strength. Used to adjust spawn_rate." | `Snake_Pit_Spawn` 1262 |
| `IGDeathScript` | (§2/§17) | — | `LEGENDARY_HEROES` 62-89, six times |

(Two line numbers per field because `mx_prototype.gpl` declares `lair` and
a second near-identical lair-ish prototype; the comments differ only in
naming the Goblin Fortress vs. the Spire as the example user.)

#### RESOLVED: what `Special_Spawn_Type` and `Has_Special_Spawn` each do

§17 flagged this as **UNVERIFIED** ("which behavior each field controls
independently — a 'guaranteed once' boss spawn vs. a substituted normal
spawn type"), because `Demo` set only the type while `Wake_the_Hunters`
set both. **This batch resolves it from the reader**, `lair_death` in
`GPLMx/mx_Building_Deaths.gpl` lines 264-298, read in full:

```gpl
$killthread (thisagent's "Spawn_function");

//SpecialLairList data only if ThisAgent's "Has_Special_Spawn" == False
If (ThisAgent's "Has_Special_Spawn" == False
    && $FillSpecialLairList (ThisAgent, Monsters) > 0)
    begin
        Foreach Monster in Monsters do
            $SpawnUnit (ThisAgent, Monster, $LocationOf (ThisAgent), "Override");
    end
Else If (ThisAgent's "Special_Spawn_Type" != "xx")
    $SpawnUnit (ThisAgent, ThisAgent's "Special_Spawn_Type", $LocationOf (ThisAgent), "Override");

$dropgoldinradius (thisagent, $getattribute (thisagent, #ATTRIB_gold));
$chance_drop_equip (thisagent);
$Drop_QItems (ThisAgent);
$building_death (thisagent);
```

So, precisely:

- **`Special_Spawn_Type` is the payload; `Has_Special_Spawn` is a
  priority override.** The two are not alternatives — the flag decides
  *which source wins* when a lair has both a data-driven special list and
  a GPL-set type.
- **The data-driven list comes from `$FillSpecialLairList(lair, outList)`**,
  which returns a count and fills a list. That is the lair's own
  `.dat`/lair-data content.
- **`"xx"` is the sentinel for "no special spawn set."** So a modder
  setting `Special_Spawn_Type` alone gets a boss *only if* the lair has no
  data-driven special list (or the list comes back empty); setting
  `Has_Special_Spawn = True` too forces the GPL value to win
  unconditionally. **§17's `Demo` (type only) and `Wake_the_Hunters` (both)
  are therefore not inconsistent — they're the two different intents.**
  `DARKNESS_FALLS` needs the forcing form because `"WightsTomb"` does have
  lair data (the same `$RemoveTitles` scan shows more than two tombs
  exist, and the code comment says so: "Remember that there are more than
  2 WightsTombs").
- **Bonus, same read:** stock `lair_death` also kills the lair's
  `"Spawn_function"` thread, drops gold by
  `#ATTRIB_gold` radius-scatter, rolls equipment via
  `$chance_drop_equip`, and calls **`$Drop_QItems (ThisAgent)`**. That last
  one is what makes 19.7's quest-item seeding work, below.

#### Quest items live *inside* lairs, and drop when the lair dies

`LEGENDARY_HEROES` lines 58-89 seed six unique artifacts across six
randomly chosen barrows, with a draw-without-replacement loop:

```gpl
Lair = $ListMember (Barrows, $RandomNumber ($ListSize (Barrows)) + 1);
$CreateNewInventoryItem (#QItem_LH_Wand_Immolation, Lair);
Lair's "IGDeathScript" = $LH_Barrows_Death;
Barrows -= Lair;                                  // §17's draw-without-replacement idiom
```

Three reusable facts: **`$CreateNewInventoryItem` accepts a *building*
as its holder**, not just a hero (§3 only ever showed the hero-purchase
form), so "the artifact is in that dungeon" needs no container object and
no map editing; **the retrieval path is entirely stock** — `$Drop_QItems`
inside `lair_death` puts it on the ground when the lair dies, and §18's
`Inventory.gpl` machinery takes over when a hero picks it up; and **the
same loop installs the death script**, so seeding the item and hooking the
escalation are one operation per lair.

#### The lair spawn-function template

`Snake_Pit_Spawn` (lines 1250-1290) is a complete, clonable example of a
lair's repeating `Spawn_function`. Read in full it is five steps:

```gpl
$AutoSpawn_Lair (ThisAgent);                                          // 1
ThisAgent's "History_Modifier" += $GetAttribute (ThisAgent, #ATTRIB_Lair_History_Mod);   // 2
$adjustattribute (thisagent, #ATTRIB_gold, $randomnumber (#lair_gold_regen) + 1);        // 3
$ListObjects (ThisAgent, "Monster", -1, Monsters);
If ($ListSize (Monsters) <= #Monster_Spawn_Cap)                       // 4
    begin
        Spawn_Num = $RandomNumber (2) + 1;
        While (Counter < Spawn_Num) do
            begin
                If ($RandomNumber (100 + 1) > 80) $SpawnUnit (ThisAgent, "GreaterGorgon");
                Else                              $SpawnUnit (ThisAgent, "Medusa");
                counter++;
            end
    end
```

1. **`$AutoSpawn_Lair` is how lairs multiply**, and it's a GPL function
   (`GPLMx/TaskModules/Buildings/Autospawn_Lair.gpl` line 9), so its rules
   are editable: `Chance = 20.0 / (count_of_same_title_lairs + 1)`, rolled
   against `$RandomNumber(100)+1`, then `$SpawnUnit(ThisAgent,
   ThisAgent's "Title", $RandomCoord(ThisAgent,
   #Autospawn_Lair_Min_Dist, #Autospawn_Lair_Max_Dist), "MaxHP")`. **A
   lair spawns a copy of itself, so the spread is self-limiting** —
   20% with one lair, 10% with two, and so on. Note two shipped defects
   worth not copying: the declared `Lairs2` list is **never populated**,
   so the guarding `If ($ListSize (Lairs2) == 0)` is always true and the
   commented-out proximity check above it was evidently meant to fill it;
   and `20.0 / …` is a float expression assigned to an `integer` (the
   same float-into-integer looseness §17.2 noted for `Treasury_Looted`).
2. **`History_Modifier` accumulates `#ATTRIB_Lair_History_Mod` per
   spawn** — the prototype comment says it exists to "adjust spawn_rate,"
   so a lair that has been productive gets harder over time. Read/written
   only in GPL, so fully moddable.
3. **`#lair_gold_regen` = 5** (`mx_Globals.gpl` line 240, comment "max
   amount of gold a lair 'regenerates' (gains) each time it spawns a
   monster") — this is where the loot a hero gets for clearing a lair
   actually comes from, accumulated one spawn at a time.
4. **`#Monster_Spawn_Cap` = 85** (`mx_Globals.gpl` line 49, comment
   "General spawn cap for monsters (they won't spawn if this many monsters
   are already on the map) Overriden in some special cases in EQuests").
   **Every custom lair spawn function must check this itself** — it is a
   GPL convention, not an engine limit, so a modder who omits the check
   gets no cap.

#### Retuning a stock lair without touching its data

`CLASH_EMPIRES` lines 1495-1512 walk every lair once at quest start and
retune the Goblin Fortress in place:

```gpl
If (Lair's "Title" == "GoblinFortress")
    begin
        Lair's "Max_Simul_Spawns" = 1;      // fewer at once
        Lair's "Max_Stored_Spawns" = 8;     // but a bigger ambush reserve
    end
```

**That is the whole mechanism for "this quest's version of unit X behaves
differently": iterate `$ListObjects(..., "Lair", ...)` in the entry
function and assign fields by `"Title"`.** No XML, no `.dat`, no CAM, and
it cannot break other quests because it happens at runtime. The same loop
in the same function does the team-splitting of 19.8 — one pass, two
unrelated jobs, which is the idiomatic shape for quest setup.

### 19.9 Spawning an elite NPC army — the full stat-stack recipe

`Spawn_Gnomes` (lines 1210-1268), `Spawn_Elves` (lines 1272-1345) and
`Spawn_Dwarves` (lines 1349-1400) are three variations on "drop a
pre-levelled friendly army on the map," and between them they show every
knob available on a freshly spawned unit. §17 established that
`$SpawnUnit` returns the agent and that `$Advance_to_Level` can then be
applied; this is the complete list of what else can follow.

```gpl
SpawnUnit = $SpawnUnit (ThisAgent, "Elf", $RandomEdgeCoord ($RandomNumber (4)));
$Advance_To_Level (SpawnUnit, $RandomNumber (5) + 20);        // level band 20-24
$LearnSpell (SpawnUnit, "Fire_Balm", FALSE);                 // note 3rd arg
$Winged_Feet_Begin (SpawnUnit);                              // pre-applied buff
$LearnSpell (SpawnUnit, "regeneration_elixer", FALSE);
$LearnSpell (SpawnUnit, "teleport_short_amulet", FALSE);
$AdjustAttribute (SpawnUnit, #ATTRIB_NumHealingPotions, 10); // starting consumables
$SetAttribute (SpawnUnit, #ATTRIB_Armor_Struct_Bonus, 2);    // gear tier
$SetAttribute (SpawnUnit, #ATTRIB_Weapon_Struct_Bonus, 2);
$MessageFlag (SpawnUnit, #Message_VSerpents_Elven_Army_Arrive);
```

| Knob | Form used here | Note |
|---|---|---|
| Level | `$Advance_To_Level (agent, $RandomNumber (5) + N)` | A *band*, not a fixed level — 8-12 for gnomes/dwarves, 20-24 for the endgame elves |
| Spells | `$LearnSpell (agent, "name", FALSE)` | **The three-arg form is new here.** §3 only showed two-arg `$LearnSpell`. The `FALSE` is UNVERIFIED in meaning; from context (items/potions being granted silently to an NPC) the likeliest reading is "don't charge / don't announce," but nothing in source states it |
| Gear | `$SetAttribute (…, #ATTRIB_Armor_Struct_Bonus, 2)` and `_Weapon_` | Same attributes §3 identified as the *purchased* equipment upgrade tier — so "well-equipped NPC" and "hero who bought upgrades" are literally the same field |
| Consumables | `$AdjustAttribute (…, #ATTRIB_NumHealingPotions, 10)` | `Adjust`, not `Set`, so it stacks on the type's default |
| Pre-applied buff | `$Winged_Feet_Begin (SpawnUnit)` | **Calling a spell's own `_Begin` function directly to pre-buff a spawn** — same trick §17.2's `Plague_Event` used offensively with `$Ratman_Plague_Begin`; here it's benign and permanent-ish |
| AI aggression | `SpawnUnit's "Self_Estimation" = 3.0;` `SpawnUnit's "Enemy_Estimation" = .5;` | See below |
| Announce | `$MessageFlag (SpawnUnit, #Message_…)` | On the **spawned agent**, so the player's message links to the arriving unit rather than the palace — and only on *one* of the group (gnomes: the fifth; dwarves: the two Dauros ones), so five units produce one message |

**`Self_Estimation` / `Enemy_Estimation` are the courage dials, and they
are floats.** Declared in `mx_prototype.gpl` lines 110-111 as
`float Enemy_estimation; float self_estimation;` immediately after
`integer percentageHPretreat`. Setting `3.0` / `.5` makes a unit rate
itself triple and its enemies half, i.e. **suicidally brave** — which is
what `Spawn_Gnomes` wants from an allied army that should charge rather
than garrison. Note `.5` written without a leading zero, which the
compiler accepted. No reader was traced in this batch, so *how* the
retreat logic consumes them is **UNVERIFIED** (the adjacent
`percentageHPretreat` field suggests the flee threshold).

**Making a spawned unit into a spellcaster takes four coordinated
writes**, from `Spawn_Gnomes`' "This one is an MU!" gnome (lines 1252-1266):

```gpl
SpawnUnit's "Attack_Action" = "Do_Nothing";                   // 1. no melee swing
SpawnUnit's "CastingRange"  = 200;                            // 2. GPL-side range
$SetAttribute (SpawnUnit, #ATTRIB_MaxAttackRange, 200);       // 3. engine-side range
$LearnSpell (SpawnUnit, "Fire_blast");   // 4. …and five more
```

**Both ranges must be set** — `"castingrange"` is the prototype field the
GPL behavior functions compare against (19.6's `Elf_Hunter` reads exactly
that field when it has a spell), while `#ATTRIB_MaxAttackRange` is the
engine attribute used when it doesn't. Setting only one produces a unit
that walks into melee to cast, or refuses to close. And
`Attack_Action = "Do_Nothing"` is how you disable the physical attack
without touching the unit type — `"Do_Nothing"` as a valid action name is
worth remembering.

### 21.4 The self-retiering lair — difficulty that scales with progress AND with the player's army

`SPIRES_DEATH` is the most transferable single system in this batch:
**five identical lairs that get harder as you destroy them, and harder
again if you over-invest in heroes.** §19.3's `LH_Barrows_Death` was the
first instance of count-based escalation; this is the same idea built
properly, as data on the agent rather than a staircase of `if`s, and it
adds a second input.

`Set_Spire_Levels` (lines 976-1074), read in full, is four steps:

```gpl
$ListObjects ( palace, "Lair", -1, spires, #CheckTitles, "SpireOfDeath",
               #NotMyPlayer, #NoHiddenMap );
newspires = spires;
foreach spire in spires do                      // 1. drop the dead ones
    if ( $IsDead ( spire )) newspires -= spire;
count = $ListSize ( newspires );

$ListObjects ( palace, "hero", -1, tempheroes, #MyPlayer, #InsideOtherUnits );
foreach hero in tempheroes do                   // 2. sum the player's levels
    if ( hero's "Subtype" == "hero" )
        total_level += $GetAttribute ( hero, #ATTRIB_ExperienceLevel );

if (( count == 5 ) || ( count == 4 ))           // 3. compensate
    begin
        if (( total_level > 40 ) && ( total_level < 70 )) count -= 1;
        else if ( total_level >= 70 )                     count -= 2;
    end
else if (( count == 3 ) || ( count == 2 ))
    if ( total_level >= 70 ) count -= 1;
if ( count < 1 ) count = 1;

if ( count == 5 ) begin spawn = $Spire_Spawn_One;  gun = "Spire_Blast_One"; end
… else if ( count == 1 ) begin spawn = $Spire_Spawn_Five; gun = "Spire_Blast_Five"; end

foreach spire in newspires do                   // 4. write the tier onto each lair
    begin
        spire's "Attack_Action"  = gun;
        spire's "Spawn_Function" = spawn;
        $SetEffectorDirection ( spire, "Spire_Lights_Effector", ( count - 1 ));
    end
```

Six findings, each independently checked:

**(a) The tier is *inverted* count: 5 spires ⇒ tier one, 1 spire ⇒ tier
five.** Tier five is "FIVE Yeti & Ice Dragons" (line 953). So progress
makes the survivors monstrous, which is a complete difficulty curve out
of one integer and no timers.

**(b) Summed hero experience level is the game's "how strong is the
player" metric, and it is used two different ways in this file.**
`Set_Spire_Levels` uses it to *shorten* the count (bands at 40 and 70);
`Post_Enemy_Reward` (line 1753, 21.6b) uses it both as a spend gate
(`if (($randomnumber(100)+1) < total_level)` — so a total of 70 means a
~70% chance to act per poll) and as a reward-flag price ladder. **Both
compute it the same way: `$ListObjects(..., "hero", ..., #MyPlayer,
#InsideOtherUnits)`, filter `"subtype" == "hero"`, sum
`#ATTRIB_ExperienceLevel`.** Two independent sites in one file, so this
is a real convention, not one author's habit. Note `#InsideOtherUnits`
in both — heroes resting in a guild still count — and the `"subtype"`
filter, which is §20.2's recovery step (the `"hero"` class also contains
peasants/caravans; `Create_Siege_Caravan` line 2213 confirms it by
querying `"hero"` with `#CheckTitles, "Caravan"`).

**(c) `Spawn_Function` is a `function`-typed field written at runtime and
invoked *indirectly* — the tier is literally a function pointer stored on
the lair.**

```gpl
declare function spawn;              // a local of type function
…
spire's "Spawn_Function" = spawn;    // stored on the agent
…
spire's "Spawn_Function" ( spire );  // Force_Spire_Spawns, line 1193
```

The indirect-call syntax itself is **already documented** (§14's
`(agent's "attr")(args)` entry, §17.5 item 6) — what is new is the
*pattern*: **a difficulty tier expressed as which function each agent
carries, with a single `foreach` to re-tier every agent at once.** Note
also this file's call form omits the wrapping parentheses that §14/§17.5's
examples used, and compiles; a sweep of the corpus finds six live sites of
the field-call form in total (`Quests_3.gpl` 1193 and 1223,
`mx_check_nearby.gpl` 17, `Hero_Deaths.gpl` 106 / `mx_Hero_Deaths.gpl`
197 — the last two calling an agent's own `ActiveScript` synchronously
behind a `$HasAttribute` guard), plus commented-out instances in
`construction_rules.gpl`/`mx_Construction_Rules.gpl` (a per-building
`"buildRequirements"` hook that was never enabled) and `mx_caravan.gpl`
line 98 (`(ThisAgent's "IGDeathScript")(ThisAgent)`).

**(d) `Attack_Action` is a per-agent string naming the action/spell the
unit fires, and swapping it retiers the weapon.** §19.9 showed
`Attack_Action = "Do_Nothing"` on a spawned caster; here five distinct
values (`"Spire_Blast_One".."Five"`) are assigned to a *building* at
runtime, and `Spire_Attack` fires whatever is in the field:
`$PerformAction (ThisAgent, ThisAgent's "Attack_Action", ThisAgent's
"Target")`. **So "this tower's gun" is a data field, not code** — the
cheapest possible way to give one unit type several weapon strengths.
(The five `Spire_Blast_*` actions themselves live in the expansion's
action data, not GPL; not opened in this batch.)

**(e) `$SetEffectorDirection (agent, "<effector name>", direction)` — new
primitive, and this file is its ONLY call site in the entire corpus**
(grep: one hit, line 1071; confirmed engine-side by its presence in the
SDK compiler keyword list, `SDK/Extras/GPL User Defined Language template
for Notepad++.xml` `Keywords3`, beside `$LookupFunction` and
`$DeleteAllEffectors`, and by having no `function` definition anywhere).
Used here to pick **frame `count - 1` of a permanent overlay** (created in
`Spire_Birth` as `$CreateEffector (thisagent,
"Spire_Lights_Effector", 1, "infinite")`, §13's marker form), i.e. **an
effector's "direction" doubles as a state selector, giving you a visible
readout of a GPL variable with no extra art beyond one multi-frame
overlay.** That an 8-way "direction" index can be repurposed as a state
index is the useful part; the exact mapping from index to displayed frame
is engine-side and **UNVERIFIED**.

**(f) The birth script re-runs the retiering, which is what keeps
regenerated spires correct.** `Spire_Birth` (1119-1129) does four things:
`$NewThread (thisagent's "activeScript", #Normal_Cycle, thisagent)` (note
it threads the slot *without assigning it* — the value comes from the
unit's data), creates the lights effector, sets
`#ATTRIB_HealingRateModifier` to 1, and calls `$Set_Spire_Levels()`.
**Pattern worth copying: put the global re-tune call in the unit's own
birth script, and every later-spawned instance configures itself.**

**Two supporting functions complete the loop:**

- `Force_Spire_Spawns` (1177) — "everyone fire at once": list the spires,
  indirect-call each one's `Spawn_Function`. Also called directly from
  `Spire_Death`, so **destroying a spire triggers an immediate volley from
  all the others** before the retier.
- `Check_Spire_Regeneration` (1198) — if fewer than five exist,
  `$SpawnUnit(Palace, "SpireOfDeath", $RandomCoord(Palace,1000,4000),
  #Monster_Player, "MAXHP")`, retier everything, then make **only the new
  one** spawn. Else still retier, with the shipped comment "in case the
  player is doing massive hero buildup." **So the quest cannot be won by
  attrition alone** — it is won by killing five faster than they respawn,
  and the last one standing is at maximum tier.

### 21.8 Elapsed-time difficulty scaling, and integer registers used as state machines

`FORTRESS_IXMIL`'s spawn system is the most numerically sophisticated
thing in §16-§21, and it is worth documenting because it answers "how do I
make waves get harder over time without authoring stages."

**The clock.** `Day_Counter` (2554) is three lines — `AIRootAgent's
"day_counter" += 1` — on `VictoryCondition2` at **60000 ms**. Two
independent shipped comments in this same file line up on what that
means: `Trade_Route_Spawn`'s header says "Launch a trade caravan every 1
to 1 1/2 days" for an interval of `$RandomNumber(30000) + 60000`, and
`Check_Spire_Regeneration`'s says "every 4-6 minutes" for
`$randomnumber(120000) + 240000`. **So one in-game "day" is 60000 ms and
GPL intervals are plain real-time milliseconds** — which also means
`Day_Counter`'s 60 s tick is exactly one day. Stated as a strong inference
from two agreeing shipped comments plus the counter's own interval, not
from an engine fact; it does resolve the steering file's standing question
about whether GPL durations are real milliseconds in the direction of
"yes, at default game speed."

**The two inputs.** Every wave function computes:

```gpl
day_modifier   = AIRootAgent's "day_counter";                        // total elapsed
delay_modifier = day_modifier - AIRootAgent's "victory_score";       // since last seen
```

…because `Warp_Out` stamps `AIRootAgent's "Victory_Score" =
AIRootAgent's "day_counter"` (line 2534) with the comment "Set the victory
score to act as the delay counter for the fortresses next appearance."
**That is the whole "punish the player for ignoring the boss" mechanic: an
integer register holding a timestamp, and a subtraction.**

**Wave type** (`Fortress_Ixmil_Spawn`, 2565):

```gpl
random = ( $RandomNumber ( 30 ) + ( day_modifier * 1 ) + ( delay_modifier * 2 ));
if ( AIRootAgent's "defeat_score" != 0 ) random *= 0.7;      // tone down mid-multi-jump
if ( random < 31 || AIRootAgent's "Quest_Flag_2" ) begin $..._Light ();    Quest_Flag_2 = FALSE; end
else if ( random < 60 || AIRootAgent's "Quest_Flag_3" ) begin $..._Moderate (); Quest_Flag_3 = FALSE; end
else $..._Heavy ();
```

**Wave size** (each of `..._Light` 2610 / `..._Moderate` 2687 /
`..._Heavy` 2755):

```gpl
SpawnPower = $RandomNumber ( 100 );
SpawnPower = SpawnPower + ( 20 + ( day_modifier * 2 ) + ( delay_modifier * 8 ));   // *10 in the other two
SpawnPower = SpawnPower / 100.0;
if ( AIRootAgent's "defeat_score" != 0 ) SpawnPower *= 0.7;
if ( SpawnPower > 2 ) SpawnPower = 2;                     // hard cap at 2×
spawns = 12.0 * SpawnPower;                               // float → integer
```

Six findings:

- **Elapsed time is a mild multiplier, absence is a strong one** (×1 vs
  ×2 for the type roll; ×2 vs ×8/×10 for the size). The tuning intent is
  spelled out in the shipped comment: "if the fortress is gone for a long
  period of time, the next spawn is likely to be more dangerous."
- **A normalised float multiplier with a hard cap is the shape to copy.**
  `SpawnPower` is built in "percent" space, divided by `100.0` into a
  0.2-2.0 multiplier, capped at 2, then multiplied against a per-wave base
  count (12/9/16/6). **One float, four different wave sizes, no tables.**
- **`float` locals and float literals work, and float→integer assignment
  truncates silently** (`spawns = 12.0 * SpawnPower` into
  `integer spawns`). Same looseness §17.2/§19.7 flagged for
  `Treasury_Looted` and `$AutoSpawn_Lair` — but here it is *deliberate and
  load-bearing*, which is the first shipped example of the conversion
  being used on purpose. Also note `random *= 0.7` applies a float to an
  `integer` variable in place.
- **`|| <bare boolean field>` is a deliberate first-time guarantee.**
  `Quest_Flag_2`/`_3` are initialised **TRUE** (lines 2331-2332, comment
  "These flags indicate that light and medium spawn waves … have not gone
  off yet") and consumed on first use, so the player is guaranteed to see
  a light wave then a moderate wave before RNG takes over. **Inverted
  polarity from §19.1's all-`False` init, and read as a bare truthy
  condition rather than `== TRUE`** — both forms ship. (This does *not*
  settle §19.3's `=`-in-a-condition question; every comparison in this
  file uses `==`.)
- **`defeat_score` is an integer state machine with negative sentinels,
  and the author documented it in-file.** Lines 2338-2352 are a 12-line
  comment block specifying the encoding — 0 = normal (and may roll a 1-in-4
  chance to start a multi-jump by setting 3); >1 = short warp, reduced
  spawn, decrement; 1 = short warp then an extended rest, set to -1;
  -1 = normal warp but still reduced spawn. **Reusable lesson, and the
  reason it is worth a paragraph: when a quest needs more than a boolean,
  the codebase's answer is one of the two score registers plus a comment
  block, not a new field.** Every read of it in the wave functions is the
  single test `!= 0`, which is what makes the encoding cheap.
- **The same thread drives both halves via one flag.**
  `Fortress_Ixmil_Warp_Engine` is `SpecialSpawnScript` and branches on
  `Quest_Flag_1` (TRUE = currently on the map), so one function alternates
  in/out and picks its own next delay per branch — 6000-10000 ms during a
  multi-jump, `$RandomNumber(90000)+120000` normally,
  `$RandomNumber(90000)+210000` after the extended-rest sentinel. **That
  is §19.3's self-pacing sequencer with a two-state phase bit instead of a
  flag chain.**

One structural oddity worth flagging so nobody hunts for it: **`Warp_Out`
(2499) takes `agent fortress` and is never called from anywhere in this
file** (grep: one definition, no call sites) — yet it holds the entire
warp-out half of the cycle, including the grove teardown and the
`defeat_score` bookkeeping, while `Fortress_Ixmil_Warp_Engine`'s own
`else` branch does only the effector/fade/thread-kill part. **So the
shipped quest appears to warp out visually but never re-arm its next
appearance through `Warp_Out`'s scheduler.** Since the engine may invoke
it by name the way it does quest entry points (§17.5), and `Fortress_
Active`/`Ixmil_Scan` are likewise data-referenced rather than
GPL-called, this is flagged as an **unresolved wiring question, not a
confirmed bug** — see 21.10.

### 22.3 The difficulty-tier system — a post-victory endless mode, and it is fully retunable

**No earlier batch saw this, and its name is misleading.** The four
`end_game_script_*` functions are not the quest's endgame. They are the
**"keep playing after you win" harassment driver**: 12 of the 19 quests
install one *immediately after* `$declarevictory`, in the same statement
block, having just killed the poll thread. §19.5d established that quest
threads survive `$declarevictory`; this is the base game's systematic use
of that fact.

#### a) The whole system, in four layers

Lines 4176-4358. Read in full.

```gpl
expression #easyMonster   1        // 4176-4180: the tier register values
expression #mediumMonster 2
expression #hardMonster   3
expression #expertMonster 4

function end_game_script_easy()                          // 4183 (tier driver)
begin
    AIRootAgent = $RetrieveAgent ("GplAIRoot");
    $spawn_monsters (3, #easyMonster);                   // batch + tier
    $setthreadinterval (AIRootAgent's "VictoryCondition2",
                        $random_time (600000));          // re-pace self
end

function spawn_monsters (integer num, integer difficulty) // 4197 (dispatcher)
begin
    while (i < num) do begin
        if (difficulty == #easymonster)  monster = $pick_easy_monster();
        else if (difficulty == #mediummonster) monster = $pick_medium_monster();
        else if (difficulty == #hardMonster)   monster = $pick_hard_monster();
        else if (difficulty == #expertMonster) monster = $pick_expert_monster();
        $spawnunit (palace, monster,
                    $RandomedgeCoord ($randomnumber (4)), #Monster_player);
        i += 1;
    end
end

function pick_easy_monster() is string                    // 4229 (roster)
begin
    i = $randomnumber (4);
    if (i == 0) return "Giant_spider";
    if (i == 1) return "Zombie";
    if (i == 2) return "Red_Bear";
    return "White_wolf";                                  // the fallthrough case
end
```

**Layer 1 — four rosters**, each a `$RandomNumber(N)` over an if-chain
with the last entry as the fallthrough return (so N equals the entry
count, and the chain has N-1 `if`s). The full shipped rosters:

| Tier | Roster fn (line) | `$RandomNumber` | Monsters |
|---|---|---|---|
| easy | `pick_easy_monster` (4229) | 4 | `Giant_spider`, `Zombie`, `Red_Bear`, `White_wolf` |
| medium | `pick_medium_monster` (4249) | 5 | `Werewolf`, `Rust_spitter`, `Goblin_fighter`, `goblin_champion`, `Harpy` |
| hard | `pick_hard_monster` (4272) | 4 | `Minotaur`, `Troll`, `Medusa`, `Skeleton` |
| expert | `pick_expert_monster` (4292) | 3 | `Evil_Oculus`, `Dragon`, `Vampire` |

**Layer 2 — one dispatcher**, `spawn_monsters(num, difficulty)` (4197),
which loops `num` times and spawns each pick at a random map edge as
`#Monster_player`.

**Layer 3 — four tier drivers.** This is where the actual tuning lives,
and the differences between the four are small and entirely legible:

| Tier driver (line) | What it spawns per firing | Re-pace interval |
|---|---|---|
| `end_game_script_easy` (4183) | `spawn_monsters(3, easy)` — unconditional | `$random_time(600000)` |
| `end_game_script_medium` (4310) | 50/50: `(6, easy)` **or** `(3, medium)` | `$random_time(450000)` |
| `end_game_script_hard` (4328) | 50/50: `(6, medium)` **or** `(3, hard)` | `$random_time(300000)` |
| `end_game_script_expert` (4345) | 50/50: `(6, hard)` **or** `(3, expert)` | `$random_time(300000)` |

**So a "tier" is exactly three numbers: a batch size, a coin-flip between
one-tier-down-in-bulk and this-tier-in-small-numbers, and a period.** Each
tier from medium up is the tier below it, doubled in count, half the time.
`hard` and `expert` share the same 300 000 ms period — the only escalation
between them is the roster.

**Layer 4 — the install site**, always the same two lines and always in a
victory branch:

```gpl
$declarevictory (palace, AIRootAgent's "end_coord");
$KillThread (AIRootAgent's "VictoryCondition");
AIRootAgent's "VictoryCondition2" = $end_game_script_easy;
$newthread (AIRootAgent's "VictoryCondition2", $random_time (600000));
```

#### b) What selects a tier: nothing at runtime — it's authored per quest

**There is no difficulty setting, no `$GetDifficulty`, no `Quest_Number`
switch.** The tier is a literal function reference written into the quest's
own victory code. Grepping `end_game_script` across all of
`SDK/OriginalQuests/` gives **19 install sites across 12 quests** (some
quests have more than one victory path and install the same tier in each),
and the tier is hardcoded at every one:

- **easy** — Barren Waste (149), Bell Book & Candle (358), Holy Chalice
  (500), Elven Treachery (1851 and 1872 in `elven_victory`, 1923 in
  `Elven_victory2` — all three paths, same tier), Goblin Hordes (2482)
- **medium** — Crown (683), Dark Forest (850), Deal with the Demon (1305
  and 1344 — both victory paths), Liche Queen (2751)
- **hard** — Slay the Dragon (1580), Fertile Plain (2101)
- **expert** — Day of Reckoning (1123), and only that one

**Seven quests install no tier at all:** Rescue the Prince, Tomb of the
Dragon King, Magic Ring, Slave Pits, Brashnard, Wizard's Curse, and
Forsaken Lands (which calls the *dispatcher* pre-victory but never a tier
driver). Two of those (Tomb of the Dragon King, Slave Pits) hand off to
`rescue_keep_playing` instead (22.4b).
**The tier↔quest mapping is authorial judgement, not a formula** — Day of
Reckoning gets expert because its win condition is already "kill
everything," and easy lands on the two introductory quests.

#### c) Can a modder add or retune a tier? Yes, and it is unusually cheap

Direct answer, from the structure above:

- **Retune an existing tier:** change the two numbers in one
  `end_game_script_*` and every quest using that tier changes. Nothing
  else references them.
- **Reroster a tier:** edit the `pick_*_monster` if-chain. **Keep
  `$RandomNumber(N)`'s N equal to the entry count** — the last entry is
  the unconditional `return`, so if you add a monster without bumping N it
  simply never appears, and if you bump N too far the extra rolls all fall
  through to the last entry. That off-by-one is the only trap here.
- **Add a fifth tier:** add an `expression #myMonster 5`, a
  `pick_my_monster()`, one more `else if` in `spawn_monsters`, and an
  `end_game_script_mine()`. All four are plain GPL in one file; there is
  no engine-side table and no CAM/XML registry, unlike §17.7's
  special-event registry.
- **Use it before victory.** `forsaken_events`' repeating tail (line 2358)
  calls `$spawn_monsters(4, #EasyMonster)` on a 50% roll during normal
  play — **the only pre-victory call site in the shipped game**, and proof
  the dispatcher isn't coupled to the post-victory path.
- **Expansion mode does not have any of this** (22.0). Porting it is a
  copy-paste of ~180 lines into an mx `Rules/` file.

Two shipped inconsistencies, so nobody treats them as intent:
`end_game_script_easy`'s comment says "1 - 2 monsters every 10ish days"
while the code spawns 3; `end_game_script_medium`'s says "1 - 2 monsters
every 5 days" while it spawns 3-6. And `spawn_monsters` **never
initialises its loop counter `i`** before `while (i < num)` — the same
uninitialised-local reliance §18.10 flagged as **UNVERIFIED as a language
guarantee**; this is now a second shipped instance of code that depends on
it (`bbc_victory`'s `sites_gone += 1` at line 340 is a third).

### 22.7 `Lair_extra_delay` — the map-wide lair pacing knob

The one lair-tuning lever §19.7's field survey missed, because it lives on
the **root agent**, not on a lair.

- **Declared:** `GPL/prototype.gpl` 29 and `GPLMx/mx_prototype.gpl` 35,
  as `integer Lair_extra_Delay`, with a shipped comment that states the
  whole contract: *"This holds the time that is added onto a lair's
  spawnrate for every extra lair on a map … This is frequently overwritten
  on a per-quest basis in Epic_quest_scripts."*
- **Default:** `7000`, set as data in `GPL/Misc_Data.dat` 206 (mx:
  `GPLMx/mx_Misc_Data.dat` 207), in the same root-agent record that
  carries `KickoffFunction` and `Track_Number`.
- **Consumed:** `GPL/TaskModules/Buildings/Lair.gpl` 31 —
  `other_lair_delay = GplRootAgent's "Lair_Extra_Delay" *
  $listsize(other_lairs);` (mx twin `mx_Lair.gpl` 44, reading
  `AIRootAgent's` instead). That product is then added to the lair's spawn
  interval.
- **Overwritten:** exactly once in the shipped game —
  `GOBLIN_HORDES` 2424 sets it to `1000`.

**So there is a global, per-quest, one-integer knob that makes lairs spawn
slower the more lairs a map has.** At the 7000 default a 10-lair map adds
70 seconds to every lair's cycle; Goblin Hordes drops it to 1000 because
the quest's entire premise is being overrun. **For a modder this is the
cheapest possible difficulty dial for any lair-heavy map**, and it is
data-settable (the `.dat` default) as well as GPL-settable.

**The sibling field, and why `$HasAttribute` guards it.** mx
`Freestyle()` writes **`"Lair_Delay_Override"`** (22.4a). Traced fully:

- Declared **only in `GPLMx/mx_prototype.gpl` 65** — `boolean
  Lair_Delay_Override`, with the comment mx `Freestyle()` copies verbatim.
  **`GPL/prototype.gpl` does not declare it** (grepped; the base prototype
  jumps from `Quest_Flag_9` to `Message_Check_1`).
- Read in `GPLMx/TaskModules/Buildings/mx_Lair.gpl` 48-52, and the reader
  carries **the same `$HasAttribute` guard as the writer**:
  ```gpl
  if ( $HasAttribute ( "Lair_Delay_Override", AIRootAgent ))
      if ( AIRootAgent's "Lair_Delay_Override" )
          begin
              If (Other_Lair_Delay < #Min_Freestyle_Lair_Spawn_Delay)
  ```
  i.e. when set, the computed `Lair_extra_delay × lair count` product is
  **clamped up to a floor**, `#Min_Freestyle_Lair_Spawn_Delay`.

So the pair is: `Lair_extra_delay` scales the delay with lair count, and
`Lair_Delay_Override` imposes a minimum for freestyle maps whose lairs are
mostly off-map. **And the double `$HasAttribute` guard is now explained by
evidence rather than guessed at — the field is absent from the base
prototype, so every access to it has to ask first.** That makes it a
worked example of the feature-detection pattern from 22.4a rather than
defensive noise.

---

## Chapter 4: Agent Behavior and Custom AI

Giving heroes, monsters and NPCs quest-specific behavior.

### 18.1 What kind of function lives here — the hook test applied to all 15

Applying §16.1/§17.5's test (is the function engine-invoked by name, is
it assigned to an agent attribute, or is it called directly from GPL?)
to every function in the file. `$Name(` call-site counts are from
repo-wide `grep_search` over the whole SDK `.gpl` tree.

| Function | How it's reached | Assigned/called from |
|---|---|---|
| `Deliver_Ring` | **attribute-assigned** to `ActiveScript`+`BasicScript`+`BackScript`+`StartingScript` | `GPL/TaskModules/Subtasks/Inventory.gpl` lines 173-183 (`QItem_Stat_Boost`, `#QItem_Magic_Ring` branch) |
| `Steal_Ring` | same four slots | same file, lines 190-200 (the `Else`, i.e. a non-player-1 hero) |
| `Drop_Ring` | **attribute-assigned** to `BackScript` only | `Deliver_Ring` itself (line 33) |
| `Steal_Ring_Arrive_Palace` | `BackScript` only | `Steal_Ring` itself (line 151) |
| `Be_Dumb` | **attribute-assigned** to `StartingScript` | `GPL/Hero_Births.gpl` line 110, inside `Generate_Character_Attributes` |
| `Hooligan_Check` | **directly called**, returns `boolean` | `Be_Dumb` line 233 — the only call site |
| `Arrest_Hooligan` | `ActiveScript`/`BackScript` | `Be_Dumb` line 236, `Arrest_Hooligan` line 331 (self, as its own BackScript) |
| `travel_to_arrest` | `ActiveScript` | `Arrest_Hooligan` line 330 |
| `Guardian_Hero_Tree` | all four behavior slots | `GPL/Rules/epic_quest_scripts.gpl` lines 3843-3846 (`WIZARDS_CURSE()`) |
| `Guardian_hero_Eval_Nearby` | **`EvaluationScript`** | same block, line 3847 |
| `Curse_Active` | **`SpecialScript`** on a *building*, then threaded | same file, lines 3814-3815 |
| `Setup_Special_Chests` | **directly called**, takes two `function` params | `epic_quest_scripts.gpl` line 457 (`HOLY_CHALICE()`) |
| `Holy_Chalice_Chest_Birth` | **`BirthScript`** | installed by `Setup_Special_Chests`; also re-entered via `$RunThread` from the death handler |
| `Holy_Chalice_Chest_Death` | **`IGDeathScript`** | installed by `Setup_Special_Chests` |
| `Captured_Peasant_Goto_Palace` | `ActiveScript`+`BasicScript`+`BackScript` | `epic_quest_scripts.gpl` lines 4024-4026 (`Wizards_Curse_Victory`) |

**Three conclusions, all load-bearing for modders:**

1. **There are no engine-invoked hooks in this file.** Every function is
   either reached through a script-slot attribute the engine reads
   (`ActiveScript`/`BackScript`/`EvaluationScript`/`BirthScript`/
   `IGDeathScript` — hooks already documented in §1, §2, §15, §17.5) or
   called explicitly from GPL. Contrast §16.1's `CanIBuildThisBuilding`
   and §17.5's `Freestyle()`/`VAMPIRIC_REVENGE()`. **Nothing in this
   file's naming or location makes it special** — "Rules/Quest_Actives"
   is an organizational convention, not a registry. A modder can put
   equivalent functions in any file in their own project.
2. **The interesting hook is therefore the *slot*, not the function.**
   This file's real contribution is a worked catalogue of *which slot to
   write into for which effect*, which 18.2 pulls out.
3. **One orphan.** `Treasure_Spawner()` (line 446) has **zero references
   anywhere in the workspace** — grepped the whole tree, only the two
   definitions (base + mx) match. It is nullary like the engine-invoked
   quest entry points, but nothing indicates the engine knows it: it is
   not a quest entry name in any shipped script, and the shipped quests
   that want scattered chests call `$setup_random_treasure(...)`
   instead (`epic_quest_scripts.gpl` line 3806 uses
   `$setup_random_treasure(20, #default_spawn_treasure_dist)`).
   **UNVERIFIED** whether any `.q` file names it as a pattern/entry
   function; our own `.q` research notes a 12-byte pattern-name field,
   and `Treasure_Spawner` is 16 characters, which argues against it, but
   that is an inference from this project's own format notes, not a
   confirmed engine fact. Treat it as dead code with a useful body
   (18.9).

### 18.2 The quest-behavior slot vocabulary, and the swap-and-stash idiom

§1 documented `ActiveScript`/`BackScript`/`TaskName`. This batch's
wiring sites use four more slots, all **plain GPL-declared prototype
fields** (`GPL/prototype.gpl`, mirrored in `GPLMx/mx_prototype.gpl`),
read directly rather than inferred:

| Slot | Declared on | Prototype comment (verbatim) | Used in this batch for |
|---|---|---|---|
| `StartingScript` | `hero` line 120, `monster` line 215 | "this holds the core start script that is inited with the agent. never change, because we rely on this to always hold the agent's starting/basic behavior. this script is never 'executed'" | the slot a *revived/reset* agent comes back as |
| `QuestScript` | `hero` line 142 | "This holds Quest-Specific logic" | the stash slot holding the agent's *original* behavior |
| `Special_Boolean` | `hero` line 156, `monster` line 229 | "This is quest specific. For instance, in WCurse, it is TRUE if a Hooligan has been found." | a per-agent claim/latch flag (18.5) |
| `SpecialScript` | `Guild` line 383, `Dwarven_Settlement` line 442 | "This holds any quest-specific functionality for the guild. For instance, in Magic Ring, it runs Hero_Generator" | giving a *building* a custom repeating behavior (18.7) |

Two things worth stating plainly because they change what a modder can
do:

- **`Special_Boolean` and `QuestScript` are sanctioned, pre-declared,
  quest-generic scratch fields on every hero and monster.** You do not
  need to invent an attribute or edit a prototype to give a quest agent
  one boolean and one saved behavior — the engine-facing prototypes
  already ship with them, and the shipped comments say that is their
  purpose. (Compare §17.3's `EventAgent`, which gives an *event* ten
  booleans; this is the per-agent equivalent.)
- **`SpecialScript` exists only on `Guild` and `Dwarven_Settlement`, not
  on `prototype building()`.** Read `prototype building()` (lines
  248-281) in full: it declares `visited_script`, `ActiveScript`,
  `RevenueScript`, `spawn_1`, the four birth/death scripts, and
  `upgradescript` — no `SpecialScript`, no `SpecialList`. So the
  "give this building a quest job" recipe below applies to guilds
  (including temples and the Wizard's Guild) and dwarven settlements;
  for any other building you must reuse its `ActiveScript` field, which
  is declared for exactly that reason ("For any buildings, like the
  TradingPost, that have ActiveScripts").

#### The swap-and-stash idiom (the single most transferable pattern here)

Both places that hand a hero a quest behavior do the *same four steps*,
and getting the order right is the whole trick. From
`Inventory.gpl` lines 173-183 (base; `mx_Inventory.gpl` 115-125 is
character-identical):

```gpl
ThisAgent's "ActiveScript" = $Deliver_Ring;
ThisAgent's "BasicScript"  = $Deliver_Ring;
ThisAgent's "BackScript"   = $Deliver_Ring;

//Put this agent's "StartingScript" into their questscript
//This is what ThisAgent is reset to after they drop the ring
ThisAgent's "QuestScript" = ThisAgent's "StartingScript";

//…so that if the holder of the ring gets ressed they keep trying
ThisAgent's "StartingScript" = $Deliver_Ring;

$Reset_Tasks (ThisAgent);
```

1. **Overwrite all three live slots** (`ActiveScript` = what runs now,
   `BasicScript` = the idle fallback, `BackScript` = the travel return
   address) so no half-finished task can bounce the agent back into its
   old behavior.
2. **Stash the original behavior in `QuestScript`.** `StartingScript` is
   the thing worth saving because it is the class's canonical entry
   behavior (§15's per-class trees, bound in `Hero_Data.dat`).
3. **Overwrite `StartingScript` too**, so the quest behavior survives
   death/revival and any `$Reset_Tasks`. Note this *deliberately
   violates the prototype's own "never change" comment* — the shipped
   code changes it anyway, and the comment's real content ("this script
   is never executed") is what makes the violation safe.
4. **`$Reset_Tasks(ThisAgent)`** to force the new scripts to take effect
   immediately (`LowLevel.gpl` lines 1011-1019 — nulls `target`, sets
   `activescript` and `backscript` from `basicscript`; §1).

**Restoring is the mirror image**, and `Drop_Ring` (lines 122-126) shows
it, including a real shipped bug worth not copying:

```gpl
ThisAgent's "ActiveScript"   = ThisAgent's "QuestScript";
ThisAgent's "BasicScript"    = ThisAgent's "QuestScript";
ThisAgent's "BasicScript"    = ThisAgent's "QuestScript";   // duplicated
ThisAgent's "StartingScript" = ThisAgent's "QuestScript";
```

`BasicScript` is assigned twice and **`BackScript` is never restored** —
so a hero that finishes the ring delivery keeps `$Drop_Ring` as its
travel return address until the next `$Reset_Tasks` overwrites it from
`BasicScript`. Harmless here only because `Drop_Ring`'s own guard clause
re-checks its preconditions and calls `$Reset_Tasks` when they fail
(18.3). Restore all four slots.

`Hero_Births.gpl` line 105-110 is the second, independent instance of
the same idiom — and it shows the variant where **only `StartingScript`
is swapped**, because the target agents are being born right now and have
no live task yet:

```gpl
If (RootAgent's "Quest_Number" == #QNumber_Wizards_Curse)
    If ($GetUnitPlayerNumber (ThisAgent) == #Player_1)
        begin
            ThisAgent's "QuestScript" = ThisAgent's "StartingScript";
            //Init scripts to be_dumb. it will call their decision trees via QuestScript
            ThisAgent's "StartingScript" = $Be_Dumb;
            …
        end
```

Three reusable details in that one block:

- **The gate is `AIRootAgent's "Quest_Number"`** (`#QNumber_Wizards_Curse`
  = 19, `globals.gpl` line 661), i.e. §16.2's global quest-mode register
  used exactly as §17.6 described for `Setup_Quest_Monster`. **This is
  the standard way to make a shared birth hook quest-specific: branch on
  `Quest_Number` inside the shared function rather than replacing it.**
- **It lives inside `Generate_Character_Attributes(agent thisagent)`**
  (`Hero_Births.gpl` line 8), whose own header comment says "This
  function is called by the in-game code when a vehicle is generated" —
  an engine-invoked hook, so **every hero born for the rest of the game
  gets the quest behavior automatically**, with no per-spawn wiring. The
  contrast with the ring (a one-off, applied to whichever hero picks the
  item up) is the general choice: gate in the birth hook for "all
  heroes, always," assign at the trigger site for "this one agent, now."
- `#WCurse_Dumb_Penalty` (5, `globals.gpl` line 681) is applied as a
  clamped stat penalty in the same block
  (`If (Intelligence <= 5) SetAttribute(…, 1) Else AdjustAttribute(…, -5)`)
  — the standard shape for "subtract N but never below 1."

### 18.3 `Deliver_Ring`/`Drop_Ring`/`Steal_Ring` — the courier pattern

Four functions, one mechanism: **"whoever holds item X carries it to
place Y, and something happens on arrival."** Reusable for capture-the-
flag, fetch-quests, "bring the prisoner home," or any escort-to-a-
location objective. One line of plot: it's the Magic Ring quest, and the
mirror-image `Steal_Ring` makes an enemy hero carrying the ring home a
loss condition instead.

**Phase 1 — the seek/despatch handler (`Deliver_Ring`, lines 8-44).**
The shape is a state machine that re-runs every cycle until the
destination is *findable*, then converts itself into a travel task:

```gpl
$ListObjects (ThisAgent, "Special", -1, Lairs, #NoHiddenMap);
Lairs = $ListTitles (Lairs, "Hidden_Ring_Site2");

If ($ListSize (Lairs) > 0)
    begin
        $SpecifyIntent (ThisAgent, #Intent_Delivering_Ring);
        ThisAgent's "Target"      = $Listmember (Lairs, 1);
        $Move (ThisAgent, ThisAgent's "Target", "avoid_vehicles");
        ThisAgent's "Destination" = $LocationOf ($ListMember (Lairs, 1));
        ThisAgent's "ActiveScript" = $Travel_to_safe;
        ThisAgent's "BackScript"   = $Drop_Ring;
    end
Else
    begin
        If ($IsMoving (ThisAgent) == False)
            $Move (ThisAgent, $RandomCoord (ThisAgent, $GetAttribute (ThisAgent, #ATTRIB_SightRange)));
        (ThisAgent's "EvaluationScript")(ThisAgent);
    end
```

Five separately reusable pieces:

1. **`ActiveScript = $Travel_to_safe; BackScript = $<on-arrival>` is the
   whole "go there, then do this" contract** (§1's `has_arrived` relay).
   `travel_to_safe` (`GPL/TaskModules/Characters/Travel_to.gpl` lines
   71-84) is the right variant for a courier: unlike `travel_to`, it does
   **not** call `$Eval_Items_Nearby` or the agent's `EvaluationScript` at
   all, and it explicitly `$clearlist(thisagent's "hostiles")` every tick
   with the shipped comment "because they don't evaluate when they are
   going somewhere via this function we must clear the hostiles list
   ourselves." **So `travel_to_safe` = "ignore distractions and threats,
   just get there"** — exactly what you want for an escort/delivery, and
   the reason the shipped ring carrier doesn't stop to loot.
2. **You must set `Target` *and* `Destination` *and* call `$Move`.**
   `Target` is what `has_arrived` tests against, `Destination` is the
   coordinate fallback, `$Move` starts the actual pathing. Setting only
   one is the classic failure.
3. **`$Move(agent, target, "avoid_vehicles")` — a previously
   undocumented optional string flag on `$Move`.** Confirmed as a real
   shipped idiom, not a one-off: 8 call sites across base and mx
   (`Follow_Heal.gpl` 37, `Follow_Heal.gpl` 119 (`follow_support`),
   `Go_Heal.gpl` 38, `Go_Control_Monster.gpl` 30, `flee_map.gpl` 63, plus
   this one), and **every single one is paired with a "get there safely"
   task** (fleeing the map, going to be healed, following to heal).
   `Travel_to.gpl` line 381's commented-out code makes the intent
   explicit: `if (safe) $move(…,"avoid_vehicles") else $move(…)`.
   **UNVERIFIED** what "vehicles" the engine avoids (caravans/tax
   collectors are the obvious candidates) — the flag's effect is
   engine-side and no GPL reads it back.
4. **The `Else` branch is the "objective not available yet" idle**:
   wander inside your own sight radius and *still run your
   `EvaluationScript`* so you defend yourself. Note the deliberate
   asymmetry — `Steal_Ring`'s equivalent line is **commented out**
   (line 158), so an enemy ring-thief whose palace is dead wanders
   without evaluating threats. Either is a valid design; know which you
   picked.
5. **`$SpecifyIntent(ThisAgent, #Intent_Delivering_Ring)`** just labels
   the unit's status for display (§7). The constant is `defines.gpl`
   line 87, value **79** — sandwiched between `#Message_Magic_Ring_
   Show_Site_2` (78) and `#Message_Dark_forest_start` (80). Independent
   re-confirmation of §16.1's finding that `#intent_*`/`#message_*`/
   `#sign_*`/`#chat_*` are **one shared, contiguous engine-side string
   index space**; `#intent_arresting_hooligan` (117, `defines.gpl` line
   125) sits between `#sign_dragon_gravestone` (116) and
   `#message_slaves_freed` (118), so this is not a coincidence of one
   block.

**Phase 2 — the arrival handler (`Drop_Ring`, lines 47-127), and its
guard clause is the important part.**

```gpl
Ring_Site = $ListMember (Lairs, 1);
If (ThisAgent's "Target" != Ring_Site || $IsAdjacent (ThisAgent, Ring_Site) == False)
    begin
        $Reset_Tasks (ThisAgent);
        return;
    end
```

**Any `BackScript` arrival handler must re-verify that it actually
arrived at the thing it meant to arrive at.** `has_arrived` hands control
back on *several* different conditions, including "target no longer
valid" and "I stopped moving" (`Travel_to.gpl` lines 200-260) — so
reaching your `BackScript` does *not* prove success. Both arrival
handlers in this file do this check and both bail out via
`$Reset_Tasks`; `Steal_Ring_Arrive_Palace` uses
`$InsideBuilding(ThisAgent) == False` as its equivalent test because its
destination is a building it entered via `$Hide`. Copy this guard.

**The completion sequence** is a compact catalogue of "end a quest
objective" calls, in shipped order:

| Step | Call | Note |
|---|---|---|
| Undo quest hostility | `$SetPlayerTeamNumber (Dude, $NeutralTeamNumber ())` on the Player 1 and Player 2 palaces | `$NeutralTeamNumber()` is the counterpart to §16.2's `$NewTeamNumber()` — **the way to *end* a forced war**, not just start one |
| Despawn quest monsters | `$ListTitles(monsters,"Black_Phantom")` then `$SetAttribute(Dude, #ATTRIB_HP, 0)` per member | **Zeroing HP is the "kill this cleanly, running its death script" idiom**; contrast `$DeleteGamePiece` (18.9), which removes without a death |
| Clear the carry marker | `If ($CheckEffector(ThisAgent,"Ring_Icon")) $DeleteEffector(…)` | the `duration 1 + "Infinite"` marker-effector pattern from §13; created in `Inventory.gpl` line 168 |
| Flip the destination's visual state | `$SetAttribute (ThisAgent's "Target", #ATTRIB_forcebuildingState, #Building_force_inactive)` | see below |
| Restore ambience | `$Reset_Quest_Music (AIRootAgent)` | pairs with `$Setup_Quest_Music`/`$Play_Endgame_Music` used at quest init |
| Win | `$declarevictory(palace, thisagent)` then `$KillThread(AIRootAgent's "VictoryCondition")` | §16.2's optional 2nd arg, here an **agent** (the courier) as the end-of-game camera focus, vs. `epic_quest_scripts.gpl` line 4048's `AIRootAgent's "end_coord"` coordinate form |
| Consume the item | `$DeleteInventoryItem (#QItem_Magic_Ring, ThisAgent)` | `#Qitem_Magic_Ring` = 13, `GPL/QItems.gpl` line 14 |
| Un-swap the scripts | the four-slot restore from 18.2 | (with the duplicate-`BasicScript` bug noted there) |

**`#ATTRIB_ForceBuildingState` is a generically useful lever and worth
naming explicitly:** `#building_normal_state` 0 / `#building_force_
inactive` 1 / `#building_force_active` 2 (`globals.gpl` lines 22-25). It
overrides a building-like agent's displayed/functional state
independently of its real condition. Confirmed call sites across
unrelated systems: `Treasure.gpl` line 61 forces a looted chest *active*
(the open-with-gold art), `Holy_Chalice_Chest_Birth` forces a fresh chest
*inactive* (closed), `Sewer_Graveyard.gpl` lines 15-17 flips a sewer
closed on a random roll, `Building_Deaths.gpl` line 825 forces
graveyard crosses active, and `epic_quest_scripts.gpl` line 3319 sets it
**at spawn time** via `$Concatenate(#ATTRIB_forcebuildingState,
#Building_force_active)` (§17.5's spawn-time attribute mechanism). **Note
the shipped comment in `Drop_Ring` says "Set the ring site to Active"
while the code sets `#Building_force_inactive`** — the comment is wrong,
or "active" means something different to the artist than to the enum;
either way, **verify which state gives which art before relying on it.**

**Phase 3 — the mirror handler (`Steal_Ring` + `Steal_Ring_Arrive_
Palace`).** Same skeleton, three differences worth copying:

- The destination is `$GetPalace(ThisAgent)` (own palace) instead of a
  searched map object, and travel is `$Hide (ThisAgent, Palace)` rather
  than `$Move` — **`$Hide(agent, building)` is the "walk in and be
  inside" move**, and `$IsHidden(agent)`/`$InsideBuilding(agent)` are the
  two ways to test that it worked (this file uses both; `$InsideBuilding`
  in the arrival guard, `$IsHidden` in 18.9's peasant despawn).
- Failure state is `$IsDead(Palace)` — **an objective whose destination
  can be destroyed needs a wander fallback**, or the handler dereferences
  a dead agent every cycle.
- On success it walks `$ListPalaces()` for `#Player_1` and calls
  `$DeclareLoss(Palace)`. **`#Player_1`-hardcoding is what makes these
  two functions single-player-only** — the same limitation §17.2 flagged
  for `$GetPlayerOnePalace()`. A multiplayer-safe version would use
  `$GetUnitPlayerNumber(ThisAgent)` (§17.3) to find the *carrier's*
  opponent.

### 18.4 `Be_Dumb` — the interposed-wrapper pattern (a debuff that is a *behavior*)

`Be_Dumb` (lines 215-261) is the cleanest example in the codebase of
**wrapping a hero's normal AI instead of replacing it.** The whole body
is a three-way decision that ends, in two of three branches, with:

```gpl
(ThisAgent's "QuestScript") (ThisAgent);
```

i.e. an indirect call (§17.5) through the stash slot 18.2 set up — which
holds the hero's real class decision tree. **So the quest behavior sits
*in front of* the class tree and delegates to it**, rather than
supplanting it. Structure:

| Order | Condition | Action |
|---|---|---|
| 0 | always, on entry | `If ($checkeffector(thisagent,"cursed_icon")) $DeleteEffector(…)` |
| 1 | `AIRootAgent's "Quest_Flag_4" == False` (curse still active) | continue to 2 |
| 2 | `$Hooligan_Check(ThisAgent)` returns TRUE | `counter = 0`, `ActiveScript = $Arrest_hooligan` (18.5) |
| 3 | else `$RandomNumber(100) + 1 > 50` | **waste the tick**: `$PerformAction(ThisAgent,"Be_dumb_idle",ThisAgent)` + `$CreateEffector(ThisAgent,"Cursed_icon",1,"infinite")` |
| 4 | else | `(ThisAgent's "QuestScript")(ThisAgent)` — act normally |
| 1' | `Quest_Flag_4 == True` (curse broken) | `(ThisAgent's "QuestScript")(ThisAgent)` |

Reusable mechanisms, in descending order of usefulness:

1. **A "50% of your turns do nothing" debuff needs no engine support, no
   attribute, and no effector — it's one `$RandomNumber` and a delegating
   call.** This is the generic recipe for confusion/drunk/stun-lite/charm-
   ish behavioral effects, and it composes with any class tree because it
   never needs to know which tree it wrapped.
2. **A single root-agent boolean is the global "effect is over" switch.**
   `Quest_Flag_4` is checked first, and when set every affected hero
   silently reverts to delegating — **no cleanup pass over the affected
   agents is needed**, which is why this scales to "every hero the player
   will ever recruit." Contrast the effector-based status effects in §11/
   §13, which must be individually removed. Note the flag is *not* reset
   in the script slots: an affected hero keeps `Be_Dumb` as its
   `StartingScript` forever; it just becomes a pass-through.
3. **Delete-then-maybe-recreate is how you make a marker effector track
   a per-tick state.** The `"cursed_icon"` is deleted unconditionally at
   the top of every cycle and recreated only in the "wasted tick" branch,
   so the icon is showing exactly when the hero is currently being dumb.
   Duration `1` + `"infinite"` is §13's marker-effector form.
4. **Quest tasks outrank the wrapper's own effect**: `Hooligan_Check` is
   tested *before* the dumb roll, so an arrest opportunity always wins. If
   you interpose a wrapper, decide explicitly where quest tasks sit
   relative to the impairment.
5. **The install site's ordering dependency is real and worth knowing.**
   `Generate_Character_Attributes` only writes `StartingScript`; it never
   touches `ActiveScript`. That works because the engine calls
   `Generate_Character_Attributes` *before* `hero_birth`, and
   `hero_birth` (`Hero_Births.gpl` lines 138-140) copies
   `StartingScript` into `basicScript`/`activeScript`/`backscript` and
   only then arms the behavior thread
   (`$NewThread(thisagent's "activeScript", #Normal_Cycle, thisagent)`,
   line 170). **Ordering claim confirmed by the code's dependency, not by
   an engine trace** — `Generate_Character_Attributes`'s effect would be
   inert if it ran after `hero_birth`, and the quest demonstrably works,
   so the order follows. Marked as inference, not a traced engine fact.
   Practical rule: **to change what an agent is born as, write
   `StartingScript` from the attribute-generation hook; to change what it
   is doing right now, write `ActiveScript` and `$Reset_Tasks`.**

Two shipped defects not to copy: the branch-4 and branch-1' comments both
say "The curse is broken - just run your QuestScript" when branch 4 is
actually the *un*-broken curse's lucky roll; and `boolean Effector;` is
declared and never used.

### 18.5 The hooligan trio — find/claim, follow, and the NPC's half of the deal

`Hooligan_Check` + `Arrest_Hooligan` + `travel_to_arrest` (lines 264-380)
are a complete **"heroes pursue a fleeing NPC and escort it home"**
mechanism, and the NPC's counterpart behavior is
`GPL/TaskModules/Characters/Henchmen/hooligan.gpl` (read in full;
`mx_hooligan.gpl` is the same). Together they are the best clonable
template in this batch for any "capture/rescue/collect a wandering NPC"
objective. One line of plot: it's the Wizard's Curse quest's arrest-the-
apprentices objective.

#### `Hooligan_Check` — find a target and *claim* it

```gpl
$ListObjects (ThisAgent, "Hooligan", -1, Hooligans);
Foreach Hooligan in Hooligans do
    If (Hooligan's "Special_Boolean" == False)
        If ($Is_Free_Task (ThisAgent, $Arrest_Hooligan, Hooligan))
            begin
                $SpecifyIntent (ThisAgent, #intent_arresting_hooligan);
                ThisAgent's "Target" = Hooligan;
                flag = True;
            end
return Flag;
```

Three reusable mechanisms:

1. **`"Hooligan"` is an object *type* you can query with
   `$ListObjects`.** Not `"hero"`, not `"monster"` — the type string comes
   from the unit's own `.dat` entry. Add this to §17.5's list of
   non-obvious type names (`"color"` for signs, `"special_item"` for
   chests, `"Hidden"` for the captive peasant in 18.9, `"Special"` for the
   ring site). **Whenever you add a quest NPC, its `type` field is the
   query key other scripts will use to find it** — pick a distinctive one
   and the "find my quest objects" query becomes one call with no title
   filtering.
2. **`$Is_Free_Task(agent, function Intention, agent Target) → boolean` is
   a generic task-contention resolver, and it is the single most reusable
   primitive in this batch.** Defined `GPL/LowLevel.gpl` lines 1258-1297
   (read in full). It lists own-player heroes within
   `#Is_Free_Task_Range` (2000, `globals.gpl` line 800), and for each one
   whose **`ActiveScript` *or* `BackScript` equals the passed function
   pointer** *and* whose `Target` is the same target, compares distances:
   if the caller is farther away it returns FALSE; otherwise it counts the
   competitor. It finally returns TRUE only if the count is
   `<= #is_free_task_max_heroes` (2, `globals.gpl` line 802). **So the
   built-in policy is "closest hero wins, but up to 2 more may pile on."**
   Passing the *intention function pointer* is what makes it generic —
   any custom behavior you write becomes claimable by passing `$MyBehavior`
   as the `Intention`. No registry, no bookkeeping, nothing to clean up on
   death.
3. **The NPC-side latch is `Special_Boolean`** (18.2), checked here and
   set by the NPC itself in `hooligan.gpl` line 59 once it notices it's
   been spotted. **Two independent "don't double-target this" mechanisms
   layered:** a per-target latch owned by the target, plus per-claimant
   distance arbitration. Note the shipped loop has no `break`, so it keeps
   iterating and the *last* eligible hooligan in the list wins the
   `Target` assignment — harmless but not what the code reads like.

#### `Arrest_Hooligan` — the follow-a-moving-target loop

This function is a **near-verbatim clone of the shipped generic follow
behavior** `Follow_Heal` (`GPL/TaskModules/Characters/Follow_Heal.gpl`
lines 8-69) — compared side by side, the skeleton is identical and only
two things differ: the range constant (`#Arrest_Hooligan_Dist` 50,
`globals.gpl` line 676, vs. `thisagent's "castingrange"`) and what
happens once in range (nothing, vs. cast a heal). That makes the skeleton
a confirmed *template*, not a one-off:

```gpl
target = ThisAgent's "Target";
if ($notvalid(target))            $reset_tasks(thisagent);
else if ($haslowHP(thisagent))    $Heal_Self(ThisAgent);
else if ($DistanceBetweenAgents(ThisAgent,Target) > <RANGE>)
    begin
        ThisAgent's "Destination"  = $LocationOf (Target);
        ThisAgent's "ActiveScript" = $Travel_to_arrest;   // travel variant
        ThisAgent's "BackScript"   = $Arrest_hooligan;    // ← itself
        $Move (ThisAgent, Target);
    end
else
    if ((thisagent's "evaluationscript")(thisagent) == FALSE)
        begin
            thisagent's "counter" += 1;
            if (thisagent's "counter" >= #followBored)
                begin
                    $move(thisagent,$randomcoord(thisagent,150));
                    thisagent's "counter" = 0;
                end
        end
```

- **The handler installs *itself* as its own `BackScript`,** producing a
  re-entrant chase: travel → arrive → re-measure → travel again. That is
  the whole "follow a moving target" mechanism; there is no follow
  primitive.
- **`$notvalid(target)` → `$reset_tasks` is the mandatory first line** of
  any behavior that holds a target across ticks.
- **`#followBored` (20, `globals.gpl` line 838) + `thisagent's "counter"`
  is the shipped anti-crowding idiom,** and the authors' comment explains
  why it exists: "if too many, I am bored, and move out of the way, in
  case I am trapping the guy I am following." **Any follow/guard behavior
  needs this** or the follower physically blocks the followed unit. 20
  ticks at `#Normal_Cycle` 300 ≈ 6 seconds. `counter` is a declared
  prototype field (`hero` line 94, `monster` line 237, comment: "Exactly
  what it says it is") — reset it when you *start* the behavior
  (`Be_Dumb` does: `thisagent's "counter" = 0` before assigning), because
  it's shared scratch.
- **`(thisagent's "evaluationscript")(thisagent)` is called for its
  boolean return, as a "did something more urgent preempt me?" test.**
  This is the indirect-call form §17.5 documented, used here as a
  *guard*: only idle-shuffle if the evaluation script did not redirect the
  hero. Every travel/follow function in the codebase routes threat
  reaction through this slot rather than calling
  `$eval_enemies_nearby` directly (the direct call is commented out in
  both `travel_to` and `travel_to_arrest`) — **so overriding one agent's
  `EvaluationScript` changes its threat response everywhere at once**
  (18.6).

#### `travel_to_arrest` — cloning a travel variant

Lines 357-380. It is `travel_to` (`Travel_to.gpl` lines 8-37) minus one
call: the `$Eval_Items_Nearby(ThisAgent)` step is gone, and the header
comment says why — "This is the travel_to for arresting hooligans. It
doesn't eval for items nearby." The family now has four confirmed
members with a clear axis:

| Variant | Evaluates threats? | Picks up items? | Clears hostiles? |
|---|---|---|---|
| `travel_to` | yes (`EvaluationScript`) | yes | no |
| `travel_to_exp` | yes | yes | no (+ awards `#explore_exp` on arrival) |
| `travel_to_arrest` (this file) | yes | **no** | no |
| `travel_to_safe` | **no** | no | yes, explicitly |

**Writing a new travel variant is a 10-line copy with steps removed** —
that is the sanctioned way to make a unit ignore distractions while on a
quest errand, and it keeps `has_arrived`'s `BackScript` relay intact for
free. Also note both `travel_to` and `travel_to_arrest` end in an empty
`begin end` block: the nested `if`s exist purely for short-circuit
sequencing, an odd but shipped style.

#### The NPC's half (`hooligan.gpl`) — flee-on-detection and self-despawn

Worth reading as the counterpart contract, because it shows what the
*target* of an escort objective has to do:

- **`Hooligan_Basic`** wanders around a remembered coordinate
  (`$RandomCoord(ThisAgent's "coord_home", SightRange *
  #Hooligan_Wander_Mod)`, mod = 3, `globals.gpl` line 423) with a 2%
  chance per tick of playing `thisAgent's "Idle_action"` instead —
  **`"coord_home" + a wander radius multiplier` is the generic
  "stay-in-this-area patrol"**, and `Coord_Home` is a declared `monster`
  prototype field ("holds the coord home for all monsters that use it (ie.
  Guardians and Offmap Sleepers)").
- **Detection is mutual and cheap:** it lists nearby heroes and accepts
  only those where `Hero's "Target" == ThisAgent` — i.e. **the NPC detects
  intent by reading the pursuer's `Target`, not by proximity alone.**
- On detection: `$StopMoving`, `$MessageFlag(ThisAgent,
  #message_found_hooligan)`, set `Special_Boolean = True`, and switch its
  own `ActiveScript` to `$Hooligan_Goto_Palace`. **So the "escort" is
  implemented as the NPC walking itself home** — no leash, no attach, no
  per-tick following by the hero. That is much less code than a real
  escort and is the pattern to copy.
- `Hooligan_Goto_Palace` does `$Hide(ThisAgent, Palace)` → on
  `$IsHidden`, checks whether it was the last one of its type
  (`$ListObjects(Palace,"Hooligan",-1,…)` size 0), and if so sets
  `AIRootAgent's "Quest_Flag_2" = True` + `$MessageFlag(Palace,
  #message_arrested_all_hooligans)`, then **releases every hero still
  chasing**:

  ```gpl
  Foreach Hero in Heroes do
      If (Hero's "ActiveScript" == $Arrest_Hooligan || Hero's "BackScript" == $Arrest_Hooligan)
          $Reset_Tasks (Hero);
  ```

  **Comparing script pointers to identify "who is doing X" is a
  first-class technique** (same shape as `Is_Free_Task`'s test and §17.1's
  `Monster's "BasicScript" != $Rooted_Guardian` check) — and **checking
  both `ActiveScript` and `BackScript` is required**, because a hero
  mid-travel has the behavior in `BackScript` only. **Any objective that
  can end while agents are still pursuing it must do this sweep**, or
  heroes keep running a behavior whose target no longer exists.
- Finally `$DeleteGamePiece(ThisAgent)` — the NPC removes itself once
  inside. See 18.9.

**Wiring note (the data-side half):** the Hooligan's own behavior slots
are **not** assigned in GPL at all — they come from its unit-type record
in `GPL/Monster_Data.dat` lines 603-608 (`mx_Monster_Data.dat` 960-965):
`(activeScript hooligan_basic)`, `(basicscript hooligan_basic)`,
`(backscript hooligan_basic)`, `(birthScript hooligan_birth)`,
`(IGdeathscript hooligan_death)`, alongside `(Guardian_Mod 3)`. This is
the same `.dat` script-binding mechanism §3 and §15 documented for
`visited_script` and `evaluationScript`, here binding a **whole quest
NPC's behavior set declaratively** — so a new quest NPC needs zero GPL
wiring at spawn time if you add a `.dat` entry for it. The spawn itself is
plain `$SpawnUnit(Hut, "Hooligan")` from every enemy `General_Housing`
(`epic_quest_scripts.gpl` lines 3761-3789, with an alternating
guaranteed/75%-chance pattern — a neat "roughly half the houses, but never
zero" trick).

### 18.6 `Guardian_Hero_Tree` + `Guardian_hero_Eval_Nearby` — a minimal decision tree and a custom leash

These two (lines 389-441) are the answer to "how do I make a hero-class
unit that acts like a stationary guardian instead of an adventurer" — and
they are the concrete demonstration that **§15's class decision trees are
replaceable wholesale by a much shorter cascade of the same shape.**

`Guardian_Hero_Tree` is a §15-shaped cascade with most modules removed:

```gpl
$createeffector(thisagent,"thought_bubble_think",#think_bubble_time);
$SpecifyIntent (ThisAgent, #Intent_Thinking);

if ($Check_nearby(thisagent) == False)
if ($Defend_home(thisagent) == False)
if ($rest(thisagent) == False)
//if ($combat_wandering_heroes(thisagent,75) == False)
if ($Go_Home(thisagent,85) == False)
    begin
        $SpecifyIntent (ThisAgent, #intent_wandering);
        thisagent's "counter" = 0;
        thisagent's "activescript" = $hero_wander;
    end
```

Compared against §15's finding that all 15 shipped class trees call
`$check_nearby`, `$Check_rewards` and `$rest` without exception, this
tree **omits `$Check_rewards` entirely** — so a guardian hero never
responds to reward flags — and keeps only home defense and rest before
falling through to `$hero_wander`. Four transferable points:

1. **The cascade needs no framework.** It's a chain of
   `if (module(agent) == False)` with the fallback in the innermost
   block; nothing registers modules and nothing enumerates them. **Your
   custom tree can call any subset of the shipped modules in any order**,
   which is what makes "a hero that behaves like a monster" a 15-line
   function.
2. **`$Go_Home(thisagent, 85)` and the commented
   `$combat_wandering_heroes(thisagent, 75)` take a numeric argument** —
   consistent with the percentage-chance module arguments §15 documented.
   Tuning "how homebound is this unit" is one integer.
3. **The thinking effector + intent pair at the top is cosmetic
   bookkeeping** (`"thought_bubble_think"` for `#think_bubble_time` =
   1000, `globals.gpl` line 526) — copy it so a custom tree's units still
   display the normal thought bubble, or omit it deliberately.
4. **The `#intent_wandering` + `counter = 0` + `activescript =
   $hero_wander` triple is the standard hand-off to the shipped wander
   behavior** — note it resets `counter` first, because `hero_wander`
   shares that scratch field with the follow/bored logic in 18.5.

`Guardian_hero_Eval_Nearby` is the *other* half, and it is the more
valuable finding: **a per-agent override of the shared threat-response
slot, used to implement a leash.**

```gpl
If ($listsize(thisagent's "Hostiles") == 0)   return FALSE;

if ($isvalidgamepiece(thisagent's "home"))
    begin
        if ($distanceBetweenCoords($locationof(thisagent),$locationof(thisagent's "home")) > 500)
            begin
                $flee(thisagent,#intent_flee_scared);
                return TRUE;
            end
        else
            return $eval_enemies_nearby(thisagent);
    end
else
    return $eval_enemies_nearby(thisagent);
```

- **This is the `EvaluationScript` slot §15 documented (bound per class in
  `Hero_Data.dat`), overridden on one instance from a quest setup
  function** — `epic_quest_scripts.gpl` line 3847,
  `E_Wizard's "EvaluationScript" = $guardian_hero_eval_nearby`. Because
  `check_nearby` and every `travel_to`-family function call this slot
  indirectly (§15, 18.5), **one assignment changes that unit's threat
  reaction across all of its behaviors at once.** That is the cheapest
  possible "this unit fights differently" knob.
- **The leash itself is 3 lines**: if farther than 500 from `"home"`,
  `$flee(thisagent, #intent_flee_scared)` — i.e. **`$flee` toward home is
  how you implement a tether**, and returning `TRUE` tells the caller
  "I handled it, stop deciding," which suppresses the normal combat
  reaction. Reusable directly for guard posts, garrisons, or any
  "don't chase off the map" behavior.
- **`$isvalidgamepiece(agent)` before dereferencing `"home"`** is the
  standard guard (same primitive §16.2's `VictoryCondition_Three` uses on
  palaces).
- **The hardcoded 500 is this function's one weakness, and the shipped
  monster equivalent is data-driven instead.** `Guardian.gpl` computes the
  same leash as `SightRange * ThisAgent's "Guardian_Mod" +
  #ATTRIB_MaxAttackRange` (lines 127 and 240), where `Guardian_Mod` is a
  declared `monster` prototype field (`prototype.gpl` line 212) set
  per-unit-type in `Monster_Data.dat` (usually 5) and overridable in GPL.
  **For a new leashed unit, prefer the `Guardian_Mod × sightrange` form** —
  it scales with the unit's own stats and is tunable from data. See 18.11.
- **Shipped defect: the last three lines are unreachable.** The
  `$clearlist(thisagent's "Hostiles")` and `return True` after the
  if/else are dead code — every path already returned. So **the hostiles
  list is never cleared by this evaluation script**, unlike
  `travel_to_safe` which clears it explicitly. Whether that leaks stale
  hostiles for a guardian hero is **UNVERIFIED** (no reader of a stale
  entry was traced), but do not copy the dead lines expecting them to run.

**The full wiring site is worth quoting because it shows the whole
"retype an existing map unit into a quest guardian" recipe**
(`epic_quest_scripts.gpl` lines 3838-3852, inside `WIZARDS_CURSE()`):
find the unit with `$ListObjects` + `$ListTitles`, then assign all four
behavior slots + `EvaluationScript` + a `BirthScript`
(`$High_Level_Hero_Birth`, which itself branches on `Quest_Number`). The
neighbouring block (lines 3818-3835) does the same trick in the opposite
direction on a `White_Wolf`: sets `"Type" = "Hero"`, `"Subtype" =
"Controlled"`, `"EnemyType" = "Monster"`, `"Guardian_Mod" = 2`, all four
slots to `$Guardian`, `BirthScript = $Guardian_Birth`, then
`$LearnSpell` ×2 and `$SetAttribute(#ATTRIB_ExperienceLevel, 10)` with
the comment "Set the Varg's level to 10 so that he actually learns the
aforementioned spells." **Two reusable facts there: `Type`/`Subtype`/
`EnemyType` are writable plain strings that redefine what a unit *is* to
every list query and targeting check, and `$LearnSpell` silently depends
on the unit's level being high enough** — set the level first.

### 19.10 The conditional-resurrection boss pair (what makes Darkness Falls' victory test work)

`DARKNESS_FALLS` seeds two named bosses into two random tombs (19.7) and
then wins on `$IsTitleAlive` being false for both (19.5). The mechanism
that makes that a *puzzle* rather than a checklist lives in
`GPLMx/mx_Monster_Deaths.gpl` — `Wight_Res_or_Die` (lines 247-295), read
in full. It is a new death-handling shape, distinct from both §8's
gravestone/revival and §18's respawn-by-rebirth:

```gpl
// installed by the wight's death script, which also does:
//   thisagent's "Activescript" = $Wight_Res_or_Die;
//   $setthreadinterval (thisagent's "ActiveScript", #wight_gravestone_interval);
//   $performaction (thisagent, "basic_death", thisagent);

If (ThisAgent's "Title" == "Styx")  Ally = "Stones";
Else                                Ally = "Styx";

$ListObjects (ThisAgent, "Lair", -1, Lairs, #CheckTitles, "WightsTomb");

if (($IsTitleAlive (ThisAgent, Ally) == False) && $ListSize (Lairs) == 0)
    begin
        thisagent's "type" = "Waiting_to_die";
        $killthread (thisagent's "activescript");
        $deletegamepiece (thisagent);
    end
Else
    begin
        $ClearEngineDeathFlags ( thisagent );
        $SetAttribute (ThisAgent, #ATTRIB_HP, $GetAttribute (ThisAgent, #ATTRIB_MaxHP));
        ThisAgent's "Type" = "Monster";
        $Reset_Tasks (ThisAgent);
        $SetThreadInterval (ThisAgent's "ActiveScript", #Normal_Cycle);
        $Say (ThisAgent, "VFX_Special2");
    end
```

Five reusable pieces:

- **`$ClearEngineDeathFlags (agent)` is the primitive that makes
  resurrect-in-place possible.** No GPL definition exists, so it's
  engine-side. This is the missing counterpart to §18's open question
  about HP-zero vs. deletion: **a dead agent is recoverable if you clear
  the engine's death flags, restore HP, and put `"Type"` back to
  `"Monster"`** — no new agent, no re-spawn, so the unit keeps its
  identity (and therefore its `"Title"`, which is what `$IsTitleAlive`
  tests).
- **`"Type"` is the switch the rest of the game reads.**
  `"Waiting_to_die"` immediately before `$deletegamepiece`,
  `"Monster"` on revival. §8 and §18 both noted `Type = "Dead"` for
  gravestones; this adds a third and fourth value and shows the field
  being used as a lifecycle state machine rather than a classification.
- **The death script converts the corpse into a timer.** It sets
  `ActiveScript` to the res-or-die handler and retunes the interval to
  `#wight_gravestone_interval`, then plays `"basic_death"`. **So "wait N
  seconds, then decide whether to come back" needs no new thread — reuse
  the dead unit's own script slot.**
- **The revival condition is a two-part world-state test**: the ally is
  gone AND no tombs remain. So killing one boss is pointless while the
  other lives or any tomb stands — which is precisely why the quest's
  victory poll is two-stage (19.5b).
- **`#wight_gravestone_interval` is declared twice with different
  values** — `mx_Globals.gpl` line 1042 says **80000**,
  `GPLMx/MajCompatibility.gpl` line 103 says **120000**, both with the
  identical comment "duration that Wight's gravestone last for in
  Darkness Falls. After this, they may ress." Which one the compiler
  keeps is **UNVERIFIED** — it's a duplicate-`expression` collision across
  two files that are both in the mx build (§14 already noted
  `MajCompatibility.gpl` as a home for constants you'd expect in
  `mx_Globals.gpl`, e.g. `#Min_Dist_To_Palace_for_Outpost` at its line
  95). Flagged because a modder redefining a constant needs to know that
  duplicates apparently compile rather than erroring.
- Minor: **`$Say (agent, "VFX_Special2")`** on revival — a second
  audio-trigger primitive alongside `$PlaySound`, taking a cue name
  directly on the agent.

### 20.3 Heroes as quest content: enemy-hero bosses, and hero↔monster AI crossover

§19's four quests built everything out of lairs and monsters. All the
genuinely new material in this file comes from doing it with **heroes**
instead, on both sides of the line.

#### (a) An enemy hero as a boss — five writes, no new unit type

`SCIONS_CHAOS` lines 349-357 promote a pre-placed enemy hero into the
quest's first boss:

```gpl
$listobjects(palace,"hero",-1,guys,#NotMyPlayer,#NoHiddenMap);
guy = $listmember(guys,1);
$advance_to_level(guy,35);
$adjustattribute(guy,#ATTRIB_MAXHP,100);
$adjustattribute(guy,#ATTRIB_HP,100);
guy's "title" = "Scion";
guy's "resist_critical" = TRUE;
```

Repeated for scions #2 and #3 (lines 405-410, 474-477) with a
freshly-`$SpawnUnit`ed `"Cultist"` / `"Warrior_of_Discord"` instead of a
pre-placed one, so the recipe is confirmed three times in the same
function. Four things are new relative to §19.9's elite-NPC stat stack:

- **`#ATTRIB_MAXHP` and `#ATTRIB_HP` must BOTH be adjusted, by the same
  amount.** Raising the ceiling doesn't fill the bar. Every one of the
  three sites does the pair; the level-35 scion gets +100/+100, the
  mid-quest one +200/+200.
- **`"title"` is writable on a live agent, and that is what boss identity
  is made of.** `#CheckTitles`, `$ListTitles` and §19.5a's
  `$IsTitleAlive` all key off this string, so retitling an ordinary unit
  makes it findable as a unique named thing. **Caution, flagged as
  inference not fact:** other systems re-derive a *unit type* from
  `"title"` (§19.7's `$AutoSpawn_Lair` does `$SpawnUnit(ThisAgent,
  ThisAgent's "Title")`, and `$rescue_buildings` in 20.4 branches on
  title strings), so retitling something that will later be asked to
  reproduce itself is a real hazard. Heroes don't self-spawn, which is
  why it's safe here.
- **`resist_critical` — new field, and its reader is traced.** Declared
  `Boolean resist_critical; // does this guy resist critical hits?
  (reduce their damage)` on both hero and monster prototypes
  (`GPLMx/mx_prototype.gpl` lines 119 and 222; base `GPL/prototype.gpl`
  87 and 177). The consumer is the attack resolver,
  `GPLMx/TaskModules/Subtasks/mx_make_attack.gpl` lines 194-198 and
  237-241 (base `GPL/TaskModules/Subtasks/make_attack.gpl` 315-319 and
  343-347), identical in both:

  ```gpl
  dmg = $getattribute(defender,#ATTRIB_MAXHP);   // a crit is an instant kill
  critical_effect = TRUE;
  if ($hasattribute("resist_critical",defender))
      if (defender's "resist_critical" == TRUE)
          dmg = dmg / 6;                          // …unless you resist
  ```

  **So a critical hit in Majesty is coded as "damage equal to the
  target's MaxHP," and `resist_critical` divides that by 6 rather than
  negating it.** That is the whole reason a boss needs the flag: without
  it, any lucky crit deletes it regardless of the HP bump above. Two
  reusable facts fall out — critical damage is MaxHP-relative (so bumping
  MaxHP does *not* help against crits), and the read is wrapped in
  §14's `$HasAttribute` reflection guard, i.e. the field is treated as
  optional and defaults to "no resistance" when absent.
- **The whole boss chain is `$List..`-count-driven, not death-hook
  driven.** No `IGDeathScript` anywhere in this quest; the poll just
  counts enemy heroes. Which is exactly why it needs 20.5's
  latch-on-appearance guard.

#### (b) `$make_raider` on heroes and peasants — and the shipped comment that blesses it

`URBAN_RENEWAL`'s two death hooks convert **hero-type agents** to monster
AI:

```gpl
// urban_guild_destroyed, lines 698-706 — third guild-loss event
$listobjects(thisagent,"Hero",-1,things,#MyPlayer, #CheckSubtypes, "Hero");
foreach thing in things do
    begin
        $make_raider(thing);
        thing's "evaluationScript" = $Monster_eval_enemies;
    end
```

```gpl
// urban_crime_spot_destroyed, lines 756-768 — "the peasants are revolting!!!"
things = $listtitles(things,"Peasant");
foreach thing in things do
    begin
        $adjustattribute(thing,#ATTRIB_Weapon_basic_Damage,10);
        $adjustattribute(thing,#ATTRIB_Strength,10);
        $adjustattribute(thing,#ATTRIB_HtoH,55);
        $adjustattribute(thing,#ATTRIB_MaxAttackRange,5);
        $adjustattribute(thisagent,#ATTRIB_ActionRateModifier, -300);   // ← bug, see 20.5
        $make_raider(thing);
    end
```

**This is sanctioned, not a hack that happens to work.** The evidence is
in the prototype itself: `GPLMx/mx_prototype.gpl` line 170 declares, on
the **hero** prototype, `boolean Raider_respond; // jim hackerama so
heroes can become raider mosnters` (typo shipped; identical in base
`GPL/prototype.gpl` line 138, and the monster prototype's own copy at
mx line 253 carries a different comment about responding to being
attacked mid-building-attack). So the field exists on heroes for exactly
this purpose. **Practical upshot: "hostile NPC heroes" needs no new unit
type, no `#force_*` value and no artifice — one `$make_raider` call per
agent.** Note both call sites use `#MyPlayer` *relative to the dying
enemy building*, so the converts are the enemy player's own heroes and
peasants, not the player's.

#### (c) Filling in §19.6's blank "Installs" column

§19.6's dispatch table left the installer bodies for `#force_raider` /
`#force_caravan_raider` / `#force_guardian` / `#force_bomber` blank.
Read directly (`GPLMx/mx_Monster_Births.gpl` lines 769-825) they are all
the same three-slot idiom §19.6 documented, so the table can be
completed:

| Installer | Slots (`ActiveScript`/`BasicScript`/`BackScript`) | `EvaluationScript` | Extra |
|---|---|---|---|
| `make_raider` (769) | `$raider` | `$monster_eval_enemies` | `"Raider_respond" = TRUE` |
| `make_caravan_raider` (784) | `$caravan_raider` | `$monster_eval_enemies` | `"Raider_respond" = TRUE` |
| `make_guardian` (798) | `$guardian` | `$monster_eval_enemies` | `$find_guardian_home(thisagent)` |
| `make_bomber` (812) | `$Bomber` | `$monster_eval_enemies` | — |

**Consequence for the code in (b): `thing's "evaluationScript" =
$Monster_eval_enemies` is redundant** — `make_raider` set that exact
value one line earlier. Harmless, but don't copy it thinking it's
required. (This was flagged as a lead worth chasing; the answer is that
it is a no-op duplicate, not a new mechanism.)

### 21.6 `SIEGE`: a complete AI opponent kingdom written in GPL

The single most valuable thing in this batch. §16.2 and §19.8 showed
*hostile* player slots; §20.6 showed hijacking an enemy player's
buildings. `SIEGE` goes all the way: **player 2 is a functioning kingdom
that recruits heroes on a budget, casts its own building spells, places
reward flags to direct its heroes at your city, researches its upgrades,
runs trade caravans, and surrenders when broke — and every line of that is
GPL in this one file.** Nothing about it is engine AI.

The brain is four threads (21.1) and one priority cascade,
`Enemy_Actions` (lines 1512-1547):

```gpl
gold = $GetPlayerData ( palace, "gold" );
$NewThread ( AIRootAgent's "SpecialSpawnScript2", ( $RandomNumber(10000) + 5000 ));
if ( gold > 2000 )
    begin
        if ( $Check_Lightning_Defense ( palace ) == FALSE )
            if ( $Check_Resurrect ( palace ) == FALSE )
                if ( $Check_Heal ( palace ) == FALSE )
                    $Post_Enemy_Reward ();
    end
else
    begin   // out of money: surrender
        $minimapanimation ( palace, "Event_beacon" );
        AIRootAgent's "Permanent_Hostility" = FALSE;
        $setplayerteamnumber ( palace, $neutralteamnumber() );
        $SiegeOutOfMoney ();
    end
```

**That cascade shape is exactly §15's hero decision tree —
`if ($module(...) == FALSE) if ($next(...) == FALSE) ...` — applied at the
kingdom level.** Each check returns TRUE when it spent the turn, so the
whole AI is "try the most valuable action, fall through to the cheapest."
It also **reschedules itself first**, before doing any work, which is the
safe ordering if a branch might `return` (compare 21.4's spire functions).

#### (a) The hostility model, and what `Permanent_Hostility` actually gates

`SIEGE`'s setup is two lines (1263-1264):

```gpl
$SetPlayerTeamNumber ( EnemyPalace, $NewTeamNumber () );
AIRootAgent's "Permanent_Hostility" = TRUE;
```

The second line's reader was traced: `check_revert_teams`
(`GPLMx/DecisionTrees/Modules/mx_check_rewards.gpl` lines 339-380; base
twin `GPL/DecisionTrees/Modules/check_rewards.gpl` lines 333-374, same
guard at its lines 343-346). Read in full, it does:

```gpl
if ( $HasAttribute ( "Permanent_Hostility", AIRootAgent ))
    if ( AIRootAgent's "Permanent_Hostility" == TRUE )  return;      // ← the gate
reset_team = TRUE;
$listobjects ( thisagent, "rewardFlag", -1, flags, #rewardflags, #Myplayer, #NoHiddenMap );
foreach flag in flags do
    if ( flag's "title" == "flag_attack" )
        begin
            target = $agentnumber ( $getattribute ( flag, #ATTRIB_targetID ));
            if ( $isvalidgamepiece ( target ))
                if (( $getunitplayernumber(target) != flagplayer )
                 && ( $getunitplayernumber(target) != #monster_player ))
                    reset_team = FALSE;
        end
if ( reset_team ) $setplayerteamnumber ( thisagent, $neutralteamnumber() );
```

**So the shipped PvP model is: placing an attack reward flag on another
player's unit is what makes your kingdom hostile, and removing your last
such flag automatically reverts you to the neutral team — unless
`Permanent_Hostility` is TRUE.** This is called from the reward-flag
removal path, i.e. it runs every time a flag goes away. Three consequences
a quest author needs:

- **A quest that forces a war must set `Permanent_Hostility`, or the war
  will end by itself** the moment the aggressor's flags are cleared.
  §16.2's deathmatch splitter and §19.8's `CLASH_EMPIRES` never had to
  care because their combatants are monster-player lairs; `SIEGE` is
  player-vs-player, so it does.
- **Peace is `Permanent_Hostility = FALSE` + `$SetPlayerTeamNumber(p,
  $NeutralTeamNumber())`**, exactly as `Enemy_Actions`' surrender branch
  and `Siege_Palace_Death` both do. `$NeutralTeamNumber` was already
  documented (§18's quest-cleanup table); what's new is that the boolean
  must be cleared too, or the neutral assignment is fighting a system that
  wants it hostile.
- **`flag_attack` is a reward-flag title**, and `$AgentNumber($GetAttribute
  (flag, #ATTRIB_TargetID))` is the standard "what is this flag pointing
  at" conversion (many sites in `check_rewards.gpl`; also §9's Zoo).

#### (b) The AI places reward flags — `$PlaceRewardFlag`, and this file is its only call site

`Post_Enemy_Reward` (1753) → `FlagEconomicTarget` (1808) /
`FlagGuildTarget` (1870) / `FlagClosestBuilding` (1930). All three are the
same five steps, so the recipe is confirmed thrice:

```gpl
if ( $CountPlacedFlags ( palace ) < 1 )                  // 1. one flag at a time
…
$ListObjects ( palace, "building", -1, buildings, #NotMyPlayer );
t1 = $RemoveTitles ( buildings, "marketplace" );          // 2. pick a target class
t2 = $ListTitles  ( buildings, "trading_post" );
targets = $AddLists ( t1, t2 );
flagtarget = $ListMember ( targets, 1 );                  // 3. nearest, by hand
distance   = $DistanceBetweenAgents ( palace, flagtarget );
foreach target in targets do
    begin
        newdistance = $DistanceBetweenAgents ( palace, target );
        if ( newdistance < distance ) begin flagtarget = target; distance = newdistance; end
    end
if ( levels < 30 ) gold = 100; … else if ( levels >= 75 ) gold = 1000;   // 4. price it
if ( $IsValidGamePiece ( flagtarget ))
    flag = $PlaceRewardFlag ( flagtarget, #Player_2, gold );             // 5. place
if ( flag != $nullagent ())
    AIRootAgent's "AI_Reward_Flags" << flag;
```

Findings:

- **`$PlaceRewardFlag (targetAgent, #Player_N, goldValue) is agent` — new
  to this guide, engine-side** (present in the SDK compiler keyword list's
  `Keywords4`, no GPL definition), and **`Quests_3.gpl` contains its only
  three call sites in the entire corpus.** Normally the player's UI places
  flags; this proves GPL can, for any player number, at any value. It
  returns the flag agent, or `$NullAgent()` on failure — the `!=
  $nullagent()` test is the shipped guard.
- **The bounty scales with the AI's army strength** (21.4b's summed hero
  levels), 100 gold at <30 up to 1000 at ≥75, and the *decision* to flag
  at all is `$randomnumber(100)+1 < total_level`. **So an AI kingdom's
  aggression is one number: the sum of its heroes' levels.**
- **Target selection is three hand-written policies** — economy
  (`marketplace`/`trading_post`), guilds
  (`$ListObjects(..., #CheckSubtypes, "Guild")`), or nearest anything —
  chosen by a uniform `$RandomNumber(3)+1`. `$RemoveTitles` partitioning
  (§19.6) and the manual nearest-search loop are the same idioms used
  elsewhere; **there is still no sort primitive**, and
  `$DistanceBetweenAgents` in a `foreach` is how this codebase finds a
  minimum.
- **Flags need explicit bookkeeping, and the list field is what makes it
  possible.** `Flag_Remover` (1422, on the `VictoryCondition` slot, every
  90-150 s) inspects **only the oldest** flag
  (`$ListMember(flags,1)`) and deletes it if its target is at full HP —
  the shipped rationale is "if that agent is in full repair it assumes
  that it has been unable to attack it effectively." It also drops
  entries whose flag failed `$IsValidGamePiece`. `End_Flag_Remover`
  (1455) sweeps every flag at game end via
  `$ListObjects(palace, "RewardFlag", -1, flags, #RewardFlags)`.
  **`#RewardFlags` is `$ListObjects` option 6** (`GPLMx/mx_LowLevel.gpl`
  line 1690, in the same enum as `#NoHiddenMap`/`#CheckTitles`) and is
  required to see flags at all — flags are not in the `"building"` or
  `"hero"` classes.
- **A one-flag-at-a-time AI needs no scheduler**: `$CountPlacedFlags`
  (1796, a local helper wrapping the same query with `#MyPlayer`) plus
  `Flag_Remover`'s eviction is the entire lifecycle.

#### (c) The AI casts *building* spells by calling the spell functions directly — and pays for them itself

`Check_Lightning_Defense` (1549), `Check_Resurrect` (1625) and
`Check_Heal` (1694) are one pattern:

| Step | Lightning | Resurrect | Heal |
|---|---|---|---|
| Building gate | `"Wizards_Guild"` with `building's "level" >= 2` | `"Temple_Krypta"` with `"level" == 3` | `"Temple_Fervus"`, any level |
| Target search | enemy heroes within **1200** of the guild; then a second query at radius **150** around the closest one | own `"dead"`-class agents, highest `#ATTRIB_ExperienceLevel`, must be > 4 | own heroes with `HP < MaxHP * 0.5` |
| Cast | ≥3 clustered → `$CreateSpellUnit(guild,"Lightning_Storm",ZapTarget)`; else 50%+ chance of `$lightning_bolt_hit(ZapTarget)` | `$Reanimate_Begin(ResTarget)` | `$Fervus_Heal_Effect(HealTarget)` |
| Cost | `$AdjustPlayerData(palace,"gold",-1600)` storm / `-400` bolt | `-2000` | `-400` |
| Return | TRUE after a storm (turn used), **FALSE after a bolt** ("AI MAY consider another action after throwing a bolt") | TRUE if it resurrected | TRUE if it healed |

Four findings:

- **`$Lightning_Bolt_Hit`, `$Reanimate_Begin` and `$Fervus_Heal_Effect`
  are the *player's* building-panel spells**, and their own headers say so
  verbatim: "player cast spell - from wizard's guild" / "from temple to
  krypta" / "from temple to fervus"
  (`GPLMx/TaskModules/Subtasks/mx_Spells.gpl` lines 2364, 4283, 3535;
  base twins `GPL/TaskModules/Subtasks/Spells.gpl` 269, 2018, 1348 —
  located, bodies not diffed). **So the building-cast pathway that
  `.kiro/steering/majesty-modding.md` and §11 flagged as having no
  data-only template is fully reachable from GPL: call the spell's own
  function on a target.** §19.9/§17.2 already showed calling a spell's
  `_Begin` to pre-buff a spawn; this is the same trick used to give an AI
  the player's entire building-spell arsenal.
- **The gold cost is *not* inside the spell function.** Every call site
  subtracts the price by hand with `$AdjustPlayerData`, and the values
  (1600/400/2000/400) are hardcoded here. **A GPL-cast building spell is
  free unless you charge for it** — which is convenient for scripted
  events and a trap for anyone simulating a player.
- **`building's "level"` is a readable integer field and the standard
  building-tier gate.** Three gates in this function set, matching §3's
  finding that Wizard's Guild's own `Obtain_Enchantment` gates on
  `ThisBuilding's "Level"`. Also used arithmetically in
  `mx_caravan.gpl` line 71 (`Gold_To_Give = $GetAttribute(ThisAgent,
  #ATTRIB_Gold) * Target's "Level"`), i.e. **a caravan's payout is
  multiplied by the receiving Marketplace's level.**
- **`$ListObjects(palace, "dead", -1, …)` is how you find corpses**, then
  `if ($IsDead(hero) == FALSE) dead_heroes -= hero` to drop anything that
  is in the class but alive. A fourth independent confirmation of §20.2's
  `"type"`-as-query-class finding, from the query side.

#### (d) RESOLVED (§20.6b): `$SpawnUnit` does **not** run `$Generate_Character_Attributes`

`Enemy_Guild_Spawn` (1473-1510) is the AI's recruitment loop, and it
carries the comment that settles §20.6b's open question. Verbatim
(lines 1490-1500):

```gpl
if ( gold > 800 )                                    // keep a reserve
    begin
        members     = $ListSize ( guild's "members" );
        max_members = $getattribute ( guild, #ATTRIB_MaxGuildMembers );
        if ( members < max_members )
            begin
                $AdjustPlayerData ( Guild, "gold", -600 );   // charge 600 per hero
                Type = Guild's "Member_Title";
                enemy_hero = $SpawnUnit ( Guild, Type, $LocationOf ( guild ));
                $Generate_Character_Attributes ( enemy_hero );
                // ↑ shipped comment: "This is necessary for heroes that are not
                //   generated via an interface call."
            end
    end
```

**§20.6b flagged as UNVERIFIED whether a script-spawned hero gets its
randomized attributes automatically, noting that `Hero_Generator`'s
explicit call "suggests not" but could be belt-and-braces. This comment
states the rule outright: it is necessary. A hero created by
`$SpawnUnit` must be passed to `$Generate_Character_Attributes` by hand.**
That is a second independent site plus an explicit statement of intent, so
the inference is now a confirmed rule. (What specifically is missing
without it — name, stat rolls, `StartingScript` — is still not enumerated
anywhere; see 21.10.)

Everything else in that loop is §20.6b's guild-membership field set
re-confirmed on a *different* player's guilds: `"members"` (live list),
`"Member_Title"` (what this guild recruits), `#ATTRIB_MaxGuildMembers`
(cap GPL must check itself). **Plus the new part: a budget.** The AI keeps
an 800-gold floor, pays 600 per hero, re-reads gold **inside** the loop so
it can stop mid-sweep, and re-threads itself at 30 s. That four-line
pattern is a complete "AI economy" and needs no new primitives.

#### (e) `SetEnemyResearch` — research flags are plain writable attributes (advances §3)

`SetEnemyResearch` (1992-2075) walks the AI's buildings once at quest
start and `$SetAttribute`s the research flags to 1 by title:

| Building | Flags set |
|---|---|
| `blacksmith` | `#ATTRIB_ResearchArmorLevel_2/3/4`, `#ATTRIB_ResearchWeaponLevel_2/3/4` |
| `marketplace` | `#ATTRIB_ResearchHealingPotions`, `#ATTRIB_ResearchRingsOfProtection`, `#ATTRIB_ResearchPowerfulItem` (shipped comment: "this is the amulet. :P") |
| `Magic_Bazaar` | `#ATTRIB_ResearchBazaar_Item_One..Four` |
| `guardhouse` | `#ATTRIB_ResearchArrows`, `#ATTRIB_ResearchGoodGuard` |
| `fairgrounds` | `#ATTRIB_ResearchTournament`, plus `#ATTRIB_CurrentEvent = 4` ("activate the building") |
| `library` | a **commented-out** block naming `#ATTRIB_ResearchTrainIntelligence`, `ResearchMagicResistance`, `ResearchWizardFireBlast_4`, `ResearchWizardMeteorStorm`, `ResearchEnergyBlast`, `ResearchFireShield` |

**§3 identified these `#ATTRIB_Research*` flags as read-gates in front of
every hero purchase/learn decision and left open how they get set,
observing only that "the player must UI-click to research." This confirms
the write side: they are ordinary engine attributes, settable from GPL
with `$SetAttribute`, on any player's building.** So a quest can hand a
kingdom (the player's or an AI's) a fully-researched economy in one loop —
or, inverted, a mod can pre-research a building to make a new item
purchasable without touching the UI. The commented-out library block is
also a free catalogue of the library's flag names.

`#ATTRIB_CurrentEvent = 4` on the fairgrounds is the one write here whose
meaning is only inferable from its comment ("Set fairgrounds research and
activate the building"); the event-index mapping is **UNVERIFIED**.

#### (f) `CheckSiegeMessage` — a 5×4 status-hint matrix, and a resettable score window

`CheckSiegeMessage` (1296-1384) is `TRADE_ROUTES`' grading table (21.3)
turned into pure feedback: every 6 caravans it **zeroes both scores** and
emits one of 20 messages chosen by a two-axis lookup — the player's
intercept differential (`victory - defeat`, five bands from ≤-4 to ≤4)
crossed with the AI's treasury (`$GetPlayerData(enemy_palace,"gold")`,
four bands). **The rolling-window trick is the reusable part: reset the
counters at the checkpoint and the score becomes "how are you doing
lately" instead of "cumulatively."** Contrast 21.3, which never resets
because its totals *are* the progress bar.

Also note it opens with `if ($IsDead(enemy_palace)) return;` — the
mandatory guard once a scorer can outlive its subject (the same
`$IsDead`/`$IsValidGamePiece` discipline §18/§20 documented).

One shipped defect: the `gold > 40000` band is tested **before**
`gold > 250000` in the first branch (lines 1329-1331), so the
250000 case is unreachable; the other four branches use a consistent
40000/25000/10000 ladder, and `250000` looks like a typo for `25000`.

#### (g) Shipped quirk: nullary functions called with an argument

`Check_Lightning_Defense`, `Check_Resurrect` and `Check_Heal` are each
declared `function X () is boolean` — no parameters — and each is called
as `$Check_Lightning_Defense ( palace )` (lines 1533-1535). All three
re-derive the palace internally via `$GetPlayerTwoPalace()`, so the
argument is dead. The same shape appears in §17.2's territory:
`Trade_Routes_Moderate_Event` calls `$Magical_Accident ( palace )` while
`CheckTradeVictory`'s commented-out debug block calls
`$Magical_Accident ()` with none.

**This compiled and shipped, so GPL evidently does not enforce argument
count at the call site** — but whether extra arguments are silently
discarded, or corrupt the call frame, is **UNVERIFIED** and would need a
test. Treat it as a bug to avoid, not a feature: match the declared
signature.

### 21.7 The phase-in/phase-out boss building (Fortress of Ixmil)

`FORTRESS_IXMIL` is "a dungeon that teleports around the map, attacks for
a while, then vanishes to heal." Everything about it is built from
primitives, and three of them are new argument forms rather than new
primitives.

**The parking mechanism.** `Warp_Out` (2499) and the warp-in half of
`Fortress_Ixmil_Warp_Engine` (2421) are exact inverses:

```gpl
// OUT (Warp_Out)                              // IN (Warp_Engine)
$hide ( fortress, marker,                      coord = $RandomCoord ( palace, 1000, 4500 );
        #TeleportInsideDestination );          $Unhide ( fortress, coord );
$Wither_Fortress_Grove ();                     $createeffector ( fortress,
$adjustattribute ( fortress,                        "Ixmil_Teleport_In_Effector", 7250 );
        #ATTRIB_HealingRateModifier, -3 );     $FadeIn ( fortress, 700 );
$KillThread ( fortress's "ActiveScript" );     $adjustattribute ( fortress,
$createeffector ( fortress,                         #ATTRIB_HealingRateModifier, 3 );
        "Ixmil_Teleport_Out_Effector", 7250 ); $Fortress_Ixmil_Spawn ();
$FadeOut ( fortress, 700 );                    $Spawn_Fortress_Grove ();
                                               $NewThread ( fortress's "ActiveScript", 500, fortress );
```

- **`$Hide (agent, destination, #TeleportInsideDestination)` — a third
  argument form on a documented primitive.** §18.3 documented
  `$Hide(agent, building)` as "walk in and be inside"; the third argument
  makes it **instant**. Its only two call sites in the corpus are this one
  and `GPLMx/TaskModules/Buildings/Mausoleum.gpl` line 75 (interring a
  dead hero), which §8 already described as a "`$hide`-teleport" —
  the constant is what does it. **`#TeleportInsideDestination` has no
  `expression` declaration anywhere in the corpus**, which places it in
  the same family as `#ATTRIB_*` (also undeclared — checked): **the `#`
  namespace includes engine-provided constants, not only GPL-declared
  ones**, so an unresolvable `#name` is not automatically a typo.
- **`$Unhide (agent, coord)` — a second argument form**, i.e. "reappear
  *there*." §14/§20.6 only had the one-argument `$UnHide(agent)`.
  Together the pair is the whole "park it off-map and redeploy it
  anywhere" mechanism, and the destination is an ordinary map decoration
  (a `"color"`-class obelisk retitled `"Fortress_Marker"` in
  `Set_Up_Fortress`, 2373 — §17's marker idiom).
- **`$FadeIn (agent, ms)` / `$FadeOut (agent, ms)` — new to this guide.**
  Five call sites total: three here, two in the teleport spell
  (`mx_Spells.gpl` lines 1693/1718 — fade out, move, fade in). Purely
  visual, and they pair with a duration-matched effector
  (`Ixmil_Teleport_*_Effector`, 7250 ms) that supplies the actual
  spectacle.
- **A building's gun is turned off by killing its `ActiveScript` thread
  and back on by re-threading the same slot** (`$NewThread(fortress's
  "ActiveScript", 500, fortress)`), never by reassigning the slot. §20.4
  found the same technique used to deactivate an outpost — but note the
  contrast: an outpost needed **five** named threads killed, a lair-class
  attacker needs one.
- **`#ATTRIB_HealingRateModifier` ±3 (base 4, set in `Set_Up_Fortress`)
  is how "it heals while it's away" is implemented**, plus a one-off
  half-damage refund on warp-out if `MaxHP - HP > 90`. So the boss's
  regeneration is an attribute toggled by the same function that hides it,
  and §17's "negative delta improves the rate" convention for that
  attribute holds here too (`+3` while active = slower healing).

**The grove: a spawn-group stored in a list field, and its teardown.**
`Spawn_Fortress_Grove` (2828) spawns 8 Strangleweed/Daemonwood around the
fortress and keeps them: `grovelist << $SpawnUnit(...)`, then `fortress's
"grovelist" = grovelist`. `Wither_Fortress_Grove` (2858) reads the field
back, and per member `$IsValidGamePiece` → effector + `$FadeOut`, then
`$ClearList (fortress's "grovelist")`.

- **`grovelist` is a declared prototype field** —
  `GPLMx/mx_prototype.gpl` line 430, shipped comment "used by the Fortress
  of Ixmil only" — i.e. **the codebase's answer to "remember what I
  spawned" is a per-agent list field**, and `$ClearList(agent's "field")`
  empties it in place. Generic recipe for any temporary spawn group
  (summons, escorts, event waves) that must be cleaned up together.
- **`"clear"` is a third `$SpawnUnit` string flag**, alongside §17's
  `"MaxHP"` and `"Override"`. Eight sites in the corpus: two here
  (grove members at `$RandomCoord(fortress,200,350)`) and six in
  `epic_quest_scripts.gpl`/`mx_Epic_Quest_Scripts.gpl` (caravans and
  bosses spawned at a specific coordinate — those files' contents are
  Batch G, only the flag occurrences were grepped). Every site spawns at a
  *precise* coordinate where something might already be, so "make room /
  ignore blockers" is the plausible reading, but the meaning is
  engine-side and **UNVERIFIED**.
- **`Shrubbery_Death` (2914) documents a real engine gotcha worth
  copying verbatim.** For a unit removed instantly rather than killed:
  ```gpl
  $stopmoving ( thisagent );
  thisagent's "type" = "Dead";
  // NLS BUGFIX2
  // need to do this to fix freeze spell gravestone bug
  $ResumeThread ( thisagent's "Activescript" );
  thisagent's "type" = "Waiting_to_die";
  $killthread ( thisagent's "activescript" );
  $deletegamepiece ( thisagent );
  ```
  **A suspended thread must be `$ResumeThread`ed before it can be killed
  and its agent deleted** — otherwise a unit that was frozen (§11's
  `$Freeze_Unit` does `$SuspendThread` on `ActiveScript`) leaves a stuck
  gravestone. The author's own comment ("there's probably some extraneous
  code in this, but I didn't want to screw with it too much for fear of
  awakening old 'death' bugs") is honest about the two `"type"` writes
  being belt-and-braces; the `$ResumeThread` is the load-bearing line.

**`$SuperBuff (agent)` — a ready-made permanent buff stack**, called on
every spawn of the spires' tier-4 wave (`Spire_Spawn_Four`, line 947).
Body in `GPLMx/TaskModules/Subtasks/mx_Spells.gpl` lines 7-60, header "//
Permanently buffs a unit with a number of the better spells. Only really
for use on monsters." It applies StoneSkin, AntiMagic, Blessing and
Vigilance, each guarded by its own `#ATTRIB_HasEffect*` flag (so it is
idempotent), each as an **effector with duration `-1`**:

```gpl
$createeffector ( thisagent, "dauros_stone_skin_icon", -1 );
$SetAttribute ( thisagent, #ATTRIB_HasEffectStoneSkin, 1 );
$adjustattribute ( thisagent, #ATTRIB_armor_basic_damage, 6 );
```

**`-1` is a fourth effector-duration form beyond §13's `0`, a positive
integer, and `1 + "Infinite"`** — used here for "never expires, no
callback." Exact engine semantics **UNVERIFIED**, but the intent is
unambiguous from the function's own header and the absence of any
`_End` pairing. Also note the stat pattern: `$MagicalAdjustAttribute` for
the to-hit/defence numbers (§14's magical-vs-plain split) and plain
`$AdjustAttribute` for damage/armour and the rate modifiers, plus
`$TurnOnSpeedTrail(thisagent, 2)` for Vigilance's visual.

---

## Chapter 5: Buildings as Quest Agents

Build gating, buildings that act on a timer, building death hooks, rescue/defection.

### 16.1 `CanIBuildThisBuilding()` — the one GPL-side placement-validation hook

`construction_rules.gpl` contains exactly one function:

```gpl
function CanIBuildThisBuilding (agent thisBuilding, list dependencies) is integer
```

**Return contract (from the file's own trailing comment, line ~143):**
"a 0 return value means OK to build, any non-zero value means don't
build." Every live branch obeys this — `return 0` on success, and on
failure a `#chat_*` constant.

**Who calls it: nothing in GPL.** A repo-wide `grep_search` for
`CanIBuildThisBuilding` returns only the two function definitions (base
+ mx) and one commented-out `$DebugOut` string inside each. There is no
`$CanIBuildThisBuilding(` call site anywhere in the `.gpl` tree, in any
quest file, or in any of our own mod GPL. **Conclusion: it is an
exe-invoked callback** — the engine calls this GPL function by name,
the same shape as other engine-called entry points in this codebase
(`Freestyle()`, birth/death scripts). **UNVERIFIED:** exactly *when* the
exe calls it — build-menu filtering vs. cursor-hover/placement-time
validation. The evidence leans placement-time, because the function
requires a positioned `thisBuilding` agent (`$ListObjects(thisbuilding,
...)` measures distance *from the candidate building's own location*),
which is meaningless for a menu-entry filter that has no position yet.
That's an inference from the argument usage, not a confirmed exe trace.
`SDK/Documentation/GPL Reference.pdf` may document the callback
contract, but it's a PDF and was not readable with the search/read
tools available in this pass.

**What `dependencies` actually receives: UNVERIFIED — and no shipped
code reads it.** Not one live branch in either the base or mx version
references the `dependencies` parameter. The only description of its
intended content is the commented-out design sketch at the end of both
files (base lines ~120-140):

```gpl
//	if ( $ListSize( dependencies ) > 0 )
//		if ( $DistanceBetweenAgents( theBuilding, $GetClosest( theBuilding, dependencies ) ) > theBuilding's "maxBuildRange" )
//			return 1; // too far away to build...
```

That sketch implies "a list of agents this building must be built near,"
plus a never-implemented per-building `"maxBuildRange"` attribute and a
never-implemented `theBuilding's "buildRequirements"` function-pointer
field (both appear ONLY inside these comments — grepped, zero live
references anywhere). No `M_Buildings.xml` field feeds it either: a grep
of `M_Buildings.xml` for `Depend`/`Prereq`/`Requir` returns zero
matches. So: the parameter exists in the signature, the engine presumably
passes something, and **nothing in the shipped data or script layer
confirms what.** Treat it as unusable until traced.

**Every per-title branch, base version (`construction_rules.gpl`):**

| Title | Search radius | Rule | Failure return |
|---|---|---|---|
| `wizards_tower` | `#wiz_tower_range` = 800 (`globals.gpl` line 522) | Must have a completed `wizards_tower` OR `wizards_guild` within range (`$listcompleted` filter, then `$listtitles` on both titles) — a *proximity-required* rule | `#chat_out_range_wiz_guild_tower` (40) |
| `ballista_tower` | `#ballista_tower_range` = 800 (`globals.gpl` line 525) | **Entirely commented out** (lines 38-50) — would have required a nearby `ballista_tower` or `dwarven_settlement`. The constant and the `#chat_out_range_ball_dsettle` (41) string still ship unused. | — |
| `marketplace` | `#Marketplace_Revenue_Threshold` = 500 for markets, `#Min_Dist_to_Market_For_Caravan_Spawn` = 1000 for trading posts (`globals.gpl` lines 364, 259) | Must have NO own-player `marketplace`/`closed` within 500 AND no `trading_post` within 1000 — a *proximity-forbidden* rule | `#chat_too_close_tpost_market` (42) |
| `trading_post` | Deathmatch: `#Deathmatch_Large_Trade_Radius` 2800 if board X > 5000 else `#Deathmatch_Small_Trade_Radius` 1700 (`globals.gpl` 885-886). Normal: `#Min_Dist_to_Market_For_Caravan_Spawn` = 1000 both checks | Same forbidden-proximity shape as marketplace, but radius is mode- and map-size-dependent | `#chat_too_close_tpost_market` (42) |
| anything else | — | falls through to `return 0` — unconditionally buildable | — |

Two reusable patterns fall straight out of this table:

1. **Proximity-required vs. proximity-forbidden are the same code
   shape, inverted.** `wizards_tower` returns 0 when the neighbour list
   is non-empty; `marketplace`/`trading_post` return 0 when it's empty.
   Nothing engine-side distinguishes the two — a modder writing a new
   branch picks the comparison direction.
2. **Radius values are plain `expression` constants in `globals.gpl`,
   not per-building XML.** Retuning wizard-tower chaining range, or
   market spacing, is a one-line constant edit that needs no XML and no
   exe change. Note the reuse: `#Min_Dist_to_Market_For_Caravan_Spawn`
   and `#Marketplace_Revenue_Threshold` are economy constants
   (`globals.gpl`'s caravan and market-revenue blocks) borrowed here as
   placement radii — editing one changes both systems.

**The failure return values are shared with the intent enum, not a
separate string table.** `#chat_out_range_wiz_guild_tower` (40),
`#chat_out_range_ball_dsettle` (41), `#chat_too_close_tpost_market` (42),
`#chat_too_close_market` (43) and `#Chat_Outpost_Too_Close` (206) are
declared inline in `GPL/defines.gpl` / `GPLMx/mx_defines.gpl` in the
*same contiguous numbering as `#intent_*`* — 39 is `#intent_assemble`,
44 is `#intent_defending_palace`. So a `CanIBuildThisBuilding` failure
code is an index into the same engine-side status/chat string list §7
documents for intents. **Practical consequence for modders: you cannot
invent a new failure message by defining a new `expression` — you can
only reuse an existing index**, because the string it renders lives
exe/`.cam`-side (§7's already-documented AITX lookup, still
UNVERIFIED in mechanism). `#chat_too_close_market` (43) is declared but
never returned by any branch in either version — a spare, already-
localized message slot.

**Base vs. expansion (`mx_Construction_Rules.gpl`): tweaked + one new
branch, not a rewrite.** The `marketplace` and `trading_post` branches
are character-for-character identical (including the same
`// should vheck for trazding posts too` typo). Three real differences:

1. **New `outpost` branch (mx only, lines 118-129).** Forbidden-proximity
   against both `Palace` and `Outpost` within
   `#Min_Dist_To_Palace_for_Outpost` = 1000 — and notably that constant
   is declared in `GPLMx/MajCompatibility.gpl` line 95, not
   `mx_Globals.gpl`. Returns `#Chat_Outpost_Too_Close` (206).
2. **The new branch uses `#CheckTitles` filtering inside
   `$ListObjects`** (`#CheckTitles` = 7, `mx_LowLevel.gpl` line 1691)
   instead of the base pattern of listing everything then post-filtering
   with `$ListTitles`. Same result, one pass instead of two — this is
   the §14 `$ListObjects` flag vocabulary being used to replace a
   filter step, and it's the idiom to copy in new code.
3. **The `wizards_tower` branch changed primitives, and the change looks
   behaviour-affecting.** Base: `$ListObjects(..., #MyPlayer)` then
   `masterlist = $listcompleted(masterlist)` then
   `list1 = $listtitles(masterlist,"wizards_tower")`. Mx: the
   `$listcompleted` call is commented out, replaced by an inline
   `#ATTRIB_FirstStageBuilt, 1` filter argument on `$ListObjects`, and
   the two title filters switched from `$listtitles` to `$removetitles`.
   From 15+ mx call sites, **`$RemoveTitles(list, "X")` returns the
   MATCHING members** (e.g. `mx_Hero_Births.gpl` line 49 counts
   `$removetitles(buildings,"library")` to compute the per-library
   intelligence bonus; `mx_Purchase_Equipment.gpl` lines 34-38 uses
   `$RemoveTitles` and `$listTitles` interchangeably against the same
   `buildings` list). **CORRECTED (this sentence originally said "it is
   `$ListTitles` that additionally strips the matches out of the source
   list" — that was wrong, and §19.6 disproved it):** the stripping is
   **`$RemoveTitles`' own side effect**, not `$ListTitles`'. Two call
   sites in `Quests_1.gpl` prove it: `Elf_Hunter`'s priority scheme does
   `Bungs = $RemoveTitles(Buildings,"Elven_Bungalow")` then treats the
   now-shorter `Buildings` as the remainder (`Non_Bungs = Buildings`),
   which only works if the matches were removed from the source; and
   `Clash_Empires_Victory` line 1592 calls
   `$RemoveTitles(Lairs,"Goblin_Watchtower")` **discarding the return
   value entirely** ("Towers don't spawn anything, so remove them"), which
   is only meaningful if the call mutates its argument. **Net rule:
   `$RemoveTitles` returns the matches AND removes them from the source,
   so successive calls partition one list** (§19.6/§19.8 use exactly
   that). The first half of the original finding stands unchanged.
   **So the mx wizards_tower rule is
   semantically equivalent to the base one** (both end up counting
   nearby towers/guilds), with "completed" redefined from
   `$listcompleted` to `#ATTRIB_FirstStageBuilt == 1` — a looser gate
   (first construction stage done, not fully built). `$removetitles`
   has **zero call sites in the base `GPL/` tree** — it appears only
   under `GPLMx/`, so base-mode GPL should stick to `$ListTitles`.
   **UNVERIFIED:** whether `$removetitles` exists as a primitive in the
   base-game exe at all.

**Cross-reference flag (not edited here, per scope):**
`TODO-New-Building-Requirements.md`'s `- [x] Placement/footprint
validation` item concludes that placement validation is entirely
exe-side and would need a Ghidra trace, and its build-menu item states
"a new building has no default prerequisite of any kind unless a quest's
own GPL explicitly calls `$disableunittype`." **`CanIBuildThisBuilding`
is a second, previously-unnamed prerequisite mechanism, and it is
pure GPL** — a per-building-title, proximity-based placement gate that
a modder can extend by adding a `title ==` branch, with no XML and no
exe change. That doc's *terrain-tile* claim still stands exactly as
written (this function reads agent proximity only, never terrain data),
and the footprint/overlap question is untouched by it — but the
"placement rules are exe-only" framing needs narrowing there. Needs
cross-referencing in that file by whoever owns it.

### 18.7 `Curse_Active` — turning a building into an active agent

Lines 478-534. **This is the template for "a building that does something
hostile on a timer,"** and it's the only function in the file installed on
a *building* rather than a unit. Wiring (`epic_quest_scripts.gpl` lines
3812-3815, inside `WIZARDS_CURSE()`):

```gpl
$ListObjects (Palace, "Building", -1, Guilds, #NoHiddenMap, #NotMyPlayer);
Guilds = $ListTitles (Guilds, "Wizards_Guild");
Guild  = $ListMember (Guilds, 1);
Guild's "SpecialScript" = $Curse_Active;
$NewThread (Guild's "SpecialScript", 5000, Guild);
```

**The `SpecialScript`-plus-`$NewThread` pair is the whole mechanism**, and
it's used 6 more times in the shipped tree, which confirms it as the
sanctioned idiom rather than a one-off: `$Hero_Generator` on every enemy
guild in `MAGIC_RING()` (`epic_quest_scripts.gpl` line 3251, interval
`30000 + $randomnumber(30000)`), the same in
`epic_quest_scripts.gpl` line 1259 (interval `60000 + $randomnumber
(60000)`) and line 2401 (30000), `GPLMx/Rules/Quests_2.gpl` line 574
(`90000 + $randomnumber(60000)`), and `$Setup_High_Level_Members` on a
rescued building at line 3025 with a 500 interval. Teardown is
`$KillThread(<building>'s "SpecialScript")` (line 3956). Three rules fall
out:

1. **A building's quest job is just a function pointer in a declared slot
   plus a thread** — same shape as §16.2's root-agent slots, at building
   scope. Interval is per-install, so the same handler can run at
   different rates on different buildings, and the randomized-interval
   form (`base + $randomnumber(base)`) keeps multiple copies from firing
   in lockstep.
2. **The agent must be passed as the thread's third argument**
   (`$NewThread(slot, interval, Guild)`) — the handler's `ThisAgent` is
   the building, not the caller. (Contrast §17.3's `EventAgent`, which had
   to pass a *name string* because a unit-less agent can't run threads; a
   building is a real unit, so the agent form works.)
3. **`SpecialScript` is only declared on `prototype Guild()` and
   `prototype Dwarven_Settlement()`** (18.2) — every shipped use targets a
   guild-family building. For a non-guild building, use its
   `ActiveScript` field instead.

The body is three unrelated jobs on one timer, and each is separately
reusable:

**(a) "Attack the best enemy hero" — the max-by-attribute scan.**

```gpl
Foreach Hero in Heroes do
    begin
        Temp_Score = $GetAttribute (Hero, #ATTRIB_ExperienceLevel);
        If (Temp_Score >= Best_Score) Best_Score = Temp_Score;
    end
If (Best_Score > 4)
    Foreach Hero in Heroes do
        If ($GetAttribute (Hero, #ATTRIB_ExperienceLevel) == Best_Score)
            $PerformAction (ThisAgent, "Level_Leach", Hero);
```

Two passes: find the max, then act on **everyone tied at the max** (so a
tie hits multiple heroes — deliberate or not, that's the behavior). The
`Best_Score > 4` gate is the "don't kick them while they're down" floor.
**`$PerformAction(building, "<ActionName>", targetHero)` is a building
casting an action at a unit** — the same primitive §13/§14 documented for
units, with a building as the actor, which is the piece that makes
"hostile building" work at all.

**(b) Self-repair, and it is a complete worked example of the
effector-callback pattern.**

```gpl
If ($GetAttribute (ThisAgent, #Attrib_HP) < $GetAttribute (ThisAgent, #Attrib_MaxHP))
    If ($CheckEffector (ThisAgent, "Magical_Repair_Effector") == False)
        $CreateEffector (ThisAgent, "Magical_Repair_Effector", 1);
```

Traced end to end: `Magical_Repair_Effector` is a **ParticleSystem**
record in `SDK/OriginalQuests/Data/M_ParticleSystems.xml` (ID `XL17`)
carrying `<Script type="0" cProc="0" GPLFunction="magical_repair"/>` and
`<DefaultSound value="Wizard_Curse_Repair"/>`; that callback is
`Magical_Repair(agent ThisAgent)` in `epic_quest_scripts.gpl` lines
4148-4172, which adds `#magical_repair_amount` (10, `globals.gpl` line
495) to HP, clamps to MaxHP, and writes it back. **So "regenerating
building" = one XML particle-system entry with a `GPLFunction` + one
5-line GPL function + a per-tick `$CheckEffector` guard.** Note the
callback's own self-retrigger block is commented out, so each effector
heals exactly once — the *repetition* comes from `Curse_Active` recreating
the effector every 5000ms while damaged. **The `$CheckEffector` guard is
what prevents stacking**; without it every tick would queue another heal.
This is also independent confirmation, from a third system, of §11/§13's
finding that `<Script GPLFunction=…>` on an overlay/particle record is the
generic "effector calls back into GPL" wiring — here on a
`subType="ParticleSystem"` record rather than an overlay.

**(c) Area denial.** `$ListObjects(ThisAgent, "Monster",
$GetAttribute(ThisAgent, #Attrib_SightRange), Enemies)` then
`$lightning_bolt_hit(Enemy)` per member. **Using the actor's own
`#ATTRIB_SightRange` as the query radius** is the tidy way to make a
building's threat range track its stats instead of a magic number.
`$lightning_bolt_hit` is GPL-defined (`GPL/TaskModules/Subtasks/
Spells.gpl` line 269, "player cast spell - from wizard's guild") —
the same helper §17.3's `Ritual_of_pain` uses, so it's a confirmed
general-purpose "zap this agent" call available in base mode.

**Two shipped defects here, both worth flagging:**

- **`$ListSubtypes (Heroes, "Hero");` on its own line discards its return
  value.** Compare `hooligan.gpl` line 33, which does
  `Heroes = $ListSubtypes (Heroes, "hero");`. **`$ListSubtypes` returns a
  filtered list; it does not filter in place** (same contract as
  `$ListTitles`). So `Curse_Active`'s subtype filter does nothing and the
  function operates on the unfiltered `"Hero"`-type list. Harmless here
  (both lists are nearly the same), but this is exactly the class of bug
  that silently makes a custom filter a no-op.
- **The lightning sweep passes no player filter**, unlike the hero query
  above it — so it zaps every `"Monster"`-type agent in range regardless
  of allegiance.

### 18.8 `Setup_Special_Chests` + the chalice chests — parameterized hook installation and respawn-by-rebirth

Lines 537-588. Three functions that together give two genuinely reusable
mechanisms: **a generic hook-installer that takes functions as
parameters**, and **respawn implemented by re-running an agent's own
`BirthScript`.**

#### The installer: `function`-typed parameters

```gpl
Function Setup_Special_Chests (list Chests, function BirthScript, function DeathScript)
Begin
    Foreach Chest in Chests do
        begin
            Chest's "BirthScript"   = BirthScript;
            Chest's "IGDeathScript" = DeathScript;
        end
End
```

**`function` is a first-class parameter type in GPL** — the caller passes
function pointers by name:

```gpl
$listobjects(palace,"special_item",-1,chests,#NoHiddenMap);
chests = $listtitles(chests,"treasure_chest");
$Setup_Special_Chests (chests, $Holy_Chalice_Chest_Birth, $Holy_Chalice_Chest_Death);
$setup_starting_treasure(chests,250,500);
```

(`epic_quest_scripts.gpl` lines 456-459, inside `HOLY_CHALICE()`.) This is
strictly more reusable than §17.1's `Setup_Multispawning_Lairs`, which
hardcodes its handler and passes *data* per instance: **here the behavior
itself is the parameter, so one installer serves any pair of handlers.**
Combine both patterns for a fully generic installer (function pointers +
per-instance data attributes).

**Ordering caveat, and it's a real trap the shipped code documents:**
`HOLY_CHALICE()` line 452 has to *re-assign* an `IGDeathScript` that an
earlier helper clobbered —

```gpl
//Reset the Chalice_Site's IGDeathScript back to Hidden_Chalice_Death (For VC.)
//This was overwritten in $Setup_Respawning_Lairs
Chalice_Site's "IGDeathScript" = $Hidden_Chalice_Death;
```

**Shared setup helpers overwrite per-instance script slots wholesale**
(`$Setup_Respawning_Lairs` rewrites *every* lair's death script — §17.3),
so **install order matters and the specific override must come last.**
Anyone chaining setup helpers in a quest init should assume the same.

#### Respawn-by-rebirth

`Holy_Chalice_Chest_Death` is the whole mechanism, in two statements:

```gpl
ThisAgent's "Type" = "Dead";
$RunThread (ThisAgent's "BirthScript",
            #HChalice_Chest_Respawn_Base + ($RandomNumber (#HChalice_Chest_Respawn_Mod) + 1),
            ThisAgent);
```

- **`BirthScript` is being used as a general "(re)initialize this agent"
  entry point, invoked from a one-shot `$RunThread`** rather than by the
  engine at creation. That is the reusable trick: an agent's birth hook is
  just a function pointer in a slot, so anything can call it, at any time,
  through a thread.
- **Delay window:** `#HChalice_Chest_Respawn_Base` 90000 +
  `$RandomNumber(#HChalice_Chest_Respawn_Mod)` 0-89999 + 1 = 90000-180000
  ticks (`globals.gpl` lines 678, 680), i.e. 1.5-3 game days on the
  60000-per-day convention §16.2/§17.3 established. Note this is the
  **base + random(mod)** form, which jitters *upward* — the opposite
  direction from `$random_time(t)`'s 75-100% downward jitter (§17.3). Both
  ship; pick deliberately.
- **`Type = "Dead"` is the *between* state.** It removes the agent from
  every `$ListObjects(…, "special_item", …)` query without deleting it,
  which is what makes the same agent revivable. The default
  `Treasure_Chest_Death` (`GPL/TaskModules/Buildings/Treasure.gpl` lines
  27-38) does *only* that line — its `$DeleteAgent` call is commented out
  with "there is no reason to keep them around."
- **The rebirth handler restores the state the death consumed**
  (`Holy_Chalice_Chest_Birth`, lines 552-572): `Type = "Special_Item"`,
  `#ATTRIB_HP = #ATTRIB_MaxHP`, `#ATTRIB_Gold = 250 + $RandomNumber(500)`,
  `#ATTRIB_ForceBuildingState = #building_force_inactive` (closed-chest
  art, 18.3), and `#ATTRIB_AlwaysView = 1`.
- **`#ATTRIB_AlwaysView`** is explained by the shipped comment: it "makes
  it so the Treasure Chest doesn't automatically deselect when its
  deathscript gets called." Same line appears in the default
  `Treasure_Chest_Birth`, so it is standard for any agent the player may
  have selected when it dies. **Worth setting on any quest object the
  player clicks on.**
- **Compare against the default chest to see exactly what an override
  adds:** default `Treasure_Chest_Birth` only sets gold (if unset) and
  `AlwaysView`; the chalice version adds a forced state, a full heal, a
  type reset, and unconditional gold. **So "override the shipped
  BirthScript/IGDeathScript pair" is the general recipe for changing one
  quest's economy of an existing object class**, with no XML and no new
  unit type.

**One genuinely unresolved point, stated rather than guessed:**
`Open_Chest` (`Treasure.gpl` lines 43-80) ends with
`$SetAttribute (Chest, #ATTRIB_HP, 0)` under the comment "**NOTE: THIS
WILL DELETE THE AGENT!**", and zeroing HP is what triggers the
`IGDeathScript` in the first place. If the agent really is deleted, the
`$RunThread` on its `BirthScript` would be arming a thread on a doomed
agent. The mechanism demonstrably ships as the Holy Chalice quest's
economy (the quest disables marketplaces via
`$disableunittype("Marketplace1")` specifically to force reliance on
respawning chests — `epic_quest_scripts.gpl` line 469), so it evidently
works, but **whether it works because `Type = "Dead"` is set *before* the
thread is armed, because `#ATTRIB_AlwaysView` defers cleanup, or because
the comment is simply wrong, is UNVERIFIED** — no GPL-side evidence
distinguishes them. Do not restate any of those as fact; if you clone
this, keep the exact statement order.

### 20.4 The rescue/defection subsystem — park, discover, claim

`VIGIL` is a "liberate the countryside" quest, and the two calls that
make it one are the most reusable thing in the file after 20.2:

```gpl
$SetUp_Rescue_Buildings (Palace);      // once, in the entry fn (line 858)
...
Function Vigil_victory()
begin
    ...
    $rescue_buildings(palace);          // FIRST line of every poll (line 893)
```

Both are ordinary GPL in `GPLMx/Rules/mx_Epic_Quest_Scripts.gpl`
(`setup_rescue_buildings` line 2802, `rescue_buildings` line 2908;
same-named functions exist in base `GPL/Rules/epic_quest_scripts.gpl` at
lines 2858 and 2953 — **the base copies were not diffed line-by-line in
this batch**, so treat base availability as "present, body unconfirmed").
Documented here only as far as `VIGIL`'s use requires; the rest of
`mx_Epic_Quest_Scripts.gpl` is Batch F/G.

**The three-phase shape, and it is entirely built on 20.2's `"type"`
register:**

**Phase 1 — park (`setup_rescue_buildings`, run once).**

```gpl
$ListObjects(palace,"building",-1,bldgs,#NotMyTeam, #NoHiddenMap);
foreach bldg in bldgs do
    begin
        bldg's "type" = "unknown";                     // ← out of every query
        if (bldg's "title" == "Dwarven_settlement" || … == "ballista_tower")
            bldg's "enemytype" = "nothing";
        if (bldg's "title" == "guardhouse") bldg's "enemytype" = "nothing";
        else if (bldg's "title" == "outpost")
            begin
                $killThread(bldg's "activeScript");
                $killThread(bldg's "Guard_Function");
                $killThread(bldg's "Guard_Spawn_Function");
                $killThread(bldg's "Tax_spawn");
                $killThread(bldg's "peasant_spawn");
                bldg's "title" = "outpost_hidden";      // ← retitle to park it
            end
    end
```

**Phase 2 — discover.** `rescue_buildings` queries the parked class:

```gpl
$ListObjects(palace,"unknown", -1, bldgs, #NotMyPlayer );
```

Note what is **missing**: `#NoHiddenMap`. Phase 1's query has it, this
one doesn't. Read with the constant's name (`GPL/LowLevel.gpl` line
1553, §14: `#NoHiddenMap` == 0, i.e. "ignore the hidden map"), that means
**phase 2 only sees buildings the player has actually explored** — which
is what makes the whole quest a rescue rather than an instant handover on
the first 4-second poll, and it lines up with the per-building
`$MessageFlag` + advisor sound fired on conversion. **Strong inference
from the flag's name plus the design's requirement, not a traced engine
fact — UNVERIFIED.** It is complicated by `#NoHiddenMap` being numerically
`0`; if the engine treats a missing option and an option of value 0
identically, something else must gate the rescue. Either way the
*pattern* stands: presence/absence of `#NoHiddenMap` is the only
difference between the two queries.

**Phase 3 — claim.** Per building, in order:

```gpl
$setunitplayernumber(bldg,player);            // §18.9's defection primitive
if (bldg's "title" == "statue")
    begin
        $messageflag(bldg,#message_rescued_statue);
        $listobjects(bldg,"hero",-1,guys,#MyPlayer,#insideOtherUnits);
        foreach guy in guys do
            if (guy's "subtype" == "hero")
                guy's "loyalty" += #statue_loyalty_boost;
    end
else
    begin
        $messageflag(bldg,#message_rescued_building);
        $PlaySound (palace, "Advisor_New_Outpost", "VFX_ADVISOR");
    end
bldg's "type" = "building";                   // ← back into normal queries
```

…then per-title reactivation, which is the mirror image of phase 1's
teardown: `enemytype = "monster"` for the settlement/ballista/guardhouse
cases, `$RunThread (bldg's "Guard_Spawn_Function", 1, bldg)` to restart
the guard pump, and for the outpost `$outpost_birth(bldg)` followed by
retitling `"outpost_hidden"` back to `"outpost"`.

**Five reusable findings:**

1. **`"type"` is a parking lot.** Setting an arbitrary string
   (`"unknown"`) removes an agent from every normal query while keeping
   it on the map, and a matching `$ListObjects(…, "unknown", …)` is the
   only thing that can still find it. **That is the generic "inert
   scenery that can be activated later" mechanism** — no new object type,
   no engine support. Same register as 20.2's invisibility and §19.10's
   death cycle.
2. **Retitling is the second parking lot, and it composes with the
   first.** `"outpost"` → `"outpost_hidden"` means even a title-based
   query misses it. Pairs with 20.3a's caution: retitle *back* before
   anything asks the object to reproduce itself.
3. **`"enemytype"` is the targeting-side switch, and `"nothing"` is a
   real value.** §18.6 established `Type`/`Subtype`/`EnemyType` as
   writable strings; this gives the idiom: **`enemytype = "nothing"`
   makes a building stop being a combat participant, `= "monster"` turns
   it back on.** Applied exactly to the buildings that would otherwise
   shoot the player's heroes while still nominally hostile
   (`ballista_tower`, `guardhouse`, `Dwarven_settlement`).
4. **Deactivating a building means killing its threads by name, and the
   five names are the full set for an outpost**: `activeScript`,
   `Guard_Function`, `Guard_Spawn_Function`, `Tax_spawn`,
   `peasant_spawn`. **A modder disabling a building has to enumerate
   these; there is no "suspend building" primitive.** Reactivation goes
   through the building's own `$outpost_birth` rather than restarting the
   five threads by hand — the commented-out block directly below it
   (lines 2960-2975) is the hand-rolled version someone replaced.
5. **`SpecialList` is a two-slots-per-record parallel list, and the
   read protocol is `$RemoveListMember(list, 1)` twice.**

   ```gpl
   If ($HasAttribute ("SpecialList", Bldg))
       While ($ListSize (Bldg's "SpecialList") > 0) do
           begin
               $SpawnUnit (Bldg, $ListMember (Bldg's "SpecialList", 1));   // herotitle
               Levels << $ListMember (Bldg's "SpecialList", 2);            // extra XP
               $RemoveListMember (Bldg's "SpecialList", 1);
               $RemoveListMember (Bldg's "SpecialList", 1);
           end
   ```

   GPL lists are untyped and have no record/struct type, so **encoding
   pairs as alternating members and draining two at a time is the
   codebase's answer to "a list of structs."** Note `$HasAttribute("name",
   agent)` guarding it — string first, agent second (§14).

#### Sibling mechanism: rescued pets, with a deliberate arming delay

`setup_rescue_pets` / `rescue_pets` / `pet_ready`
(`mx_Epic_Quest_Scripts.gpl` lines 2839-2905) are the same three-phase
shape for units, and they add one thing the buildings don't need:

```gpl
monster's "type" = "pet";                                  // phase 1, park
...
$setunitplayernumber(pet,player);                          // phase 3, claim
pet's "type" = "hidden";
$createeffector(pet,"charm_icon",1,"infinite");            // §13's marker form
pet's "activescript" = $pet_ready;
$setthreadinterval(pet's "Activescript", #charm_delay_time);
$stopmoving(pet);
// …then $pet_ready flips "type" = "hero", "enemytype" = "monster",
//   resets the interval to #Normal_cycle and calls $Reset_Tasks.
```

**Two extra ideas worth stealing:** a **third parking value** (`"pet"`
for "convertible", `"hidden"` for "converted but not yet active"), and
**an arming delay implemented by retuning the unit's own `ActiveScript`
interval** — the same "reuse the agent's script slot as a timer" trick
§19.10 found on a corpse, here on a live defector. `$Reset_Tasks` at the
end is §18.2's "make the slot swap take effect now."

#### One-line addition to §19.8: the idempotence guard on a team split

`urban_victory` lines 626-628:

```gpl
bldg = $Listmember(bldgs,1);
if ($getPlayerTeamNumber(palace) == $getPlayerTeamNumber(bldg))
    $setplayerteamNumber(bldg,$newteamnumber());
```

`$GetPlayerTeamNumber(agent)` is the read side of §16.2/§19.8's
`$SetPlayerTeamNumber` — no GPL definition exists (grepped
`function getplayerteamnumber` across the corpus: zero hits), so it's
engine-side. **The guard is what makes a per-poll war-declaration safe:
compare the two teams first, split only if they still match.** Without
it, a 4-second poll would call `$NewTeamNumber()` forever and leak team
numbers.

Does this settle §19.12's open "`$SetPlayerTeamNumber`'s exact scope"?
**No — but it narrows it.** The call is made on **one** representative
building (`$ListMember(bldgs,1)`) out of a whole enemy player's estate,
same one-call-per-faction shape §19.8 saw with lairs, which is
consistent with per-*player* scope. It is not proof: a per-agent
implementation would also stop the guard from re-firing on that one
building. **Still UNVERIFIED.**

### 20.6 Enemy buildings as quest agents — the `ActiveScript` variant, and higher-order death handlers

`URBAN_RENEWAL`'s entry function (lines 565-590) is the densest
building-hijack setup in the corpus: it partitions the enemy player's
estate by subtype and gives each half a behavior and a death hook.

```gpl
$ListObjects (Palace, "Building", -1, alist, #NotMyPLayer, #NoHiddenMap);
Guilds = $ListSubtypes (alist, "Guild");
bldgs  = $listsubtypes (alist, "entertainment");

Foreach Guild in Guilds do
    begin
        Guild's "IGDeathScript" = $Urban_guild_destroyed;
        Guild's "SpecialScript" = $Hero_Generator;
        $NewThread (Guild's "SpecialScript", 90000 + $randomnumber(60000), Guild);
    end

foreach guild in bldgs do
    begin
        guild's "IGDeathScript" = $Urban_crime_spot_destroyed;
        guild's "ActiveScript"  = $Corrupt_peasant_home;
        $NewThread (Guild's "ActiveScript", 90000 + $randomnumber(60000), Guild);
    end
```

**The `SpecialScript` half is already documented — §18.7 cites this exact
line (574) as one of its seven confirming call sites.** Three things here
are not.

**(a) The `ActiveScript` variant is the shipped worked example of §18.7's
rule 3, and it is destructive where `SpecialScript` is additive.** §18.7
concluded "for a non-guild building, use its `ActiveScript` field
instead"; entertainment buildings (Inn/Tavern-family, subtype
`"entertainment"`) have no `SpecialScript` declared, and this is the code
that does it. **But the two are not equivalent:** `SpecialScript` is a
dedicated, normally-empty quest slot, whereas `ActiveScript` is the
building's *own* behavior slot, so this assignment **overwrites whatever
the building was doing, with no stash** (contrast §18.2's swap-and-stash
into `QuestScript`). Whether the building's pre-existing `ActiveScript`
thread keeps running the old function pointer, or the assignment plus a
second `$NewThread` leaves two threads on one slot, is **UNVERIFIED** —
`$NewThread` is called without a preceding `$KillThread`. **Safe recipe
for a modder: stash the old value, `$KillThread` the slot, assign, then
`$NewThread`.**

**(b) `$Hero_Generator` reveals the guild-membership field set, and that
manual spawns need `$Generate_Character_Attributes` called by hand.**
Body in full (`GPLMx/TaskModules/Buildings/mx_Lair.gpl` lines 183-195;
base twin `GPL/TaskModules/Buildings/Lair.gpl` line 157):

```gpl
If ($ListSize (ThisAgent's "Members") < $getattribute(thisagent,#ATTRIB_MaxGuildMembers))
    begin
        thisspawn = $SpawnUnit (ThisAgent, ThisAgent's "Member_Title");
        $Generate_Character_Attributes(thisspawn);
    end
```

- **`"Members"` is a live list field on a guild** (the current occupants,
  also read by `guild_destroyed_common` below), and **`"Member_Title"` is
  the unit type that guild recruits** — so "spawn one more of whatever
  this guild makes" is data-driven, exactly like §19.8's
  `$SpawnUnit(Lair, Lair's "Spawn_Type")` is for lairs. Same design, two
  building families.
- **The cap is the engine attribute `#ATTRIB_MaxGuildMembers`, and GPL
  must check it itself** — same "convention, not enforcement" property
  §19.7 found for `#Monster_Spawn_Cap`. §4 already noted the
  base/expansion divergence here (base `max_members` field vs. mx's
  engine attribute); this is the mx form.
- **`$SpawnUnit` alone does not appear to run
  `$Generate_Character_Attributes`.** §18.4 established that the engine
  calls it on natural hero births; this call site adds it explicitly
  right after a scripted spawn. **Inference, flagged: the likeliest
  reading is that a GPL-spawned hero gets no randomized stats, name or
  `StartingScript` unless you call it yourself** — but a belt-and-braces
  double call would look identical in source, so this is **UNVERIFIED.**
  Cheap insurance either way: call it after spawning a hero from script.

**(c) Death handlers are higher-order — a function value is a first-class
argument.** `urban_guild_destroyed` ends with

```gpl
$guild_destroyed_common(thisagent,$homeless);      // line 728
```

and the callee's signature is literally
`function guild_destroyed_common (agent thisagent, function nowhere_script)`
(`GPLMx/mx_Building_Deaths.gpl` line 708; base `GPL/Building_Deaths.gpl`
line 526, parameter named `no_where_script`). Read in full it is four
steps:

```gpl
ThisAgent's "Type" = "Dead";            // so evicted heroes don't pick this guild
members = thisagent's "members";
$release_occupants ( thisagent );
foreach member in members do
    $Find_New_Home ( member, nowhere_script );   // ← the passed-in function
$building_death ( thisagent );
```

Three findings:

- **GPL passes functions as ordinary arguments, not just by name string.**
  §17's `$LookupFunction` and §19.4's `$SetMusicStoppedCallback` resolve a
  function from a *string*; this is the direct form — `$homeless`
  (`GPLMx/TaskModules/Characters/mx_homeless.gpl` line 7) is passed as a
  value into a `function`-typed parameter. **So "what should the evicted
  occupants do if there's nowhere to go" is a plug-in point, and a mod can
  pass its own function there.**
- **The shipped comment on `Type = "Dead"` independently confirms 20.2:**
  verbatim, "This is done so that the Heroes don't return this guild when
  they search for a new home - it is redundant with building_death." That
  is the `"type"` register being used *as a query filter, on purpose,
  with the reason written down* — the strongest single piece of evidence
  for 20.2 in the corpus. The neighbouring `GuardHouse_Death` (line 733)
  shows the same register from the other side: hidden guards are
  `$IsHidden` with a non-`"Hero"` type, and reactivating them is
  `Guard's "Type" = "Hero"` + `$UnHide (Guard)`.
- **Two stock building-death handlers exist, and both are meant to be
  tail-called.** `$guild_destroyed_common(agent, function)` for guilds
  (which itself ends in `$building_death`), `$building_death(agent)`
  directly for everything else — `urban_crime_spot_destroyed` line 802
  uses the latter. Together with §19.3's `$Lair_Death`, that makes
  **three** confirmed stock handlers and settles the convention: **an
  `IGDeathScript` override adds behavior and then calls its family's stock
  handler; it never reimplements the teardown.**

**One-off worth knowing: `$adjustattribute(thisagent,
#ATTRIB_MaxGuildMembers, 20)`** immediately before the "release a bunch
of 'corrupt' guys" spawns (line 709). The spawns that follow use `palace`
as their source, not the dying guild, so what the +20 is actually for is
**UNVERIFIED** — plausibly to stop `$release_occupants` /
`$guild_destroyed_common` capping the eviction. The transferable fact is
just that **the guild cap is runtime-writable via `$AdjustAttribute`.**

#### Spawning enemy lairs onto the player's own buildings

`Ratmen_Events` stage 6 (lines 190-206) is the one genuinely new *effect*
in that quest, and it is three lines:

```gpl
$listobjects(palace,"building",-1,bldgs, #MyPlayer, #ATTRIB_FirstStageBuilt, 1);
bldgs << palace;
i2 = $listsize(bldgs);
i = 0;
while (i < 7) do
    begin
        bldg = $listmember(bldgs,$randomnumber(i2) + 1);
        $minimapanimation(bldg,"Event_beacon");
        $spawnunit(bldg,"BrokensewerMain","maxhp");
        i += 1;
    end
```

**`$SpawnUnit(<a player building>, "<lair type>", "maxhp")` drops a
fully-built enemy lair at the player's own building** — the "the sewers
erupt inside your city" beat, built from §17's `"MaxHP"` flag and nothing
else. Two details: the draw is **with** replacement (no `bldgs -= bldg`,
unlike every other draw in this file), so fewer than 7 distinct sites is
normal; and **the palace has to be appended by hand** (`bldgs << palace`)
because the `#ATTRIB_FirstStageBuilt, 1` query didn't return it. Why not
is **UNVERIFIED** — either the palace isn't in the `"building"` class or
it doesn't carry that attribute.

---

## Chapter 6: Agent State, Type and Identity

The `"type"` register, despawning, ownership changes, and quest-wide unit setup.

### 20.2 RESOLVED (§19.12 open question): `"type"` IS the `$ListObjects` class register, and `"invisible"` is populated by GPL

§19.12 left open **"what populates the `"invisible"` `$ListObjects` type
class"** — its existence and its deliberate union with `"monster"` were
confirmed, its membership was not. **This batch answers it, and the
answer is larger than the question.**

The trigger is `list_all_enemy_heroes` (this file, lines 514-532), a
local helper `SCIONS_CHAOS` uses instead of a plain hero query, read in
full:

```gpl
function list_all_enemy_heroes(agent palace) is list
begin
    $listobjects(palace,"hero",       -1,guys,#NotMyPlayer,#NoHiddenMap);
    $listobjects(palace,"invisible",  -1,l2,  #NotMyPlayer,#NoHiddenMap);
    $listobjects(palace,"camouflaged",-1,l3,  #NotMyPlayer,#NoHiddenMap);

    l2 = $addlists(l2,l3);
    foreach thing in l2 do
        if (thing's "subtype" == "hero")      // ← the recovery step
            guys << thing;
    return guys;
end
```

The `"subtype" == "hero"` filter only makes sense if a hidden hero is
**not** in the `"hero"` class at all. Chasing that gives the mechanism,
confirmed from five independent write sites:

| Write | Site |
|---|---|
| `thisagent's "type" = "Invisible"` | `GPLMx/TaskModules/Subtasks/mx_Spells.gpl` line 1141 (`Invisibility_brew_effect`) and line 3576; base twin `GPL/TaskModules/Subtasks/Spells.gpl` line 1389 |
| `thisagent's "type" = "camouflaged"` | `mx_Spells.gpl` line 3245; base `Spells.gpl` line 1074 |
| `thisagent's "type" = thisagent's "original_type"` | `mx_Spells.gpl` lines 1156, 3196, 3259, 3591, 4275, 4305 — the restore path |
| `thisagent's "type" = "dead"` | `mx_Spells.gpl` lines 1159, 3594 — restore-when-dead branch |
| `"Type"`/`"Original_Type"` written as a pair | `mx_Control_Monster.gpl` 67-68, `mx_Reset_Controlled.gpl` 15-16, `mx_Monster_Births.gpl` 483-484 / 513 / 583, `mx_Hero_Births.gpl` 564-565 |

**So, precisely:**

- **`$ListObjects`' second argument is not a fixed taxonomy — it is the
  agent's own writable `"type"` string.** `"invisible"` and
  `"camouflaged"` are not extra flags layered on top of `"hero"`; they
  **replace** it. Going invisible silently removes a unit from every
  `"hero"`/`"monster"` query in the game, which is exactly the intended
  gameplay effect and exactly the trap for a modder writing a naive
  census.
- **`"original_type"` is the stash slot for the swap** — declared
  `string Original_type;` on all four prototypes in
  `GPLMx/mx_prototype.gpl` (lines 107, 218, 957, 997; base
  `GPL/prototype.gpl` line 176). This is §18.2's swap-and-stash idiom
  applied to a *string* field rather than a script slot, and it is why
  the restore path is a single assignment.
- **`"subtype"` survives the swap and is how you recover what the thing
  really is.** That is the whole reason `list_all_enemy_heroes` and
  §19.5a's `$IsTitleAlive` both union-then-filter rather than querying
  once.
- **Dying is the same mechanism.** `"type" = "dead"` (§8's gravestone
  state) and §19.10's `"Waiting_to_die"`/`"Monster"` cycle are not
  special cases — they are the same one-string lifecycle register, and
  §19.10's `$ClearEngineDeathFlags` resurrection works *because* putting
  `"Monster"` back makes the agent visible to queries again.

**Practical rule for any custom census or victory poll: query
`"hero"`/`"monster"`, then also query `"invisible"` and `"camouflaged"`
and filter the union on `"subtype"`.** Three shipped helpers do exactly
this — `list_all_enemy_heroes` here, `$IsTitleAlive`
(`mx_Epic_Quest_Scripts.gpl` line 7, §19.5a, monster ∪ invisible), and
`all_enemies_dead` (`mx_Epic_Quest_Scripts.gpl` lines 1167-1200, which
unions **six** classes: building, lair, monster, hero, Invisible,
camouflaged). Anything less has a false negative that only shows up when
a player drinks an invisibility brew.

**Still not answered:** whether the *engine* also writes `"type"`
(e.g. on death, or when a unit enters a building) rather than GPL doing
all of it. Every write found in the corpus is GPL-side; an engine-side
writer would be invisible to source reading. **UNVERIFIED.**

### 18.9 Arrive-and-despawn, defection, and the orphaned chest spawner

#### `Captured_Peasant_Goto_Palace` — the smallest complete quest behavior

Lines 591-616, and it is eleven lines of substance:

```gpl
Palaces = $ListPalaces ();
Palace  = $ListMember (Palaces, 1);

If ($IsMoving (ThisAgent) == False)
    $Hide (ThisAgent, Palace);

If ($IsHidden (ThisAgent))
    $DeleteGamePiece (ThisAgent);
```

**"Walk to a place, then vanish" needs no travel script, no `BackScript`,
and no arrival guard** — because `$Hide` is re-issued every tick while not
moving (so it self-recovers from any interruption) and `$IsHidden` is the
arrival test. Reusable verbatim for rescued civilians, delivered items,
messengers, or any temporary NPC that should clean itself up.

- **`$DeleteGamePiece(agent)` is removal *without* death** — no death
  script, no gravestone, no XP, no loot. The contrast pair is worth
  memorizing: `$SetAttribute(agent, #ATTRIB_HP, 0)` kills the agent and
  runs its `IGDeathScript` (18.3's phantom cleanup); `$DeleteGamePiece`
  just removes it (here, `hooligan.gpl`'s `Hooligan_Goto_Palace` and
  `Hooligan_Leave_Map`).
- **`$ListMember($ListPalaces(), 1)` as "the player's palace" is a
  single-player-only shortcut** — same limitation as 18.3's `#Player_1`
  hardcoding. Multiplayer-safe form is `$GetPalace(ThisAgent)` (used by
  `Steal_Ring`) or `$GetUnitPlayerNumber` (§17.3).
- No `$SpecifyIntent` call, so the peasant displays whatever intent it
  last had. Cosmetic, but easy to forget.

**The wiring site adds the mechanism that makes this a *rescue***
(`epic_quest_scripts.gpl` lines 4013-4030, inside
`Wizards_Curse_Victory`): the captive is found with
`$ListObjects(Palace, "Hidden", -1, Peasants, #NoHiddenMap, #NotMyPlayer)`
+ `$ListTitles(Peasants,"Peasant")`, then

```gpl
$setunitplayernumber (Peasant, #Player_1);
Peasant's "ActiveScript" = $Captured_Peasant_Goto_Palace;   // + BasicScript + BackScript
AIRootAgent's "end_coord" = $locationof(peasant);
```

- **`$SetUnitPlayerNumber(agent, playerNumber)` changes an existing
  agent's owner at runtime.** That is the defection/rescue/conversion
  primitive: one call, no respawn, and it pairs naturally with a behavior
  swap on the next lines. (Read-side counterpart `$GetUnitPlayerNumber`
  is used throughout this batch.)
- **Object type `"Hidden"`** is how a unit currently inside/behind
  something is queried — another entry for §17.5's non-obvious type-name
  list, and the reason a naive `"hero"`/`"Monster"` query misses captives
  (§16.2 made the same point about `"Invisible"`/`"camouflaged"`).
- **`AIRootAgent's "end_coord"` is set from the rescued unit** so the
  end-of-game camera lands on it — §16.2's optional `$declarevictory`
  second argument, coordinate form, with an `else` branch defaulting to
  the palace when no captive survived. **Always set a fallback**; the
  shipped code does.
- The trigger above it is `$istitlealive(palace,"werewolf") == FALSE`
  (`epic_quest_scripts.gpl` line 7 — `function istitlealive(agent palace,
  string title) is boolean`), which is the tidy shipped wrapper for
  "are any units with this title left." Prefer it over open-coding a
  `$ListObjects` + `$ListTitles` + `$ListSize` triple.

#### `Treasure_Spawner()` — dead code, useful body

Lines 446-471. Zero callers anywhere (18.1). What it demonstrates anyway:

```gpl
Random = $RandomNumber (4) + 1;
If (Random == 1)
    $SpawnUnit (Palace, "Treasure_Chest1",
                $RandomCoord (Palace, #default_spawn_treasure_dist, -1),
                "MaxHP", #Monster_Player);
… (Chest2/3/4 identically)
```

- **`$RandomCoord(agent, min, -1)` = "at least `min` away, no upper
  bound"** — the annulus form §17.5 documented (`800, 1000`) with `-1`
  as the unbounded maximum, so "anywhere on the map but not near the
  palace" is one call.
  `#default_spawn_treasure_dist` = 500 (`globals.gpl` line 793).
- **Chests are spawned as `#Monster_Player`** — i.e. neutral map loot is
  owned by the monster player, which is why the player's heroes treat them
  as lootable objects rather than own-team buildings.
- `"MaxHP"` spawns them complete (§17.5).
- The four-way `if` chain differing only in the type name is exactly the
  shape §17.2 flagged as the shipped extension pattern (add a branch, bump
  the `$RandomNumber` bound); the live equivalent the shipped quests
  actually call is `$setup_random_treasure(count, distance)`.

### 20.7 Two more quest-setup primitives: advisor voices, and a starting hero level

Both from `VIGIL`, both small, both reusable in any quest.

**(a) `$ElvesVoice_setOperative(0)` / `$dwarvesVoice_setOperative(0)`**
(lines 847-848) — **new to this guide.** No `function` definition exists
anywhere in the corpus (grepped `Voice_setOperative`: 25 call sites, zero
definitions), so both are engine primitives, and they appear in **base
and expansion** (`GPL/Rules/epic_quest_scripts.gpl` lines 50-51, 720-721,
1404-1405, 1804, 1950-1951, 2154-2155, 2667, 3107-3108, plus the mx
mirror). The argument is an integer used as a boolean; the re-enable form
is real — `mx_Epic_Quest_Scripts.gpl` lines 858-859 call `(1)` on both,
immediately after `$enableunittype("Dwarven_settlement")` /
`("Gnome_hovel")`.

**Every single call site pairs them with `$DisableUnitType` of the
matching racial building** (`Elven_bungalow` for the elf voice,
`Dwarven_settlement`/`Gnome_hovel` for the dwarf one), and the one
re-enable site pairs them with `$EnableUnitType`. **So the idiom is:
disabling a race's building and silencing its voice are two halves of the
same edit — if you gate a race out of a quest, call both, or the player
gets audio prompts about content that cannot exist.** What exactly is
silenced (advisor hints vs. unit barks) is **UNVERIFIED**: the primitives
are engine-side with no traceable reader, and the inference rests on the
naming plus the 100%-consistent pairing.

**(b) `$setup_hero_level(palace, 10)`** (line 859) — a quest-wide starting
hero level, two lines of body (`GPLMx/Rules/mx_Epic_Quest_Scripts.gpl`
lines 1150-1164; base `GPL/Rules/epic_quest_scripts.gpl` line 1178):

```gpl
$listobjects(thisagent,"hero",-1,heroes,#MyPlayer,#NoHiddenMap);
foreach hero in heroes do
    begin
        $advance_to_level(hero,explevel);
        $setattribute(hero,#ATTRIB_StartedwithThisUnit,1);
    end
```

- **It only touches heroes that already exist**, i.e. the ones the `.q`
  pre-placed. Heroes recruited later start normally — so this is "the
  veterans you begin with," not a global level floor.
- **`#ATTRIB_StartedwithThisUnit` is new to this guide, and it is
  engine-consumed.** Five write sites, no GPL reader:
  `mx_Epic_Quest_Scripts.gpl` 1162 and 3030, base twins at 1190 and 3060,
  and — the one that gives it meaning — `High_Level_Hero_Birth`
  (`GPLMx/mx_Hero_Births.gpl` line 586, base `GPL/Hero_Births.gpl` 510),
  whose header comment reads "Epic Quest Scripts sets this as a Hero's
  birthscript if they are supposed start as a High Level hero."
  **So the attribute marks "the player began the quest with this unit,"
  and it is set on exactly the units a quest hands you for free.** What
  the engine does with it (scoring, loss conditions, the
  "you've lost your last hero" check) is **UNVERIFIED** — no reader is
  visible from source. Set it when you pre-level or gift a hero, since
  every shipped site that does one does the other.
- Incidental defect spotted in the same family, flagged not chased
  (it lives in Batch F/G's file): `mx_Epic_Quest_Scripts.gpl` line 3030
  writes `$setattribute(thisagent,#ATTRIB_StartedwithThisUnit,1)` inside
  the `SpecialList` drain loop of 20.4, where `thisagent` is the
  **building** and the freshly spawned `Member` is what the neighbouring
  `$advance_to_level (Member, Start_Level)` targets. Same wrong-target
  shape as 20.5c's `ActionRateModifier` line.

**Design note worth one line, because it's the reason both of the above
exist:** `VIGIL` calls `$DisableUnitType` **20 times** (lines 828-854) —
all four guilds, all seven temples, embassy, mausoleum, fairgrounds,
magic bazaar, sorcerer's abode, outpost, and all three racial
settlements. The player therefore cannot recruit a single new hero.
**"Fixed roster" is a real quest genre here, and it is composed of
`$DisableUnitType` × N + `$setup_hero_level` + the 20.4 rescue subsystem
as the only source of reinforcements** — the same "compose it out of
existing primitives" story as §19.5c's protect-what-you-can't-build.

### 19.8 Three-way faction war: `$NewTeamNumber` applied to monsters, not palaces

§14 documented `$setplayerteamnumber(p2, $newteamnumber())` in the
deathmatch free-for-all splitter, where the arguments are *palaces*.
`CLASH_EMPIRES` uses the same pair on **monster lairs**, which is a
different capability and the whole basis of the quest:

```gpl
$RevealWholeMap ( #Player_2 );   // the goblins
$RevealWholeMap ( #Player_3 );   // the rats

$ListObjects ( Palace, "Lair", -1, Lairs, #NoHiddenMap );
Foreach Lair in Lairs do
    begin
        If ( $GetUnitPlayerNumber ( Lair ) == #Player_2 ) Lairs2 << Lair;
        Else                                             lairs3 << lair;
        ...
    end

Lair = $ListMember ( Lairs2, 1 );
$SetPlayerTeamNumber ( Lair, $NewTeamNumber ());     // goblins get their own team
lair = $listmember (lairs3, 1);
$setplayerteamNumber ( lair, $newTeamNumber());      // rats get their own team
```

(`Quests_1.gpl` lines 1481-1524.) Four findings:

- **`$SetPlayerTeamNumber` operates on the agent's *player*, not the
  agent.** One representative lair per faction is enough — the code picks
  `$ListMember(Lairs2, 1)` and never touches the rest. That is the only
  reading consistent with the quest working (all goblins end up hostile to
  all rats, not just the one lair), and it matches §14's palace-level
  usage where one call per palace changes that palace's whole side.
  Stated as a strong inference from the call pattern; the primitive's
  internals are engine-side and **UNVERIFIED**.
- **`#Player_2` / `#Player_3` can host monsters.** The quest's `.q` file
  assigns lairs to player slots 2 and 3, and GPL then splits those slots
  onto fresh teams. **So a modder wanting mutually hostile monster
  factions does it in the `.q` (player assignment) plus two GPL lines
  (team assignment)** — not with a new hostility system.
- **`$RevealWholeMap (#Player_N)` takes a player constant, not an agent**
  — unlike `$RevealArea (viewer, coord, radius)`. Giving it to the AI
  factions is what makes them find each other and fight instead of
  wandering. It has zero other call sites in the shipped tree (the only
  other occurrences are commented-out lines in this project's own
  `custom_rules.gpl` templates), so this is its one worked example.
- **`#force_Monster_Hunter` is the behavioral other half** (19.6): the
  event sequencer spawns matched rat and goblin packs *at the same
  coordinate* with that artifice, so they immediately find each other.
  `$RevealArea (Palace, Loc, 200)` on the same spot is what lets the
  player watch.

#### The population equalizer — a self-balancing faction AI in ~30 lines

`Clash_Empires_Victory` lines 1568-1640 runs a 35%-per-poll rebalance that
is worth stealing wholesale for any "two AI factions should stay
comparable" design:

```gpl
If ( ($RandomNumber (100) + 1) < 35)
    begin
        $ListObjects ( Palace, "Monster", -1, Monsters, #NoHiddenMap );
        Rats = $ListFamily (Monsters, "Ratman");
        Gobs = $ListFamily (Monsters, "Goblin");
        Rat_Diff = $ListSize (Gobs) - $ListSize (Rats);
        Gob_Diff = $ListSize (Rats) - $ListSize (Gobs);

        Rat_Lairs = $RemoveTitles (Lairs, "RatsNest");
        lairs2    = $removeTitles (lairs, "brokensewermain");
        rat_lairs = $addlists (rat_lairs, lairs2);
        $RemoveTitles (Lairs, "Goblin_Watchtower");     // side effect only
        Gob_Lairs = Lairs;                              // whatever's left

        If (Rat_Diff > 0)      // spawn from a random rat lair
            $SpawnUnit (Member, Member's "Spawn_Type");
        Else if (Gob_Diff > 0) // …or a random goblin lair
            $SpawnUnit (Member, Member's "Spawn_Type");
    end
```

- **`$ListFamily (list, "<family>")` is the family-level filter** —
  defined in `GPLMx/mx_LowLevel.gpl` line 59 as a `Foreach` over
  `Dude's "family" == family`, returning a new list. **So `"family"` is a
  readable per-agent string field, and it groups unit types the way
  `"Title"` cannot** (`"Ratman"` covers Ratman/RatmanShaman/
  RatmanChampion/RatmanCatapult in one test). Its other shipped use is
  `GPLMx/DecisionTrees/Modules/Buff.gpl` line 41, buffing same-family
  allies — an independent confirmation, not an inference from this one
  site. **mx-only** (defined in `mx_LowLevel.gpl`; no base-`GPL/`
  definition found).
- **The reinforcement is `$SpawnUnit (Lair, Lair's "Spawn_Type")`** —
  i.e. it asks the lair what it makes instead of hardcoding a unit, so the
  equalizer keeps working if the `.q` assigns different lair types.
  `LEGENDARY_HEROES` line 44 uses the identical form for its "roll to
  pre-spawn each lair at quest start" loop, with the shipped comment
  "This will be overriden by lair data."
- **Partitioning a list by repeated `$RemoveTitles`** is the idiom, per
  19.6 — three calls turn one `Lairs` list into "rat lairs," "goblin
  lairs," and a discarded towers bucket.
- **Both diffs are computed, not one and its negation used twice**, which
  is redundant but harmless; the `Else if` means at most one unit is added
  per poll, so the balancing is gentle rather than instant.

---

## Chapter 7: Primitive, Helper and Constant Reference

Engine hooks, shared helper library, primitives and constants catalogued.

### 17.5 Engine-invoked hooks and previously-undocumented primitives

#### Engine-invoked callbacks found in this batch

Applying §16.1's test (function is defined, has zero `$Name(` call sites
anywhere in the `.gpl` corpus, and something clearly runs it):

1. **`VAMPIRIC_REVENGE()`** — the quest entry function. Grepped: the only
   occurrences of the name in the whole workspace are the two definitions
   (base + mx). **Zero GPL call sites, so the engine calls it by name**,
   resolved from the `.q` file's pattern-name field (per
   `.kiro/steering/majesty-modding.md`'s Q-format notes). Signature is
   nullary. This is the hook every custom quest already uses, now
   confirmed by absence-of-caller rather than assumed.
2. **`Freestyle()`** — same test, same result, and it self-documents:
   "This will be called at the start of any Freestyle game." Base version
   `GPL/Rules/epic_quest_scripts.gpl` line 4084, mx version line 4047.
   **This is the one place a mod can add global freestyle-mode setup**,
   and the mx version proves it's the intended extension point (that's
   where the whole special-event framework was bolted on).
3. **`<anything>'s "IGDeathScript"`** — `Demo_Dark_Castle_Death` is
   *assigned* (`Lair's "IGDeathScript" = $Demo_Dark_Castle_Death`) and
   never called from GPL — grepped, zero `$Demo_Dark_Castle_Death(` call
   sites. So **the engine invokes whatever function pointer sits in that
   attribute when the object dies, passing the dying agent as
   `thisagent`.** Same shape as the `birthscript` /
   `DoWizTowerEnchant` / `CanIBuildThisBuilding` hooks this guide already
   documents, but *per-instance and reassignable at runtime*, which the
   others are not. That combination — engine-invoked, but the pointer is
   a plain writable attribute — makes it the most flexible hook in the
   codebase.
4. **A new hook category: engine-*named*, GPL-invoked.**
   `$GetSpecialEvent1Script()`/`$GetSpecialEvent2Script()` don't call
   anything — they return a function *name* which GPL then binds with
   `$LookupFunction` and calls itself. **The engine's only contribution is
   the choice.** This is architecturally different from every hook
   previously documented here (where the engine holds the call site), and
   it's strictly friendlier to modders: the contract is a string, so any
   function you write is reachable the moment its name is selectable.
   §16.2's `$GetVictoryConditionIndex()` is the weaker index-based
   cousin of the same idea.

Note what is **not** a hook, to avoid a §16-style over-claim: the 15
special-event functions and the 14 random-event functions are ordinary
GPL functions. `Random_Events.gpl`'s `// RANDOM_EVENT` tag comments are
inert. Nothing scans a file, a directory, or a naming convention.

#### Primitives this guide hadn't documented, that recur across this batch

§13/§14 covered the effector family plus `$ListObjects`/
`$AdjustAttribute`/`$PerformAction`/`$RandomNumber`/`$NewThread`, and
explicitly *deferred* `$MessageFlag` and `$Concatenate` as "quest
scripting only / pure plumbing." This batch is that system, so they get
covered here.

**Reflection and dynamic dispatch (new):**

- **`$LookupFunction(string) → function`** — name-to-pointer. Also in the
  base-game compiler keyword list, so usable in base mode.
- **`(agent's "attr")(args)`** — indirect call through a function-pointer
  attribute. Two independent confirmations now: `Freestyle()` line 4081
  and §12's `Dwarfeh_AI` spell dispatch.
- **`$CreateAgent("<Prototype>", "<Instance>")` + `$RetrieveAgent(name)`**
  as a pure state container, with **the constraint that a unit-less agent
  cannot run threads** — hence the `string AgentName` parameter
  convention (17.3). The constraint is stated in the shipped comment, not
  inferred.

**Player notification triad (all three used side by side in `Demo.gpl`
and `Quests_3.gpl`, so the division of labour is confirmed by usage, not
by documentation):**

- **`$MessageFlag(agent, #Message_*)`** — a one-shot notification anchored
  on an agent. Needs a `#Message_*` expression index
  (`GPLMx/mx_defines.gpl` block at 227-244 for the event system).
- **`$Post_Message(agent, #sign_*)`** — persistent text attached to a map
  decoration. **Every one of the ~20 call sites across
  `Demo.gpl`/`epic_quest_scripts.gpl`/`Quests_3.gpl` targets an object
  retrieved as type `"color"`** (titles seen: `sign_wood`,
  `sign_fancy_iron`, `Banner_wood`, `obelisk`, `stone_tablet`) and uses a
  `#sign_*` constant. No non-sign call site exists. **UNVERIFIED** whether
  the engine rejects a non-`"color"` target or just renders nothing.
- **`$MiniMapAnimation(agentOrCoord, "Event_beacon")`** — draws attention
  on the minimap. Accepts **either** an agent (`Undead_Horde`'s
  `$minimapanimation(building, ...)`, `mx_Monster_Births.gpl`'s
  `boss_monster_birth`) **or** a bare coordinate (`Undead_Horde`'s
  fallback branch, `Wandering_Heroes`) — a real overload worth knowing.
  `"Event_beacon"` is the only animation name used in this batch.
- Supporting: **`$RevealArea(palace, $LocationOf(x), radius)`** — used at
  quest init in `Demo.gpl` (600 around the palace), per-sign in
  `Setup_Trade_Markers` (300 each), and per-palace in
  `boss_monster_birth` (300, looped over `$ListPalaces()` so every player
  sees it). **The loop-over-palaces form is the multiplayer-correct one.**

**Spawning (`$SpawnUnit` is variadic and order-insensitive — this is the
single most practically useful finding in 17.5):**

Every one of these shipped forms appears in this batch, with arguments in
different orders:

```gpl
$SpawnUnit ( marker, "Goblin_Fighter", spawnpoint, #monster_player,
             $concatenate ( #ATTRIB_Artifice, #force_caravan_raider ));   // Random_Events
$spawnUnit ( Palace, "Minotaur", #Monster_Player,
             $concatenate ( #ATTRIB_artifice, #force_overlay ),
             $RandomCoord ( Palace, -1 ));                               // Special_Events
$SpawnUnit ( building, "vampire", #monster_player, "override" );          // Random_Events
$SpawnUnit ( ThisAgent, "Vampire", "Override" );                          // Demo
$SpawnUnit ( Palace, "Mausoleum", "MaxHP", $RandomCoord ( Palace, 200 )); // Special_Events
$SpawnUnit ( Mausoleum, $Mausoleum_Random_Hero_Type ( Mausoleum ));       // Special_Events
$spawnunit ( palace, "wizard",
             $concatenate ( #ATTRIB_NumHealingPotions, 5 ),
             $RandomCoord ( palace, -1 ));                                // Demo
```

So: **argument 1 is the reference agent (position/ownership source),
argument 2 is the unit-type name, and everything after that is optional
and identified by type/value, not position.** The optional vocabulary
observed: a `coordinate` (spawn location), a player constant
(`#monster_player`, or `$GetUnitPlayerNumber(agent)` for "same side as"),
a `$concatenate(#ATTRIB_x, value)` attribute-value pair list, and the
bare string flags `"Override"` (bypass spawn gating) and `"MaxHP"` (spawn
a building pre-completed at full health). Casing is inconsistent across
call sites (`"Override"`/`"override"`) so **the string flags appear to be
case-insensitive** — UNVERIFIED as a guarantee, but shipped code relies
on it. `$SpawnUnit` **returns the spawned agent** (`Bandit_Event`'s
`rogue = $SpawnUnit(...)` then `$Advance_to_Level(rogue,3)`;
`Dead_Heroes`' `Hero = $SpawnUnit(...)`), which is how you post-process a
spawn.

- **`$Concatenate(#ATTRIB_x, value)`** — now with a concrete purpose
  rather than §14's "pure plumbing": it is the *only* way to set an
  attribute at spawn time rather than after. Used for
  `#ATTRIB_NumHealingPotions` (starting inventory) and
  `#ATTRIB_Artifice` (behavior override, which **must** be set at spawn
  because `check_override_behavior` runs during `monster_birth`).

**Coordinate helpers (a family, all used here, none previously
documented):**

| Primitive | Meaning |
|---|---|
| `$RandomCoord(agent, -1)` | anywhere on the map (`-1` = unbounded) |
| `$RandomCoord(agent, radius)` | within `radius` of the agent |
| `$RandomCoord(agent, min, max)` | in an annulus (`Undead_Horde`: `800, 1000`) |
| `$RandomCoord(coord, radius)` | also accepts a *coordinate* as origin (`Demo.gpl`'s `$randomcoord(coord,250)`) |
| `$RandomEdgeCoord($RandomNumber(4))` | random point on one of the 4 map edges; the ubiquitous "off-map attackers arrive" idiom. `Special_Events.gpl` wraps it as `function on_perimeter() is coordinate` |
| `$ClosestMapEdge(agent)` | nearest edge point to that agent (`Goblin_Blockade`, so raiders arrive near the marker they'll hunt) |
| `$FarthestMapEdge_OnMap(agent)` | farthest edge point (`Wandering_Heroes`, `Bandit_Event`) |
| `$FarthestMapCorner(agent)` | farthest corner (`Spawn_Paladin`) |

**Choosing near vs. far edge is the whole difference between a threat
that reaches its target immediately and one the player has time to
intercept** — worth being deliberate about.

**Player-data and damage:**

- **`$GetPlayerData(palace, "gold")` / `$AdjustPlayerData(palace, "gold",
  delta)`** — string-keyed treasury access, negative delta to subtract.
  §5 documented `$AdjustPlayerData` in the revenue path; this batch adds
  the read side and confirms `"gold"` is a string key rather than a
  constant.
- **`$CreateSpellUnit(caster, "<SpellName>", target)`** — instantiate a
  spell with no hero casting it. Used for `"Earthquake"` and
  `"Meteor_Storm"`. **Allegiance comes from `caster`** (17.2's borrowed-
  caster workaround).
- **`$GetSpellAttribute("<spell>", "<field>")`** — read a spell's own
  tuning data (`Demo.gpl`: `"teleport"`, `"effector_duration"`). Keeps
  script-applied effects in sync with spell XML.
- **`$player_spell_attack(target, damage, damage_minimum)`** → wraps
  `$spellhit` + `$spelldamage($nullagent(), ...)`. **`$spelldamage` with
  `$nullagent()` is the unattributed/environmental damage path.** Both
  are GPL-defined and exist in base (`make_attack.gpl` line 490).
- **`$Advance_to_Level(agent, level)`** and **`$spawn(agent)`** (trigger a
  lair's own spawn logic) — two more base+mx GPL helpers reused as quest
  levers.

### 18.10 Primitives, constants and quirks this guide hadn't documented

§14's sweep explicitly left "`$Move`/`$StopMoving`/`$IsMoving`/… and most
of the victory-condition/player-data/inventory-item primitives" as
spot-checked only. Quest actives are where that family actually lives, so
they get covered here. Every row was read at its definition or confirmed
across two or more shipped call sites, as noted.

**Movement, arrival and presence:**

| Primitive | Contract as used here |
|---|---|
| `$Move(agent, agentOrCoord)` | start pathing; check `$IsMoving(agent) == False` before re-issuing, or you cancel your own path every tick |
| `$Move(agent, target, "avoid_vehicles")` | **optional string flag**, 8 shipped call sites, all in "get there safely" tasks (18.3). Effect engine-side, **UNVERIFIED** |
| `$Hide(agent, building)` | enter/occupy a building; §14 listed `$Hide`/`$UnHide` but not this "travel into it" usage |
| `$IsHidden(agent)` / `$InsideBuilding(agent)` | the two arrival tests for a `$Hide` (18.3, 18.9) |
| `$IsAdjacent(a, b)` | arrival test for a non-building target; also `ReachedTargetDistance`'s fallback when arrive-distance ≤ 15 (`Travel_to.gpl` lines 183-190) |
| `$DeleteGamePiece(agent)` | remove without death — no death script, no loot, no gravestone |
| `$flee(agent, #intent_*)` | flee toward home, with a display intent (18.6) |
| `$notvalid(agent)` / `$isvalidgamepiece(agent)` | the two guards used before dereferencing a stored agent |

**Ownership, teams and identity (all writable at runtime):**

| Primitive / field | Contract |
|---|---|
| `$SetUnitPlayerNumber(agent, #Player_N)` | change an existing agent's owner — the defection/rescue primitive (18.9) |
| `$NeutralTeamNumber()` | the "make peace" counterpart to §16.2's `$NewTeamNumber()`; fed to `$SetPlayerTeamNumber` |
| `$GetPalace(agent)` | that agent's own palace — the multiplayer-safe alternative to `$ListMember($ListPalaces(),1)` |
| `agent's "Type"` / `"Subtype"` / `"EnemyType"` | plain writable strings that redefine what list queries and targeting see (18.6) |
| `$istitlealive(palace, title)` | GPL helper (`epic_quest_scripts.gpl` line 7) for "are any of these left?" |

**Lists and filtering:**

- **`$ListSubtypes(list, "subtype")` returns a new filtered list** and does
  not filter in place — confirmed by contrasting `hooligan.gpl` line 33
  (assigns the result) against `Curse_Active` (discards it, a real no-op
  bug). Same contract as `$ListTitles`.
- **Non-obvious `$ListObjects` type strings seen in this batch**, adding to
  §17.5's list: `"Hooligan"` (a quest NPC's own type, from its `.dat`
  record), `"Hidden"` (a unit inside/behind something — how the captive
  peasant is found), `"Special"` (the ring site), `"special_item"`
  (chests). **The type string is whatever the unit's `.dat` record says**,
  so a custom quest NPC can define its own query key.

**Per-agent scratch fields declared in `prototype.gpl` (18.2):**
`QuestScript`, `StartingScript`, `Special_Boolean`, `Counter`,
`Coord_Home`, and `SpecialScript`/`SpecialList` (guild-family buildings
only).

**Constants introduced or first cited here:**

| Constant | Value | Source | Meaning |
|---|---|---|---|
| `#Arrest_Hooligan_Dist` | 50 | `globals.gpl` 676 | follow stop distance |
| `#followBored` | 20 | `globals.gpl` 838 | ticks before a follower steps aside |
| `#Is_Free_Task_Range` | 2000 | `globals.gpl` 800 | contention search radius |
| `#is_free_task_max_heroes` | 2 | `globals.gpl` 802 | extra claimants allowed |
| `#think_bubble_time` | 1000 | `globals.gpl` 526 | thinking effector duration |
| `#Hooligan_Wander_Mod` | 3 | `globals.gpl` 423 | × sight range = wander radius |
| `#default_spawn_treasure_dist` | 500 | `globals.gpl` 793 | min chest distance from palace |
| `#HChalice_Chest_Respawn_Base` / `_Mod` | 90000 / 90000 | `globals.gpl` 678, 680 | 1.5-3 game days |
| `#WCurse_Dumb_Penalty` | 5 | `globals.gpl` 681 | intelligence penalty |
| `#wiz_curse_mod` | 5 | `epic_quest_scripts.gpl` 3725 | × lair spawn rate (slows spawning) |
| `#magical_repair_amount` | 10 | `globals.gpl` 495 | HP per repair effector |
| `#building_normal_state` / `_force_inactive` / `_force_active` | 0 / 1 / 2 | `globals.gpl` 22-25 | `#ATTRIB_ForceBuildingState` values |
| `#Intent_Delivering_Ring` | 79 | `defines.gpl` 87 | shares the intent/message/sign index space |
| `#intent_arresting_hooligan` | 117 | `defines.gpl` 125 | same |
| `#Qitem_Magic_Ring` | 13 | `QItems.gpl` 14 | — |
| `#QNumber_Wizards_Curse` / `_Magic_Ring` / `_Holy_Chalice` | 19 / 16 / 3 | `globals.gpl` 661, 658, 645 | quest-mode register values |

**Defensive-coding warnings — real defects in this shipped file, cited so
nobody clones them:**

- **`Drop_Ring` assigns `BasicScript` twice and never restores
  `BackScript`** (18.2). Restore all four slots.
- **`Curse_Active` discards its `$ListSubtypes` result** (18.7) — the
  filter is a no-op.
- **`Guardian_hero_Eval_Nearby`'s last three lines are unreachable**
  (18.6) — its `$clearlist` never runs.
- **`Hooligan_Check` has no early exit**, so the *last* matching candidate
  wins the `Target` assignment rather than the first (18.5).
- **`Curse_Active`'s lightning sweep has no player filter** while the query
  above it does (18.7).
- **`Be_Dumb` declares an unused `boolean Effector`, and two of its
  comments describe the wrong branch** (18.4).
- **`Deliver_Ring` and `Steal_Ring` differ in whether their idle branch
  runs the `EvaluationScript`** — one is commented out (18.3). If you clone
  one, decide deliberately.
- **`Curse_Active`'s `Best_Score` is read before assignment** (in
  `Temp_Score >= Best_Score` on the first iteration) — the same
  implicit-zero-init assumption §17.2 flagged in `Bandit_Event`, still
  **UNVERIFIED** as a language guarantee. Initialize it.

### 19.4 Music: a string-named engine callback and a plain-text track registry

Genuinely new — nothing in §1-§18 covers game music, and it turns out to
be one of the most modder-friendly subsystems in the codebase: three
primitives, one editable text file, no XML and no CAM.

All four quests call `$Setup_Quest_Music (AIRootAgent)`, and the win paths
call `$Reset_Quest_Music`; `$Play_Endgame_Music` fires at the dramatic
peak (`LH_Barrows_Death` when one barrow remains, line 561; Vale stage 18,
line 1043; Clash stage 7, line 1806). All three are ordinary GPL
functions in `GPLMx/mx_Music_Player.gpl` (base twin:
`GPL/Music_Player.gpl` — this one module *is* present in both trees, read
both, they are identical apart from one blank line). Read in full:

```gpl
Function Setup_Quest_Music (agent ThisAgent)
Begin
    $SetMusicStoppedCallback ("Quest_Music_Stopped");   // by STRING name
    $PlayMusic (#Early_Theme);
End

function Quest_Music_Stopped (integer lastTrack)
Begin
    lastTrack = $LastMusicTrack();          // NOT the parameter — see below
    If (lastTrack < #Midgame_Theme)  lastTrack ++;
    Else if (lastTrack == #MidGame_Theme) lastTrack --;
    $PlayMusic (lastTrack);
End
```

**The three primitives** (all engine-side; no GPL definition exists for
any of them, and `mx_Music_Player.gpl` + `Music_Player.gpl` are their
only call sites anywhere in the tree):

| Primitive | Signature | Notes |
|---|---|---|
| `$PlayMusic` | `(integer track)` | Starts a track immediately, replacing what's playing |
| `$SetMusicStoppedCallback` | `(string functionName)` | Registers a GPL function **by name string**, called when a track ends |
| `$LastMusicTrack` | `() is integer` | Returns the track GPL last *requested* |

Four things a modder can act on:

1. **`$SetMusicStoppedCallback` is a string-named callback registration —
   a distinct engine-hook mechanism from everything §1-§18 catalogued.**
   Script slots take a `function` value (`$MyFunc`); this takes a quoted
   name. So the callback target is resolved by name at fire time, which
   means **a mod can register its own function without any engine, XML or
   `.dat` change** — just `$SetMusicStoppedCallback("My_Music_Handler")`.
   Compare §17's `$LookupFunction` framework: same "resolve GPL by name"
   idea, applied to a different subsystem.
2. **Trust `$LastMusicTrack()`, not the callback's own parameter.** Both
   handlers immediately overwrite their `lastTrack` argument with
   `$LastMusicTrack()`, and the shipped comment says why, verbatim: "The
   input track is the track that just finished, this may not be what gpl
   had requested." So the engine may substitute a different track than
   asked for, and the parameter reports reality while
   `$LastMusicTrack()` reports intent.
3. **The track numbers index a plain text file.** `#early_theme` 3,
   `#midgame_theme` 4, `#endgame_theme` 5 (`mx_Globals.gpl` lines 765-767,
   identical in base `globals.gpl` lines 740-742). `Data/MusicTracks.txt`
   is six lines: `GeneralTheme.mp3`, `GeneralTheme.mp3`, `EarlyGame.mp3`,
   `MidGame.mp3`, `EndGame.mp3`, `EpicQuest.mp3`. **Reading it as
   1-indexed lines up the constants with the filenames exactly**
   (3→EarlyGame, 4→MidGame, 5→EndGame). Stated as an inference from that
   name alignment, not a confirmed engine fact — a 0-indexed reading
   would have `#early_theme` play MidGame.mp3, which contradicts the
   function names, but nothing in source proves the indexing base.
4. **Track 6 (`EpicQuest.mp3`) is orphaned, and tracks 1-2 are never
   requested.** Grepped `$PlayMusic` across the whole tree: every call
   site passes `#Early_Theme`, `#Endgame_Theme`, or a value derived from
   the 3↔4 bounce. So there is a shipped music track no shipped GPL ever
   plays, in the same category as §9's Zoo. `$PlayMusic(6)` from a quest
   script should reach it, and **appending a 7th line to
   `MusicTracks.txt` plus `$PlayMusic(7)` is the obvious route to custom
   quest music — UNVERIFIED, not tested in-game**, but the mechanism has
   no XML/CAM/exe dependency to block it.

**Also new here: the state machines are trivially different, which is the
whole "quest vs freestyle" distinction.** `FreeStyle_Music_Stopped`
increments to `#Endgame_Theme` and then wraps back to `#Early_Theme`;
`Quest_Music_Stopped` bounces 3→4→3 forever and leaves track 5 for
`$Play_Endgame_Music` to fire explicitly. `Reset_Quest_Music` is a
one-line alias for `Setup_Quest_Music` — used on victory, so the endgame
track stops looping and the ambient bounce resumes (the comment on every
call site in this file reads "Set quest music back to bounce between early
and mid game tracks").

### 22.2 The reusable-helper catalogue — the high-value half of this file

**Why this subsection exists:** §17-§21 repeatedly *called into* this
file without reading it. These are the functions other files invoke, with
signatures, contracts and gotchas, read in full at the cited lines. All
line numbers are `GPL/Rules/epic_quest_scripts.gpl` unless stated. All of
them exist in `mx_Epic_Quest_Scripts.gpl` too (22.0) — the only
base-vs-mx split in this catalogue is `High_Level_Hero_Birth`, which
lives in a different file in each mode.

**One property they all share, and it is the whole reason they're
reusable:** every one of them takes the palace (or an explicit list) as
its scope argument rather than reading a global, so they work unchanged
from a quest entry function, a poll thread, or a death handler.

#### Census / predicate helpers

| Function | Signature | Contract |
|---|---|---|
| `istitlealive` (7) | `(agent palace, string title) is boolean` | Unions `$ListObjects(palace,"monster",…)` **and** `"invisible"`, both `#NoHiddenMap`, `$AddLists`, then `$ListTitles(…, title)`; TRUE iff nonempty. **The idiomatic "is the named boss still out there" test** — 5 shipped call sites (Slave Pits, Dark Forest, Liche Queen, Wizard's Curse, plus mx), every one of them with the raw `$ListSize(monsters)==0` version commented out directly above. **Does *not* include `"camouflaged"`**, unlike `all_enemies_dead` — a boss under a camouflage spell would read as dead. |
| `all_enemies_dead` (1195) | `(agent thisagent) is boolean` | Six-class union census — `"building"`, `"lair"`, `"monster"`, `"hero"`, `"Invisible"`, `"camouflaged"` — each queried with `#NotMyTeam, #NoHiddenMap, #InsideOtherUnits`, merged with `$AddLists`, then filtered through a **hardcoded seven-title exclusion list** (`ratman`, `Giant_rat`, `sewer`, `graveyard`, `skeleton`, `zombie`, `troll`) of things that "don't count as an enemy". TRUE iff the remainder is empty. §20.9 flagged this as a ready-made victory helper and that reading is confirmed. **Caveat for reuse: the exclusion list is literal source, not data** — clone the function if your quest wants a different one. One shipped caller (`DOR_victory` 1114). |
| `no_monsters_titled` (2108) | `(agent thisagent, string title) is boolean` | The negative-form twin of `istitlealive` with the `#NotMyTeam, #InsideOtherUnits` filters `istitlealive` lacks. **Structurally inconsistent with itself:** the `"monster"` half uses `$ListTitles`, but the `"invisible"` half hand-rolls `if (whatever's "title" == title)`. Since the two shipped callers pass `"Rock_Golem"` and `"dirgo"` while the shipped unit titles are `Rock_Golem` and `Dirgo`, **the `$ListTitles` half is evidently case-insensitive on the title value and the `==` half may not be** — see 22.8 for how far that goes as a claim. |
| `remove_statues` (1880) | `(list stuff) is list` | Returns a copy of `stuff` with every member titled `"statue"` dropped. Exists because Elven Treachery's "kill all enemy buildings" test would otherwise never pass — the map's statues are enemy buildings. **The general pattern (`$RemoveTitles` is the built-in for this, §19.6) but hand-rolled**, and worth knowing as the shape to copy when the thing you must exclude is a title rather than a class. |

#### World-setup helpers (call these from the quest entry function)

| Function | Signature | Contract |
|---|---|---|
| `setup_starting_treasure` (4099) | `(list chests, integer startgold, integer randomgold)` | `$AdjustAttribute(chest, #ATTRIB_gold, startgold + $RandomNumber(randomgold))` on each. **Takes a list you built yourself** — every shipped caller does `$ListObjects(palace,"special_item",…)` then `$ListTitles(…,"treasure_chest")` first. Shipped ranges: 100+d100 (Bell Book) up to 800+d300 (Crown). |
| `setup_random_Treasure` (4112) | `(integer how_many, integer Dist_from_palace)` | Spawns `how_many` chests, each a uniform pick of `Treasure_Chest1..4`, at `$RandomCoord(Palace, Dist_from_palace, -1)`, owned by `#Monster_Player`, with `"maxhp"`. **Finds the palace itself** (`$ListMember($ListPalaces(),1)`) — so unlike its sibling it takes no agent. Every shipped call passes `#default_spawn_treasure_dist` as the second argument; counts run 20-65. |
| `Setup_Respawning_Lairs` (3070) | `(agent Palace)` | Sets **every** `"Lair"` in `$ListObjects(Palace,"Lair",-1,…,#NoHiddenMap)` to `IGDeathScript = $Respawning_Lair_Death`. §17 documented it as "whole rules change in one call"; the body confirms that and adds the gotcha: **it is indiscriminate**, so a quest that needs one special lair exempt must re-override it *after* the call. `HOLY_CHALICE` does exactly that (line 456 restores `Chalice_Site's "IGDeathScript" = $Hidden_Chalice_Death` with a comment saying why). |
| `Setup_Multispawning_Lairs` (4070) | `(list Lairs, integer Num_Spawns)` | Sets each member's `IGDeathScript = $Lair_Multispawn_Death` **and** `"Multi_Spawn_Num" = Num_Spawns` — a death payload plus its count. Takes a list, so it composes: `LICHE_QUEEN` (2669-2683) partitions its lairs into two lists by title and calls it twice, at 2 and 6. |
| `Setup_Rescue_Heroes` (2838) | `(agent Palace, string GuildName, string Class, integer StartLevel)` | Finds the first `#NotMyTeam` building titled `GuildName` and pushes **two** values onto its `"SpecialList"`: the class string, then the start level. Consumed by `rescue_buildings`. **Its own header comment is the contract: "CALL THIS FUNCTION BEFORE SETUP_RESCUE_BUILDINGS!"** Call it once per hero you want; `SLAY_DRAGON` (1381-1386) queues six across six different guild titles, `HOLY_CHALICE` queues four Paladins into the *same* guild. This is the writer side of §20.4's two-members-per-record `SpecialList` protocol. |
| `setup_rescue_buildings` (2858) | `(agent palace)` | Sets `bldg's "type" = "unknown"` on every `#NotMyTeam` building, and additionally `"enemytype" = "nothing"` for `Dwarven_settlement`, `ballista_tower` and `guardhouse`. §20.4 documented this; the base body is identical. **The `"enemytype"` exception list is the interesting half**: those three are the buildings that would otherwise shoot at the monsters guarding them. |
| `setup_rescue_pets` (2884) | `(agent palace, string whatpet)` | Sets `"type" = "pet"` on every `#NotMyTeam` monster titled `whatpet`. One shipped caller (`DAY_OF_RECKONING`, `"Daemonwood"`). |
| `gold_bonus` (787) | `(agent palace, string what_building, integer bonus_amount)` | `$AdjustAttribute(bldg, #ATTRIB_gold, bonus_amount)` on every building with that title. Two callers, both `"trading_post"` (8000 in Dark Forest, 9000 in Tomb). **`#ATTRIB_gold` on a building is a stock, writable per-building purse** — same attribute the treasure chests use. |
| `setup_hero_level` (1178) | `(agent thisagent, integer explevel)` | `$Advance_To_Level(hero, explevel)` + `$SetAttribute(hero, #ATTRIB_StartedwithThisUnit, 1)` for every `#MyPlayer, #NoHiddenMap` hero. §20.7 documented the mx twin; **the base body is identical line for line**, which closes one of §20.9's "base twin present, body unconfirmed" items. `DAY_OF_RECKONING` calls it with `50`. |

#### Per-tick / runtime helpers

| Function | Signature | Contract |
|---|---|---|
| `rescue_buildings` (2953) | `(agent palace)` | **Call this every poll tick, not once.** Claims every `"unknown"`-typed `#NotMyPlayer` building: reassigns player number, fires a message (`#message_rescued_statue` or `#message_rescued_building` + `$PlaySound(palace,"Advisor_New_Outpost","VFX_ADVISOR")`), flips `"type"` back to `"building"`, restores `"enemytype" = "monster"` for the three exception titles, `$RunThread`s a rescued Guardhouse's `"Guard_Spawn_Function"`, and — if the building `$HasAttribute("SpecialList")` — drains that list two members at a time, `$SpawnUnit`ing the class and stashing the level, then re-seats the levels list and installs `Setup_High_Level_Members` on the guild's `"SpecialScript"` at a 500 ms interval. **A rescued statue instead grants `#statue_loyalty_boost` to every `#MyPlayer` hero inside it** (filtered on `guy's "subtype" == "hero"`). Nine quests call it; three call it from `rescue_keep_playing` after victory (22.4b). |
| `rescue_pets` (2904) | `(agent palace)` | Claims every `"pet"`-typed `#NotMyPlayer` monster: player number, `"type" = "hidden"`, `$CreateEffector(pet,"charm_icon",1,"infinite")`, `ActiveScript = $pet_ready` retimed to `#charm_delay_time`, `$StopMoving`. |
| `pet_ready` (2930) | `(agent thisagent)` | The arming callback: `"type" = "hero"`, `"enemytype" = "monster"`, interval back to `#Normal_cycle`, `$Reset_Tasks`. **The delay is implemented as the unit's own `ActiveScript` interval** — §20.4 documented this; base body identical. |
| `Setup_High_Level_Members` (3036) | `(agent ThisAgent)` — thread on the guild's `"SpecialScript"` | Waits until the guild's `"Members"` list is non-empty, then `$Advance_To_Level`s each member to the next level popped off `"SpecialList"`, and `$KillThread`s itself when the list empties. **This is where a rescued guild's queued heroes actually get their levels** — they can't be levelled at spawn because they aren't guild members yet. **Contains a shipped defect (22.8).** |
| `Magical_Repair` (4148) | `(agent ThisAgent)` | Adds `#magical_repair_amount` HP, clamped at MaxHP. Not called from this file at all — it's here for other modules (the enchanted Wizard's Tower path). Carries a commented-out `$CheckEffector`-guarded `$CreateEffector` block, i.e. the intended visual was cut. |
| `High_Level_Hero_Birth` | `(agent ThisAgent)` — **`GPL/Hero_Births.gpl` 506; mx twin `GPLMx/mx_Hero_Births.gpl` 582** | Not in this file, but installed *by* it (`WIZARDS_CURSE` 3862 sets it as the enemy Wizard's `"BirthScript"`). Sets `#Attrib_StartedWithThisUnit`, **tail-calls `$Hero_Birth` (the §20.6c "add behavior then call the family handler" convention)**, then branches on `AIRootAgent's "Quest_Number"`. **Only one branch is implemented** (`#QNumber_Wizards_Curse`: level 20, MaxHP+HP 50, `#attrib_Armor_basic_damage` +4, `$LearnSpell` ×2, +5 healing potions). **So this is a shared, extensible per-quest hero-specialisation hook: add your own `#QNumber_*` branch and any quest can have bespoke starting heroes without a bespoke birthscript.** |

#### Small utilities worth knowing

- **`avg_coords(coordinate, coordinate) is coordinate`** (765) —
  `$GetX`/`$GetY`/`$MakeCoord` midpoint. One caller, which uses it to put
  a signpost halfway between the palace and a quest building. Trivial, but
  it is the only shipped example of arithmetic on coordinates.
- **`$random_to_percent(integer amount, integer fraction) is integer`** —
  **not in this file**; defined in `GPL/TaskModules/Buildings/
  Auto_Revenue.gpl` 268 (mx twin `mx_Auto_Revenue.gpl` 265). Returns
  `amount - amount/fraction + $RandomNumber(amount/fraction)`, i.e. with
  `fraction = 3` it is "2/3 of the interval plus up to another 1/3."
  **Its own comment says 3/4 + random 1/4, which is only true for
  `fraction = 4`** — the comment describes a different argument than every
  shipped call passes (all pass 3). Use the formula, not the comment.
  It is the interval jitter helper used where §19 used `$Random_Time`.
- **`$Create_Sign(agent palace, string signtype, expression message,
  coordinate where)`** — spawns a sign object and posts a message on it in
  one call, replacing the shipped `$ListObjects("color")` +
  `$ListTitles` + `$Post_Message` three-step. Two callers here
  (`HOLY_CHALICE` 451, `DARK_FOREST` 757). Defined in
  `GPL/TaskModules/Buildings/Message_Signs.gpl` 8 (mx twin
  `GPLMx/TaskModules/Buildings/mx_Message_Signs.gpl` 8) with the exact
  signature `(agent ThisAgent, string type, integer Message,
  coordinate Loc)` — note the message parameter is typed `integer`, so
  the `#sign_*` expression constants are plain integers. Body not read.

### 22.6 The rest of the new material, one item each

Everything here is genuinely absent from §16-§21. Kept to a paragraph
apiece; each is cited to the line that proves it.

**a) Victory by developing your own city, and `$EnableUnitType` as the
reward.** §16 documented `$DisableUnitType` as a build restriction. Its
inverse, **`$EnableUnitType("<type>")`**, is used here to *unlock* content
mid-quest, and that turns out to be the base game's main progression
device. `barren_victory` (83-152) is a five-stage chain in which **three of
the five stages test the player's own construction**, not enemy
destruction: `$ListCompleted($ListTitles(bldgs,"guild"))` non-empty, then
`palace's "level" == 2 && $GetAttribute(palace,#ATTRIB_currentstagebuilt)
== 1`, then the same at level 3, then a lair gone, then a completed
Fairgrounds — where the Fairgrounds was `$DisableUnitType`d at setup and
`$EnableUnitType`d by stage 4. `dark_forest_victory` (863-889) is the
dramatic version: finding one building unlocks **14 building types plus
`$ElvesVoice_setOperative(1)` and `$dwarvesVoice_setOperative(1)`** in one
block — and that is also the first shipped evidence that the two voice
toggles take **1 to re-enable**, which §20.7 could only infer from the `0`
calls. `Slay_Dragon_Victory` (1457-1468) adds the conditional form: unlock
`Dwarven_Settlement` only once the player has found a completed one.
**Two supporting primitives:** `$ListCompleted(list) is list` (filters to
finished buildings) and **`$ListCompletedTitles(agent, string class,
string title, integer range) is list`** — a single call replacing
`$ListObjects` + `$ListTitles` + `$ListCompleted`, used twice in Slay the
Dragon (1460, 1494).

**b) The slot convention is a convention, and two quests invert it.**
§19.1 established `"VictoryCondition"` = poll, `"VictoryCondition2"` =
sequencer. `DOR_victory` (1009) and `fertile_victory` (1970) put **the
escalation sequencer in the `"VictoryCondition"` slot**, re-pacing it with
`$SetThreadInterval(AIRootagent's "VictoryCondition", N)` per stage
(DOR: 300000, 300000, 240000, 240000, then back to
`#VictoryCondition_callback_frequency` for the final win check; Fertile:
150000 → 75000 → 300000 → 180000 → 200000 → 2000). `DOR_Victory2` then
carries the fast upkeep at 5 000 ms. **So the slots carry no engine
meaning at all — they are named fields on the root agent and nothing
enforces which job goes where.** The Fertile Plain case also shows the
tidy trick of **dropping the interval to 2 000 ms for the final stage**,
with the shipped comment "set it to 10 minutes - new: set it to 5 seconds
for victory checking": one thread can be a slow pacer and then a fast
poll.

**c) `$GetNearestHiddenCoord(agent, coordinate) is boolean` — an
out-parameter primitive.** `dark_forest_events` 914:

```gpl
if ($getnearesthiddencoord (palace, dest) == FALSE)
    dest = $locationof (palace);
```

**Two things are new here.** The utility: it finds the closest still-fogged
coordinate to an agent, which is exactly what you want for "a hero
appears out of the unexplored woods." And the calling convention: **it
returns a boolean and writes its result into the coordinate variable
passed as the second argument** — the only shipped GPL primitive found in
this pass that takes an out-parameter. The idiom is inseparable from the
fallback: the return is FALSE when there is no hidden area left, and `dest`
must not be trusted in that case.

**d) The rain-of-lightning random harasser.** `DOR_Victory2` (1153-1176)
is the cleanest reusable "ambient divine wrath" recipe in the codebase:
roll `$RandomNumber(100) < 75`, union `"monster"` + `"hero"` +
`"building"` via three `$ListObjects` + two `$AddLists`, pick
`$ListMember(mainlist, $RandomNumber($ListSize(mainlist)) + 1)`, and call
`$lightning_bolt_hit(target)` directly. **It deliberately does not filter
by team** — the player's own heroes and buildings are valid targets, which
is the point. The direct spell-effect call is §21.6c's pathway
(no caster, caller pays nothing); the `+1` on the random index is the
standard 1-based-list correction.

**e) The pre-parked slot as a deferred callback.** `SLAY_DRAGON` (1414)
assigns `AIRootAgent's "victoryCondition2" = $slay_dragon_delay;` with the
shipped comment `// don't run this!!!` and **never threads it**.
`slay_dragon_delay` (1591) does one thing: set `Quest_Flag_4 = True`. The
runner is elsewhere — **`Vendral_Death` in `GPL/Monster_Deaths.gpl` 140**
does `AIRootAgent's "end_coord" = $locationof(thisagent);` then
`$NewThread(AIRootAgent's "VictoryCondition2", 5000)`, with the comment
"this is just a delay, so people can see vendral die." **So the quest file
pre-loads a function into a slot and a death handler in a different file
fires it with a delay, without needing to know the function's name.** This
is a third use of the script-slot vocabulary beyond §18.2's swap-and-stash
and §21.3's slot-as-latch: **the slot as a one-shot mailbox between two
files.** The victory poll then just watches `Quest_Flag_4`, so the
5-second delay buys the death animation.

**f) `#Allow_Cloned_Quest_Item` — how to give the same quest item to
everyone.** `Slay_Dragon_Victory` 1560-1566:

```gpl
Heroes = $ListSubtypesInRadius (Palace, "Hero", "Hero", -1);
Foreach Hero in Heroes do
    If ($AgentHasInventoryItem (#QItem_Magic_Sword, Hero) == False)
        begin
            $CreateNewInventoryItem (#QItem_Magic_Sword, Hero, #Allow_Cloned_Quest_Item);
            $createeffector (hero, "got_item", 0);
        end
```

Three new pieces: **`$AgentHasInventoryItem(#QItem, agent) is boolean`**
(the per-agent test, distinct from §21's map-wide
`$FindInventoryItem`); **`$CreateNewInventoryItem`'s optional third
argument `#Allow_Cloned_Quest_Item`**, which is what lets a `#QItem_*`
exist on more than one holder at a time — implying the default is a
uniqueness constraint; and **`$ListSubtypesInRadius(agent, class,
subtype, range)`**, a combined class+subtype+radius query. The
`$CreateEffector(hero,"got_item",0)` is §13's duration-0 form used as a
one-shot "you got something" sparkle.

**g) Retiming another agent's engine-owned thread, and `$IsRunning`.**
`Slay_Dragon_Victory` 1441-1454 reaches into a *monster's*
`"SleeperScript"` — a slot no earlier batch has documented — and does
`$setthreadinterval(Vendral's "sleeperScript", 90000)` to make the boss go
dormant sooner on his first appearance; later (1533-1539) it kills the same
thread outright, guarded by **`$IsRunning(<slot>) is boolean`**. Two
transferable facts: **`$SetThreadInterval` and `$KillThread` work on
another agent's slots, not just the root agent's**, and `$IsRunning` is
the guard to use before killing a thread you did not start. `"SleeperScript"`
itself is the stock dormancy timer for map bosses — its writer was not
traced, so **what installs it is UNVERIFIED**; this quest only retimes it.

**h) `$SetDrawEffects(agent, string effect, integer)` — recolor without
art.** `TOMB_DRAGON` 1653: `$SetDrawEffects(vampire, "gray", 0)` on each
vampire it is converting into a rooted `$returning_guardian`. **A visible
per-agent tint applied from GPL with no overlay, no effector and no new
sprite** — the cheapest way to mark a unit as special. Only one shipped
call site in this file, `"gray"` is the only value seen, and **the argument
set (what other strings work, what the integer means) is engine-side and
UNVERIFIED.**

**i) Temporary invulnerability, built from the `"type"` register plus two
attributes.** `GOBLIN_HORDES` (2405-2415) needs its quest-critical enemy
Wizard's Guild to survive the early game:

```gpl
Guild's "Type" = "Invulnerable";
$SetAttribute (Guild, #ATTRIB_NotFlaggable, 1);
$SetAttribute (Guild, #ATTRIB_NotSpellTarget, 1);
$MessageFlag (Guild, #message_ghordes_invulnerable_wguild);
```

and `Goblin_Events` (2558-2582) reverses all three when the timer says so,
re-finding the building by **querying the `"Invulnerable"` class**
(`$ListObjects(Palace,"Invulnerable",-1,…)`) and setting `"Type"` back to
`"Building"`. **This is a fourth confirmed value of §20.2's `"type"`
register (`"Invulnerable"`, joining `"unknown"`/`"pet"`/`"hidden"`/
`"invisible"`/`"camouflaged"`/`"Dead"`), and the first one used for
invulnerability rather than staging.** The three writes do three different
jobs: the `"type"` change takes the building out of every normal census
(including the one attackers use), `#ATTRIB_NotFlaggable` stops the player
targeting it with a reward flag, `#ATTRIB_NotSpellTarget` stops spells.
**All three are needed and all three are reversible.** Two footnotes: the
reversal branch sets `Quest_Flag_1 = True` where it clearly means
`Quest_Flag_3` (line 2576) — harmless only because the same branch
immediately `$killthread`s its own thread; and it is the first shipped use
of `#ATTRIB_NotFlaggable`/`#ATTRIB_NotSpellTarget` this guide has cited.

**j) `$EnchantWizTower(agent)`.** `GHorde_Wiz_Tower_Enchanter` (2628) is a
nullary-behaviour thread run **with the palace as its agent argument**
(`$NewThread(AIRootAgent's "SpecialSpawnScript2", 120000, Palace)`, and
called once directly at setup so it can fire immediately). Body: list
`#NotMyPlayer` buildings titled `"Wizards_Tower"`, and on a 50% roll call
`$EnchantWizTower(Tower)`. A single-argument engine primitive that turns a
Wizard's Tower into its enchanted state; **what "enchanted" changes is
engine-side and UNVERIFIED**, though `Magical_Repair` (22.2) sitting in
this file unreferenced suggests self-repair is part of it. Also note
**`"SpecialSpawnScript2"`** — a second spawn slot on the root agent, so
that vocabulary is at least two deep.

---

## Chapter 8: Quest Inventory

Every shipped quest, its entry function and the mechanisms it uses.

### 19.2 All four quests at a glance

Every mechanism named in the last column is either already documented in
§16-§18 or gets its own subsection below — no quest needs reading on its
own.

| Quest | Entry fn (line) | Threads | Win / lose test | Mechanisms used |
|---|---|---|---|---|
| Legendary Heroes | `LEGENDARY_HEROES` (8) | `Legendary_Heroes_Victory`, `Legendary_Heroes_Events`, `Legendary_Heroes_Time_Limit` | Win: zero `"AncientBarrow"` lairs left. Lose: never — the deadline only turns on a punishment | `$CreateNewInventoryItem` into lairs (19.7), per-instance `IGDeathScript` override (§17), `$SetUp_Respawning_Lairs` (§17), escalating `LH_Barrows_Death` staircase (19.3), `$CreateSpellUnit("Earthquake")` (§17), `$Make_PC_Hunter` at runtime (19.6), `UtilityScript` deadline (19.5), `heroes_to_upgrade` (19.5) |
| Valley of the Serpents | `VALE_SERPENTS` (606) | `Vale_Serpents_Victory`, `Vale_Serpents_Events`, then `Vale_Post_Victory_Events` | Win: zero `"SnakePit"` lairs. **Lose: zero `"Elven_Bungalow"` buildings** | 18-stage sequencer (19.3), `$DisableUnittype` on the very building you must protect (19.5), `$DeclareLoss` (19.5), post-victory continuation thread (19.5), elite-NPC-army recipe (19.9), `Snake_Pit_Spawn` lair spawn fn (19.7), `#force_Elf_Hunter` → `Elf_Hunter` (19.6) |
| Clash of Empires | `CLASH_EMPIRES` (1465) | `Clash_Empires_Victory`, `Clash_Empires_Events`, then `clash_post_victory` | Win: zero lairs of any kind | Three-way faction war via `$NewTeamNumber` (19.8), `$RevealWholeMap` per player (19.8), `$ListFamily` population equalizer (19.8), `Max_Simul_Spawns`/`Max_Stored_Spawns` retune (19.7), `#force_Monster_Hunter` → `Monster_Hunter` (19.6) |
| Darkness Falls | `DARKNESS_FALLS` (1891) | `Darkness_Victory`, `Darkness_Events` | Two-stage: all `"WightsTomb"` lairs gone **then** `$IsTitleAlive` false for both named bosses | `Special_Spawn_Type` + `Has_Special_Spawn` named-boss seeding (19.7), `$IsTitleAlive` (19.5), conditional-resurrection boss pair (19.10), `$setup_random_treasure` (§18), `$PlaySound` taunts (19.5), and a **shipped `=`-for-`==` bug** (19.3) |

### 20.1 All four quests at a glance

| Quest | Entry fn (line) | Threads | Win / lose test | Mechanisms used |
|---|---|---|---|---|
| Rise of the Ratmen | `RISE_RATMEN` (8) | `Ratmen_victory` (poll), `Ratmen_Events` (7-stage sequencer, first fire `$random_time(210000)`) | Win: `Quest_Flag_7` latched (Rhoden has been spawned) **and** `$IsTitleAlive(palace,"RhodenKingRat") == False` **and** zero `"BrokenSewerMain"` lairs. No loss condition | All documented: §19.3 sequencer (self-terminating variant, 20.0), §19.5b two-stage victory gate, §19.5a `$IsTitleAlive`, §19.5's `$PlaySound(palace,"<unittype>","taunt")`, §17's draw-without-replacement (`sewers -= place`), §16.1's inline `#ATTRIB_FirstStageBuilt, 1` filter. Only new touch: **spawning new lairs *onto the player's own buildings*** (20.6) |
| Scions of Chaos | `SCIONS_CHAOS` (315) | `Scions_victory` (poll only — no second thread) | Win: third enemy hero dead. No loss condition | **Enemy heroes as the boss chain (20.3)** — `$Advance_To_Level` + `"title"` retitle + `resist_critical` + HP bump on a live agent; **`$list_all_enemy_heroes` and the `"type"`-class union (20.2)**; **latch-on-appearance before testing disappearance (20.5)**; `$make_raider` mass conversion of `#CheckSubtypes,"Animal"` monsters; §17's `$FarthestMapCorner` + `$RandomCoord` |
| Urban Renewal | `URBAN_RENEWAL` (535) | `urban_victory` (poll); per-building `SpecialScript` and `ActiveScript` threads installed on **enemy** buildings | Win: zero enemy buildings of subtype `"guild"` or `"entertainment"`. No loss condition | **`ActiveScript` install on a non-guild building (20.6)** — the shipped worked example of §18.7's advice; **`$guild_destroyed_common(agent, function)` function-as-argument (20.6)**; **`$make_raider` on heroes and peasants (20.3)**; `$GetPlayerTeamNumber` guard + §19.8's `$SetPlayerTeamNumber`/`$NewTeamNumber` (20.4); per-building `IGDeathScript` count-down escalator (§19.3's `LH_Barrows_Death` shape); `$Hero_Generator` on enemy guilds — **already cited in §18.7 from this exact line** (574) |
| Vigil for a Fallen Hero | `VIGIL` (807) | `Vigil_victory` (poll, also drives `$rescue_buildings`), `vigil_events` (4-stage sequencer, self-terminating) | Win: zero `"Abomination"` monsters. No loss condition | **The rescue/defection subsystem (20.4)** — `$SetUp_Rescue_Buildings` + `$rescue_buildings` and the `"unknown"` staging type class; **`$setup_hero_level` (20.7)**; **`$ElvesVoice_setOperative` / `$dwarvesVoice_setOperative` (20.7)**; **a victory camera that tracks a live boss (20.5)**; §19.6's `$Make_PC_Hunter`-at-runtime + `#ATTRIB_sightrange` boost; §17's `$Concatenate(#ATTRIB_Artifice, #force_*)` spawn form |

### 21.1 All four quests at a glance

Every mechanism named in the last column is either already documented
(§16-§20, or 21.9's recombination list) or gets its own subsection below.

| Quest | Entry fn (line) | Threads | Win / lose test | Mechanisms used |
|---|---|---|---|---|
| Trade Routes | `TRADE_ROUTES` (8) | `Check_Market_Defeat` (poll, `VictoryCondition`), `Trade_Route_Spawn` (caravan pump, `SpecialSpawnScript`), `Trade_Route_Standard_Events` (7-stage fixed-cadence sequencer, `SpecialSpawnScript2`), `Spawn_Strangleweed` (`UtilityScript`, endless 8s) | **Neither is polled.** Win/lose both come from `CheckTradeVictory`, called from *outside this file* every time a caravan lives or dies; loss also if the player's last Marketplace is gone | **Externally-scored graded victory (21.3)** — 5 checkpoints × 4-5 outcome bands, and a script slot compared against a function value as a "already decided" latch; **`SpecialSpawnScript`/`2` slots (21.2)**; caravan spawn-at-map-edge-near-a-marker (21.9); §17.2's tier dispatchers + markers (21.0); §19.5c-style `$DisableUnitType` of `Marketplace1`/`Trading_Post` |
| Spires of Death | `SPIRES_DEATH` (822) | `Force_Spire_Spawns` (`SpecialSpawnScript`), `Check_Spire_Regeneration` (`SpecialSpawnScript2`); per-spire `ActiveScript` (scan/attack ping-pong) and `Spawn_Function` | Win: zero live `"SpireOfDeath"` lairs — **tested inside `Spire_Death`, no poll thread** | **Self-retiering lair (21.4)** — fewer spires ⇒ harder tier, with hero-level compensation, a `function`-valued `Spawn_Function` field swapped at runtime, `Attack_Action` swapped to a per-tier spell name, and `$SetEffectorDirection` as a visible tier readout; **tower scan/attack pair cloned from stock `Tower.gpl`** (21.9); `$SuperBuff` (21.7); victory-from-a-death-script (21.5) |
| The Siege | `SIEGE` (1237) | `Flag_Remover` (`VictoryCondition`), `Siege_Route_Spawn` (`VictoryCondition2`), `Enemy_Guild_Spawn` (`SpecialSpawnScript`), `Enemy_Actions` (`SpecialSpawnScript2`) | Win: enemy palace dead (its `IGDeathScript`) **or** enemy gold ≤ 2000, which force-kills the palace via `#ATTRIB_HP = -50` | **A GPL-implemented AI opponent kingdom (21.6)** — gold-budgeted hero recruitment, building-cast spells paid for by hand, `$PlaceRewardFlag` used *by* the AI, `SetEnemyResearch` writing `#ATTRIB_Research*`, surrender-to-peace via `$NeutralTeamNumber`, and the `Permanent_Hostility` flag that keeps a forced war from auto-reverting (21.6a); enemy-palace teardown (21.5) |
| Fortress of Ixmil | `FORTRESS_IXMIL` (2296) | `Day_Counter` (`VictoryCondition2`, 60s), `Fortress_Ixmil_Warp_Engine` (`SpecialSpawnScript`); fortress `ActiveScript` gun | Win: fortress destroyed (`Fortress_Death`) | **Phase-in/phase-out boss building (21.7)** — `$Hide(agent, marker, #TeleportInsideDestination)` / `$Unhide(agent, coord)` + `$FadeIn`/`$FadeOut`; **elapsed-time difficulty scaling (21.8)** off `day_counter` and a "days since last appearance" delta, including a float `SpawnPower` multiplier; a spawn-group list field (`grovelist`) for teardown; `"clear"` as a third `$SpawnUnit` string flag (21.7); the `$ResumeThread`-before-delete gravestone-bug workaround (21.7) |

### 22.1 All 19 quests plus Freestyle at a glance

One row is the entire treatment. **Every mechanism in the last column is
either already documented in §16-§21 or gets a subsection below** — no
quest needs opening on its own. "Poll" = the `"VictoryCondition"` slot at
`#VictoryCondition_callback_frequency`; "seq" = §19.3's self-pacing staged
sequencer in `"VictoryCondition2"`. Tier = which `end_game_script_*` the
quest installs on victory (22.3).

| Quest | Entry fn (line) | Threads | Win / lose | Mechanisms | New? |
|---|---|---|---|---|---|
| Barren Waste | `BARREN_WASTE` (27) | `barren_victory` (poll, 5-stage flag chain) | Win: build a Fairgrounds, after 4 prior milestones. No loss | **City-development victory (22.6a)**: guild built → palace L2 → palace L3 → `"Dark_castle"` gone → Fairgrounds built; `$ListCompleted`, `$EnableUnitType` as the reward | Tier: easy |
| Bell, Book & Candle | `BELL_BOOK_CANDLE` (161) | `bbc_victory` (poll) | Win: all 3 retitled altar lairs destroyed | Runtime `agent's "title"` retitle as a quest marker + `$CreateNewInventoryItem` payload (§18/§19.7); **sequential message flags (22.5)**; last-lair `special_spawn_type` swap so the finale isn't anticlimactic (§19.7) | Tier: easy |
| Quest for the Holy Chalice | `HOLY_CHALICE` (416) | `Holy_Chalice_Victory` (poll), `Holy_Chalice_Victory_2` (30-min deadline) | Win: flag set by `Hidden_Chalice_Death`. **Lose: deadline expires without it** | **`*_victory2` deadline arbiter (22.4c)**; rescue-heroes queue (22.2); `$SetUp_Respawning_Lairs` then a **per-agent re-override** of one lair's `IGDeathScript`; `$Setup_Special_Chests` (§18.8); `$Create_Sign`; `$DisableUnitType("Marketplace1")` to force chest economy | Tier: easy |
| Quest for the Crown | `QUEST_FOR_CROWN` (600) | `crown_victory` (poll) | Win: zero `"Crown_site"` lairs | Rescue subsystem (§20.4); `special_spawn_type` downgrade loop (vampire→werewolf); `rescue_keep_playing` handoff (22.4b) | Tier: medium |
| Dark Forest | `DARK_FOREST` (693) | `dark_forest_victory` (poll), `dark_forest_events` (seq, 2 stages, self-terminating) | Win: `"Witch_king_tower"` gone **then** `$istitlealive("witch_king")` false | **`$EnableUnitType` mass-unlock as the mid-quest reward (22.6a)** — 14 building types plus both voice toggles; `$gold_bonus` (22.2); `$avg_coords` (22.2); **`$GetNearestHiddenCoord` (22.6c)** | Tier: medium |
| Day of Reckoning | `DAY_OF_RECKONING` (944) | `DOR_victory` (**sequencer in the poll slot**), `DOR_Victory2` (5 s upkeep) | Win: `$all_enemies_dead` after 5 authored waves | **Slot-convention inversion (22.6b)**: escalation lives in `"VictoryCondition"`, upkeep in `"VictoryCondition2"`; **rain-of-lightning random harasser (22.6d)**; `$setup_hero_level(palace,50)`; `$setup_rescue_pets(palace,"Daemonwood")` | Tier: expert |
| Deal with the Demon | `DEAL_DEMON` (1233) | `demon_victory` (poll), `demon_victory2` (2×20-min deadline) | Win: hold 100 000 gold — **and it is then deducted**. Lose: deadline | **The 1.8 M ms interval ceiling and its tick-counting workaround (22.4d)**; `$GetPlayerData(palace,"Gold")` as a victory test; `$Hero_Generator` on every enemy guild (§20.6b) | Tier: medium |
| Slay the Dragon | `SLAY_DRAGON` (1358) | `Slay_Dragon_Victory` (poll), `Vendral_Spawner` (`SpecialSpawnScript`, 4-stage), `slay_dragon_delay` (**parked, never threaded here**) | Win: sword found → Dwarven Settlement built → Vendral killed | **Pre-parked slot as a deferred callback (22.6e)** — `Vendral_Death` threads it; `$ListCompletedTitles`; `$AgentHasInventoryItem` + **`#Allow_Cloned_Quest_Item` (22.6f)**; **`"SleeperScript"` retimed on another agent (22.6g)**; `$IsRunning`; conditional mortality via a birthscript flag | Tier: hard |
| Tomb of the Dragon King | `TOMB_DRAGON` (1607) | `Tomb_victory` (poll), `tomb_events` (seq, 3 stages **then an infinite trickle**) | Win: all lairs gone, final tomb spawned and destroyed | `$Setup_Multispawning_Lairs` (§17); **`$SetDrawEffects` recolor (22.6h)**; `$returning_guardian` rooted-guardian install; spawn-a-new-lair-on-victory-condition staging | none |
| Elven Treachery | `ELVEN_TREACHERY` (1786) | `elven_victory` (poll), `Elven_victory2` (30-min deadline) | Win: 50 000 gold **or** all enemy buildings+heroes dead. Lose: deadline | `*_victory2` deadline (22.4c); `$remove_statues` (22.2) as a filter that keeps a title out of a census | Tier: easy |
| The Fertile Plain | `FERTILE_PLAIN` (1935) | `fertile_victory` (**sequencer in the poll slot**, 8 stages, per-stage `$SetThreadInterval`) | Win: survive 7 waves, then `$no_monsters_titled` clear for two titles | Slot inversion again (22.6b); `$RandomEdgeCoord(#North/#South/#East/#West)` — **named compass constants**, not just `$RandomNumber(4)`; `$no_monsters_titled` (22.2) | Tier: hard |
| The Forsaken Land | `FORSAKEN_LANDS` (2131) | `forsaken_victory` (poll), `forsaken_events` (seq, 5 stages **then a repeating tail**) | Win: `"Dark_castle"` gone. No loss | Sequential message flags (22.5); caravan escort spawns with `$Concatenate(#ATTRIB_Sightrange,250)`; the repeating tail calls `$spawn_monsters(4,#EasyMonster)` — **the only pre-victory use of the tier library (22.3)** | none |
| Hold off the Goblin Hordes | `GOBLIN_HORDES` (2365) | `Goblin_victory` (poll), `Goblin_Events` (seq, 3 stages), `GHorde_Troll_Spawner_Setup`→`GHorde_Troll_Spawner` (`SpecialSpawnScript`), `GHorde_Wiz_Tower_Enchanter` (`SpecialSpawnScript2`) | Win: zero lairs | **Temporary invulnerability recipe (22.6i)**; **`Lair_extra_delay` retune (22.7)**; **`$EnchantWizTower` (22.6j)**; `#Monster_Spawn_Cap` enforced by hand (§19.7) — base-game confirming site; `SpecialSpawnScript2` as a second spawn slot; a **thread that replaces its own slot function** to become a different job | see 22.6i/22.7 |
| Vengeance of the Liche Queen | `LICHE_QUEEN` (2650) | `liche_queen_victory` (poll), `liche_queen_events` (seq, 3 stages, self-terminating) | Win: `"Liche_queen_lair"` gone **then** `$istitlealive("liche_queen")` false | Two-stage victory (§19.5b); `$Setup_Multispawning_Lairs` at **two different counts for two lair partitions**; `$PlaySound` taunts (§19.5) | Tier: medium |
| Rescue the Prince | `SAVE_PRINCE` (3084) | `prince_victory` (poll) | Win: `"tower_prison"` lair gone | Pure recombination — `$DisableUnitType` ×11, `$setup_starting_treasure`, `$Post_Message`, `end_coord` preset from a lair location | none |
| Quest for the Magic Ring | `MAGIC_RING` (3170) | `Magic_Ring_Victory` (poll), `Magic_Ring_Events` (one-shot) | Win: driven entirely by `Hidden_Ring_Birth`/`_Death` outside this file | `$SetPlayerTeamNumber(palace,$NewTeamNumber())` to start a war mid-quest (§19.8); `$SpawnUnit(…, $Concatenate(#ATTRIB_forcebuildingState,#Building_force_active))` — the **building-state** artifice channel, distinct from `#ATTRIB_Artifice`; `$GetPlayerTeamNumber` equality as an "are we still at peace" test | none |
| Free the Slaves | `SLAVE_PITS` (3336) | `slaves_victory` (poll), `slaves_events` (seq, 2 stages, self-terminating) | Win: all `"Slave_pits"` gone → boss `url_shekk` spawns → boss dies | Latch-on-appearance via `Quest_flag_4` (§20.5a); `"clear"` spawn flag (§21.7); `rescue_keep_playing` handoff (22.4b) | none |
| Brashnard's Sphere | `BRASHNARD` (3480) | `Brashnard_Victory` (poll), `Dirgo_Spawner` (`SpecialSpawnScript`, one-shot) | Win: all 7 `"Brashnards_Sphere"` lairs gone | **A shipped RGSEditor-data repair loop** (any lair with `MaxHP==5` is reset to 200, with the comment "coverup for RGSEditor booboo") plus a `$ListSize != 7` `$DebugOut` **map-integrity assertion** — both worth copying; 7 distinct `$CreateNewInventoryItem` shard payloads | none |
| The Wizard's Curse | `WIZARDS_CURSE` (3729) | `Wizards_Curse_Victory` (poll, 4-flag chain) | Win: spellbook delivered → werewolves killed **or** the enemy Wizard dies | Monster→hero conversion (`Varg's "Type" = "Hero"` + `$Guardian` + `$LearnSpell` ×2 + level 10) — §20.3's recipe, base-game instance; `$Curse_Active` (§18.7); `High_Level_Hero_Birth` (22.2); **a global lair-rate multiplier applied and later divided back out** (`#wiz_curse_mod 5`, lines 3729/3891) | none |
| *(Freestyle)* | `Freestyle` (4084) | — (delegates to `$SetVictoryCondition`, §16.2) | per the freestyle dropdown | **3 statements in base (22.4a)** | 22.4a |

---

## Chapter 9: Base vs Expansion Availability

Which files and mechanisms exist in base game vs the expansion only.

### 17.0 File-level scoping: two of these three systems are expansion-only

**Confirmed by directory listing, not inference.**
`SDK/OriginalQuests/GPL/Rules/` contains exactly five files:
`construction_rules.gpl`, `Demo.gpl`, `epic_quest_scripts.gpl`,
`Quest_Actives.gpl`, `victory_conditions.gpl`.
`SDK/OriginalQuests/GPLMx/Rules/` contains those five as `mx_`-prefixed
equivalents **plus** `Quests_1.gpl`, `Quests_2.gpl`, `Quests_3.gpl`,
`Random_Events.gpl`, `Special_Events.gpl`. There is no
`Random_Events.gpl` or `Special_Events.gpl` anywhere under `GPL/`, and
neither filename is `mx_`-prefixed — they were added, not forked.

Three further independent confirmations that the whole event system is
expansion-only:

1. **Build-project membership.** `GPLMx/Path_Build.gplproj` line 7 lists
   `source="Rules\Random_Events.gpl"`; `GPLMx/Path_Data.gplproj` line 20
   lists `source="Rules\Special_Events.gpl"`. `GPL/path.gplproj` (the
   base-game project) lists neither — it includes `rules\Demo.gpl`
   (line 21) but no events file.
2. **The launcher doesn't exist in base.** `GPL/Rules/
   epic_quest_scripts.gpl`'s `function Freestyle()` (lines 4084-4096) is
   eight lines long: retrieve `GplAiRoot`, `$SetUp_Freestyle_Music`,
   `$setvictorycondition()`. The mx version
   (`mx_Epic_Quest_Scripts.gpl` lines 4047-4108) adds the
   `Lair_Delay_Override` flag and the entire special-event kickoff block
   described in 17.3. Nothing in base ever calls a special event.
3. **The agent prototype doesn't exist in base.** `Prototype EventAgent`
   is declared only in `GPLMx/mx_prototype.gpl` line 1117 (grepped the
   whole SDK `.gpl` tree — one match, plus copies inside our own
   `MyQuest`/`IceSpell_Quest`/`PanelTest_Quest` `mx_prototype.gpl`
   forks). Base `prototype.gpl` has no such prototype, so base-mode GPL
   has no agent type able to hold an `EventScript`.

**Practical consequence:** a modder targeting **base game mode** has
neither the random-event pool, the special-event framework, nor the
`EventAgent` prototype. They can copy the *patterns* (they use only
primitives that exist in base — see the per-item notes below), but not
the files, and specifically not `$GetSpecialEvent1Script()`, whose
base-exe existence is **UNVERIFIED** (it appears in the SDK's
compiler-keyword list, which is a single shared list not split by
base/expansion — see 17.5). Expansion mode gets all of it for free.

### 18.0 File scoping: base-game file, and the expansion copy is a near-clone

`Quest_Actives.gpl` is a **base-game** file (unlike §17's
`Random_Events.gpl`/`Special_Events.gpl`), present in both trees and in
both build projects: `GPL/path.gplproj` line 20
(`source="rules\quest_actives.gpl"`), `GPLMx/Path_Build.gplproj` line 4
(`source="rules\mx_quest_actives.gpl"`).

**`mx_Quest_Actives.gpl` is functionally identical to the base file.**
Both were read end to end. Same 15 functions, in the same order, with
the same bodies — the same `$declarevictory(palace,thisagent)`, the same
`#Arrest_Hooligan_Dist` check, the same chest constants. The only
differences are cosmetic:

1. Whitespace/blank-line churn and one reflowed comment
   (`// … so they tend to act more like guardian monster-types` is split
   across two lines in mx).
2. **One expansion-only addition, and it is entirely commented out**:
   `mx_Quest_Actives.gpl` lines ~578-592 carry a dead
   `//Function Henchman_Wander (agent ThisAgent)` block ("This just
   wanders around the unit's DESTINATION"). Every line is commented; it
   is absent from the base file. Grepped `Henchman_Wander` across the
   whole workspace — the commented block is the only occurrence, so it
   is neither defined nor called anywhere. Nothing to trace.

**So every finding below applies identically to base and expansion**, and
unlike §17's event framework, quest actives are fully available in base
game mode.

### 19.0 File scoping: expansion-only, no base-game equivalent

`Quests_1.gpl` exists **only** under `GPLMx/`. Verified directly:
`file_search` for `Rules/Quests_` returns exactly three hits, all
`GPLMx/Rules/Quests_1.gpl`, `Quests_2.gpl`, `Quests_3.gpl` — there is no
`GPL/Rules/Quests_1.gpl`. Build wiring agrees: `GPLMx/Path_Data.gplproj`
lines 16-18 list all three; no `.gplproj` under `GPL/` mentions them.

**So, same caveat as §17.0's `Random_Events.gpl`/`Special_Events.gpl`:
everything in this file is expansion-mode only.** That matters for two
reasons beyond "you can't use these quests in base mode":

1. Several helpers these quests lean on are also mx-only
   (`$ListFamily` is defined in `GPLMx/mx_LowLevel.gpl` line 59, and
   §14 already established `$RemoveTitles` has zero base-`GPL/` call
   sites). A base-mode modder cloning a pattern from here must check
   each helper.
2. The `#force_*` constants this file uses most (`#Force_Elf_Hunter` 8,
   `#force_Monster_Hunter` 10) are declared in `GPLMx/mx_Globals.gpl`
   lines 852-854 and **have no counterpart in base `GPL/globals.gpl`**,
   which stops at `#force_bomber` 4 plus `#Force_PC_Hunter` 5 /
   `#Force_Wandering` 6 (base `globals.gpl` lines 821-824 onward).

### 20.0 File scoping: expansion-only, four quests, skeleton mostly followed

**Expansion-only, confirmed directly rather than assumed:** `file_search`
for `Quests_2.gpl` returns exactly one hit,
`SDK/OriginalQuests/GPLMx/Rules/Quests_2.gpl` — there is no
`GPL/Rules/Quests_2.gpl`. Same caveat as §19.0 applies to everything
below unless a base twin is named.

**Four quests**, each an engine-invoked nullary entry function:
`RISE_RATMEN` (line 8), `SCIONS_CHAOS` (315), `URBAN_RENEWAL` (535),
`VIGIL` (807). All four use §19.1's five-part skeleton — `Quest_Number`
register first, palace lookup, `$Setup_Quest_Music`, `$DisableUnitType`
block, then `VictoryCondition` at
`#VictoryCondition_callback_frequency` — with three deviations worth
naming up front:

1. **`SCIONS_CHAOS` runs on ONE thread.** It has no
   `"VictoryCondition2"` at all; its staging lives inside the victory
   poll as nested flag pairs (20.5). So the §19.1 skeleton's two-thread
   split is a convention, not a requirement.
2. **Nobody in this file initialises its quest flags.** §19.1 found
   explicit `= False` init blocks (18 consecutive lines in one case);
   all four quests here rely on unset flags reading as `False`. Both
   forms ship and evidently work, so **the init block is defensive
   style, not a requirement** — but note §19.1's sequencer correctness
   argument depends on the flags starting false either way.
3. **Two of the four sequencers `$KillThread` themselves** at their last
   stage (`Ratmen_Events` line 226, `vigil_events` line 969) instead of
   ending in §19.3's difficulty-ratchet `Else`. That is the other half
   of that pattern: an authored, *finite* escalation.

### 21.0 File scoping: expansion-only, four quests, skeleton largely abandoned

**Expansion-only, confirmed directly rather than assumed:** `file_search`
for `Quests_3.gpl` returns exactly one hit,
`SDK/OriginalQuests/GPLMx/Rules/Quests_3.gpl` — there is no
`GPL/Rules/Quests_3.gpl`. §19.0's caveat applies to everything below
unless a base twin is named.

**Lines ~524-756 were already covered by Batch B** and are *not*
re-derived here: the four difficulty-tier random-event dispatchers
(`Trade_Routes_Helpful_Event` 524, `..._Minor_Event` 561,
`..._Moderate_Event` 597, `..._Major_Event` 637), plus
`Setup_Trade_Markers` (665) and `GetMarker` (721) — the signposts-as-
`"color"`-objects + `$Post_Message` + retitle-for-fast-lookup idiom. See
§17.2 and §17's `$Post_Message` entry. This batch only adds the two
*consumers* of those markers (`Create_Trade_Caravan`, and the Siege
quest's near-identical `Setup_Siege_Routes`/`GetSiegeMarker` clones at
2077/2126).

**Four quests**, each an engine-invoked nullary entry function:
`TRADE_ROUTES` (line 8), `SPIRES_DEATH` (822), `SIEGE` (1237),
`FORTRESS_IXMIL` (2296). Four structural deviations from §19.1 worth
naming up front, because they are what makes the file interesting:

1. **Two more root-agent script slots are in play**, and they are
   declared, not improvised: `SpecialSpawnScript` and
   `SpecialSpawnScript2` (`GPLMx/mx_prototype.gpl` lines 23-24, shipped
   comment "These hold the functions (if any) that spawns a creature
   after a certain amount of time (Like Dirgo in Brashnard)"). All four
   quests here use them; §19/§20 used only
   `VictoryCondition`/`VictoryCondition2`/`UtilityScript`. See 21.2 for
   the full slot/register set.
2. **Three of the four quests never poll for victory.** `SPIRES_DEATH`
   and `FORTRESS_IXMIL` declare victory from a **death script**;
   `TRADE_ROUTES` declares it from an **externally-called scorer**
   (21.3); only `SIEGE`'s `Flag_Remover` occupies the
   `"VictoryCondition"` slot at all, and it is housekeeping, not a win
   test. `FORTRESS_IXMIL` still has its poll thread present but
   **commented out** (lines 2361-2362).
3. **`Quest_Flag_N` is used as ordinary state, not as a program
   counter.** `FORTRESS_IXMIL` initialises three flags to **`TRUE`**
   (inverted polarity vs §19.1's all-`False` init) and uses them as a
   phase bit and two "not yet fired" latches; `SPIRES_DEATH` and `SIEGE`
   use no quest flags at all. Only `TRADE_ROUTES`'
   `Trade_Route_Standard_Events` (lines 55-104) is a §19.3 sequencer —
   and even that one is a pure `else if` chain with **no
   `$SetThreadInterval`**, i.e. the degenerate fixed-cadence form.
4. **`Victory_Score` / `Defeat_Score` / `day_counter` are general-purpose
   integer registers**, not scores, in two of the four quests (21.6). The
   prototype comment says so explicitly: "used on a quest by quest
   basis."

### 22.0 File scoping: a base-game file, and the mx clone differs in exactly two ways

**This is a base-`GPL/` file** — the first quest-implementation file in
this pass that is (§19/§20/§21 were all `GPLMx`-only). `GPLMx/Rules/
mx_Epic_Quest_Scripts.gpl` is a near-verbatim clone: both files set
`Quest_Number` for the **same 19 quests**, in the same order
(`#QNumber_Barren_Waste`, `Bell_Book`, `Holy_Chalice`, `Crown`,
`Dark_Forest`, `Day_Reckoning`, `Deal_Demon`, `Slay_Dragon`,
`Tomb_Dragon`, `Elven_Treachery`, `Fertile_Plain`, `Forsaken_Lands`,
`Goblin_Hordes`, `Liche_Queen`, `Save_Prince`, `Magic_Ring`,
`Slave_Pits`, `Brashnard`, `Wizards_Curse` — verified by grepping the
`Quest_Number` writes in both files). So **the expansion re-ships all 19
base epic quests**, and a modder can copy patterns from this file in
either mode.

Two differences, both confirmed by direct read rather than inferred from
the line-count delta:

1. **The entire post-victory difficulty-tier library is base-only.**
   `end_game_script_easy/_medium/_hard/_expert`, `spawn_monsters`, and
   `pick_easy/medium/hard/expert_monster` exist **only** in
   `GPL/Rules/epic_quest_scripts.gpl` (lines 4176-4358). A grep for
   `end_game_script` across all of `SDK/OriginalQuests/` returns 19
   install sites plus 4 definitions, **all in the base file and zero in
   mx**. Spot-confirmed at the source: base `barren_victory` lines
   140-152 install `$end_game_script_easy` after `$declarevictory`; the
   mx clone (lines 135-152) is otherwise identical and simply **omits
   those two lines**. The mx file ends at `Magical_Repair` with no tier
   library at all. **Consequence: "keep playing after you win" in
   expansion mode gets no escalating monster pressure from this file.**
2. **`Freestyle()` is 3 statements in base and ~40 in mx** (22.4a).

Everything else spot-checked matched byte-for-byte, including
`all_enemies_dead`'s exclusion list (base 1218-1220 / mx 1190-1192) and
`Setup_High_Level_Members`' shipped defect (base 3060 / mx 3030, see
22.8).

---

## Chapter 10: Research Provenance: What Is NOT New, Sources, and Open Questions

Recombination lists (so no file needs re-reading) plus per-batch sources and UNVERIFIED items.

### Batch scope statements (verbatim, from the original §16-§22 headings)

Each research batch opened with a statement of exactly which files
were read in full. Those statements are preserved here so the
coverage claim stays auditable after the reorganisation.

### 16. Quest Rules Deep Dive — Batch A: Construction Rules & Victory Conditions

Batch A of a multi-batch pass over `GPL/Rules/` (remaining batches
tracked in `TODO-GPL-Deepdive.md`). Files read in full:
`GPL/Rules/construction_rules.gpl` (145 lines),
`GPL/Rules/victory_conditions.gpl` (326 lines), and both expansion
equivalents `GPLMx/Rules/mx_Construction_Rules.gpl`,
`GPLMx/Rules/mx_Victory_Conditions.gpl`. Scoped to reusable modding
mechanisms, not quest plot summaries.

### 17. Quest Rules Deep Dive — Batch B: Demo, Random Events, Special Events

Batch B of the multi-batch `Rules/` pass (Batch A = §16; Batches C-G
still open in `TODO-GPL-Deepdive.md`). Files read in full:
`GPL/Rules/Demo.gpl` (328 lines), `GPLMx/Rules/mx_Demo.gpl`,
`GPLMx/Rules/Random_Events.gpl` (370 lines),
`GPLMx/Rules/Special_Events.gpl` (915 lines). Supporting reads cited
inline. Scoped to reusable mechanisms — quest plot gets one line at most.

### 18. Quest Rules Deep Dive — Batch C: Quest Actives

Batch C of the multi-batch `Rules/` pass (Batch A = §16, Batch B = §17;
Batches D-G still open in `TODO-GPL-Deepdive.md`). Files read in full:
`GPL/Rules/Quest_Actives.gpl` (616 lines) and
`GPLMx/Rules/mx_Quest_Actives.gpl`. Supporting reads cited inline.
Scoped to reusable mechanisms; quest plot gets one line at most.

**What this file is, in one sentence:** the base game's library of
**per-agent quest behavior handlers** — functions written to be *stored
in an agent's script-slot attributes* by some other file, then run by
the agent's own script cycle. It is the complement to §15's per-class
hero decision trees (which are the *default* contents of those slots)
and to §1's `ActiveScript`/`BackScript` state machine (which is the
dispatch mechanism). Nothing in this file is engine-invoked, and nothing
in it schedules itself; every function here is dead code until a quest
setup function assigns it somewhere (18.1).

### 19. Quest Rules Deep Dive — Batch D: Quests_1.gpl

Batch D of the multi-batch `Rules/` pass (Batch A = §16, Batch B = §17,
Batch C = §18; Batches E-G still open in `TODO-GPL-Deepdive.md`). File
read in full: `GPLMx/Rules/Quests_1.gpl` (2232 lines). Supporting reads
cited inline. Scoped hard to reusable mechanisms — this file is four
complete expansion quests, and a per-quest narrative would be useless to
a modder, so the recurring skeleton is documented once (19.1), every
quest gets one table row (19.2), and only genuinely new mechanisms get
their own subsection.

**What this file is, in one sentence:** four self-contained expansion
quest implementations, each consisting of an engine-invoked nullary entry
function plus 2-4 root-agent threads, sharing one skeleton so exactly
that the fourth quest is mostly the first with the nouns changed.

### 20. Quest Rules Deep Dive — Batch E: Quests_2.gpl

Batch E of the multi-batch `Rules/` pass (Batch A = §16, Batch B = §17,
Batch C = §18, Batch D = §19; Batches F-G still open in
`TODO-GPL-Deepdive.md`). File read in full:
`GPLMx/Rules/Quests_2.gpl` (977 lines). Same output shape as §19,
because it is the same kind of file: skeleton documented once (§19.1,
not repeated), one table row per quest (20.1), own subsection only for
genuinely new mechanisms, explicit recombination list (20.8), sources
and open questions (20.9).

**Scoped hard against §19.** Roughly two thirds of this file is §19
mechanisms with different nouns. What is new is concentrated in one
place: **this is the file where quest content is made out of *heroes* and
*enemy buildings* rather than lairs and monsters**, and that pulls in a
different set of primitives.

### 21. Quest Rules Deep Dive — Batch F: Quests_3.gpl

Batch F of the multi-batch `Rules/` pass (Batch A = §16, Batch B = §17,
Batch C = §18, Batch D = §19, Batch E = §20; **Batch G
(`epic_quest_scripts.gpl` / `mx_Epic_Quest_Scripts.gpl`) is still open**).
File read in full: `GPLMx/Rules/Quests_3.gpl` (2977 lines). Same output
shape as §19/§20: skeleton not repeated (§19.1), one table row per quest
(21.1), own subsection only for genuinely new mechanisms, explicit
recombination list (21.9), sources and open questions (21.10).

**Scoped hard against §19/§20.** This is the third `Quests_N.gpl` and the
least like its siblings: **none of its four quests is built out of the
§19.1 timed-sequencer skeleton.** Three of the four have no victory poll
at all, one has no `Quest_Flag` chain at all, and the file's real content
is four *systems* — an externally-scored delivery game, a self-retiering
tower, a GPL-implemented AI opponent kingdom, and a phase-in/phase-out
boss building. That is where all the new material is.

### 22. Quest Rules Deep Dive — Batch G: epic_quest_scripts.gpl

Batch G, the **final** batch of the multi-batch `Rules/` pass (Batch A =
§16, B = §17, C = §18, D = §19, E = §20, F = §21). With this section the
whole "Quest rules pass" item is complete.

Files read: `GPL/Rules/epic_quest_scripts.gpl` (4358 lines, 85 function
definitions) plus targeted diffs against
`GPLMx/Rules/mx_Epic_Quest_Scripts.gpl`. Supporting reads cited inline.

**What this file is, in one sentence:** the base game's 19 named epic
quests plus `Freestyle()`, sitting on top of **a shared helper library
that the rest of the GPL tree calls into** — and the library is the half
that matters to a modder.

**Scoping, stated up front.** By §16-§21 the quest skeleton, the staged
sequencer, the victory/loss vocabulary, the `$SpawnUnit` grammar, the
`"type"` register, artifice/`#force_*`, script-slot idioms, building
hijack, death-handler conventions and the coordinate helpers are all
documented. This section is **strictly the delta**. Concretely that
means: every quest gets one table row (22.1) and nothing else; the helper
library gets a catalogue with signatures and contracts (22.2); the
difficulty-tier system, which no earlier batch saw, gets its own
subsection (22.3); and four smaller new mechanisms get one subsection
each (22.4-22.7). Recombination is listed once, in 22.9.

### 19.11 Recombination only — already documented, nothing new to add

Stated explicitly so a later batch doesn't re-read these looking for
something. The following all appear in `Quests_1.gpl`, some very heavily,
and are pure reuse of mechanisms §16-§18 already cover. Each gets one line
because one line is all it warrants:

- **`$SpawnUnit`'s variadic grammar** — this file exercises nearly every
  documented permutation (`(src, type)`, `(src, type, coord)`,
  `(src, type, coord, player)`, `(src, type, coord, player, artifice)`,
  `(src, type, player, artifice, coord, "override")`, plus `"MaxHP"` in
  several positions). §17's argument-order finding holds throughout; no
  new argument or ordering rule appeared.
- **`"MaxHP"`** for spawning pre-completed buildings — used for
  SnakePits, BrokenSewerMains, Goblin Watchtowers and a GoblinFortress.
  Same string flag §17 documented.
- **Coordinate helpers** — `$RandomEdgeCoord ($RandomNumber (4))`,
  `$RandomCoord (agent, min, max)` and `$RandomCoord (agent, radius)`,
  `$ClosestMapEdge`, `$FarthestMapEdge_OnMap`, `$LocationOf`. All §17.
- **`$MessageFlag` / `$minimapanimation (…, "Event_beacon")` /
  `$RevealArea`** as the standard "tell the player something happened"
  trio. All §17. Confirmed again here that `$MessageFlag` accepts an agent
  *or* a coordinate (`$MessageFlag ($LocationOf (ThisAgent), #Message_…)`
  in `LH_Barrows_Death`).
- **`$CreateSpellUnit (caster, "Earthquake", target)`** — §17.2's
  no-hero-caster spell primitive, used identically.
- **`$setup_random_treasure (20, #default_spawn_treasure_dist)`** —
  §18's form, verbatim.
- **`$SetUp_Respawning_Lairs (Palace)`** — §17's "whole rules change in
  one call," used verbatim by `LEGENDARY_HEROES`.
- **`$DisableUnittype`** — §16's gating pattern (`"Elven_bungalow"` in
  Vale, `"dwarven_Settlement"` in Darkness Falls). Only the *combination*
  with `$DeclareLoss` is new, and that's 19.5c.
- **`$Reset_Tasks`, `$Move (…, "avoid_vehicles")`, `$IsMoving`,
  `$IsDead`, `$ListPalaces`, `$RetrieveAgent ("GPLAIRoot")`,
  `$GetUnitPlayerNumber`, `$ListObjects` option flags
  (`#NoHiddenMap` / `#CheckTitles` / `#CheckSubtypes` /
  `#InSideOtherUnits` / `#NotMyTeam`), `$Random_Time`,
  `$KillThread` / `$NewThread` / `$RunThread`, `$Addlists`,
  `list -= member`, `list << member`** — all §14/§16/§17/§18.
- **`$Make_PC_Hunter` called at runtime on an existing monster**
  (`Legendary_Heroes_Events`, three times, each followed by
  `$Reset_Tasks`) is *nearly* new but reduces to 19.6's installer plus
  §18.2's "call `$Reset_Tasks` to make a slot swap take effect
  immediately." The one fact worth keeping: **the `#force_*` installers
  work on any live monster, not just newborns** — the artifice attribute
  is only needed when you want the *birth* hook to do it for you.

Two stylistic observations, non-actionable but worth a line each so
nobody mistakes them for mechanisms: the file leans on copy-paste rather
than loops (`Legendary_Heroes_Victory` has 18 near-identical `$SpawnUnit`
blocks; `Spawn_Elves` repeats a 9-line stanza seven times), and it carries
a lot of commented-out code that documents intent — most consistently the
`$ListObjects`+`$ListTitles` two-step being replaced by the one-call
`#CheckTitles` form (exactly the migration §14 noted), with the old
version left in place directly above the new one.

### 20.8 Recombination only — already documented, nothing new to add

Stated explicitly, per §19.11, so a later reader doesn't re-open this
file hunting for more. Everything below appears in `Quests_2.gpl`, some
of it heavily, and is pure reuse:

- **The five-part quest skeleton** (§19.1) — all four quests, with the
  three deviations already noted in 20.0 (single-thread `SCIONS_CHAOS`,
  no flag-init blocks, self-terminating sequencers).
- **The self-pacing staged sequencer** (§19.3) — `Ratmen_Events`
  (7 stages) and `vigil_events` (4 stages), `$SetThreadInterval` with
  `$random_time(N)` per stage, values 200000-420000 plus one deliberate
  `5000` beat (line 208, the "Rhoden appears a moment later" pause). No
  new property.
- **`$IsTitleAlive` for a named boss** (§19.5a) — `"RhodenKingRat"`,
  line 55. This was flagged as a lead; it is an exact reuse, including
  the commented-out `$listtitles` version directly below it.
- **Two-stage victory with a gate flag** (§19.5b) — `Ratmen_victory`
  gates on `Quest_flag_7` (Rhoden spawned) before testing boss-dead and
  zero-lairs.
- **`$PlaySound(palace, "<unit type>", "<cue>")`** (§19.5) —
  `"Ratman_king"` with cues `"taunt"`, `"taunt2"` and `"VFX_GO_COMBAT"`,
  fired from the palace before Rhoden exists on the map. Same mechanism;
  the only addition is two more real cue names.
- **`$Make_PC_Hunter` at runtime + an attribute boost** (§19.11) — the
  `#ATTRIB_sightrange` loop at lines 866-870 on the map's starting
  `"GreaterGorgon"`s. Also flagged as a lead; it reduces to §19.6's
  installer plus a plain `$AdjustAttribute`. **One inconsistency worth
  one line:** §19.11 noted Legendary Heroes always follows
  `$Make_PC_Hunter` with `$Reset_Tasks` so the swap takes effect
  immediately; **this file's loop omits it.** Whether the
  swap still takes effect on the unit's next natural cycle, or these
  gorgons stay on their old behavior until something else resets them,
  is **UNVERIFIED**.
- **`$Concatenate(#ATTRIB_Artifice, #force_*)` at spawn time** (§17.5) —
  `#force_PC_hunter` and `#force_raider` in `vigil_events`.
- **Coordinate helpers** — `$RandomEdgeCoord($RandomNumber(4))`,
  `$RandomCoord(agent, radius)`, `$FarthestMapCorner(palace)`,
  `$LocationOf`. All §17.
- **`$MessageFlag` and `$minimapanimation(agent,"Event_beacon")`** as the
  "tell the player" pair — §17, used on every wave spawn.
- **Draw-without-replacement** (`sewers -= place`) — §17's idiom, used
  eleven times in `Ratmen_Events`.
- **`$DisableUnitType`** (§16) and **the inline `#ATTRIB_FirstStageBuilt,
  1` `$ListObjects` filter** (§16.1).
- **`$Setup_Quest_Music` / `$Reset_Quest_Music`** (§19.4) — all four
  quests set up, all four reset on victory. Note **no
  `$Play_Endgame_Music` anywhere in this file**, so §19.4's three-function
  set is only partially exercised here.
- **`$declarevictory`** in both forms (bare, and with an `end_coord`
  second argument), each followed by `$KillThread` of the poll slot —
  §16.2. **No quest in this file continues after victory**, so §19.5d's
  post-victory-thread pattern does not appear.
- **`$ListSubtypes` / `$ListTitles` / `$AddLists` / `list << x` /
  `list -= x` / `$ListMember` / `$ListSize` / `$HasAttribute` /
  `$GetUnitPlayerNumber` / `$SetUnitPlayerNumber` / `$Advance_To_Level` /
  `$AdjustAttribute` / `$SetAttribute` / `$NewThread` / `$KillThread` /
  `$SetThreadInterval` / `$RetrieveAgent("GplAIRoot")` / `$random_time`** —
  all §14/§16/§17/§18.
- **`SpecialScript` + `$NewThread(slot, interval, agent)` with
  `$Hero_Generator`** (§18.7) — **§18.7 already cites this file's line
  574 as a confirming site**, so only the `ActiveScript` sibling (20.6a)
  and `Hero_Generator`'s body (20.6b) needed treatment.

**Absent from this file entirely, worth knowing so nobody looks:** no
`UtilityScript` deadline, no lair field writes (`Spawn_Type`,
`Special_Spawn_Type`, `Max_Simul_Spawns` — the whole §19.7 cluster),
no `$SetUp_Respawning_Lairs`, no `$CreateNewInventoryItem`, no
`$LearnSpell`, no `Self_Estimation`/`Enemy_Estimation`, no `$ListFamily`,
no `#force_*` beyond `#force_PC_Hunter`/`#force_raider`, and **no
instances of §19.3's `=`-in-a-condition bug** — every comparison in this
file uses `==`.

**Two stylistic notes**, non-actionable, so nobody mistakes them for
mechanisms: the file is even more copy-paste-heavy than `Quests_1.gpl`
(five `rat_gangN` roster functions of 6-10 near-identical `$SpawnUnit`
lines each — §17.2's roster-dispatcher shape without the dispatcher; and
24 consecutive identical `$spawnunit(palace,"Strangleweed",…)` lines in
`Scions_victory`), and it carries the same commented-out
`$ListObjects`+`$ListTitles` two-step directly above its replacement
`#CheckTitles` one-liner in six places — the §14 migration, again.

### 21.9 Recombination only — already documented, nothing new to add

Per §19.11/§20.8, stated explicitly so nobody re-opens this file looking
for more. All of the following appear in `Quests_3.gpl`, much of it
heavily, and are pure reuse:

- **The `Quest_Number` register set first in every entry function**
  (§16.2/§19.1) — all four quests, and 21.3's scoring hooks are its most
  interesting consumer.
- **`$Setup_Quest_Music (AIRootAgent)`** (§19.4) — all four quests. **No
  `$Reset_Quest_Music` and no `$Play_Endgame_Music` anywhere in this
  file**, so the endgame track never plays in these four quests;
  `$PlaySound (Palace, "Victory_Theme", "Begin")` (§17) is used instead,
  at three sites.
- **`$DisableUnitType`** (§16) — `Marketplace1`/`Trading_Post` in
  `TRADE_ROUTES` (so the market you must protect cannot be rebuilt —
  §19.5c's "protect what you cannot build," a third independent
  instance), `Wizards_guild1` in `SIEGE`.
- **The four random-event difficulty dispatchers, `Setup_Trade_Markers`,
  `GetMarker`** — Batch B, §17.2 (see 21.0). `Setup_Siege_Routes` (2077)
  and `GetSiegeMarker` (2126) are copy-paste clones with the messages
  removed.
- **Signs/markers as `"color"`-class objects + `$Post_Message` + retitle
  for fast lookup** (§17) — used three times (trade markers, siege
  markers, the Ixmil obelisk).
- **`$SpawnUnit`'s variadic grammar** (§17) — every documented
  permutation appears, plus `"MaxHP"` for pre-built lairs/guilds and
  `"override"`; the only genuinely new item is the `"clear"` flag (21.7).
- **`$Concatenate (#ATTRIB_Artifice, #force_*)` at spawn time** (§17.5,
  §19.6) — `#Force_Guardian`, `#Force_Raider`, `#Force_Bomber`,
  `#Force_PC_Hunter`, `#Force_Caravan_Raider` all used; no new artifice
  value, no new behavior function.
- **Coordinate helpers** — `$RandomCoord` (both radius and min/max
  forms), `$ClosestMapEdge`, `$FarthestMapCorner`,
  `$FarthestMapEdge_OnMap`, `$LocationOf`, `$GetX`/`$GetY`/`$MakeCoord`
  (the caravan spawn-point jitter at lines 795-806 is the only place the
  three coordinate accessors are used together, but they are all §17).
- **`$MessageFlag` + `$MiniMapAnimation(…, "Event_beacon")` +
  `$RevealArea`** as the "tell the player" trio (§17) — everywhere.
- **`$CreateSpellUnit (caster, "<spell>", target)`** (§17.2) — the AI's
  `"Lightning_Storm"`.
- **Calling a spell's own effect function directly to apply it without a
  caster** (§17.2's `$Ratman_Plague_Begin`, §19.9's
  `$Winged_Feet_Begin`) — the AI's `$Reanimate_Begin`,
  `$Fervus_Heal_Effect`, `$lightning_bolt_hit`. **The *pathway* is
  recombination; what's new (21.6c) is that these three are specifically
  the player's building-panel spells, and that the caller pays the gold.**
- **Indirect call through a function-typed agent field** (§14, §17.5) —
  `spire's "Spawn_Function" (spire)`. New only in *what it's used for*
  (21.4c).
- **The stock tower scan/attack ping-pong.** `Spire_Scan`/`Spire_Attack`
  (1076/1093) and `Ixmil_Scan`/`Ixmil_Attack` (2939/2957) are near-verbatim
  copies of `Tower_Scan`/`Tower_Attack`
  (`GPLMx/TaskModules/Buildings/mx_Tower.gpl` lines 10-68; base twin
  `GPL/TaskModules/Buildings/Tower.gpl`), including the
  `if (thisagent's "enemytype" != "nothing")` guard (§20.4's
  combat-participation switch) and `$list_enemies_seen (agent, range)` —
  already documented in §3's garrison discussion. `list_enemies_seen`
  itself is worth one line since this file leans on it four times: it
  unions `"hero"` and `"monster"` at `#NotMyTeam` and **orders the union so
  the nearer group comes first**, which is why every caller can just take
  `$ListMember(Enemies,1)`. The only addition in the copies is
  `$CreateEffector (ThisAgent, "<X>_Attack_Effector", 0)` before each
  shot, with the shipped comment "this is a workaround to allow the tower
  to 'animate' in its damaged states" — §13's duration-0 form used as a
  per-shot animation trigger.
- **`$Advance_To_Level` on a fresh spawn** (§17/§19.9) —
  `Trade_Standard_One`'s level-2-to-5 rogue ladder.
- **`$SetAttribute(#ATTRIB_MaxHP, x2)` then `#ATTRIB_HP = MaxHP`**
  (§20.3a's "raising the ceiling doesn't fill the bar") — independently
  re-confirmed on the siege caravans (2209-2210).
- **`$ListObjects` option flags** — `#MyPlayer`, `#NotMyPlayer`,
  `#NotMyTeam`, `#NoHiddenMap`, `#CheckTitles`, `#CheckSubtypes`,
  `#InsideOtherUnits`, plus `#RewardFlags` (21.6b). All §14/§17.
- **`$RemoveTitles` partitioning + `$AddLists`** (§19.6) — five sites.
- **`$IsValidGamePiece` / `$IsDead` guards before dereferencing a stored
  agent** (§18) — everywhere, and mandatory in 21.5a/21.6b.
- **`$GetPlayerData` / `$AdjustPlayerData` with the `"gold"` string key**
  (§5, §17.2) — new only in that the agent argument is a guild or a
  palace of a *non-player* kingdom (21.5b).
- **`$SetPlayerTeamNumber` / `$NewTeamNumber` / `$NeutralTeamNumber`**
  (§16.2, §18, §19.8) — `SIEGE`'s war and peace. **This file does not
  narrow §19.12's "exact scope of `$SetPlayerTeamNumber`" question any
  further than §20.4 did**: it is again one call per palace.
- **`$Lair_Death` / `$building_death` tail-called from an override**
  (§19.3, §20.6c) — `Spire_Death` calls the former; `Fortress_Death`
  hand-rolls the four-call lair teardown (`$dropgoldinradius`,
  `$chance_drop_equip`, `$Drop_QItems`, `$building_death`) instead of
  calling `$Lair_Death`, which is the same sequence §19.7 read out of
  `lair_death` minus the special-spawn block — i.e. **a deliberate
  "die without spawning your special payload."**
- **`$KillThread` / `$NewThread` / `$RunThread` / `$SetThreadInterval`,
  `$RetrieveAgent("GplAIRoot")`, `$ListMember`/`$ListSize`/`list << x`/
  `list -= x`, `$RandomNumber`, `$DebugOut` (variadic, per §20.5c),
  `$PerformAction`, `$StopMoving`, `$DeleteGamePiece`,
  `$CreateEffector`/`$CheckEffector`** — all §13/§14/§16/§17/§18.

**Absent from this file entirely, worth knowing so nobody looks:** no
`$IsTitleAlive`, no two-stage victory gate, no `$declareloss` other than
`TRADE_ROUTES`' single call, no `$SetUp_Respawning_Lairs`, no
`$CreateNewInventoryItem`, no `$LearnSpell`, no
`Self_Estimation`/`Enemy_Estimation`, no `$ListFamily`, no `$make_raider`
family calls, no `resist_critical`, no rescue/defection subsystem, no
`$setup_hero_level`, no `$ElvesVoice_setOperative`, no `$random_time`
(this file writes its intervals as explicit `$RandomNumber(N)+M`
expressions throughout), and **no `Special_Spawn_Type`/`Has_Special_
Spawn`/`Max_Simul_Spawns` lair-field writes** — the only lair field this
file writes is `Spawn_Function` (21.4c).

**Two stylistic notes**, so nobody mistakes them for mechanisms: the file
carries the same copy-paste habit as its siblings (ten identical
`$SpawnUnit` barbarian lines, three near-identical `Flag*Target`
functions differing only in their target query, four
`Fortress_Ixmil_Spawn_*` functions sharing an eight-line preamble), and
two empty authored-but-unwritten event functions ship in it
(`Spires_Death_Events` 856 and `Fortress_Ixmil_Events` 2925, both
`begin`/`end` with nothing inside) — the same category as §9's Zoo and
§20.5c's empty event branches.

### 22.9 Recombination only — already documented, nothing new to add

Per §19.11/§20.8/§21.9, stated explicitly so nobody re-opens a 4358-line
file hunting for more. This is the promise made in the §22 intro
("Recombination is listed once, in 22.9"). Everything below appears in
`epic_quest_scripts.gpl`, most of it many times, and is pure reuse of
mechanisms §13-§21 already cover. The seven quests marked "New? none" in
22.1 — Tomb of the Dragon King, Forsaken Lands, Rescue the Prince, Magic
Ring, Slave Pits, Brashnard, Wizard's Curse — are built **entirely** from
this list plus the 22.2 helpers.

- **`Quest_Number` set as the first statement of every entry function**
  (§16.2/§19.1) — all 19 quests, verified as the roster check in 22.0.
  Its only consumer in this file's orbit is `High_Level_Hero_Birth`'s
  per-quest branch (22.2).
- **The full music trio** (§19.4) — `$Setup_Quest_Music (AIRootAgent)` in
  every quest entry, `$Reset_Quest_Music` on victory, and
  `$Play_Endgame_Music` at the dramatic mid-quest beat (barren 129,
  bbc 339, chalice 522, dark forest 828, wizard's curse 3993). **This is
  the file that exercises all three**, which §20.8 and §21.9 both noted
  their files did not. Same three functions, no new property.
- **`$DisableUnitType`** (§16) — the heaviest user in the tree: 14
  consecutive calls in `DARK_FOREST` (705-718), 11 in `SAVE_PRINCE`, five
  in `BARREN_WASTE` (44-48), and `"Marketplace1"` in `HOLY_CHALICE` (468)
  to force the chest economy. Its inverse `$EnableUnitType` is 22.6a
  because *unlocking* mid-quest is new; disabling is not.
- **`$ElvesVoice_setOperative (0)` / `$dwarvesVoice_setOperative (0)`
  paired with the matching `$DisableUnitType`** (§20.7) — 51-52, 721.
  The `1` calls are 22.6a.
- **`$MessageFlag` + `$MiniMapAnimation (…, "event_beacon")` +
  `$RevealArea (agent, coord, radius)`** as the "tell the player" trio
  (§17) — everywhere; `$RevealArea` at 1035, 2397, 2418, 3269, 3958.
  `$MessageFlag` again takes an agent *or* a coordinate.
- **Signs as `"color"`-class objects found by `$ListTitles`, then
  `$Post_Message`** (§17) — `BARREN_WASTE` 60-61, `QUEST_FOR_CROWN`
  637-643, `WIZARDS_CURSE` 3975-3978. 22.2's `$Create_Sign` is the
  one-call replacement for exactly that three-step.
- **`$SpawnUnit`'s variadic grammar** (§17) — every documented
  permutation appears, including `"MaxHP"` for pre-built lairs/guilds and
  `"Override"` (3632). No new argument and no new ordering rule. The
  mixed-case `"Override"`/`"override"` habit §17 flagged recurs here too.
- **`$Concatenate (#ATTRIB_Artifice, #force_*)` at spawn time**
  (§17.5/§19.6) — `#force_bomber` (1493-1500 on Dragons and Harpies,
  3666-3672 on Harpies) and `#force_raider` (2791, 2807, 2823 on
  Skeletons). **No new artifice value and no new behavior function.**
  `$make_raider` appears **only commented out** (1520-1523, with the
  `activeScript`/`basicScript`/`raider_respond` writes commented beside
  it and a live `$reset_tasks (vendral)` left behind) — §19.6's installer,
  authored then abandoned.
- **Coordinate helpers** (§17) — `$RandomEdgeCoord ($RandomNumber (4))`
  throughout, `$RandomCoord` in both the radius and the `-1` forms,
  `$LocationOf`, and `$GetX`/`$GetY`/`$MakeCoord` inside 22.2's
  `avg_coords`. The only addition is passing **named compass constants**
  (`$RandomEdgeCoord (#North)`, 2082) instead of a random index — the
  same primitive with a legible argument.
- **`$random_time (N)`** (§17/§19.3) — every tier driver and most event
  threads. 22.2's `$random_to_percent` (749) is the one call that reaches
  for the other jitter helper.
- **Draw-without-replacement (`list -= member`) and `list << member`**
  (§17) — lair partitioning in `LICHE_QUEEN`, and the `Levels` re-seat in
  `rescue_buildings`.
- **`$ListObjects` option flags** — `#MyPlayer`, `#NotMyPlayer`,
  `#NotMyTeam`, `#NoHiddenMap`, `#InsideOtherUnits`, `#CheckTitles` — plus
  `$ListTitles`, `$ListSubtypes`, `$AddLists`, `$ListMember`, `$ListSize`,
  `$ListPalaces`, `$HasAttribute`, `$RemoveListMember`. All §14/§17.
  `$ListCompleted`/`$ListCompletedTitles` are 22.6a.
- **`$declarevictory` in both forms (bare, and with an `end_coord` second
  argument), each followed by `$KillThread` of the poll slot** (§16.2),
  and **`$declareloss`** (§16.2/§19.5c) at three sites (chalice 577,
  demon, elven). 22.4b/c are the *patterns around* these calls; the calls
  themselves are §16.
- **The two-stage victory gate** (§19.5b) — Dark Forest, Liche Queen and
  Wizard's Curse all gate a boss-dead test behind a lair-gone test.
  `$IsTitleAlive`'s **body** is catalogued in 22.2; its **use** is §19.5a
  verbatim, including the commented-out `$ListSize == 0` version above
  every call.
- **`$PlaySound (agent, "<unit type>", "<cue>")`** (§19.5) — Liche Queen
  and Slave Pits taunts, plus `$PlaySound (palace,
  "Advisor_New_Outpost", "VFX_ADVISOR")` inside `rescue_buildings`. And
  **`$Say (agent, "<cue>")`** (§19.10) — `$say (vendral, "Taunt")` at
  1519, a second shipped site for the agent-direct audio primitive, with
  a new cue name.
- **`$Advance_To_Level` on fresh spawns, and the paired `#ATTRIB_MaxHP` →
  `#ATTRIB_HP` stat stack** (§19.9/§20.3a) — Varg (3830-3835) and
  `High_Level_Hero_Birth` (22.2). What they add is only that they are
  **base-game** instances of §20.3's enemy-hero recipe.
- **Runtime retitle as a quest marker** (§18/§19.7) — `bbc`'s three altar
  lairs (194, 201, 208), each retitled then given a
  `$CreateNewInventoryItem` payload. The commented-out
  `bldg's "Epic_Quest_Item" = #QItem_…` lines directly above (195, 202,
  209) document a field that call replaced.
- **`$CreateNewInventoryItem` on a lair as a findable payload**
  (§18/§19.7) — three altars, the chalice site, seven Brashnard shards.
  Only its optional third argument is new (22.6f).
- **Lair-field writes** (§19.7) — per-agent `IGDeathScript` override
  (456), `Special_Spawn_Type` swaps and downgrade loops,
  `Max_Simul_Spawns`, `"MaxHP"` repair (`BRASHNARD`'s "coverup for
  RGSEditor booboo" loop), and **`#Monster_Spawn_Cap` enforced by hand**
  in `GHorde_Troll_Spawner` — a base-game confirming site for §19.7's
  "it's a GPL convention each spawn function must enforce, not an engine
  limit." The one lair knob §19.7 missed lives on the root agent and is
  22.7.
- **The rescue/defection subsystem** (§20.4) — the mechanism is §20.4's;
  22.2 adds only the base bodies, 22.4b the post-victory handoff.
- **`SpecialScript` + `$NewThread (slot, interval, agent)`** (§18.7) —
  `$Curse_Active` on the enemy Wizard's Guild (3814-3816),
  `$Hero_Generator` on every enemy guild in `DEAL_DEMON`, and
  `Setup_High_Level_Members` on a rescued guild.
- **Script-slot idioms** (§18.2/§21.3) — `$NewThread`, `$RunThread`,
  `$KillThread`, `$SetThreadInterval`, `$RetrieveAgent ("GplAIRoot")`, a
  thread that replaces its own slot function to become a different job,
  and `$Reset_Tasks` after a slot swap (`pet_ready` 2949). The genuinely
  new slot uses are 22.6b (inversion), 22.6e (mailbox) and 22.6g
  (another agent's slot).
- **`$CreateEffector`'s duration-0 one-shot, its `"infinite"` string form,
  and its amount-carrying 4-argument form** (§13) — `"got_item"` (1564),
  `$createeffector (pet, "charm_icon", 1, "infinite")` (2920), and
  `$CreateEffector (Palace, "got_gold_bldg", 0, <amount>)` at five reward
  sites (2536, 2552, 3358, 3478, 3489). Same three forms §13 documented;
  `"got_gold_bldg"` is just another effector name.
- **`$GetPlayerData` / `$AdjustPlayerData` with the gold string key**
  (§5/§17.2) — the four gold-threshold victory tests (1295, 1334, 1844,
  1913), each followed by an `$AdjustPlayerData (palace, "gold",
  -<amount>)` that **deducts the money you just proved you had**. One
  note: the getter is called with `"Gold"` and the setter with `"gold"`
  two lines apart, a further instance of the string-key case
  inconsistency §13/§17 flagged — and per 22.8 that still licenses
  nothing about *title-value* comparisons.
- **`#ATTRIB_currentstagebuilt` as the "is this upgrade finished" test**
  (§16.1) — `barren_victory` 100 and 110, paired with `palace's "level"`.
- **`$DebugOut`, variadic** (§20.5c) — `BRASHNARD`'s `$ListSize != 7`
  map-integrity assertion (3558-3560) is an interesting *use*, not a new
  primitive; several commented-out `$DebugOut` probes survive beside it.
- **`$IsDead` guards before dereferencing a stored agent** (§18) —
  including on `$FindInventoryItem`'s return (3933-3934).
- **`$SetVictoryCondition`** (§16.2) — one call, in `Freestyle()` (22.4a).
- **`$GetUnitPlayerNumber` / `$SetUnitPlayerNumber` / `#Monster_Player` /
  `#Player_1`** (§14/§17) — throughout, and the whole basis of the
  rescue-claim step.

**Absent from this file entirely, worth knowing so nobody looks:** no
`$Hide`/`$Unhide`/`$FadeIn`/`$FadeOut` (§21.7), no
`$PlaceRewardFlag`/`#RewardFlags` (§21.6b), no `$NeutralTeamNumber` and no
`Permanent_Hostility` (§21.6d) — the two team-number calls here only start
wars, never end them; no `$ListFamily` and no `$RevealWholeMap` (§19.8),
no `$SetEffectorDirection` (§21.4e), no `resist_critical` (§20.3a), no
`Self_Estimation`/`Enemy_Estimation` (§19.9), no `$CreateSpellUnit`
(§17.2) — the only spell application is the direct `$lightning_bolt_hit`
call in 22.6d; no `$RemoveTitles` (§19.6) — `remove_statues` (22.2)
hand-rolls it instead; no `$ClearEngineDeathFlags` (§19.10), no
`$Freeze_Unit` (§11), no `$Control_Monster` (§9), no `$IsValidGamePiece`
(§18 — this file guards with `$IsDead` alone), no live `$Make_PC_Hunter`
(only the commented-out `$make_raider` above), no `"Closed"` retitle
(§21.3), and **no `=`-in-a-condition instances** (§19.3) — every
comparison in all 4358 lines uses `==`.

**Two stylistic notes, so nobody mistakes them for mechanisms.** First,
the file prefers copy-paste to loops even more than its siblings: 16
identical `$spawnunit` Dragon/Harpy lines at 1493-1500, 14 more at
3666-3672, the 14- and 11-call `$DisableUnitType` walls, and three
byte-identical `while` blocks spawning `#force_raider` Skeletons
(2790-2826). Second, it carries a lot of commented-out code that
documents intent rather than dead ends — the abandoned `$make_raider`
conversion (1520-1523), the replaced `Epic_Quest_Item` field writes
(195/202/209), `Magical_Repair`'s cut visual effect (4168-4171), and
`Holy_Chalice_Victory_2`'s commented tick-counting block (548-556) that
`demon_victory2` ships live (22.4d).

### 16.4 Batch A scope and open items

Read in full and cited above: `construction_rules.gpl`,
`victory_conditions.gpl`, `mx_Construction_Rules.gpl`,
`mx_Victory_Conditions.gpl`. Supporting reads: constant declarations in
`globals.gpl` / `mx_Globals.gpl` / `defines.gpl` / `mx_defines.gpl` /
`MajCompatibility.gpl` / `LowLevel.gpl` / `mx_LowLevel.gpl`, the
`Freestyle()` caller in `epic_quest_scripts.gpl` /
`mx_Epic_Quest_Scripts.gpl`, `$removetitles` usage sites across
`GPLMx/`, and `M_Buildings.xml`'s `Wizards_Tower` entry.

Not resolved in this batch:

- **When exactly the exe calls `CanIBuildThisBuilding`** (build-menu
  filter vs. placement cursor) and **what it puts in `dependencies`** —
  both need an exe trace; neither is inferable from any shipped script or
  data file. Candidate Ghidra item, not yet scoped in `TODO-Ghidra.md`.
- **Where the freestyle victory dropdown's rows are defined** (UI/`.cam`
  side) — needed before a modder can safely repurpose a row rather than
  guess from the `$debugout` index.
- **Whether `$removetitles` exists in the base-game exe** — it has zero
  base-`GPL/` call sites.
- `SDK/Documentation/GPL Reference.pdf` was not readable with this
  pass's tools; it may document the engine-called-callback contract for
  `CanIBuildThisBuilding` and the `$GetVictoryCondition*` primitives.
- The remaining `Rules/` files (`Demo.gpl`, `Random_Events.gpl`,
  `Special_Events.gpl`, `Quest_Actives.gpl`, `Quests_1/2/3.gpl`,
  `epic_quest_scripts.gpl` beyond the `Freestyle()` function) are
  Batches B-G, untouched here except for the specific line citations
  above.

### 17.6 Batch B scope, and what's still unresolved

Read in full: `GPL/Rules/Demo.gpl`, `GPLMx/Rules/mx_Demo.gpl`,
`GPLMx/Rules/Random_Events.gpl`, `GPLMx/Rules/Special_Events.gpl`.
Supporting reads (targeted, cited inline): `Quests_3.gpl` lines 400-760
(the tier dispatchers, `Setup_Trade_Markers`, `GetMarker`),
`mx_Epic_Quest_Scripts.gpl` lines 4010-4130 (`Freestyle()`,
`Setup_Multispawning_Lairs`, `setup_starting_treasure`),
`GPL/Rules/epic_quest_scripts.gpl` lines 4080-4105 (base `Freestyle()`),
`GPLMx/mx_prototype.gpl` lines 1100-1135 (`Prototype EventAgent`),
`GPL/Monster_Births.gpl` lines 1-30 + 495-535 (`monster_birth`,
`check_override_behavior`, `Setup_Quest_Monster`'s DEMO branch),
`mx_Monster_Births.gpl` lines 140-245, `GPL/globals.gpl` /
`mx_Globals.gpl` `#force_*` and `#Monster_Spawn_Cap` blocks,
`mx_defines.gpl` lines 226-247 (`#Message_*`),
`Sewer_Graveyard.gpl` lines 125-145 (`random_time`),
`make_attack.gpl` lines 486-515 (`player_spell_attack`), plus the two
`.gplproj` build files and the SDK Notepad++ keyword list.

One extra confirmed hook worth flagging for later batches:
**`Setup_Quest_Monster` is a per-quest monster-spawn override keyed on
`AIRootAgent's "Quest_Number"`.** `Demo.gpl` sets
`Quest_Number = #QNumber_DEMO` (500, `globals.gpl` line 663) purely so
that `GPL/Monster_Births.gpl` line 510's branch fires: any monster whose
title is `"Vampire"` spawns 4 skeletons alongside itself. That's the
mechanism behind `Demo.gpl`'s comment "The Vampires spawn a bunch of
Follower Skeletons in Setup_Quest_Monster." **Reusable: to give a quest
custom spawn behavior for a unit type, add a `Quest_Number` branch there
instead of editing spawn call sites.** `#QNumber_DEMO` is also
special-cased in `LowLevel.gpl` line 21 / `mx_LowLevel.gpl` line 89 to
return a hardcoded string index 20 — a reminder that `Quest_Number` is
read by unrelated subsystems, so pick a unique value.

Open items from this batch:

- ~~**Where the freestyle "special event" dropdown's selectable names
  live**~~ — **RESOLVED after this batch's main pass, see §17.7.** It is
  CAM `STRT` data in `DataMX/mx_gpltext.cam` (`EVSC` binds ID→function
  name, `ENTX` the label, `EDTX` the description) — not exe-side. Since
  quest-CAM `STRT` override is already confirmed working, the whole
  special-event framework is quest-distributable and §17.3's "needs an
  exe/UI change" verdict is superseded. No Ghidra required.
- **Residual sub-question from §17.7: is the dropdown's row *count*
  data-driven?** (i.e. does adding an `EV16` row to all three tables make
  a 16th entry appear, or does the engine read a fixed 16?) This is the
  only thing between the framework and being fully open-ended, and it's
  an **in-game test, not a Ghidra item** — now tracked in
  `TODO-GameTests.md`.
- **What the numeric field in each `EVSC` row does** (20-95, correlating
  loosely with event severity; no GPL reads it, so the consumer is
  engine-side). §17.7.
- **Whether `$GetSpecialEvent1Script`/`$GetSpecialEvent2Script`/
  `$LookupFunction` exist in the base-game exe.** The SDK keyword list is
  a single shared file that doesn't distinguish base from expansion, so
  keyword presence is not proof for base mode. `$LookupFunction` at least
  sits in the `Keywords3` block alongside primitives used constantly in
  base GPL; the two `$GetSpecialEvent*` calls have zero base call sites.
- **`"Special_Spawn_Type"` vs. `"Has_Special_Spawn"` semantics** —
  `Demo.gpl` sets only the former, `Wake_the_Hunters` sets both. Neither
  field is read anywhere in the `.gpl` tree, so the reader is engine-side.
- **Whether a `#Message_*` index above the shipped range (254) renders
  any text**, and more generally whether new message/sign string indices
  can be added data-side. Same open question as §16.1's `#chat_*` return
  codes; unresolved by this batch.
- **Whether `$disableunittype` on a tier-1 building also prevents an
  existing higher tier from being upgraded**, and the internal storage
  those primitives write to (already tracked as `TODO-Ghidra.md` §5.2).
- **Whether GPL guarantees zero-initialized locals** (`Bandit_Event`
  depends on it).
- `SDK/Documentation/GPL Reference.pdf` remains unreadable with this
  pass's tools; it likely documents `$LookupFunction`, `$SpawnUnit`'s
  real argument grammar, and the `$GetSpecialEvent*` contract, all of
  which are inferred from call-site usage above.
- Batches C-G (`Quest_Actives.gpl`, `Quests_1/2/3.gpl` beyond the
  cited ranges, the rest of `epic_quest_scripts.gpl`) remain untouched.
  (Batch C = `Quest_Actives.gpl` is now §18.)

### 18.11 Batch C scope, and what's still unresolved

Read in full: `GPL/Rules/Quest_Actives.gpl`,
`GPLMx/Rules/mx_Quest_Actives.gpl`,
`GPL/TaskModules/Characters/Henchmen/hooligan.gpl`,
`GPL/TaskModules/Buildings/Treasure.gpl`, and
`GPL/TaskModules/Characters/Travel_to.gpl` lines 1-260 (the travel family
plus `has_arrived`/`ReachedTargetDistance`). Supporting targeted reads, all
cited inline: `GPL/TaskModules/Subtasks/Inventory.gpl` lines 110-230
(`QItem_Stat_Boost` and its `#QItem_Magic_Ring` branch) and
`GPLMx/…/mx_Inventory.gpl` lines 114-145,
`GPL/DecisionTrees/Modules/Eval_Items.gpl` lines 95-105 (the
`$QItem_Stat_Boost` caller), `GPL/Hero_Births.gpl` lines 60-210 + 336-406
(`Generate_Character_Attributes`, `hero_birth`, `Hooligan_birth`),
`GPL/Rules/epic_quest_scripts.gpl` lines 415-475 (`HOLY_CHALICE`),
3209-3290 (`MAGIC_RING`), 3725-3880 (`WIZARDS_CURSE`), 3960-4060
(`Wizards_Curse_Victory`'s captive-rescue block) and 4145-4175
(`Magical_Repair`), `GPL/LowLevel.gpl` lines 1250-1300 (`Is_Free_Task`),
`GPL/prototype.gpl` lines 248-300 + 353-458 and the `hero`/`monster`
blocks (slot declarations),
`GPL/TaskModules/Characters/Follow_Heal.gpl` lines 1-140 (the follow
template `Arrest_Hooligan` clones), `GPL/Monster_Data.dat` lines 595-610
(the Hooligan's declarative script binding),
`SDK/OriginalQuests/Data/M_ParticleSystems.xml` entry `XL17`, plus
constant declarations in `globals.gpl`/`mx_Globals.gpl`/`defines.gpl`/
`QItems.gpl` and both `.gplproj` build files.

**Headline results.** No engine-invoked hooks live in this file (18.1) —
its value is the catalogue of *which script slot to write for which
effect* (18.2) plus seven clonable behavior templates: courier/delivery
(18.3), interposed AI wrapper (18.4), claim-and-follow via `$Is_Free_Task`
(18.5), minimal decision tree + `EvaluationScript` leash (18.6),
building-as-active-agent via `SpecialScript` (18.7), respawn-by-rebirth
with `function`-typed installers (18.8), and arrive-and-despawn plus
runtime defection (18.9). All of it works in **base game mode** — nothing
here is expansion-only (18.0).

Not resolved in this batch:

- **What `"avoid_vehicles"` actually makes `$Move` avoid.** Eight
  consistent call sites establish the *intent* ("travel safely"), not the
  mechanism; no GPL reads it back, so the behavior is engine-side.
- **Whether `Treasure_Spawner()` is reachable at all.** Zero references
  anywhere in the workspace; whether a `.q` file could name it as an entry
  function is **UNVERIFIED** (argued against by this project's own 12-byte
  pattern-name note, which is an internal reverse-engineering claim, not a
  confirmed engine fact).
- **Whether `$SetAttribute(agent, #ATTRIB_HP, 0)` deletes the agent**, and
  therefore *why* respawn-by-rebirth works (18.8). `Open_Chest`'s comment
  says it deletes; the shipped Holy Chalice economy depends on it not
  deleting, or on `Type = "Dead"`/`#ATTRIB_AlwaysView` deferring cleanup.
  An in-game test or Ghidra trace, not more source reading.
- **Which art `#ATTRIB_ForceBuildingState`'s `active`/`inactive` actually
  select** — `Drop_Ring`'s comment and its code disagree (18.3). Settled by
  one in-game observation.
- **The exact engine ordering of `Generate_Character_Attributes` vs.
  `hero_birth`** — inferred from the `Be_Dumb` install's dependency (18.4),
  not traced. Same class of open question as §16.1's "when does the exe
  call `CanIBuildThisBuilding`."
- **Whether a never-cleared `"Hostiles"` list has any consequence** for an
  agent whose `EvaluationScript` skips the clear (18.6).
- ~~**What `Guardian_Mod` does** — no live reader traced.~~
  **CORRECTED before publishing, by grepping instead of assuming (kept
  visible per this guide's convention): `Guardian_Mod` is fully traced and
  NOT unresolved.** It is a declared `monster` prototype field
  (`prototype.gpl` line 212, comment: "This is multiplied times a Guardian
  Monster's sightrange to find the area that they will pick a random coord
  to move to (around their home)"), set per-unit-type in `Monster_Data.dat`
  (mostly 5; 3 for the Hooligan and PC-Hunter-ish types; 2 for one
  Guardian) and overridable in GPL (`Varg's "Guardian_Mod" = 2`,
  `epic_quest_scripts.gpl` line 3826). Live readers:
  `GPL/TaskModules/Characters/Monsters/Guardian.gpl` line 20
  (`$RandomCoord(ThisAgent's "coord_home", SightRange * Guardian_Mod)` —
  the wander area) and lines 127/240 (`SightRange * Guardian_Mod +
  #ATTRIB_MaxAttackRange` — the **leash distance at which a guardian
  abandons a chase**), plus `Returning_Guardian.gpl` line 109.
  **So the data-driven equivalent of 18.6's hardcoded 500-unit hero leash
  already exists for monsters: `coord_home` + `Guardian_Mod × sightrange`.**
  `Hooligan_Basic`'s wander uses `#Hooligan_Wander_Mod` (3) instead, with
  the `Guardian_Mod` form sitting commented out one line above — the
  hooligan is the one unit that ignores its own field.
- Batches D-G (`Quests_1/2/3.gpl` beyond the ranges cited in §17 and here,
  and the rest of `epic_quest_scripts.gpl` — this batch read roughly 400 of
  its ~4300 lines) remain open.

### 19.12 Sources and headline results

**Read in full:** `GPLMx/Rules/Quests_1.gpl` (2232 lines).
**Supporting reads (all direct, all cited inline):**
`GPLMx/mx_Music_Player.gpl` and `GPL/Music_Player.gpl` (both complete);
`GPLMx/mx_Monster_Births.gpl` lines 148-207 and 820-880;
`GPLMx/mx_Monster_Deaths.gpl` lines 225-295;
`GPLMx/mx_Building_Deaths.gpl` lines 264-330;
`GPLMx/TaskModules/Buildings/Autospawn_Lair.gpl` (complete);
`GPLMx/Rules/mx_Epic_Quest_Scripts.gpl` lines 1-55;
`GPLMx/mx_LowLevel.gpl` lines 55-90;
`GPLMx/mx_prototype.gpl` (lair / hero / monster / palace field
declarations); `GPLMx/mx_Globals.gpl` and `GPL/globals.gpl` (music,
`#force_*`, lair and cap constants); `GPLMx/MajCompatibility.gpl` line 103;
`GPLMx/mx_Victory_Conditions.gpl` line 7;
`GPLMx/mx_Building_Births.gpl` lines 150-170 and 995-1005;
`GPL/Monster_Data.dat` line 510 and `GPLMx/mx_Monster_Data.dat` line 867;
`Data/MusicTracks.txt`; `GPLMx/Path_Data.gplproj`.

**Headline results — six genuinely new mechanisms:**

1. **The music subsystem** (19.4): `$PlayMusic` / `$LastMusicTrack` /
   `$SetMusicStoppedCallback`, the last being a **string-named callback
   registration**, plus a plain-text track registry
   (`Data/MusicTracks.txt`) and an orphaned sixth track no shipped GPL
   plays. Custom quest music needs no XML, CAM or exe change.
2. **The `#force_*` loop closed** (19.6): the artifice→behavior table is
   editable GPL, so a modder can **add their own `#force_*` value and
   behavior function**; `#force_overlay` turns out not to be a behavior at
   all (cosmetic, and only the Troll can read it); and
   `Target` + `Relentless` + `$Monster_Attack_Object` is a
   no-artifice-needed "chase that specific unit" recipe.
3. **§17's `Special_Spawn_Type` / `Has_Special_Spawn` question resolved**
   (19.7) from `lair_death`: payload vs. priority-override, with `"xx"` as
   the unset sentinel — plus the rest of the writable lair field set
   (`Max_Simul_Spawns`, `Max_Stored_Spawns`, `History_Modifier`) and the
   lair spawn-function template, including the finding that
   `#Monster_Spawn_Cap` is a **GPL convention each spawn function must
   enforce itself**, not an engine limit.
4. **The self-pacing staged sequencer** (19.3) — a fourth event-thread
   lifecycle beyond §17.4's three, where one thread walks a flag chain,
   sets its own next interval per stage, and ends in a difficulty-ratchet
   `Else`.
5. **Multi-faction warfare** (19.8) via `$SetPlayerTeamNumber` +
   `$NewTeamNumber` applied to *lairs*, `$RevealWholeMap (#Player_N)`, and
   the `$ListFamily` population equalizer.
6. **Conditional resurrection in place** (19.10) via
   `$ClearEngineDeathFlags` + `"Type"` lifecycle swapping, using the dead
   unit's own script slot as the timer — a different mechanism from both
   §8's gravestones and §18's respawn-by-rebirth.

**Plus five smaller additions:** `$IsTitleAlive`'s monster∪invisible union
(19.5a); the two-stage-victory flag-gate shape (19.5b); "protect what you
cannot build," composed entirely from `$DisableUnittype` + `$DeclareLoss`
(19.5c); **quest threads survive `$declarevictory`**, which is how "keep
playing after you win" actually works (19.5d); and the elite-NPC
stat-stack recipe including `Attack_Action = "Do_Nothing"` + the
dual-range caster conversion (19.9).

**Explicitly recombination, not new:** everything in 19.11 — the
`$SpawnUnit` grammar, `"MaxHP"`, the coordinate helpers, the
message/beacon/reveal trio, `$CreateSpellUnit`, `$setup_random_treasure`,
`$SetUp_Respawning_Lairs`, `$DisableUnittype` itself, and
`$Make_PC_Hunter`-at-runtime. Most of this file's *volume* is
recombination; the findings above are the part that isn't.

**Correction recorded (kept visible per this guide's convention):** §14's
claim that `$ListTitles` is the primitive which additionally strips
matches out of its source list is **contradicted** by two call sites in
this file — the stripping belongs to `$RemoveTitles` (19.6). The original
finding was right that `$RemoveTitles` returns the matching members.
**Correction has since been applied in place** — the wrong sentence lives
in **§16.1** (the mx-diff discussion of the `wizards_tower` branch), not
§14 as first reported, and now carries a visible CORRECTED note pointing
back here.

**Not resolved in this batch:**

- **What `$LearnSpell`'s third argument (`FALSE`) means** (19.9). Seven
  call sites in this file, all `FALSE`; no reader traced.
- **Whether `Data/MusicTracks.txt` is 1-indexed**, and whether appending a
  7th line makes track 7 playable (19.4). Name alignment strongly implies
  1-indexed; settled by one in-game test.
- **What `=` in a condition compiles to** (19.3). Two shipped instances;
  either reading breaks the intended behavior.
- **Whether agent attribute name lookup is case-insensitive** (19.5) —
  inferred from `"End_Coord"` / `"End_coord"` shipping and evidently
  working, not from a grammar document.
- **Which duplicate `#wight_gravestone_interval` wins** (19.10) — 80000 in
  `mx_Globals.gpl` vs 120000 in `MajCompatibility.gpl`.
- **How `Self_Estimation` / `Enemy_Estimation` are consumed** (19.9). The
  fields, their types and their writers are confirmed; the retreat/engage
  logic that reads them was not traced.
- **`$SetPlayerTeamNumber`'s exact scope** (19.8) — inferred to act on the
  agent's *player* from the one-call-per-faction usage, not confirmed.
- ~~**What populates the `"invisible"` `$ListObjects` type class**
  (19.5a)~~ — **RESOLVED by Batch E, see §20.2.** `"invisible"` and
  `"camouflaged"` are written by GPL spell code overwriting
  `thisagent's "type"` (five sites across base and mx), with
  `"original_type"` as the stash and `"subtype"` as the recovery field —
  i.e. `$ListObjects`' second argument is the agent's own writable
  `"type"` string, not a fixed taxonomy.
- Batches F-G (`Quests_3.gpl`, and the bulk of
  `epic_quest_scripts.gpl` / `mx_Epic_Quest_Scripts.gpl`) remain open.
  **Batch E is done — see §20**; both leads this batch flagged for it
  (`"RhodenKingRat"`'s `$IsTitleAlive` quest and the
  `$Make_PC_Hunter` + `#ATTRIB_sightrange` loop) turned out to be pure
  recombination of §19 mechanisms, per §20.8.

### 20.9 Sources and headline results

**Read in full:** `GPLMx/Rules/Quests_2.gpl` (977 lines).

**Supporting reads, all direct and all cited inline:**
`GPLMx/Rules/mx_Epic_Quest_Scripts.gpl` lines 1148-1200
(`setup_hero_level`, `all_enemies_dead`) and 2795-2990
(`setup_rescue_buildings`, `setup_rescue_pets`, `rescue_pets`,
`pet_ready`, `rescue_buildings`);
`GPLMx/TaskModules/Subtasks/mx_Spells.gpl` lines 1118-1145 plus targeted
searches for every `"type"` write in that file;
`GPLMx/TaskModules/Subtasks/mx_make_attack.gpl` lines 194-198 and 237-241
(the `resist_critical` reader — read via targeted search with context,
not the whole function);
`GPLMx/mx_Monster_Births.gpl` lines 765-830 (the four `make_*` installers);
`GPLMx/mx_Building_Deaths.gpl` lines 705-760 (`guild_destroyed_common`,
`GuardHouse_Death`);
`GPLMx/TaskModules/Buildings/mx_Lair.gpl` lines 180-195 (`Hero_Generator`);
`GPLMx/mx_Hero_Births.gpl` lines 576-594 (`High_Level_Hero_Birth`);
`GPLMx/mx_prototype.gpl` (hero/monster field declarations — lines 107,
118-119, 169-170, 217-218, 222, 252-253) and `GPL/prototype.gpl`
(lines 86-87, 137-138, 176-177) for the base twins.
**Base twins located by search but NOT diffed line-by-line:**
`GPL/Rules/epic_quest_scripts.gpl` (2858, 2953, 1178),
`GPL/TaskModules/Buildings/Lair.gpl` 157, `GPL/Building_Deaths.gpl` 526,
`GPL/TaskModules/Subtasks/Spells.gpl` 1074/1389, `GPL/Monster_Births.gpl`
570. Treat those as "present, body unconfirmed."

**Headline results — six genuinely new mechanisms:**

1. **`"type"` is the `$ListObjects` class register, not a fixed taxonomy**
   (20.2). Resolves §19.12's open question outright: `"invisible"` and
   `"camouflaged"` are populated by GPL spell code writing
   `thisagent's "type"`, with `"original_type"` as the stash and
   `"subtype"` as the recovery field. Same register carries
   `"unknown"`/`"pet"`/`"hidden"`/`"Dead"`/`"Waiting_to_die"`. **Practical
   rule: any census must union `"invisible"` + `"camouflaged"` and filter
   on `"subtype"`** — three shipped helpers do, and the shipped comment on
   `guild_destroyed_common`'s `Type = "Dead"` spells out the reason.
2. **Heroes as quest content** (20.3): the five-write enemy-hero boss
   recipe (`$Advance_To_Level` + paired `#ATTRIB_MAXHP`/`#ATTRIB_HP` +
   runtime retitle + `resist_critical`), and **critical hits are coded as
   damage equal to the target's MaxHP, divided by 6 if the defender
   resists** — reader traced in `mx_make_attack.gpl`. Plus
   `$make_raider` on hero-type agents, which the hero prototype's own
   shipped comment blesses ("jim hackerama so heroes can become raider
   mosnters").
3. **The rescue/defection subsystem** (20.4): park → discover → claim,
   built entirely on the `"type"` register; `enemytype = "nothing"` as the
   combat-participation switch; the five named threads that must be killed
   to deactivate an outpost; the `SpecialList` two-members-per-record
   parallel-list protocol drained with `$RemoveListMember(list,1)` twice;
   and the pet variant's arming delay via the unit's own `ActiveScript`
   interval.
4. **Two poll-thread patterns** (20.5): **latch-on-appearance** (wait for
   the count to reach 1 before testing for 0) and a **live-tracking
   `end_coord`** that gives a victory camera without a death hook.
5. **Building hijack, the destructive variant, and higher-order death
   handlers** (20.6): `ActiveScript` on a non-guild building overwrites
   its behavior with no stash (vs. `SpecialScript` being additive);
   `$guild_destroyed_common(agent, function)` takes a **GPL function as a
   value**, not a name string; three stock death handlers
   (`$Lair_Death`/`$guild_destroyed_common`/`$building_death`) confirm the
   "add behavior then tail-call the family handler" convention; guild
   recruitment is data-driven via `"Members"`/`"Member_Title"`; and
   `$SpawnUnit(<player building>, "<lair>", "maxhp")` erupts an enemy lair
   inside the player's city.
6. **Two quest-setup primitives** (20.7): `$ElvesVoice_setOperative` /
   `$dwarvesVoice_setOperative` (engine-side, base+mx, always paired with
   the matching `$DisableUnitType`), and `$setup_hero_level` with
   `#ATTRIB_StartedwithThisUnit` — plus the "fixed roster" quest genre
   they compose into.

**Prior-batch items resolved or advanced:**

- **RESOLVED — §19.12's "what populates the `"invisible"`
  `$ListObjects` type class."** See 20.2. Five write sites in two files,
  base and mx, plus the restore path and the corroborating comment in
  `guild_destroyed_common`.
- **COMPLETED — §19.6's dispatch table** now has bodies for all four
  previously-blank installers (`make_raider`, `make_caravan_raider`,
  `make_guardian`, `make_bomber`); all four install
  `$monster_eval_enemies`, two also set `"Raider_respond" = TRUE`
  (20.3c). Consequence: this file's `evaluationScript` write after
  `$make_raider` is a **no-op duplicate**, not a mechanism.
- **NARROWED, still open — §19.12's "`$SetPlayerTeamNumber`'s exact
  scope."** A second one-call-per-faction site plus its
  `$GetPlayerTeamNumber` idempotence guard (20.4), consistent with
  per-player scope but not proof.
- **Not answerable from this file:** `$LearnSpell`'s third argument,
  `Self_Estimation`/`Enemy_Estimation` consumers, `MusicTracks.txt`
  indexing, and what `=`-in-a-condition compiles to — **none of those
  constructs appear in `Quests_2.gpl` at all** (20.8).

**Explicitly recombination, not new:** everything in 20.8 — the quest
skeleton, the staged sequencer, `$IsTitleAlive`, the two-stage victory
gate, `$PlaySound` taunts, `$Make_PC_Hunter`-at-runtime, the artifice
spawn form, the coordinate helpers, the message/beacon pair,
draw-without-replacement, `$DisableUnitType`, the music calls,
`$declarevictory`, and `SpecialScript`+`$NewThread`. **Both of the
`$IsTitleAlive` and `$Make_PC_Hunter` leads flagged for this batch turned
out to be recombination**; the third and fourth leads (the
`SpecialScript` install at line 574 and the `evaluationScript` write at
line 702) turned out to be, respectively, already-cited in §18.7 and a
redundant no-op — the value in chasing them was in the *surrounding*
code, which is 20.6 and 20.3.

**Still UNVERIFIED after this batch:**

- **Whether the engine also writes `"type"`** (20.2), or GPL does all of
  it. Every write found is GPL-side; an engine writer is invisible to
  source reading.
- **What gates phase 2 of the rescue** (20.4) — the absence of
  `#NoHiddenMap` on the `"unknown"` query is the only difference from the
  setup query, and reading it as "only explored buildings" is an
  inference complicated by `#NoHiddenMap` being numerically `0`.
- **Whether the `ActiveScript` hijack leaves the old thread running**
  (20.6a) — no `$KillThread` precedes the assignment.
- **Whether `$SpawnUnit` runs `$Generate_Character_Attributes`
  automatically** (20.6b) — `Hero_Generator` calls it explicitly, which
  suggests not, but a redundant call looks identical in source.
- **What the engine consumes `#ATTRIB_StartedwithThisUnit` for** (20.7) —
  five writers, no reader.
- **What `$ElvesVoice_setOperative`/`$dwarvesVoice_setOperative` actually
  silence** (20.7) — engine-side, inferred from naming plus a
  100%-consistent pairing with `$DisableUnitType`.
- **Why latch-on-appearance is needed** (20.5a) — spawn-visibility
  latency is the obvious reason; the pattern is confirmed, the reason
  isn't.
- **Why the palace is absent from the `#ATTRIB_FirstStageBuilt` building
  query** (20.6) and has to be `<<`-appended.
- **What the `#ATTRIB_MaxGuildMembers` +20 on a dying guild is for**
  (20.6).
- **Whether `$Make_PC_Hunter` without a following `$Reset_Tasks` takes
  effect promptly** (20.8).
- **The base twins of the rescue/hero-level helpers were not diffed**
  against their mx versions (20.9 sources).
- Batches F-G remain open: `Quests_3.gpl`, and the bulk of
  `epic_quest_scripts.gpl` / `mx_Epic_Quest_Scripts.gpl` (~4300 lines,
  of which this batch read roughly 250 lines around the rescue and
  hero-level helpers). Incidental observations for whoever takes them:
  `mx_Epic_Quest_Scripts.gpl` line 3030 has the same wrong-target
  `$setattribute(thisagent, …)` shape as 20.5c inside the `SpecialList`
  drain loop; `all_enemies_dead` (line 1167) is a ready-made six-class
  union census with a hardcoded exclusion list of "doesn't count as an
  enemy" titles (ratman, giant_rat, sewer, graveyard, skeleton, zombie,
  troll) that looks like a reusable victory-condition helper.

### 21.10 Sources and headline results

**Note on this subsection:** the Batch F dispatch was interrupted after
writing 21.0-21.9, so this closing subsection was written separately to
consolidate the UNVERIFIED items already flagged inline above and to
resolve the forward references to "21.10" in 21.3, 21.6b and 21.8. Every
item below is a consolidation of a claim already made and cited in
21.0-21.9 — no new source reading was done for it, and nothing here
introduces a finding not already supported above.

**Read in full:** `GPLMx/Rules/Quests_3.gpl` (2977 lines), minus lines
~524-756 which Batch B had already covered (§17.2) and which 21.0
deliberately does not re-derive.

**Supporting reads** are cited inline at each point of use in 21.2-21.8
(`mx_prototype.gpl`'s root-agent slot/register declarations,
`mx_Building_Deaths.gpl`'s stock teardown sequence, stock `Tower.gpl`'s
scan/attack pair, and the specific helper functions this file calls).
**Per the dispatch's scope limit, `epic_quest_scripts.gpl` /
`mx_Epic_Quest_Scripts.gpl` were NOT read broadly** — only individual
helpers this file actually calls were followed, and Batch G still owns
those files.

**Headline results — the four systems, and why they matter:**

1. **Externally-scored graded victory** (21.3) — `TRADE_ROUTES` is the
   only quest in §16-§21 whose outcome is decided by a scorer called from
   *outside* its own file, across 5 checkpoints × 4-5 outcome bands, using
   a script slot compared against a function value as an
   "already-decided" latch. The reusable shape for any delivery/escort
   game with graded endings.
2. **The self-retiering lair** (21.4) — the most transferable single
   system in the batch: *fewer* spires makes the survivors *harder*, with
   compensation scaled to the player's own army, implemented by swapping a
   `function`-valued `Spawn_Function` field and an `Attack_Action` spell
   name at runtime, and using `$SetEffectorDirection` as a visible tier
   readout with no extra art.
3. **A complete AI opponent kingdom written in GPL** (21.6) — gold-budgeted
   recruitment, building-cast spells paid for by hand, `$PlaceRewardFlag`
   used *by* the AI, `SetEnemyResearch` writing `#ATTRIB_Research*`, and
   surrender-to-peace via `$NeutralTeamNumber` plus the
   `Permanent_Hostility` flag that stops a forced war auto-reverting.
4. **The phase-in/phase-out boss building** (21.7) plus **elapsed-time
   difficulty scaling** (21.8) — `$Hide(agent, marker,
   #TeleportInsideDestination)`/`$Unhide` with `$FadeIn`/`$FadeOut`, a
   float `SpawnPower` multiplier driven off a day counter and a
   days-since-last-appearance delta, and integer registers used as state
   machines.

**Prior-batch items resolved or advanced:**

- **RESOLVED — §20.6b's "does `$SpawnUnit` run
  `$Generate_Character_Attributes` automatically?"** It does not.
  `Enemy_Guild_Spawn` is a second independent call site *and* carries an
  explicit statement of intent in its own comment, so §20.6b's
  "suggests not, but a redundant call would look identical" inference is
  now a confirmed rule: **a hero created by `$SpawnUnit` must be passed
  to `$Generate_Character_Attributes` by hand** (21.6b). What specifically
  is missing without it — name, stat rolls, `StartingScript` — is still
  not enumerated anywhere in source.
- **NOT advanced — §19.12/§20.4's "`$SetPlayerTeamNumber`'s exact
  scope."** This file gives a third one-call-per-palace site, same shape,
  so it neither confirms nor refutes per-player scope (21.9).
- **Not answerable from this file** — none of these constructs appear in
  it at all (21.9's "absent entirely" list): `$LearnSpell` (so its third
  argument is still open), `Self_Estimation`/`Enemy_Estimation`,
  `MusicTracks.txt` indexing, and `=`-in-a-condition (every comparison
  here uses `==`).

**Still UNVERIFIED after this batch** — each already flagged at its point
of use above, consolidated here:

- **Which stock function retitles a Marketplace to `"Closed"`** (21.3).
  The value is confirmed live and the false-negative hazard is real; the
  writer was not traced.
- **`$SetEffectorDirection`'s index→frame mapping** (21.4e). Repurposing
  an 8-way direction index as a state index is confirmed; what each index
  displays is engine-side.
- **`$DropGoldEveryone`'s split rule** (21.5b) — name implies all players
  share the drop, which suits a captured treasury, but the division is
  engine-side.
- **Whether `$DeleteAgent` on an already-rubbled building differs
  behaviourally from the stock commented-out form** (21.5b) — both exist
  in shipped code; no difference established.
- **`#ATTRIB_CurrentEvent`'s event-index mapping** (21.6e) — only
  inferable from the one shipped comment.
- **Whether GPL silently discards extra call arguments or corrupts the
  call frame** (21.6f). A shipped call passes more arguments than the
  declared signature and compiles; treat it as a bug to avoid, not a
  feature. Needs a test, not more source reading.
- **What `"clear"` means as a `$SpawnUnit` string flag** (21.7) — "make
  room / ignore blockers" is the plausible reading from every call site
  spawning at a precise coordinate, but it is engine-side.
- **`-1` as a fourth effector-duration form** (21.7) — intent
  ("never expires, no callback") is unambiguous from the function header
  and the absence of any `_End` pairing; exact engine semantics are not.
- **`Fortress_Ixmil`'s `Warp_Out` scheduling** (21.8) — the shipped
  `else` branch appears to warp out visually without re-arming the next
  appearance. Because the engine may invoke these by name the way it does
  quest entry points (§17.5), this is recorded as an **unresolved wiring
  question, not a confirmed bug.**

**Batch G remains open:** `epic_quest_scripts.gpl` /
`mx_Epic_Quest_Scripts.gpl` (~4300 lines), of which prior batches have
read only scattered helpers — `Freestyle()` and a few `$declarevictory`
sites (§16, §17), `Setup_Multispawning_Lairs` and
`setup_starting_treasure` (§17), the rescue/hero-level helpers (§20.4,
§20.7), and whatever individual helpers this batch followed (21.10
sources). §20.9's two incidental finds still stand as leads for it: a
wrong-target `$setattribute(thisagent, …)` inside the `SpecialList` drain
loop at line 3030, and `all_enemies_dead` (line 1167) as a ready-made
six-class union census with a hardcoded "doesn't count as an enemy" title
list.

### 22.8 Sources and headline results

**Note on this subsection:** the Batch G dispatch was interrupted after
writing 22.0-22.7, so this closing subsection and 22.9 were written
separately, to resolve the four forward references left dangling in the
§22 intro, in 22.0, and twice in 22.2's helper table. Everything below is
a consolidation of claims already made and cited in 22.0-22.7, **except
three targeted re-reads done specifically for this subsection** and named
at their point of use: the `Setup_High_Level_Members` defect, the shipped
title strings behind 22.2's case-sensitivity question, and
`$LearnSpell`'s argument count.

**Read in full:** `GPL/Rules/epic_quest_scripts.gpl` (4358 lines, 85
function definitions).

**Targeted diffs against `GPLMx/Rules/mx_Epic_Quest_Scripts.gpl`:**
`Freestyle()` 4048-4109 (in full), `barren_victory` 135-152,
`all_enemies_dead`'s exclusion list 1190-1192, `setup_hero_level`
1155-1165, `Setup_High_Level_Members` 3010-3035, and every
`Quest_Number` write (the 19-quest roster check in 22.0).

**Supporting reads, all direct and all cited inline at their point of
use:** `GPL/prototype.gpl` (29, 42+) and `GPLMx/mx_prototype.gpl` (35,
59+, 65) for the root-agent registers; `GPL/Misc_Data.dat` 206 and
`GPLMx/mx_Misc_Data.dat` 207 for the `Lair_extra_Delay` default;
`GPL/TaskModules/Buildings/Lair.gpl` 31 and
`GPLMx/TaskModules/Buildings/mx_Lair.gpl` 44-52 for its consumer;
`GPL/Hero_Births.gpl` 506-539 and `GPLMx/mx_Hero_Births.gpl` 582
(`High_Level_Hero_Birth`); `GPL/Monster_Deaths.gpl` 140 (`Vendral_Death`,
the runner for 22.6e's parked slot);
`GPL/TaskModules/Buildings/Auto_Revenue.gpl` 268 and
`mx_Auto_Revenue.gpl` 265 (`$random_to_percent`);
`GPL/TaskModules/Buildings/Message_Signs.gpl` 8 and its mx twin
(`$Create_Sign`'s signature); and **`GPL/Monster_Data.dat` lines 380,
427, 473, 497, 569, 667** for the shipped `(title …)` strings used below.

**Headline results — six clusters of genuinely new material:**

1. **The reusable-helper catalogue** (22.2) — the highest-value half of
   the batch, because §17-§21 kept *calling into* this file without
   reading it. Signatures and contracts for the census predicates
   (`istitlealive`, `all_enemies_dead`, `no_monsters_titled`,
   `remove_statues`), the world-setup helpers (treasure, respawning and
   multispawning lairs, the rescue-heroes queue, hero level), and the
   per-tick helpers (`rescue_buildings`, `rescue_pets`,
   `Setup_High_Level_Members`) — plus `High_Level_Hero_Birth` as a
   **shared, extensible per-`#QNumber_*` starting-hero hook**.
2. **The difficulty-tier system** (22.3) — a post-victory "keep playing"
   harassment driver in four layers (roster → dispatcher → tier driver →
   install site), installed by 12 of the 19 quests, **base-only**, with
   no runtime difficulty input at all: the tier is a literal function
   reference authored into each quest's victory branch. Retuning a tier is
   two numbers; adding a fifth is four small edits in one file.
3. **Sequential message flags** (22.5) — `$IsMessageFlagPresent` plus the
   `Message_Check_N` root-agent registers, a named subsystem for queueing
   tutorial messages behind the player's dismissal of the previous one.
4. **Three post-victory / deadline patterns** (22.4) — `rescue_keep_playing`
   as a deliberately *downgraded* replacement thread in the slot victory
   just vacated; `*_victory2` as a deadline arbiter rather than a second
   win condition; and the **~1 800 000 ms interval ceiling with its
   tick-counting workaround** (count firings in a flag instead of
   lengthening the interval).
5. **`Lair_extra_delay` and `Lair_Delay_Override`** (22.7) — a global,
   per-quest, one-integer lair pacing knob that is both data-settable and
   GPL-settable, plus the `$HasAttribute` feature-detection pattern (22.4a)
   that its expansion-only sibling forced on both its reader and its
   writer.
6. **The 22.6 cluster, ten items** — `$EnableUnitType` as the base game's
   main mid-quest progression device (with `$ListCompleted` /
   `$ListCompletedTitles`); the slot-convention inversion that proves
   `"VictoryCondition"`/`"VictoryCondition2"` carry **no engine meaning**;
   `$GetNearestHiddenCoord`, the one out-parameter primitive found in this
   pass; the rain-of-lightning ambient harasser; **the script slot as a
   one-shot mailbox between two files**; `#Allow_Cloned_Quest_Item` +
   `$AgentHasInventoryItem` + `$ListSubtypesInRadius`; retiming and
   killing *another agent's* `"SleeperScript"` under an `$IsRunning`
   guard; `$SetDrawEffects` recolor-without-art; **temporary
   invulnerability** as `"Type" = "Invulnerable"` +
   `#ATTRIB_NotFlaggable` + `#ATTRIB_NotSpellTarget`, all three reversible;
   and `$EnchantWizTower`.

**The shipped defect in `Setup_High_Level_Members`** — resolves the
forward references in 22.0 and in 22.2's `Setup_High_Level_Members` row,
and confirms §20.9's incidental lead. Read in full at
`GPL/Rules/epic_quest_scripts.gpl` 3036-3066:

```gpl
Foreach Member in ThisAgent's "Members" do
    begin
        If ($ListSize (ThisAgent's "SpecialList") > 0)
            begin
                Start_Level = $ListMember (ThisAgent's "SpecialList", 1);
                $advance_to_level (Member, Start_Level);

                $setattribute(thisagent,#ATTRIB_StartedwithThisUnit,1);   // 3060
                $RemoveListMember (ThisAgent's "SpecialList", 1);
            end
    end
```

- **`thisagent` here is the guild building, not the hero.** The function
  is threaded by `rescue_buildings` as
  `$NewThread (Bldg's "SpecialScript", 500, Bldg)` (3030-3031), so its
  agent argument is the rescued guild; `Member` is the hero being
  levelled on the line above. The attribute therefore lands on the
  building every iteration.
- **Both modes ship it, and §20.9's line number was right:** base 3060,
  mx 3030, bodies otherwise identical (diffed).
- **One refinement to §20.9's description.** It recorded the write as
  being "inside the `SpecialList` drain loop," which is ambiguous —
  there are two loops that drain `SpecialList`. The first, in
  `rescue_buildings` (3006-3019), spawns the heroes and is correct; the
  defect is in the *second*, `Setup_High_Level_Members`' `Members` loop,
  which drains the re-seated levels list.
- **The correct form is 1870 lines earlier in the same file.**
  `setup_hero_level` 1189-1190 does `$advance_to_level(hero,explevel);`
  then `$setattribute(hero,#ATTRIB_StartedwithThisUnit,1);` — same pair
  of statements, right target. So this is a copy of a working idiom with
  the agent argument not updated.
- **Consequence, stated honestly:** the intended flag never reaches the
  rescued high-level heroes, and the guild gets an attribute it was not
  meant to have. Neither is observable from source, because **nothing in
  the `.gpl` tree reads `#ATTRIB_StartedwithThisUnit` at all** (§20.7,
  and still true after this batch). It is not a crash and not worth
  patching in the shipped game; it is worth not copying, and it is a
  clean example of why **the guild-scoped `ThisAgent` and the
  member-scoped loop variable must not be confused** in any
  `SpecialScript` thread you write.

**Prior-batch items resolved, advanced, or not answerable here:**

- **RESOLVED — §20.9's "the base twins of the rescue/hero-level helpers
  were not diffed."** All of them are now read in the base file at their
  base line numbers and catalogued in 22.2
  (`setup_rescue_buildings` 2858, `setup_rescue_pets` 2884,
  `rescue_pets` 2904, `pet_ready` 2930, `rescue_buildings` 2953,
  `Setup_Rescue_Heroes` 2838, `setup_hero_level` 1178), with
  `setup_hero_level`'s base body identical line for line to the mx
  version. Base-vs-mx differences in this whole 4358-line file reduce to
  22.0's two.
- **ADVANCED — §19.12's "what `$LearnSpell`'s third argument means."**
  The argument is **optional**. All four base-game call sites pass only
  two arguments (`epic_quest_scripts.gpl` 3831-3832 on Varg;
  `GPL/Hero_Births.gpl` 530-531 in `High_Level_Hero_Birth`), against
  §19.9's seven mx sites all passing `FALSE`. **What it means is still
  unread** — no reader traced, and the primitive is engine-side. A second,
  softer advance from the same two sites: both pair the spell grants with
  an experience-level raise, and 3834-3835 carries the shipped comment
  *"Set the Varg's level to 10 so that he actually learns the
  aforementioned spells"* — i.e. **spell learning appears to be gated on
  level**, and the level write may come *after* the `$LearnSpell` calls
  (it does on Varg; `High_Level_Hero_Birth` raises the level first). That
  is a developer comment plus a two-file ordering pattern, not a traced
  mechanism: a strong hint, **still UNVERIFIED**.
- **ADVANCED — §20.7/§20.9's advisor-voice toggles.**
  `dark_forest_victory` 863-889 is the first shipped call passing **1**
  (`$ElvesVoice_setOperative(1)` / `$dwarvesVoice_setOperative(1)`,
  22.6a), so the argument is a plain enable/disable boolean rather than
  something §20.7 could only infer from the `0` calls. **What they
  actually silence is still engine-side and open.**
- **NARROWED, still open — §19.12/§20.4/§21.10's "`$SetPlayerTeamNumber`'s
  exact scope."** Two more sites, both one call per palace (`MAGIC_RING`
  3313, `WIZARDS_CURSE` 3999), which on their own add nothing. The new
  evidence is on the *getter*: `WIZARDS_CURSE` 3997 tests
  `$getplayerteamnumber(item_holder) == $getplayerteamnumber(palace)`,
  where `Item_Holder` is whatever agent `$FindInventoryItem
  (#QItem_Spellbook)` returned (3932) — **not a palace**. So the getter
  demonstrably accepts an arbitrary agent and resolves through its owner,
  which is what "team number is a property of the player, not the
  agent" predicts. Consistent with per-player scope for the setter;
  **still not proof of it.**
- **UNCHANGED — §20.9's "what consumes `#ATTRIB_StartedwithThisUnit`."**
  This file adds two writers (1190, and the defective 3060) and no
  reader. A grep of every `.gpl` file in `SDK/OriginalQuests/` gives
  **six writes in four files and zero reads**:
  `GPL/Rules/epic_quest_scripts.gpl` 1190 and 3060,
  `GPLMx/Rules/mx_Epic_Quest_Scripts.gpl` 1162 and 3030,
  `GPL/Hero_Births.gpl` 510 and `GPLMx/mx_Hero_Births.gpl` 586 — so
  §20.9's "five writers" was an undercount, and the reader situation is
  unchanged. Worth restating precisely *because* the defect above
  is judged harmless on exactly that basis — the judgement is only as
  good as the no-reader search, which is source-side only.
- **NOT ANSWERABLE from this file — the constructs are absent entirely**
  (see 22.9): `Self_Estimation`/`Enemy_Estimation` (§19.9), the
  `=`-in-a-condition question (§19.3 — grepped for both the spaced and
  unspaced forms inside `if (…)`, zero hits; every comparison in the file
  uses `==`), the stock function that retitles a Marketplace to
  `"Closed"` (§21.3 — the string `"Closed"` does not appear in this file),
  and `MusicTracks.txt` indexing (§19.4).

**How far 22.2's title-case claim actually goes** — the second forward
reference from the `no_monsters_titled` row, answered as precisely as
source reading allows.

*Confirmed by direct read:* the shipped title values are capitalised.
`GPL/Monster_Data.dat` gives `(title Ratman)` 380, `(title Rock_Golem)`
427, `(title Skeleton)` 473, `(title Troll)` 497, `(title Zombie)` 569,
`(title  Dirgo)` 667.

*Confirmed:* `no_monsters_titled`'s only two callers are in
`fertile_victory` 2091-2092, and they pass `"Rock_Golem"` — an exact case
match, so it tests nothing — and `"dirgo"`, a real mismatch against
`(title Dirgo)`. The mismatched one goes through the **`$ListTitles`
half** (the `"monster"` class query), not the hand-rolled `==` half.
`$istitlealive(palace,"werewolf")` at 4009 is a second case-mismatched
call on the same `$ListTitles` path, sitting two lines below
`$ListTitles (Monsters, "Werewolf")` in the same function.

*Not confirmed, and the shipping game is unusually weak evidence here.*
In **every** case-mismatched call found, the failure mode is a **false
"clear"** — `no_monsters_titled` returns TRUE, `istitlealive` returns
FALSE — and both feed victory tests. A case-sensitive `$ListTitles` would
therefore hand out victory slightly *early* rather than break anything a
playtester would file. So "it ships and the quest is winnable" carries
almost no information about case-sensitivity. Contrast §17.5's
`$LookupFunction` finding, where the mismatched lowercase names had to
resolve or the special event would not have run at all — that inference
is sound and this one is not the same shape.

*The one decidable case, and it is an in-game test, not a source read.*
`all_enemies_dead` (1217-1221) filters with `thing's "title" != "ratman"
&& … != "skeleton" && … != "zombie" && … != "troll"` — the `==`/`!=`
operator, not `$ListTitles` — and four of those seven literals are
lowercase against capitalised shipped titles. Here the failure mode is
**inverted**: a case-sensitive comparison leaves that rabble in the
census, so `DOR_victory`'s `$all_enemies_dead` test never passes and
**`DAY_OF_RECKONING` would be unwinnable while any ratman, skeleton,
zombie or troll is alive.** That is one quest, one playthrough, and it
settles the operator half outright.

*Therefore, recorded here as a narrowing rather than by editing 22.2's
row (this guide's keep-the-original-visible convention):* 22.2's "the
`$ListTitles` half is evidently case-insensitive on the title value and
the `==` half may not be" **overstates the evidence in both directions.**
Neither half is confirmed either way, no source-side observation
distinguishes them, and the guide's other case-insensitivity findings do
not transfer — §13's `"Infinite"`/`"infinite"`, §17's
`"Override"`/`"override"`, §17.5's `$LookupFunction` and §19.5's
attribute-*name* lookup are a flag string, a flag string, a function name
and a field name respectively, none of them a title *value* comparison,
and per this guide's no-analogy rule none of them licenses a claim about
this one. **UNVERIFIED.** The safe rule for a modder is unchanged and
cheap: **match the case of the shipped `(title …)` string exactly**, in
both the `$ListTitles` form and the `==` form.

**Still UNVERIFIED after this batch** — each already flagged at its point
of use above, consolidated here:

- **Title-value case-sensitivity, in both the `$ListTitles` and `==`
  forms** (22.2, resolved as far as source allows immediately above).
  Decidable by one `DAY_OF_RECKONING` playthrough.
- **Whether GPL guarantees uninitialised locals start at zero** (22.3).
  `spawn_monsters` never initialises `i` before `while (i < num)`;
  `bbc_victory`'s `sites_gone += 1` (340) is a third shipped instance
  after §18.10's. Still a language-level question, not answerable from
  source.
- **Whether the engine really enforces a ~1 800 000 ms thread-interval
  ceiling, and what it does when exceeded** (22.4d). Two shipped sites
  name it in comments, one works around it, no interval in the file
  exceeds it — but the only evidence is the developers' own comment.
- **What installs `"SleeperScript"`** (22.6g). This quest only retimes
  and kills an existing one.
- **`$SetDrawEffects`' argument set** (22.6h) — one call site, `"gray"`
  is the only string seen, the integer's meaning is engine-side.
- **What `$EnchantWizTower` changes** (22.6j) — engine-side;
  `Magical_Repair` sitting unreferenced in this file (22.2) suggests
  self-repair is part of it, which is inference from adjacency, not
  evidence.
- **`Magical_Repair`'s actual caller** (22.2) — none in this file, and
  the "enchanted Wizard's Tower path" attribution is the plausible
  reading, not a traced one.
- **What `#ATTRIB_NotFlaggable` and `#ATTRIB_NotSpellTarget` do
  individually** (22.6i) — first citations in this guide; the
  three-write recipe and its exact reversal are confirmed, the split of
  responsibility between the three writes is read off their names.
- **That `#Allow_Cloned_Quest_Item` implies a default uniqueness
  constraint on `#QItem_*`** (22.6f) — the flag's existence and effect
  in context are confirmed; "so the default must be unique" is
  inference.

**Closing note — the `Rules/` pass (§16-§22) is now complete.** Between
them the seven batches cover **all 15 files** in
`SDK/OriginalQuests/GPL/Rules/` (5: `construction_rules.gpl`,
`victory_conditions.gpl`, `Demo.gpl`, `Quest_Actives.gpl`,
`epic_quest_scripts.gpl`) and `SDK/OriginalQuests/GPLMx/Rules/` (10: the
five `mx_` twins plus `Random_Events.gpl`, `Special_Events.gpl`,
`Quests_1/2/3.gpl`) — §16 = construction + victory conditions, §17 =
demo/random/special events, §18 = quest actives, §19-§21 = the three
expansion quest files, §22 = the base epic quest library. Nothing in
`Rules/` is left unread.

**What remains open across the whole pass, for whoever reads next.** Three
categories, and the split matters because they need different tools:

1. **Engine-side semantics that source reading cannot settle** — the
   1.8 M ms interval ceiling (22.4d), `$SetDrawEffects`' arguments
   (22.6h), `$EnchantWizTower` (22.6j), `$SetEffectorDirection`'s
   index→frame mapping (§21.4e), `$DropGoldEveryone`'s split rule
   (§21.5b), `"clear"` as a `$SpawnUnit` flag (§21.7), `-1` as an
   effector duration (§21.7), `#ATTRIB_CurrentEvent`'s mapping (§21.6e),
   what the advisor-voice toggles silence (§20.7), whether the engine
   ever writes `"type"` itself (§20.2), and `$SetPlayerTeamNumber`'s
   exact scope (§19.8, narrowed three times and still not proven).
   **These want Ghidra, not more GPL.**
2. **Questions one in-game test each would close** — title-value case
   sensitivity via `DAY_OF_RECKONING` (22.8), whether appending a 7th
   line to `Data/MusicTracks.txt` makes track 7 playable (§19.4), what
   `=` in a condition compiles to (§19.3), whether GPL discards extra
   call arguments or corrupts the frame (§21.6f), whether
   `$Make_PC_Hunter` without `$Reset_Tasks` takes effect promptly
   (§20.8), and whether uninitialised locals are reliably zero (22.3).
3. **Untraced consumers — the "writer found, reader not found" set.**
   `#ATTRIB_StartedwithThisUnit` (§20.7/22.8 — six writes in four files,
   zero reads),
   `Self_Estimation`/`Enemy_Estimation` (§19.9), `$LearnSpell`'s third
   argument (§19.9/22.8), the function that retitles a Marketplace to
   `"Closed"` (§21.3), what installs `"SleeperScript"` (22.6g), and
   `Fortress_Ixmil`'s `Warp_Out` re-arming (§21.8, recorded as an
   unresolved wiring question rather than a confirmed bug).
   **These are answerable by more source reading, but outside `Rules/`**
   — in `TaskModules/`, `DecisionTrees/` and the `_Births`/`_Deaths`
   files, which this pass only entered where a `Rules/` file led into
   them.

---

## Retracted Claims (shared with `GPL_MODDING_GUIDE.md`)

Reproduced here because both files' evidence standard refers to it.

1. **WRONG:** "Hall of Champions' bounty functions are a `RewardFlag`-
   based mechanic similar to Zoo's." **Correction:** `Hall_Champs_Check`
   (the real hero-AI trigger) does a hardcoded building-title search with
   zero reference to `RewardFlag`/`check_rewards()`. **Update (§3
   continued):** `HallOfChampions_Bounty_Cost`/`Period` themselves have
   now been read in full — they're pure cost/period data lookups
   (400/800 gold, 60000/120000ms for index 1/2) with no call sites
   anywhere in the `.gpl` tree. What exe-side code calls them, and
   whether a "bounty" mechanic manifests as anything beyond these two
   values, remains unknown — narrowed from "genuinely unknown" to
   "caller unknown," not fully resolved.
2. **WRONG (partial):** framing implied Zoo's charm mechanic was "shared
   logic" with the Cultist's spell. **Correction:** shared primitive
   (`$control_monster`), independent wrapper logic — see §9.

**Why this matters:** both mistakes came from assuming two similar-
looking systems work the same way without reading the second one's actual
source. Every claim in this guide was written only after that direct
read — extend it the same way.
