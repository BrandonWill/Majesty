---
inclusion: manual
description: How to create Quests and Mods for Majesty HD — RGSEditor workflow, file formats, Steam Workshop
---

# Making A New Quest

A complete Quest definition in Majesty contains several parts:

| Component | Extension | Purpose |
|-----------|-----------|---------|
| Quest Definition file | `.mqxml` | Master file — description, display name, references to all other files |
| Quest Template | `.q` | Map layout and starting conditions (edited by RGSEditor) |
| GPL Bytecode | `.bcd` | Compiled GPL source code the Quest runs |
| Game Object Definitions | `.xml` | Optional — create or modify Buildings, Characters, Sounds |
| Art/Sound Binary Data | `.cam` | Images and sounds for game objects |
| RGS Constants | `.rgs` | Random Generation System data for map generation |

**Adding Game Object Definitions, Binary Data, and changing RGS Constants is optional** — a Quest can use just existing Majesty assets.

## Getting Started

1. Create the Quest Definition file and Quest Template using the **RGSEditor** (in the SDK folder).
2. Launch RGSEditor → File → New Quest...

## Create New Quest Dialog

Define the following:

- **GPL Initialization Function Name** — not case sensitive, no spaces (only underscore allowed)
- **Data Set** — Original Majesty or Northern Expansion
- **Map Size** — dimensions of the generated map
- **Random Seed** — 0 = new seed every time; fixed value = same map each time (useful for testing)

Example: Function name `InitializeMyQuest`, data set `Majesty:Original`.

## Unit Patterns

A Unit Pattern describes the placement layout of one or more units.

**Key properties:**
- 5×5 grid layout
- Variable resolution (spacing between center points of grid cells)
- Spacing adjusts based on map size
- Overlap prevention — units placed as close as possible without overlapping
- Grid is randomly rotated for placement variety

**Each unit definition is placed only once for the entire pattern.** Marking a unit at multiple grid locations randomizes WHERE it appears (the RGS picks one location).

### Adding Units to a Pattern

1. Press Add... in the Unit section
2. Select category (Buildings, Characters, etc.) and unit type
3. Click grid locations to set candidate positions

**Multiple units at one grid location:** Grid shows `*`. Only one unit is chosen for that location at generation time.

**Same unit type multiple times:** Add multiple Unit instances referencing the same type. Each gets its own grid positions and each is placed exactly once.

### Layout Grid Resolution

The Resolution dropdown controls spacing between grid cells. A tile is 32 pixels wide, so resolution of 3 = 96 pixels between neighbors.

### Randomization

- Mobile units (monsters, heroes) and terrain objects get an additional random shift of up to 100 pixels (~3 tiles)
- The entire placement grid is randomly rotated (0°/90°/180°/270°)

## Force Patterns

A Force Pattern defines how Unit Patterns are placed on the map as a whole. Most quests have one Force Pattern laying out all Unit Patterns.

1. Quest menu → Edit Force Patterns...
2. New... → name it (e.g., "Quest Layout")
3. Add... → select a Unit Pattern (e.g., "Player Start")
4. Click a Map Layout grid entry to set position

## Region Patterns

A Region Pattern defines terrain appearance and landscape objects (trees, rocks).

1. Quest menu → Edit Region Pattern...
2. New... → name it (e.g., "Quest Terrain")
3. Add Region Patches

### Region Patches

Each patch contains:
- **Terrain Pattern** — texture type (see below)
- **Fractal Settings** — terrain bumpiness
- **Landscape Pattern** — landscape objects placed on terrain

### Terrain Types

| Type | Appearance |
|------|-----------|
| Dirt | Brown dirt, occasional small rocks and grass tufts |
| Plains | Light green grass |
| Plains (child) | Dark green grass |
| Arid | Very light green grass, occasional brown grass tufts |
| Arid (child) | Yellowed grass, occasional light green tufts |
| Scorch | Gray dirt, occasional grass tufts |
| Scorch (child) | Dark gray dirt, occasional rocks |
| Swamp | Green/blue dirt, occasional dark grass tufts |
| Swamp (child) | Red/brown dirt, occasional dark grass tufts |
| Snow | Snow-covered dirt |

### Fractal Settings

Controls terrain bumpiness. Predefined options include "Rolling Hills", "Small Hills", etc.

### Landscape Patterns

Controls what landscape objects appear and how many. Example: `#BBC_Grass` (from Bell Book and Candle Quest — green leafy trees + rocks).

### Region Pattern Configuration

- **Amount Present** slider — percentage of map covered by each patch
- **Number of Seeds** slider — how many seed points the RNG uses for distribution

## The Project View

Switch via Edit menu → Project View. Shows all Quest Definition values:

- GPL Initialization Function Name
- Map Size
- Random Seed
- Difficulty
- GUID (unique identifier)
- Display Name
- Short/Long Description
- Data Set
- Load section (files)

### GUID Rules

- Auto-generated on Quest creation
- **MUST change** if using an existing Quest as a template for a new one
- Changing it invalidates previous save games
- Generate new: click current ID → press ellipses button (…)

### Description Line Breaks

Use `[newline]` tag in Short/Long descriptions for line breaks.

### Load Section

Right-click sub-sections to add/remove files. Sub-sections:
- Descriptions (XML)
- CAM (binary data)
- GPL Bytecode
- Strings
- Quest Template

**Files don't need to exist when added** — useful for bytecode files that will be compiled later.

**Paths are fully qualified when added but automatically made relative** to the Quest save location. Best practice: keep all files at or below the Quest save location.

## Compiling GPL Source to Bytecode (.bcd)

In the Project View:
1. Specify target bytecode file
2. Add source files to the GPL Bytecode entry
3. Right-click the Entry → Compile

The RGSEditor creates a temporary `.gplproj` file and calls the GPL compiler (must be in same directory as RGSEditor.exe). Output appears in the Log window.

**Compile All:** Right-click GPL Bytecode entry → Compile All, or use Quest menu → Compile GPL.

---

# Quest Definition File Format (.mqxml)

XML formatted file. Can be edited manually with a text editor (don't have it open in RGSEditor simultaneously).

## Example (Wrath Of Krolm)

```xml
<Majesty>
  <Quest id="{9757F443-4229-41dc-860B-9BD980D72733}">
    <Name>WrathOfKrolm</Name>
    <DisplayName lang="en_US">Wrath of Krolm - The Example</DisplayName>
    <Description lang="en_US">
      <Short>Destroy all Altars to Krolm, or defeat his Avatar...</Short>
      <Long>"The followers of Krolm have challenged..."</Long>
    </Description>
    <Difficulty>Hard</Difficulty>
    <DataConfiguration>
      <Dataset base="Majesty">
        <Load>
          <Descriptions>Data/WrathOfKrolm_Actions.xml</Descriptions>
          <Descriptions>Data/WrathOfKrolm_Sounds.xml</Descriptions>
          <Descriptions>Data/WrathOfKrolm_Characters.xml</Descriptions>
          <Descriptions>Data/WrathOfKrolm_Buildings.xml</Descriptions>
          <Descriptions>Data/WrathOfKrolm_Overlays.xml</Descriptions>
          <CAM>Data/WrathOfKrolm_maindata.cam</CAM>
          <CAM>Data/WrathOfKrolm_soundfx.cam</CAM>
          <CAM>Data/WrathOfKrolm_voices.cam</CAM>
          <GPL>Data/WrathOfKrolm.bcd</GPL>
          <GPLSource>GPL</GPLSource>
          <Template>Quests/WrathOfKrolm.q</Template>
          <Strings>Data/WrathOfKrolm_Text.xml</Strings>
        </Load>
        <Unload>
          <CAM/>
          <GPL/>
          <Constants/>
        </Unload>
      </Dataset>
    </DataConfiguration>
  </Quest>
</Majesty>
```

## Tag Reference

### `<Majesty>` — Top-level tag (always present)

### `<Quest id="...">` — Formal Quest Definition
- `id` attribute: Standard GUID, unique per quest
- Auto-generated by RGSEditor
- **Never reuse** for another quest
- Save games store the id to know what quest data to load

### `<Name>` — Compact Identifier
- Letters and numbers only (no spaces, no special characters)
- Primary use: name of the GPL function called when the Quest begins
- If no GPL function of that name exists, the game shows an error dialog
  (`GplDispatcherHandle error: script $Name() doesn't exist`) but the Quest still
  loads after clicking OK — just with no custom initialization or victory conditions
- **Best practice:** Either provide a matching GPL function, or use a name that already
  exists in the base GPL (e.g., `basicAI` from the template) to avoid the error popup

### `<DisplayName lang="...">` — Screen Display Name
- Shown in Quest list UI
- `lang` attribute: language/country code

**Supported language codes:**
| Code | Language |
|------|----------|
| `en_US` | English, USA |
| `fr_FR` | French, France |
| `de_DE` | German, Germany |
| `es_ES` | Spanish, Spain |
| `it_IT` | Italian, Italy |
| `en_GB` | English, Great Britain |
| `ja_JA` | Kanji, Japan |
| `ko_KR` | Korean, Korea |
| `zh_CN` | Simplified Chinese, China |
| `zh_TW` | Simplified Chinese, Taiwan |
| `pl_PL` | Polish, Poland |
| `ru_RU` | Russian, Russia |
| `pt_PT` | Portuguese, Portugal |

Multiple `<DisplayName>` entries allowed (different `lang` values). Falls back to `en_US` if requested language missing.

### `<Description lang="...">`
- Child tags: `<Short>` and `<Long>`
- Short: quest goals (available during gameplay as reminder)
- Long: displayed at quest start
- Same `lang` attribute and multiple-language support as DisplayName

### `<Difficulty>`
Values: `Easy`, `Medium`, `Hard`, `Master`

### `<DataConfiguration>` → `<Dataset base="...">`
- `base` attribute: `Majesty` or `MajestyExpansion`
- `Majesty` = original game art/sound/GPL
- `MajestyExpansion` = Northern Expansion art/sound/GPL
- **Warning:** Changing base after creation can cause crashes (Quest Template is tightly coupled to data set)

### `<Load>` — Files to load

| Tag | Purpose |
|-----|---------|
| `<Descriptions>` | XML files with asset definitions (Characters, Buildings, Sounds, Actions) — can also modify existing assets |
| `<CAM>` | Binary art/sound data |
| `<GPL>` | Compiled GPL bytecode (.bcd) |
| `<GPLSource>` | Relative path to GPL source (for debugger — optional but useful). Searches recursively through sub-folders. Multiple entries allowed. |
| `<Template>` | RGS quest template (.q) — only one entry |
| `<Strings>` | Text displayed by the Quest |

### `<Unload>` — Files to unload (rare)
Used when a Quest completely replaces base data file contents.

---

# Mod Definitions (.mmxml)

Mods are similar to Quests but loaded **alongside** a Quest, modifying the base data set.

## Key Differences from Quests

| Aspect | Quest | Mod |
|--------|-------|-----|
| Primary tag | `<Quest>` | `<Mod>` |
| File extension | `.mqxml` | `.mmxml` |
| Dataset base options | `Majesty` or `MajestyExpansion` | `Majesty`, `MajestyExpansion`, or `Any` |
| Template tag | Required | Ignored |
| Map view in RGSEditor | Yes | No (independent of quest map) |
| Loading | Standalone | Loaded with a Quest |

## Dataset Compatibility

- `base="Any"` → loaded with ANY quest (if mod only changes things common to both datasets or adds new data)
- `base="Majesty"` → only loaded with Majesty-base quests
- `base="MajestyExpansion"` → only loaded with expansion-base quests

## Multiple Mods

- Multiple mods can be active simultaneously
- Load in the order they appear in the Active Mods list
- Incompatible mods (wrong base) are silently skipped

## Example (Adjust Guardhouse)

```xml
<Majesty>
  <Mod id="{D666FCBE-9906-4582-A6A0-DC96F812441E}">
    <Name>AdjustGuardHouse</Name>
    <DisplayName lang="en_US">Adjust Guardhouse</DisplayName>
    <Description lang="en_US">
      <Short>Upgraded guard houses increase the number of guards posted
        at the guard house to two.</Short>
      <Long></Long>
    </Description>
    <DataConfiguration>
      <Dataset base="Any">
        <Load>
          <GPL>Data/AdjustGuardhouse.bcd</GPL>
        </Load>
      </Dataset>
    </DataConfiguration>
  </Mod>
</Majesty>
```

## Creating a Mod

1. RGSEditor → File → New Mod...
2. Edit values in Project View
3. Add GPL/Data files to Load section
4. Compile GPL if needed

---

# Data Descriptions (XML)

Game objects and actions are defined by data descriptions.

## Structure

- **type** — primary type (Unit, Sound)
- **subtype** — for Units: Building, Character, Projectile, Overlay, Particle System
- **name** and **ID** — identifiers
- **Engine section** — common values (not game-specific), same across all subtypes
- **Game section** — Majesty-specific values, varies by subtype

## Usage

- Majesty shipped descriptions in binary format
- SDK provides XML versions
- User-generated Quests can create/modify XML description files
- Add them to the Quest Definition's `<Descriptions>` tag
- Modifications to existing assets override the base data

---

# Steam Workshop

## Upload Process

1. RGSEditor → File → Steam Workshop Upload...
   - If grayed out: Steam Client not running — restart Steam then RGSEditor

## Workshop Project Settings

| Field | Notes |
|-------|-------|
| **Visibility** | Private, Friends Only, or Public. Keep Private/Friends until stable. |
| **Content** | Directory with your Mod/Quest files. Usually `My Games/MajestyHD/Mods/YourMod` |
| **Preview** | Screenshot or artwork (.png/.jpg, under 1MB). Do NOT put in content folder. Save near Workshop project file. |
| **Tags** | Check all relevant: Mod, Quest, Character, Building, Majesty, Northern Expansion, etc. |
| **Title** | 128 characters or less. Required. |
| **Description** | 5000 characters or less. Required. Explain what the Mod changes or Quest goals. |

## Content Best Practices

- Everything in the content directory gets uploaded (including subdirectories)
- Keep contents minimal — only what the Mod/Quest needs
- Including `.gpl` source files is encouraged (lets others see your changes)
- Build from just your changes to the SDK, not the whole SDK

## Upload Steps

1. Fill in all project values
2. File → Save (save the workshop project file)
3. File → Upload...
4. Enter optional Change Note → OK
5. **IMPORTANT:** After first upload, save the project file again (Steam assigns an ID that must be preserved)

## Recovering Lost Workshop ID

If you forget to save after first upload:
1. Go to your Workshop item page (Steam Client or browser)
2. Look at URL: `?id=yourItemNumber`
3. Edit project file with text editor → put number in `id` attribute of `SteamWorkshop` tag

## Updating

1. Reload saved Workshop project
2. Most fields will be unchecked/grayed (won't re-upload unless checked)
3. File → Upload...
4. This prevents overwriting changes made through the Workshop web pages

## Subscribing and Loading

- Users subscribe via Steam Workshop page
- Steam Client downloads to Steam install directory (NOT the My Documents location)
- If you subscribe to your own mod, it appears twice in-game (local copy + Steam copy)
- Save games look for matching Mod/Quest ID — local My Documents copy takes priority

---

---

# Programmatic Quest Generation (No RGSEditor)

There is an ongoing project to generate `.q` quest template files programmatically, bypassing
the RGSEditor entirely. See `QuestMapGenerator/quest_map_generator.py` and the
`Quest Map Generator` section in the main steering file (`majesty-modding.md`) for details.

**Current status:**
- Parser reads all .q format versions (RGMa, RGM6, RGM9) — 37/37 files pass
- Writer uses a template-based approach (splices custom UnitPattern entries into a known-good .q)
- CLI supports `parse`, `validate`, `generate` subcommands
- Convenience API: `generate_test_quest(name, lairs, output_dir)`
- **No generated quest has been loaded in-game yet** — see `QuestMapGenerator/TODO.md`

**When to use RGSEditor vs QuestMapGenerator:**
- RGSEditor: full control over terrain, Region Patterns, Force Patterns, visual preview
- QuestMapGenerator: automated/batch generation of test quests, CI-friendly, no GUI needed

The long-term goal is to eliminate the RGSEditor dependency for quest creation workflows
that can be fully described in code (e.g., test quests for mod validation, procedural quest packs).

---

# Quick Reference: Minimum Viable Quest

1. **RGSEditor** → New Quest → set name, data set, map size
2. **Unit Pattern** → at least one (e.g., Palace placement)
3. **Force Pattern** → places Unit Pattern on map
4. **Region Pattern** → at least one Region Patch (terrain + fractal + landscape)
5. **GPL** → write initialization function matching the Quest name (optional but needed for win conditions)
6. **Compile** → Quest menu → Compile GPL
7. **Save** → creates `.mqxml` + `.q` files
8. Copy to `My Games/MajestyHD/Quests/YourQuest/` folder
9. Launch game → Quest appears in Quest list

# Quick Reference: Minimum Viable Mod

1. **RGSEditor** → New Mod → set name, data set (Any/Majesty/MajestyExpansion)
2. Write GPL source modifying desired behavior
3. Compile GPL → produces `.bcd`
4. Add `.bcd` to Mod's Load section
5. Optionally add XML descriptions (character/building/sound modifications)
6. Save `.mmxml`
7. Copy to `My Games/MajestyHD/Mods/YourMod/` folder
8. Launch game → Mod appears in Mod list → activate it
