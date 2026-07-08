# Majesty HD Sprite Editor

A work-in-progress toolset for extracting, viewing, and injecting sprite graphics
into Majesty Gold HD's `maindata.cam` binary data file.

## Status

| Component                          | Status        |
|-------------------------------------|---------------|
| Container format (sections/files)  | ✅ Solid - validated against real `` C# source |
| IMAG blob parsing (image-set table)| ✅ Confirmed against 3 units (Adept, Barbarian, Warrior) |
| Frame descriptor / direction blocks| ✅ Confirmed against 2 directional units |
| TILE index resolution              | ✅ Confirmed - frame indices resolve to real, sensible TILE entries |
| TILE pixel payload format          | ✅ **CRACKED** - 8-bit paletted, per-row RLE with absolute x-positioning |
| Palette system                     | ✅ **SOLVED** - SPLT section holds 854 RGBA palettes, indexed by u32 at TILE byte 22 |
| PNG extractor                      | ✅ Working with correct colors and transparency |
| Palette identification             | ✅ Automatic - each TILE entry embeds its palette index |
| PNG injector                       | ⬜ Not started |
| GUI tool                           | ⬜ Stretch goal |

## Files

- `RESEARCH_NOTES.md` — Full reverse-engineering findings, current as of the  breakthrough
- `cam_reader.py` — Faithful Python port of ``'s container-format reader. Trust this over hand-derived offset math.
- `sprite_extractor.py` — Built on `cam_reader.py`. Parses IMAG blobs (image-set tables, frame descriptors, per-direction geometry) and resolves frame indices into the TILE section. Cannot yet produce PNGs - the TILE payload format itself isn't decoded.
- `` / `proj` — Ground-truth C# unpack/pack tool source (not built/run in this environment - no .NET SDK or network access here, so it was ported to Python instead).

## Quick Start

```
python sprite_extractor.py --cam maindata.cam --list
python sprite_extractor.py --cam maindata.cam --dump-anim AVA1
python sprite_extractor.py --cam maindata.cam --dump-frames AVA1 Walk
python sprite_extractor.py --cam maindata.cam --extract AVA1 Walk
python sprite_extractor.py --cam maindata.cam --extract-tile 3547
```

## What changed this session

A previous session found the real `` source (someone else's
validated unpack/pack tool for this exact format). That's a much stronger
source of truth than continued hand-decoding, and it caught real bugs:

- The container-format section directory was being misparsed (a tag/offset
  byte-alignment bug), leading to a false belief that the pixel-index
  section was tagged `CUT` with 854 entries. It's actually tagged `SPLT`.
  A real, separate `CUT ` section exists but only has 20 entries.
- The image-set table format (inside each unit/building's IMAG blob) was
  wrong - assumed 12-byte `(setID, frameCount, relOffset)` triplets, but
  it's actually a `u32` count followed by 8-byte `(setID, relOffset)` pairs,
  with no frame-count field in this table at all.
- **The single most important finding:** neither `SPLT` (854 entries, fixed
  1032 bytes each) nor `CUT` (20 entries, fixed 886 bytes each) is where
  character animation pixel data lives - both are too small and too
  uniformly-sized. The real home is the **`TILE` section, with 17,224
  variable-sized entries** - confirmed by checking that frame descriptor
  indices (e.g. 3547+) resolve to real, sensibly-sized TILE entries, for
  two different units (Adept, Barbarian).

Frame descriptor parsing was also corrected and validated against a second
unit: direction offsets must be read as **signed**, and frame count per
direction is best derived from the byte-distance to the next populated
direction slot, not from a header field (which gave a wrong answer when
checked against Barbarian's data).

## Next Steps (for next session)

1. **Build the PNG injector** — Encode a PNG back into the RLE format:
   - Quantize colors to the target SPLT palette (or create a new one)
   - Encode rows as `[u16 x_pos][u8 count][u8 flags][pixel bytes]` segments
   - Build the u32 offset table and TILE header
   - Replace the TILE entry in the CAM archive and repack
2. **CAM repacker** — Port or integrate the m-architek  pack logic
   to write modified TILE/SPLT entries back into maindata.cam.
3. **Test full round-trip** — Extract → modify PNG → re-inject → verify in-game.
4. **New unit creation** — Requires creating new IMAG blob, TILE entries,
   SPLT palette, and hooking into `unittype.cam` definitions.
