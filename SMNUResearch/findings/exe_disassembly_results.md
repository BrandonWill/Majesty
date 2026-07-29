# Ghidra Disassembly Results — Building-to-Panel Mapping

## DEFINITIVE ANSWER

**The mapping is HARDCODED in per-building-class virtual functions (vtable methods).**

Each building type has its own C++ class with a vtable. One vtable slot is the "handle action
code" method. When the engine receives handler code 8851 (0x2293), it calls this virtual
method on the building's panel class. Each building's override function has the target panel
name **burned in as a 4-byte constant**.

This is **Answer #2 from the task doc**: a compiled per-building handler, not a naming
convention and not a data table.

## The Mechanism (step by step)

1. User clicks "Research" button in a building panel
2. Button fires: action type 5, action ID 82, handler code 8851
3. Engine calls the building panel class's virtual "handle code" method
4. The virtual method checks: `if (code == 0x2293)` → open hardcoded panel name
5. Panel is opened by calling `FUN_004b0ce0(panelName4CC, 0)`

## Code Pattern (identical for all buildings)

Every building with a research panel has this exact pattern at its vtable handler:

```asm
MOV  EAX, [ESP+4]       ; get handler code from stack
CMP  EAX, 0x2293        ; is it 8851 ("open sub-panel")?
JZ   open_panel          ; YES → jump to panel open
MOV  [ESP+4], EAX       ; NO → pass to parent class handler
JMP  FUN_00497690        ; call generic handler (which enables/disables research buttons)

open_panel:
PUSH 0x0                 ; param2 = 0 (use current building context)
PUSH 0xXXXXXXXX         ; param1 = 4-byte panel name (e.g., "MX03" = 0x3330584d)
CALL FUN_004b0ce0        ; OpenPanelByName(name, context)
RET  0x4
```

## Complete Building → Research Panel Mapping (from exe)

| Handler Address | Panel Opened | Panel Name Hex | Building (DialogID) | Vtable Address |
|-----------------|-------------|----------------|---------------------|----------------|
| 0x0049ef40 | **APa0** | 0x30615041 | AP90 (Fairgrounds?) | 0x00756060 |
| 0x004a0c10 | **APa1** | 0x31615041 | AP40 (Palace?) | 0x00756188 |
| 0x004a56a0 | **APa2** | 0x32615041 | AP26 (Library) | 0x00756498 |
| 0x004a5a30 | **APa3** | 0x33615041 | AP31 (Marketplace) | 0x007564e8 |
| 0x004b2680 | **APa4** | 0x34615041 | AP25 (Inn?) | 0x007572a0 |
| 0x00499b90 | **AP99** | 0x39395041 | AP20 (?) | 0x00755f58 |
| 0x004bb480 | **MX01** | 0x3130584d | MX00 (Hall of Champ) | 0x00757684 |
| 0x004bc570 | **MX03** | 0x3330584d | MX02 (Magic Bazaar) | 0x00757728 |
| 0x004bd990 | **MX07** | 0x3730584d | MX06 (Sorcerer) | 0x00757858 |

## The Panel Factory Function (0x0051b150)

This massive function is the **building panel class factory**. It takes a 4-char DialogID
as a u32 and creates the corresponding building panel handler class:

```
param_1 = DialogID as packed 4-byte value (e.g., 0x3230584d = "MX02")
```

Key mappings confirmed in the factory:
- `0x3230584d` ("MX02") → `FUN_004bc430` → sets vtable `PTR_FUN_0075771c` → handler opens MX03
- `0x31335041` ("AP31") → `FUN_004a56d0` → sets vtable `PTR_FUN_007564dc` → handler opens APa3

## The Panel Open Function (0x004b0ce0)

```c
bool __thiscall OpenPanelByName(int this, uint panelName4CC, int buildingContext)
```

Takes a 4-byte packed panel name (like "MX03" = 0x3330584d) and opens it.
The second parameter is the building/context pointer (0 = use current).

## Implications for Modding

### BAD NEWS: Cannot add new building-to-panel mappings
The panel name to open is a compiled constant in the exe. There is no data file to edit.
You cannot make a custom building's Research button open a custom panel name without
modifying the executable binary.

### GOOD NEWS: The panel navigation buttons (System B) still work
The hero panel navigation buttons (System B format with literal panel indices) use a
DIFFERENT code path that doesn't go through the vtable handler. Those buttons directly
specify a panel index and the engine navigates to it.

### KEY INSIGHT: The "Return to Main" button in MX03 works differently!
The "Return to Main" button in research panels uses action type 5 with target = 9.
This is NOT the same as the 8851 handler — it's a **direct panel index navigation**
(same as System B but simpler, without the 258/266 alternates).

If a building already HAS a research panel that the exe knows how to open, you can:
1. Modify that research panel to include a "Page 2 →" navigation button
2. The nav button uses action type 5 + a panel INDEX (not name) to jump to page 2
3. Page 2 is a custom panel loaded from textdata.cam with its own buttons
4. Page 2 has a "← Page 1" button pointing back

This works because:
- The exe opens the FIRST research panel via the hardcoded vtable handler
- Once IN a panel, navigation between panels uses panel indices (not the vtable path)
- Panel indices are data-driven (assigned sequentially as panels are loaded from CAM files)

### STRATEGY: Multi-page research for EXISTING buildings

1. The exe opens the research panel (e.g., MX03 for Magic Bazaar) — this is hardcoded
2. We MODIFY MX03 in textdata.cam to add a "More →" button with a panel INDEX
3. We ADD a new panel (e.g., "MX03b") to textdata.cam at a known index
4. The "More →" button navigates to MX03b by index
5. MX03b has a "← Back" button that navigates back to MX03 by index

This requires knowing the panel index. The panel index is the sequential position
of the panel in the SMNU section of textdata.cam. Since we control the CAM file
contents for quest mods, we can determine this at build time.

### CANNOT DO: New custom building types with their own research panels

A completely new building type (new DialogID) that wants a Research button opening
a custom panel would need the exe patched to add a new vtable handler. This is possible
(binary patching) but much harder than the multi-page approach above.

## Generic Handler Path (buildings WITHOUT a research panel)

Buildings without a specific override fall through to `FUN_00497690`:
```c
if (code == 0x2293) {
    FUN_00495790();   // Setup research button labels/counts
    FUN_004972e0();   // Enable/disable research UI elements
    return 0;
}
// else: pass to parent FUN_00495fa0
```

This path does NOT open a new panel — it just configures the current panel's
research button state. This is for buildings that show research info inline
rather than in a separate sub-panel.

## Key Addresses Summary

| Address | Function |
|---------|----------|
| 0x004b0ce0 | `OpenPanelByName(name4CC, context)` — opens a panel by its 4-char name |
| 0x00497690 | Generic 8851 handler — enables research UI, no panel navigation |
| 0x0051b150 | Building panel class factory — creates handler class from DialogID |
| 0x004972e0 | Research button state manager — shows/hides/enables research buttons |
| 0x00495790 | Research panel content populator — fills in item names, costs, progress |

## Verified Building Class Constructors

| DialogID | Hex | Constructor | Building Name |
|----------|-----|-------------|---------------|
| MX02 | 0x3230584d | FUN_004bc430 | Magic Bazaar |
| AP31 | 0x31335041 | FUN_004a56d0 | Marketplace |
| MX00 | 0x3030584d | FUN_004bb700 | Hall of Champions |
| MX06 | 0x3630584d | FUN_004bd870 | Sorcerer's Abode |

---

## Research Item Click Dispatch (UNCONFIRMED — not yet Ghidra-decompiled)

Distinct from the panel-OPEN mechanism above (which IS Ghidra-confirmed via
disassembly): clicking an individual research/purchase item WITHIN an
already-open panel (action codes 5061-5066 etc., see
`findings/action_codes_decoded.md`) is reported — from an earlier
`exe_patcher.py` binary-patching experiment, not from Ghidra decompilation
with disassembly shown — to work like this:

- `FUN_004a8510` registers ALL research buttons at startup (reported count:
  26), each via `FUN_004a83e0(cost_expr, time_expr, level, buttonID,
  iconIdx, controlID)`
- Registrations are stored in a map keyed by `control_id`
- A click handler (reported: `FUN_004a94c0`) routes clicks by `control_id`
  RANGE per building (reported example: Marketplace = 5040-5043)
- `cost_expr`/`time_expr` are GPL expression references (e.g.
  `#ResearchCostX`), NOT hardcoded values — the exe owns the dispatch
  mechanism, GPL data owns the actual numbers

**Empirical support (partial):** `exe_patcher.py` successfully hijacked an
existing button's registration (control_id `0x13B3`, the "PowerfulItem"
slot) and, in-game, the target button showed a cost pulled from a test GPL
expression (`#ResearchCostTestItem`) instead of its original value. This
demonstrates registration IS controllable and IS distinct from the panel
open mechanism, but does NOT independently confirm the specific addresses,
the "26 buttons" count, or the exact control_id ranges — those numbers were
carried over from that session's notes, not re-derived via decompilation
here.

**Practical implication if true:** adding a genuinely new (not just cloned)
purchase-style button to an existing panel likely requires either (a) an
unused/free control_id already registered by the exe with no visible
widget currently pointing at it, or (b) an exe patch to register a new
control_id — the button widget itself (SMNU/STRT) is fully within our
tooling's reach via quest CAM override, but making it produce true
purchase behavior on click may not be, depending on how strict this
range-based dispatch turns out to be.

**Follow-up needed:** re-derive this via actual Ghidra decompilation (not
just binary patching + observed in-game behavior) to confirm or correct
the specific addresses/counts/ranges. See `TODO-Ghidra.md`.
