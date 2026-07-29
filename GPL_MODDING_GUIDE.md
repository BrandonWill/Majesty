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

## Open Questions Catalog (consolidated UNVERIFIED items)

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
  gate-then-autonomous-purchase pattern (§3)
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
- Whether Hall of Champions' `HallOfChampions_Bounty_Cost`/`Period`
  functions connect to `RewardFlag` at all — genuinely unknown, an earlier
  guess that they did was wrong (see Retracted Claims)

## Retracted Claims (kept visible — do not repeat these mistakes)

1. **WRONG:** "Hall of Champions' bounty functions are a `RewardFlag`-
   based mechanic similar to Zoo's." **Correction:** `Hall_Champs_Check`
   (the real hero-AI trigger) does a hardcoded building-title search with
   zero reference to `RewardFlag`/`check_rewards()`. What the bounty
   functions actually do and what calls them remains unknown — the
   original claim was pure speculation by surface-level analogy.
2. **WRONG (partial):** framing implied Zoo's charm mechanic was "shared
   logic" with the Cultist's spell. **Correction:** shared primitive
   (`$control_monster`), independent wrapper logic — see §9.

**Why this matters:** both mistakes came from assuming two similar-
looking systems work the same way without reading the second one's actual
source. Every claim in this guide was written only after that direct
read — extend it the same way.
