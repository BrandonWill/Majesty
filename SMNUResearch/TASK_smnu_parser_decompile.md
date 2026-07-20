# Task: Decompile the SMNU Panel Parser

## Context

We attempted to build a custom SMNU panel from scratch. The game crashed with:
- **ACCESS_VIOLATION reading address 0x00000002** (null deref)
- **Crash address: 0x0063A232**

This means the engine found our panel (override worked!) but our custom SMNU binary
is malformed. We don't actually understand the SMNU format well enough to author panels.

## Objective

Decompile the SMNU parser to get the **exact struct layout** the engine expects.
We need to know what every field means, in what order, with what sizes.

## Primary Target: 0x0063A232

This is where the crash occurred. Decompile the function containing this address.
It's likely the SMNU widget parser or a widget renderer that's reading our malformed data.

Steps:
1. Find the function containing address 0x0063A232
2. Decompile it fully
3. Look at what it was trying to read (offset 2 from a null pointer = struct->field_02)
4. Trace back to see what struct it expected and how it's populated from SMNU data

## Secondary Target: SMNU Section Loader

The SMNU section is read from the CAM file and parsed into widget objects.
Find this parser by:
1. Search for string "SMNU" — find where the engine identifies this section type
2. Trace to the function that reads the SMNU binary blob
3. Decompile that function — it creates the panel's widget tree from the raw bytes

## What We Need to Know

### Panel Header
Our assumption (76 bytes):
```
[1000, 2, x, y, w, h, 10, 2, 10, flags, 12, "IMG", 13, tile, 18, "font", 11, "pal", -1]
```
Is this correct? What's the actual struct?

### Widget Definition
Our assumption was widgets start after the header and are variable-length, terminated by -1.
But our hand-built widgets crashed. What's the real widget format?

Key questions:
- Is there a widget COUNT field somewhere we missed?
- Is there a total size field that must match the actual data?
- Are widgets in a tree structure (parent-child) rather than a flat list?
- Does the "12, IMG_NAME" pattern REQUIRE a valid image set to be loaded?
- What happens if we reference "INTG" but the image isn't available?

### The STRT Connection
How does SMNU reference its STRT string table?
- By panel name match (same entry name in both sections)?
- By index?
- Is there a pointer/offset stored in the SMNU header?

## Approach

1. Decompile function at 0x0063A232 — see what struct access failed
2. Find the caller — what was building/populating that struct?
3. Trace to where SMNU bytes are read — that's the actual parser
4. Document the complete struct/format

## Fallback: Incremental Binary Testing

If decompilation is too complex, the alternative is:
1. Build a CAM that loads the ORIGINAL MX03 bytes unmodified as the override
2. Confirm it doesn't crash (proving override mechanism works)
3. Make ONE change (e.g., modify a single string index)
4. Test again
5. Repeat until we find what our custom panel got wrong

This is slower but doesn't require understanding the full parser.

## Also Generate Test CAM

While investigating, also produce a test CAM with the unmodified original MX03:
- Read MX03 from `DataMX/mx_textdata.cam`
- Pack it into a new CAM file named `Quest_textdata.cam` with entry name "MX03"
- Include the original STRT too
- This tests whether the override mechanism itself works (separate from our format issue)
