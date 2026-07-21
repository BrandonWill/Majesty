# RGSEditor Decompilation (Ghidra MCP — July 2026)

Binary analyzed: `SDK/RGSeditor.exe` (2.5 MB, x86 PE, MFC90-based C++ app)

## Key Functions Identified

| Address | Role | Description |
|---------|------|-------------|
| `0x00467670` | **LoadQuest** | Main .q file reader — detects RGM1-RGM9/RGMa magic |
| `0x00465f90` | **SaveQuest** | Main .q file writer — always writes "RGMa" header |
| `0x0047bb00` | ReadUnitPatterns | Reads the collection of Unit Pattern sections |
| `0x004735c0` | ReadSingleUnitPattern | Reads one Unit Pattern (metadata + instances + spawners) |
| `0x00478e70` | ReadUnitInstance | Reads one unit (object ID, name, position cells) |
| `0x0047e8d0` | ReadRegionPatterns | Reads Region Pattern section (terrain) |
| `0x0047e3d0` | ReadRegionPatternEntry | Single region entry (terrain type + landscape) |
| `0x00481480` | ReadForcePattern | Reads Force Pattern section |
| `0x0047ef60` | ReadForceEntry | Reads one force entry (faction placement on map) |
| `0x0046e830` | ReadSpawnerBlock | Reads a spawner block (version-dependent fields) |
| `0x0046e1c0` | ReadTeamDefinition | Reads a team/player definition |
| `0x0047c0e0` | ReadSpawnerItem | Reads individual spawner entry (monster + level) |

## Low-Level I/O Primitives

| Address | Signature | Description |
|---------|-----------|-------------|
| `0x004f2520` | `ReadU32(stream, &dest)` | Reads 4 bytes as u32 from file stream |
| `0x004f24a0` | `ReadTag4(stream, &dest)` | Reads 4 bytes as 4-char tag (same binary op as ReadU32) |
| `0x004f2440` | `ReadBytes(stream, buf, n)` | Reads N arbitrary bytes |
| `0x004eb2a0` | `ReadString(stream, &str)` | Reads null-terminated string (supports ASCII + wide) |
| `0x004f1bb0` | `WriteU32(stream, val)` | Writes 4-byte u32 |
| `0x004f1ab0` | `WriteTag4(stream, tag)` | Writes 4-byte tag |
| `0x004eb180` | `WriteString(stream, str)` | Writes null-terminated string |

## Version Handling (LoadQuest)

The loader recognizes versions RGM1 through RGM9 and RGMa. Each version maps to
internal "component versions" stored in global variables:

```
iStack_a4 (file magic) -> sets these globals:
  DAT_006153f0 = "Force Pattern" format version (RGC1-RGC8)
  DAT_006153d8 = "Spawner/Team" format version (RGC1-RGC3)
  DAT_00615390 = "Team definition" format version (RGC1-RGC7)
  DAT_006154bc = "Spawner item" format version (RGC1-RGC3)

Version mappings (hex LE -> string):
  0x394d4752 = "RGM9" -> Force=RGC8, Spawner=RGC3, Team=RGC7, SpawnItem=RGC3
  0x614d4752 = "RGMa" -> Force=RGC8, Spawner=RGC3, Team=RGC7, SpawnItem=RGC3
  0x384d4752 = "RGM8" -> Force=RGC7, Spawner=RGC3, Team=RGC7, SpawnItem=RGC3
  0x374d4752 = "RGM7" -> Force=RGC7, Spawner=RGC3, Team=RGC7, SpawnItem=RGC3
  0x364d4752 = "RGM6" -> Force=RGC7, Spawner=RGC2, Team=RGC7, SpawnItem=RGC2
  0x354d4752 = "RGM5" -> Force=RGC7, Spawner=RGC2, Team=RGC7, SpawnItem=RGC1
  0x344d4752 = "RGM4" -> Force=RGC6, Spawner=RGC2, Team=RGC1, SpawnItem=RGC1
  0x334d4752 = "RGM3" -> Force=RGC5, Spawner=RGC2, Team=RGC1, SpawnItem=RGC1
  0x324d4752 = "RGM2" -> Force=RGC1, Spawner=RGC2, Team=RGC1, SpawnItem=RGC1
  0x314d4752 = "RGM1" -> Force=RGC1, Spawner=RGC1, Team=RGC1, SpawnItem=RGC1
```

## File Structure (Read Order from LoadQuest)

```
1. HEADER
   - Read file-level metadata (via BLKHeaderEx / stream open)
   - iStack_a4 = 4-byte magic (detected and version-mapped)

2. QUEST NAME / PATTERN NAME
   - Read quest name string
   - Read other metadata fields

3. SPAWNER BLOCKS (count read from stream)
   For each spawner block (FUN_0046e830):
     Version RGC3:
       - u32: field_0x00  
       - u32: field_0x04
       - u32: field_0x08  
       - u32: field_0x0c
       - u32: field_0x10
       - TeamDef (FUN_0046e1c0): name_tag + null_string + bool x2 + spawner_items
       - u32: extra_item_count
       - extra_item_count x 4-byte tags (extra names)
     Version RGC2:
       - u32: field_0x00 through field_0x10 (5 u32s)
       - TeamDef (same structure)
     Version RGC1:
       - u32: field_0x00 through field_0x0c (4 u32s)
       - TeamDef (same structure)

4. UNIT PATTERNS (count read from stream)
   For each Unit Pattern (FUN_004735c0):
     - 4-byte tag: terrain type code (at offset +0x0c in struct)
     - Read stream metadata (null-terminated string)
     - Read grid dimensions (unknown fields)
     - bool: flag at offset +0x28
     - u32: unknown field
     - 4-byte tag: offset +0x48
     - u32: offset +0x44
     - Initialize container for unit instances
     - u32: unit_instance_count
     - For each instance (FUN_00478e70):
       - 4-byte tag: object_name (e.g. "BBH1", "ABJ1")
       - u32: unknown field at +0x08
       - Read null-terminated string (description)
       - Initialize position container
       - u32: position_count
       - For each position: read 1 byte (grid cell 'A'-'Y')
     - u32: spawner_count_for_pattern  
     - For each spawner in pattern (FUN_0046e830): same as #3
     - Version-dependent extra fields:
       - Force >= RGC5: u32 resolution at +0x6c
       - Force >= RGC7: u32 x3 + bool x4 extra fields

5. TWO MORE U32 VALUES
   - param_2[0x46] and param_2[0x47]

6. QUEST MODE / FREESTYLE CHECK
   - Read u32 value
   - If version >= RGM2: read quest/freestyle string, check for "FREESTYLE"
   - Sets param_2[3] (quest_type_code) and param_2[4] (freestyle_flag)

7. REGION PATTERNS (FUN_0047e8d0)
   - u32: count
   - For each: read 4-byte tag, if != "NONE" -> read region entry
   - Region entry: terrain code mapping + landscape reference

8. FORCE PATTERN (FUN_00481480)
   - u32: force_entry_count
   - For each force entry (FUN_0047ef60):
     - 4-byte tag: faction_short_code
     - null-terminated string: faction_full_name
     - 4-byte tag: unit_pattern_ref
     - 4-byte tag: unknown
     - 4-byte tag: unknown  
     - u32: active/enabled flag
     - u32: map_grid_position (0-24, same as 'A'-'Y' encoding)

9. UNIT PATTERNS SECOND SET (same reader as #4)
   - param_2 + 0x16 and param_2 + 0xd

10. FINALIZATION
    - If version <= RGM7: set param_2[0] = "Rel" (0x6c6552)
    - Else: read string into param_2[0]
    - Validation/fixup calls
```

## Force Pattern Entry Structure (Write Side)

```
WriteTag4(faction_short_code)      // e.g. "Monst", "Play1"
WriteString(faction_full_name)     // null-terminated, e.g. "Monsters\0"
WriteTag4(field[4])                // unit pattern reference?
WriteTag4(field[5])                // unknown
WriteTag4(field[6])                // unknown
WriteU32(field[7])                 // active flag
WriteU32(field[8])                 // grid position
```

## Spawner Item Structure (version-dependent)

```
SpawnItem version RGC3:
  ReadTag4(name)          // +0x04: monster/lair 4-char code
  ReadU32(spawn_level)    // +0x08
  ReadU32(field_0x0c)     // +0x0c
  ReadU32(field_0x10)     // +0x10
  ReadU32(->bool active)  // +0x14: 0 or 1
  ReadU32(lair_resource)  // +0x18

SpawnItem version RGC2:
  Same as RGC3 minus lair_resource field

SpawnItem version RGC1:
  ReadTag4(name) + ReadU32 x3 (no bool, no lair_resource)
```

## Key Insights

1. **Everything is 4-byte aligned** — all values are either u32 or 4-char tags.
   The only exception is position bytes (1 byte each) and null-terminated strings.

2. **Tags and u32s use the same read function** — the 4-byte read is identical,
   interpretation happens in the caller.

3. **The file has TWO sets of Unit Patterns** — one main set and a second set.
   The second set may be the "alternate patterns" for different team configurations.

4. **NONE markers are sentinels** — Region Pattern entries with tag "NONE"
   (0x454e4f4e) are skipped.

5. **RGMa is the current editor format** — the writer always outputs "RGMa".
   The game engine likely reads RGM6 (base game) and RGM9 (expansion).

6. **Resolution field** only exists in Force version >= RGC5 (file version >= RGM3).
   Default is 3 for older versions.
