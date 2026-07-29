# Majesty Modding — Ghidra / EXE Patch TODO

Work that requires the Ghidra machine and MajestyHD.exe disassembly/patching.

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
| (Low priority) Confirm the exe never calls a GPL "birthscript2" attribute directly (only "birthscript" is known to be engine-invoked, via `NewUnitInit`) — see `TODO-GPL-Deepdive.md` "birthscript vs birthScript2" finding, "Not yet checked / UNVERIFIED" | `TODO-GPL-Deepdive.md` (birthscript/birthScript2 section) |
| (Low priority) Confirm whether the exe calls `$DoMarketDay`/`$EndMarketDay` on a Marketplace's `RevenueScript` thread (only the functions' own leading comments — "called by the ingame code" — are evidence; no GPL-side call site found) | `TODO-GPL-Deepdive.md` (building revenue finding) |
| (Low priority) Find what sets a building's `#ATTRIB_isTaxed`/`#ATTRIB_QuickTax` flags — no GPL/`.dat` set-site found, only read-sites in `collect_tax.gpl` | `TODO-GPL-Deepdive.md` (building revenue finding) |

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
