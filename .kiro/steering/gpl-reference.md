---
inclusion: manual
description: GPL scripting reference — undocumented primitives, engine gotchas, patterns, debugging
---

# GPL Scripting Reference

Complete reference for GPL (Game Programming Language) scripting in Majesty Gold HD.
Combines SDK documentation, Workshop mod analysis (10 mods), and Ghidra decompilation findings.

---

## Undocumented Engine Primitives

These functions exist in MajestyHD.exe (searchable as plaintext) but are NOT in the SDK docs.
All confirmed working via Workshop mods.

### Unit/Agent Manipulation

| Primitive | Signature | Purpose | Source |
|-----------|-----------|---------|--------|
| `$AdvanceLevel` | `(agent unit, int level)` | Instantly advance unit to specified level | WorldWarMajesty |
| `$Freeze_Unit` | `(agent target)` | Pause unit actions (crowd control) | Improved Heroes |
| `$make_Monster_Hunter` | `(agent unit)` | Convert living monster to hunt other-team monsters | Gotchas doc |
| `$SpecifyName` | `(agent, "text_id")` | Per-instance naming from Strings table | WorldWarMajesty |
| `$turnonSpeedTrail` | `(agent, int N)` | Activate speed trail visual effect | Improved Heroes |
| `$SetDrawEffects` | `(agent, "color", int)` | Tint agent (e.g. "red", 0) | Gotchas doc |

### Stat/Attribute Manipulation

| Primitive | Signature | Purpose | Source |
|-----------|-----------|---------|--------|
| `$MagicalAdjustAttribute` | `(agent, #ATTRIB, int amount)` | Stat change that auto-reverses on effector end | Improved Heroes |
| `$adjustattribute` | `(agent, #ATTRIB, int amount)` | Permanent stat change (must manually reverse) | SDK + mods |
| `$SetAttribute` | `(agent, #ATTRIB, int value)` | Set flag/value directly | SDK |
| `$GetAttribute` | `(agent, #ATTRIB) → int` | Read attribute value | SDK |
| `$Concatenate` | `(#ATTRIB, #value)` | Concatenate into spawn-time flag | WorldWarMajesty |

### Building/Kingdom Abilities

| Primitive | Signature | Purpose | Source |
|-----------|-----------|---------|--------|
| `$DoAssembly` | `(agent building)` | Triggers Call to Arms (Warriors Guild) | StandAloneAI |
| `$DoRageOfKrolm` | `(agent building)` | Triggers Rage of Krolm (temple) | StandAloneAI |
| `$SetPlayerTeamNumber` | `(agent palace, int teamNum)` | Set faction alliance team | WorldWarMajesty |
| `$NewTeamNumber` | `() → int` | Allocate new unique team number | WorldWarMajesty |
| `$AdjustPlayerData` | `(agent palace, "gold", int amount)` | Modify player gold | SDK + debugging |

### Spawning/Coordinates

| Primitive | Signature | Purpose | Source |
|-----------|-----------|---------|--------|
| `$RandomEdgeCoord` | `(int edge) → coord` | Random coordinate on map edge (0-3) | UncappedCheats |
| `$RandomCoord` | `(agent anchor, int radius) → coord` | Random position around anchor (-1 = entire map?) | UncappedCheats |
| `$SpawnUnit` | `(agent anchor, "type", coord, #player)` | Spawn unit at position | UncappedCheats |
| `$CreateAgent` | `("type", "name")` | Create named agent (EventAgent pattern) | WorldWarMajesty |
| `$RetrieveAgent` | `("name") → agent` | Get agent by unique name | WorldWarMajesty |

### Thread/Control Flow

| Primitive | Signature | Purpose | Source |
|-----------|-----------|---------|--------|
| `$NewThread` | `(function, int periodMs, "name")` | Start RECURRING thread (NOT one-shot!) | SDK |
| `$RunThreadOnce` | `(function, int delayMs, agent)` | Delayed one-shot execution | SDK |
| `$IsRunning` | `(thread) → bool` | Check if thread/callback is still running | Gotchas doc |
| `$KillThread` | `(thread)` | Kill a running thread (DANGEROUS from inside!) | Gotchas doc |
| `$SetThreadInterval` | `(attr, int ms)` | Change a thread's fire interval | Gotchas doc |

### Effects/Visuals

| Primitive | Signature | Purpose | Source |
|-----------|-----------|---------|--------|
| `$createeffector` | `(agent, "name", int duration)` | Create overlay effector (visual + timer) | SDK |
| `$createeffector` | `(agent, "name", 0, int value)` | Floating-number debug display | Gotchas doc |
| `$createeffector` | `(agent, "name", 1, "infinite")` | Persistent visual marker | Gotchas doc |
| `$CheckEffector` | `(agent, "name") → bool` | Check if effector is active | SDK |
| `$MiniMapAnimation` | `(agent, "event_beacon")` | One-shot minimap ping | Gotchas doc |
| `$Setup_Quest_Music` | `(agent root)` | Start quest soundtrack | WorldWarMajesty |

### Queries

| Primitive | Signature | Purpose | Source |
|-----------|-----------|---------|--------|
| `$ListObjects` | `(agent, "type", list) → int` | Get visible objects (fog-gated!) | SDK |
| `$ListPalaces` | `(list) → int` | Get ALL palaces (fog-independent) | Gotchas doc |
| `$IsDead` | `(agent) → bool` | Death check | SDK |
| `$IsValidGamePiece` | `(agent) → bool` | Validity check (FALSE for GplAIRoot!) | Gotchas doc |
| `$HasAttribute` | `(agent, #ATTRIB) → bool` | Check if attribute exists on agent | SDK |

---

## Critical Engine Gotchas

### Thread Behavior

1. **`$NewThread` is setInterval, not setTimeout** — fires FOREVER at the given period. There is no built-in one-shot timer.
2. **`$RunThreadOnce` chains don't work** — re-arming `$RunThreadOnce` from INSIDE the fired function is a silent no-op. Use EventAgent + `$NewThread` for repeated scheduling.
3. **Heavy functions (~300 lines, 4+ lists) silently fail as thread targets** — the engine skips them. Use a thin shim function that directly calls the heavy one.
4. **`$KillThread` from inside a `$NewThread`'d function = heap corruption crash** (~15s delay). Use `$RunThreadOnce` for true one-shots instead.

### Silent Failures

5. **Thread silently aborts on undeclared attribute access** — no error, no crash, code after the bad line never runs. Always verify attributes exist with `$HasAttribute` or declare in prototype.
6. **`$RandomNumber(N)` is frozen within a single tick** — returns the SAME value for ALL calls in one synchronous execution frame. Split across ticks if you need different values.
7. **`$ListObjects` order varies run-to-run** — bugs that "move around" mean one bad agent in a shuffled list. Never assume list ordering.
8. **From a MOD bcd, writes to palace/root via derived handles silently vanish** — only engine-given handles (thisagent, function params) work. Quest BCDs don't have this limitation.
9. **`$IsValidGamePiece(GplAIRoot)` returns FALSE** — never validity-guard the root agent.

### Crashes

10. **`foreach` exit with `return`/`break` can crash the game** — let the loop complete, latch results into a variable, check after loop ends.
11. **`$CreateSpellUnit` from a building context** — heap corruption after extended play. Buildings must NOT cast spells via GPL.
12. **Re-applying a `_Begin` buff while active** — double-freed effector corrupts memory. Always guard with `$GetAttribute(target, #ATTRIB_HasEffect*) == 1` check.
13. **`$UpgradeAgentAttributes` called directly from script** — crashes. No script path for building upgrades.

### Data/Binding Issues

14. **`base="Any"` can misbind attribute names** against wrong ruleset. Declare the real target dataset in mmxml.
15. **Quest overrides DON'T reach stored function pointers** (e.g., lair Spawn_Function). The base game's lair spawn thread keeps its original pointer. Drive lair spawning from quest code if you need to override.
16. **Expression constants resolve BY NAME at load** across all modules — last loaded wins. A mod's expression redef can silently clobber another mod's changes.
17. **`.dat` files do whole-block replacement** — defining ANY field in a .dat block replaces the ENTIRE block. Must redeclare all fields you want to keep.

### Timing/Limits

18. **An in-game day is ~72,000 ms of game time.**
19. **Gold is clamped at 2,000,000 by the script-side write path** — engine cheat bypasses this but it snaps back on next script write.
20. **Building sweeps (`$ListObjects` for buildings) are fog-of-war gated** — enemy buildings only appear after discovery. Use `$ListPalaces` for reliable kingdom-alive checks.

### Compiler

21. **`Gplbcc.exe` returns exit code 0 even on failure** — must check output file timestamp or stderr content.
22. **Stale build trap** — old .bcd loads fine but doesn't have your changes. Always verify .bcd timestamp matches your compile.

---

## MOD vs QUEST BCD Binding Differences

| Feature | MOD BCD | QUEST BCD |
|---------|---------|-----------|
| By-name function calls | Override works | Override works |
| .dat birthScript/deathScript | Override works | Override works |
| Stored function pointers (e.g., Spawn_Function) | Override works | **DOES NOT work** |
| Root agent attribute writes via derived handles | **Silently fail** | Work normally |
| Expression redefinitions | Last loaded wins | Last loaded wins |

---

## Common Patterns

### EventAgent Pattern (Recurring Events — Most Robust)

```gpl
$CreateAgent("EventAgent", "UniqueEventName");
evt = $RetrieveAgent("UniqueEventName");
evt's "EventScript" = $my_function;
$NewThread(evt's "EventScript", periodMs, "UniqueEventName");
(evt's "EventScript")("UniqueEventName");   // immediate first call
```

### Delayed One-Shot (Non-Recurring)

```gpl
$AddAttribute(root, "AttrName", "function", $my_function);
$RunThreadOnce(root's "AttrName", delayMs, root);
```

### Spell/Buff Implementation (Begin/End with Effectors)

```gpl
function MySpell_Begin(agent thisagent, agent target)
begin
    If ($IsDead(target)) return;
    If (target's "Type" == "Building") return;
    If (target's "Type" == "Lair") return;
    If ($GetAttribute(target, #ATTRIB_HasEffectMySpell) == 1) return;

    $createeffector(target, "myspell_effector", 0);      // visible effect
    $createeffector(target, "myspell_icon", duration);    // invisible timer → calls _End
    $SetAttribute(target, #ATTRIB_HasEffectMySpell, 1);  // double-apply guard

    // Apply effects:
    $MagicalAdjustAttribute(target, #ATTRIB_stat, amount);   // auto-reverses
    $adjustattribute(target, #ATTRIB_MovementRateModifier, value);  // manual reverse
    // For CC: $Freeze_Unit(target); $SpecifyIntent(target, #intent_petrified);
end

function MySpell_End(agent thisagent)   // called by icon overlay expiry
begin
    // $MagicalAdjustAttribute stats auto-reverse when effector dies
    // Manual reversal for $adjustattribute:
    $adjustattribute(thisagent, #ATTRIB_MovementRateModifier, -value);
    $SetAttribute(thisagent, #ATTRIB_HasEffectMySpell, 0);
end
```

### AI Kingdom Thread Architecture (StandAloneAI Model)

| Thread # | Purpose | Notes |
|----------|---------|-------|
| 1 | Build | Guild/temple/settlement selection based on devotion |
| 2 | Hire | Gold-gated, respects guild member limits |
| 3 | Research | Survey available research, purchase if affordable |
| 4 | Upgrade | Building upgrades when funded |
| 5 | Markets | Trading posts and marketplace |
| 6 | Self-state | Health, danger assessment, strategy adjustment |
| 7 | Defense towers | Placement logic |
| 8 | Flags | Attack/defense reward flags |
| 9 | Abilities | Wizard tower enchant, Call to Arms, Rage of Krolm |
| 10 | Overall status | Win/loss conditions |

Entry via modified palace prototype — palace `birthScript` IS the AI entry function.

### Defensive Function Entry (Always Use This)

```gpl
function Spell_Begin(agent ThisAgent, agent target)
begin
    If ($IsDead(target)) return;
    If (target's "Type" == "Building") return;
    If (target's "Type" == "Lair") return;
    If ($GetAttribute(target, #ATTRIB_HasEffectSpell) == 1) return;
    // ... rest of logic
end
```

---

## Debugging Cheat-Sheet

All techniques work in retail builds (no debug mode needed).

### Gold Channel (Code-Reached Markers)

```gpl
// Add distinctive gold amounts to confirm code paths reached:
$AdjustPlayerData(palace, "gold", 100000);   // "checkpoint 1 reached"
$AdjustPlayerData(palace, "gold", 200000);   // "checkpoint 2 reached"
// WARNING: Gold capped at 2,000,000 from script-side writes
```

### Floating-Number Display

```gpl
// Shows arbitrary integer floating over an agent:
$createeffector(building, "got_gold", 0, 500000123);
// The number 500000123 appears briefly above the building
```

### Minimap Beacon

```gpl
// One-shot ping on minimap — good for "event fired" confirmation:
$MiniMapAnimation(agent, "event_beacon");
```

### Visual Marking

```gpl
// Tint an agent red (permanent until removed):
$SetDrawEffects(agent, "red", 0);

// Persistent icon overlay (infinite duration):
$createeffector(agent, "charm_icon", 1, "infinite");
```

### Debug Master Switch Pattern

```gpl
expression #MY_MOD_DEBUG 1   // Set to 0 for release

function DebugLog(agent target, int code)
begin
    If (#MY_MOD_DEBUG == 0) return;
    $AdjustPlayerData(palace, "gold", code);
    $MiniMapAnimation(target, "event_beacon");
end
```

### Crash Dump Analysis

- Crash dumps: `majestyhd_crash_*.mdmp` in game directory
- Same EIP across crashes = deterministic bug (your code)
- Scattered EIP = heap corruption (usually $KillThread or building-cast)
- Engine primitives searchable as plaintext in MajestyHD.exe (verify existence before designing)

---

## SpellRank and AI Casting

The AI will NEVER cast a spell unless it has `<SpellRank value="N"/>` in the action XML.
Higher rank = AI prefers this spell over lower-ranked alternatives.

```xml
<Game version="1">
    <SpellRank value="6"/>      <!-- REQUIRED for AI to cast -->
    <SpellType value="Attack"/> <!-- Attack, CombatUtility, 4 (self-buff) -->
</Game>
```

### SpellType Values

| Value | Meaning | When Used |
|-------|---------|-----------|
| `Attack` | Offensive spell | Most damage spells |
| `CombatUtility` | Utility/CC | Heals, buffs, debuffs |
| `4` (numeric) | Self-buff | Stealth, personal buffs |
| Multiple tags | Stacks flags | `<SpellType value="Attack"/>` + `<SpellType value="CombatUtility"/>` |

---

## Key Constants

| Constant | Value | Meaning |
|----------|-------|---------|
| Game day | ~72,000 ms | One in-game day duration |
| Gold cap | 2,000,000 | Script-side write maximum |
| Monster cap | 85 | Default `#Monster_Spawn_Cap` (override in quest GPL) |
| Movement modifier | NEGATIVE = faster | `$adjustattribute(target, #ATTRIB_MovementRateModifier, -200)` = speed up |
