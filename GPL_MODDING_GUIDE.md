# Majesty Gold HD — Gameplay Logic (GPL) Modding Guide

A companion to `CAM_MODDING_GUIDE.md`. That guide covers binary CAM
container/section formats — this one covers actual gameplay logic: what
GPL/XML/`.dat` files do, and how building/hero/spell systems really work.

**Evidence basis:** every claim below was verified by directly reading the
cited GPL/XML/`.dat` source (base game in `SDK/OriginalQuests/GPL/`,
expansion in `GPLMx/`, both under the `Majesty_Files` repo unless noted).
Items that could not be confirmed from available source are explicitly
marked **UNVERIFIED**/**UNKNOWN** rather than guessed at — several early
claims in this research had to be retracted after a closer read (see
"Retracted Claims" at the end), so treat file/function/line citations as
load-bearing, not decorative.

---

## Contents

1. The Core State Machine: ActiveScript, BackScript, TaskName
2. Building Lifecycle: Birth, Construction, and Upgrades
3. Building Visit Systems: Shopping, Purchasing, Services
4. Guild Life: The Lived_In_Script Mechanic
5. Building Economy: Revenue, Taxation, Palace Income
6. Guard Spawning and Defense
7. The Intent System (`#intent_*`)
8. Hero Death, Gravestones, and Revival
9. Orphaned Content: The "Zoo" Building
10. Hero AI Dispatch Is a Closed Set — Not Generically Extensible
11. Petrification System Re-Verification (Template for New Status Effects)
12. Building-Unlocked Guild Skills
13. The Effector System, and Other Shared Primitives
14. Cross-System Primitive Sweep
15. Hero Class Decision Trees — Comparative Pass

Quest scripting (`GPL/Rules/`, former §16-§22) lives in
`GPL_QUEST_RULES_REFERENCE.md` — see the pointer at the end of this file.
Also here: **Retracted Claims** (end of file) — corrected earlier findings,
kept visible on purpose.

---

## 1. The Core State Machine: ActiveScript, BackScript, TaskName

Nearly every hero/monster/building behavior in this codebase routes
through three GPL-side struct fields. Understanding this first makes every
other section easier to read.

**Declaration:** `ActiveScript`, `BackScript`, `TaskName` are ordinary
GPL-declared fields per-prototype (`SDK/OriginalQuests/GPL/prototype.gpl`,
mirrored in `GPLMx/mx_prototype.gpl`) — not engine-builtin names. Not every
prototype has all three: `prototype hero()` has all three (lines 103-126);
`prototype building()` has only `ActiveScript` (line 263, no
`BackScript`); `prototype GuardHouse()` has no `ActiveScript` of its own —
it uses `Guard_Function` as its "ActiveScript equivalent" (line 557,
comment confirms this framing) instead. `prototype Palace()`/`RewardFlag()`
also lack `BackScript`. Fields are declared independently per prototype,
not inherited from one shared base — confirmed by reading each block
directly rather than assuming symmetry.

**Mechanism:** `ActiveScript` holds a GPL function reference the engine
calls repeatedly on a timer. `$NewThread(agent's "activescript", interval,
agent)` registers the function to fire every `interval` ms
(`#Normal_Cycle` = 300ms is the standard hero tick, `globals.gpl`/
`mx_Globals.gpl` line ~123-125; other named intervals include
`#Henchmen_Cycle` 500, `#Flag_Cycle` 500, `#Lair_cycle` 1200). Simply
reassigning `agent's "activescript" = $SomeFunc` does **not** trigger a
call — it only swaps which function the already-running timer invokes
next tick. `$SetThreadInterval(agent's "activescript", newInterval)`
changes the tick rate without restarting the timer (used constantly in
`Shop_Visited.gpl` to slow down mid-purchase, then reset to
`#Normal_Cycle` when done). `LowLevel.gpl`'s `reset_tasks` (lines
1011-1019) is the canonical "abort current task" call: nulls `target`,
resets both `activescript` and `backscript` to `basicscript` — the true
idle/fallback state.

**BackScript** is a return-address consumed specifically by the travel/
movement family. `Travel_to.gpl`'s `has_arrived` (called every tick by
any `travel_to`-family ActiveScript) does `activescript = backscript` at
every arrival branch — this is the actual mechanism behind the ubiquitous
pattern `activeScript = $travel_to; backScript = $use_building;` ("go
there, then do this"). `BackScript` is also *read* elsewhere:
`Travel_to.gpl`'s `gettargetrange` branches on `backscript ==
$use_building`/`$go_steal` to pick arrival distance, and some
list-search helpers treat "is agent doing X" as true if X matches either
`ActiveScript` or `BackScript`.

**TaskName** is a plain string scratch field, not a single global-purpose
key. Two independent consumer patterns exist: (1) same-agent dispatch key
set before travel, read on arrival — e.g. `go_home.gpl` sets `taskname =
"go_home"`, and the shared `use_building.gpl` explicitly checks for that
exact string to route to `Lived_in_Script` instead of `visited_script`
(see §4); (2) an unrelated building-side mode flag — `Building_Guard.gpl`
sets `TaskName = "Wander"`/`"Switch_guards"` on the *Guardhouse itself*
(not a hero) to track its own scan state (see §7). It's treated as a
one-shot signal, explicitly cleared (`TaskName = ""`) once consumed in
multiple files. No confirmed case of one agent reading another agent's
`TaskName` was found.

**UNVERIFIED:** the exact engine-side semantics of `$NewThread`/
`$RunThread`/`$ResumeThread`/`$KillThread` (real per-agent coroutine vs.
callback timer table) — GPL source only shows call sites, not the
scheduler internals. Would need Ghidra.

---

## 2. Building Lifecycle: Birth, Construction, and Upgrades

### birthscript vs birthScript2

Both are GPL-declared fields on the "building" family of prototypes only
(`building`, `Library`, `Fairgrounds`, `Guild`, `Dwarven_Settlement`,
`GuardHouse`, `Tower` — NOT Palace, Lair, tax_collector, Caravan, which
have only `birthScript`). The mx-only `Outpost` prototype is the one
exception among Palace-family buildings, adding a `BirthScript2` Palace
itself lacks.

**Only `birthscript` is engine-invoked.** `LowLevel.gpl`'s `NewUnitInit`
(the function whose own comment says "called by the in-game code when a
unit's HP are set to 0 or less" — wait, actually its comment is
"Initialize a newly spawned unit") does `$RunThread(newAgent's
"birthScript", 1, newAgent)`. `birthScript2` is **never** called by the
engine directly — it's only invoked from three ordinary GPL functions in
`Building_Births.gpl`: `basic_birth`, `magical_birth`, and
`BuildingReachedMaxHP`. This means the two fields are **not** parallel
"generic setup vs. building-specific setup" callbacks run independently —
it's a single sequential chain: `birthscript` fires at creation → building
may queue on `buildings_waiting` if under construction → only once
construction completes does `birthscript2` fire.

- `basic_birth`: if HP already == MaxHP (placed pre-built), calls
  `birthscript2` immediately; otherwise queues on `palace's
  "buildings_waiting"` and waits for hero/peasant labor.
- `magical_birth`: adds a fixed HP amount per tick and re-queues *itself*
  via `$runthread(birthscript, #magical_build_delay, ...)` — no hero/labor
  involved at all — until HP reaches max, then calls `birthscript2`.
- `BuildingReachedMaxHP`: the general "HP just reached max" handler,
  called from hero/peasant build-action code (not birth-time). Only calls
  `birthscript2` if `#ATTRIB_FirstStageBuilt` isn't already 1 (i.e. only
  on the building's very first completion, never on upgrade).

**Common case confirmed literally:** most buildings set `birthscript =
basic_birth` / `birthScript2 = Building_Birth` (the generic completion
function — starts `RevenueScript` if present, calls `$count_building`).
**Level-2/3 building entries systematically skip both fields**, setting a
single bare `birthScript` pointing straight at the completion function —
because upgraded-in-place buildings never start at 0 HP, so there's no
"under construction from scratch" case to route through `basic_birth`.

**Building-specific `birthScript2` targets vary in shape, not just
content** (confirmed reading 3 in full): `Trading_Post_Birth`/
`Fairgrounds_Birth` both start a dedicated `ActiveScript` thread (on
`#Henchmen_Cycle`/`#Fairgrounds_Cycle` respectively) then delegate to
`Building_Birth`; `gambling_hall_Birth` instead calls `$auto_birth` (a
simpler generic function, no RevenueScript step) then resets a
palace-level spawn-gating flag — a genuinely different job shape than the
other two.

**UNVERIFIED:** whether the exe ever calls a `birthscript2`-named
attribute directly; why `.dat` authors chose to skip `basic_birth` for
level-2/3 buildings (inferred from code structure, not a comment).

### upgradescript: basic_upgrade vs magical_upgrade

Same pattern, but here the "genuinely different mechanic" guess is
**confirmed correct**. `upgradescript` fires via `building_upgraded`
(`Building_Births.gpl`, one-line body, comment: "called by the in-game
code when a building is upgraded" — same engine-entry-point comment style
as `NewUnitInit`, though **no independent GPL-side call site for
`$building_upgraded` was found** — only this workspace's own `MyAI`
cheat/upgrade logic calls it directly, bypassing any real purchase-click
flow; the true engine trigger is UNVERIFIED).

- **`basic_upgrade`**: queues the building onto the SAME `buildings_
  waiting` list fresh construction uses — an upgrading building is worked
  on by hero/peasant labor exactly like new construction, completing via
  `BuildingReachedMaxHP`.
- **`magical_upgrade`**: a pure self-re-queuing 450ms timer
  (`#magical_build_delay`) adding a fixed HP amount per tick, zero labor
  involvement, and it **never calls `BuildingReachedMaxHP` at all** —
  it inlines its own completion (`$UpgradeAgentAttributes`, advisor
  sound/chat). `Magical_build_rate` (expansion-only field, absent from
  base `prototype.gpl`) is a per-instance tunable read directly inside
  `magical_upgrade`, controlling the tick amount — and it's consumed by
  **both** `magical_birth` (construction speed) and `magical_upgrade`
  (upgrade speed) wherever declared, not two separate fields.

**`Magical_build_rate` users are NOT limited to Sorcerer's Abode** — base
game has no Sorcerer's Abode entry at all; base-game `magical_upgrade`
users are `Wizards_Guild1`/`2` (using the hardcoded global constant, no
per-instance field exists in base `prototype.gpl`). Expansion adds
`SorcerersAbode`/`SorcerersAbode2` and gives `Wizards_Guild1`/`2` their own
`Magical_build_rate` values. `Wizards_Tower` uses `Magical_build_rate` for
birth only (no upgrade path — Towers have no level 2/3 at all).

**Palace is the one exception with a second upgrade field**
(`upgradescript2`, Palace/Outpost only). `palace_upgrade` calls
`$basic_upgrade` directly (reusing the generic labor mechanic) and also
starts `upgradescript2` (`palace_upgrade2`) on a 15-second poll —
`palace_upgrade2` waits for construction to finish, then restarts the
Palace's Guard/Tax/Peasant spawner threads to enforce new henchman limits.

### The construction labor system: exactly what makes a building buildable

**Added when the question "how do peasants decide what to build?" was
raised, after a report that workers sometimes never upgrade a
script-upgraded building and never touch a cheat-placed tier-2 one.**
Both behaviors are fully explained by plain GPL — no engine mystery.

**The queues.** The palace prototype holds two lists,
`buildings_waiting` and `buildings_under_construction`, plus an
`integer busy_peasants`. Producers: `basic_upgrade` and `basic_birth`
push onto `buildings_waiting` (`Building_Births.gpl`);
`make_attack.gpl` pushes onto `buildings_under_construction` when a
building is attacked mid-build. Consumers: **peasants**
(`TaskModules/Characters/Henchmen/peasant.gpl`) and **heroes**
(`TaskModules/Characters/hero_build.gpl` — heroes really do build, using
the same lists).

**`peasant_basic` selection order:** take the first member of
`buildings_waiting` if any; else go help on the first member of
`buildings_under_construction`; else go home and `$hide` in the nearest
city building. Selection is `$listmember(..., 1)` — **plain FIFO, no
distance or priority scoring** — though `peasant_go_build` does consult
`$Closest_Peasant_Building()` before switching to a new target, so
proximity enters as a tie-break, not as the selection rule.

**The two gate functions, both plain GPL in `peasant.gpl`:**

```gpl
function building_level_complete(agent thisagent) is boolean
begin
    if (($getattribute(thisagent,#ATTRIB_FirstStageBuilt) == 1) &&
        ($getattribute(thisagent,#ATTRIB_CurrentStageBuilt) == 1))
        return TRUE;
    else return FALSE;
end

function offrepair(agent thisagent) is boolean
begin
    if ($building_level_complete(thisagent))
        if (($getattribute(thisagent,#ATTRIB_isrepaired) == 0) &&
            ($getattribute(thisagent,#ATTRIB_QuickRepair) == 0))
            return TRUE;
    return FALSE;
end
```

**So the complete contract — a worker will build a building if and only
if all three hold:**

1. It is on `buildings_waiting` or `buildings_under_construction`.
2. **`HP < MaxHP`.** `peasant_go_build` abandons immediately on
   `HP == MaxHP` (resets tasks, decrements `busy_peasants`, drops it from
   the list).
3. **`offrepair()` is false** — i.e. either the building is *not*
   level-complete (`FirstStageBuilt` and `CurrentStageBuilt` not both 1),
   **or** it is explicitly flagged for repair (`#ATTRIB_isrepaired == 1`
   or `#ATTRIB_QuickRepair == 1`).

`reconstruct_lists(palace)`, called at the top of every `peasant_basic`
tick, prunes `buildings_under_construction` using the same condition —
so a job that stops satisfying (3) is **abandoned mid-build**, not just
skipped at selection. It also *adds* damaged completed buildings back
when they are flagged for repair, which is how the repair queue buttons
work.

**The build step itself** is `$performaction(thisagent,"basic_build",
building)` followed by `HP += #basic_build_amount` (or
`#Deathmatch_repair_amount` when Deathmatch rules are on *and* the
building is already level-complete), clamped to `MaxHP`; on reaching
`MaxHP` it calls `$BuildingReachedMaxHP(building)`. **Construction is
purely HP accretion** — there is no separate progress counter.

#### Consequences that explain real observed behavior

**A cheat-placed building sits unbuilt forever because of gate (1) alone —
queue membership — and the recovery path deliberately cannot rescue it.**
Reported case: a cheat-placed level-2 Magic Bazaar, **placed at 1 HP**, is
never worked on. Note 1 HP means `HP < MaxHP`, so **gate (2) is satisfied**
— it is not an "already finished, nothing to do" situation. The reason is:

- **Nothing ever put it on a queue.** Only `basic_birth`/`basic_upgrade`
  push onto `buildings_waiting`, and those run as a building's
  `birthScript`/`upgradescript`. A cheat or bare `$SpawnUnit` that
  bypasses the birth script never enqueues the building.
- **`reconstruct_lists` cannot add it back, by design.** Its add-back loop
  is scoped to *repairs of finished buildings* and filters incomplete ones
  out twice: it calls `buildings = $listcompleted(buildings)` before the
  loop, then requires `$building_level_complete(bldg)` inside it, then
  requires `#ATTRIB_isrepaired == 1` or `#ATTRIB_QuickRepair == 1`. A
  1-HP never-built building fails the first two conditions.

**So an incomplete building that is not on `buildings_waiting` is orphaned
permanently — invisible to the entire labor system.** There is no sweeper
that notices "this building is unfinished and nobody is coming."

This also explains why `$SpawnUnit` accepts a `"MaxHP"` string flag
(§3's spawn discussion, and `Housing_Boom`/`Hero_Births.gpl` use it):
spawning a building **pre-completed** is the way to sidestep the orphan
state entirely, because a completed building needs no labor.

**Fix for anyone hitting this:** after spawning, push the building onto
the palace's queue yourself — `$getpalace(bldg)`'s `"buildings_waiting"
<< bldg`, which is precisely what `basic_upgrade`'s one meaningful line
does — or give the building a real `birthScript` so the engine enqueues it
through `NewUnitInit`. **UNTESTED**, but it follows directly from the
producer/consumer relationship above.

**A scripted upgrade must satisfy all THREE gates — queueing alone is not
enough, and neither is state alone.** In practice that means:
- **(1)** get it onto `buildings_waiting`, which in GPL means running the
  building's `upgradescript` (`$building_upgraded(bldg)` does this) or
  pushing onto the palace list directly.
- **(3)** `$setattribute(building, #ATTRIB_CurrentStageBuilt, 0)` → makes
  `building_level_complete` false, so `offrepair` is false.
- **(2)** ensure `HP < MaxHP` — raising `MaxHP` (e.g.
  `$adjustattribute(building, #ATTRIB_MaxHP, 50)`) achieves this without
  visibly damaging the building.

**Failure presentation differs by which gate is missed, which is useful
for diagnosis:** miss (1) and no worker ever *starts* — the building sits
untouched with nobody walking toward it. Miss (2) or (3) and a worker
walks over, then abandons on the same tick, and `reconstruct_lists` prunes
the job. Both present loosely as "workers just won't upgrade it," so the
distinguishing observation is **whether anyone ever approaches the
building.**

The `Dwarfeh_AI` mod satisfies all three around its `$ChangeUnitType`
call — `$setAttribute(..., #ATTRIB_currentstagebuilt, 0)`,
`$adjustAttribute(..., #ATTRIB_MaxHP, 50)`, then
`$building_upgraded(building)` — which is why its upgrades complete.
**UNVERIFIED** which gate its earlier, abandoned attempt was missing; the
author recalls only that workers never upgraded the building.

> **CORRECTION to this guide's own earlier recommendation, kept visible.**
> The `$UpgradeAgentAttributes` subsection below suggests replacing
> `$ChangeUnitType` with a bare `$basic_upgrade(building)` call.
> **`$basic_upgrade` alone is NOT sufficient** — it only performs step (1),
> the queue push. Without also clearing `#ATTRIB_CurrentStageBuilt` and
> ensuring `HP < MaxHP`, the queued building fails gates (2)/(3) and is
> abandoned instantly. The `Dwarfeh_AI` mod already does both of those
> things around its `$ChangeUnitType` call, which is why its upgrades
> complete at all.

#### Does the sprite change without `$ChangeUnitType`? Yes — by elimination

**A fair objection to the advice above:** building tiers are genuinely
distinct unit types. `ABH1`/`ABH2`/`ABH3` are three separate XML
`<Description>` entries with **their own `ImageIDBase`** (so, their own
sprites) and three separate `.dat` entries with their own script bindings.
If a scripted upgrade skips `$ChangeUnitType`, what makes the building
*become* tier 2 — art and scripts included?

**Answer: `$UpgradeAgentAttributes` must perform the whole type
transition, because nothing else in the human path could.** The argument
is by elimination and it is tight:

1. `BuildingReachedMaxHP`'s upgrade branch calls **only**
   `$UpgradeAgentAttributes(theBuilding)`, plus advisor sound, chat
   message, and the Palace/Guardhouse special cases. `magical_upgrade`'s
   completion branch likewise calls only `$UpgradeAgentAttributes`.
2. **Shipped GPL never calls `$ChangeUnitType` on a building at all.** All
   five call sites across both repos are character transformations:
   `Gnome` → `GnomeChamp` (`mx_give_exp.gpl`, under the comment "change
   gnome art here!"), hero → `Dryad`/`Medusa`/`Minotaur`
   (`mx_Spells.gpl`), and hero → `Red_Bear` for Change Shape
   (`Spells.gpl` / `mx_Spells.gpl`).
3. Human upgrades demonstrably do change both sprite and tier-gated
   abilities.

Given (1) and (2), the transition in (3) **is performed exe-side, not by
GPL** — that much is solid. `$ChangeUnitType` is not how buildings change
tier; it is the "become a different unit type entirely" tool for
shape-shifting characters, and no shipped code points it at a building.

> **Do NOT over-read this into "`$UpgradeAgentAttributes` does the whole
> transition."** An earlier draft of this subsection concluded exactly
> that, and it does not follow. The elimination argument only bounds the
> **GPL** call graph; the exe is not confined to it. At least two readings
> remain open:
> - `$UpgradeAgentAttributes` resolves `UpgradeTo` and applies the new
>   tier definition wholesale, sprite included; or
> - `$UpgradeAgentAttributes` genuinely only touches attributes, and the
>   engine performs the type/sprite swap in its own upgrade handling,
>   before or after it calls `BuildingReachedMaxHP` — in which case a
>   purely GPL-driven upgrade might update stats but leave the old sprite.
>
> Nothing in readable source distinguishes these. Filed as a Ghidra task.

**Supporting detail that fits this reading:** the `Dwarfeh_AI` author's
note that the game "will crash after a few seconds" if
`$UpgradeAgentAttributes` is not run after `$ChangeUnitType` is exactly
what you'd expect if `$UpgradeAgentAttributes` is the routine that
reconciles an agent with its type definition — `$ChangeUnitType` swaps the
type and leaves the agent unreconciled until it runs.

**Honest bound:** what is established is that **the tier/sprite transition
is exe-side and is not driven by any GPL call**. Which exe routine does it
— and specifically whether `$UpgradeAgentAttributes` is that routine or
merely an attribute refresh alongside it — is **UNVERIFIED**, and cannot
be settled by reading GPL at all.

❓ **The experiment worth running, now precisely scoped:** set
`#ATTRIB_CurrentStageBuilt = 0`, bump `MaxHP`, queue the building, and
call **no** `$ChangeUnitType`. If the tier, sprite and abilities all
advance when `BuildingReachedMaxHP` fires, that is the clean
human-equivalent upgrade and it removes the crash-versus-early-unlock bind
entirely. If the sprite does *not* change, this deduction is wrong and
`$ChangeUnitType` is required after all — in which case the correct
sequencing is to defer it until construction completes.

### `$UpgradeAgentAttributes` is the moment an upgrade takes effect — and the reason scripted upgrades misbehave

**Added after the above, prompted by a question about where
`upgradescript` targets are defined. This subsection is about the step
those scripts lead to.**

**`$UpgradeAgentAttributes(agent)` is an engine primitive** — no GPL
function definition anywhere in either repo. It has exactly **two shipped
call sites, both in `Building_Births.gpl`**:

1. Inside **`BuildingReachedMaxHP`**, in the `else if
   ($getattribute(theBuilding,#ATTRIB_currentstagebuilt) != 1)` branch —
   i.e. *the building was already built once and is now finishing an
   upgrade.* This is followed by the advisor "Building_Upgraded" sound,
   `#chat_building_upgraded`, a Palace special case
   (`#ATTRIB_Upgrade_herosNeeded`), and a Guardhouse special case
   (`$RestartGuardSpawnThread`, because `Max_Guards` may have changed).
2. Inside **`magical_upgrade`**'s completion branch, which inlines its own
   finish instead of routing through `BuildingReachedMaxHP`.

**So the full human upgrade path is:** player clicks upgrade → engine
calls `building_upgraded` → `$runthread(upgradescript)` →
`basic_upgrade` pushes the building onto `palace's "buildings_waiting"` →
a peasant/gnome/dwarf works it and raises HP → HP reaches max →
`BuildingReachedMaxHP` → **`$UpgradeAgentAttributes` applies the new
tier's attributes.** `BuildingReachedMaxHP` then unconditionally sets HP
to max and both `#ATTRIB_currentstagebuilt` and
`#ATTRIB_FirstStageBuilt` to 1.

**`$UpgradeAgentAttributes` evidently resolves the target tier itself.**
No shipped call site passes it a tier or type argument, and no shipped
code calls `$ChangeUnitType` as part of an upgrade — so the engine must
derive the next tier on its own (the XML `UpgradeTo` field is the obvious
candidate). **UNVERIFIED** that `UpgradeTo` is specifically what it
reads; only that the primitive needs no help from GPL to find the target.

#### Why this matters: two real failure modes when scripting an upgrade

Both are confirmed from the `Dwarfeh_AI` mod
(`PanelTest_Quest/MyAI/GPL/custom_rules.gpl`), whose author hit them
building an AI opponent and left comments recording the symptoms.
**Evidence class: another modder's field experience plus his in-code
notes, not an engine trace.**

1. **Calling `$UpgradeAgentAttributes` early unlocks tier content
   early.** That mod upgrades with `$ChangeUnitType(building,
   "Blacksmith2")` + `$UpgradeAgentAttributes(building)` immediately,
   rather than waiting for labor. Result: **tier-2 abilities become
   available before the building is physically upgraded** — the author's
   confirmed example is Rogues' Guild level-2 poison being available to
   heroes early. He fixed it for that one building by commenting the call
   out, with the note "*This lets heroes poison before the building
   completes so disabled it to be more human like*." The other upgrade
   branches still call it, so the behavior persists elsewhere in that
   mod. **Corollary worth stating explicitly: resetting
   `#ATTRIB_currentstagebuilt` to 0 does NOT re-gate tier content** — the
   mod does that on every branch and it does not help. That attribute
   tracks construction state; it is not the content gate.
2. **`$ChangeUnitType` leaves the agent inconsistent, and
   `$UpgradeAgentAttributes` is what repairs it.** The same mod's comment
   on its Palace upgrade path: "*No idea why it's needed but game will
   crash after a few seconds if it isn't ran after changing unit type.*"
   So the two calls are load-bearing as a pair. **This puts anyone using
   `$ChangeUnitType` for upgrades in a bind — omit the follow-up and the
   game crashes within seconds, include it and tier content unlocks
   early.** ❓ What state `$ChangeUnitType` leaves stale is unknown.

#### The recommended shape for a scripted upgrade

**Don't use `$ChangeUnitType` for tier upgrades.** No shipped code does.
Instead reuse the labor path the engine already drives — call
`$basic_upgrade(building)` (or replicate its one meaningful line, pushing
the building onto `$getpalace(building)`'s `"buildings_waiting"` list),
and let workers and `BuildingReachedMaxHP` complete it on the engine's
own schedule. That gets correct timing, the advisor sound, the chat
message, the Guardhouse guard-thread restart, and the flag bookkeeping
for free, because it is the same code the player's click runs.

**UNTESTED** — this follows from the shipped call graph rather than from
a working implementation; the mod that hit the problem never tried this
route. Recorded as the indicated fix, not as a verified recipe.

**Confirmed inconsistency, unexplained:** Zoo (all 3 levels), MagicBazaar
(all 3 levels), HallOfChampions, and Mausoleum all keep `upgradescript
basic_upgrade` set despite apparently having no reachable upgrade path
(Zoo3/MagicBazaar3 are max-level; HallOfChampions/Mausoleum are
single-instance). **UNVERIFIED** why — no comment explains it, not
investigated further.

---

## 3. Building Visit Systems: Shopping, Purchasing, Services

**There is no single shared "purchase completed" function.** Each building
family has its own dedicated `Visited_Script`, confirmed by reading
`Building_Data.dat`/`mx_Building_Data.dat` in full — not assumed
symmetric:

| Visited_Script | Buildings |
|---|---|
| `Shop_Visited` | Marketplace (all levels), Trading_Post |
| `Bazaar_Visited` | Magic_Bazaar (all levels) — separate file, own item set |
| `Upgrade_Equipment` | Blacksmith (all levels), Zoo (real building, see §9) |
| `Enchant_Equipment` | Wizard's Guild (all levels) |
| `Library_Visited` | Library (all levels) |
| `GuardHouse_Visited` | Guardhouse (both levels) |
| `Inn_visited` | Inn |
| `Fairgrounds_Visited` | Fairgrounds |
| `Hall_Of_Champions_visited` | Hall of Champions |
| `Poison_Weapons`/`Gambling_Hall`/`Brothel`/`Gardens_visited` | their namesake buildings only |

`Shop_Visited.gpl` (byte-identical to `mx_Shop_Visited.gpl`) dispatches on
`ThisAgent's "Taskname"` across exactly 3 cases (Entertain_Shop,
Ring_Protection, Market3_Item, default Heal_Potions). `Bazaar_Visited`
(`Magic_Bazaar.gpl`'s `Purchasing_at_Bazaar`) dispatches across 6 cases
(Bazaar_Item_One–Six) — a completely separate function, not an extension
of `Shop_Visited`'s dispatch, despite doing the same job for a different
building. Both follow the same internal shape (dispatch on `TaskName` →
per-item purchase function → `$Spend_Gold` + `$CreateNewInventoryItem` +
a "done purchasing" cleanup that clears `TaskName` and calls
`$Reset_Tasks`), but there's no inheritance — it's copy-pasted-and-
extended per building family.

**Practical implication for "add research/purchase to building X":** find
X's `Visited_Script` in the table above, then extend *that specific
function*. Extending `Shop_Visited` only affects Marketplace/Trading_Post;
extending `Bazaar_Visited` only affects Magic Bazaar. There's no single
choke point.

**Two `.dat`-declared `Visited_Script` values are misleading:**

- **Mausoleum's `Visited_Script: Upgrade_Equipment` does not drive
  revival.** `Mausoleum.gpl` defines dedicated `Mausoleum_Resurrect_Cost`
  ("Called by the interface to fill in the resurrection cost field") and
  `Mausoleum_Resurrect_Begin` — entirely separate, no call relationship to
  `Upgrade_Equipment`. Revival is interface/occupant-driven, not
  arrival-driven (dead heroes are already stored as occupants, they don't
  "visit"). **UNVERIFIED** whether `Upgrade_Equipment` is genuinely dead
  for Mausoleum or fires under some other circumstance.
- **"Zoo" is real but orphaned content** — see §9.

### The two purchase systems, and how they connect

Don't conflate **player UI clicks** (research/purchase buttons in open
panels — dispatch mechanism is exe-hardcoded by `control_id`, currently
**UNCONFIRMED** pending Ghidra, see `TODO-Ghidra.md` Priority 3.4; cost/
time values themselves are GPL expression references like
`#ResearchCostX`) with **hero AI autonomous purchases** (heroes wandering
into shops — pure GPL, decision tree calls a purchase-check function like
`Purchase_Bazaar`, sets `ActiveScript = $Use_Building` + an Intent, and
the building's `Visited_Script` executes the purchase on arrival).

**The link:** hero AI purchase checks gate on the SAME building attribute
the player's UI click sets. `Purchase_Bazaar`'s `Researched_Item()`
checks `#ATTRIB_ResearchBazaar_Item_One` before a hero will even consider
buying that item — the player must UI-click to "research" (unlock) an
item before hero AI will ever autonomously buy it. **UNVERIFIED** whether
every other researchable item follows this same gate-then-purchase
pattern, or some unlocks are purely cosmetic with no AI consumer — only
confirmed for Magic Bazaar.

To make an AI-controlled player (no mouse) perform UI-research-click
equivalents, see the polling pattern in `PanelTest_Quest/MyAI/GPL/
custom_rules.gpl`'s `basicAI()` — custom mod logic, not base game, that
directly polls building attributes/gold and sets them the way the exe's
click handler would, on a timer instead of a click event.

### §3 continued: the remaining `Visited_Script` functions, individually traced

The table above only named these functions. Each is read from its own
`.gpl` source below (all in `GPLMx/TaskModules/Buildings/`, base-game
`GPL/TaskModules/Buildings/` is byte-identical for every one of them
except `Guardhouse_Visited`, which only exists in expansion's
`mx_Building_Guard.gpl`/base's `Building_Guard.gpl` — not checked further
since it's the same file either way).

**`Upgrade_Equipment` (Blacksmith)** — `mx_Upgrade_Equipment.gpl`. Only 1
dispatch case, not a `TaskName` switch at all: `Obtain_Upgrade` branches
on whether `ThisAgent's "Task_Number"` equals `#ATTRIB_Armor_Struct_Bonus`
(armor path) or anything else (weapon path, "check weapon upgrading" per
the source comment). Each path is a 3-tier ladder — tier 1/2/3 upgrade,
each gated by both `Total_Gold` affordability AND a building research
flag (`#ATTRIB_ResearchArmorLevel_2/3/4` or `#ATTRIB_ResearchWeaponLevel_
2/3/4`), armor costs multiplied by `#armor_multiplier`. It buys the
*highest* tier it can afford in one visit (each tier check falls through
to the next, overwriting `Gold`/`Upgrade` rather than accumulating).
Cleanup (`Done_Enhancing_Equipment`) does NOT match `Shop_Visited`'s
shape: no `$CreateNewInventoryItem` call at all — `$SetAttribute` writes
the upgrade tier directly onto the hero's own struct-bonus attribute (a
structural/durability boost applied to gear that already exists, not a
new inventory item spawned). It also runs unrelated side effects
`Shop_Visited` never touches: a cosmetic `got_armor`/`got_weapon`
effector, and a `palace's "blacksmith_trips"` counter that spawns a
`minotaur` monster once it hits `#minotaur_blacksmith_limit` — a
Blacksmith/Wizard's-Guild-shared escalation mechanic (see below) with no
equivalent in any other building traced so far. Ends with
`Task_Number = 0` + `$Reset_Tasks`, the same TaskName/Reset_Tasks half of
`Shop_Visited`'s cleanup, just without the `$Spend_Gold`+
`$CreateNewInventoryItem` half.

**`Enchant_Equipment` (Wizard's Guild)** — `mx_Enchant_Equipment.gpl`.
Structurally identical to `Upgrade_Equipment`'s pattern but simpler: one
function (`Obtain_Enchantment`), a 3-tier ladder gated by `Total_Gold` and
`ThisBuilding's "Level"` (tier 2 needs `Level > 1`, tier 3 needs
`Level > 2` — no separate research-flag gate, unlike the Blacksmith).
Reuses the *same* `Done_Enhancing_Equipment` cleanup function as
`Upgrade_Equipment` (confirmed by identical function name/call in both
files) — so despite being a different building family, this one case
genuinely IS shared code, not copy-paste-and-diverge. That sharing has a
real consequence: `Done_Enhancing_Equipment`'s `blacksmith_trips`
increment and minotaur-spawn check are unconditional (only the
`got_armor`-vs-`got_weapon` cosmetic effector choice is gated on
`task_number`), so a Wizard's Guild enchantment visit increments the same
`palace's "blacksmith_trips"` counter a Blacksmith visit does and can
trigger the same minotaur spawn — confirmed by reading the shared
function, not assumed from the building's name.

**`Library_Visited` (Library)** — `mx_Library.gpl`. Structurally the
closest to `Shop_Visited`'s shape of anything traced so far: a real
`TaskName` dispatch with 5 cases (`Wizard_Spell`, `Wizard_Train_Intel`,
`Train_Magic_Resist`, `Learn_Generic_Spell`, `Study`), all inside one
`Study_at_Library` function rather than split into per-item sub-
functions. Every visit also gives XP first (`#Wiz_Learn_at_Library_Exp`
if the hero's title is "Wizard", `#Gen_Hero_Learn_at_Library_Exp`
otherwise), regardless of which case fires — a step none of the other
traced buildings have. `Wizard_Spell` and `Learn_Generic_Spell` each
delegate to a `Does_Library_Have_New_*_Spell` gate function (in
`Check_Library.gpl`) that checks the hero's level/already-knows-it state
AND a building research flag (`#ATTRIB_ResearchWizardFireBlast`,
`#ATTRIB_ResearchWizardMeteorStorm`, `#ATTRIB_ResearchEnergyBlast`,
`#ATTRIB_ResearchFireShield`) before returning a spell name to learn —
the same gate-then-consume shape already confirmed for Magic Bazaar,
independently confirmed here rather than assumed. `$LearnSpell` replaces
`$CreateNewInventoryItem` as the "purchase" — spells aren't inventory
items. `Wizard_Train_Intel`/`Train_Magic_Resist` spend flat prices
(`#Library_Train_Wiz_Intel_Price`/`#Library_Train_MResist_Price`) for a
permanent `$AdjustAttribute` stat boost, no research gate on those two.
Cleanup differs from `Shop_Visited`: no `$Reset_Tasks` call at all —
just `TaskName = ""` then `$Exit_Building`, done inline at the end of
`Study_at_Library` rather than in a separate cleanup function.

**`GuardHouse_Visited` (Guardhouse)** — `mx_Building_Guard.gpl`. Not a
shopping/purchase system at all — confirmed structurally different, not
assumed from the name. `Guardhouse_Visited` itself just calls
`$Enter_Building`, awards flat `#garrison_exp`, and hands off to
`Garrison_Scan_Or_Leave`, which runs repeatedly (it's the `ActiveScript`,
not a one-shot) scanning for nearby enemies via `$list_enemies_seen`. If
enemies are found the hero exits and switches to `$Attack_Object`
targeting the closest one; otherwise there's a flat
`#Stop_Garrisoning_Chance` roll each cycle to just leave. No `TaskName`
dispatch, no gold spent, no `$CreateNewInventoryItem`, no `$Reset_Tasks`
in the exit path shown — exit is a bare `$Exit_Building` inside the scan
function itself. This is a loitering/ambush behavior, not a purchase.

**`Inn_visited` (Inn)** — `mx_Inn_Visited.gpl`. No `TaskName` dispatch on
entry either — branches on the hero's *current* `#ATTRIB_AIIntentionString`
intent instead, to decide what display-intent to set while resting
(`#intent_going_to_bard` → performing a minstrel show;
`#intent_flee_scared`/`#intent_flee_lowHP` → seeking-refuge/recuperating
variants keyed on whether `Target's "Subtype"` is `"Inn"` vs a Gazebo;
anything else → plain resting). Also branches on `thisagent's "home"` +
`TaskName == "sulking"` as a separate path entirely, redirecting to
`$sulk` (a loyalty-check/desertion mechanic, not related to purchasing).
Payment runs the opposite direction from every shop-style building: the
**hero pays the Inn** a flat `#Price_per_Inn_Visit` via `$Pay_Inn`
(skipped for Elves, per an explicit title check), rather than the
building selling the hero something. `$Setattribute`s HP to max
(`rest_at_inn`) is the actual "service." Cleanup (`done_resting_inn`) is
the most divergent from `Shop_Visited` of anything traced: no
`$Reset_Tasks` call, `ActiveScript` is restored to
`ThisAgent's "BasicScript"` directly instead, and if the intent was the
minstrel-show variant the hero is paid `#Elf_Visits_Inn_Gold` +
`#Elf_Visits_Inn_Exp` on exit — the only building in this trace where
the *building* effectively pays *the hero* for a service rendered, the
mirror image of every purchase-style building.

**`Fairgrounds_Visited` (Fairgrounds)** — `mx_Fairgrounds.gpl`. Not a
`TaskName`-dispatch shop either — it's a 2-branch check
(`ThisAgent's "TaskName" == "Stat_Boost"` → `$Boost_Stats`, else →
`Enter_Tourney` if `#ATTRIB_CurrentEvent > 0` and the combatant list has
room, else the hero just leaves). `Boost_Stats` (the closest thing to a
"purchase" here) spends a flat `#Stat_Boost_Price` via `$Spend_Gold`,
then rolls a stat boost from a fixed pool keyed on `AttackType` (fighter
gets HtoH/Parry/Dodge, archer gets Ranged/Dodge/Parry, caster gets
Dodge/Parry) — no `$CreateNewInventoryItem`, the "item" is a permanent
`+1` via `$AdjustAttribute` capped at 95. The tourney path is a
genuinely separate subsystem: `Enter_Tourney` charges
`#Tourney_Entrance_Fee`, and the Fairgrounds' own `ActiveScript`
(`Fairgrounds_Poll`, run on the building itself, not per-hero) manages a
`Combatants` list and runs `Execute_Tourney`/`tourney_round` — a
best-of-N skill-roll contest keyed on `#ATTRIB_CurrentEvent` (1=Ranged,
2=HtoH, 3=Intelligence, 4=all three) that ranks heroes and pays out via
`Exit_Fair` (XP scaled by rank and hero count, plus gold/an
`got_prize1` effector/an instant level-up for a large first-place win).
No `$Reset_Tasks` anywhere in this file — cleanup is always a bare
`$Exit_Building` (in `Boost_Stats`, `Fairgrounds_Poll`'s no-tourney
branch, or `Exit_Fair`).

**`Hall_Of_Champions_visited` (Hall of Champions)** — confirmed to be a
"hang out and heal" loitering script per its own source comment, NOT a
shop — matches the guide's prior suspicion but now independently
verified rather than assumed. `Hall_Of_Champions_visited` itself is
nearly a no-op: `$enter_building` + intent + a fixed-duration timer
(`#Hall_of_Champions_Visit_Duration`, 10000ms per `mx_Globals.gpl`) before
`Leaving_Hall_Of_Champions` runs. That function heals the hero to full
HP and, if the hero doesn't already have the `Champions_Vigor_Icon`
effector, calls `Champions_Vigor_Begin` (`mx_Spells.gpl`) — a buff
granting `+15 MaxHP` for 90000ms. No gold, no `TaskName` dispatch, no
inventory item — cleanup is `$exit_building` + `$Reset_Tasks`, matching
only the Reset_Tasks half of `Shop_Visited`'s shape.

The building attribute gating this visit, `Hall_Champs_Check`
(`GPLMx/DecisionTrees/Modules/Hall_Champs_Check.gpl`), does a
**hardcoded `$ListObjects ... #CheckTitles, "HallOfChampions"` title
search**, not a `RewardFlag`/`check_rewards()` lookup — this independently
reconfirms the guide's existing Retracted Claim #1 (the earlier "bounty
functions are a RewardFlag mechanic" guess was wrong) rather than
repeating it.

**`HallOfChampions_Bounty_Cost`/`HallOfChampions_Bounty_Period` — traced,
previously genuinely unknown.** Both live in the same
`Hall_of_Champions.GPL` file as `Hall_Of_Champions_visited`, but are
**never called from anywhere in the `.gpl` source tree** — `grep_search`
across every `.gpl` file in both `GPL/` and `GPLMx/` finds zero call
sites for either function name; their own doc comments ("Called by the
guild action to determine the bounty period" / "Called by the interface
to fill in the bounty cost field") describe an exe-side interface/action
caller that has no GPL-visible counterpart, the same
UI-click-dispatch-is-exe-hardcoded situation already flagged for
research buttons elsewhere in this guide. Read as pure data: `bounty_index`
1/2 map to cost 400/800 gold and period 60000/120000ms respectively; a
commented-out `bounty_index == 3` branch (cost 1200, period 120000) exists
in both functions but is dead code, matching `Retracted Claims` #1's
observation of unused-but-declared bounty machinery. **Still UNVERIFIED:**
what exe-side UI/action actually invokes these two functions, and whether
a "bounty" ever manifests as anything beyond these two cost/period
lookups — no GPL function anywhere sets, checks, or pays out a bounty
using these values. This narrows the prior "genuinely unknown" status
(the functions' own content is now fully read) without fully resolving
it (their caller remains outside GPL source).

**The four namesake-only buildings** (`Poison_Weapons`, `Gambling_Hall`,
`Brothel`, `Gardens_visited`) are each short, single-purpose, and don't
share a common shape with each other beyond the `$Enter_Building`/
`$Exit_Building` bracketing every building in this guide uses:
- **`Poison_Weapons`** (`mx_Poison_Weapons.gpl`) — no `TaskName` dispatch,
  no gold spent. `Obtain_Poison` unconditionally sets
  `#ATTRIB_WeaponPoisoned = 1` on the hero. Cleanup
  (`Done_Poisoning_Weapon`) is `$Exit_Building` + `$Reset_Tasks` — matches
  only the Reset_Tasks half of `Shop_Visited`'s shape, no purchase step
  at all (poisoning is free).
- **`Gambling_Hall`** (`mx_Gambling_Hall.gpl`) — a wager-and-roll mechanic,
  not a purchase. `Exit_Gambling_Hall` wagers a random amount (capped by
  `#Maximum_Wager`) against a `Luck`-then-`Artifice` skill roll; on a win
  `$Give_Gold` pays out the wager, on a loss `$Hero_Pay_Distractor` takes
  it — read in full in `mx_LowLevel.gpl`: it subtracts gold from
  `ThisAgent` (`#ATTRIB_StoredGold` first, then `#ATTRIB_Gold`) but never
  credits the building at all, confirmed by its own comment ("This is
  for Hero Distractors like the Gambling Hall and Brothel. They have
  taxrate 0, but still need to have the overlays above their heads show
  that they got gold") — the hero visibly loses gold but the building's
  own coffers never increase, unlike every `$Spend_Gold`-based purchase
  elsewhere in this guide. No `$Reset_Tasks` call anywhere in the file.
  Also calls `$IncrementStatCounter(thisagent, "gutter")` on entry, a
  statistics side effect `Shop_Visited` never has.
- **`Brothel`** (`mx_Brothel.gpl`) — the simplest of the four: sets
  `#intent_relaxing_in_lounge`, enters, sleeps for `Target's "Sleep_For"`,
  then `Exit_Brothel` charges a flat `#Brothel_Cost` via the same
  building-doesn't-actually-get-paid `$Hero_Pay_Distractor` function
  `Gambling_Hall` uses, then exits. No `$Reset_Tasks`. Same `"gutter"`
  stat-counter call as `Gambling_Hall` on entry.
- **`Gardens_visited`** (`mx_Gardens.gpl`) — a healing-plus-random-buff
  script, structurally closest to `Hall_Of_Champions_visited` of the
  four (rest → heal to full → random beneficial effect), not to
  `Shop_Visited`. `Done_resting_gardens` rolls 1-of-6 buffs (winged feet,
  blessing, stone skin, camouflage, invisibility, anti-magic shield),
  each gated by "don't already have this effect," then restores
  `ActiveScript` to `ThisAgent's "BasicScript"` directly — no
  `$Reset_Tasks`, matching `Inn_visited`'s cleanup shape rather than
  `Shop_Visited`'s.

**Net finding across all 10 traced functions:** only `Shop_Visited`,
`Bazaar_Visited`, `Library_Visited` (partially), and the two structurally-
gold-purchasing paths (`Obtain_Upgrade`/`Obtain_Enchantment`,
`Boost_Stats`) actually spend gold via `$Spend_Gold` for a permanent
attribute/spell gain. `Poison_Weapons`, `Gardens_visited`,
`Hall_Of_Champions_visited`, and `Guardhouse_Visited` are free services.
`Inn_visited`, `Brothel`, and `Gambling_Hall` move gold in the *other*
direction (hero pays or is paid, not "buys an item"). `$Reset_Tasks` is
present in roughly half the traced cleanups and absent in the other
half (Library, Inn, Fairgrounds, Gardens, Gambling_Hall, Brothel all skip
it) — it is NOT a universal building-visit cleanup step despite
appearing in the original `Shop_Visited`/`Bazaar_Visited` writeup;
correcting that impression is itself a finding, not a retraction, since
the original writeup never claimed universality, only described those
two functions.

**Resolving the "does every researchable item follow the gate-then-
purchase pattern" question, partially:** Library's spell-learning cases
confirm a second independent instance of Magic Bazaar's
`Researched_Item()`-style gate (a building `#ATTRIB_Research*` flag
checked before the AI purchase function returns something to buy) — see
`Does_Library_Have_New_Wiz_Spell`/`Does_Library_Have_New_Generic_Spell`
above. Blacksmith's `Obtain_Upgrade` also gates each tier on a research
flag (`#ATTRIB_ResearchArmorLevel_2/3/4` etc.), a third instance. But
Wizard's Guild's `Obtain_Enchantment` gates tiers on `ThisBuilding's
"Level"` instead, with no research-flag check at all, and
Fairgrounds/Poison_Weapons/Gardens/Inn have no research gate of any
kind (nothing to unlock — they're either always available or gated
purely by intent/state). So the pattern holds for every *researchable*
item across 3 independently-confirmed buildings (Bazaar, Library,
Blacksmith), but **not every purchasable/consumable thing in the game is
researchable** — some are flat-priced with no unlock step, which is a
different question than the original one and now distinguishes the two
rather than conflating them.

---

## 4. Guild Life: The Lived_In_Script Mechanic

Genuinely different from visiting, not a variant of it. `Lived_In_Script`
is declared only on `Guild()`/`Dwarven_Settlement()` prototypes (plus
mx-only `Outpost()`). A hero who "lives in" a building is a permanent
occupant (guild member, `"home"` field points at the building) who
periodically cycles through sleep/heal/tax on its own timer — not a
one-shot transaction ending in the hero leaving.

**`max_members`** (base game field) / **`#ATTRIB_MaxGuildMembers`**
(expansion, read via engine attribute instead — a real base/expansion
divergence, expansion's `prototype.gpl` literally comments the field out)
gates **recruitment capacity only** — read by `GuildHasOpenSlots` and
`Lair.gpl`'s bungalow-spawning loop, never by `Lived_In.gpl` itself. By
the time a hero reaches `Lived_In`, it's already a member.

**`Sleep_for`** is not a total stay duration — it's the one-shot delay
before `Rest_at_guild` (the next sub-phase) runs, set via
`$SetThreadInterval`. Every guild sets it to 30000ms (30s) with zero
exceptions. `Rest_at_guild` does the actual work: drops carried resources,
heals to full, hands off to `Done_resting_Guild` (`$exit_building` +
`$Reset_Tasks`).

**Confirmed structural differences from visiting** (not just naming):
- Entry/exit uses the same shared `$enter_building`/`$exit_building` pair
  as `Shop_Visited` — that part IS shared.
- `Lived_In` branches on the hero's *current* intent to pick a *new*
  display intent (`#Intent_Going_Home` → `#Intent_Resting`, etc.).
  `Shop_Visited` never sets an intent anywhere.
- Guilds **tax and bank** a hero's gold (`Transfer_Gold` to `StoredGold`);
  shops **spend** it on purchases. Structurally different money model.
- `Lived_In` has zero `TaskName` dispatch — every hero gets the identical
  tax→sleep→heal→leave sequence, because `use_building.gpl` explicitly
  clears `TaskName` to `""` right before jumping to `Lived_in_Script`.

**The `go_home` → `use_building` → `Lived_in_Script` chain, traced
concretely:** every hero class's decision tree calls `$Go_home`.
`go_home.gpl` returns FALSE immediately if `home == $Nullagent()`
(Palace-born heroes have no "home" — `hero_birth` explicitly nulls it if
the parent is a Palace); otherwise sets `ActiveScript = $use_building`,
`target = home`, **`taskname = "go_home"`**, and
`$SpecifyIntent(#Intent_Going_Home)`. Once travel completes (via the
`BackScript` relay in §1), `use_building` runs with the hero physically
inside: it checks `taskname == "go_home"` — **this exact string
comparison is the entire routing mechanism** — true routes to
`target's "Lived_in_Script"` (and clears TaskName); false (any other
arrival, e.g. via `Visit_Building`) routes to `target's "visited_script"`.
This is a closed, single-entry-point mechanism — no other GPL code reads
`Lived_in_Script` anywhere in the workspace.

**A building can have BOTH fields simultaneously** — e.g. `Rogues_Guild2`
sets both `Lived_In_Script` and `Visited_Script: Poison_Weapons`. They're
not mutually exclusive; `use_building`'s TaskName check is what decides
which one runs for any given arrival.

**Confirmed NOT to use this mechanism** despite superficially "holding"
heroes: Mausoleum (interface/occupant-driven revival) and HallOfChampions
(hardcoded title-search, no membership concept) — both `{Building}`-typed,
not `{Guild}`-typed.

---

## 5. Building Economy: Revenue, Taxation, Palace Income

**`RevenueScript`/`Revenue_Amount`/`Revenue_Time`** are declared only on
`building`/`Fairgrounds`/`GuardHouse`/`Tower` prototypes. The mechanism
IS a recurring timer (started once at second-stage birth via
`building_birth`, interval = the building's own `revenue_time` field), but
what happens on each tick is **not uniform** — 5 distinct function bodies
exist, all funneling into `$Give_Gold`:

1. **`Revenue_Adjuster`+`Get_Marketplace_Revenue`** (Marketplace only) —
   the most complex: reads OTHER buildings' counts (extra markets, trading
   posts, housing), adds Palace-level bonuses, applies an Elven_Bungalow
   multiplier, self-requeues explicitly.
2. **`inn_revenue`** — flat amount ±25% jitter, bonus scaled by housing
   count. No self-requeue call (interval fixed for the building's life).
3. **`fairgrounds_revenue`** — the base amount **doubles per combatant**
   currently in the Fairgrounds (multiplicative, not additive).
4. **`generic_revenue`** — the only variant matching "flat amount on a
   timer" literally. Used only by `Royal_gardens`.

Complete cross-reference (both `.dat` files, identical between base and
expansion — expansion does **not** add more auto-revenue buildings, a
plausible-sounding assumption that's false): `Marketplace1/2/3`,
`Fairgrounds`, `Inn`, `Royal_gardens` — exactly 6 buildings, no others.
`GuardHouse`/`Tower` **declare but never set** these fields (dead for
those families). `Trading_Post` shares `Shop_Visited` with Marketplace but
has **no** `RevenueScript` at all — its income (if any) comes from its own
dedicated `ActiveScript` thread instead.

**Marketplace also has a bursty "Market Day" mechanic** layered on top
(`DoMarketDay`/`EndMarketDay`, both commented "called by the ingame code")
that computes a lump payout and `$SuspendThread`s the normal revenue timer
while it runs. **UNVERIFIED**: no GPL-side call site for either function
was found — same "comment is the only evidence" caveat as
`building_upgraded` above.

**Revenue does not reach the player's spendable gold directly.**
`$Give_Gold` adds to the *building's own* `#ATTRIB_gold` attribute, a
separate pool from player gold. Getting it to the player requires a Tax
Collector: `collect_tax.gpl`'s `tax_building` reads the building's
`#ATTRIB_gold`, moves it onto the collector, zeroes the building; then
`bring_home_goods` has the collector physically travel home and calls
`$AdjustPlayerData(..., "gold", ...)` — the actual player-gold-increasing
call. **UNVERIFIED**: what sets a building's `#ATTRIB_isTaxed`/
`#ATTRIB_QuickTax` gating flags — no source location found anywhere in the
available SDK.

**Palace's own income is structurally independent.** Palace has no
`RevenueScript` fields at all. Its `ActiveScript` (`palace_revenue`,
started by `Palace_Birth` on a 20-second cycle) computes
`#palace_revenue_amount * level * (buildingCount+1)` (capped at 300) and
calls `$AdjustPlayerData` **directly** — skipping the building-pool-then-
tax step entirely. `palace_revenue` also separately gives flat gold to
completed `General_Housing` buildings — so housing income is Palace-
driven, not building-self-driven. No call site connects `palace_revenue`
to any of the 6 `RevenueScript` functions or vice versa (only indirect
contact: Marketplace's revenue math reads Palace's level for a bonus).

---

## 6. Guard Spawning and Defense

`Guard_Function`/`Guard_Spawn_Function` are declared as a pair on
**three** prototypes — `GuardHouse`, `Palace`, and mx-only `Outpost` — not
just Guardhouse as the name might suggest. Palace's own comment frames
Guardhouse's copy as the derivative ("Guardhouse's version of an
ActiveScript"). `Tower` declares neither.

**`Guard_Function` is a scan/dispatch loop, never a spawner.** Started via
`$NewThread` on `#Normal_Cycle` (300ms, i.e. it behaves exactly like an
ActiveScript). It cycles between exactly two values:
- **`Building_Guard`** (the birth-time initial value): each tick, checks
  for enemies in sight or buildings under construction — if found, swaps
  itself to `$Release_Guards`. If none found and title is literally
  `"Guardhouse"`, has a 1% chance to swap and set `TaskName = "Wander"`,
  or (research-gated) swap and set `TaskName = "Switch_guards"` — this
  is the confirmed origin of both `TaskName` values cited generically in
  §1.
- **`Release_Guards`**: fires the Guardhouse arrow action if researched,
  drains waiting guards, sets each guard's *own* ActiveScript to
  `$Guard_Find_Target`, resumes them. Never touches `Guard_Function`
  again itself.

**`Guard_Spawn_Function` is a completely separate concern** — three
distinct spawner functions, all of which actually call `$SpawnUnit`
(which none of `Guard_Function`'s values do):
- **`City_Guard_Spawner`** (GuardHouse only) — spawns at the *Palace*, not
  the Guardhouse itself, then queues the Guardhouse on `Palace's
  "Waiting_Guardhouses"`. Does **not** self-requeue — re-arming is handed
  off to the newly-spawned guard's own birth logic.
- **`Palace_Guard_Spawner`** (Palace/Outpost) — spawns directly at the
  Palace, self-requeues explicitly on a fixed 17-second interval
  (`#Guard_Spawn_Time`).
- **`RestartGuardSpawnThread`** — never itself assigned to the field; a
  shared helper other code calls to conditionally restart whichever
  spawner is already registered, guarded by `$IsRunning`. Called from a
  newly-attached guard's own birth, a guard's death (a slot opened up),
  and `BuildingReachedMaxHP` (Guardhouse-specific — Max_Guards may have
  changed after an upgrade).

Confirmed set (both `.dat` files): `Palace1/2/3`, `GuardHouse1/2`, plus
expansion-only `Outpost`/`EvilPalace` (using the same `Palace_Guard_
Spawner`, no dedicated Outpost variant exists). `Ballista_Tower`/
`Wizards_Tower` set neither field, consistent with Tower declaring
neither.

**UNVERIFIED**: where the literal function `GuardHouse_Birth` (referenced
as `birthScript2` in the `.dat`) is actually defined — not found anywhere
in the GPL source despite the near-identical `guardhouse_birth` function
existing; not assumed to be the same function despite the name similarity.
Also unverified: what "trigger" Palace's field comment refers to (actual
logic is plain-timer-based, not event-driven, per the code read).

---

## 7. The Intent System (`#intent_*`)

`#intent_*` values are GPL-declared `expression` constants in
`defines.gpl`/`mx_defines.gpl` (86 base, 96 expansion), sharing one flat
integer namespace with `#message_*`/`#chat_*`/`#sign_*` — not four
separate ID spaces. `$SpecifyIntent` has no GPL definition (confirmed
engine primitive); there is no dedicated `$GetIntent` — reads go through
the generic `$GetAttribute(agent, #ATTRIB_AIIntentionString)`.

**Not purely cosmetic, but writes vastly outnumber reads.** Exactly 6 GPL
functions across 5 files genuinely read intent back to make decisions:

- **`Lived_In`** — reads current intent to pick a *new* display intent
  (feeds another write, not a behavior gate).
- **`Inn_visited`/`done_resting_inn`** — a real gameplay gate: if intent
  was `#intent_performing_minstrel`, grants actual gold/exp.
- **`Flee_Check`/`Berserk_Check`** (expansion-only, no base equivalent) —
  read intent to gate whether Speed Tonic/Strength Potion are allowed to
  be cast on an agent, wired via `<ValidationScript>` in the Action XML.
- **`ChangeOfHeart_Begin`** (expansion-only) — branches actual spell
  behavior (make a fleeing hero berserk, or vice versa) purely on current
  intent.

**For the specific intents most likely to come up in modding work**
(`#intent_visiting_hall_of_champions`, `#intent_charming_animals`,
`#Intent_purchasing_Bazaar_Item_One`–`_Six`, `#intent_controlling_undead`)
— confirmed **zero** GPL-side reads anywhere. `$SpecifyIntent` is the only
thing that happens to them.

**The primary real consumer is a shared string table, not GPL code.** The
`AITX` STRT section in `Data/gpltext.cam`/`DataMX/mx_gpltext.cam` is
positionally indexed by the exact same integer as the `#intent_*`/
`#message_*`/`#chat_*` expression values (confirmed via direct binary
extraction with `cam_reader.py`/`str_tool.py` — index 32 = "Charming
animals", index 265 = "Visiting Hall of Champions", etc.). This strongly
implies an exe-side lookup renders this as hero status text, but the exe
code itself, and exactly what UI element displays it, is **UNVERIFIED** —
needs Ghidra.

**Direct takeaway:** intent is primarily a "what is this agent doing"
display flag; a small set of GPL functions opportunistically reuse it as a
cheap boolean rather than adding a dedicated attribute. It was not
designed around GPL consumption, but it isn't write-only either.

---

## 8. Hero Death, Gravestones, and Revival

### What a gravestone actually is

**A gravestone is not a separate object.** There is no gravestone unit
type, IMAG entry, or XML `Description` anywhere in the game data. It IS
the same dead hero agent, with `"type"` set to `"Dead"`, its `ActiveScript`
swapped to a decay-timer function, playing its own `Die` animation once
and holding the last frame. (The base-game `BBJ1`/"Graveyard" building is
a structurally unrelated decorative AutoBuilding the Palace spawns after
15 hero deaths — don't conflate the two.)

**Creation:** `Unit_Call_Deathscript` (`Hero_Deaths.gpl`, comment: "called
by the in-game code when a unit's HP are set to 0 or less") dispatches to
whatever function each hero class's `IGDeathScript` field points to. Most
classes route to `gravestone()` directly; Healer routes through
`Healer_Death` first (calls `gravestone()` only if `Healer_Reborn_Check`
fails — see below); expansion-only Barbarian similarly checks a knockdown
roll first. Henchmen (guards, peasants, tax collectors) never get
gravestones — they go straight to deletion.

`gravestone()` itself: computes a level-scaled lifespan
(`#gravestone_lifespan` 10s × (level/3 + 1), capped at
`#Gravestone_lifespan_max` 90s), sets `type = "Dead"` (the single field
every other system uses to recognize it), sets intent to `#intent_dead`,
drops immediate-flagged inventory items, and reassigns `ActiveScript =
$be_dead` with the computed lifespan as the new tick interval.

### Decay and removal

`be_dead` fires once the timer expires: drops remaining quest items,
removes from any member lists, and **deletes the game piece outright** —
not archived, not hidden. It also increments a Palace-level dead-hero
counter that, once it hits 15, spawns the decorative Graveyard building
(unrelated bookkeeping, not about the specific gravestone just removed).

**Expansion adds exactly one gate before this runs:** `if
($Check_Mausoleum(thisagent) == FALSE)` — the entire deletion path is
conditional on Mausoleum interception failing (see below).

Two early-dismissal functions exist (`Unit_Dismiss_Gravestone`/`_Fast`,
both commented "called by the in-game code when a gravestone is being
dismissed") but **no GPL-side call site for either was found anywhere** —
only the comments describe when the engine calls them. **UNVERIFIED.**

### Three independent revival systems — do not conflate them

1. **Mausoleum** (interface/occupant-driven). `Check_Mausoleum` runs
   *inside* `be_dead`, at the moment the decay timer expires — before
   deletion. If a legal Mausoleum has an open slot, the hero is
   `$hide`-teleported inside it instead of deleted; type stays `"Dead"`.
   Excludes Healer/Monk/Paladin explicitly (Priestess exclusion
   **UNVERIFIED**). Actual revival requires the building's own
   `Mausoleum_Resurrect_Cost`/`_Begin` functions.
2. **Krypta/Agrela player-cast spells** (`$Reanimate_Begin`/
   `$Resurrection_Begin`, explicitly commented "player cast spell — from
   temple to krypta/agrela"). Target dead heroes found via
   `$ListObjects(..., "Dead", ...)` — the SAME `"Dead"` type-string
   `gravestone()` set. This means **a live, undecayed gravestone on the
   map is a legal spell target** for as long as it exists — but
   **UNVERIFIED** whether a Mausoleum-interred hero can still be matched
   by that same "Dead" query (if not, Mausoleum interception effectively
   removes a hero from Reanimate/Resurrection eligibility; not confirmed
   either way). A real base-game AI function, `Check_Resurrect`
   (`Quests_3.gpl`, wired to the SIEGE quest), implements a near-identical
   pattern for Krypta only — the workspace's own `MyAI` mod's
   `AI_Check_Resurrect` is a close adaptation of this real function, not
   invented from scratch, extended to also check Agrela. Note: the mod's
   `costToRevive` local variable is set but never actually read — the
   real gold check/deduction uses separate hardcoded literals that happen
   to match (2000/1500).
3. **Healer-Reborn** (self-resurrection, gated by a level-based chance
   roll before `gravestone()` even runs).

None of these three call each other or share a helper function — confirmed
by tracing all three independently.

### Looting gravestones (a fourth, unrelated interaction)

`Loot_Gravestones.gpl` is a hero-AI "steal gold from dead bodies"
behavior — chance-gated, queries `"Dead"`-type objects with
`#ATTRIB_Gold > 0`, filters out moving targets (a "probably mid-
resurrection" heuristic the code's own comment admits is imperfect) and
`Black_Phantom` titles specifically, then routes the looting hero to
`$Go_Steal`. Confirms gravestones carry a live, stealable gold value while
on the map.

### Modding gravestones

Appearance is **not** independently swappable and **not** hardcoded
per-gravestone — it's simply whichever `ImageIDBase`/`Die` animation set
the dying hero's own unit definition already resolves to. Changing a
hero's `ImageIDBase` (per `CAM_MODDING_GUIDE.md`'s appearance recipe)
changes its gravestone look too, since it's the same sprite entry, not a
separate DialogID. The `Basic_death` action GPL triggers uses a numeric
`cProc="8192"` callback (rather than a named `GPLFunction=`) — what that
numeric code resolves to on the engine side is **UNVERIFIED**, would need
Ghidra.

---

## 9. Orphaned Content: The "Zoo" Building

Real assets and real GPL logic exist, but nothing wires it up as a
placeable building anywhere in current data — treat as inactive/orphaned,
not something you'd encounter in normal play.

- **Sprites confirmed present**: `ABn1`/`ABn2`/`ABn3` ("Zoo Level 1/2/3")
  IMAG entries in `DataMX/mx_maindata.cam`.
- **GPL logic confirmed complete, not a stub**: `Zoo.gpl` implements a
  bounty-flag "capture a monster on its death" mechanic —
  `zoo_flag_birth` → `Set_Subdue_Chance` (cost curve: gold spent vs.
  target strength, capped at 95%) → `zoo_flag_check` (fired from the
  flagged creature's own deathscript: roll the charm chance, if a living
  hero is within radius, revive the creature at 1/3 HP and hand control
  to that hero via `$Control_monster`) → cleanup.
- **No XML building definition anywhere** — searched `M_Buildings.xml`/
  `MX_Buildings.xml` case-insensitively for `ABn1`/`ABn2`/`ABn3`/`Zoo`,
  zero matches (the only `ABN1` hit is an unrelated "Sewers" entry, a
  different casing/ID collision). No quest file references it either.

**Zoo's charm mechanic and the Cultist's level-1 `Charm_Monster` spell
share a primitive, not logic.** Both call `$Control_monster`/
`$control_monster`, but Zoo's is passive/chance-based/death-triggered,
Cultist's is an actively player-cast spell. Similarly, Zoo and Hall of
Champions' bounty system both build on the same generic `RewardFlag`
infrastructure (stubbed out generically in base `LowLevel.gpl`'s
`RewardFlag_Birth`), each wrapping it with different payoff logic — not
shared code between the two.

See `TODO-Ghidra.md` for a low-priority idea: since Zoo already has a
reserved DialogID family and sprites, it might be a lower-risk repurposing
target than carving out brand-new IDs for other exe-patch work — pending
confirmation the exe itself has any dormant plumbing for it.

### §9 continued: Systematic sweep result — Zoo remains the only orphan

Zoo was found opportunistically. This is the systematic follow-up: every
entity-shaped IMAG prefix (`AB` player buildings, `AV` heroes/NPCs, `BV`
monsters, `BB` lairs/structures — the same categories `CAM_DEEP_DIVE.md`
assigns them) was extracted in full from both `Data/maindata.cam` (380
IMAG entries) and `DataMX/mx_maindata.cam` (166 IMAG entries) via
`cam_reader.py`, then each individual ID was grepped as an `ID="..."`
attribute against `M_Buildings.xml`, `MX_Buildings.xml`,
`M_Characters.xml`, and `MX_Characters.xml` (the only building/character
definition files under `Majesty_Files/SDK/OriginalQuests/{Data,DataMX}/`
— confirmed by listing that directory, no other unit/building XML exists
there).

**Prefixes checked (entity-shaped, would plausibly have an XML
`Description` if real):** `AB` (67 unique IDs across both CAMs), `AV` (36
unique IDs), `BV` (48 unique IDs), `BB` (49 unique IDs).

**Prefixes deliberately excluded, with reason:** every other prefix in
both CAMs' IMAG sections — `AP`/`AR`/`BG`/`BP`/`BR`/`CG`/`CR`/`DR`/`FG`/
`GG`/`HR`/`IG`/`LG`/`LR`/`MR`/`MV`/`NP`/`NR`/`PG`/`PP`/`PR`/`QR`/`RG`/
`SR`/`TG`/`TR`/`UG`/`VG`/`WG`/`WP`/`WR`/`XL`/`YG`/`NG`/`WV`/`XR`/`FX`.
`CAM_DEEP_DIVE.md`'s own per-prefix breakdown sections independently
categorize these as projectiles/spell-effects/particle-effects/movement-
effects (`MR`, `MV`, `WP`, `WR`, `XL`, `NG`, `WV`, `XR`, `PR`), not
placeable buildings/characters — confirmed by their own ID names (e.g.
`WPh1` "Chain_proj", `XL24` "earthquake_p") which have no unit-placement
shape at all (no plausible `Description type="Unit"` slot to occupy).
None of these were checked individually against the XML files; this
matches the task's own guidance not to treat every unmatched IMAG entry
as a meaningful orphan.

**Result — `AB`, `BV`, `BB`: zero unmatched IDs beyond the already-known
Zoo.** Every single `AB`/`BV`/`BB` ID in both CAMs (including all 14
mx-only `AB` IDs, 16 mx-only `BV` IDs, and 11 mx-only `BB` IDs) has a
matching `ID=` entry in `M_Buildings.xml`/`MX_Buildings.xml`/
`M_Characters.xml` — checked individually via `grep_search`, not sampled.
`ABn1`/`ABn2`/`ABn3` (Zoo) remain the sole exception, already documented
above.

**Result — `AV`: two unmatched IDs found, `AVn8`/`AVn9` ("selection_red"),
but they do NOT match Zoo's orphan shape.** Extracted their IMAG blobs
directly (`n_dirs=4`, 2 image sets each: `setID=8` "Stand" +
`setID=1005`) — structurally identical to `AVn1` ("selection_ring") and
`AVn2` ("flag_brackets"), which **are** both wired into
`M_Characters.xml` (`ID="AVn1"`/`ID="AVn2"`, both `subType="Character"`
but flagged `Info value="Directionless"`/`"NotVisibleInOverheadView"`,
i.e. UI/selection-indicator overlays, not placeable entities). `AVn8`/
`AVn9`'s real sprite data (not a stub — same frame-set shape as their
wired siblings) plus their "selection_red" name place them in the same
UI-selection-indicator family as `AVn1`/`AVn2`, not the hero/NPC entity
category the `AV` prefix is otherwise used for. Unlike Zoo, they also
have **zero GPL references anywhere** (`selection_red`, `AVn8`, `AVn9`
all searched, zero hits in any `.gpl` file) — Zoo's defining trait was
sprites **plus working GPL gameplay logic** with no XML wiring; `AVn8`/
`AVn9` have neither GPL logic nor a plausible entity role, so they don't
meet the bar. Noted here rather than silently dropped, per the evidence
standard, but **not** counted as a second orphan family.

**Conclusion: the systematic sweep found no additional orphaned
buildings/heroes/monsters/lairs beyond the already-documented Zoo.** For
the `TODO-Ghidra.md` "Zoo as an EXE expansion point" idea, Zoo is
confirmed to still be the only candidate of its kind in the base+
expansion IMAG data — not one opportunistic find among several
undiscovered ones.

---

## 10. Hero AI Dispatch Is a Closed Set — Not Generically Extensible

`check_rewards()` (the generic reward-flag hero-AI evaluator) only
recognizes exactly two hardcoded flag titles: `"flag_attack"` and
`"flag_explore"`. There is no default/fallthrough case — an unrecognized
title simply never accumulates score and is never selected. Zoo's
`RewardFlag` variant is never assigned either title — its charm effect
fires reactively from the target's own deathscript, never through
`check_rewards()` at all.

**Practical implication:** creating a new custom flag/reward variant does
**not** get automatically picked up by hero behavior. Adding new
hero-seekable flag behavior requires either (a) extending
`check_rewards()` itself — affects **all** hero classes at once since they
funnel through the same function, or (b) writing a dedicated check
function and explicitly adding a call to it in every hero class's decision
tree file individually (the `Hall_Champs_Check` pattern — confirmed called
from at least 13 separate files). There is no single registration point
that automatically applies to every hero class except `check_rewards()`
itself.

---

## 11. Petrification System Re-Verification (Template for New Status Effects)

`.kiro/steering/majesty-modding.md`'s "Petrification System" section
lists 6 claims about the petrify system, written down as a template for
new status effects but never independently re-checked against source.
Re-verified here against `GPL/TaskModules/Subtasks/Spells.gpl`
(`Petrify_Begin`/`Petrify_End`, lines 1515-1558),
`GPLMx/TaskModules/Subtasks/mx_Spells.gpl` (byte-identical base pair at
lines 3708-3751, plus `Gorgon_Petrify_Begin`/`Gorgon_Petrify_End` at
lines 1307-1351), `GPL/LowLevel.gpl`/`GPLMx/mx_LowLevel.gpl`
(`IsFrozen`, lines 683-691 base / 759-767 expansion), `Data/M_Actions.xml`,
`Data/M_Overlays.xml`, and `DataMX/MX_Actions.xml`.

1. **CONFIRMED, with a correction — and a further correction after user
   input identified a real gap in how this item was originally scoped.**
   No Action XML entry exists anywhere in the `.gpl`/`.xml` tree with
   `GPLFunction="Petrify_Begin"` — grepped the full workspace, zero
   matches. No `AllowedSpells` entry on any hero/character grants it
   either. **This originally read as "UNVERIFIED how the base game
   invokes it," but that framing missed the actual mechanism: Petrify is
   not a hero-cast spell at all — confirmed by the user (a modder
   experienced with this game) that Petrify is cast directly from the
   Temple to Dauros building itself, unlocked at building Level 3.** This
   is consistent with, not contradicted by, everything actually found in
   source: `Petrify_Begin`'s own comment says "player cast spell - from
   temple to duaros" (already cited above) — a building-cast spell
   correctly has no hero `AllowedSpells` entry and no need for a
   `GPLFunction`-wired Action XML record the way a hero's spell would,
   because a building's own DialogID panel is a different UI/casting
   pathway that this research had not previously distinguished from the
   hero-cast pathway. **`Temple_Dauros1/2/3` (`M_Buildings.xml`) all
   share `DialogID value="AP05"`** (confirmed — same value on all 3
   tiers, matching this doc's own §2-equivalent finding elsewhere in the
   project that tier upgrades don't change `DialogID`), so Dauros's
   building panel is a single, real, already-mapped panel. **What
   remains genuinely UNVERIFIED, now correctly scoped:** the Level-3
   gating itself has no visible source anywhere — `Temple_Dauros3`'s XML
   `<Game>` block has no spell-grant field, `AllowedSpells`-equivalent,
   or any attribute distinguishing it from `Temple_Dauros1/2` beyond the
   ordinary `Cost`/`MaxHP`/`Level` tier fields already documented
   elsewhere in this project — and no GPL call site invokes
   `Petrify_Begin` from anywhere. This strongly suggests the AP05
   panel's own "cast" button (if Petrify appears there only once the
   building reaches tier 3) is an exe-hardcoded per-DialogID mechanism,
   the same general class of opacity as the already-documented
   `DialogID`→panel-factory hardcoding — but this is a NEW, more precise
   Ghidra question than the original vague "how is it invoked," and
   hasn't been added as its own scoped item yet (see `TODO-Ghidra.md`).
   The expansion's Gorgon variant **is** fully wired the ordinary
   hero/monster-spell way: `DataMX/MX_Actions.xml` ID `A030` Name
   `Gorgon_Petrify`, `GPLFunction="Gorgon_Petrify_Begin"`,
   `TimeoutDuration="90000"`, `SpellType="Attack"`, `SpellRank="1"`, and
   `MX_Characters.xml` line 457 grants it to the Gorgon via
   `<Spell ID="0" Value="Gorgon_Petrify"/>` — confirming the Gorgon spell
   and the base Petrify spell are wired through two structurally
   different systems (monster attack-spell vs. building-cast spell),
   not the same mechanism reused. **Lesson for future dispatches, stated
   plainly:** this gap wasn't a research failure so much as a scoping
   gap — nothing in this project's docs previously named "building-cast
   spell (selected on the map, cast from its own panel)" as a distinct
   third spell-casting pathway alongside hero-`AllowedSpells` and
   monster-attack-spells, so a source-only grep had no vocabulary to
   search for the right thing. Domain knowledge from an experienced
   player/modder closed this gap faster than re-reading source further
   would have.
2. **CONFIRMED for the overlay definitions, corrected for the callback
   mechanism.** Both overlays are real: `Data/M_Overlays.xml` ID `MRB1`
   Name `petrify_effector` (visible, `Info=Directionless`+`DontBlock`,
   `DefaultSound="Petrify"`, no script) and ID `MRB2` Name `petrify_icon`
   (`Info=Directionless`+`DontBlock`+`NotVisibleInISOView`,
   `Script GPLFunction="Petrify_End"`). The "invisible timer that calls
   end function" claim is **correctly traceable, not just a comment's
   assertion**: `petrify_icon`'s own XML `<Script>` tag wires
   `GPLFunction="Petrify_End"` directly — the engine invokes it when the
   overlay's effector duration (the `time` value passed to
   `$createeffector(thisagent,"petrify_icon",time)` in `Petrify_Begin`)
   expires. The GPL comment ("callback from petrify_icon effector") is a
   correct human description of this same real XML-level wiring, not an
   independent/unverifiable claim.
3. **CONFIRMED exactly**, read line by line. `Petrify_Begin(agent
   thisagent)`: no-target-check via `$IsDead`, computes `time = 19000`
   (halved on a `#ATTRIB_MagicResistance` roll), creates both effectors,
   sets `#ATTRIB_HasEffectPetrify = 1`, calls `$GetProperUnitArt`, calls
   `$Freeze_Unit`, calls `$SpecifyIntent(thisagent, #intent_petrified)`.
   `Petrify_End(agent thisagent)`: clears `#ATTRIB_HasEffectPetrify = 0`,
   calls `$GetProperUnitArt`, calls `$UnFreeze_Unit`. This matches
   "applies effect"/"removes it" exactly — no discrepancy.
4. **CONFIRMED, not redundant — they serve different purposes.**
   `#ATTRIB_HasEffectPetrify` is petrify-specific: set in `Petrify_Begin`/
   cleared in `Petrify_End`, and it is the exact flag `UnFreeze_Unit`
   checks (alongside `HasEffectVines`/`HasEffectParalyticGaze`/
   `HasEffectLevelLeach`) before it will actually resume the unit — i.e.
   it's petrify's entry in a shared "freeze lock" gate used by 4 different
   effects. `#ATTRIB_IsFrozen` is a **generic movement-lock flag** set by
   `Freeze_Unit`/cleared by `UnFreeze_Unit` themselves (`Spells.gpl` lines
   2137/2161) — it is not set or read anywhere inside `Petrify_Begin`/
   `Petrify_End` directly. It's a side effect of calling the shared
   `Freeze_Unit`/`UnFreeze_Unit` helpers, read by unrelated code
   (`Guild_Skills.gpl`'s `DoAssembly`, `mx_Spells.gpl`'s
   `ChangeOfHeart_Begin`) via the `$IsFrozen()` GPL function — which
   itself does **not** read `#ATTRIB_IsFrozen` at all; it checks
   `$CheckEffector(thisagent,"petrify_icon")` (plus 3 other effect
   overlays) directly (`LowLevel.gpl` lines 683-691). So: two flags, two
   distinct roles — one is petrify's specific "don't unfreeze me yet"
   vote, the other is a general "can't move" flag set as a side effect,
   and the actual frozen-check helper function (`$IsFrozen`) reads
   neither of them, it reads effector presence instead.
5. **CONFIRMED that the intent is set** (`$SpecifyIntent(thisagent,
   #intent_petrified)`, `Spells.gpl` line 1540) but the "forces unit to
   stop acting" characterization is **not what actually immobilizes the
   unit**. `#intent_petrified` (value 82, `defines.gpl` line 90) is a
   pure display/status flag per §7's findings — it has no GPL-side
   behavioral enforcement anywhere (confirmed no `== #intent_petrified`
   read exists in the `.gpl` tree). The real immobilization is
   `$Freeze_Unit`, called on the line immediately before
   `$SpecifyIntent` in `Petrify_Begin` — it calls `$StopMoving` +
   `$SuspendThread(ThisAgent's "ActiveScript")` + sets
   `#ATTRIB_IsFrozen = 1` (`Spells.gpl` lines 2128-2139). So the doc's
   claim attributes the actual stop-acting mechanism to the wrong
   primitive — it's `$Freeze_Unit`/`$SuspendThread`, not `#intent_petrified`.
6. **NOT CONFIRMED — marking UNVERIFIED, correcting to UNKNOWN.** No
   decision-tree code anywhere reads `#ATTRIB_IsFrozen` — grepped
   `DecisionTrees/` specifically, zero matches. `#ATTRIB_IsFrozen` has
   exactly 2 writers (`Freeze_Unit`/`UnFreeze_Unit`) and 0 readers
   anywhere in the `.gpl` tree (only the mod's own unreleased `IceSpell.gpl`
   reads/writes it for a different, unrelated stacking mechanic). The
   actual "is this unit safe to skip/interact with" check AI code uses is
   `$IsFrozen()` (confirmed real, `LowLevel.gpl`), but even that isn't
   called from any decision tree — its 2 real call sites are
   `Guild_Skills.gpl`'s `DoAssembly` (skip teleporting frozen guild
   members) and `mx_Spells.gpl`'s `ChangeOfHeart_Begin` (skip
   berserk-flip on a frozen hero). Neither is a decision tree. The doc's
   claim that "AI uses this to skip petrified units in decision trees" is
   unsupported by any found call site — the mechanism doesn't exist as
   described.

**Correction recorded in `.kiro/steering/majesty-modding.md`:** claim 1
(Action XML) had its wrong implication removed, claim 5 (intent) was
corrected to name `$Freeze_Unit` as the actual immobilizer, and claim 6
was corrected to note it's unverified/no call sites found. See that
file's Petrification System section for the corrected text — this is a
visible correction, not a silent overwrite (same convention as this
guide's own "Retracted Claims" section, applied here across two files).

---

## 12. Building-Unlocked Guild Skills

Two real base-game examples of the same general shape as building-cast
Petrify — `Guild_Skills.gpl`'s `DoRageOfKrolm` (Temple of Krolm) and
`DoAssembly`/"Call to Arms" (Warriors Guild, `DialogID="AP52"`) — traced
per the two sub-questions raised in `TODO-GPL-Deepdive.md`.

### Question 1: Unlock/lock mechanism

1. **CONFIRMED (by the user, an experienced player/modder): Rage of
   Krolm and Call to Arms are ordinary button clicks inside their own
   guild's building panel** (Temple of Krolm's own panel for Rage of
   Krolm, Warriors Guild's `AP52` panel for Call to Arms) — the same
   general trigger CLASS as Petrify's AP05 button, not a mystery
   mechanism. This resolves the "how is it triggered, conceptually"
   question the earlier pass had marked UNVERIFIED. **What remains
   genuinely unconfirmed from source alone is only the exe-side
   click-dispatch code itself** — no GPL/XML call site invokes either
   function (grepped the full `.gpl` tree, base `GPL/` and expansion
   `GPLMx/`, for literal `$DoRageOfKrolm(`/`$DoAssembly(` call syntax,
   zero matches anywhere), consistent with these being ordinary
   building-panel buttons whose click handler lives entirely in the exe
   (the same `DialogID`-scoped click-dispatch class already documented
   for research/recruit buttons elsewhere in this project, not a new or
   different mechanism). The only other appearances of these function
   names in the workspace are: the function *definitions* themselves
   (`Guild_Skills.gpl`/`mx_Guild_Skills.gpl`), a stray self-referencing
   comment inside `DoRageOfKrolm`, the custom `Dwarfeh_AI` mod's
   `.dat`/`.gpl` files (Question 2 below — a mod calling it, not the
   base game wiring it), and this project's own research docs
   classifying `$DoRageOfKrolm`/`$DoAssembly` as "undocumented engine
   primitives callable from GPL" — consistent with an exe-side button
   handler that happens to call out to a real GPL function once
   clicked, exactly like a research-panel purchase button does.
2. **CONFIRMED as bare as Temple_Dauros — no Skill/Ability field
   anywhere.** Read `Temple_Krolm`'s (`M_Buildings.xml` ID `ABS1`,
   `DialogID="AP24"`) and `Warriors_Guild`'s (ID `ABV1`,
   `DialogID="AP52"`) full `<Description>` blocks end to end. Both
   `<Game>` blocks contain only the ordinary guild-building field set —
   `DialogID`, `Cost`, `Multiplier`, `IncomeType`/`IncomeAmount`,
   `MaxHP`, `MaxGuildMembers`, `SightRange`, `Flags` (`IsGuild`/
   `HasHPBar`/`HasGoldToolTip`), `HelpID`, `Produces` (the unit type the
   guild recruits) — no `Skill`, `Ability`, `AllowedSpells`, or any
   similarly-named field on either. Grepped the entire `M_Buildings.xml`
   for `<Skill`/`<Ability`/`AllowedSpells` — zero matches anywhere in the
   file, not just on these two buildings. **Genuinely new finding vs.
   Petrify, not symmetrical:** unlike `Temple_Dauros1/2/3` (3 upgrade
   tiers), `Temple_Krolm` and `Warriors_Guild` are **single-tier
   buildings with no `UpgradeTo`/tier chain at all** — confirmed by
   grepping for `Warriors_Guild2`/`Warriors_Guild3`/`Temple_Krolm2`/
   `Temple_Krolm3`, zero matches, and by their `Building_Data.dat`
   entries (`SDK/OriginalQuests/GPL/Building_Data.dat`) which declare no
   `Level`/`UpgradeTo` fields at all (unlike e.g. `Temple_Krypta1`'s
   entry two buildings above Krolm's in the same file, which does have
   `(Level 1)`). This means the guild-skill mechanism cannot be a
   level-gate the way Petrify's apparently is — there is no tier to gate
   on. Whatever unlocks Rage of Krolm/Call to Arms, it is tied to
   something other than building level, because these buildings only
   have one level.
3. **UNVERIFIED, stated explicitly as requested — no evidence found
   either direction.** Read `building_death`, `guild_destroyed_common`,
   `guild_destroyed_a`/`guild_destroyed_2` in full
   (`SDK/OriginalQuests/GPL/Building_Deaths.gpl` lines 204-218,
   526-610+, plus the two 1-line wrappers). `Temple_Krolm`/
   `Warriors_Guild`'s `IGdeathscript` is `guild_destroyed_a`
   (`Building_Data.dat` lines 736-747/423-434), which calls
   `$guild_destroyed_common(thisagent, $homeless)`. That function's full
   body handles only guild-member reassignment (finding the members a
   new home guild, or making them homeless/fleeing) and calls
   `$release_occupants` — it contains no reference to any player-level
   flag, no `#ATTRIB_*` write resembling a skill-revocation, and no call
   to anything Rage-of-Krolm/Call-to-Arms related. `building_death`
   itself (the function `guild_destroyed_a`/`_2` do NOT call directly,
   but which every non-guild building's death path funnels through) is
   even simpler: sets `type = "Dead"`, releases occupants, cleans the
   palace's construction lists, triggers the `Become_Rubble` visual, and
   deletes the agent — again nothing skill-related. **No GPL code
   anywhere checks "does the player still have a Temple of
   Krolm/Warriors Guild" before allowing `DoRageOfKrolm`/`DoAssembly` to
   fire** (consistent with finding 1: since nothing in GPL calls these
   functions in the first place, there is also nothing in GPL that could
   gate them). Whether destroying the building revokes the ability is
   therefore **UNVERIFIED** — it depends entirely on whatever
   exe-side code renders the AP24/AP52 panel buttons (does it check for
   building existence live, same as it would need to for the Level-3
   Petrify gate?), which no GPL/XML source addresses. Do not assume
   either "yes it's revoked" or "no it persists" — neither is supported.
   Given finding 1's confirmation that this is an ordinary panel button
   (not a hidden/unusual mechanism), the most direct way to resolve this
   without Ghidra would be an in-game test: destroy the Temple of
   Krolm/Warriors Guild and check whether the Rage of Krolm/Call to Arms
   button is still present/clickable on... nothing, since the building
   is gone — the real test is whether a SECOND copy of the same guild
   (if the player has two Warriors Guilds) still shows the button, or
   whether losing the only one simply removes the button along with the
   building itself (the more likely/mundane answer, given the button
   lives ON that building's own panel — you can't click a panel for a
   building that no longer exists). This may be more "obviously the
   building is just gone, so is its panel and button" than a genuine
   revocation mechanic — flagged as the likely resolution, not confirmed
   from source, and not requiring Ghidra to settle empirically.
4. **CONFIRMED genuinely different, not the same mechanism as Petrify's
   Level-3 gate — checked directly, not assumed.** Petrify's gate is
   tier-based (`Temple_Dauros3` only) on a building that has 3 tiers.
   Guild skills' buildings have exactly 1 tier each (finding 2 above) —
   there is no tier for a "reach tier 3" gate to apply to. If an
   exe-side gate exists for guild skills at all, it must check something
   other than building level (e.g. building existence alone, guild
   member count, or something else entirely) — structurally it cannot be
   "the same Level-3 mechanism Petrify uses" even if both are ultimately
   exe-hardcoded-and-unfindable-in-source. This directly answers the
   cross-check requested: the two are **at minimum differently
   parameterized**, and possibly entirely different mechanisms — source
   alone cannot say which, but it can rule out "identical Level-3 gate
   reused."

### Question 2: GPL exposure / moddability

1. **CONFIRMED — the Dwarfeh_AI mod calls the real base-game function,
   not a reimplementation.** Read `Dwarfeh_AI_Spells.gpl`'s
   `Dwarfeh_AI_castRageOfKrolm` call site directly: it does
   `(spell's "castSpell")( palace )` where `spell` is an instance of the
   `Dwarfeh_AI_Spell` prototype created via `$CreateAgent
   ("Dwarfeh_AI_Rage_of_Krolm", "Dwarfeh_AI_Rage_of_Krolm")`. The
   `castSpell` function pointer for that named agent is set in the
   companion `.dat` file, `Dwarfeh_AI_Spells.dat`:
   `[Dwarfeh_AI_Rage_of_Krolm] { Dwarfeh_AI_Spell (title Rage_of_Krolm)
   (cost 1500) (canCast Dwarfeh_AI_canCast) (castSpell DoRageOfKrolm) }`
   — the literal value bound to `castSpell` is the bare name
   `DoRageOfKrolm`, which resolves to `Guild_Skills.gpl`'s real function
   (same file cited throughout this section, not a mod-local
   duplicate — the mod's own `.gpl` files contain no function named
   `DoRageOfKrolm`, confirmed by grep restricted to
   `PanelTest_Quest/MyAI/GPL/Dwarfeh_AI/`). So this is a genuine
   external call into the base game's real guild-skill function through
   GPL's function-pointer-as-data-field mechanism, not a look-alike.
2. **CONFIRMED: no base-game equivalent registry exists — the mod's
   pattern is a from-scratch invention, not mirroring a real base-game
   structure.** Grepped `SDK/OriginalQuests/GPL/prototype.gpl` (base) and
   its `GPLMx/mx_prototype.gpl` counterpart for every `prototype`
   declaration in the base game — 15 prototypes total (`AIRoot`, `hero`,
   `monster`, `RewardFlag`, `Lair`, `Tower_Lair`, `building`, `Outpost`,
   `Palace`, `Library`, `Fairgrounds`, `Guild`, `Dwarven_Settlement`,
   `GuardHouse`, `Tower`, `tax_collector`, `Caravan`, `Generic_Object`,
   `Resource`, `Special_Item`, `Spell`, `map_goodie`,
   `Parabolic_Missile`, `EventAgent`). One of these, `prototype Spell()`
   (`prototype.gpl` line 806), looked like a promising candidate by
   name — read in full: it declares only `type`/`subtype`/`title`/
   `birthscript`/`deathScript`/`activescript`/`IGDeathScript`, all
   explicitly commented as engine-plumbing placeholders ("not used, but
   attribute must exist for `$NewUnitInit()`/`$UnitDelete()`/
   `$Unit_Call_Deathscript()`") — **no `canCast`, no `cost`, no
   castSpell-equivalent field of any kind.** This is not a spell
   registry; it is the generic per-agent-type bookkeeping every
   prototype needs, reused for whatever `Spell`-typed agents the base
   game happens to instantiate. `prototype Guild()` was also read in
   full (the actual prototype `Temple_Krolm`/`Warriors_Guild` use) — it
   has `Lived_In_Script`/`Visited_Script`/`SpecialScript`/`members`/
   `member_title` etc., nothing resembling a skill list either. **No
   `.dat`-like file, prototype, or field anywhere in base `GPL`/`GPLMx`
   resembles a "spell/skill registry" with `canCast`/`cost` semantics.**
   The Dwarfeh_AI mod's own comment on `dwarfeh_prototype.gpl`
   ("Not all the spells were built in an easily accessible way for AI")
   is therefore accurate and precise, not just a plausible-sounding
   remark — it's the mod author independently reaching the same
   conclusion this grep confirms: the base game has zero callable-spell
   abstraction, and the mod's `canCast`/`castSpell` wrapper prototype was
   built to compensate for that absence, from scratch.
3. **Answer: hits the same "no confirmed data-only template" wall
   Petrify's research found — the two extra base-game examples do NOT
   give a more complete template, checked directly rather than assumed.**
   `DoRageOfKrolm`/`DoAssembly` are confirmed ordinary callable GPL
   functions (finding 1), which is a real, concrete difference from
   Petrify (where even `Petrify_Begin` itself had to be located by name
   rather than by any registry) — a modder CAN write a new plain GPL
   function of the same shape and call it from anywhere GPL can reach
   (e.g. a custom `ActiveScript`/thread/other building's function, the
   same way Dwarfeh_AI calls it). What remains blocked, identically to
   Petrify, is the **player-facing UI trigger**: there is no confirmed
   Action-XML-with-`GPLFunction`, `AllowedSpells`, `.dat` field, or any
   other data-only mechanism that makes a NEW function appear as a
   clickable button on a building's panel (`DialogID`-keyed panels are
   exe-hardcoded per `TODO-Ghidra.md`/§11's findings, and neither
   `Temple_Krolm`'s nor `Warriors_Guild`'s XML/`.dat` entries reference
   their `AP24`/`AP52` panel's button layout in any way — checked, not
   assumed). The `Sound`/`.dat` wiring that does exist for these two
   (`M_Sounds.xml` IDs `RM01` `Rage_of_Krolm`/`CM01` `Call_to_Arms`, the
   `$playsound` calls in each function, and the `Rage_Icon` overlay's
   real `GPLFunction="rage_end"` XML callback wiring) is **strictly
   better documentation of the ability's own visual/audio side-effects**
   than anything Petrify had — but it does not touch the missing piece
   (the panel button trigger), so it does not close the gap Petrify's
   research identified. **Net answer:** a modder can reuse
   `DoRageOfKrolm`/`DoAssembly` themselves (call them from new GPL code)
   with full confidence, and can build a new function of identical shape
   with full confidence — but making that new function player-triggerable
   from a building panel the way the original two are is UNVERIFIED/
   blocked by the same exe-hardcoded-panel wall as Petrify, not a solved
   problem just because two working examples exist.

- Exact exe/scheduler semantics of `$NewThread`/`$RunThread`/
  `$ResumeThread`/`$KillThread` (§1)
- Whether the exe truly calls `$building_upgraded`/`$DoMarketDay`/
  `$EndMarketDay` from real player actions — only comments are evidence
  (§2, §5)
- What sets a building's `#ATTRIB_isTaxed`/`#ATTRIB_QuickTax` gating flags
  (§5)
- Why several single/max-level buildings keep `upgradescript
  basic_upgrade` set with no reachable upgrade path (§2)
- Where the literal function `GuardHouse_Birth` is defined (referenced but
  not found in source) (§6)
- What research-purchase-button click dispatch actually looks like at the
  exe level (control_id ranges) — see `TODO-Ghidra.md` Priority 3.4 (§3)
- Whether every researchable item follows Magic Bazaar's confirmed
  gate-then-autonomous-purchase pattern — **RESOLVED for researchable
  items specifically:** yes, confirmed independently for Library
  (`Does_Library_Have_New_Wiz_Spell`/`..._Generic_Spell`) and Blacksmith
  (`Obtain_Upgrade`'s `#ATTRIB_ResearchArmorLevel_*`/`ResearchWeaponLevel_
  *` gates), in addition to the already-confirmed Bazaar. **Still open:**
  not every purchasable thing is researchable at all — Enchant_Equipment
  gates on building `Level` instead, and Fairgrounds/Poison_Weapons/
  Gardens/Inn have no unlock step of any kind (§3 continued)
- What exe-side UI/action calls `HallOfChampions_Bounty_Cost`/`Period` —
  **narrowed:** both functions are fully read now (cost 400/800 gold,
  period 60000/120000ms for bounty_index 1/2, a commented-out index-3
  tier exists as dead code in both), and confirmed to have zero call
  sites anywhere in the `.gpl` source tree — but their exe-side caller
  and whether a "bounty" ever manifests beyond these two lookups remains
  genuinely unknown (§3 continued)
- Whether a Mausoleum-interred hero remains reachable by `"Dead"`-type
  list queries (i.e. whether Reanimate/Resurrection can still target them)
  (§8)
- What numeric `cProc="8192"` resolves to on the engine side (§8)
- Whether the exe renders the AITX status-string lookup as a tooltip,
  icon, or something else (§7)
- Whether ImageIDBase is ever branched on directly by GPL code (as
  opposed to unit title/type)
- Whether stat redefinition via XML can conflict with hardcoded
  `#ATTRIB_*` threshold assumptions elsewhere in GPL
- Whether other building panels have the same per-panel-STRT-vs-general-
  GMTX text trap already confirmed for Marketplace/APa3 (see
  `CAM_MODDING_GUIDE.md`)

## 13. The Effector System, and Other Shared Primitives

§11 traced `$createeffector`/`$checkeffector` opportunistically, as a side
effect of re-verifying Petrify. This section treats the effector system as
its own topic — reading enough call sites across genuinely different
systems (building enchantment, hall-of-champions buff, hero-AI thought
bubbles, monster spell debuffs, quest-item markers) to confirm what's
general versus what's specific to Petrify — plus a deliberate sweep for
any other primitive that recurs across 3+ unrelated systems.

### 1. `$createeffector(agent, "name", duration, ...)` — mechanics

**Duration is confirmed in milliseconds**, not some other tick unit —
`Petrify_Begin` (`Spells.gpl`/`mx_Spells.gpl`) sets `time = 19000` and
calls `$createeffector(thisagent,"petrify_icon",time)`; the same file's
many `effector_duration`-driven attack spells (`acid_bolt`, `Pestilence`,
`horrify`, etc.) pull their duration from `$GetSpellAttribute(spellname,
"effector_duration")`, and that value traces directly to each spell's own
`<EffectorDuration value="..."/>` field in `M_Actions.xml`/`MX_Actions.xml`
(confirmed reading several: `acid_bolt` `EffectorDuration="1000"` at
`M_Actions.xml` line 214, paired with `TimeoutDuration="17000"` — the
same millisecond scale already confirmed elsewhere in this guide for
`TimeoutDuration`/`Sleep_for`/thread intervals, e.g. §4's `Sleep_for`
30000ms, §1's `#Normal_Cycle` 300ms). No separate "effector tick" unit
exists — it's the same millisecond timebase as everything else in GPL.

**Confirmed general, not Petrify-specific: the EFFECTOR'S OWN overlay XML
`<Script GPLFunction=...>` is what wires the expiry callback, not the GPL
call site.** Read 3 more real examples beyond Petrify, each a genuinely
different system:
- **Building enchantment** (`Tower.gpl`'s `DoWizTowerEnchant` — corrected
  from an earlier pass's `EnchantWizTower`, a real but DIFFERENT name,
  see below): creates `$createeffector(thisagent,"wiztower_enchantment",
  1, "Infinite")` (an "Infinite" duration, see below) and its own
  comment says "Infinite because the callback will destroy the
  effector." `M_Overlays.xml` ID `ARM1` `wiztower_enchantment` has NO
  `<Script>` tag — confirmed real, not a gap: this pairing is GPL-side,
  not overlay-XML-side. **`DoWizTowerEnchant` and `EndWizTowerEnchant`
  are BOTH engine-invoked, not GPL-called** — `DoWizTowerEnchant`
  carries the exact same "This is called by the ingame code" comment
  style already confirmed elsewhere in this guide for genuine engine
  entry points (§1/§2's `birthscript`, §8's `Generate_Character_
  Attributes`), and `EndWizTowerEnchant` has zero GPL call sites
  anywhere in the tree — consistent with being its paired engine-invoked
  "on-timeout" callback, not a missing/broken wiring. **`$EnchantWizTower`
  is a SEPARATE real engine primitive** (confirmed in the Notepad++
  Keywords4 list), used directly by quest scripts (`epic_quest_
  scripts.gpl`: `If ($RandomNumber(100) >= 50) $EnchantWizTower(Tower)`)
  — the earlier pass's citation of "`EnchantWizTower`" conflated this
  primitive's name with the GPL function `DoWizTowerEnchant` it
  presumably triggers internally; they are two different, real, both-
  confirmed-to-exist things, not one thing cited under the wrong name.
  This building-enchantment status effect is a genuine THIRD trigger
  class beyond Petrify's building-panel-button and Champions_Vigor's
  GPL-callable-function shapes: **quest-script/engine-primitive
  triggered**, with both its start and end GPL hooks being engine-
  invoked rather than GPL-called — no UNVERIFIED gap remains here, this
  is a fully-traced, just differently-shaped mechanism.
- **Hall of Champions buff** (`mx_Spells.gpl`'s `Champions_Vigor_Begin`/
  `_End`): `$createeffector(thisagent,"Champions_Vigor_icon", 90000)` —
  and here `MX_Overlays.xml` ID `XR57` `Champions_Vigor_Icon` DOES have
  `<Script type="0" cProc="0" GPLFunction="Champions_Vigor_End"/>`
  (confirmed, lines 829-840), the same wiring shape as Petrify's
  `petrify_icon`→`Petrify_End`. Two-overlay split confirmed too:
  `Champions_Vigor_effector` (visible, duration 0, no script — the
  permanent-until-manually-removed visual) + `Champions_Vigor_icon`
  (duration 90000, has the script — the timer).
- **Turn Undead** (`mx_Spells.gpl`'s `turn_undead_hit`): `MX_Overlays.xml`
  ID `XR67` `turn_undead_eff` has `<Script GPLFunction="turn_undead_hit"/>`
  — but note this is a self-referential wiring (the overlay's own name
  IS the damage-application function, not a separate "_End" cleanup
  function), confirming the callback mechanism is generic (whatever
  function name the XML names gets called), not tied to any "_Begin"/
  "_End" naming convention — that convention is just what most base-game
  spells happen to use, not something the engine enforces.

**Confirmed: `$createeffector` with `duration=0` (like `petrify_effector`)
means "permanent until manually removed," not "instant/no-op."** Every
zero-duration effector examined (`petrify_effector`, `Champions_Vigor_
effector`, `Strength_potion_effector`, `Meditation_effector`, `fire_
shield_effector`, `monk_stone_skin_effector`, `Damage_Shield_Effector`,
etc. — all in `mx_Spells.gpl`) is a VISUAL-only overlay with no `<Script>`
in its XML entry, always paired with a second, non-zero-duration
"_icon"/timer effector on the same agent that DOES carry the callback.
The zero-duration visual is removed explicitly by the callback function
(e.g. `Petrify_End` doesn't call `$deleteeffector` on `petrify_effector`
at all — instead `$GetProperUnitArt(thisagent)` recomputes which overlay
should be showing based on current attribute flags; this differs by
spell, not a single universal cleanup call — UNVERIFIED whether
`$GetProperUnitArt` implicitly clears stale zero-duration effectors or
whether some other zero-duration effectors leak until `$DeleteEffector`
is called explicitly elsewhere, e.g. `Reset_Controlled.gpl`'s explicit
`$deleteEffector(thisagent,"charm_icon")` on an effector that in other
call sites is created with a real timeout).

**A third duration form exists beyond a plain integer: the string
literal `"Infinite"`, and separately a 4th positional argument.**
`EnchantWizTower`'s `$createeffector(thisagent,"wiztower_enchantment", 1,
"Infinite")` and `Inventory.gpl`'s `$CreateEffector(ThisAgent, "Ring_
Icon", 1, "Infinite")` and `WrathOfKrolm.gpl`'s `$CreateEffector(
ThisAgent, "Perm_Rage_Icon", 1, "infinite")` all pass duration `1` (not
`0`) plus the string `"Infinite"`/`"infinite"` as a 4th argument — a
different permanence mechanism from the plain `duration=0` case above,
and case-INconsistent across call sites (`"Infinite"` vs `"infinite"`),
suggesting the engine does a case-insensitive string match rather than
requiring an exact literal. Separately, `mx_Monster_Deaths.gpl`'s
`give_gold` does `$createeffector(thisagent,"got_gold",0, Amount)` where
`Amount` is a plain integer (the gold value to display on the floating
overlay text) — a 4th argument with completely different semantics
(a display value, not a duration modifier) depending on which overlay is
being created. **UNVERIFIED**: whether the 4th argument's meaning is
effector-specific (i.e. the engine dispatches on the overlay name) or
positionally overloaded by argument type — no GPL-side documentation of
`$createeffector`'s full signature exists beyond these observed call
shapes.

### 2. `$checkeffector(agent, "name")` — confirmed simple boolean presence check, with one surprising non-visual use

Read `Hall_Champs_Check.gpl` (`If ($CheckEffector (ThisAgent,
"Champions_Vigor_Icon")) return False` — skip re-visiting if the buff
icon is already present), `mx_flee.gpl` (`if ($CheckEffector (ThisAgent,
"Speed_Tonic_Icon") == False) return 1` — flee-decision gate), and
`LowLevel.gpl`'s `IsFrozen` (already cited in §11: ORs together 4 separate
`$CheckEffector` calls — `petrify_icon`, `vines_effector`, `Level_Leach_
Effector`, `paralytic_gaze_icon` — as a shared "freeze lock" check). All
three confirm: it's a plain boolean presence test, no side effects, no
duration/remaining-time info returned.

**Surprising non-visual usage, confirmed as a real pattern, not a single
outlier:** `Check_Champion_Rewards.gpl` and `mx_Combat_wandering.gpl`
(two independent hero/monster decision-tree modules) both use
`$CheckEffector(Monster, "Champion_Icon")` purely as a **generic
marker/flag** — "has this monster been tagged as a champion reward" —
with no relation to a visual status-effect timer at all. `Champion_Icon`
(`MX_Overlays.xml` ID `XR26`) does render an on-screen icon, so it's not
PURELY invisible plumbing, but the GPL code reading it treats it exactly
like a boolean tag/marker on the agent, not a "buff is active" check —
confirming `$checkeffector`/`$createeffector` together function as a
general-purpose per-agent boolean-flag-with-optional-visual system, not
a status-effect-only mechanism. (`Rage_Icon` is used the same
marker-like way in `Building_Births.gpl`'s stray-hero-adoption cleanup:
`If ($CheckEffector (Stray, "Rage_Icon")) $DeleteEffector (Stray,
"Rage_Icon")` — checking/clearing a marker before the stray hero changes
ownership, unrelated to whether Rage's buff timer has any gameplay
relevance at that moment.)

### 3. Early removal: `$DeleteEffector`/`$deleteeffector` confirmed real and commonly used

Real call sites across unrelated systems, all confirmed: `make_attack.gpl`
(`$DeleteEffector(thisagent,"camouflage_icon")` — attacking breaks
camouflage early, before its timer would naturally expire), `Reset_
Controlled.gpl` (`$deleteEffector(thisagent,"charm_icon")` — control
ends early on death/reset), `mx_Tower.gpl`'s `EndWizTowerEnchant`
(removes the permanent `wiztower_enchantment` visual), `Quest_Actives.gpl`
(`$DeleteEffector(ThisAgent, "Ring_Icon")` on item loss — removing a
duration `1`/`"Infinite"` marker effector), and `mx_Heal.gpl` (`$Delete
Effector(target, "Ratman_Plague_Icon")` — a heal that isn't a full-potion
heal cures the plague status by deleting its effector directly, bypassing
whatever "_End" callback would otherwise fire on natural expiry). This
last case confirms early removal via `$DeleteEffector` does NOT
necessarily invoke the effector's own `<Script GPLFunction>` callback —
`mx_Heal.gpl` has no companion call to a plague-end function immediately
after, meaning the calling code is expected to independently undo
whatever the plague's own callback would have undone (UNVERIFIED whether
the engine ever fires the callback on manual delete vs. only on natural
timeout — no case was found where `$DeleteEffector` was immediately
followed by a manual call to that effector's own callback function,
which would suggest the callback ISN'T auto-fired on manual delete and
the calling code must duplicate its cleanup logic by hand).

**CORRECTION:** `$DeleteAllEffectors` was originally claimed to have zero
call sites — wrong, a real one exists: `GPLMx/mx_Hero_Deaths.gpl` line
110 calls `$DeleteAllEffectors(thisagent)` directly in a hero's death
path, flagged by its own author's alarmed inline comment ("TODO: REVIEW
THE ADDITION OF THIS LINE! IT REPRESENTS A MAJOR LOW LEVEL CHANGE WITH
POTENTIALLY SEVERE REPERCUSSIONS!!!") — a genuine, deliberate, if
nervously-added, bulk-cleanup call confirming the primitive IS used to
strip every active effector from a dying hero in the expansion's death
handling. **Confirmed expansion-only:** the base game's `GPL/Hero_Deaths.gpl` has
NO equivalent call — grepped directly, zero matches — so this is a real
Majesty Gold expansion-specific addition to hero death cleanup, not
present in the original game at all. The underlying "what does it do
beyond bulk-remove" question remains unverified (no primitive definition
exists to read), but "the base game never exercises it" is now confirmed
true for the BASE game specifically, while the earlier "zero call sites
anywhere" claim is confirmed false once the expansion is included.

### 4. Is "effector" separable from "overlay" — can one exist as a pure timer with no visual and no callback?

**Confirmed yes — attack-hit "flash" effectors are the clearest example,
and they're a large, common category, not an edge case.** Every
zero-duration attack-impact effector checked (`acid_bolt_effector`
`M_Overlays.xml` ID `NRa2`, `energy_blast_effector` ID `WRa1`,
`electrical_fury_effector` ID `NRb2`, `insect_swarm_effector` ID `NRg2` —
4 read in full) has an overlay XML entry with **no `<Script>` tag** and
is created with a real `effector_duration` (not 0) pulled from
`$GetSpellAttribute`. These ARE visible (they have real `ImageIDBase`
sprite art — the visual flash of the spell hitting) but have no callback
of any kind: the timer just expires and the overlay disappears on its
own with no GPL function ever running. This confirms overlay-visual and
callback-wiring are two INDEPENDENT XML-level choices, not coupled —
you can have (a) visual + callback (`petrify_icon`, `Champions_Vigor_
Icon`), (b) visual + no callback (every attack-hit flash above,
`petrify_effector`/`Champions_Vigor_effector` themselves), or by
implication (c) no visual + callback, though **no confirmed example of
(c) was found** — every effector with a `<Script>` tag examined across
both `M_Overlays.xml` and `MX_Overlays.xml` also has real sprite-adjacent
fields (`ImageIDBase`, `Info value="Directionless"`, etc.), so whether a
GPL modder could register a purely-invisible timer-with-callback effector
(no overlay art at all) by omitting `ImageIDBase` is **UNVERIFIED** —
not found either confirmed or denied in source; would need an in-game
test with a deliberately image-less overlay entry.

**No effector name was found with a `$createeffector`/`$checkeffector`
GPL call site but NO corresponding overlay XML entry in either
`M_Overlays.xml` or `MX_Overlays.xml`** — spot-checked every effector
name cited in this section (`wiztower_enchantment`, `Champions_Vigor_
icon`/`_effector`, `turn_undead_eff`, `got_gold_bldg`, `Ring_Icon`,
`Champion_Icon`, `Rage_Icon`, `charm_icon`, `cursed_icon`, `camouflage_
icon`) against the XML files directly — all present. This matches the
project's existing pre-flight-validation rule (`.kiro/steering/majesty-
modding.md`'s "Effector name consistency" check) rather than
contradicting it: every real base-game effector name IS backed by an
overlay entry, consistent with the engine likely requiring one to even
create the effector successfully (UNVERIFIED — no crash/rejection
behavior for a missing overlay entry was observed in source, since no
such case exists in the base game to observe).

### 5. The general pattern, confirmed across multiple systems (not just Petrify)

`.kiro/steering/majesty-modding.md`'s status-effect template ("a visible
overlay + an invisible timer effector") **generalizes, confirmed by 3
independent real examples beyond Petrify**, though the exact shape
varies more than the template implies:

- **Champions_Vigor** (Hall of Champions buff): exactly Petrify's shape —
  `Champions_Vigor_effector` (visible, duration 0, no script) +
  `Champions_Vigor_icon` (duration 90000, has `GPLFunction="Champions_
  Vigor_End"`). Closest 1:1 match to the template.
- **Wizard Tower enchantment**: only ONE overlay total
  (`wiztower_enchantment`, duration `1`/`"Infinite"`), no separate
  invisible timer effector at all — the "timer" here is a real GPL
  `ActiveScript` thread (`$Wiz_Tower_Scan`/`$Wiz_Tower_Attack`) started
  alongside the effector, and cleanup (`EndWizTowerEnchant`) is called
  from somewhere outside the effector-callback system entirely (§13.1
  finding: no `<Script>` tag on this overlay). **This is a real
  counter-example to "always 2 effectors"** — the two-effector split is
  common but not universal; a single permanent visual effector paired
  with an ordinary thread-based timer is an equally valid alternative
  shape, confirmed real in the base game, not a hypothetical variant.
- **Attack-hit flashes** (`acid_bolt`, `energy_blast`, etc.): the
  INVERSE split — a single effector that's both visible AND timed, with
  no callback and no companion invisible effector at all, because
  nothing needs to happen when a damage-flash overlay naturally expires
  (the damage was already applied synchronously via `$spell_attack` in
  the same function). Confirms the 2-effector pattern is specifically
  for STATUS EFFECTS that need an explicit start/end state transition
  (freeze, buff, debuff), not a general effector-usage requirement.

**Practical modding takeaway, updated from the steering doc's original
single-example template:** the visible+invisible pairing is the right
default for a NEW status effect that needs a clean start/end transition
(matches Petrify and Champions_Vigor exactly), but it is not the only
valid shape — a one-shot visual-only flash (no companion effector, no
callback) or a permanent visual paired with an ordinary `ActiveScript`
thread (Wizard Tower's shape) are both real, precedented alternatives
depending on whether the effect needs a callback-driven end state at
all.

## 14. Cross-System Primitive Sweep

§13 covered the effector family (`$createeffector`/`$checkeffector`/
`$deleteeffector`/`$deleteAllEffectors`) as its own topic. This section is
the deliberate sweep promised there: candidates were compiled from the
Notepad++ GPL keyword file's `Keywords3`/`Keywords4` blocks (`SDK/Extras/
GPL User Define Language template for Notepad++.xml`) and checked against
what §1-§13 already trace in depth, then grepped for real call sites
across the full `.gpl` tree (`GPL/` + `GPLMx/`, plus mod-side `.gpl` files
that call the same base-game primitives). Only primitives with call sites
in 3+ genuinely unrelated systems are written up below; everything else
is listed as discarded with the reason.

### 1. `$ListObjects` — full parameter/flag semantics

**The flag arguments are not opaque engine magic — `GPL/LowLevel.gpl`
and `GPLMx/mx_LowLevel.gpl` both declare them as ordinary GPL
`expression` constants with real numeric values**, in a shared comment
block titled `Search functions :` (`GPL/LowLevel.gpl` lines 1553-1564,
`GPLMx/mx_LowLevel.gpl` lines 1682-1693, byte-identical in both):

```
expression   #NoHiddenMap          0
expression   #MyPlayer             1
expression   #NotMyPlayer          2
expression   #MyTeam               3
expression   #NotMyTeam            4
expression   #InsideOtherUnits     5
expression   #RewardFlags          6
expression   #CheckTitles          7
expression   #CheckSubtypes        8
expression   #FindFirstMatchOnly   9
```

This confirms two things beyond what scattered prior sections implied:
(a) these are plain integer constants, not bitflags — `#MyPlayer`==1 and
`#NotMyPlayer`==2 are mutually exclusive values, not bit 0 vs bit 1, so
passing both in the same call is meaningless rather than a valid
combination; (b) `#CheckTitles`/`#CheckSubtypes`/`#RewardFlags` are
**paired markers, not standalone flags** — each is always immediately
followed by its own extra argument in every real call site read
(`#CheckTitles, "Magic_Bazaar"`, `#CheckSubtypes, "Hero"`, `#RewardFlags`
paired with `#MyPlayer` in `check_rewards.gpl`'s
`$ListObjects(thisagent, "RewardFlag", -1, flags, #RewardFlags)` — here
`#RewardFlags` has no trailing string because the type-string argument
itself, `"RewardFlag"`, already does that job; other call sites like
`mx_Building_Deaths.gpl`'s `$listobjects(thisagent,"rewardFlag",-1,units,
#rewardflags,#Myplayer,#NoHiddenMap)` pass `#RewardFlags` alongside
`#MyPlayer`/`#NoHiddenMap` with no extra positional argument at all,
confirming `#RewardFlags` itself takes no parameter — it's a pure
type-filter flag, unlike `#CheckTitles`/`#CheckSubtypes` which always
consume the next argument as their match string).

**Confirmed call shape:** `$ListObjects(SearchOrigin, TypeString, Range,
OutputList, [flag [, flagArg]]...)` — `SearchOrigin` is any agent (not
just heroes/AI roots: buildings, palaces, monsters, even spell-target
victims all appear as the first argument across real call sites read),
`TypeString` is a bare unquoted-in-spirit string literal
(`"building"`/`"hero"`/`"monster"`/`"lair"`/`"dead"`/`"RewardFlag"`/
`"spell"`/`"invisible"`/`"camouflaged"`/`"color"`/`"special_item"`/
`"AutoBuilding"` all confirmed as real type strings across
`Guild_Skills.gpl`, `check_rewards.gpl`, `custom_rules.gpl`,
`mx_Epic_Quest_Scripts.gpl`), `Range` is a search radius in the same
coordinate units as `$DistanceBetweenAgents`, and **`-1` means unlimited
range** (confirmed by the overwhelming majority of call sites passing
`-1` when combined with `#NoHiddenMap`/`#MyPlayer`-style whole-map
filters, vs. small positive integers like `160`/`700`/`800` when doing
a genuine local proximity search, e.g. `mx_Spells.gpl`'s
`$ListObjects(ThisAgent, "hero", 160, Heroes, #MyPlayer, #CheckSubtypes,
"Hero")`).

**Return value: `$ListObjects` returns the resulting list size as an
integer, not the list itself — the list is written into the 4th
argument (an out-parameter), and the function's own return value is
usable directly in comparisons.** Confirmed by two different usage
styles for the exact same call, both real: some call sites ignore the
return value entirely (`$ListObjects (ThisAgent, "Building", -1,
Buildings, #MyPlayer);` as a bare statement, `Guild_Skills.gpl`) while
others capture it (`ListSize = $ListObjects (ThisAgent, "Building", -1,
targets, #NotMyPlayer, #CheckSubtypes, "Guild");`,
`mx_Spells.gpl`/`Quests_3.gpl`) or use it inline in a condition
(`If ($ListObjects (ThisAgent, "spell", -1, Gates, #FindFirstMatchOnly,
#MyPlayer) > 0)`, `mx_Spells.gpl`). This is a genuinely useful modding
fact not obvious from the keyword list alone or from any single call
site in isolation — a modder can skip the `$ListSize` follow-up call
entirely when only the count is needed.

**`#FindFirstMatchOnly` is a real, distinct optimization flag, not a
synonym for "return only 1 result" via `Range`.** Confirmed via
`mx_Spells.gpl`'s `$ListObjects (ThisAgent, "Building", -1, Abodes,
#CheckTitles, "SorcerersAbode", #FindFirstMatchOnly, #NoHiddenMap,
#MyPlayer)` — combined with `-1` (unlimited range) and a `#CheckTitles`
filter, meaning it's specifically an early-exit-on-first-match
optimization over an otherwise whole-map search, not a range restriction.
Only 2 call sites found using it (both in `mx_Spells.gpl`) — below the
3-unrelated-system bar on its own, but it's documented here as part of
`$ListObjects`'s general flag vocabulary rather than as its own entry.

**Confirmed across 3+ unrelated systems (building-birth logic, hero-AI
decision trees, monster/spell targeting, quest-rules event scripts, the
Dwarfeh_AI custom mod) — this primitive is the single most call-site-
dense primitive in the entire `.gpl` tree**, easily exceeding the 3-
unrelated-system bar by a wide margin (hundreds of call sites across
`Guild_Skills.gpl`, `check_rewards.gpl`, `mx_Building_Births/Deaths.gpl`,
`mx_Spells.gpl`, `mx_LowLevel.gpl`, `custom_rules.gpl`, and many more).

### 2. `$AdjustAttribute` vs `$MagicalAdjustAttribute` — confirmed real, cosmetic-only difference

**Confirmed by explicit source comments in 2 independent files, not
inferred:** `Guild_Skills.gpl`'s `DoRageOfKrolm` comments
"Magically adjust attribs so that they appear a diff color on the stats
window" immediately above a block of `$MagicalAdjustAttribute` calls, and
its cleanup function `EndRageOfKrolm` repeats the same comment
("Use MagicalAdjustAttrib so that the color-changing stats window deltas
are accurate") above the matching negative-delta calls. **Both functions
call `$AdjustAttribute` for some stats (`#ATTRIB_MaxHP`, `#ATTRIB_HP`,
`#ATTRIB_MovementRateModifier`) and `$MagicalAdjustAttribute` for others
(`#ATTRIB_Strength`, `#ATTRIB_HtoH`, `#ATTRIB_Dodge`, `#ATTRIB_Parry`) in
the SAME function, on the SAME hero, for the SAME buff** — confirming
the choice between the two is a per-stat display decision made by the
spell's author, not a difference in what kind of buff is being applied
or how long it lasts. The same split pattern repeats in `mx_Spells.gpl`
across genuinely unrelated buffs/debuffs — `Ratman_Plague` (a monster-
inflicted hero debuff: `$MagicalAdjustAttribute` for `#ATTRIB_Strength`/
`#ATTRIB_Parry`/`#ATTRIB_Dodge`, plain `$AdjustAttribute` for
`#ATTRIB_MovementRateModifier`/`#ATTRIB_ActionRateModifier`/
`#ATTRIB_HealingRateModifier`), `Wither` (`Random_Events.gpl`, a random
quest event debuff: `$MagicalAdjustAttribute` for `#ATTRIB_strength`,
plain `$AdjustAttribute` for the two rate modifiers), `Blessing`/
`Vigilance`/`Strength_Potion`/monster transformation spells (Dryad/
Medusa/Minotaur shapeshifts) — in every case, core combat/mental stats
(`Strength`, `HtoH`, `Dodge`, `Parry`, `Intelligence`, `Vitality`,
`WillPower`, `Magicresistance`) go through `$MagicalAdjustAttribute`,
while HP/movement-rate/action-rate/healing-rate modifiers consistently
go through plain `$AdjustAttribute`. **This is a real, consistent
authoring convention across the entire base game and the Dwarfeh_AI mod
(same split reproduced verbatim in `mx_Spells.gpl`'s AI-mod copy) — not
a hard engine rule** (no GPL-side validation prevents mixing them up),
but a modder adding a new stat-boosting status effect should follow the
same convention: use `$MagicalAdjustAttribute` for the stats shown with
colored deltas in the hero stats window (str/dodge/parry/htoh/ranged/
intelligence/willpower/vitality/artifice/magicresistance), plain
`$AdjustAttribute` for everything else (HP, movement/action/healing rate
modifiers, armor/weapon basic damage). **UNVERIFIED**: no GPL-side
definition of either primitive exists to confirm mechanically what the
"Magical" variant does differently at the engine level beyond the stats-
window color-coding the comments describe — this is inferred entirely
from consistent real-world usage, not from a primitive definition.

Confirmed across 3+ unrelated systems: guild-skill buffs (`Guild_
Skills.gpl`'s Rage of Krolm), monster-attack debuffs (`mx_Spells.gpl`'s
Ratman Plague, Medusa Slow), quest-event debuffs (`Random_Events.gpl`'s
Wither), and building-upgrade HP grants (`custom_rules.gpl`'s AI-mod
palace/building level-ups, which use only plain `$AdjustAttribute` for
`#ATTRIB_MAXHP` — consistent with the "HP is never Magical" half of the
convention holding even in a completely different, non-spell context).

### 3. `$PerformAction` — confirmed generic "play this Action-XML entry as a one-shot animation/effect" primitive, not attack-specific

**Confirmed shape:** `$PerformAction(Agent, "ActionName", Target)` —
`ActionName` is a bare string matching a `Description type="Action"
... Name="..."` entry in `M_Actions.xml`/`MX_Actions.xml` (confirmed:
`"Guardhouse_Arrow"` → `M_Actions.xml` ID `AXA6` `Name="Guardhouse_
Arrow"`; `"Basic_death"` → ID `A005`; `"Become_Rubble"` → ID `A009` —
all 3 read in full and confirmed to exist with matching `Name=`
attributes, not GPL-side function names). `Target` is usually the same
agent as `Agent` itself (self-targeted animation, e.g. `$performaction
(thisagent,"basic_death",thisagent)`) but can be a different agent for
directed effects (`$PerformAction (ThisAgent, "Guardhouse_Arrow",
ThisAgent's "Target")` — a guardhouse firing at an intruder,
`mx_Building_Guard.gpl`).

**Confirmed NOT attack-specific — used for death animations, building
crumble effects, and generic movement/idle actions across unrelated
systems**, not just combat: `Hero_Deaths.gpl`/`mx_Hero_Deaths.gpl`
(`"basic_death"`, `"henchman_death"`, `"Knockout"`, `"Standup"` — hero
death/unconsciousness/revival animations), `Monster_Deaths.gpl`/
`mx_Monster_Deaths.gpl` (`"basic_death"` again, confirming it's a shared
Action entry usable by both heroes and monsters, not a hero-only or
monster-only animation), `custom_rules.gpl`/`mx_LowLevel.gpl`
(`"Become_Rubble"` on building death — a completely different subsystem,
buildings not characters), and `Quests_1.gpl`/`Quests_3.gpl`/`mx_Building_
Guard.gpl` (`$PerformAction(ThisAgent, ThisAgent's "Attack_Action",
Target)` / `ThisAgent's "Idle_action"` — here the action NAME itself is
a per-agent attribute lookup, not a hardcoded literal, confirming attack/
idle animations are just data-driven Action-XML names stored on the
agent, dispatched through the exact same generic primitive as death/
building-crumble effects).

**One real inconsistency found, not resolved:** `LowLevel.gpl`/
`mx_LowLevel.gpl`/`Monster_Deaths.gpl`/`mx_Monster_Deaths.gpl` all have a
commented-out `//$PerformAction (ThisBuilding, "Got_Gold_Bldg",
ThisBuilding)` / `//$performaction(thisagent,"got_gold_bldg",thisagent)`
immediately above a real, active `$CreateEffector(...,"got_gold_bldg",
0, Amount)` call — meaning the original author considered
`$PerformAction` as an alternative to the effector system for this
specific "show a floating gold-amount popup" effect and rejected it in
favor of `$CreateEffector`, in every one of the (at least 4) places this
pattern appears. **UNVERIFIED** why — no comment explains the choice,
and no `Got_Gold_Bldg`-equivalent Action-XML entry with a floating-text
capability was checked to confirm whether `$PerformAction` could even
support the `Amount` display value the effector's 4th argument uses (see
§13.1) — plausibly `$PerformAction` has no equivalent of an effector's
extra display-value argument, which would fully explain the rejection,
but this is inferred, not confirmed from a primitive definition.

Confirmed across 3+ unrelated systems: hero death/state-transition
animations, monster death animations, building destruction, and hero/
monster attack-and-idle dispatch (4 distinct subsystems, well past the
bar).

### 4. `$RandomNumber`/`$RandomCoord` — confirmed inclusive-range convention, universal `+1` idiom

**`$RandomNumber(N)` is confirmed to return a value in `[0, N-1]` (or
possibly `[0, N]`), not `[1, N]`** — inferred from an extremely
consistent idiom repeated at hundreds of call sites across every system
that uses it: **`$RandomNumber(100) + 1` used as a percent-chance roll
compared against a 1-100 threshold** (`mx_Purchase_Equipment.gpl`'s
`ThisAgent's "Upgrade_Weapon_Chance" > $RandomNumber (100) + 1`,
`Magic_Bazaar.gpl`'s `bazaar_chance > $RandomNumber ( 100 ) + 1`,
`Zoo.gpl`'s `( $RandomNumber ( 100 ) + 1 ) < charm_percentage`,
`custom_rules.gpl`'s dozens of `$RandomNumber ( 2 ) + 1` /
`$RandomNumber ( 3 ) + 1` "randomly choose 1-2"/"1-3" comments). The
universality of the `+ 1` across every single roll-a-percentage or
roll-a-choice call site in the entire tree — with zero counter-examples
found of a bare `$RandomNumber(100)` being compared against a 1-100
scale without the `+1` — confirms `$RandomNumber(N)` alone would produce
a 0-based result that needs the `+1` to reach a 1-based range; if `N`
were already inclusive of both endpoints starting at 1, the `+1` idiom
would systematically bias every roll in the entire codebase, which is
implausible for a shipped game. **UNVERIFIED** whether the true range is
`[0,N-1]` or `[0,N]` — both are consistent with the `+1` idiom, and no
primitive definition was found to disambiguate; this refines but does
not fully resolve the steering doc's existing "need verification" note
on GPL duration ticks (a related but distinct question about `$createeffector`
timing, not `$RandomNumber`'s range).

**`$RandomCoord(agent, minDist, maxDist)` and the 2-argument form
`$RandomCoord(agent, dist)` are confirmed as two distinct real call
shapes, not a single optional-argument signature guess** —
`custom_rules.gpl`'s `$RandomCoord( palace, distance, (distance + 600))`
(min/max band) vs. `mx_LowLevel.gpl`'s `$RandomCoord (Palace, -1)` (single
distance argument, `-1` meaning unlimited/anywhere-on-map, the same `-1`-
means-unbounded convention confirmed for `$ListObjects`'s `Range`
argument above) vs. `mx_Building_Deaths.gpl`'s `$randomcoord(coord,300)`
(single positive distance, meaning "within 300 units of `coord`" as a
max with an implicit 0 minimum). All 3 shapes are real and coexist across
the same file family, confirming the primitive accepts either 2 or 3
arguments depending on whether a minimum exclusion radius is needed.

Confirmed across 3+ unrelated systems for `$RandomNumber`: building-visit
hero-AI decision trees (`mx_Purchase_Equipment.gpl`), a completely
different building's charm mechanic (`Zoo.gpl`), and whole-game AI-mod
building/temple selection logic (`custom_rules.gpl`) — plus quest-rules
monster spawning (`mx_Demo.gpl`, `mx_Epic_Quest_Scripts.gpl`) for
`$RandomCoord` specifically (building deaths spawning spiders, quest
scripts placing signs/caravans, cheat/demo monster-wave spawners).

### 5. `$NewThread`/`$RunThread`/`$RunThreadOnce` — confirmed real distinctions between the three, still no engine-internals confirmation

**Genuinely new finding beyond §1's original `$NewThread` coverage:**
`$RunThread` and `$RunThreadOnce` are NOT just alternate names for
`$NewThread` — real call sites show a confirmed distinction. `$NewThread`
is used for primary, ongoing per-agent tick loops that a function
reassigns to itself as a persistent field (`ActiveScript`/`Guard_
Function`/etc., §1's existing finding, re-confirmed). `$RunThread` is
used for **secondary, often one-off or conditionally-guarded threads**
layered on top of an agent that already has its own `$NewThread`-driven
main loop — e.g. `Building_Births.gpl`'s Palace birth calls `$NewThread`
once for the palace's own revenue-cycle `ActiveScript`, then separately
`$RunThread`s 3 more helper threads (`Guard_Spawn_Function`/`Tax_spawn`/
`peasant_spawn`) on the SAME agent in the SAME function — confirming an
agent can have multiple independent named thread slots running
concurrently, not just one `ActiveScript`. The pattern
`If ($isrunning(X) == False) $runthread(X, ...)` (`Building_Guard.gpl`,
`Building_Deaths.gpl`, `Hero_Deaths.gpl` — 3 unrelated systems) further
confirms `$RunThread` is commonly guarded against double-starting a
thread that might already be running, a concern that wouldn't arise if
`$RunThread` behaved identically to `$NewThread`'s unconditional
(re)registration. **`$RunThreadOnce`** has far fewer call sites (only
found in the Dwarfeh_AI custom mod's `custom_rules.gpl`,
`$RunThreadOnce(AIRootAgent's "player2AI", (1000))`) — below the 3-
unrelated-system bar on its own, so not written up beyond this note;
its name strongly implies "run once, do not reschedule," consistent with
being the natural complement to `$NewThread`'s repeating-timer semantics,
but this is a naming inference, not a confirmed behavioral difference —
**UNVERIFIED**.

This does not resolve the existing `TODO-GPL-Deepdive.md`/§1 UNVERIFIED
item about the true engine-side scheduler semantics (real coroutine vs.
callback timer table) — it only confirms that `$NewThread` vs `$RunThread`
is a real, intentional distinction at the GPL call-site level (primary
loop vs. secondary/guardable helper thread), which was not previously
documented anywhere in this guide.

Confirmed across 3+ unrelated systems: building birth/upgrade logic
(`Building_Births.gpl`'s Palace, Guard_House, Tax_spawner threads),
hero death/gravestone timers (`Hero_Deaths.gpl`'s tax/peasant thread
resumption), and monster/lair respawn timers (`Building_Deaths.gpl`'s
`$RunThread (ThisAgent's "ActiveScript", $RandomNumber (30000) +
400000, ThisAgent)` lair respawn).

### 6. Float arithmetic is unreliable, and the compiler's constant folding defeats the obvious workaround

**This is a language/runtime-level gotcha, not a primitive, and it is the
only entry in this section sourced from a modder's field experience
rather than from shipped Majesty source.** Recorded because it silently
produces wrong numbers rather than failing loudly, and because the
workaround is non-obvious.

**Source:** the `Dwarfeh_AI` mod's `custom_rules.gpl` (in this repo, e.g.
`PanelTest_Quest/MyAI/GPL/custom_rules.gpl`), in the comment block above
`getBuildingCostMultiplier`, plus the split-function structure that
comment exists to explain. Reported directly by that mod's author.
**Provenance caveat, stated because it matters:** the author notes this
was a pragmatic solution arrived at without documentation or guidance —
it is a reliable account of *what broke and what worked*, not a claim
about the engine's internals, and a cleaner mechanism may exist.

Three claims, in the order they bite:

1. **Multiplying by a float literal does not work.** `100 * 1.5`
   produces a wrong result. `100 * 3 / 2` produces the right one. The
   author's phrasing: "you can't multiply by floats... `100 * 1.5` is
   bad, but `100 * 3 / 2` is good."
2. **The compiler constant-folds `3 / 2` into `1.5`.** So you cannot
   move the ratio into a helper — `return 3 / 2;` from a `is float`
   function compiles to `return 1.5;`, which lands you straight back in
   problem 1.
3. **Therefore the numerator and denominator must be kept separate all
   the way to the call site**, as two operations. The mod does exactly
   this with a `getBuildingCostMultiplier()` / `getBuildingCostDivisor()`
   pair applied as `x * mult / div` inline, never as a single
   pre-divided factor.

**Worked example from that mod** (its per-copy building cost escalation,
reproducing the XML `<Multiplier>` values as exact rationals): Magic
Bazaar `3.0 / 2.0` = 1.5, Embassy `7.0 / 2.0` = 3.5, Guardhouse
`2.5 / 2.0` = 1.25, Inn `5.5 / 5.0` = 1.1, Blacksmith/Library
`1.0 / 1.0` = 1.0.

**A second, unrelated hazard from the same function, worth its own
line:** the mod guards every multiply against exceeding a hardcoded
`400000.0` ceiling, with the comment "if we go above MAX_INT game
crashes without error." So **integer/float overflow in GPL arithmetic is
a silent-crash class, not an exception** — clamp before multiplying in
any compounding loop.

**UNVERIFIED, deliberately:** the precise rule behind claim 1 (whether
it is a parser issue, a bytecode-emission issue, a `float`-vs-`integer`
coercion issue, or specific to certain operand types) is not established
— only the observed behavior and the working workaround. Do not
generalise it into "GPL has no floats": `is float` return types,
`float` declarations and float literals all clearly exist and the
divisor functions return them.

### Candidates checked and discarded (fewer than 3 unrelated systems)

- **`$FindFirstMatchOnly`** — real, but only 2 call sites, both in
  `mx_Spells.gpl` (see §14.1 above, folded into the `$ListObjects` entry
  rather than discarded outright since it's a flag of an already-
  qualifying primitive).
- **`$RunThreadOnce`** — only 1 call site found (Dwarfeh_AI mod's
  `custom_rules.gpl`), noted above but not separately written up.
- **`$TeleportToPoint`/`$TeleportToUnit`** — real call sites exist in
  `Guild_Skills.gpl` (Assembly's teleport-to-guild skill),
  `mx_Spells.gpl` (Gate/Dismiss/Blink/Witch-King-taunt spells), and
  `SpecialItemsExample.gpl` (a Dorgo-summoning special item) — genuinely
  3 files, but all 3 are spell/magic-item teleportation, arguably the
  same "system" (magical relocation) rather than 3 unrelated systems in
  the spirit of this sweep (a building, a hero decision tree, a monster
  system). Borderline; not written up given the other primitives above
  already fill the "movement/positioning" category more clearly via
  `$RandomCoord`.
- **`$MessageFlag`** — extremely common, but every single call site
  found is in quest-rules event scripts (`mx_Epic_Quest_Scripts.gpl`,
  `Quests_1.gpl`, and siblings) — one system category (quest scripting),
  not 3 unrelated ones, despite the high call count.
- **`$Hide`/`$UnHide`** — real call sites in Guardhouse guard-release
  (`Building_Guard.gpl`), hero task travel (`use_building.gpl`,
  `collect_tax.gpl`, `peasant.gpl`), and a quest-specific fortress
  warp-in (`Quests_3.gpl`) — plausibly 3 unrelated systems (building
  defense, ordinary hero task-travel, a one-off quest set-piece), but
  the building-defense and hero-task-travel uses are both instances of
  the same general "agent enters/exits visibility for a travel-to-
  destination task" pattern already covered by this guide's existing
  `TaskName`/`ActiveScript` state-machine sections (§1), so no
  additional distinct finding would result from a dedicated writeup.
- **`$HasAttribute`** — very common, but it's a generic "does this
  dynamically-added attribute exist" reflection check used consistently
  the same way everywhere it appears (guarding an optional field before
  reading it) — no distinct per-system behavior difference was found
  worth documenting beyond what's obvious from its name.
- **`$ChangeUnitType`** — real call sites in the Dwarfeh_AI mod's
  building-upgrade logic (`custom_rules.gpl`) and `mx_Spells.gpl`'s
  monster transformation spells (Dryad/Medusa/Minotaur) — 2 systems,
  below the bar.
- **`$Concatenate`** — extremely common as a generic "build an attribute-
  value pair list" helper passed to `$SpawnUnit`, but it has no
  interesting per-system behavior variance to report; it's pure argument-
  packing plumbing.

The remaining `Keywords3`/`Keywords4` primitives not named above
(`$Move`/`$StopMoving`/`$IsMoving`/`$DistanceBetweenAgents`/etc., basic
list ops like `$ListMember`/`$ListSize`/`$RemoveListMember`, and most of
the victory-condition/player-data/inventory-item primitives) were spot-
checked against the candidate list but either (a) already have dedicated
coverage elsewhere in this guide, (b) are simple single-purpose utility
calls with no cross-system behavioral variance worth documenting, or (c)
had too few call sites to assess. This sweep is not exhaustive of every
keyword in the file — it targeted the specific candidates named in
`TODO-GPL-Deepdive.md`'s "Not Yet Investigated" item plus judgment calls
from the keyword list, per that task's instructions.

## 15. Hero Class Decision Trees — Comparative Pass

All 15 base-game hero classes (`SDK/OriginalQuests/GPL/DecisionTrees/`:
`Adept`, `Barbarian`, `Cultist`, `Discord`, `Dwarf`, `Elf`, `Gnome`,
`Healer`, `Monk`, `Paladin`, `Priestess`, `ranger`, `Rogue`, `Solarus`,
`warrior`, `Wizard` — confirmed via `list_directory`, one file per class,
no extras) were read in full. Every tree is a single, flat priority-
ordered cascade of `if ($module(thisagent, args) == False) if (...) ...`
calls exactly like `Barbarian.gpl`'s existing documented shape — the
first module to return `TRUE` wins and the cascade stops there for that
tick; if every module falls through, the hero defaults to `$hero_wander`.
**Structurally, all 15 are identical in shape** — no class has a loop, an
`else` branch, or any control flow beyond the cascade. The only
per-class "structural" difference found is that `Cultist` and `Priestess`
each prepend one extra cascade entry ahead of `$check_nearby`
(`$Build_Pack`/`$Build_Horde` respectively) — still a plain cascade
entry, not a different shape.

**Real branching does exist, but it lives one level below the tree
file, in `check_nearby`.** Every class's tree calls `$check_nearby`
first, and `check_nearby.gpl` doesn't hardcode a single eval function —
it calls `(thisagent's "evaluationscript")(thisagent)`, a per-hero
function pointer. `target_eval.gpl` defines at least 6 different
`*_eval_nearby`-style implementations (`eval_enemies_nearby` — the
default fight-or-flee logic; `wizard_eval_nearby` — flees casters with
`#ATTRIB_magicresistance > 60` or a magic-mirror effect instead of
fighting; `cultist_eval_nearby` — tries to charm a nearby animal before
falling back to normal combat eval; `Healer_Eval_Nearby` — only checks
whether to heal or flee, never initiates a fight; `gnome_eval` — pure
flee, no fight branch at all; `support_eval_nearby` — used by
`follow_support_check`-based followers).

**CORRECTION — the wiring the previous pass marked UNVERIFIED is
directly confirmed in `Hero_Data.dat`/`mx_Hero_Data.dat`, one file the
original pass never opened.** Every class's `.dat` block sets
`evaluationScript` as a plain field, on the same lines as
`activeScript`/`basicscript` (both already-traced fields) — not hidden,
not exe-side, just a file this pass initially skipped. Full confirmed
mapping, read directly from `Hero_Data.dat`:

| Class | `evaluationScript` |
|---|---|
| Adept, Barbarian, Dwarf, Elf, Monk, Paladin, Priestess, Rogue, Solarus, Warrior, Warrior_of_Discord | `eval_enemies_nearby` (the generic default) |
| Cultist | `cultist_eval_nearby` |
| Gnome | `gnome_eval` |
| Healer | `Healer_eval_nearby` |
| Ranger | `support_eval_nearby` |
| Wizard | `wizard_eval_nearby` |

This directly confirms the naming-based guess the previous pass declined
to assert without a citation: **10 of 15 classes use the generic
fight-or-flee default, and only 5 get a class-specific evaluator** —
Cultist/Gnome/Healer/Wizard map exactly to their own namesake functions
as guessed, but **Ranger is the one genuine surprise**: it does NOT use
a ranger-specific evaluator (no `ranger_eval_nearby` exists at all) — it
reuses `support_eval_nearby`, the same follower/support-class evaluator
`target_eval.gpl`'s own comment ties to `follow_support_check`-based
followers. This is a real, non-obvious finding this doc's own §15
comparison already flagged Ranger as behaviorally distinct (highest
`explore_map`, lowest `go_home`, exclusive `$Journey_Offmap_Check`) —
its danger-evaluation logic is comparatively passive/support-flavored
even though its exploration behavior is the most aggressive of any
class, a genuine split between "how it evaluates threats" and "how it
spends its free time" that isn't visible from the tree file alone.
Non-hero `.dat` entries (`City_Guard`, `Veteran_City_Guard`,
`Palace_Guard`, `Tax_Collector`, `Peasant`, `Peasant_Female`, `Caravan`,
`illusionary_hero`) set no `evaluationScript`/`activeScript` at all —
confirming this whole mechanism is specific to the 15 playable/AI-tree
classes, not a universal hero-prototype field.

### Universal vs. class-specific modules

Confirmed by direct comparison of the module-call list across all 15
trees:

**Called by all 15 classes, no exceptions:** `$check_nearby`,
`$Check_rewards`, `$rest`. `$Defend_home` is called by 14/15 — **Gnome
is the sole exception**, with the call visibly commented out
(`//	if ($Defend_home(thisagent) == False)`), a deliberate, visible
choice rather than an oversight (Gnome's tree has no other
home-defense substitute either).

**Called by most, with notable exceptions:** `$Purchase_equipment` is
called by 14/15 — **Monk is the sole exception**, its tree has no
equipment-purchase step at all. `$pursue_entertainment` is called by
13/15 — **Healer and Monk both omit it** (Healer's tree has no leisure
step whatsoever; Monk's tree substitutes `$Visit_Building(..., "Inn",
50)` later in its cascade instead of the generic entertainment module).

**`$Check_rewards`'s own `no_attack` parameter is not uniform despite
the call being universal:** 14/15 classes pass `FALSE` (attack-flags
allowed); **Healer is the sole class passing `TRUE`** — per the
module's own logic (`Modules/check_rewards.gpl`), this unconditionally
zeroes the score for any `flag_attack`-type reward flag, meaning Healer
heroes will pursue explore-flags but categorically never self-select
into an attack-flag reward, the only class-level behavioral gate
confirmed on this particular module.

**`$defend_building(thisagent, "BuildingName")` is class-specific by
construction — the building name is a literal argument, not a shared
default — and it correlates directly with each class's own guild/temple:**

| Class | Building defended |
|---|---|
| Barbarian | `Rangers_guild` |
| Discord | `Temple_Fervus` |
| Dwarf | `Blacksmith` |
| Elf | `Gambling_hall`, then `Brothel` (two separate calls) |
| Monk | `Marketplace` |
| Paladin | `Temple_Dauros` |
| ranger | `trading_post` |
| Rogue | `Gambling_hall` |
| Solarus | `Marketplace` |
| warrior | `temple_agrela` |
| Wizard | `Library`, then `Marketplace` (two separate calls) |

Adept, Cultist, Gnome, Healer, and Priestess have no `$defend_building`
call at all — confirmed absent from their trees, not overlooked. Note
Barbarian defends the **Rangers' guild**, not a Barbarian-specific
building (there's no dedicated Barbarian guild to defend), and Elf and
Wizard are the only two classes defending two buildings.

**Modules called by exactly one class (confirmed via full 15-file
comparison, not just skimmed):**

- **Cultist-only:** `$Build_Pack` (charm-monster follower recruitment,
  gated on `#Max_Number_Cultist_Followers` and the `charm_monster`
  spell), `$Swarm` (attacks whatever the hero's Palace has flagged as
  its shared `"Swarm_Target"`, a Palace-level coordination slot, not a
  per-hero target), `$Patrol(thisagent, "Animal_Den", 60)`.
- **Priestess-only:** `$Build_Horde` (structurally the undead mirror of
  `$Build_Pack` — gates on `#Max_Number_Priestess_Followers`, tries
  `control_undead` first, falls back to casting `animate_skeleton` if no
  undead are nearby to control — a genuinely different fallback shape
  than `Build_Pack`, which has no such cast-instead-of-control
  fallback).
- **ranger-only:** `$Collect_resource(thisagent, "healing_herbs", 95)`,
  `$Journey_Offmap_Check` (checks `$getnearesthiddencoord` — if any
  hidden map remains, refuses, otherwise sends the hero to
  `$FarthestMapEdge`; a real "leave the known map" behavior no other
  class's tree has).
- **Solarus-only:** `$Find_Lair` (the module's own comment: "covers
  both hidden and unhidden lairs" — a superset of `$Raid_lair` used only
  by Solarus, revealing hidden lairs via `$RevealArea` when found new,
  raiding directly when already-seen), `$Garrison_Check` (picks a random
  guardhouse from the farthest N candidates and loiters there —
  confirmed distinct from `$defend_building`'s reactive-only shape;
  Garrison_Check pre-positions the hero speculatively, `defend_building`
  only reacts to a building already `In_danger`).
- **Dwarf/Gnome shared, no other class:** `$help_build` (queues the
  hero onto `palace's "buildings_waiting"`/`"buildings_under_
  construction"` — a construction-labor behavior). Dwarf passes
  `(3500, 85)`, Gnome `(5500, 75)` — different search-radius/chance
  pairs, same module.
- **Wizard-only:** `$Check_Library(thisagent, 90, "Wizard_Spell")` and
  `$check_library(thisagent, 55, "Wizard_train_intel")` (the two
  Wizard-exclusive `Intention` strings inside the shared
  `Check_Library` module — see `Modules/Check_Library.gpl`, confirmed no
  other class's tree passes either string), `$follow_support_check(...,
  "barbarian", 30)` / `(..., "monk", 20)` (Wizard is the only class
  whose tree calls `follow_support_check` — a caster hanging back near
  melee escorts).
- **Healer-only:** `$Heal_Others`, `$Follow_Heal_Check` (called 3
  times, for `"Warrior"` at 75, `"Wizard"` at 35, and lowercase
  `"tax_collector"` at 50 via the separate `follow_heal_check` module —
  confirmed two distinct functions in the same file, `Follow_Heal_Check`
  vs. `follow_support_check`, not a typo).
- **Rogue-only:** `$Loot_Gravestones` (targets `"Dead"`-type objects
  with gold, screening out anything still `$IsMoving` or titled
  `"Black_Phantom"` to avoid looting a resurrecting hero — see this
  guide's existing gravestone coverage in §8 for the general mechanic;
  this module's screening logic is the one new fact this pass adds),
  `$Collect_Resource(thisagent, "poison_plants", 90)`.
- **Elf-only:** `$Visit_Building(..., "Trading_Post", 35)` and
  `$Visit_Building(..., "Marketplace", 20)` as dedicated cascade entries
  (other classes that visit these buildings only do so reactively via
  `$defend_building`, not as a standalone leisure visit).
- **Adept-only:** `$patrol(thisagent, "building", 95)` (the generic
  "patrol the whole city" branch of the shared `Patrol` module — Solarus
  has a commented-out `$patrol(thisagent, "guardhouse", 25)` call
  suggesting this was once considered for Solarus too and dropped in
  favor of `$Garrison_Check`/`$Find_Lair` instead).

**Shared by 2-3 classes but not universal:** `$Steal_Check` (Cultist 25,
Elf 50, Rogue 95 — all three are the game's "greedy" archetypes),
`$Seed_Resource_Check` (Cultist 55, Healer 50 — otherwise unrelated
classes sharing one resource-seeding module), `$collect_special_item`
(Barbarian 30, Cultist 45, Dwarf 40, Elf 80, Monk 70, Rogue 90, warrior
20 — 7/15, skewed toward melee/greedy classes, absent from every pure
caster: Adept, Discord, Priestess, Solarus, Wizard all omit it, Healer
and ranger and Gnome and Paladin also omit it).

### Numeric parameter meaning, confirmed from module source

Every `chance`/`Chance` integer parameter across every module checked in
this pass (`raid_lair`, `raid_enemy_building`, `combat_wandering`,
`combat_wandering_heroes`, `explore_map`, `go_home`, and all the
class-exclusive modules above) resolves to the exact same idiom at the
top of the function body:

```gpl
if ($randomnumber(100) + 1 > chance) return FALSE;
```

**Confirmed meaning: it's a per-tick percentage gate on whether the
hero even considers that behavior this cycle — not a strength/damage
multiplier, and not a literal aggression stat read anywhere else.**
Higher values make a class more likely to attempt that action on any
given tick it's reached in the cascade; the number never appears again
inside the function beyond this single early-exit roll (confirmed by
reading `raid_lair`, `raid_enemy_building`, `combat_wandering`,
`combat_wandering_heroes`, `explore_map`, and `go_home` in full — none
of them reuse `chance` after the gate check). Cascade position still
matters independently of the chance value — a module earlier in the
list that happens to succeed pre-empts every later module regardless of
that later module's own chance — so the numbers tune "how often does
this fire when reached," not "how does this rank against sibling
modules."

### Aggression/exploration personality comparison (by the numbers)

| Class | raid_lair / raid_enemy_bldg | combat_wandering / _heroes | explore_map | go_home |
|---|---|---|---|---|
| Barbarian | 95 / 95 | 95 / 95 | 45 | 45 |
| warrior | 95 / 90 | 95 / 95 | 45 | 90 |
| Discord | 95 / 95 | 95 / 95 | — (none) | 50 |
| Paladin | 85 / 85 | 90 / 80 | — (none) | 80 |
| Solarus | 95† / 95 | — (none) | 75 | 5 |
| Dwarf | 75 / 80 | 15 / 15 | — (none) | 80 |
| Monk | 50 / — | 75 / — | — (none) | 60 |
| Priestess | 40 / 30 | 75‡ / 70 | 50 | 80 |
| Wizard | 45 / 30 | 65 / 60 | 50 | 85 |
| Cultist | 20 / 20 | 85‡ / 85 | — (none) | 30 |
| Elf | 15 / 15 | 80 / 80 | — (none) | 90 |
| ranger | 15 / 10 | 75 / 55 | 95 | 15 |
| Rogue | — (none)§ | 65 / 55 | 20 | 95 |
| Adept | — (none) | 60 / 55 | — (none) | 95 |
| Gnome | — (none) | 20 / 10 | — (none) | 90 |
| Healer | — (none) | — (none) | — (none) | 90 |

† Solarus uses `$Find_Lair` (95) instead of `$Raid_lair` — functionally
the closest equivalent, not the same module.
‡ Priestess's/Cultist's own source comments explicitly say they never
actually attack their "natural enemy" type via this module (undead for
Priestess, animals for Cultist) — they use it to hunt other monster
types while trying to *charm/control* the ones matching their own
build-follower module instead. The number itself doesn't encode that
distinction; the comment plus the presence of `$Build_Horde`/
`$Build_Pack` earlier in the cascade does.
§ Rogue's tree has `$Raid_lair` present but commented out
(`//	if ($Raid_lair(thisagent,35) == False)`) — a deliberate exclusion
visible in the source, not a module the class never considered.

**What the spread plainly supports, without over-reading it:**
Barbarian/warrior/Discord/Paladin form a clear "high melee aggression"
cluster (90-95 across the board on both raid and combat-wandering
values). Gnome and Dwarf both post very low combat_wandering values
(20/10 and 15/15) despite being at opposite ends of the raid spectrum
(Dwarf 75-80, Gnome has no raid modules at all) — Dwarf's own source
comment ("Dwarves do extra damage against buildings") explains why its
tree ranks `$Raid_lair`/`$raid_enemy_building` ahead of monster combat:
this is a stated building-focused playstyle, not an inferred one.
Solarus's 5 for `go_home` is the single lowest value of any class for
that module — combined with `$Find_Lair`/`$Garrison_Check` at 95/50, the
tree plainly biases Solarus toward staying out in the field over
returning home, more than any other class. ranger's 95 for
`explore_map` is likewise the highest of any class, paired with the
lowest `go_home` (15) and the class-exclusive `$Journey_Offmap_Check` —
three independent data points in the same tree all pointing the same
direction (ranger explores before anything else). Beyond these
source-stated or multi-signal-confirmed cases, this pass does not claim
further "personality" narratives the numbers alone don't independently
support — e.g. Wizard's `check_library` priority is genuinely higher
than Barbarian's (Wizard: 90/55/15 across three `check_library`-family
calls positioned right after `$Purchase_equipment`; Barbarian: 5/5,
positioned near the very end of its cascade, after all combat/explore
modules) — that specific comparison IS directly supported by cascade
position, not just the chance numbers.

### mx_ expansion spot-check (4 of 15: Barbarian, Wizard, Cultist, Solarus)

**Not byte-identical, but not substantially rewritten either — a
consistent, small, additive pattern across all 4 checked:** every
`mx_*.gpl` tree preserves its base tree's exact module order and exact
numeric parameters, with 1-3 new module calls spliced in at the same
relative position (immediately after `$Purchase_equipment`) in every
file checked:

- `mx_Barbarian.gpl` / `mx_Wizard.gpl` / `mx_Cultist.gpl`: all three add
  `$Purchase_bazaar(thisagent, 70)` right after `$Purchase_equipment`.
  This is an expansion-only module (the Magic Bazaar building itself is
  expansion-only) — confirmed added identically across all 3 files
  checked, not class-specific tuning.
- `mx_Barbarian.gpl` / `mx_Wizard.gpl` / `mx_Solarus.gpl` (not Cultist)
  additionally add `$Hall_Champs_Check(thisagent, N)` — Barbarian 40,
  Wizard 30, Solarus 40 — right after the bazaar check. This matches
  §3's existing documentation of `Hall_Champs_Check` as an
  expansion-only Hall-of-Champions loitering trigger; **Cultist's mx
  tree omits it**, consistent with Cultist having no Royal_gardens-style
  leisure-building affinity to extend in the base tree either.
- `mx_Solarus.gpl` adds one further module not seen in any of the other
  3 checked files: `$Check_Champion_Rewards(ThisAgent, 70)`, inserted
  between `$Hall_Champs_Check` and `$Find_Lair`. This module's own
  internals were not traced (out of scope for this comparative pass —
  no other class's tree references it in either base or the 3 other mx_
  files checked, so it doesn't affect the cross-class comparison above).

**Net characterization from this 4-file spot-check:** the base-vs-
expansion relationship for hero decision trees is "additive patch," not
"parallel rewrite" — every base-game module call, in its original order
and with its original chance value, survives unchanged in the mx_
version of all 4 files checked; expansion-only content is inserted, not
substituted. This was a 4-of-15 spot-check as scoped, not exhaustive —
the other 11 mx_ files were not opened in this pass.

---

## Quest Scripting — moved to its own file

The quest-scripting layer (`GPL/Rules/` and `GPLMx/Rules/` — all 15 files)
was researched as §16-§22 of this guide and has been **moved to**
**`GPL_QUEST_RULES_REFERENCE.md`**, reorganised by mechanism with a
task-oriented index. Subsection numbers (`§16.1`, `§21.4` …) are unchanged,
so existing cross-references still resolve — they now resolve into that
file.

Go there for: quest entry points and threads, victory/loss conditions,
event scheduling, spawn and difficulty tuning, custom agent behavior,
buildings as quest agents, the `"type"` register, and the quest-side
primitive/helper catalogue.

That file refers back to `§1`-`§15` (this file) unqualified in many places,
because the two halves were written as one document. **Rule for resolving a
bare `§N`: `§1`-`§15` = this file, `§16`-`§22` = the quest reference.**

## Retracted Claims (kept visible — do not repeat these mistakes)

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
