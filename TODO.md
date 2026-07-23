# Majesty Modding Toolkit — Master TODO

---

## Active Work

### SMNU Panel Override via Quest CAM
- [ ] **TEST:** Deploy PanelTest_Quest with passthrough CAM (byte-identical MX03)
  - If works: confirms override mechanism is fine, our SMNU generation is the bug
  - If crashes: still a CAM-level or scope issue
- [ ] Build SMNU compiler (`smnu_compiler.py`) that produces valid panel binary
  - Must handle the custom constructor formats for widget types 0, 1, 2, 5, 6, 9
  - Validate against real game panels by roundtrip comparison
- [ ] EXE patch: sub-panel navigation code (Ghidra machine)
  - Add new action code to building sub-panel click dispatcher
  - Allows buttons in SMNU data to open arbitrary panels by name

### Landscape Objects (Trees/Rocks)
- [ ] Document which fractal refs (`xFel`, `xFer`, `xBBC`, etc.) produce which vegetation
- [ ] Test terrain presets with different fractal refs to get trees (current `grass` preset is bare)
- [ ] Consider adding "density" parameter to presets (bare, sparse, forested)

---

## Needs In-Game Verification

### Particle Systems
- [ ] Does the 4th value in BirthColor/MidlifeColor/DeathColor = alpha?
  (All game systems use pattern `0,0,0,0` → `0,0,0,1` → `0,0,0,0` suggesting alpha fade)
- [x] Does `ImageIDBase` map to single sprite frame or can it use multi-frame animation?
  **ANSWERED:** Both. IMAG entries range from 132B (single frame, e.g., XL25/XL28/XL30) to
  444B (multi-frame, e.g., XL31 icebreath_hit). The engine likely animates through frames.
- [ ] Do custom particle systems load from quest CAMs via `<Descriptions>`?
  (Overlays work, particle systems likely do too — never explicitly tested)
- [ ] What does `AllocateLocalID` info flag do? (Only on XL00 placeholder_spell)
- [ ] What do AttachmentPointID values actually correspond to visually?
  (Guesses: 0=ground, 1=head, 2=center, 3=feet — based on which effects use which)

### Scrollable List Widgets (from AP52/MX01 research)
- [ ] Can type 6 (scrollable list) be placed in a research panel?
  (Likely requires C++ populator code to fill it — may need exe patch)
- [ ] What action code range links a type 6 list to its type 9 scrollbar?
  (Observed: list=5000, scrollbar=5001 or 5010)

### constants.rgs Modifiability
- [ ] Can quests/mods load custom constants.rgs files?
  - SDK docs mention "changing RGS Constants is optional" but no Workshop mod does it
  - MQXML has `<Constants>` in the Unload section — implies load/unload is possible
  - Need to test: reference a modified constants.rgs in MQXML, see if game loads it

### Engine Timing (low priority — test via GPL $DebugOut logging when relevant)
- [ ] Game tick → real time ratio. Method: `$NewThread` at known ms interval,
  count iterations until dawn/dusk transition, derive ratio.
- [ ] `$RandomCoord(anchor, -1)` radius: does -1 mean entire map? Log returned
  coords and measure spread vs map bounds.

---

## Lower Priority / Future

### Workshop Integration
- [ ] `--workshop` flag for quest_map_generator to create Workshop-ready packages
- [ ] Generate .mswproj files programmatically

### EXE Patch Ideas (Ghidra machine)
- [ ] Sub-panel navigation: new action code for building panel click dispatcher
- [ ] Expose cheat functionality to GPL (e.g., `$RevealMap()`, `$AddGold(amount)`)
  - Cheats are hardcoded in the exe (string matching → engine action)
  - Some already call GPL (`cheat_wave_undead`, `cheat_wave_raiders`, etc.)
  - Could add new GPL primitives that call the same internal functions
  - Would enable quest scripts to reveal map, grant resources, etc. programmatically
- [ ] Scroll list widget support for research panels (populate type 6 from C++ code)

---

## Completed (reference only)

- ✅ Quest Map Generator: parse 37/37, roundtrip, create API, spawners, terrain, force layout, multi-kingdom, CLI
- ✅ GPL Knowledge Base: primitives, gotchas, patterns, debugging (in steering files)
- ✅ XML Schema: actions, overlays, buildings, research, particle systems (in CAM_MODDING_GUIDE + steering)
- ✅ MQXML/MMXML capabilities documented (steering file)
- ✅ TILE v3 RLE fix: exclusive-end X encoding (sprite_extractor + sprite_injector)
- ✅ CAM override mechanism: all resource types override via quest CAM (last-loaded wins)
- ✅ UUID generation: was misdiagnosis, uuid.uuid4() is correct
- ✅ `<CAM>` tag works for sprites (IceSpell_Quest confirmed)
