# Complete Requirements: Adding a New Hero — TODO

**Goal:** Answer "how do I add a new hero to Majesty Gold HD?" completely
— every requirement, every file touched, every gotcha — as a standalone
reference modders can follow end to end. Not scoped to GPL alone: sprite/
CAM requirements, XML schema, sound, and UI/recruitment integration all
belong here. Where the honest answer is "this lives in CAM_MODDING_GUIDE.md
under X" or "this is UNVERIFIED, needs Ghidra," say so explicitly rather
than skipping it.

## Evidence Standard (same as GPL_MODDING_GUIDE.md's — non-negotiable)

Every requirement claimed here must cite the specific file/function/line
(GPL), XML attribute (with a real example from shipped data), or CAM
section/field (with a real example, ideally extracted via `cam_reader.py`/
`sprite_extractor.py` to confirm dimensions/format) it was verified
against. No claim from "this is probably required because similar systems
need it." If something can't be confirmed from available source, mark it
**UNVERIFIED**/**UNKNOWN** explicitly — do not silently assume a
requirement exists or doesn't. This is the same standard that already
caught two false-analogy mistakes during the GPL deep dive — see that
doc's "Retracted Claims" for what NOT to do.

**This is expected to be incomplete after the first pass.** Mark
genuinely unresolved gaps as gaps, don't paper over them to look complete.

## Target Output

A `NEW_HERO_REQUIREMENTS.md` guide (or a new section in an existing guide —
decide once the research below is done) structured as a literal checklist:
"to add a new hero, you need ALL of the following, in this order, or the
game will [crash/silently fail/not appear]." Every checklist item traces
back to a citation in this file.

## Required Coverage Areas

### 1. Sprite/Art Requirements (cross-reference CAM_MODDING_GUIDE.md,
verify with real examples via cam_reader.py/sprite_extractor.py — don't
just restate the guide's existing IMAG/TILE section, confirm it against an
actual hero's real data)
- [ ] Which animation sets are MANDATORY vs optional for a hero
  specifically (Walk, Stand, Attack, Die, Cast, Special, Carry, Recoil,
  Damage, Minimap, Sel-Underlay/Overlay — per `ImageSetIDXRef.xml`'s
  setID table already known from CAM_MODDING_GUIDE.md). Confirm by
  checking whether ANY shipped hero is missing one of these sets — if
  none are ever missing a given set, that's evidence it's mandatory; if
  some heroes lack a set, that's evidence it's optional. Don't assume,
  check actual IMAG records.
- [ ] Frame dimension/hotspot conventions — is there a fixed canvas size
  heroes must use, or does it vary per hero? Check multiple real heroes'
  TILE dimensions.
- [ ] 8-directional requirement — confirmed for which animation sets
  specifically? (Die was noted in earlier research as having "more
  variants" than 8 — confirm the exact count and why.)
- [ ] Palette constraints — must a new hero use an EXISTING SPLT palette,
  or can a quest-scoped hero ship its own palette? (SPLT is documented as
  read-only for existing entries — does that restriction apply to
  quest-added new palette entries too?)
- [ ] Minimap icon requirements (setID 300 per existing docs) — mandatory?
- [ ] What happens if a required animation frame is missing at runtime —
  UNVERIFIED unless something in GPL/engine behavior confirms it
  (silent fallback, crash, T-pose equivalent?) — mark UNVERIFIED if not
  confirmable from source, don't guess.

### 2. Unit XML Definition Requirements (M_Characters.xml / MX_Characters.xml)
- [ ] Full required-field catalog for `type="Unit" subType="Character"`
  with `CanUse value="HumanPlayer"` — read multiple real hero definitions
  side by side (not just one) to determine which fields are ALWAYS present
  vs. sometimes-omitted-with-a-default.
- [ ] `Menu value="N"` — confirm what N=6 (hero, per existing partial
  note) actually controls, and whether other menu values also work for
  heroes or specifically break something if wrong.
- [ ] Stat fields (MaxHP, Attack, Speed, SightRange, Intelligence, etc.) —
  full list, not a sample — read a real hero's complete `<Game>` block.
- [ ] `AllowedSpells` — how spells are actually granted to a hero class,
  confirmed against real XML, and what happens if a spell in the list
  doesn't exist or the hero's level is below `CharacterLevel` (tie to the
  existing "what happens if AllowedSpells references an incompatible
  spell" open question in TODO-GPL-Deepdive.md if still unresolved there).
- [ ] `Attachment kind="Movement"` — which DMOV classes exist, which ones
  are valid for heroes specifically vs. monsters-only.
- [ ] Inventory/equipment slot requirements — is this XML-defined,
  GPL-defined, or engine-hardcoded per hero class?

### 3. GPL Requirements (cross-reference GPL_MODDING_GUIDE.md's existing
findings — don't re-derive what's already confirmed there, but DO verify
anything that guide left as UNVERIFIED and is now blocking this checklist)
- [ ] Decision tree file — is a NEW hero class required to have its own
  dedicated decision tree file (`DecisionTrees/<ClassName>.gpl`), or can
  it reuse an existing class's tree? What's the actual wiring point in
  `.dat`/prototype that connects a hero title to its decision tree?
  (This wiring point was NOT confirmed in the existing GPL deep dive —
  genuinely new territory.)
- [ ] `prototype hero()` fields — full required-vs-optional list (existing
  GPL guide documents ActiveScript/BackScript/TaskName but not the FULL
  hero prototype schema — read `prototype.gpl`'s `hero()` block completely
  for this task, not just the 3 fields already covered).
- [ ] Birth wiring — `Hero_Data.dat`'s required fields for a new hero
  entry (IGdeathscript, birthscript, StartingScript, etc.) — full
  required-field catalog, not just the death-related ones already
  documented.
- [ ] Death handling — already covered by GPL_MODDING_GUIDE.md §8, cite
  it, don't re-derive, but confirm a NEW hero class doesn't need anything
  beyond what's already documented there (e.g. does every hero need its
  own death function, or can it use the generic `gravestone()`?).
- [ ] GPL bytecode compilation and dataset wiring — how does a new hero's
  decision tree GPL actually get compiled and loaded as part of the base
  game vs. as a mod? (`.gplproj`/`Path.gplproj` structure, `DataSets.xml`
  GPL bytecode loading groups per CAM_MODDING_GUIDE.md's brief mention —
  needs a real end-to-end trace for a NEW hero class specifically, not
  just "existing classes are compiled this way.")

### 4. Sound Requirements
- [ ] What sound definitions/WAVE entries are mandatory for a hero
  (voice lines, combat sounds) vs. optional — check `DefaultSound`/
  `SoundPhase` usage across real hero definitions.

### 5. Recruitment — How a Hero Actually Enters the Game (GENUINELY
UNRESEARCHED — this is the biggest gap, trace it fully, don't assume it's
"just like birth")
- [ ] How does clicking "Recruit" in a guild/temple panel actually create
  a new hero agent and add it to the player's roster? Trace the full
  chain: panel click → action code → GPL function → `$SpawnUnit` or
  equivalent → hero attached to Palace/player.
- [ ] Is recruitment building-specific (different mechanism per guild
  type) or does it funnel through one shared recruit function? (Compare
  to the already-confirmed "no single shared Visited_Script" finding —
  does recruitment follow the same "each building family has its own"
  pattern, or is it actually unified?)
- [ ] What's the relationship between a NEW hero class and the EXISTING
  guild-recruitment UI (does a new class need a new recruit button/panel
  entry, or can it slot into an existing guild's roster)? This connects
  directly to the building-requirements doc's building-queue/panel
  research — cross-reference, don't duplicate.
- [ ] Cost/prerequisite gating for recruitment — where is this defined?

### 6. Known Gaps After This Pass
(Fill in as research proceeds — list every UNVERIFIED item explicitly,
don't let them disappear into the writeup.)
