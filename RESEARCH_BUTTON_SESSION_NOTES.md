# Research Button Investigation — Session Notes

## Goal
Add new research/purchase buttons to existing buildings (marketplace, library, etc.) via modding.

## Status: TEXT MODIFICATION WORKING ✅ (Root Cause Found)

The "regression" was a misidentification of which string entry controls the button label.
- **GMTX[210]** in the STRT section is NOT the button label — it's general game text (used elsewhere).
- **APa3 string[1]** in the STRT section IS the actual marketplace research button label.
- The earlier "working" state likely coincidentally modified APa3 during SMNU experiments, then a revert restored APa3 while keeping GMTX[210] changed — making it look broken.
- The Polish translation (known-working) confirmed this: it modifies APa3[1] for button text.
- `mx_textdata.cam` does NOT override APa3, so only `Data/textdata.cam` needs patching.

---

## What Was Proven Working

### 1. EXE Patch: Research Button Cost/Time (CONFIRMED ✅)
- `exe_patcher.py` successfully hijacks an existing research button slot
- Registering with control_id 0x13B3 (PowerfulItem slot) overwrites its cost
- In-game: Amulet button showed 500g cost (from `#ResearchCostTestItem` GPL expression)
- Proves: registration pipeline works, GPL expressions control cost/time

### 2. Text Modification via textdata.cam (WORKING ✅ — Correct Entry Identified)
- **APa3 string[1]** in the STRT section of textdata.cam = actual "Market Day" button label
- GMTX[210] is NOT the button label (it's general game text used elsewhere)
- Modifying APa3[1] to "TEST ITEM" (preserving 4-byte prefix \x01\x00\x00\x00) shows in-game ✅
- Works in both base game and expansion modes (mx_textdata.cam does NOT override APa3)
- Each building has its own STRT entry for panel strings (APa3 = marketplace research panel)

### 3. Quest CAM Overlay for textdata (DOES NOT WORK ❌)
- `<CAM>Data\Quest_textdata.cam</CAM>` in mqxml — file loads (confirmed in err.log) but STRT entries are NOT used to override base strings
- Quest CAM overlays only work for IMAG/TILE/sound data, not SMNU/STRT text

---

## Architecture Findings

### Research Button System (4 layers)

**Layer 1: Registration (EXE code)**
- `FUN_004a8510` (VA 0x4A8510) registers ALL 26 research buttons at startup
- Each calls `FUN_004a83e0(cost_expr, time_expr, level, buttonID, iconIdx, controlID)`
- Stored in a map keyed by control_id
- Cost/time come from GPL expressions (`#ResearchCostX`, `#ResearchTimeX`)

**Layer 2: UI Panel Template (textdata.cam SMNU section)**
- AP31 entry in SMNU section defines the marketplace panel widgets (3204 bytes)
- Contains INBb (button) widget definitions with internal IDs 1000-1003
- The panel creates child controls from this template
- Child controls are iterated by FUN_004a93d0 (range check [5000, 5099])

**Layer 3: Per-Panel String Table (textdata.cam STRT section — APxx entries)**
- Each building has its OWN STRT entry (e.g., APa3 = marketplace research panel strings)
- APa3 string[1] = button label ("Market Day"), string[2] = tooltip description
- The 4-byte prefix is the string's own index within the entry (NOT a global ID)
- Polish translation confirmed: they modify APa3[1] to translate button text
- mx_textdata.cam does NOT override APa3 — safe to patch base file only

**Layer 4: General Game Text (textdata.cam STRT section — GMTX entry)**
- GMTX[210] = "Market Day" — used for OTHER references (not the button label itself)
- GMTX is indexed by a global u32 ID (the 4-byte prefix matches the array index)
- Expansion's mx_textdata.cam DOES override GMTX (442 strings vs 388)

### Prerequisite Table (EXE .data section)
- VA 0x7D3D10: maps building types to control IDs (28 bytes per row)
- Marketplace (ABH) at 0x7D3D80: [5040, 5041, 5042, 5043, EMPTY, EMPTY]
- Adding entries here BREAKS upgrade prerequisites (makes game think research isn't complete)
- This table is for prerequisite CHECKING only, not button creation

### Click Handler (EXE code)
- FUN_004a94c0: routes button clicks by control_id range
- Marketplace range: 5040-5043 (would need extending for 5th button)

---

## What Doesn't Work

1. **Quest CAM overlay for textdata** — file loads but STRT entries ignored
2. **Adding SMNU widget bytes by insertion** — corrupts the SMNU section (broke GMTX text too)
3. **Prerequisite table patch** — breaks building upgrades

---

## Tools Created

| File | Purpose |
|------|---------|
| `exe_patcher.py` | Patches MajestyHD.exe to register a new research button (cost/time from GPL) |
| `TestResearch/` | GPL mod with `#ResearchCostTestItem` and `#ResearchTimeTestItem` expressions |
| `utility/test_decoder.py` | Scratch investigation script (various states) |
| `utility/decompiled_marketplace.txt` | Decompiled registration function from Ghidra |

---

## Next Steps (for next session)

### Priority 1: Understand SMNU widget format (for adding a 5th button)
- Inserting raw bytes corrupts the section — there must be internal size/count fields
- Need to properly parse the SMNU format (tree structure with nested widgets)
- The Polish translation's textdata.cam has identical SMNU to English (they only changed STRT)
- Decompile the CYLib SMNU parser in Ghidra to understand field layout

### Priority 2: Add a 5th research button
- Requires: correct SMNU widget insertion + registration (exe patch) + APa3 text entry
- The Blacksmith has 6 research slots, so the system supports more than 4
- The 120-byte INBb block pattern is identified but insertion breaks the format
- Now that we know text comes from APa3 (not GMTX), adding a new string to APa3 is straightforward

### Priority 3: Clean up test modifications
- Restore game's textdata.cam APa3[1] back to "Market Day" (or leave for continued testing)
- Restore mx_textdata.cam GMTX[210] back to "Market Day" (already backed up as .bak)
- The GMTX[210] modification in Data/textdata.cam is harmless but pointless

---

## Key Files in Game

| File | Contains | Moddable via quest? |
|------|----------|-------------------|
| `Data/textdata.cam` | SMNU (panel layouts) + STRT (text strings) | NO — direct replacement only |
| `DataMX/mx_textdata.cam` | Expansion SMNU + STRT (overrides base for expansion quests) | NO |
| `Data/gpltext.cam` | GPL help text, quest names, character descriptions | Unknown |
| `MajestyHD.exe` | Research registration, UI logic, prerequisite table | Binary patch required |

---

## Polish Translation Reference

A working textdata.cam modification exists: `c:\Users\Brandon\Downloads\Majesty_HD_PL_v0.2\Data\textdata.cam`
- 1,709,722 bytes (includes IMAG+TILE sections for localized button sprites)
- Uses STRT version 0x00 (original Polish format: u16 offsets, NO 4-byte prefix)
- English HD uses STRT version 0x02 (u32 offsets, WITH 4-byte prefix per string)
- Their GitHub tools: https://github.com/m-architek/Majesty-Tools
- Installation: direct file replacement in Data/ folder (confirmed working approach)

---

## Cleanup Needed

- Restore game's `DataMX/mx_textdata.cam` from .bak (GMTX[210] change was pointless)
- The `Data/textdata.cam` has both APa3[1]="TEST ITEM" (working!) and GMTX[210]="TEST ITEM" (harmless)
- Remove `IceSpell_Quest/Data/Quest_textdata.cam` (broken/useless — quest overlays don't work for STRT)
- Remove `<CAM>Data\Quest_textdata.cam</CAM>` from IceSpell Quest.mqxml
- The exe_patcher.py is still configured for the MarketDay hijack test
- `utility/compare_polish.py` — investigation script, can be kept or removed
