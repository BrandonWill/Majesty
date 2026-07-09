# IceSpell Mod — TODO

## Current Status

Everything works EXCEPT the Quest_maindata.cam IMAG records. The game crashes on CAM load with no error messages.

- ✓ Mod loads (GUID valid, mmxml format correct)
- ✓ IceElemental spawns from Ice Cave
- ✓ GPL freeze logic runs correctly (all DebugOut confirmed)
- ✓ TILE sprite frames are valid (round-trip verified, palette_id=0)
- ✓ SPLT palette correct
- ✓ CAM has 3 sections (no CUT) matching WrathOfKrolm structure
- ✓ IR01/IR02/IR03 names are UNIQUE — no conflicts in maindata.cam, mx_maindata.cam, or WoK CAM
- ✗ IMAG record binary format is wrong — causes hard crash on zone load

---

## The Problem: IMAG Record Writing

We can READ/PARSE IMAG records correctly. We cannot WRITE new ones that the engine accepts.

Previous attempts:
1. Built IMAG from scratch with guessed offsets → crash
2. Copied MRB1's first 128 bytes as template → crash
3. Fixed palette_id and removed CUT section → crash

The IMAG record format has unknown metadata fields that we're getting wrong.

---

## Solution: Use WrathOfKrolm's XR47 as Template

The WrathOfKrolm mod CAM (`SDK/Example/Data/WrathOfKrolm_maindata.cam`) has 5 working IMAG records. The simplest is:

- `XR47DustofDeth` — 292 bytes (a directionless overlay, exactly like our ice effector)
- `KR0TKrolm-appear` — 364 bytes (another overlay)

These are PROVEN WORKING in a mod-loaded CAM file. The next step is:

1. Byte-dump `XR47DustofDeth` completely
2. Compare its structure against MRB1 (from base maindata.cam) to find differences
3. The difference between MRB1 (works in base CAM) and XR47 (works in mod CAM) may reveal what's special about mod CAM IMAG records
4. Build our IR01 matching XR47's exact structure, just with different frame count/tile indices

Key question: Does a mod CAM IMAG reference TILE indices relative to ITS OWN TILE section (0, 1, 2...) or relative to the combined global pool? XR47's tile indices will tell us.

---

## Deployment Info

- Mod folder: `C:\Users\Brandon\Documents\My Games\MajestyHD\Mods\IceSpell`
- Junction link from repo → mod folder (no copying needed)
- Compile: `gplbcc.exe -in IceSpell.gplproj -out IceSpell.bcd -stdout` in the GPL folder
- Deploy: just git pull (junction handles the rest)

---

## File State

```
IceSpell/
├── IceSpell.mmxml              ✓ Working
├── Data/
│   ├── IceSpell.bcd            ✓ Compiles and loads
│   ├── IceSpell_Actions.xml    ✓ Loaded
│   ├── IceSpell_Characters.xml ✓ IceElemental spawns
│   ├── IceSpell_Overlays.xml   ✓ References IR01/IR02/IR03
│   └── Quest_maindata.cam      ✗ IMAG format wrong — crashes
├── GPL/
│   ├── IceSpell.gpl            ✓ Debug version with $DebugOut
│   ├── IceSpell_Globals.dat    ✓ IceElemental data + Ice_Cave override
│   └── IceSpell.gplproj        ✓ Compiles
└── sprites/                    ✓ TILE frames (round-trip verified)
```

---

## Workaround (for testing freeze mechanics without custom sprites)

Remove `<CAM>Data\Quest_maindata.cam</CAM>` from mmxml and change overlay XML to use `ImageIDBase value="MRB1"` (petrify sprite from base game). This confirms the full freeze/unfreeze cycle works while the IMAG format is being cracked.
