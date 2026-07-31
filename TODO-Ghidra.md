# Majesty Modding — Ghidra / EXE Patch TODO

Work that requires the Ghidra machine and MajestyHD.exe disassembly/patching.

**Starting a Ghidra-machine session? Start from `GHIDRA_TASK.md`
(repo root), not this file directly** — it points here plus the exact
findings file for the current task, and confirms `Majesty_Files` isn't
needed for any of this. This file is still the source of truth for task
details/status; `GHIDRA_TASK.md` is just the minimal entry point.

## Work Order (read this first — priority NUMBERS below are topic labels,
## not a strict queue)

1. **Priority 1 (Sub-Panel Navigation Action Code) — IN PROGRESS, continue
   this first.** Was actively being worked when the Ghidra machine ran out
   of monthly tokens; pick back up where that session left off.
2. **Priority 3.4 (Research Item Click Dispatch) — do this NEXT, out of
   its numeric order.** No dependency on Priority 1 (different target
   functions — `FUN_004a8510`/`FUN_004a94c0` vs. the code-8013 sub-panel
   dispatcher/`OpenPanelByName`), so it doesn't need to wait. Bumped ahead
   because it gates the most other open work: `SMNUResearch/FUTURE_TODO.md`
   Priority 3.6 (new research/purchase button), `TODO-New-Hero-Requirements.md`
   §5's recruit-cost gap, and `TODO-New-Building-Requirements.md` §7(E)'s
   combined-case gap all resolve once this lands.
3. Resume remaining priorities in their existing numeric order (2, 3, 3.5,
   4, 5, 6) after 3.4 is done, unless a future note here says otherwise.
4. **Priority 7 (GPL engine-primitive semantics) is explicitly LAST** —
   it's a batch of small "what does this primitive actually do outside its
   one shipped call site" questions from the now-complete GPL Rules pass.
   None of them block a modding workflow. Pick individual rows up
   opportunistically when you're already in adjacent code rather than
   scheduling the section as a unit.

(Not renumbering the sections below to match this order — "Priority 3.4"
etc. are referenced by that exact label from `TODO.md`, `TODO-GPL-Deepdive.md`,
`TODO-New-Hero-Requirements.md`, `GPL_MODDING_GUIDE.md`, and
`SMNUResearch/FUTURE_TODO.md`; relabeling risks stale cross-references
without actually changing what work gets done.)

**When you complete a task or discover new info, update THESE files:**

| What you found | Update this file |
|----------------|-----------------|
| New exe address / function ID | This file → "Known EXE Addresses" table below |
| Panel format / SMNU behavior | `SMNUResearch/findings/smnu_parser_decompilation.md` |
| Action codes / click handling | `SMNUResearch/findings/action_codes_decoded.md` |
| Panel navigation specifics | `SMNUResearch/findings/nav_button_pattern.md` |
| Widget type constructors | `SMNUResearch/findings/smnu_parser_decompilation.md` |
| Scroll widget / type 6/9 | `SMNUResearch/FUTURE_TODO.md` (Priority 3.5 section) |
| Cheat function internals | `CAM_MODDING_GUIDE.md` (new section if confirmed) |
| Particle system engine behavior | `CAM_MODDING_GUIDE.md` (particle section) |
| Resource load order / scope | `CAM_MODDING_GUIDE.md` (Quest CAM Loading section) |
| General progress / completion | `TODO.md` (root) + mark done here |

---

## Priority 1: Sub-Panel Navigation Action Code

**Goal:** Enable multi-page building research panels via a new action code.

**Evidence this needs an exe patch (not just data authoring):** `PanelTest_Quest`
concretely proved widget insertion itself works — a genuine 5th widget was added
to MX03 and rendered/functioned correctly — but every action code/target
combination tried for *forward* navigation (System B format, code 4004 target=7,
code 8851 action=83, code 8013 with a non-return target) was silently ignored.
Only code 8013 targeting the parent (return) works. See commits `8ba9226`
through `e7e2882` in PanelTest_Quest, and `SMNUResearch/FUTURE_TODO.md`
("Building Sub-Panel Navigation") for details.

**Steps:**
1. Find the building sub-panel click handler (the function that checks for code 8013)
2. Identify where it rejects/ignores unknown codes
3. Add new code path: `if (code == 8852) { OpenPanelByName(actionID_as_4CC, 0); }`
4. Likely requires a code cave (jump to new code in unused exe section)

**Start from:** `FUN_004b0ce0` (believed to be `OpenPanelByName` — confirm first).
Cross-ref with action code 8013 handler to find the dispatcher.

**Record results in:** `SMNUResearch/findings/action_codes_decoded.md`

**What this enables:**
- Navigation buttons in SMNU data: `[1024, 5, "PT01", 6, 8852]`
- Multi-page building research panels (6 items per page, unlimited pages)
- Quest-distributable via `<CAM>` (SMNU override confirmed working)

---

## Priority 2: New Building Panel Registration

**Goal:** Allow custom buildings (new DialogID) to have Research panels.

**Steps:**
1. Decompile `FUN_0051b150` (panel class factory) — confirm it maps DialogID → panel name
2. Find where it rejects unknown DialogIDs
3. Either extend the mapping table or add a hook for custom IDs

**Record results in:** `SMNUResearch/findings/smnu_parser_decompilation.md`

**Potential approaches:**
- Modify the panel factory function to handle new DialogIDs
- Hijack an unused building class's vtable handler
- DLL proxy that hooks the panel factory at runtime

---

## Priority 3: Scroll List Widget for Research Panels

**Goal:** Determine if type 6 (scrollable list) can replace fixed button slots in research panels.

**Steps:**
1. Decompile `FUN_00495790` (believed to be research panel populator)
2. Check: does it look for type 6 list widgets, or only fixed button widgets?
3. If buttons-only: assess patch difficulty to make it populate a type 6 list

**Record results in:** `SMNUResearch/FUTURE_TODO.md` (Priority 3.5 section)

**Context:** Type 6 and type 9 constructors are at `FUN_006d0dd0` and `FUN_006cc5d0`.
See `SMNUResearch/FUTURE_TODO.md` for geometry examples and known behavior.

---

## Priority 3.4: Confirm Research Item Click Dispatch Mechanism

**Goal:** Re-derive via actual Ghidra decompilation (not binary-patch
experimentation) the mechanism that dispatches clicks on individual
research/purchase items WITHIN an already-open panel — distinct from the
panel-OPEN mechanism (Priority answered, see "DEFINITIVE ANSWER" section
above and `findings/exe_disassembly_results.md`).

**Background:** An earlier `exe_patcher.py` session reported this
architecture but never confirmed it via decompilation/disassembly:
- `FUN_004a8510` registers all research buttons at startup (reported: 26)
- Each via `FUN_004a83e0(cost_expr, time_expr, level, buttonID, iconIdx,
  controlID)`, stored in a map keyed by control_id
- Click handler `FUN_004a94c0` routes by control_id RANGE per building
  (reported example: Marketplace 5040-5043)
- Empirically, hijacking control_id `0x13B3` (PowerfulItem slot) via binary
  patch did redirect that button's cost to a test GPL expression in-game —
  so SOME registration/dispatch-by-id mechanism is real, just not
  independently re-verified at the disassembly level

**Steps:**
1. Confirm/correct `FUN_004a8510` and `FUN_004a83e0` addresses and
   signatures via decompilation
2. Confirm the "26 buttons" count and control_id ranges per building
   (at least Marketplace 5040-5043, ideally all buildings with research)
3. Confirm `FUN_004a94c0` is the actual click dispatcher and how strictly
   it validates control_id ranges (does it reject ids outside the
   registered set, or fall through silently?)
4. Determine whether an UNUSED/free control_id already exists in any
   building's registered range that has no widget currently pointing at
   it (would allow a new button without needing a NEW registration)

**Record results in:** `SMNUResearch/findings/exe_disassembly_results.md`
("Research Item Click Dispatch" section) — replace the UNCONFIRMED framing
once addresses/ranges are independently verified.

**Relevant to:** `SMNUResearch/FUTURE_TODO.md` Priority 3.6 (new
research/purchase button) — this dispatch mechanism determines whether
that task is achievable without an exe patch or not.

**Also relevant to:** `TODO-New-Hero-Requirements.md` §5 (Recruitment) —
that doc's GPL/data-side trace found no GPL-side cost-check/`$SpawnUnit`
call site for plain (non-Embassy) guild recruit buttons, strongly
suggesting the recruit button's gold check + spawn happens entirely
exe-side (panel click handler), the same class of gap as the research-item
click dispatch above. Confirming/correcting `FUN_004a94c0`'s dispatch
behavior (or finding the equivalent handler for the "Recruit" action
code/control_id, Action ID 75 / Handler Code 8009 per
`SMNUResearch/findings/action_codes_decoded.md`) would resolve both that
doc's open item and this one — same disassembly work, applied to the
recruit button specifically. Record findings for the recruit-specific case
in `TODO-New-Hero-Requirements.md` §5 as well as here.

**Also relevant to:** `TODO-New-Building-Requirements.md` §7 (the
combined "building that recruits a new hero" case) — that section's item
(E) flags the same open question (does the recruit-click gold-check/
`$SpawnUnit` step behave differently for a brand-new building vs. an
existing one) as genuinely unknown for the combined scenario specifically.
No new disassembly target beyond what's already scoped above — resolving
this item resolves that one too. Update `TODO-New-Building-Requirements.md`
§7(E) if/when this lands.

---

## Priority 3.5: Confirm GDB4 Out-of-Range STRT References (Debugger Panel)

**Goal:** Confirm whether GDB4's two "extra" widgets (in `Data/textdata.cam`)
are dead code, or are populated without going through the normal STRT
string lookup.

**Background:** `smnu_compiler.py` (SMNUResearch/) strictly validates that
every tag-7/tag-33 string index resolves within the panel's paired STRT
table — this is exactly the check that would have caught the original
null-STRT-handle crash (see TASK_smnu_parser_decompile.md). Running it
against all 169 real panels found ONE exception: GDB4 (GPL Debugger UI
panel, `Data/textdata.cam`) has two type-0 button widgets referencing STRT
indices 28 and 29, but its own paired STRT only has 28 strings (valid
0-27). Confirmed via direct file reads (not a load_panels() pairing bug —
see `utility/test_decoder.py`). The game evidently doesn't crash on this
panel in normal play, so *something* prevents those two indices from ever
being resolved.

**Steps:**
1. Find where GDB4 is loaded/opened (likely gated behind a debug/dev mode
   flag — search for xrefs to the "GDB4" string, similar to the SMNU
   section string search in TASK_smnu_parser_decompile.md)
2. Decompile the code path that populates those two specific button
   widgets (offsets/action codes 2016/2017 in the SMNU — see
   SMNUResearch/FUTURE_TODO.md "Known Data Quirk: GDB4" for exact geometry)
3. Determine: are these buttons ever actually shown/clickable, or is this
   panel only reachable via a debug build/cheat that never exercises them?
4. If they ARE reachable: find where their label text actually comes from
   if not tag-7's STRT lookup (hardcoded string? separate resource?)

**Record results in:** `SMNUResearch/FUTURE_TODO.md` ("Known Data Quirk:
GDB4" section) and update `smnu_compiler.py`'s validation/exclusion if the
finding changes how string refs should be checked.

---

## Priority 4: Expose Cheat Functions to GPL

**Goal:** Add GPL primitives that call internal cheat engine functions.

**Steps:**
1. Find cheat string handler in exe (handles "revelation", gold cheats, etc.)
2. Identify the internal functions cheats call (map reveal, resource add)
3. Create new GPL primitive dispatch entries pointing to those functions
4. Test: `$RevealMap()`, `$AddGold(amount)` from quest GPL

**Record results in:** `CAM_MODDING_GUIDE.md` (new "Engine Cheats" section if confirmed)

**Context:** Some cheats already call GPL (`cheat_wave_undead`, `cheat_wave_raiders`).
The reverse direction (GPL → cheat internals) should be structurally similar.

---

## Priority 5: Building-Specific EXE Research (from `TODO-New-Building-Requirements.md`)

**Goal:** Resolve the building-specific engine internals that
`TODO-New-Building-Requirements.md`'s research (all 8 sections
complete) could not resolve from GPL/XML/`.dat`/CAM source alone. None
of these have a hero-side equivalent — they're genuinely new targets,
not overlap with Priority 1-4/3.4 above.

### 5.1 Building Placement/Collision Footprint Validation

**Why this needs Ghidra:** no dedicated footprint/collision-size field
exists in `M_Buildings.xml`, `Building_Data.dat`, or the documented DUNT
binary field list (confirmed by direct grep across all three — see
`TODO-New-Building-Requirements.md` §2's "Footprint/collision size"
item). The only spatial data confirmed anywhere is the per-frame
`(x_off, y_off)` sprite hotspot. Whether the engine derives a
placement/overlap collision box from that sprite bounding box, from an
undocumented DUNT field, or from something else entirely is unconfirmed.

**Steps:**
1. Find the live placement-cursor validation code (triggered when the
   player drags a building icon over the map before clicking to place)
2. Identify what data it reads to determine "does this footprint
   overlap an existing building" — sprite dimensions? a DUNT field not
   yet reverse-engineered? a fixed per-building-class constant?
3. Cross-check against the RGS `.q`-file generation-time overlap
   prevention (`.kiro/steering/majesty-modding.md`'s "Overlap
   prevention" note) — confirm or refute whether live placement and RGS
   generation-time placement share the same underlying collision-size
   lookup, or are two unrelated code paths

**Record results in:** `TODO-New-Building-Requirements.md` §1/§4
(footprint items) and `CAM_MODDING_GUIDE.md` if a new DUNT field is
found.

### 5.2 `$DisableUnitType`/`$EnableUnitType` Internal Storage

**Why this needs Ghidra:** these are real, GPL-called, compiler-
recognized engine primitives (confirmed listed in `SDK/Extras/GPL User
Define[d] Language template for Notepad++.xml`'s `Keywords4` block,
extensively used in `Rules/Demo.gpl`/`epic_quest_scripts.gpl` to gate
what appears in the build menu) with zero GPL-visible implementation.
What internal flag/table they write to, and whether it's per-player or
global, is unconfirmed — see `TODO-New-Building-Requirements.md` §4.

**Steps:**
1. Find the primitive's dispatch entry (same GPL-primitive-table
   mechanism as any other `$Function` — cross-reference with however
   other confirmed primitives like `$SpawnUnit` were located)
2. Identify what it writes (a per-player bitmask? a flag on the
   unit-type's compiled DUNT record?) and where that data is read at
   build-menu-render time

**Record results in:** `TODO-New-Building-Requirements.md` §4 and
`CAM_MODDING_GUIDE.md` (new "Engine Primitives" section if one doesn't
exist yet).

### 5.3 ~~`$SetBuildingLimit`/`$RemoveBuildingLimit`/`$RemoveAllBuildingLimits` Semantics~~ — RESOLVED, DO NOT WORK

> **RESOLVED from official SDK documentation, no Ghidra needed.** The
> "GPL (Game Play Language) Reference" PDF documents all three. See
> `GPL_LANGUAGE_REFERENCE.md`:
>
> - **`SetBuildingLimit(string type, integer limit)`** — *"Limits **all
>   players** to no more than the specified number of buildings for the
>   specified type. When the limit = 0 this has much the same effect as
>   `DisableUnitType`. **Note that these limits are NOT enforced by
>   `SpawnUnit`.**"*
> - **`RemoveBuildingLimit(string type)`** and
>   **`RemoveAllBuildingLimits()`** — remove limits imposed by
>   `SetBuildingLimit` **or by the player in the Build Tree Editor**.
>
> So: **global, not per-player**; keyed by **type name**; a **count**, not
> a boolean; and `SpawnUnit` bypasses it entirely.
>
> **Bonus finding worth following up elsewhere:** the docs reveal a
> **Build Tree Editor available to players in freestyle games only**,
> which can itself impose building limits. That is a player-facing
> feature nothing in this project had identified, and it is plausibly
> connected to the freestyle conflicting-faction behavior recorded in
> `TODO-New-Building-Requirements.md` §10.8. Not a Ghidra task.

**Original steps (do not execute):** find the dispatch entries, determine
limit keying, scope, and enforcement point.

**Record results in:** already recorded — `GPL_LANGUAGE_REFERENCE.md` and
`TODO-New-Building-Requirements.md` §4.

### 5.4 `Menu` Value Engine-Keying + Graveyard/Sewer Anomaly

**Why this needs Ghidra:** `Menu` values 0/1/2/3 correlate strongly with
build-menu category (temple/guild/ordinary/non-buildable) and with
`Flags value="IsGuild"`, but which field the engine actually keys off of
for categorization is unconfirmed, and two Monster-`CanUse` lairs
(`Graveyard`, `Sewer`/`BBN1`) break the otherwise-consistent
Monster→`Menu="2"` pattern by using `Menu="3"` instead — see
`TODO-New-Building-Requirements.md` §2.

**Steps:**
1. Find the build-menu-population/categorization code (likely near
   whatever the `$DisableUnitType` render-time check in 5.2 lives)
2. Confirm whether it reads `Menu` or `Flags value="IsGuild"` (or both)
   for category placement
3. Check whether `Graveyard`/`Sewer`'s `Menu="3"` value causes any
   different runtime behavior than other `Menu="2"` monster lairs, or
   is a harmless inconsistency in the shipped data

**Record results in:** `TODO-New-Building-Requirements.md` §2.

### 5.5 Construction-Stage `Build`-Set Selection Logic

**Why this needs Ghidra:** buildings have 2-3 populated `Build`-family
ImageSets (setIDs 80-82) per building, but no GPL/XML/`.dat` source
selects among them based on construction progress (%HP built) —
`Building_Births.gpl`'s `basic_birth`/`magical_birth`/
`BuildingReachedMaxHP` only reference `birthscript`/`birthscript2`
function pointers, never an ImageSet name. See
`TODO-New-Building-Requirements.md` §1.

**Steps:**
1. Find the code that renders a building's current construction-stage
   sprite (likely reads `#ATTRIB_FirstStageBuilt` or a raw HP percentage
   directly)
2. Confirm whether it selects `Build`/`Build-2`/`Build-3` by a fixed
   percentage-of-max-HP threshold, or some other mechanism
3. Also resolve whether the numbered `Die`-family variants (setIDs
   97-103, confirmed present-but-not-content-verified on buildings) hold
   genuinely distinct frame content or are unused/reserved slots

**Record results in:** `TODO-New-Building-Requirements.md` §1.

### 5.6 Ordinary-Building Minimap Representation

**Why this needs Ghidra:** only Palace (`ABJ1`/`ABJ2`/`ABJ3`) has a
dedicated `Minimap` ImageSet among all 91 `AB*`/`BB*` building/lair
records checked — the other 88 have none, yet presumably still show
something on the minimap. Heroes, by contrast, universally have a
`Minimap` set (zero exceptions across 15 heroes checked) — a genuine
building-vs-hero asymmetry. See `TODO-New-Building-Requirements.md` §1.

**Steps:**
1. Find the minimap-rendering code path
2. Determine whether ordinary buildings render as a generic
   engine-computed dot/rectangle (using player color/team only, no
   per-building sprite), a downscaled existing ImageSet (e.g. `Active`),
   or aren't individually represented at all

**Record results in:** `TODO-New-Building-Requirements.md` §1.

---

## Priority 6: Hero Recruitment EXE Research (from `TODO-New-Hero-Requirements.md`)

**Goal:** Resolve the recruitment-specific engine internals
`TODO-New-Hero-Requirements.md` §5/§6 flagged as needing Ghidra, beyond
the recruit-button click dispatch already scoped in Priority 3.4 above
(don't duplicate that item — these are the narrower follow-ons it
didn't cover).

### 6.1 Hero `Cost` XML Field's Actual Consumer

**Why this needs Ghidra:** every playable hero declares a `Cost` value
in `M_Characters.xml`, but no GPL function anywhere reads it via
`thisagent's "cost"` or an equivalent accessor. The one confirmed
AI-facing gold-charge function (`Enemy_Guild_Spawn`) uses an unrelated
hardcoded flat value (600) instead of the hero's own `Cost` — a genuine
unexplained mismatch. See `TODO-New-Hero-Requirements.md` §5 item 4.

**Steps:**
1. Find the recruit-button click handler (likely the same function
   Priority 3.4 targets for the Recruit action code/control_id)
2. Confirm whether it reads the hero's `Cost` field from the compiled
   unit-type table at click time, or does something else entirely

**Record results in:** `TODO-New-Hero-Requirements.md` §5.

### 6.2 `RecruitDelay` Enforcement Mechanism

**Why this needs Ghidra:** `RecruitDelay` is a universal per-hero XML
field (4000ms-20000ms range across sampled heroes), and
`#DelayRecruitCheckPeriod`'s GPL comment is suggestive ("will be
recruited if individual recruitment delay is up") but has zero GPL
call sites anywhere in the corpus reading it as a real timer argument.
See `TODO-New-Hero-Requirements.md` §5 item 4.

**Steps:**
1. Determine whether a per-guild recruit cooldown timer exists
   exe-side at all, and if so what field it reads
2. If found, confirm it reads the hero's own `RecruitDelay` value
   rather than a fixed/global cooldown

**Record results in:** `TODO-New-Hero-Requirements.md` §5.

### 6.3 `$BuildingIsRecruiting` Primitive Contract

**Why this needs Ghidra:** this engine primitive is consumed inside
`GuildHasOpenSlots` (the one real, confirmed, shared capacity gate for
recruitment) but has no GPL definition anywhere — its boolean return
contract is used but never explained. See `TODO-New-Hero-Requirements.md`
§5 items 2 and 4.

**Steps:**
1. Find the primitive's dispatch entry and decompile its body
2. Determine exactly what condition it checks (building under
   construction? already at capacity via a different counter? something
   else?)

**Record results in:** `TODO-New-Hero-Requirements.md` §5.

**Cross-reference, not duplicated:** whether a genuinely new hero
recruited via a brand-new building's `DialogID` behaves any differently
at any of 6.1-6.3 than an existing building is the open question
`TODO-New-Building-Requirements.md` §7(E) flags for the combined case —
resolving 6.1-6.3 for the general case resolves that cross-reference
too, no separate building-specific variant of this work is needed.

---

## Priority 7: GPL Engine-Primitive Semantics (from the completed `Rules/` pass)

**Goal:** Resolve the engine-side primitive behaviors the GPL deep dive's
quest rules pass (Batches A-G, now complete — `TODO-GPL-Deepdive.md`
Completed item 16, `GPL_QUEST_RULES_REFERENCE.md` §16-§22) could not settle from
source. These are collected here as one section because they share a
shape: the GPL call sites are fully read and cited, the primitive's
implementation is exe-side, and no amount of further GPL reading will
close them. `GPL_QUEST_RULES_REFERENCE.md` §22.8's closing note is the canonical
list; this is the Ghidra-facing half of it.

**Low priority as a group** — none of these block a modding workflow the
way Priority 1/3.4 do. Each is "I know how to use this primitive from the
shipped examples, but not what it will do outside them." Pick them up
opportunistically when already in adjacent code.

| Primitive / behavior | What's unknown | Cited at |
|---|---|---|
| `$SetDrawEffects` | Full argument set. One shipped call site, `"gray"` is the only string ever passed, the integer argument's meaning is unread. Recolors a unit without new art, so it's a cheap effect for modders IF the arguments are known. | §22.6h |
| `$EnchantWizTower` | What it actually changes. `Magical_Repair` sits unreferenced in the same file, suggesting self-repair is part of it — adjacency, not evidence. | §22.6j, §22.2 |
| Thread-interval ceiling (~1 800 000 ms) | Whether the engine really enforces it and what it does when exceeded. Two shipped comments name it, one works around it by counting firings instead, no interval in the file exceeds it — the only evidence is the developers' own comment. | §22.4d |
| ~~`$SetEffectorDirection`~~ | **RESOLVED — no Ghidra needed.** Official SDK docs: *"The direction of the effect. 0–31, with 0 being NORTH and increasing values going clockwise around the agent."* See `GPL_LANGUAGE_REFERENCE.md`. | §21.4e |
| `$DropGoldEveryone` | The split rule (per hero? per team? equal shares?). **Still open** — absent from the official function list entirely, so it is a GPL library function or an undocumented primitive. | §21.5b |
| ~~`"clear"` as a `$SpawnUnit` flag~~ | **RESOLVED — no Ghidra needed.** Official SDK docs: *"any units under the footprint of the new unit will be removed. This is useful when spawning buildings."* | §21.7 |
| `-1` as an effector duration | **Narrowed.** Official docs give **`"infinite"` as a documented string option** on `$CreateEffector`, and `after` to fire the effect's DeathScript on completion — but say nothing about a `-1` integer duration. So `-1` is either undocumented or incidental. | §21.7 |
| `#ATTRIB_CurrentEvent` | Value→event mapping beyond the 1-4 the Fairgrounds tourney uses. | §21.6e |
| `$ElvesVoice_setOperative` / `$dwarvesVoice_setOperative` | What they actually silence. The argument is now confirmed a plain enable/disable boolean (Batch G found the first `1` calls) — the effect is still engine-side. | §20.7, §22.8 |
| Whether the engine ever writes `"type"` itself | GPL writes it constantly (the `$ListObjects` class register, §20.2); whether the engine also does is unconfirmed, which matters for any census code. | §20.2 |
| `$SetPlayerTeamNumber` scope | Per-player or per-agent. **Narrowed three times, still unproven** — Batch G showed the *getter* demonstrably accepts a non-palace agent and resolves through its owner, which is what per-player scope predicts, but that's not proof for the setter. | §19.8, §22.8 |
| `#ATTRIB_NotFlaggable` / `#ATTRIB_NotSpellTarget` | What each does individually. The three-write temporary-invulnerability recipe and its exact reversal are confirmed; the split of responsibility between the writes is read off their names. | §22.6i |

**Record results in:** `GPL_QUEST_RULES_REFERENCE.md` at the cited section
(each row names it — every row in this table cites §19-§22, which live in
the quest reference, not `GPL_MODDING_GUIDE.md`; see `TODO.md`'s "See also"
note on the §-range split), and tick the matching entry in §22.8's
"engine-side semantics" list.

**Already tracked elsewhere, do not duplicate here:** the `$NewThread`/
`$RunThread`/`$ResumeThread`/`$KillThread` scheduler semantics and the
`$building_upgraded`/`$DoMarketDay`/`$EndMarketDay` engine-invocation
questions are in the Verification Tasks table below; the research-button
click dispatch is Priority 3.4; `$DisableUnitType`/`$EnableUnitType` and
the building-limit primitives are Priority 5.2/5.3.

**Not Ghidra work — routed to `TODO-GameTests.md` instead:** title-value
case-sensitivity (one `DAY_OF_RECKONING` playthrough settles it),
whether uninitialised GPL locals are reliably zero, what `=` in a
condition compiles to, whether GPL discards extra call arguments, and
whether `$Make_PC_Hunter` without `$Reset_Tasks` takes effect promptly.
See that file's "GPL Language Semantics" section.

---

## Low Priority: `CanIBuildThisBuilding` Callback Contract

**Background:** `GPL/Rules/construction_rules.gpl`'s
`CanIBuildThisBuilding(agent thisBuilding, list dependencies)` is
confirmed (see `GPL_QUEST_RULES_REFERENCE.md` §16.1) to be an exe-invoked GPL
callback — zero GPL call sites anywhere in the tree, the engine calls it
by name, returns 0 to permit a build and a non-zero `#chat_*` code to
refuse it. It's a real, modder-extensible placement-prerequisite hook
(per-building-title proximity rules). Two things about the contract
can't be resolved from GPL/XML source:

**Steps:**
1. **When is it called?** Build-menu entry filtering vs. live
   placement-cursor validation. Evidence leans placement-time (the
   function does `$ListObjects(thisbuilding, ...)` measuring distance
   from the candidate building's own position, meaningless for a
   position-less menu entry) — but that's an inference from argument
   usage, not a trace. Also worth confirming whether it's called
   repeatedly during cursor drag or once on click.
2. **What does the engine put in `dependencies`?** No shipped branch
   reads the parameter, no `M_Buildings.xml` field feeds it (grepped
   `Depend`/`Prereq`/`Requir`, zero matches), and the only description
   is a commented-out design sketch referencing never-implemented
   `"maxBuildRange"`/`"buildRequirements"` fields. If the engine passes
   something real, this is a free, already-wired input a modder could
   use.
3. While in this code, check whether `$removetitles` exists in the
   base-game exe at all — it has zero call sites in the base `GPL/`
   tree and appears only under `GPLMx/` (§16.1's mx-diff finding).

**Record results in:** `GPL_QUEST_RULES_REFERENCE.md` §16.1 and
`TODO-New-Building-Requirements.md`'s §4 placement items (both already
cross-reference this question).

---

## ~~Low Priority: Freestyle Victory-Condition Dropdown Row Definitions~~ — LARGELY RESOLVED WITHOUT GHIDRA

**RESOLVED, keep for the residual question only.** The dropdown labels
were found in plain CAM `STRT` data, not the exe: `Data/gpltext.cam`'s
`GOAL` entry (header count = 4) holds the four victory labels, and
`textdata.cam`'s `GMTX` holds the companion status/prompt strings. See
`GPL_QUEST_RULES_REFERENCE.md` §16.3's correction block. The same pass also
resolved the sibling special-event registry the same way (§17.7:
`mx_gpltext.cam`'s `EVSC`/`ENTX`/`EDTX`).

**No Ghidra needed for the original question.** Two residual items, both
**in-game tests** now tracked in `TODO-GameTests.md`, not disassembly:
1. Does adding a 5th `GOAL` row produce a 5th dropdown entry (and make
   `$GetVictoryConditionIndex()` return 4)? The header has an explicit
   count field, but the engine may read a fixed 4.
2. The `GOAL` row order does not obviously match the GPL branch indices
   (`GOAL` row 0 = "Survive", but §16.2's dispatcher handles survive at
   `index == 2`) — the real mapping needs establishing empirically via
   the dispatcher's own `$debugout` of the index.

Only escalate to Ghidra if the in-game tests come back ambiguous.

**Original background retained below for reference:**
`GPL/Rules/victory_conditions.gpl`'s
`SetVictoryCondition()` dispatches on `$GetVictoryConditionIndex()` — an
engine primitive reporting which row the player selected in the setup
menu's victory dropdown. Confirmed (see `GPL_QUEST_RULES_REFERENCE.md` §16.2/
§16.3): **the dropdown's row labels exist nowhere in GPL, nowhere in
`M_*`/`MX_*` XML, and nowhere in any `.mqxml`** (grepped for `Victory`,
zero matches) — so adding a genuinely new selectable victory condition
is an exe/UI change, while repurposing an existing row's meaning is
GPL-only and fully supported.

**Steps:**
1. Find where the victory dropdown's row list/labels are defined
   (likely UI/`.cam` string data — cross-reference the SMNU/STRT panel
   research already done in `SMNUResearch/`, since this may just be a
   panel string table nobody has connected to this feature yet).
2. Confirm the index→row mapping (§16.2 notes the GPL branch order is
   2,1,0,3 — NOT dropdown order — so the mapping is currently only
   discoverable by reading the function's own
   `$debugout(911,"victory condition index:",index)` at runtime).
3. Assess whether a 5th row can be added via panel/string data alone
   (if the dropdown is SMNU-driven, this might be data-moddable after
   all, which would upgrade the §16.3 verdict) or needs a real exe
   patch.
4. Also resolve what `$GetVictoryConditionIndex()` returns outside a
   freestyle game (a custom quest that calls `$setvictorycondition()`
   with no dropdown ever shown) — this project's own
   `QuestMapGenerator/rgs_format.py` asserts the default behaves as
   "destroy all enemy structures" (index 0), but that's a
   project-internal claim with no source citation behind it.

**Record results in:** `GPL_QUEST_RULES_REFERENCE.md` §16.2/§16.3.

---

## Low Priority: Temple-to-Dauros Level-3 Petrify Unlock Mechanism

**Background:** confirmed (by an experienced modder, then cross-checked
against source — see `GPL_MODDING_GUIDE.md` §11's Petrification
re-verification) that the base game's Petrify spell is cast directly
from the Temple to Dauros building's own panel (`DialogID="AP05"`,
shared across all 3 tiers per `M_Buildings.xml`), and only becomes
available once the Temple reaches Level 3. This is a genuinely different
casting pathway from hero-`AllowedSpells` or monster-attack-spells (which
both have real Action XML + GPLFunction wiring) — no comparable wiring
exists for base Petrify anywhere in XML/GPL/`.dat` source. `Petrify_Begin`
(the GPL function) has no caller anywhere in the `.gpl` tree, and
`Temple_Dauros3`'s XML `<Game>` block has no spell-grant/unlock field
distinguishing it from tiers 1/2 beyond ordinary `Cost`/`MaxHP` fields.

**Why this needs Ghidra:** the Level-3 gate and the actual "cast Petrify"
click handler are both invisible from data alone — this is presumably an
exe-hardcoded per-`DialogID`/per-building-level mechanism (same general
opacity class as the already-documented `DialogID`→panel-factory
hardcoding, Priority 2 above, though a different specific mechanism —
that one is about which PANEL opens, this one is about which SPELL
BUTTONS appear inside an already-open, already-mapped panel based on
building level).

**Steps:**
1. Find the AP05 panel's populate/render code (likely near whatever
   populates other building-panel spell/research buttons generally —
   cross-reference with Priority 3.4's research-button registration
   work, since this may be a related or identical mechanism)
2. Determine what condition gates the Petrify button's visibility —
   reads the building's `Level`/tier directly? A hidden attribute set
   somewhere? Confirm the Level-3-specifically claim mechanically, not
   just by observed behavior
3. Note whether this same level-gated-spell-button pattern exists on any
   OTHER temple/building panel (worth checking once you're in this code,
   low additional cost) — would confirm or refute whether this is a
   general "buildings can gate spell buttons by level" mechanism or a
   Dauros-specific special case

**Record results in:** `GPL_MODDING_GUIDE.md` §11 (Petrification
re-verification section) and `.kiro/steering/majesty-modding.md`'s
Petrification System template if it changes the guidance there.

**Related, still needs a narrower Ghidra pass (source research is
done, and the scope shrank after user input):** `TODO-GPL-Deepdive.md`
Topic 13 resolved the source-side investigation for ordinary guild skills
(Rage of Krolm / Call to Arms via `Guild_Skills.gpl`'s
`DoRageOfKrolm`/`DoAssembly`). **Correction (kept visible, not
overwritten in that doc either):** the original framing treated "how is
Rage of Krolm/Call to Arms triggered" as an open trigger-class question
of the same kind as Petrify's genuinely-unresolved gap — the user
confirmed directly that both are ordinary button clicks inside their own
guild's building panel, the same trigger CLASS as Petrify's AP05 button,
not a separate mystery. So the trigger CLASS no longer needs Ghidra to
confirm. What's still open is narrower: the exe-side click-dispatch code
for these two specific buttons — the same general class of question as
Priority 3.4's research-item click dispatch, not a new mechanism to
discover. Also still genuinely new: `Temple_Krolm`/`Warriors_Guild` are
both single-tier (no `UpgradeTo` chain at all), so whatever gates these
two abilities' panel buttons, it CANNOT be a Level-3-style tier gate the
way Petrify's is — there's no tier to gate on. This is confirmed
structurally different from Petrify's mechanism, not the same gate
reused, so it needs its own decompilation target, not just an assumption
that Priority "Low: Temple-to-Dauros Level-3 Petrify Unlock Mechanism"'s
findings will transfer.

**Steps (guild skills, separate from Petrify's Level-3 steps above):**
1. Find the AP24 (Temple_Krolm)/AP52 (Warriors_Guild) panel populate/
   render code — likely the same general research/spell-button
   registration mechanism as Priority 3.4 and Petrify's AP05, but must be
   independently confirmed since these buildings have no tier to gate on
2. Determine what condition (if any) gates `DoRageOfKrolm`/`DoAssembly`
   button visibility — building's mere existence? A hidden attribute?
   Always visible with no gate at all (plausible given single-tier)?

**Dropped from this Ghidra scope (moved to an in-game test instead):**
whether destroying `Temple_Krolm`/`Warriors_Guild` revokes the
corresponding skill no longer needs decompilation first — no GPL-side
revoke logic exists in `building_death`/`guild_destroyed_common`/
`guild_destroyed_a`, and the likely mundane explanation (the button
lives ON that building's own panel, so losing the only copy just removes
panel+button together, not a separate revocation mechanic) is directly
testable in-game with a duplicate guild, no exe research required. See
`TODO-GameTests.md`'s "Guild Skill Panel Persistence" item. Only revisit
this as a Ghidra item if that in-game test finds surprising behavior
(e.g. the skill remains castable from elsewhere after the building is
destroyed).

**Record results in:** `GPL_MODDING_GUIDE.md` §12 (guild skills section)
and cross-reference from `TODO-GPL-Deepdive.md` Topic 13 if the finding
changes that section's framing.

---

## Low Priority: Investigate "Zoo" Building as a Possible EXE Expansion Point

**Background:** Confirmed via direct data inspection (not yet Ghidra) that
"Zoo" is real but orphaned content: `DialogID`-shaped sprites `ABn1`/`ABn2`/
`ABn3` ("Zoo Level 1/2/3") exist in `DataMX/mx_maindata.cam`, and
`GPLMx/TaskModules/Buildings/Zoo.gpl` has a working `zoo_flag_check`
mechanic (charms a nearby monster to the closest hero via a `RewardFlag`/
`charm_percentage` system, using the same `$control_monster` primitive as
the Cultist's `Charm_Monster` spell). BUT there is no XML building
definition (`M_Buildings.xml`/`MX_Buildings.xml`) referencing `ABn1/2/3`,
and no quest data places it — it's unreachable in normal play. See
`CAM_MODDING_GUIDE.md`'s Visited_Script table note for the full writeup.

**Why this might matter for exe patching:** several patches we want
(Priority 1 sub-panel nav, Priority 2 new building panel registration)
are blocked on needing new vtable slots / DialogID mappings / control_ids
that don't currently exist. An already-reserved-but-unused DialogID
family (with its own sprites already in the game data) is exactly the
kind of "free" slot that might be cheaper to repurpose than carving out
brand new IDs from nothing — IF the exe still has any dormant
Zoo-related building-class plumbing (vtable slots, panel factory
mapping, etc.) sitting unused alongside the orphaned data.

**Steps (low priority, exploratory):**
1. Search the exe for xrefs to "ABn1"/"ABn2"/"ABn3" or "Zoo" — does the
   panel/building class factory (`FUN_0051b150`, see "DEFINITIVE ANSWER"
   section above) have ANY entry for these DialogIDs, even if currently
   unreachable from the dataset?
2. If a vtable/class mapping exists: what panel (if any) does it point to?
   Does it reference a stub/dialog research panel that was never finished
   (would answer the "any dialog/research panels exist" question)?
3. If dormant plumbing IS found: assess whether repurposing it (redirect
   an existing-but-dead mapping to a NEW panel/DialogID of our choosing)
   is lower-risk than adding a brand new vtable entry from scratch
4. If NOTHING exists in the exe for Zoo (i.e., only the data files have
   orphaned content, exe has zero awareness of it): this dead-ends, Zoo
   is not useful as an expansion point, note that and close this out

**Record results in:** `SMNUResearch/findings/exe_disassembly_results.md`
(new "Zoo / Orphaned Content Investigation" section)

---

## Low Priority: Decompile Sound Editor EXE

**Goal:** Reverse-engineer the SDK sound editor executable to understand sound/DSND authoring.

**Record results in:** `CAM_MODDING_GUIDE.md` (sound sections) or new `SoundResearch/` folder if large.

---

## Verification Tasks

| Task | Record in |
|------|-----------|
| Confirm `FUN_004b0ce0` = `OpenPanelByName` | This file (Known Addresses table) |
| Confirm `FUN_00495790` = research panel populator | This file (Known Addresses table) |
| Identify sub-panel click dispatcher function | `SMNUResearch/findings/action_codes_decoded.md` |
| Document resource search direction in `FUN_00679a80` | `CAM_MODDING_GUIDE.md` (Quest CAM Loading) |
| What does `AllocateLocalID` do for particle systems | `CAM_MODDING_GUIDE.md` (particle section) |
| **RESCOPED by official SDK docs — find the engine's appearance swap for player-initiated building upgrades.** The original framing asked whether `$UpgradeAgentAttributes` performs the tier transition. **It does not:** official docs say it *"copies the GPL attribute values from the agent's definition template into its local storage"* — attributes only — while `$ChangeUnitType` changes *"only the appearance"*. So GPL needs both, and a scripted upgrade must call both. **What's left:** the human upgrade path calls only `$UpgradeAgentAttributes` (inside `BuildingReachedMaxHP`), never `$ChangeUnitType`, yet the building visibly becomes its new tier — so the engine swaps appearance itself somewhere in its own upgrade handling. Find that. Secondary: what state `$ChangeUnitType` leaves inconsistent, given a modder reports a crash within seconds unless `$UpgradeAgentAttributes` follows it (now explained in principle — appearance advanced, attributes stale — but not traced). | `GPL_MODDING_GUIDE.md` §2 |
| ~~**Trace `$UpgradeAgentAttributes` and the building tier transition.**~~ *(superseded by the row above)* Building tiers are separate unit types with their own `ImageIDBase` and `.dat` scripts (`ABH1`/`ABH2`/`ABH3`), yet **no shipped GPL calls `$ChangeUnitType` on a building** — all 5 call sites are character shape-shifts. The only call in the human upgrade path is `$UpgradeAgentAttributes`, inside `BuildingReachedMaxHP` (`Building_Births.gpl`). So the tier/sprite swap is exe-side, but **which routine does it is unknown**: (a) `$UpgradeAgentAttributes` resolves the XML `UpgradeTo` field and applies the whole next-tier definition, or (b) it only refreshes attributes and the engine swaps type/sprite separately in its own upgrade handling. **This decides whether a GPL-only scripted upgrade can work at all** — under (b) it would update stats but keep the old sprite. Also worth capturing: what state `$ChangeUnitType` leaves stale, since a modder reports the game crashes within seconds unless `$UpgradeAgentAttributes` follows it. | `GPL_MODDING_GUIDE.md` §2 ("Does the sprite change without `$ChangeUnitType`?") |
| (Low priority) Confirm the exe never calls a GPL "birthscript2" attribute directly (only "birthscript" is known to be engine-invoked, via `NewUnitInit`) — see `TODO-GPL-Deepdive.md` "birthscript vs birthScript2" finding, "Not yet checked / UNVERIFIED" | `TODO-GPL-Deepdive.md` (birthscript/birthScript2 section) |
| (Low priority) Confirm whether the exe calls `$DoMarketDay`/`$EndMarketDay` on a Marketplace's `RevenueScript` thread (only the functions' own leading comments — "called by the ingame code" — are evidence; no GPL-side call site found) | `TODO-GPL-Deepdive.md` (building revenue finding) |
| (Low priority) Find what sets a building's `#ATTRIB_isTaxed`/`#ATTRIB_QuickTax` flags — no GPL/`.dat` set-site found, only read-sites in `collect_tax.gpl` | `TODO-GPL-Deepdive.md` (building revenue finding) |
| (Low priority) Find what exe-side code, if any, calls `HallOfChampions_Bounty_Cost`/`Period` (`Lair.gpl` — pure cost/period lookups, 400/800 gold and 60000/120000ms for bounty_index 1/2) — zero GPL call sites found anywhere in the corpus; unknown whether a "bounty" mechanic exists beyond these two values | `TODO-GPL-Deepdive.md` (Building visit-system deep dive / Retracted Claims update) |

---

## Known EXE Addresses (MajestyHD.exe)

Update this table as you confirm/discover functions.

| Address | Function | Status | Purpose |
|---------|----------|--------|---------|
| 0x006d34d0 | STRT loader | CONFIRMED | Loads STRT by entry name |
| 0x00679a80 | Resource find | CONFIRMED | Resource manager lookup (scope flag 0x80000001) |
| 0x004b0ce0 | OpenPanelByName? | UNCONFIRMED | Opens panel by 4-char name |
| 0x0051b150 | Panel class factory | CONFIRMED | Creates building panel handler from DialogID |
| 0x0063a220 | String setter | CONFIRMED | Where STRT null crash occurs (null deref) |
| 0x0064d330 | Panel factory | CONFIRMED | Allocates panel, connects STRT, parses widgets |
| 0x00668390 | Child widget parser | CONFIRMED | Reads widget stream from SMNU |
| 0x00675b50 | Widget property parser | CONFIRMED | Processes tag-value property pairs |
| 0x006655e0 | Panel header parser | CONFIRMED | Processes panel header block (tag 1000) |
| 0x00495790 | Research populator? | UNCONFIRMED | Fills research panel content |
| 0x006d0dd0 | Type 6 constructor | CONFIRMED | Scrollable list widget (368 bytes) |
| 0x006cc5d0 | Type 9 constructor | CONFIRMED | Scrollbar/slider widget (340 bytes) |
| 0x006d3110 | Type 0 constructor | CONFIRMED | Standard button widget (340 bytes) |
| 0x006d2b80 | Type 1 constructor | CONFIRMED | Widget type 1 (340 bytes) |
| 0x006d2570 | Type 2 constructor | CONFIRMED | Widget type 2 (340 bytes) |
| 0x006d1a20 | Type 5 constructor | CONFIRMED | Text/label widget (352 bytes) |
| 0x00692a10 | Type 12 constructor | CONFIRMED | Largest widget type (464 bytes) |
