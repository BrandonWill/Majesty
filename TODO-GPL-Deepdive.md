# GPL / Gameplay Logic Deep Dive — TODO

**Status: First consolidation done.** All completed research (10 topics)
has been written up in `GPL_MODDING_GUIDE.md` — see that file for the
actual findings, organized by system. This TODO now tracks what's still
open: unresolved UNVERIFIED items, un-investigated topics, and the pass
structure for continuing the deep dive.

**Where the findings live (updated after the quest-rules pass closed):**
the write-up outgrew one file, so it is now two.
- `GPL_MODDING_GUIDE.md` — **§1-§15**, gameplay systems.
- `GPL_QUEST_RULES_REFERENCE.md` — **§16-§22**, quest scripting
  (`GPL/Rules/` + `GPLMx/Rules/`), reorganised into mechanism chapters
  behind an "I want to …" task index.

Subsection numbers were **not** renumbered by the split, because this
file and `TODO-Ghidra.md`/`TODO-GameTests.md` cite them by exact string.
So when reading either doc: **a bare `§1`-`§15` resolves to the guide, a
bare `§16`-`§22` resolves to the quest reference.**

## Evidence Standard (non-negotiable — applies to all future work here)

Every claim in `GPL_MODDING_GUIDE.md` must cite the specific file/function/
line it was verified against. No claim based on naming conventions or
assumed symmetry between similar-looking systems. Unconfirmed behavior
must be labeled **UNVERIFIED**/**UNKNOWN**, not stated as fact. This
standard exists because two early claims in this research had to be
retracted after a closer read — see `GPL_MODDING_GUIDE.md`'s "Retracted
Claims" section for both, and don't repeat that failure mode (assuming a
similar-looking system behaves the same way without reading its actual
source).

## Completed (see GPL_MODDING_GUIDE.md for full findings)

1. ActiveScript/BackScript/TaskName state machine
2. birthscript vs birthScript2
3. upgradescript (basic_upgrade vs magical_upgrade)
4. Building revenue system (RevenueScript/Revenue_Amount/Revenue_Time)
5. Guard_Function/Guard_Spawn_Function
6. Lived_In_Script (guild buildings)
7. The Intent system (#intent_*)
8. Krypta/Agrela hero revival
9. Hero death and gravestone handling
10. Building visit-system deep dive, full depth — every remaining
    `Visited_Script` function (`Upgrade_Equipment`, `Enchant_Equipment`,
    `Library_Visited`, `GuardHouse_Visited`, `Inn_visited`,
    `Fairgrounds_Visited`, `Hall_Of_Champions_visited`, `Poison_Weapons`,
    `Gambling_Hall`, `Brothel`, `Gardens_visited`) individually traced —
    see `GPL_MODDING_GUIDE.md` §3's "§3 continued" subsection. Also
    resolved `HallOfChampions_Bounty_Cost`/`Period` (read in full, no
    call sites found — see Retracted Claims update) and partially
    resolved the researchable-item gate-then-purchase question (confirmed
    for 3 buildings, not universal to all purchasable items)
11. **Systematic orphaned-content sweep** — every entity-shaped IMAG
    prefix (`AB`, `AV`, `BV`, `BB`) fully extracted from both
    `Data/maindata.cam` and `DataMX/mx_maindata.cam` via `cam_reader.py`
    and cross-checked individually against `M_Buildings.xml`/
    `MX_Buildings.xml`/`M_Characters.xml`/`MX_Characters.xml` `ID=`
    attributes. Result: Zoo remains the only genuine orphan (real
    sprites + real GPL logic + no XML wiring) — `AB`/`BV`/`BB` had zero
    unmatched IDs, and the two unmatched `AV` IDs found (`AVn8`/`AVn9`
    "selection_red") don't meet Zoo's bar (no GPL references, same
    UI-selection-indicator shape as already-wired `AVn1`/`AVn2`, not an
    entity). See `GPL_MODDING_GUIDE.md`'s "§9 continued" subsection.
12. **Re-verified `.kiro/steering/majesty-modding.md`'s Petrification
    System description** against `Spells.gpl`/`mx_Spells.gpl`
    (`Petrify_Begin`/`Petrify_End`/`Gorgon_Petrify_Begin`/
    `Gorgon_Petrify_End`), `LowLevel.gpl`/`mx_LowLevel.gpl` (`IsFrozen`),
    and the Action/Overlay XMLs. 4 of 6 claims confirmed exactly; 2
    corrected — **the sub-agent's original "UNVERIFIED how the base game
    invokes Petrify_Begin" was itself corrected after the fact: the user
    (an experienced modder) identified that base Petrify is cast directly
    from the Temple to Dauros building's own panel (`DialogID="AP05"`),
    unlocked at Temple Level 3 — a third "building-cast spell" pathway
    this research hadn't previously named, which is why a source-only
    grep for hero `AllowedSpells`/Action-XML callers found nothing.
    The Level-3 unlock mechanism itself remains genuinely UNVERIFIED
    (no XML/GPL/`.dat` field found) — a real, correctly-scoped Ghidra
    candidate, tracked in `TODO-Ghidra.md`'s "Low Priority:
    Temple-to-Dauros Level-3 Petrify Unlock Mechanism" section.** The "AI skips
    petrified units in decision trees via IsFrozen" claim has zero
    matching call sites anywhere in `DecisionTrees/`. Corrections made
    visibly in both the steering doc and `GPL_MODDING_GUIDE.md` §11 (not
    silently overwritten). See `GPL_MODDING_GUIDE.md` §11 for full
    citations.
13. **Building-unlocked "guild skill" castable abilities** — both
    sub-questions resolved, see `GPL_MODDING_GUIDE.md` §12 for full
    citations. **Correction after user input (kept visible, not
    overwritten):** the sub-agent's original framing treated "how is
    Rage of Krolm/Call to Arms triggered" as an open question of the
    same class as Petrify's genuinely-unresolved trigger gap — the user
    confirmed directly that **both are ordinary button clicks inside
    their own guild's building panel**, the same trigger CLASS as
    Petrify's AP05 button, not a separate mystery. **Q1 (unlock/lock):**
    with the trigger class now confirmed, what remains unconfirmed is
    only the exe-side click-dispatch code (grepped the full `.gpl` tree
    for `$DoRageOfKrolm(`/`$DoAssembly(` call syntax — zero matches,
    consistent with an ordinary exe-side button handler). `Temple_Krolm`/
    `Warriors_Guild`'s full `M_Buildings.xml` `<Description>` blocks have
    no `Skill`/`Ability`/`AllowedSpells`-equivalent field, same bare
    shape as Petrify's `Temple_Dauros`. Genuinely new finding: both
    buildings are single-tier (no `UpgradeTo` chain at all, confirmed by
    grep + their `Building_Data.dat` entries), so the guild-skill unlock
    **cannot** be a Level-3-style tier gate the way Petrify's is — there
    is no tier to gate on, meaning the two mechanisms are confirmed
    structurally different, not the same gate reused. Destruction
    behavior is explicitly **UNVERIFIED** — `building_death`/
    `guild_destroyed_common`/`guild_destroyed_a` read in full, no
    skill-revocation logic of any kind found — but the likely mundane
    explanation (the button lives ON that building's own panel, so
    losing the only copy just removes panel+button together, not a
    separate revocation mechanic) doesn't need Ghidra, only an in-game
    test with a duplicate guild. **Q2 (moddability):**
    confirmed the Dwarfeh_AI mod's `castSpell DoRageOfKrolm` `.dat` field
    really does bind to the base game's real `Guild_Skills.gpl` function
    (not a mod-local duplicate). Confirmed no base-game "spell registry"
    exists anywhere in `GPL/GPLMx` `prototype.gpl` (15 prototypes read,
    including `prototype Spell()` itself — it has no `canCast`/`cost`
    fields, just engine-plumbing placeholders) — the Dwarfeh_AI mod's
    `canCast`/`castSpell` wrapper is a from-scratch invention, confirming
    its own source comment. Net: a modder CAN call
    `DoRageOfKrolm`/`DoAssembly` (or write a new function of the same
    shape) from custom GPL with full confidence, but making a NEW such
    function player-triggerable from a building panel hits the same
    exe-hardcoded-panel wall Petrify's research found — the two working
    base-game examples give better `Sound`/overlay-callback documentation
    than Petrify had, but do not close the panel-button gap.
14. **Shared primitive catalog, remaining primitives** — both parts done.
    Part 1 (the effector system as its own topic — `$createeffector`/
    `$checkeffector`/`$deleteeffector`/`$deleteAllEffectors` duration
    semantics, overlay/callback wiring) is `GPL_MODDING_GUIDE.md` §13.
    Part 2 (a deliberate sweep for any other primitive recurring across
    3+ unrelated systems, beyond effectors/`$SpecifyIntent`/
    `$control_monster`/`RewardFlag`) is §14 — qualified: `$ListObjects`
    (full flag vocabulary, confirmed via the `expression` constants in
    `LowLevel.gpl`/`mx_LowLevel.gpl`), `$AdjustAttribute` vs
    `$MagicalAdjustAttribute` (confirmed cosmetic stats-window-color
    difference, not a functional one), `$PerformAction` (generic
    Action-XML one-shot dispatch, not attack-specific), `$RandomNumber`/
    `$RandomCoord` (confirmed inclusive-range `+1` idiom and 2/3-arg
    `$RandomCoord` shapes), `$NewThread` vs `$RunThread`/`$RunThreadOnce`
    (confirmed primary-loop vs. secondary-guardable-helper distinction,
    still not resolving the underlying scheduler-internals UNVERIFIED
    item). Discarded for insufficient unrelated-system spread:
    `$FindFirstMatchOnly` (2 sites, folded into `$ListObjects`),
    `$RunThreadOnce` (1 site), `$TeleportToPoint`/`$TeleportToUnit`
    (3 sites but all magic/teleport-flavored), `$MessageFlag` (many
    sites, all quest-scripting), `$Hide`/`$UnHide` (3 sites but
    overlapping with the existing `TaskName`/`ActiveScript` coverage),
    `$HasAttribute`, `$ChangeUnitType`, `$Concatenate`.
15. **Hero class decision tree pass** — all 15 base-game classes
    (`Adept`, `Barbarian`, `Cultist`, `Discord`, `Dwarf`, `Elf`, `Gnome`,
    `Healer`, `Monk`, `Paladin`, `Priestess`, `ranger`, `Rogue`,
    `Solarus`, `warrior`, `Wizard`) read in full and compared — see
    `GPL_MODDING_GUIDE.md` §15. Confirmed universal vs. class-specific
    module calls, confirmed the `chance` parameter's meaning (a flat
    per-tick percentage gate read once at function entry, never reused,
    confirmed from 6+ modules' source), tabulated the aggression/
    exploration numeric spread across all 15, and traced the one real
    branching mechanism found (`check_nearby`'s per-hero
    `"evaluationscript"` function pointer, dispatching to 6 different
    `*_eval_nearby` implementations in `target_eval.gpl`) — **left
    UNVERIFIED: which class maps to which `evaluationscript`
    implementation**, no assignment site found in the `.gpl` tree.
    Spot-checked 4 mx_ equivalents (Barbarian/Wizard/Cultist/Solarus):
    confirmed additive-patch relationship (base module order/params
    preserved exactly, expansion-only calls spliced in after
    `$Purchase_equipment`), not a parallel rewrite — not exhaustive of
    all 15 mx_ files.
16. **Quest rules pass, Batches A-G** — all 15 files in
    `SDK/OriginalQuests/GPL/Rules/` and `GPLMx/Rules/` read; see
    `GPL_QUEST_RULES_REFERENCE.md` §16-§22 for findings and the "Quest Rules
    Pass — COMPLETE" section below for the per-batch record. Headline
    shape: §16 construction rules + victory conditions, §17 demo/random/
    special events, §18 quest actives, §19-§21 the three expansion quest
    files, §22 the base epic-quest helper library (including the
    post-victory difficulty-tier system and the `Lair_extra_delay` pacing
    knob). Each batch closes with a recombination list so no file needs
    re-reading; §22.8 carries the whole-pass list of what is still open.

## Open UNVERIFIED Items (carried over, need resolution)

**Routing note (added when Batch G closed the pass):** the `Rules/`-pass
items (§16-§22) are now filed where they can actually be worked, so they
are not re-listed below — engine-side primitive semantics went to
`TODO-Ghidra.md` **Priority 7** (as a table, one row per primitive, with
its guide citation), and the one-test-each language/runtime questions went
to `TODO-GameTests.md` **"GPL Language Semantics"**. `GPL_QUEST_RULES_REFERENCE.md`
§22.8's closing note stays the canonical source for that split, including
its third category (untraced consumers, answerable by more source reading
outside `Rules/`). The list below is the older pre-`Rules/`-pass carry-over
and is unchanged.

See `GPL_MODDING_GUIDE.md`'s "Open Questions Catalog" for the full list
with section references. Highlights that would need Ghidra specifically
(coordinate with `TODO-Ghidra.md`):

- Engine-side `$NewThread`/`$RunThread`/`$ResumeThread`/`$KillThread`
  scheduler semantics
- Whether the exe truly calls `$building_upgraded`/`$DoMarketDay`/
  `$EndMarketDay` from real player actions
- Research-purchase-button click dispatch (control_id ranges) —
  `TODO-Ghidra.md` Priority 3.4
- What numeric `cProc="8192"` resolves to (hero death action callback)
- What renders the AITX intent/status string lookup and how

Highlights answerable from GPL/XML/`.dat` source alone (no Ghidra needed):

- What sets `#ATTRIB_isTaxed`/`#ATTRIB_QuickTax` on a building
- Where `GuardHouse_Birth` (referenced as a `birthScript2` value) is
  actually defined — not found in any `.gpl` file searched so far
- **RESOLVED for researchable items specifically** (see
  `GPL_MODDING_GUIDE.md` §3 continued / Open Questions Catalog): confirmed
  independently for Library and Blacksmith in addition to Bazaar. Still
  open: not every purchasable item is researchable — some (Enchant_
  Equipment, Fairgrounds, Poison_Weapons, Gardens, Inn) have no unlock
  step at all, which is a different question than originally posed.
- Whether a Mausoleum-interred hero remains reachable by `"Dead"`-type
  list queries (affects whether Reanimate/Resurrection can still target
  them)
- Whether other building panels have the same per-panel-STRT-vs-GMTX text
  trap already confirmed for Marketplace/APa3
- **NARROWED, not fully resolved:** Hall of Champions'
  `HallOfChampions_Bounty_Cost`/`Period` — both functions read in full
  (pure cost/period data lookups, 400/800 gold and 60000/120000ms for
  bounty_index 1/2), confirmed to have zero call sites anywhere in the
  `.gpl` source tree. What exe-side code calls them, and whether a
  "bounty" mechanic manifests as anything beyond these two values, is
  still genuinely unknown — see `GPL_MODDING_GUIDE.md`'s Retracted Claims
  update.

## Quest Rules Pass — COMPLETE (was "Not Yet Investigated")

This section held the last remaining un-investigated item. **With Batch G
done it is finished**, and the per-batch findings below are kept in place
as the working record (they are also summarised as Completed item 16).
Remaining open work for this doc now lives in "Open UNVERIFIED Items"
above and the Prioritization Note below.

- [x] **Quest rules pass** (`GPL/Rules/` + `GPLMx/Rules/`) — **COMPLETE,
  Batches A-G, see `GPL_QUEST_RULES_REFERENCE.md` §16-§22.** All **15 files**
  across both `Rules/` directories read: base
  `construction_rules.gpl`, `victory_conditions.gpl`, `Demo.gpl`,
  `Quest_Actives.gpl`, `epic_quest_scripts.gpl`; expansion the five
  `mx_` twins plus `Random_Events.gpl`, `Special_Events.gpl`,
  `Quests_1/2/3.gpl`. Scoped throughout to extracting genuinely reusable
  mechanisms rather than per-quest plot summaries — every batch ends with
  a "recombination only" subsection listing what *isn't* new, so no file
  needs re-opening. §22.8's closing note names what remains open across
  the whole pass, split into engine-side questions (Ghidra),
  one-in-game-test questions, and untraced consumers that live outside
  `Rules/`.
  - [x] **Batch A: `construction_rules.gpl` + `victory_conditions.gpl`**
    (plus both `GPLMx/Rules/` equivalents) — see
    `GPL_QUEST_RULES_REFERENCE.md` §16. `CanIBuildThisBuilding` fully traced:
    exe-invoked callback (zero GPL call sites), all per-title branches
    tabulated with their `globals.gpl` radius constants, failure returns
    confirmed to share the `#intent_*` numbering space in
    `defines.gpl`, mx diff = one new `outpost` branch plus a
    `$listcompleted`→`#ATTRIB_FirstStageBuilt` /
    `$listtitles`→`$removetitles` swap. `dependencies` is
    **UNVERIFIED** — no live branch reads it and no XML field feeds it.
    `SetVictoryCondition` fully traced: 4 branches (index 0/1/2/3 →
    `VictoryCondition_Three/_Two/_One/_four`), `$GetVictoryConditionIndex`
    = setup-menu dropdown row, `$GetVictoryConditionModifier` unit is
    per-branch GPL-decided (days vs. gold), mx diff = base's
    `VictoryCondition_four` re-splits teams every poll, mx's doesn't.
    **Verdict on custom victory conditions: quest-driven ones need GPL
    only** (the ~30 epic quests and `SDK/SpecialItemsExample` all arm
    their own `"VictoryCondition"` thread and call `$declarevictory`
    directly); **a new freestyle dropdown row needs an exe/UI change**
    (no dropdown labels in GPL/XML/`.mqxml`) — repurposing an existing
    row is the GPL-only workaround.
    **Cross-reference needed (not edited by that pass):**
    `TODO-New-Building-Requirements.md`'s placement-validation and
    build-menu-prerequisite items conclude placement gating is
    exe-only/`$disableunittype`-only — `CanIBuildThisBuilding` is a real
    GPL-side, per-building-title placement prerequisite hook and that
    framing needs narrowing there (its terrain-tile claim still stands).
  - [x] **Batch B: `Demo.gpl` + `Random_Events.gpl` + `Special_Events.gpl`**
    (plus `GPLMx/Rules/mx_Demo.gpl`) — see `GPL_QUEST_RULES_REFERENCE.md` §17.
    **`Random_Events.gpl` and `Special_Events.gpl` are expansion-only** —
    confirmed four ways (absent from `GPL/Rules/`, absent from
    `GPL/path.gplproj`, base `Freestyle()` has no event kickoff,
    `Prototype EventAgent` exists only in `mx_prototype.gpl`).
    `mx_Demo.gpl` is byte-identical to `Demo.gpl` bar one blank line —
    no expansion-only Demo content exists.
    **New engine-invoked hooks confirmed** (zero-GPL-call-site test):
    the quest entry function itself (`VAMPIRIC_REVENGE`), `Freestyle()`,
    and **per-instance `agent's "IGDeathScript"`** — engine-invoked but a
    plain writable attribute, the most flexible hook found so far. Plus
    **a new hook category: engine-*named*, GPL-invoked** —
    `$GetSpecialEvent1Script()`/`$GetSpecialEvent2Script()` return a
    function *name string* which GPL binds via `$LookupFunction`, so any
    modder function is reachable by name (strictly better than §16.2's
    index-based victory dropdown).
    **Random vs. special events is a real mechanical distinction:**
    random events are stateless effect functions with no schedule of
    their own (the 14 in `Random_Events.gpl`; scheduler lives in the
    caller — `Quests_3.gpl`'s four difficulty-tiered dispatchers, chosen
    by player performance = rubber-band difficulty via function-pointer
    assignment); special events are self-scheduling stateful plugins
    (15 functions, fixed `(string AgentName)` signature, own `EventAgent`
    with 10 `Event_Flag_N` booleans, reschedule via
    `$SetThreadInterval`). **Selection is uniform/unweighted everywhere**
    — no probability tables exist in either system.
    Also documented: full `$disableunittype` build-menu gating pattern
    (22 calls, tier-suffix semantics, **no re-enable in Demo — verified
    by grep + full read**, contrast the two real re-enable sites),
    `#ATTRIB_Artifice`/`#force_*` spawn-time AI override (4 constants in
    base, 10 in mx — the cleanest pure-GPL extension point found),
    `$SpawnUnit`'s variadic order-insensitive argument grammar, the
    coordinate-helper family, the borrowed-caster workaround for hostile
    `$CreateSpellUnit`, `$spelldamage($nullagent(),...)` as the
    unattributed-damage path, and `$random_time()`'s 75-100% jitter
    (independently re-confirming the 60000-ticks-per-game-day finding).
    **Batch B's biggest open question was then RESOLVED in a follow-up
    pass (see `GPL_QUEST_RULES_REFERENCE.md` §17.7): the special-event registry
    is plain CAM `STRT` data in `DataMX/mx_gpltext.cam`** — `EVSC` binds
    `EVxx` → GPL function name (+ an unexplained 20-95 number), `ENTX`
    holds dropdown labels, `EDTX` descriptions; 16 rows (`NONE` +
    `EV01`-`EV15`); base `Data/gpltext.cam` has none of these tables,
    re-confirming expansion-only at the data layer. Because quest-CAM
    `STRT` override is already confirmed working, **the whole
    special-event framework is quest-distributable with no exe patch**,
    superseding §17.3's original "needs an exe/UI change" verdict.
    Shipped case-mismatches (`EVSC` says `Goblin_attack`, the function is
    `goblin_attack`) also prove **`$LookupFunction` is
    case-insensitive**. The same pass found the **victory-condition
    dropdown labels are likewise CAM data** (base `Data/gpltext.cam`'s
    `GOAL` entry, count=4) — see §16.3's correction block, and
    `TODO-Ghidra.md`'s now-mostly-resolved item.
    **Still UNVERIFIED:** whether either dropdown's row *count* is
    data-driven (adding an `EV16`/5th `GOAL` row — both now in-game tests
    in `TODO-GameTests.md`, not Ghidra items), the `GOAL` row-order vs.
    GPL-index mismatch, what the `EVSC` number does, base-exe existence
    of `$GetSpecialEvent*`, and ~~`"Special_Spawn_Type"` vs.
    `"Has_Special_Spawn"` semantics~~ — **that last one RESOLVED by Batch
    D, see `GPL_QUEST_RULES_REFERENCE.md` §19.7:** read from `lair_death`
    (`mx_Building_Deaths.gpl` 264-298), `Special_Spawn_Type` is the
    payload and `Has_Special_Spawn` is a priority override that forces
    the GPL-set value to win over the lair's own
    `$FillSpecialLairList` data; `"xx"` is the unset sentinel. Batch B's
    two apparently-inconsistent call sites were simply the two different
    intents.
  - [x] **Batch C: `Quest_Actives.gpl`** (plus `GPLMx/Rules/
    mx_Quest_Actives.gpl`) — see `GPL_QUEST_RULES_REFERENCE.md` §18.
    **`mx_Quest_Actives.gpl` is functionally identical to the base file**
    (only whitespace plus one fully commented-out `Henchman_Wander`
    block), and unlike Batch B's event system **everything here works in
    base game mode**. **Key structural result: there are no
    engine-invoked hooks in this file** — all 15 functions are either
    stored in an agent script slot (`ActiveScript`/`BasicScript`/
    `BackScript`/`StartingScript`/`EvaluationScript`/`BirthScript`/
    `IGDeathScript`/`SpecialScript`) by some other file, or called
    directly from GPL; "Rules/Quest_Actives" is an organizational
    convention, not a registry, so a modder can put equivalent functions
    anywhere. Traced every assignment site (`Inventory.gpl`'s
    `QItem_Stat_Boost` ring branch, `Hero_Births.gpl`'s
    `Generate_Character_Attributes`, and `epic_quest_scripts.gpl`'s
    `HOLY_CHALICE`/`MAGIC_RING`/`WIZARDS_CURSE` setup blocks).
    Seven clonable behavior templates documented: **courier/delivery**
    (§18.3, incl. `travel_to_safe` = "ignore distractions", the mandatory
    arrival re-verification guard, and `$Move(…, "avoid_vehicles")`),
    **interposed AI wrapper** (§18.4 — `Be_Dumb` delegates to the class
    tree via `(agent's "QuestScript")(agent)`, so a "50% of turns do
    nothing" debuff needs no attribute and no effector, and one root-agent
    boolean cancels it globally with no cleanup pass), **claim-and-follow**
    (§18.5 — `$Is_Free_Task(agent, $Behavior, target)` is a generic
    task-contention resolver: closest hero wins, up to
    `#is_free_task_max_heroes` extras; plus `#followBored` anti-crowding
    and the NPC-side `Special_Boolean` latch and self-escort), **minimal
    decision tree + `EvaluationScript` leash** (§18.6), **building-as-
    active-agent** (§18.7 — `SpecialScript` + `$NewThread`, 7 shipped
    sites; includes the fully traced `Magical_Repair_Effector` →
    `<Script GPLFunction="magical_repair">` → +10 HP callback chain),
    **respawn-by-rebirth** (§18.8 — `$RunThread(agent's "BirthScript", …)`
    with `Type = "Dead"` as the between state, installed by a
    `function`-typed installer `Setup_Special_Chests(list, function,
    function)`), and **arrive-and-despawn plus runtime defection** (§18.9 —
    `$Hide`/`$IsHidden`/`$DeleteGamePiece`, `$SetUnitPlayerNumber`).
    Also new: the `QuestScript`/`StartingScript` swap-and-stash idiom and
    the pre-declared per-agent quest scratch fields (`Special_Boolean`,
    `Counter`, `Coord_Home`), the fact that `SpecialScript` exists only on
    `Guild`/`Dwarven_Settlement` prototypes (not plain `building()`),
    `#ATTRIB_ForceBuildingState`, `#ATTRIB_AlwaysView`, `$NeutralTeamNumber`,
    `$istitlealive`, `$ListSubtypes`'s not-in-place contract, the
    `"Hooligan"`/`"Hidden"`/`"Special"` query type names, and the Hooligan's
    fully declarative script binding in `Monster_Data.dat`. Eight shipped
    defects cited so nobody clones them (§18.10).
    **Still UNVERIFIED:** what `"avoid_vehicles"` avoids; whether
    `$SetAttribute(agent, #ATTRIB_HP, 0)` really deletes the agent (which
    is why respawn-by-rebirth's mechanism is unexplained — in-game test or
    Ghidra, not more source reading); which art
    `#ATTRIB_ForceBuildingState`'s active/inactive select (`Drop_Ring`'s
    comment contradicts its code); the engine ordering of
    `Generate_Character_Attributes` vs. `hero_birth` (inferred, not
    traced); whether `Treasure_Spawner()` (zero references anywhere) is
    reachable at all.
  - [x] **Batch D: `Quests_1.gpl`** (2232 lines, read in full) — see
    `GPL_QUEST_RULES_REFERENCE.md` §19. **Expansion-only, no base-game
    equivalent** (only `GPLMx/Rules/Quests_{1,2,3}.gpl` exist; only
    `GPLMx/Path_Data.gplproj` lines 16-18 reference them) — same caveat as
    Batch B's event files. Four quests (`LEGENDARY_HEROES`,
    `VALE_SERPENTS`, `CLASH_EMPIRES`, `DARKNESS_FALLS`), all built on one
    five-part skeleton documented once in §19.1 with a per-quest summary
    table in §19.2. **Six genuinely new mechanisms:** (1) the whole
    **music subsystem** — `$PlayMusic` / `$LastMusicTrack` /
    `$SetMusicStoppedCallback`, the last being a **string-named GPL
    callback registration**, backed by the plain-text registry
    `Data/MusicTracks.txt` (six tracks; `EpicQuest.mp3` is orphaned — no
    shipped GPL plays it), so custom quest music needs no XML/CAM/exe
    change; (2) **the `#force_*` loop closed** — `check_override_behavior`
    is editable GPL, so modders can add their own artifice value +
    behavior function, `#force_overlay` turns out to be cosmetic-only and
    readable by just the Troll, and `Target`+`Relentless`+
    `$Monster_Attack_Object` is a no-artifice "chase that unit" recipe;
    (3) **Batch B's `"Special_Spawn_Type"` vs. `"Has_Special_Spawn"`
    question RESOLVED** from `lair_death` (`mx_Building_Deaths.gpl`
    264-298) — payload vs. priority-override over the lair's own
    `$FillSpecialLairList` data, `"xx"` = unset sentinel; (4) a **fourth
    event-thread lifecycle** beyond §17.4's three: the self-pacing staged
    sequencer (flag chain + per-stage `$SetThreadInterval` +
    difficulty-ratchet terminal `Else`); (5) **multi-faction war** via
    `$SetPlayerTeamNumber`/`$NewTeamNumber` applied to *lairs*,
    `$RevealWholeMap(#Player_N)`, and a `$ListFamily` population
    equalizer; (6) **conditional resurrection in place** via
    `$ClearEngineDeathFlags` + `"Type"` lifecycle swapping, reusing the
    dead unit's own script slot as the timer. **Plus:** `$IsTitleAlive`'s
    monster∪invisible union, two-stage victory gating, "protect what you
    can't build" (`$DisableUnittype` + `$DeclareLoss`), **quest threads
    survive `$declarevictory`** (how "keep playing after you win" works),
    the writable lair field set (`Max_Simul_Spawns`/`Max_Stored_Spawns`/
    `History_Modifier`), `#Monster_Spawn_Cap` as a GPL convention each
    spawn function must enforce itself, `Palace's "heroes_to_upgrade"`,
    and the elite-NPC stat-stack recipe. **Correction recorded (not
    edited in place, out of scope):** §14's claim that `$ListTitles` is
    the primitive that strips matches from its source list is wrong — the
    stripping is `$RemoveTitles`' side effect (two call sites in this file
    prove it, one discarding the return value entirely). **Explicitly
    recombination, not new:** `$SpawnUnit` grammar, `"MaxHP"`, coordinate
    helpers, message/beacon/reveal trio, `$CreateSpellUnit`,
    `$setup_random_treasure`, `$SetUp_Respawning_Lairs`,
    `$Make_PC_Hunter`-at-runtime (§19.11). **Still UNVERIFIED:**
    `$LearnSpell`'s third arg; whether `MusicTracks.txt` is 1-indexed and
    a 7th line is playable; what `=` in a condition compiles to (two
    shipped instances in `Darkness_Events`); whether attribute-name
    lookup is case-insensitive (`"End_Coord"`/`"End_coord"`); which
    duplicate `#wight_gravestone_interval` wins (80000 vs 120000); how
    `Self_Estimation`/`Enemy_Estimation` are consumed;
    `$SetPlayerTeamNumber`'s exact scope; what populates the
    `"invisible"` `$ListObjects` class.
  - [x] **Batch E: `Quests_2.gpl`** (977 lines, read in full) — see
    `GPL_QUEST_RULES_REFERENCE.md` §20. **Expansion-only** (`file_search` returns
    exactly one hit, no `GPL/Rules/` twin) — same caveat as Batches B/D.
    Four quests (`RISE_RATMEN`, `SCIONS_CHAOS`, `URBAN_RENEWAL`, `VIGIL`),
    all on §19.1's skeleton with three deviations: `SCIONS_CHAOS` runs on
    ONE thread (staging nested inside the victory poll), nobody
    initialises quest flags, and two of four sequencers `$KillThread`
    themselves instead of ending in a difficulty ratchet. **This file is
    where quest content is made out of *heroes and enemy buildings*
    rather than lairs and monsters**, which is where all the new material
    comes from. **Six new mechanisms:** (1) **`"type"` is the
    `$ListObjects` class register, not a fixed taxonomy** (§20.2) — this
    **RESOLVES Batch D's open "what populates the `"invisible"` class"**:
    invisibility/camouflage spells *overwrite* `thisagent's "type"`
    (`mx_Spells.gpl` 1141/3245/3576, base `Spells.gpl` 1074/1389),
    `"original_type"` is the stash, `"subtype"` is how you recover what
    the thing really is, and the same register carries `"unknown"`/
    `"pet"`/`"hidden"`/`"Dead"`/`"Waiting_to_die"`; `guild_destroyed_common`'s
    shipped comment states the reason outright. Practical rule: any
    census must union `"invisible"`+`"camouflaged"` and filter on
    `"subtype"`. (2) **Heroes as quest content** (§20.3) — the five-write
    enemy-hero boss recipe (level + paired `#ATTRIB_MAXHP`/`#ATTRIB_HP` +
    runtime retitle + `resist_critical`), and **critical hits are damage
    equal to the target's MaxHP, `/6` if the defender resists** (reader
    traced in `mx_make_attack.gpl` 194-198/237-241); `$make_raider` works
    on hero-type agents, blessed by the hero prototype's own comment
    ("jim hackerama so heroes can become raider mosnters"). (3) **The
    rescue/defection subsystem** (§20.4) — park → discover → claim built
    on the `"type"` register, `enemytype = "nothing"` as the
    combat-participation switch, the five threads that must be killed to
    deactivate an outpost, and `SpecialList`'s two-members-per-record
    parallel-list protocol. (4) **Two poll patterns** (§20.5) —
    latch-on-appearance (wait for count 1 before testing 0) and a
    live-tracking `end_coord` victory camera. (5) **Building hijack +
    higher-order death handlers** (§20.6) — `ActiveScript` on a non-guild
    building is *destructive* where `SpecialScript` is additive;
    `$guild_destroyed_common(agent, function)` takes a **function value**,
    not a name string; three stock death handlers confirm the "add
    behavior then tail-call the family handler" convention. (6) **Advisor
    voices + starting hero level** (§20.7) —
    `$ElvesVoice_setOperative`/`$dwarvesVoice_setOperative` (engine-side,
    base+mx, always paired with the matching `$DisableUnitType`) and
    `$setup_hero_level` + `#ATTRIB_StartedwithThisUnit`. **Also
    COMPLETED Batch D's §19.6 dispatch table** — all four
    previously-blank installers read (`make_raider`/`make_caravan_raider`/
    `make_guardian`/`make_bomber`), which makes this file's
    `evaluationScript` write after `$make_raider` a **no-op duplicate**.
    **Both flagged leads turned out to be recombination** — the
    `"RhodenKingRat"` `$IsTitleAlive` quest is exact reuse of §19.5a, and
    the `$Make_PC_Hunter`+`#ATTRIB_sightrange` loop reduces to §19.6 plus
    a plain `$AdjustAttribute` (it does omit the `$Reset_Tasks` that
    Batch D saw everywhere — UNVERIFIED whether that matters). §20.8
    lists the full recombination set so nobody re-reads this file.
    **Narrowed but still open:** `$SetPlayerTeamNumber`'s scope (a second
    one-call-per-faction site plus a `$GetPlayerTeamNumber` idempotence
    guard, consistent with per-player scope, not proof). **Not answerable
    from this file** (none of the constructs appear in it):
    `$LearnSpell`'s third arg, `Self_Estimation`/`Enemy_Estimation`
    consumers, `MusicTracks.txt` indexing, `=`-in-a-condition.
    **New UNVERIFIED:** whether the engine also writes `"type"`; what
    gates the rescue's discovery phase (absence of `#NoHiddenMap`, which
    is numerically 0); whether the `ActiveScript` hijack leaves the old
    thread running; whether `$SpawnUnit` runs
    `$Generate_Character_Attributes` automatically; what consumes
    `#ATTRIB_StartedwithThisUnit`; what the voice primitives silence; why
    latch-on-appearance is needed; why the palace is absent from the
    `#ATTRIB_FirstStageBuilt` building query; what the
    `#ATTRIB_MaxGuildMembers` +20 on a dying guild is for. Base twins of
    the rescue/hero-level helpers were located but not diffed.
  - [x] **Batch F: `Quests_3.gpl`** (2977 lines, read in full minus lines
    ~524-756 already covered by Batch B/§17.2) — see
    `GPL_QUEST_RULES_REFERENCE.md` §21. **Expansion-only** (`file_search`: one
    hit, no `GPL/Rules/` twin). **Process note: the dispatch was
    interrupted after writing §21.0-21.9; the closing §21.10 (sources,
    headline results, consolidated UNVERIFIED list) was written
    separately afterwards and says so inline.** Four quests
    (`TRADE_ROUTES`, `SPIRES_DEATH`, `SIEGE`, `FORTRESS_IXMIL`) and
    **this is the sibling that abandons §19.1's skeleton** — three of the
    four never poll for victory (two declare it from a *death script*,
    one from an *externally-called scorer*), `Quest_Flag_N` is used as
    ordinary state rather than a program counter (one quest inits its
    flags to `TRUE`), and two more declared root-agent script slots are
    in play (`SpecialSpawnScript`/`SpecialSpawnScript2`). The file's
    content is four *systems*, not four flag chains: (1) **externally
    scored graded victory** (§21.3) — 5 checkpoints × 4-5 outcome bands,
    with a script slot compared against a function value as an
    "already-decided" latch; (2) **the self-retiering lair** (§21.4, the
    most transferable system in the batch) — fewer spires ⇒ harder
    survivors, compensation scaled to the player's own army, via a
    runtime-swapped `function`-valued `Spawn_Function` and
    `Attack_Action` spell name, with `$SetEffectorDirection` as a free
    visible tier readout; (3) **a complete AI opponent kingdom in GPL**
    (§21.6) — gold-budgeted recruitment, hand-billed building-cast
    spells, `$PlaceRewardFlag` used *by* the AI, `SetEnemyResearch`
    writing `#ATTRIB_Research*`, surrender-to-peace via
    `$NeutralTeamNumber` + the `Permanent_Hostility` flag; (4) **a
    phase-in/phase-out boss building** (§21.7) plus **elapsed-time
    difficulty scaling** (§21.8) — `$Hide(agent, marker,
    #TeleportInsideDestination)`/`$Unhide` + `$FadeIn`/`$FadeOut`, a
    float `SpawnPower` multiplier off a day counter and a
    days-since-last-appearance delta. Also new: §21.2's full root-agent
    declared surface (two slots + five general-purpose integer
    registers — the prototype comment confirms they're "used on a quest
    by quest basis"), victory-declared-from-a-death-script and
    hostile-palace teardown (§21.5), `$DropGoldEveryone`,
    killing-by-negative-HP, `"Closed"` as a live Marketplace title
    (the §20.2 `"type"`-register trick applied to `"title"`), `"clear"`
    as a third `$SpawnUnit` string flag, and `-1` as a fourth
    effector-duration form. **RESOLVED §20.6b's open question:
    `$SpawnUnit` does NOT run `$Generate_Character_Attributes`** — a
    second independent call site plus an explicit shipped comment make it
    a confirmed rule, so a script-spawned hero must be passed to it by
    hand. **Not advanced:** `$SetPlayerTeamNumber`'s scope (a third
    one-call-per-palace site, same shape). **Not answerable here** (absent
    from the file entirely): `$LearnSpell`'s third arg,
    `Self_Estimation`/`Enemy_Estimation`, `MusicTracks.txt` indexing,
    `=`-in-a-condition (every comparison here uses `==`). **New
    UNVERIFIED:** which stock function retitles a Marketplace to
    `"Closed"`; `$SetEffectorDirection`'s index→frame mapping;
    `$DropGoldEveryone`'s split rule; whether GPL silently discards extra
    call arguments (a shipped call exceeds its declared signature and
    compiles); `"clear"`'s meaning; `-1`-duration semantics;
    `#ATTRIB_CurrentEvent`'s event-index mapping; and
    `Fortress_Ixmil`'s `Warp_Out` scheduling (flagged as an unresolved
    wiring question, **not** a confirmed bug, since the engine may invoke
    it by name). §21.9 lists the full recombination set so nobody
    re-reads this file.
  - [x] **Batch G (FINAL): `epic_quest_scripts.gpl`** (4358 lines, 85
    function definitions, read in full) plus targeted diffs against
    `GPLMx/Rules/mx_Epic_Quest_Scripts.gpl` — see
    `GPL_QUEST_RULES_REFERENCE.md` §22. **Process note: the dispatch was
    interrupted after writing §22.0-22.7; the closing pair §22.8
    (sources, headline results, prior-batch resolutions, consolidated
    UNVERIFIED list, whole-pass closing note) and §22.9 (recombination
    set) were completed separately afterwards and say so inline.**
    **This is the first base-`GPL/` quest-implementation file in the
    pass** (D/E/F were all `GPLMx`-only): the expansion re-ships all 19
    base epic quests and the mx clone differs in **exactly two ways** —
    the whole post-victory difficulty-tier library is base-only, and
    `Freestyle()` is 3 statements in base vs. ~40 in mx (§22.0/22.4a).
    All 19 quests plus `Freestyle` get **one table row each** (§22.1);
    the real content is the shared helper library the rest of the GPL
    tree calls into. **Six clusters of new material:** (1) **the
    reusable-helper catalogue** (§22.2, the high-value half) — 17
    functions with signatures/contracts, all palace-scoped so they work
    from an entry function, a poll or a death handler, including
    `all_enemies_dead`'s six-class union census with its hardcoded
    "doesn't count as an enemy" title list, `Setup_Rescue_Heroes`' "call
    me BEFORE setup_rescue_buildings" contract, and
    `High_Level_Hero_Birth` as a **shared extensible per-`#QNumber_*`
    starting-hero hook**; (2) **the difficulty-tier system** (§22.3) — a
    post-victory "keep playing" harassment driver in four layers (roster
    → dispatcher → tier driver → install site), installed by 12 of 19
    quests, with **no runtime difficulty input at all** (the tier is a
    literal function reference authored into each victory branch);
    retuning is two numbers, adding a fifth tier is four small edits in
    one file, and expansion mode has none of it; (3) **sequential
    message flags** (§22.5) — `$IsMessageFlagPresent` + the
    `Message_Check_N` root-agent registers, a named subsystem for
    queueing tutorial messages behind the player's dismissal of the
    previous one; (4) **three post-victory/deadline patterns** (§22.4) —
    `rescue_keep_playing` as a deliberately *downgraded* thread in the
    slot victory just vacated, `*_victory2` as a **deadline arbiter**
    rather than a second win condition, and the **~1 800 000 ms interval
    ceiling with its tick-counting workaround**; (5) **`Lair_extra_delay`
    + `Lair_Delay_Override`** (§22.7) — a global per-quest one-integer
    lair pacing knob, data-default 7000 in `Misc_Data.dat`, consumed in
    `Lair.gpl`, overwritten once in the shipped game, plus the
    `$HasAttribute` feature-detection pattern its expansion-only sibling
    forces on both reader and writer; (6) **the §22.6 cluster, ten
    items** — `$EnableUnitType` as the base game's main mid-quest
    progression device (with `$ListCompleted`/`$ListCompletedTitles`),
    the slot inversion proving `"VictoryCondition"`/`"VictoryCondition2"`
    carry **no engine meaning**, `$GetNearestHiddenCoord` (the only
    out-parameter primitive in the pass), the rain-of-lightning ambient
    harasser, **the script slot as a one-shot mailbox between two
    files**, `#Allow_Cloned_Quest_Item` + `$AgentHasInventoryItem` +
    `$ListSubtypesInRadius`, retiming/killing *another agent's*
    `"SleeperScript"` under an `$IsRunning` guard, `$SetDrawEffects`
    recolor-without-art, **temporary invulnerability** as
    `"Type" = "Invulnerable"` + `#ATTRIB_NotFlaggable` +
    `#ATTRIB_NotSpellTarget` (all reversible), and `$EnchantWizTower`.
    **§20.9's incidental lead CONFIRMED as a shipped defect** (§22.8):
    `Setup_High_Level_Members` writes
    `$setattribute(thisagent,#ATTRIB_StartedwithThisUnit,1)` — base 3060
    / mx 3030 — where `thisagent` is the **rescued guild building**
    (the function is threaded with `Bldg` as its agent) while the
    `$advance_to_level(Member, …)` on the line above targets the hero;
    the correct form is 1870 lines earlier in `setup_hero_level`
    (1189-1190). Refines §20.9's wording: the write is in
    `Setup_High_Level_Members`' `Members` loop, not `rescue_buildings`'
    spawn-drain loop. Harmless only because nothing in the `.gpl` tree
    reads that attribute — don't copy it. **RESOLVED §20.9's "base twins
    of the rescue/hero-level helpers not diffed"** — all now read at
    their base lines and catalogued, `setup_hero_level` identical line
    for line. **ADVANCED §19.12's `$LearnSpell` third argument: it is
    optional** — all four base-game sites pass two arguments
    (3831-3832; `GPL/Hero_Births.gpl` 530-531) against §19.9's seven mx
    `FALSE` sites; meaning still unread, plus a shipped comment ("set
    the Varg's level to 10 so that he actually learns the aforementioned
    spells") hinting spell learning is **level-gated** — UNVERIFIED.
    **ADVANCED §20.7's voice toggles** — first shipped `1` calls, so the
    argument is a plain enable/disable. **NARROWED, still open:**
    `$SetPlayerTeamNumber`'s scope (two more one-call-per-palace sites,
    but `$GetPlayerTeamNumber` is demonstrably called on a non-palace
    agent and compared to a palace's value, which is what per-player
    scope predicts). **Not answerable here** (absent entirely, §22.9):
    `Self_Estimation`/`Enemy_Estimation`, `=`-in-a-condition (zero
    instances in 4358 lines), the Marketplace `"Closed"` writer,
    `MusicTracks.txt` indexing. **New/kept UNVERIFIED:** title-value
    case-sensitivity in both the `$ListTitles` and `==` forms — §22.8
    shows the shipped game is unusually *weak* evidence here because
    every case-mismatched call fails toward granting victory, and
    identifies the one decidable test (`all_enemies_dead`'s lowercase
    `troll`/`ratman`/`skeleton`/`zombie` would make `DAY_OF_RECKONING`
    unwinnable if `==` is case-sensitive); the 1.8 M ms ceiling as an
    engine behavior; what installs `"SleeperScript"`;
    `$SetDrawEffects`' argument set; what `$EnchantWizTower` changes;
    `Magical_Repair`'s caller; the individual jobs of
    `#ATTRIB_NotFlaggable`/`#ATTRIB_NotSpellTarget`; and whether
    uninitialised locals are reliably zero (a second and third shipped
    instance found). §22.9 lists the full recombination set — including
    an "absent from this file entirely" list — so nobody re-opens 4358
    lines hunting for more.

## Prioritization Note

Don't start with "read all 306 files." Let real modding needs pull
sections into existence. Whatever gets pulled in must meet the evidence
standard above.

## Process Notes for Future Sub-Agent Dispatches

- Use `general-task-execution` (full tool access), not `context-gatherer`
  (read-mostly — will ask the user to run commands manually instead of
  writing findings itself).
- For investigation, use `grep_search`/`read_file`/`read_files` directly —
  no shell needed. If a script is genuinely needed (e.g. extracting CAM/
  STRT data), overwrite `utility/test_decoder.py` (the project's one
  named, trusted scratch-script convention per `.kiro/steering/majesty-
  modding.md`) and run it via `python utility/test_decoder.py` — don't
  invent new scratch file names, don't reach for PowerShell for tasks the
  dedicated search/read tools already cover.
- Dispatch sequentially, not in parallel, when multiple agents write to
  the same file — concurrent `str_replace`s on one doc will clobber each
  other. Have each agent re-read the target file immediately before
  editing, since prior agents in the sequence may have appended sections
  since it was first read.
- One dispatch in this research thread failed outright with a tool-side
  error before writing anything — always verify via `git status`/`grep`
  that a dispatch's claimed edit actually landed before treating the topic
  as done.
