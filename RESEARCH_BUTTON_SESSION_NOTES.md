# ⚠️ ACCURACY REVIEW

Cross-referenced against proven findings in:
- `SMNUResearch/FUTURE_TODO.md` (confirmed test results)
- `SMNUResearch/findings/exe_disassembly_results.md` (Ghidra findings)
- `SMNUResearch/findings/smnu_parser_decompilation.md` (SMNU format)

## CORRECT ✅

1. **SMNU format is tag-value int32 stream** — Confirmed by smnu_parser_decompilation.md and FUTURE_TODO.md ("SMNU format is a tag-value int32 stream (fully decoded)")
2. **Quest CAMs ARE loaded but STRT entries are NOT used to override** — Confirmed by FUTURE_TODO.md ("Quest CAMs loaded via `<CAM>` ARE loaded... Quest SMNU/STRT entries with same name as base/expansion do NOT override (first-loaded wins)")
3. **It's a search priority issue, not a loading issue** — Confirmed by FUTURE_TODO.md ("This is a search priority issue in FUN_00679a80, not a loading issue")
4. **Quest CAMs DO work for IMAG/TILE/sound (sprites)** — Confirmed by FUTURE_TODO.md ("Quest CAMs DO work for: IMAG, TILE, SPLT (sprites), WAVE (audio) — these DO override")
5. **Building-to-panel mapping is hardcoded in vtable methods** — Confirmed by exe_disassembly_results.md ("The mapping is HARDCODED in per-building-class virtual functions (vtable methods)")
6. **Panel open function is FUN_004b0ce0(panelName4CC, context)** — Confirmed by exe_disassembly_results.md (exact match)
7. **Inserting widgets into existing SMNU panels WORKS (via direct file replacement)** — Confirmed by FUTURE_TODO.md ("Inserting widgets into existing SMNU panels WORKS (via direct file replacement)")
8. **Each building panel has its own STRT entry (same entry name as SMNU)** — Confirmed by smnu_parser_decompilation.md ("STRT is found by SAME entry name as SMNU in the CAM")
9. **Tag 7 = string from STRT by index** — Confirmed by smnu_parser_decompilation.md
10. **Distribution requires modified mx_textdata.cam (direct file replacement)** — Confirmed by FUTURE_TODO.md

## INCORRECT ❌

1. **"there must be internal size/count fields" (Priority 1 in Next Steps)** — WRONG. The SMNU format has NO size/count fields. It's a pure tag-value int32 stream terminated by -1 markers. The earlier insertion failures were due to not understanding the stream format, not missing size fields. The decompilation proves there are no embedded counts for the widget list.
2. **"tree structure with nested widgets" (Priority 1)** — PARTIALLY WRONG. It's a flat sequential int32 stream, not a tree structure. Panels DO nest (type 1000 creates a sub-panel block), but the format is a sequential stream with -1 terminators, not a hierarchical tree with size prefixes.
3. **"120-byte INBb block pattern" (Priority 2)** — INCORRECT framing. There is no fixed "120-byte block" in SMNU. Widgets are variable-length sequences of tag-value int32 pairs terminated by -1. The 120-byte observation was likely a coincidence of specific widgets having similar property counts.
4. **Sub-panel navigation — session notes imply it might work with correct SMNU insertion** — INCORRECT. FUTURE_TODO.md proves "Only action code 8013 (return to parent) works from inside a sub-panel. Codes 4004, 8851, System B format — all silently ignored. Multi-page navigation is impossible without an exe patch."
5. **"The 4-byte prefix is the string's own index within the entry" (Layer 3)** — INCORRECT. FUTURE_TODO.md confirms STRT format is "u16 count + u8 unicode_flag + u8 version + u32 offsets + null-terminated strings (NO index prefix)". The version 0x02 STRT has NO per-string index prefix — the "4-byte prefix" described in this file contradicts the proven format.

## UNVERIFIED ⚠️ (not confirmed or contradicted by our findings)

1. **EXE Patch: exe_patcher.py research button cost/time test** — The session notes claim in-game confirmation of the 500g cost appearing. Not referenced in the three comparison documents, so this is self-reported from the earlier session but not cross-validated.
2. **FUN_004a8510 registers ALL 26 research buttons** — Specific registration function address and "26 buttons" count not confirmed in the comparison documents.
3. **FUN_004a83e0(cost_expr, time_expr, level, buttonID, iconIdx, controlID)** — Registration function signature not in the comparison documents.
4. **Prerequisite table at VA 0x7D3D10** — Not referenced in comparison documents.
5. **Click handler FUN_004a94c0 routes by control_id range 5040-5043** — Not in comparison docs.
6. **AP31 SMNU entry = 3204 bytes** — Specific byte count not validated in comparison docs.
7. **"The Blacksmith has 6 research slots"** — Not confirmed in comparison documents.
8. **Polish translation STRT version 0x00 uses u16 offsets** — FUTURE_TODO.md confirms version 0x02 uses u32 offsets, but the version 0x00 format details are not explicitly validated.

## SUMMARY

The session notes are **mostly correct** on the high-level architecture and what works/doesn't work. The main errors are:
- Mischaracterizing the SMNU format as having "size/count fields" and being a "tree structure" (it's a flat int32 tag-value stream with -1 terminators)
- Describing widgets as "120-byte fixed blocks" (they're variable-length)
- Claiming STRT strings have a "4-byte prefix" (version 0x02 STRT has NO per-string prefix — just u32 offset table + null-terminated strings)
- Missing the critical finding that sub-panel navigation is IMPOSSIBLE without an exe patch (only code 8013/return works)

---

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
