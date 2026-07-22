# SMNU Research — Future Work

## Confirmed Limitations (Exhaustively Tested)

### Building Sub-Panel Navigation
- Only action code 8013 (return to parent) works from inside a sub-panel
- Codes 4004, 8851, System B format — all silently ignored in sub-panel context
- Multi-page navigation is impossible without an exe patch

### Quest CAM Override Capability (CORRECTED July 2026)
- Quest CAMs loaded via `<CAM>` **DO override** all resource types (last-loaded wins)
- SMNU and STRT overrides WORK — confirmed by another modder replacing "Market Day" text
- **Previous incorrect finding:** We thought SMNU/STRT used "first-loaded wins." This was
  a misdiagnosis — our PanelTest crash was caused by a malformed custom SMNU binary
  (bad tag-value stream), not by a failed override
- Practical impact: panel mods CAN be distributed as quest-only packages via `<CAM>` tags
- The SMNU compiler (Priority 4) becomes critical — must produce perfectly valid binary

### Panel Modifications (Working)
- Inserting widgets into existing SMNU panels WORKS (via quest CAM override)
- The SMNU format is a tag-value int32 stream (fully decoded)
- Widget type 0 buttons can be cloned and repositioned successfully
- The CAM builder (`build_cam()`) produces byte-perfect output

### Distribution Model (REVISED)
- **Quest CAM with SMNU+STRT override** = the correct approach (no file replacement needed)
- **Patched exe** = still needed for sub-panel NAVIGATION (new action code)
- A quest/mod can override existing panels, but cannot navigate between sub-panels
  without the exe patch to the building sub-panel click dispatcher

---

## Priority 1: EXE Patch — Sub-Panel Navigation Action Code

### Problem
Only action code 8013 (return to parent) works from inside a building sub-panel.
All other codes (4004, 8851, System B format) are silently ignored.
This prevents multi-page panel navigation (Page 1 → Page 2 → Page 3).

### What We Need
A new action code (e.g., 8852) recognized by the sub-panel click dispatcher that calls
`OpenPanelByName(name4CC, context)` with the action ID interpreted as a 4-char panel name.

### Ghidra Task
1. Find the building sub-panel click handler (the function that checks for code 8013)
2. Identify where it rejects/ignores unknown codes
3. Add a new code path: `if (code == 8852) { OpenPanelByName(actionID_as_4CC, 0); }`
4. This likely requires a code cave (jump to new code in an unused section of the exe)

### What This Would Enable
- Navigation buttons in SMNU data: `[1024, 5, "PT01", 6, 8852]`
- Multi-page building research panels (6 items per page, unlimited pages)
- Quest-distributable via `<CAM>` (SMNU override works, confirmed)

---

## Priority 2: Multi-Page Panel (Quest CAM Approach)

### Now Viable (no file replacement needed!)
Since SMNU/STRT overrides via quest CAM work (last-loaded wins), the approach is:
1. Build a modified MX03 SMNU with a "More →" navigation button
2. Build matching STRT with button labels
3. Build new panels (PT01, PT02) with their own SMNU + STRT
4. Pack all into a quest CAM, load via `<CAM>` tag
5. The "More →" button needs the exe nav code patch (Priority 1) to function

### Steps
- [ ] Build a VALID MX03 SMNU override (correctly formatted tag-value stream)
- [ ] Verify it loads without crash (just override, keep original layout)
- [ ] Add navigation button widget to the overridden MX03
- [ ] Build PT01/PT02 panel SMNU + STRT entries
- [ ] Test with exe patch (Priority 1) for navigation

---

## Priority 3: EXE Patch — New Building Panel Registration

### Problem
Building-to-panel mapping is hardcoded in per-building vtable methods.
New custom buildings (new DialogID) can't have Research panels without exe patching.

### Potential Approaches
- Modify the panel factory function (0x0051b150) to handle new DialogIDs
- Or: hijack an unused building class's vtable handler to point to custom panel name
- Or: DLL proxy that hooks the panel factory and adds new mappings at runtime

---

## Key Addresses (MajestyHD.exe)

| Address | Function | Purpose |
|---------|----------|---------|
| 0x006d34d0 | STRT loader | Loads STRT by entry name — **PATCH TARGET** for scope fix |
| 0x00679a80 | Resource find | Resource manager lookup (takes scope flag 0x80000001) |
| 0x004b0ce0 | OpenPanelByName | Opens panel by 4-char name |
| 0x0051b150 | Panel class factory | Creates building panel handler from DialogID |
| 0x0063a220 | String setter | Where crash occurs (null deref from failed STRT) |
| 0x0064d330 | Panel factory | Allocates panel, connects STRT, parses widgets |
| 0x00668390 | Child widget parser | Reads widget stream |
| 0x00675b50 | Widget property parser | Processes tag-value property pairs |
| 0x006655e0 | Panel header parser | Processes panel header block |

## Confirmed Format Knowledge

### SMNU: Tag-value int32 stream
- Panel: `1000 [tags...] -1` then `[widget_type sub_id [tags...] -1]...` then `-1`
- Tags consume 1 value (most), 4 values (tag 2 = geometry), or 1+N (color arrays)
- Tag 7 = string from STRT by index
- Tag 33 = tooltip from STRT by index
- Tag 12 = image set (4-char packed as i32)
- Tag 6 = action identifier (stored at widget+0x14)
- Widget types: 0-12, each with specific constructors

### STRT: Header + offset table + strings
- Header: u16 count, u8 unicode_flag (0x00), u8 version (0x02)
- Offsets: count × u32 absolute byte positions
- Content: null-terminated strings (no index prefix)
- STRT is found by SAME entry name as SMNU in the CAM

### CAM Override Behavior
- Quest CAMs ARE loaded into the resource system (no error on load)
- SMNU/STRT from quest CAMs are shadowed by base/expansion (first-loaded wins)
- IMAG/TILE/SPLT/WAVE from quest CAMs DO override (last-loaded wins)
- This is a search direction issue in `FUN_00679a80`

---

## Priority 3.5: Investigate Scrollable List Widget (Type 6) for Research Panels

### Findings (July 2026 session)
- **Widget type 6** = scrollable list container (object size 368 bytes, constructor FUN_006d0dd0)
- **Widget type 9** = scrollbar/slider (object size 340 bytes, constructor FUN_006cc5d0)
- Both read geometry directly after sub_id: `[type, sub_id, x, y, w, h, <tag-value pairs>]`
- Linked by action codes: list uses **5000**, paired scrollbar uses **5001** or **5010**
- Scrollbar is always 25px wide, positioned to the right of the list area
- Image set "INDj" for scrollbar, "INTI" for list in scroll contexts

### Geometry Examples
- MX01 (Hall of Champions): list=164×160, scrollbar at x=174 w=25 h=167
- AP40 (Palace hero roster): list=173×356, scrollbar at x=176 w=25 h=362

### Open Question
- List CONTENTS are populated by C++ building class code at runtime
- The SMNU only defines the container (size, position, styling)
- Adding type 6 to a research panel would render an empty list unless the
  building's C++ populator knows to fill it with research items
- Need Ghidra to check: what does the research panel populator (`FUN_00495790`) actually do?
  Does it look for a type 6 list and fill it, or only set text on fixed button widgets?

### Warriors Guild (AP52) Dynamic Panel Pattern
- ALL possible recruit buttons are pre-defined in SMNU (Warrior, Discord, Paladin)
- C++ code shows/hides buttons at runtime based on what temples are built
- This means the engine supports **runtime widget visibility control**
- Recruit buttons use action 8009 with 258/266 alternates (conditional navigation)
- This is a viable pattern: define max slots in SMNU, let C++ hide unused ones

### Possible Approach (alternative to multi-page navigation)
If we could make the research panel C++ code populate a type 6 list widget with
research items (instead of fixed button slots), scrolling would work natively.
BUT this likely requires an exe patch to the research panel populator function.
Compare difficulty: one exe patch for scroll support vs one exe patch for sub-panel nav.

---

## Priority 4: Modder Tooling — XML Panel Definition Language

### Goal
Modders should define panels in human-readable XML, not hand-assemble binary.
A build tool compiles XML → SMNU binary + STRT, packs into CAM.

### Proposed XML Format
```xml
<Panels>
    <Panel name="MX03" background="IX01" tile="1001" font="fnt4" palette="MMS1">
        <Widget type="0">
            <Geometry x="0" y="0" w="202" h="245"/>
            <Image set="INBg" tile="1024"/>
            <Action type="6" value="1"/>
        </Widget>
        <Widget type="0">
            <Geometry x="20" y="70" w="160" h="25"/>
            <Text strt="2"/>
            <Tooltip strt="1"/>
            <Image set="INTG" tile="1005"/>
            <Action type="5" target="35" code="NEW_NAV_CODE"/>
        </Widget>
        <Widget type="0">
            <Geometry x="3" y="223" w="25" h="20"/>
            <Image set="INTG" tile="1005"/>
            <Action type="5" target="9" code="8013"/>
        </Widget>
    </Panel>
    <Strings name="MX03">
        <String id="0">MAGIC BAZAAR - RESEARCH</String>
        <String id="1">View potion research items</String>
        <String id="2">Potions</String>
    </Strings>
</Panels>
```

### Build Pipeline
```
panel_defs.xml → smnu_compiler.py → Quest_textdata.cam (SMNU + STRT sections)
```

### Implementation Steps (after exe patches are working)
- [ ] Write `smnu_compiler.py` that reads XML and emits valid SMNU int32 stream
- [ ] Include STRT generation from `<Strings>` section
- [ ] Pack into CAM using existing `build_cam()` function
- [ ] Validate output with existing SMNU parser/verifier
- [ ] Integrate into quest build pipeline (call from build scripts)
