# Majesty Modding Toolkit — Master TODO

Based on findings from Workshop mod analysis (10 mods/quests) + existing work.
Focus: comprehensive knowledge of engine capabilities for quest/mod creation.

---

## Quest Map Generator Enhancements

### ~~Multi-Kingdom Support~~ ✅ DONE
- [x] Add `slot_configs` parameter to `create_quest()` for >2 player kingdoms
- [x] Support 7Kings-style FFA (up to 7 active player slots + 1 monster slot)
- [x] Each slot gets: name, starting_gold, active flag, sub_items (spawner indices)
- [x] 6 unit tests added (50 total passing)
- [x] Auto-adds Monsters slot at index 7 if not explicitly provided

### Landscape Objects (Trees/Rocks)
- [ ] Document which fractal refs (`xFel`, `xFer`, `xBBC`, etc.) produce which vegetation
- [ ] Test terrain presets with different fractal refs to get trees (current `grass` preset is bare)
- [ ] Consider adding "density" parameter to presets (bare, sparse, forested)

---

## ~~GPL Knowledge Base~~ ✅ DONE

Created `.kiro/steering/gpl-reference.md` (manual inclusion) containing:

### ~~Undocumented Engine Primitives~~ ✅
- [x] All 20+ discovered primitives documented with signatures, purpose, and source mod
- [x] Categorized: Unit/Agent, Stat/Attribute, Building/Kingdom, Spawning, Thread, Effects, Queries

### ~~GPL Gotchas Document~~ ✅
- [x] 22 critical engine behaviors documented with workarounds
- [x] Thread behavior (4 gotchas), Silent failures (5), Crashes (4), Data/binding (4), Timing (2), Compiler (2)

### ~~GPL Patterns Reference~~ ✅
- [x] EventAgent pattern (recurring events)
- [x] Spell/buff Begin/End pattern with effectors
- [x] AI kingdom thread architecture (StandAloneAI 10-thread model)
- [x] Debugging patterns (gold channel, floating numbers, minimap beacons, visual tints)
- [x] Defensive function entry pattern

---

## ~~XML Schema Knowledge~~ ✅ DONE

Added to `quest-and-mod-creation.md` steering file:

### ~~Action/Spell Definitions~~ ✅
- [x] SpellRank (REQUIRED for AI), SpellType (Attack/CombatUtility/4), CharacterLevel
- [x] ValidationScript, EffectorDuration, multiple SpellType stacking, Rate

### ~~Overlay Definitions~~ ✅
- [x] Visible effector pattern (Menu 11, ImageIDBase, AttachmentPointID, TransparentToMouse)
- [x] Invisible timer pattern (Script GPLFunction for expiry callback, StackPriority)
- [x] Static overlays (Info value="Static")

### ~~Building Definitions~~ ✅
- [x] UpgradeTo chain, Multiplier cost escalation, IncomeType (revenue/maintenance)
- [x] Produces (recruitable units), NumberedName flag

### ~~Research/Items/Services System~~ ✅
- [x] "Invisible character as UI slot" pattern (subType="Character" + Menu 8)
- [x] RecruitDelay = research time, birthScript = on-purchase callback

---

## ~~MQXML/MMXML Capabilities~~ ✅ DONE

Added to `quest-and-mod-creation.md` steering file:

### ~~Newly Discovered Tags~~ ✅
- [x] `<GPLSource>GPL</GPLSource>` — source directory for debugger
- [x] `<CAM>` tag — loads raw CAM archives (sound confirmed, sprites theoretically possible)
- [x] Multiple `<Mod>` entries in one .mmxml (15 variants in StandAloneAI)
- [x] Dual-dataset mods (one entry for Majesty, one for MajestyExpansion)
- [x] `base="Any"` risks (misbinding attributes against wrong ruleset)
- [x] Nested description paths (subdirectories work)

### ~~Mod Architecture Patterns~~ ✅
- [x] Palace-prototype-as-entry-point (StandAloneAI pattern)
- [x] Expression-only BCD as tuning mod
- [x] Same-name function override
- [x] Mod load order and override behavior

---

## ~~Debugging & Testing~~ ✅ DONE

### ~~Engine Debugging~~ ✅
- [x] GPL debugging cheat-sheet (gold channel, floating numbers, minimap beacons, visual tints)
- [x] Debug master switch pattern
- [x] Crash dump analysis notes (same EIP = deterministic, scattered = heap corruption)
- [x] Engine primitives searchable as plaintext in MajestyHD.exe

### ~~Compiler Gotchas~~ ✅
- [x] Gplbcc.exe returns exit code 0 even on failure (check file timestamp)
- [x] Stale build trap (old .bcd loads fine but doesn't have your changes)

---

## ~~Steering File Updates~~ ✅ DONE

- [x] Created `gpl-reference.md` steering file (manual inclusion) — primitives, gotchas, patterns, debugging
- [x] Added XML schema quick-reference to `quest-and-mod-creation.md`
- [x] Added MQXML/MMXML advanced features to `quest-and-mod-creation.md`
- [x] Added multi-kingdom API docs to `quest-and-mod-creation.md`
- [x] Updated `majesty-modding.md` to point to new GPL reference steering

---

## Lower Priority / Future Work

### constants.rgs — Unknown Modifiability
- [ ] **UNVERIFIED:** Can quests/mods load custom constants.rgs files?
  - SDK docs mention "changing RGS Constants is optional" but no Workshop mod does it
  - MQXML has `<Constants>` in the Unload section — implies load/unload is possible?
  - No Workshop mod ships a custom constants.rgs (0 out of 10 analyzed)
  - Need to test: create a minimal modified constants.rgs, reference it in MQXML, see if game loads it
- [ ] If modifiable: implement RGCB format writer for custom landscape patterns
- [ ] If NOT modifiable: document this limitation, focus on selecting from existing 410 patterns

### Landscape Objects (Trees/Rocks)
- [ ] Document which fractal refs produce which vegetation
- [ ] Test terrain presets with different fractal refs to get trees
- [ ] Consider adding "density" parameter to presets (bare, sparse, forested)

### Workshop Integration
- [ ] `--workshop` flag for quest_map_generator to create Workshop-ready packages
- [ ] Generate .mswproj files programmatically
- [ ] Support multiple mods in one .mmxml generation

### Engine Exploration
- [ ] Scan MajestyHD.exe for additional undocumented GPL primitives
- [ ] Verify `$RandomCoord(anchor, -1)` radius behavior (entire map?)
- [ ] Test if `<CAM>` tag works for sprite data (only proven for audio so far)
- [ ] Determine exact game tick → real time relationship (72,000ms = 1 in-game day)
