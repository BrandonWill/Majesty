# Quest Map Generator — TODO

## Status: Fully Working ✅

Generated quests load in-game with no errors. Default win condition included.

### What Works
- Parser: 37/37 files pass
- Writer: minimal splice approach — in-game validated, no freeze
- Default GPL: `DefaultQuest()` function with `$setvictorycondition()` — no error dialog
- MQXML generation: correct format, quest appears in list with DisplayName
- Slot assignment: lairs → Pattern 0 (enemy quadrant), Palace → Pattern 2 (player quadrant)
- Full CLI: `generate` subcommand produces complete quest package in one call

### Usage

```bash
# Generate a quest with Palace + lairs
python quest_map_generator.py generate --name "My Quest" --output output\MyQuest --lairs "BBH1:Goblin Camp:N,BBw1:Ice Cave"

# Deploy to game
xcopy /E /Y output\MyQuest "C:\Users\Brandon\Documents\My Games\MajestyHD\Quests\MyQuest\"
```

---

## Template Mapping (MyQuest/Quest.q)

### Unit Pattern Slots

| Slot | RGSEditor Name | Role | What to put here |
|---|---|---|---|
| 0 | Goblin Kingdom | Enemy territory | Monster lairs (placed in enemy quadrant) |
| 1 | AutoExpanding | Neutral expanding | Additional structures (center-south) |
| 2 | Player1 | Human player start | Palace + player-area buildings |
| 3 | player2_ai | AI opponent | AI Palace (top of map) |

### Force Pattern Layout
```
     col0   col1   col2   col3   col4
row0:  .      .     AI(1)   .      .
row1:  .      .      .      .      .
row2:  .      .      .      .      .
row3:  .    Gob(4) Auto(2) Gob(3)  .
row4:  .      .   Player(0) .      .
```

---

## Remaining Work

### Put lairs near the player (not in enemy quadrant)

Currently `generate_test_quest` puts lairs in slot 0 (Goblin Kingdom = enemy quadrant,
far from player). For testing mods like IceSpell where you want the player to encounter
lairs quickly, lairs should go in slot 2 (Player1) alongside the Palace.

**Option:** Add a `--near-player` flag that puts lairs in slot 2 instead of slot 0.

### Add `--deploy` flag to CLI

Automatically copy the generated quest to the game's Quests folder:
```bash
python quest_map_generator.py generate --name "Test" --output out --lairs "..." --deploy
```

### Terrain preset support

The code has terrain presets (grass, snow, scorched, etc.) but they require modifying
the Region Pattern section which hasn't been validated in-game. Low priority since the
template's terrain works fine for testing.

### Explore RGSEditor decompiled source

`SDK/RGSeditor/` may contain source code that reveals exact binary formats for:
- Region Pattern section
- Force Pattern section
- Metadata block meanings

This could enable generating those sections from scratch instead of relying on templates.

---

## Known Limitations

- Template locked to MyQuest/Quest.q structure (4 pattern slots, fixed Force Pattern)
- Cannot add/remove pattern slots without breaking Force Pattern references
- Lairs in slot 0 appear in enemy quadrant, not near player
- Seed=0 means different map each time (set fixed seed in template for reproducibility)
- Goblin Kingdom pattern is reused 4× by Force Pattern — all 4 get modified together
