# Quest Map Generator — TODO

## Status: In-Game Validated ✅

Generated .q files load in-game successfully using the **minimal splice** approach
(replacing only the entry data within an existing template pattern).

### What Works
- Parser: 37/37 files pass
- Minimal splice: game loads the .q without freezing
- RGSEditor: reads our generated .q correctly (patterns, entries, positions all correct)
- Map generation: buildings spawn at the expected grid positions
- MQXML generation: game scans folder, quest appears in list

### What's Broken
- The `write_q_file()` function in `quest_map_generator.py` produces invalid structural
  bytes between patterns (metadata/faction transition blocks are wrong). This causes the
  game to freeze when scanning the Quests folder.
- The minimal splice approach (in `utility/test_decoder.py`) works but only replaces entries
  within ONE existing pattern — it doesn't rewrite the full pattern section.

---

## Template Mapping (MyQuest/Quest.q)

Confirmed via RGSEditor screenshots:

### Unit Patterns (4 definitions)

| RGSEditor Name | Parser Index | Binary Offset | Contents |
|---|---|---|---|
| Goblin Kingdom | 0 | 0x0433 | 2 Goblin Fortress + 6 Goblin Camp |
| AutoExpanding | 1 | 0x0555 | Originally: lairs + monsters surrounding player |
| Player1 | 2 | 0x07F3 | Palace (human player's starting building) |
| player2_ai | 3 | 0x0856 | Palace (AI opponent's starting building) |

### Force Pattern ("MyAI", Multi-Player 2)

7 instances placed on the 5×5 map grid:

| Instance | Unit Pattern | Map Position | Role |
|---|---|---|---|
| 0 - Player1 | Player1 | W (2,4) | Human player (blue) |
| 1 - player2_ai | player2_ai | C (2,0) | AI opponent (red) |
| 2 - AutoExpanding | AutoExpanding | R (2,3) | Neutral expanding faction |
| 3 - Goblin Kingdom | Goblin Kingdom | S (3,3) | Enemy goblin cluster |
| 4 - Goblin Kingdom | Goblin Kingdom | Q (1,3) | Enemy goblin cluster |
| 5 - Goblin Kingdom | Goblin Kingdom | ? | Enemy goblin cluster |
| 6 - Goblin Kingdom | Goblin Kingdom | ? | Enemy goblin cluster |

```
Map Layout (Force Pattern grid):
     col0   col1   col2   col3   col4
row0:  .      .     AI(1)   .      .
row1:  .      .      .      .      .
row2:  .      .      .      .      .
row3:  .    Gob(4) Auto(2) Gob(3)  .
row4:  .      .   Player(0) .      .
```

### Force Pattern Freestyle Options
- Allowed Players: Single Player, Two Player
- Allowed Map Sizes: Medium (128×128), Large (256×256), Huge (512×512)
- Difficulty Ratings: Money=50, Time=50, Kill All=50

### Key Insight: <Name> in .mqxml
- The `<Name>` tag is the GPL initialization function called at quest start
- If the function doesn't exist, game shows error dialog but still loads
- For quests without custom GPL, use a name that exists in the loaded bytecode
  (e.g., a base game quest name) or accept the error popup
- `<DisplayName>` is what shows in the quest selection UI

---

## Next Steps

### 1. Fix write_q_file() — use minimal splice approach

The current writer tries to rebuild the entire pattern section from scratch (metadata blocks,
faction names, transition bytes) and gets the structure wrong. Fix:

**Replace the approach**: Instead of writing all patterns from scratch, do what
`utility/test_decoder.py` does — splice entry data into existing pattern slots:

```
For each pattern to modify:
  1. Find the pattern header in template: [terrain][u32 5][u32 count]
  2. Replace [u32 count][entries...] with new count + new entries
  3. Leave all metadata, faction names, and structural bytes untouched
```

This means:
- The number of patterns stays the same as the template (4)
- To add entries to the player's area: modify Pattern 2 (Player1)
- To add monster lairs: modify Pattern 0 (Goblin Kingdom) or Pattern 1 (AutoExpanding)
- The Force Pattern, Region Pattern, metadata blocks all stay byte-identical

### 2. Target the correct pattern for player buildings

For test quests where we want the player's Palace + nearby lairs:
- Palace → Pattern 2 ("Player1", offset 0x07F3) — this is where the human player starts
- Monster lairs → Pattern 0 ("Goblin Kingdom", offset 0x0433) — enemy territory
- Or Pattern 1 ("AutoExpanding", offset 0x0555) — neutral expanding

### 3. Handle the <Name> field properly

Options:
- Generate a minimal GPL .bcd with an empty init function matching the quest name
- Or hardcode a known-working name from the base game bytecode
- Or document that the error popup is cosmetic (quest still loads)

### 4. Remove the InGameTest deployment after testing

The `C:\Users\Brandon\Documents\My Games\MajestyHD\Quests\InGameTest` folder
should be cleaned up once testing is complete.

---

## Known Limitations

- Template locked to MyQuest/Quest.q structure (4 patterns, specific Force Pattern layout)
- Cannot add/remove patterns without breaking Force Pattern references
- Random GUID works but RGSEditor shows a numeric ID representation
- Seed=0 in template means different map each time (no reproducible layout)
