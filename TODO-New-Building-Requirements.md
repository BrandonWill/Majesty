# Complete Requirements: Adding a New Building — TODO

**Goal:** Answer "how do I add a new building to Majesty Gold HD?"
completely — every requirement, every file touched, every gotcha — as a
standalone reference. Not scoped to GPL alone: sprite/CAM requirements
(dimensions, art style/isometric conventions, shadow/footprint), XML
schema, and UI/build-queue integration all belong here. Where the honest
answer is "this lives in CAM_MODDING_GUIDE.md under X" or "this is
UNVERIFIED, needs Ghidra," say so explicitly.

## Evidence Standard (same as GPL_MODDING_GUIDE.md's — non-negotiable)

Every requirement must cite the specific file/function/line (GPL), XML
attribute (with a real shipped example), or CAM section/field (with a
real example, ideally extracted via `cam_reader.py`/`sprite_extractor.py`
to confirm real dimensions/footprint) it was verified against. No claim
from assumed similarity to another building type. Mark anything
unconfirmed **UNVERIFIED**/**UNKNOWN** explicitly rather than guessing —
same standard that already caught two false-analogy mistakes in the GPL
deep dive (see that doc's "Retracted Claims").

**This is expected to be incomplete after the first pass.**

## Target Output

A `NEW_BUILDING_REQUIREMENTS.md` guide (or new section in an existing
guide) structured as a literal checklist: "to add a new building, you
need ALL of the following, in this order, or the game will [crash/
silently fail/not appear in the build menu]." Every item traces to a
citation here.

## Required Coverage Areas

### 1. Sprite/Art Requirements (cross-reference CAM_MODDING_GUIDE.md,
verify with real examples — extract real building sprites via
sprite_extractor.py to confirm dimensions/conventions, don't just restate
the existing IMAG/TILE docs)
- [x] Which animation/state sets are mandatory for a building
  specifically (buildings don't walk/attack like heroes — what states DO
  they need? Under-construction stages, idle, destroyed/collapsed,
  minimap icon — confirm against real building IMAG records, e.g.
  compare a single-level building like Inn against a multi-level one like
  Marketplace to see if level-tiers need separate full sprite sets or
  share one).

  **Method:** extracted real IMAG records for `ABF1` (Inn, single-level),
  `ABH1`/`ABH2`/`ABH3` (Marketplace tiers 1/2/3), `ABE1`/`ABE2`
  (Guardhouse tiers 1/2, a defensive building), and `ABJ1` (Palace, a
  unique) directly from `Data/maindata.cam` via `cam_reader.py`/
  `sprite_extractor.py`'s `parse_anim_set`/
  `parse_directional_frame_descriptor`, using an EXACT-CASE prefix match
  (not `sprite_extractor.py`'s built-in case-insensitive `find_record()`
  — carrying forward the exact same `AVN1`/`AVn1`-style collision risk
  found in the hero doc's pass: `ABJ1` Palace and `ABj1` Fountain are
  genuinely different records that collide under case-insensitive
  matching). Full script preserved in git history of
  `utility/test_decoder.py` for this pass.

  **Confirmed present on every one of the 7 building records checked,
  zero exceptions — treat as mandatory:** `Build` (setID 80), `Die`
  (setID 96), `Active` (setID 192), `Inactive` (setID 208), `Dead`
  (setID 224), `Crumble` (setID 240), `Hotspot` (setID 400), `Interface`
  (setID 1000). Buildings have **no `Stand` (setID 8) set at all** —
  confirmed absent on all 7 — buildings use `Active`/`Inactive` as their
  idle-state pair instead of a hero-style `Stand`. This is a genuine
  building-specific difference from the hero animation-set catalog (the
  hero doc's §1 found `Stand` mandatory for every hero), not an
  extraction gap — re-checked directly by dumping `Active`/`Inactive`
  frame descriptors and confirming real, non-degenerate hotspot/size/
  tile-index data on all 7.

  **Minimap (setID 300) is NOT a general building requirement —
  Palace-specific in this data.** Broadened the check to a full scan of
  every `AB*`/`BB*`-prefixed IMAG record in `maindata.cam` (91 records
  total): only `ABJ1`/`ABJ2`/`ABJ3` (all 3 Palace tiers) have a `Minimap`
  set; the other 88 — including Inn, all 3 Marketplace tiers, both
  Guardhouse tiers, Blacksmith, Fairgrounds, every Temple/Guild tier,
  every lair (`BB*`) — do **not**. This directly contradicts the item's
  own premise (grouping "minimap icon" with the other mandatory states)
  — it's real shipped data, not an assumption. **UNVERIFIED** why Palace
  specifically has one (Palace already gets a hardcoded flag icon on the
  minimap per common Majesty UI knowledge, but no GPL/XML source
  confirms this mechanism — not traced further here, out of this item's
  scope).

  **Construction stages: only ONE `Build` set exists per building record,
  not a progressive sequence of stage-specific sets.** All 7 records have
  exactly one `setID=80` (`Build`) entry — there is no `Build-2`/
  `Build-3`-style numbered variant the way `Die` has `setID_97`-
  `setID_103` (Die-2 through Die-8) sitting unused alongside it (see
  below). Whatever progressive-construction visual exists, if any, is
  not expressed as multiple discrete `Build`-family IMAG sets.

  **`Die`'s numbered variants (setID 97-103, i.e. "Die-2" through
  "Die-8") ARE present on buildings, unlike on heroes.** The hero doc's
  §1 confirmed setIDs 97-103 have **zero** `AV*`-prefixed (hero) hits
  anywhere in the CAM and are used "exclusively by buildings and monster
  lairs" — this building-side pass confirms that positively: `ABF1`
  Inn, `ABE1`/`ABE2` Guardhouse, and a broadened scan turned up
  417 total setID-97-to-103 hits across many `AB*` records (Ballista
  Tower, Blacksmith 1-3, Fairgrounds, Guardhouse 1-2, Inn, Library 1-2,
  Marketplace 1+, etc.) — confirming buildings really do have multiple
  numbered Die-family slots reserved, though **whether these numbered
  slots hold actually-different collapse-stage art (vs. just being
  reserved/empty placeholders) was NOT verified in this pass** — only
  their presence in the setID table was confirmed, not their frame
  content. Would need per-slot frame-descriptor dumps to confirm they
  hold real distinct pixel data — **UNVERIFIED** beyond presence.

  **Level-tiers (Marketplace1/2/3, Guardhouse1/2) get their OWN separate
  full sprite set each — they do NOT share one set of building art.**
  Confirmed directly: `ABH1`/`ABH2`/`ABH3` are three entirely separate
  IMAG records (6488/6472/6728 bytes respectively) with their own
  `Active`/`Build`/`Crumble`/etc. tile indices — e.g. Marketplace1's
  `Active` slot-2 tile_indices start `[0, 256, ...]` while Marketplace2's
  and Marketplace3's start `[256, 0, ...]` (different tile pointers, not
  byte-identical). `Crumble` tile indices are also tier-specific and
  non-overlapping (`1004` for tier1, `1018` for tier2, `1035` for
  tier3 — sequential-but-distinct TILE-section pointers, confirming
  distinct art assets per tier, not a shared/reused set). Guardhouse1 vs.
  Guardhouse2 shows the same pattern (separate `9904`/`9868`-byte
  records). This directly answers the item's own question: **each
  building level tier requires its own full sprite set**, not a shared
  one — consistent with `M_Buildings.xml`'s XML-level finding (see
  Section 2 research) that each tier is a wholly separate `Description`
  entry (`ABH1`/`ABH2`/`ABH3`), not a single entry with sub-fields.

  **Palace is the one outlier that lacks a `Build` set entirely.**
  `ABJ1` has no `setID=80` entry at all (confirmed: `Build: ABSENT` in
  direct extraction) — consistent with `GPL_MODDING_GUIDE.md` §2's
  finding that Palace has no `birthscript2`/construction-queue path the
  way ordinary buildings do (Palace-family buildings use `birthScript`
  only, not the `birthscript`/`birthscript2` two-stage chain). This is a
  genuine correlation between the GPL-side birth mechanism and the
  sprite-side asset requirement, not a coincidence — a building that
  skips the two-stage birth chain apparently doesn't need `Build`-set
  art either. **UNVERIFIED** whether this is enforced/required by the
  engine or just happens to be true of the one Palace example checked
  (no second birthScript-less building type was checked to confirm the
  pattern generalizes).
- [x] Isometric art conventions — footprint/tile-size, ground-plane
  alignment, shadow handling. Is there a documented or inferable pixel
  grid buildings must align to (the existing `PG01`-style terrain prefix
  table implies a tile system — does building art need to match specific
  tile-multiples)?

  **No fixed pixel-grid tile-multiple requirement for building sprite
  art — refuted directly.** Extracted the `Active` (idle) frame's
  width/height for all 7 sampled building records and checked against
  the 32px terrain-tile unit (`.kiro/steering/quest-and-mod-creation.md`
  / `.kiro/steering/majesty-modding.md`'s RGS "Resolution" note: "a tile
  is 32 pixels wide" — that finding is about the **map/RGS placement
  grid**, not building sprite art, and this pass confirms those are
  genuinely unrelated systems): Inn 69×101 (69%32=5, not a multiple),
  Marketplace 1/2/3 105×116 (105%32=9), Guardhouse 1/2 55×73 (55%32=23).
  None of the sampled buildings' pixel dimensions are multiples of 32,
  or of any other common value across the sample — **frame canvas size
  is per-building arbitrary pixel dimensions, the same "no fixed canvas
  size" finding the hero doc's §1 already made for heroes.** (Palace's
  reported `65392×191` for this same slot is `[width truncated: line too
  long]`-style corrupted/degenerate data — the same known-unreliable
  last-populated-direction-slot heuristic flagged in
  `sprite_extractor.py`'s own docstring, not a real building dimension —
  excluded from this comparison.) The 32px-tile system governs **where**
  a building's hotspot/origin is placed on the RGS map grid (a
  completely separate, already-documented mechanism — RGS `.q` file
  placement, not sprite art), not what pixel dimensions the art itself
  must be.

  **Ground-plane alignment convention: confirmed via the per-frame
  hotspot field, not a separate footprint field.** Every building's
  frame descriptor carries an `(x_off, y_off)` hotspot pair (Inn
  `(-65,-2)`, Marketplace `(-96,-9)`, Guardhouse `(-57,-2)`) — the same
  mechanism the hero doc's §1 already confirmed for heroes (per-
  direction-block hotspot at `+0x14`, `CAM_MODDING_GUIDE.md`'s IMAG
  binary appendix, byte offset confirmed there too). No separate
  "footprint" or "ground-plane" field exists in the IMAG binary format
  beyond this hotspot pair — placement/ground-plane alignment for
  buildings uses the identical mechanism heroes use, just with
  building-specific hotspot values tuned per sprite. **UNVERIFIED**
  whether the engine additionally derives a *collision footprint* (for
  overlap/placement checking) from this hotspot+size pair or from an
  entirely separate value elsewhere (e.g. `unittype.cam`'s DUNT binary
  fields) — this pass only confirmed the sprite-side hotspot mechanism,
  not the collision/placement-validation side, which belongs to Section
  2/4's XML and build-queue research, not this sprite-art item.

  **Shadow-index range (248-255) usage: confirmed real and used by
  buildings, but not universally in every extracted tile.** Decoded the
  actual TILE pixel data (not just metadata) for the first `Active`
  frame of each sampled building via `sprite_extractor.py`'s
  `decode_tile`: `ABF1` Inn, `ABH1` Marketplace1, and `ABE1`/`ABE2`
  Guardhouse tiles all contain real pixel values in the 248-250 range
  (a subset of the documented 248-255 shadow/blend range in
  `CAM_MODDING_GUIDE.md`'s TILE format appendix and
  `.kiro/steering/majesty-modding.md`) — confirming buildings genuinely
  use shadow-blend palette indices, not just heroes/units. Some sampled
  tiles (`ABH2`/`ABH3` Marketplace2/3's, `ABJ1` Palace's specific
  `Active` frame checked) show `shadow-range used=[]` — no shadow
  pixels in that SPECIFIC extracted frame, which is consistent with
  "shadow usage is per-sprite-artist-choice, not mandatory," not a
  contradiction — some individual frames legitimately have no shadow
  pixels (e.g. a frame where the shadow falls entirely off-canvas or the
  artist didn't paint one for that angle). **No building-specific shadow
  mechanism beyond the existing generic TILE-format convention was
  found** — cite `CAM_MODDING_GUIDE.md`'s "Pixel bytes — palette indices
  (0 = transparent, 248-255 = shadow/blend)" and
  `.kiro/steering/majesty-modding.md`'s identical note, don't re-derive;
  this pass only confirms buildings actually exercise that existing
  convention with real examples, it doesn't add a new rule.
- [x] Construction-stage visuals — does the game render partial-HP
  construction progressively (scaffolding-style sprites) or is
  construction invisible until `birthscript2`/completion (per
  GPL_MODDING_GUIDE.md §2 — cite it, don't re-derive, but confirm what
  the VISUAL side of "under construction" actually shows, which that
  section doesn't cover).

  **GPL side (not re-derived, cited):** `GPL_MODDING_GUIDE.md` §2
  ("Building Lifecycle: Birth, Construction, and Upgrades") already
  confirms `birthscript` fires at creation, the building queues on
  `palace's "buildings_waiting"` while under construction (via
  `basic_birth`), and only once HP reaches max does `birthscript2` fire
  (via `BuildingReachedMaxHP`, which explicitly checks
  `#ATTRIB_FirstStageBuilt`). That section does not address what the
  player actually SEES while a building sits in this
  under-construction/queued state.

  **Visual side — confirmed real, multi-frame "Build" art exists per
  building, refuting the "invisible until birthScript2" possibility.**
  `CAM_MODDING_GUIDE.md`'s setID table documents `Build | 80-83 |
  Construction animations` as a 4-variant range (same pattern as
  `Attack 16-19`). Direct extraction confirms multiple sampled buildings
  actually populate several of these numbered slots as GENUINELY
  SEPARATE frame descriptors (distinct `relOff` blob offsets — e.g.
  `ABH1` Marketplace1's `Build`/`setID_81`/`setID_82` live at
  `relOff=0x25C`/`0x2C8`/`0x334` respectively, not aliased to the same
  descriptor): Inn has 2 populated Build-family setIDs (80,81),
  Marketplace1 and Guardhouse1 each have 3 (80,81,82), Marketplace2/3
  and Guardhouse2 have fewer (2 and 1 respectively) — **the count of
  populated Build-stage slots varies per building/tier, it is not a
  fixed "always exactly N stages" rule.** This directly confirms
  construction is NOT simply invisible until completion — there is
  dedicated, multi-slot "under construction" art infrastructure in the
  IMAG format that a real building actually uses.

  **However, the numbered Build variants checked are pixel-IDENTICAL in
  their dimensions/hotspot/first-tile-index within a given building —
  NOT visually distinct scaffolding progression frames, at least for the
  slot-2/first-tile-index data checked.** For every building sampled,
  `setID=80`, `81`, and `82` (where present) report the exact same
  `width`/`height`/hotspot and the exact same first 6 `tile_indices`
  (e.g. Marketplace1: all three report `105x116`, hotspot `(-96,-9)`,
  tile_indices starting `[256, 0, 0, 0, 0, 0]`). This means either (a)
  these 4 "Build" variants are NOT literally "construction stage 1 of
  4"/"stage 2 of 4" progressive scaffolding frames — they may instead
  be alternate-direction or alternate-context Build sets whose slot-2
  data happens to coincide, or (b) the actual progression lives in
  frames/tile_indices beyond the first 6 checked, not in a different
  setID at all. **This pass could NOT distinguish between those two
  possibilities** — only the first 6 tile indices of each set's slot 2
  were compared, not every frame in the set, and no in-game visual
  confirmation of what these render as was done (would need to render
  each `Build`-family setID's actual TILE pixel data to PNG and visually
  compare, or find a decisive GPL/XML reference to what selects between
  Build/Build-2/Build-3/Build-4 at different construction-progress
  percentages — no such selection logic was found in
  `GPL_MODDING_GUIDE.md` §2 or in `Building_Births.gpl`'s
  `basic_birth`/`magical_birth`/`BuildingReachedMaxHP` functions, which
  only reference `birthscript`/`birthscript2` function pointers, never
  an ImageSet or ActionXML name). **Mark explicitly UNVERIFIED:**
  whether/how the engine selects among the 2-3 populated Build-family
  setIDs based on construction progress (%HP built) — no GPL, XML, or
  `.dat` source found that ties construction percentage to a specific
  ImageSet selection; this may be exe-side logic invisible to GPL/XML,
  same class of gap as the hero doc's "missing animation frame at
  runtime" UNVERIFIED item.
- [x] Destruction/collapse visuals — `Building_Collapse` action was
  noted in earlier research (GPL_MODDING_GUIDE.md §8's cProc mention) —
  is a collapse animation mandatory or optional for a new building?

  **Correction to this item's own premise:** the action's real XML name
  is `Become_Rubble` (ID `A009`), not `Building_Collapse` —
  `Building_Collapse` is actually the **sound** definition's name
  (`M_Sounds.xml`, `<Description type="Sound" ... ID="BC01"
  Name="Building_Collapse">`), referenced FROM the `Become_Rubble`
  action via `<Sound value="Building_Collapse"/>`. Confirmed directly:
  `M_Actions.xml`'s `Become_Rubble` (`A009`) entry is `<ImageSet
  value="Crumble"/> <Sound value="Building_Collapse"/> <SoundPhase
  begin="Begin"/> <Script type="0" cProc="8192"/>` — this is genuinely
  the same numeric `cProc="8192"` GPL_MODDING_GUIDE.md §8 already flags
  as **UNVERIFIED** for the (unrelated) `Basic_death` hero action — the
  two different actions share the same numeric engine callback code,
  which §8 doesn't resolve and this pass doesn't either (would need
  Ghidra).

  **Mandatory, not optional — confirmed unconditional call site.**
  `Building_Deaths.gpl`'s `building_death(agent thisagent)` — the
  single shared death function nearly every building's `IGdeathscript`
  ultimately routes through (confirmed via grep across
  `Building_Data.dat`: dozens of entries from `Blacksmith`/`Fairgrounds`/
  `Inn`/`Trading_Post`/`Brothel`/`General_Housing` etc. point
  `IGdeathscript` straight at `building_death`, and even the
  building-family-specific death functions —
  `statue_death`/`gardens_death`/`guild_destroyed_common`/
  `GuardHouse_Death`/`Hidden_Sword_Death`/`Hidden_Ring_Death`/
  `Hidden_Chalice_Death`/`crown_site_Death`/`slave_pits_death` (via
  `lair_death`) — all end by calling `$building_death(thisagent)`
  themselves) — **unconditionally calls `$performaction(thisagent,
  "Become_Rubble", thisagent)`** with no guard/flag check around it
  (read the full function body: `thisagent's "type" = "Dead"` →
  `$release_occupants` → `$Clean_Palace_Construction_Lists` →
  `$performaction(thisagent,"Become_Rubble",thisagent)` →
  `$deleteagent(thisagent)`). `Palace_Death` (the one building-type
  death function that does NOT call `building_death`, since Palace has
  its own bespoke death handler) **still calls the identical
  `$performaction(thisagent,"Become_Rubble",thisagent)` line directly**
  — confirmed by reading `Palace_Death` in full. Every death path
  checked in this pass triggers `Become_Rubble` — there is no
  building-death code path found that skips it. This makes the
  `Crumble` (setID 240) IMAGE set **a hard requirement for any new
  building**, not optional — every building's `IGdeathscript`, however
  it's implemented, converges on `$performaction(...,"Become_Rubble",...)`
  which reads the `Crumble` ImageSet per `Become_Rubble`'s own XML
  (confirmed present on all 7 sampled building records in this pass's
  §1 item — zero exceptions found there either, consistent with this
  finding). **UNVERIFIED:** whether omitting a `Crumble` set on a
  genuinely new building would crash `$performaction` outright or just
  render nothing — no source describes the fallback, same class of gap
  as the missing-animation-frame question already flagged in the hero
  doc; not tested in-game here.
- [x] Minimap icon requirements.

  **Not a general building requirement — refuted the item's implicit
  premise, cross-referencing this pass's §1 first item's finding rather
  than re-deriving it.** Already established above: broadening the scan
  to all 91 `AB*`/`BB*`-prefixed IMAG records in `maindata.cam` found
  `Minimap` (setID 300) present ONLY on `ABJ1`/`ABJ2`/`ABJ3` (all 3
  Palace tiers) — the other 88 building/lair records, including every
  shop/guild/temple/defensive building and every monster lair checked,
  have no `Minimap` set at all. **A new ordinary building does NOT need
  a dedicated `Minimap` IMAGE set** based on this data — it appears to
  be Palace-specific, not a universal building requirement the way it
  was for heroes (the hero doc's §1 found `Minimap` mandatory, zero
  exceptions, across all 15 heroes checked — a genuine building-vs-hero
  asymmetry, not an oversight in either pass).

  **UNVERIFIED:** what actually represents an ordinary building on the
  minimap if not a dedicated `Minimap` IMAGE set — options not
  distinguished by this pass: (a) buildings render on the minimap as a
  generic colored dot/rectangle computed by the engine from the
  building's player-color/team, with no per-building sprite at all, or
  (b) some other already-checked ImageSet (e.g. `Active`) doubles as
  the minimap representation via a downscale, or (c) buildings simply
  don't appear individually on the minimap the way heroes/monsters do
  (only Palace, being the single most important structure per player,
  gets a distinct icon). No GPL/XML source read in this pass describes
  minimap rendering source data for buildings specifically — would need
  either a Ghidra trace of the minimap-rendering code path or an
  in-game screenshot comparison of an ordinary building vs. Palace on
  the minimap to resolve which of (a)/(b)/(c) is correct. Do not assume
  "probably a generic dot" — mark explicitly unknown, same standard the
  hero doc used for its own missing-animation-frame gap.
- [x] Palette constraints — same question as the hero doc: existing-only
  vs. quest-scoped-new-palette-allowed.

  **Not re-derived — cited from existing docs, same as the hero doc's
  §1 handled this identical question.** `.kiro/steering/
  majesty-modding.md`'s "Critical Constraints" section and
  `CAM_MODDING_GUIDE.md`'s TILE-format appendix both confirm: **existing
  SPLT palette entries are READ-ONLY** (modifying them crashes the
  game — "No palette modifications in SPLT entries (crashes the game)"
  is explicitly listed as a pre-flight validation check in the steering
  doc), but a quest/mod's own CAM file can ship **brand-new** SPLT
  entries of its own — confirmed by `CAM_MODDING_GUIDE.md`'s "IMAG
  Writing Notes for Mod CAMs" section citing the real shipped
  `MDL1_maindata.cam` example (Krolm quest CAM), which per that same
  guide's file-inventory table ships "5 IMAG + 638 TILE + **12 SPLT**"
  entries of its own. This mechanism is entity-agnostic — it's a
  property of the CAM/SPLT container format itself, not something that
  varies between hero sprites and building sprites. **A new building
  can therefore either reuse an existing base-game palette (quantize new
  building art to match) or ship its own new SPLT palette entry inside
  its own quest/mod `maindata.cam`, exactly like the hero doc already
  confirmed for new heroes** — no building-specific palette restriction
  beyond the universal read-only-existing-entries rule was found in this
  pass, and none was expected to exist given the format is shared
  IMAG/TILE/SPLT infrastructure across all entity types (confirmed
  directly in this pass's own extraction: building TILE entries decode
  via the identical `decode_tile`/`palette_id`-lookup mechanism as hero
  tiles, with real building tiles observed using `palette_id` values
  like `0`, `37`, and `57` — ordinary palette-table indices, nothing
  building-specific about how they're referenced).

### 2. Unit XML Definition Requirements (M_Buildings.xml / MX_Buildings.xml)

**Method:** read the full `<Description type="Unit" subType="Building"
...>` blocks for `Marketplace1` (ID `ABH1`, shop-type), `Rangers_Guild`
(ID `ABW1`, guild-type) and `Warriors_Guild` (ID `ABV1`, second guild for
cross-check), `Guardhouse1` (ID `ABE1`, defensive-type), and `Palace1`
(ID `ABJ1`, unique) side by side directly from `SDK/OriginalQuests/Data/
M_Buildings.xml`, plus their Level-2/3 tier siblings where present
(`ABH2`/`ABH3`, `ABE2`, `ABJ2`/`ABJ3`) and the bare-minimum
`placeholder_building` entry (`ABA0`) as an extra reference point.

- [x] Full required-field catalog for `type="Unit" subType="Building"`
  with `CanUse value="HumanPlayer"` — read multiple real building
  definitions side by side (a shop-type, a guild-type, a defensive-type
  like Guardhouse, and a unique like Palace) to determine always-present
  vs. sometimes-omitted fields — don't generalize from one example.

  **`<Engine>` block — present on every one of the 5 sampled buildings
  (Marketplace1, Rangers_Guild, Warriors_Guild, Guardhouse1, Palace1),
  zero exceptions — treat as mandatory:** `CanUse value="HumanPlayer"`,
  `Menu value="N"`, `ImageIDBase`, `DefaultSound`. **Sometimes omitted —
  real variation, not universal:** `Info value="BlockGround"`/
  `Info value="BlockFlying"` are present on all 5 sampled (and on nearly
  every other `AB*` building in the file), but `Rangers_Guild` uniquely
  **lacks** `Info value="ModifyTerrainTextureOnPlacement"` — every other
  sampled building (Marketplace1, Warriors_Guild, Guardhouse1, Palace1)
  has it, confirming this Info flag is genuinely per-building-optional,
  not mandatory. `Info value="ModifyTerrainHeightOnPlacement"` appears
  **only on Palace1** among the 5 sampled — confirmed elsewhere in the
  file to correlate with visually large/terrain-reshaping structures
  (Fairgrounds, Dark_Castle, Sewer lair also have it), not a general
  building requirement.

  **`<Game>` block — present on every one of the 5 sampled buildings,
  zero exceptions — treat as mandatory:** `DialogID`, `MaxHP`,
  `SightRange`, `Flags value="HasHPBar"`, `HelpID`. **Sometimes omitted —
  confirmed real, not an extraction gap:** `Cost`/`Multiplier`/
  `IncomeType`/`IncomeAmount` are present on Marketplace1
  (`Cost=1500`, `Multiplier=1.3`, `IncomeType=2`, `IncomeAmount=40`),
  Rangers_Guild/Warriors_Guild (`Cost`, `Multiplier=2.0`, `IncomeType=2`,
  `IncomeAmount=40`), and Guardhouse1 (`Cost=600`, `Multiplier=1.25`,
  `IncomeType=3`, but **no `IncomeAmount` at all** — `IncomeType=3`
  buildings, i.e. non-revenue "service" buildings, can validly omit
  `IncomeAmount`) — but **all four of `Cost`/`Multiplier`/`IncomeType`/
  `IncomeAmount` are completely absent on Palace1**, which instead
  relies on `Flags value="NotBuildable"` (Palace can't be purchased
  through the normal build menu at all, consistent with it being
  auto-placed at map start, not player-constructed). `UpgradeTo` is
  present on Marketplace1/Guardhouse1/Palace1 (all have Level-2/3 tier
  siblings) but **absent on Rangers_Guild/Warriors_Guild** in this
  data — those two guilds have no further tiers, confirming `UpgradeTo`
  is tier-dependent, not universal. `MaxGuildMembers` and `Flags
  value="IsGuild"` are present **only** on Rangers_Guild/Warriors_Guild
  among the 5 sampled — confirmed guild-specific by cross-referencing
  against every other `Flags value="IsGuild"` building in the file
  (Dwarven_Settlement, Elven_Bungalow, Gnome_Hovel, Rogues_Guild1,
  Wizards_Guild1 all pair `IsGuild` with `MaxGuildMembers`, zero
  exceptions found). `Produces` (with nested `<Unit ID="..."/>` entries)
  is present on Rangers_Guild/Warriors_Guild/Guardhouse1/Palace1 (all
  spawn units — heroes for guilds, `City_Guard` for Guardhouse,
  `Palace_Guard`/`Tax_Collector`/`Peasant` for Palace) but **absent on
  Marketplace1**, which produces nothing — `Produces` is
  behavior-dependent, not a universal field. `Flags value="NumberedName"`
  is present on Marketplace1/Guardhouse1 (buildings the player can build
  multiple of, needing "#2"/"#3" disambiguation in the UI) but absent on
  Rangers_Guild/Warriors_Guild/Palace1 in this sample. `Flags
  value="HasGoldToolTip"` is present on Marketplace1/Rangers_Guild/
  Warriors_Guild/Palace1 but **absent on Guardhouse1** — confirmed real
  (Guardhouse doesn't show a gold-income tooltip, consistent with its
  `IncomeType=3`/no-`IncomeAmount` non-revenue role).

  **Level-tiers are separate, complete `Description` entries, not one
  entry with sub-fields — confirmed directly (also answers item 3
  below):** `ABH1`/`ABH2`/`ABH3` (Marketplace1/2/3) and `ABE1`/`ABE2`
  (Guardhouse1/2) and `ABJ1`/`ABJ2`/`ABJ3` (Palace1/2/3) are each their
  own full `<Description>` block with their own `ID`/`Name`/full
  `<Engine>`/`<Game>` content — tier 2/3 entries add `UpgradeFrom`
  (pointing back at the previous tier's `Name`, e.g. Marketplace2 has
  `<UpgradeFrom value="Marketplace1"/>`) alongside `UpgradeTo` where a
  further tier exists, and add `Flags value="NotBuildable"` (tier-2/3
  buildings can't be built directly from scratch, only reached via
  upgrade — confirmed on `ABE2`/`ABH2`/`ABH3`/`ABJ2`/`ABJ3`, all of
  which have it, vs. their tier-1 counterparts which don't).

  **Every field-presence/absence claim above was cross-checked against
  at least one additional building beyond the core 5** (Dwarven_Settlement,
  Elven_Bungalow, Gnome_Hovel, Rogues_Guild1, Wizards_Guild1 for the
  `IsGuild`/`MaxGuildMembers` pairing; Fairgrounds/Dark_Castle/BBN1 Sewer
  for the `ModifyTerrainHeightOnPlacement` correlation) rather than
  asserted from the 5-building sample alone.
- [x] `Menu value="N"` for buildings — confirm what values are valid/what
  they control (existing docs note "2=building" generically — is there
  sub-categorization by building menu value that affects build-menu
  placement?).

  **Confirmed real sub-categorization by direct cross-reference of every
  `Menu value=` occurrence in `M_Buildings.xml` against the entity it's
  attached to — buildings use `Menu` values 0/1/2/3, a genuinely
  different value range from the hero doc's Character-subtype findings
  (Menu 4/5/6/7/12/13), confirming `Menu` is interpreted per-`subType`,
  not one global enum shared across `Character` and `Building` entities:**
  `Menu="0"` = Temple-family buildings, `CanUse="HumanPlayer"`, directly
  buildable (all 7 temples — Agrela, Dauros, Fervus, Helia/Solarus,
  Krolm, Krypta, Lunord — confirmed zero exceptions, and their Level-2/3
  tiers keep `Menu="0"` too). `Menu="1"` = guild/recruitment-family
  buildings — every building carrying `Flags value="IsGuild"` uses
  `Menu="1"` with zero exceptions found (`Warriors_Guild`, `Rangers_Guild`,
  `Rogues_Guild1`, `Wizards_Guild1`, `Dwarven_Settlement`,
  `Elven_Bungalow`, `Gnome_Hovel`) — this is the value that actually
  determines "shows up as a guild/recruitment option," not `IsGuild`
  alone (both are always present together on every guild checked, so
  which one the engine actually keys off of for menu placement is
  **UNVERIFIED** without an exe trace — only the correlation is
  confirmed). `Menu="2"` = the general/default bucket — the large
  majority of ordinary economic/defensive/decorative buildings
  (Marketplace, Guardhouse, Palace, Blacksmith, Fairgrounds, Inn,
  Library, Ballista_Tower, Trading_Post, the placeholder `ABA0` entry,
  etc.) **and most Monster-`CanUse` lairs** (`Animal_Den`, `Dark_Castle`,
  `Goblin_Camp`, `Goblin_Hovel`, `Dragon_Lair`, `Dragon_Tomb`, and
  others) share this same value — `Menu="2"` is NOT exclusively a
  "human player building menu" signal, it's shared with monster lairs
  too, so `Menu` value alone doesn't distinguish player-buildable from
  monster-only; that distinction is carried by `CanUse` instead.
  `Menu="3"` = a small set of `CanUse="HumanPlayer"` buildings that are
  **never player-constructed from the build menu at all** — `Brothel`,
  `Gambling_Hall`, `General_Housing`, and `Sewer` (`BBN1`, despite the
  `BB`-style ID prefix normally associated with monster content, this
  entry is `CanUse="HumanPlayer"`) — all four have `Flags
  value="NotBuildable"` and no `Cost` field, confirming `Menu="3"` marks
  buildings that appear/spawn through other game mechanics (quest
  scripting, city growth, etc.) rather than the construction menu. Two
  `Menu="2"` monster lairs (`Graveyard` `BBJ1`, and the same `Sewer`-
  family entry checked above) were the only Monster-`CanUse` exceptions
  found still using `Menu="3"` rather than `2` — **not fully resolved
  why these two specifically deviate from the otherwise-consistent
  Monster→Menu=2 pattern**, marking this specific sub-case
  **UNVERIFIED** beyond the raw data observed. **For a new
  player-buildable building meant to appear in the normal construction
  menu, `Menu="2"` (ordinary) or `Menu="0"`/`Menu="1"` (if it's meant to
  be categorized as a temple or guild specifically) are the confirmed
  working values** — no test was done to see whether an ordinary
  economic building set to `Menu="0"` or `"1"` would still appear
  correctly categorized or would break/misfile (same caveat as the hero
  doc's identical open question for Character Menu values) —
  **UNVERIFIED** whether wrong-but-nonzero Menu values simply misfile a
  building in the wrong UI category or crash/hide it outright.
- [x] Cost/`costMultiplier`/`Level` fields — how multi-level buildings are
  declared as separate `Description` entries vs. one entry with tiers —
  confirm from real XML, this was asserted generically in earlier
  `.dat`-focused research but not confirmed at the XML layer.

  **Confirmed at the XML layer (this directly duplicates/reinforces item
  1's "Level-tiers are separate, complete `Description` entries" finding
  above — cited from there, not re-derived a second time): each tier is
  its own full `<Description>` block with its own `ID` (`ABH1`/`ABH2`/
  `ABH3` for Marketplace, `ABE1`/`ABE2` for Guardhouse, `ABJ1`/`ABJ2`/
  `ABJ3` for Palace) — there is no single entry with a `Level`
  sub-element or repeating tier list at the XML layer.** `Cost` (a plain
  integer, e.g. Marketplace1 `Cost="1500"`, Marketplace2 `Cost="1000"`,
  Marketplace3 — read directly, `Cost="1000"` also, i.e. NOT
  monotonically increasing per tier in this data, contradicting a naive
  "upgrade always costs more" assumption) is present per-tier, each
  tier's own value, not computed from a multiplier.

  **`costMultiplier`/`Level` as literal XML attribute names do NOT
  exist anywhere in `M_Buildings.xml` — this item's own premise is
  refuted by a direct grep (zero matches for `Level=`/`Tier=` in the
  entire file).** What the XML actually calls `Multiplier` (e.g.
  Marketplace1 `<Multiplier value="1.3"/>`) is a **different,
  unrelated field** — confirmed by reading `IceSpell_Quest/MyAI/GPL/
  Game/mx_prototype.gpl`'s `building()` prototype comment: `float
  costMultiplier; //cost multiplier for each building` — this is a
  fan-made AI script's own custom field on a fan-extended prototype
  (`mx_prototype.gpl`, not the base game's `SDK/OriginalQuests/GPL/
  prototype.gpl`), used by that AI's own `getBuildingCostMultiplier()`
  helper (in `custom_rules.gpl`) to scale a bot's calculated build cost
  — **this `costMultiplier` is NOT the same as the XML's `<Multiplier>`
  field and NOT part of base-game building definition at all** — it's
  mod-specific AI tooling. The XML's real `Multiplier` field's actual
  engine consumer/purpose was **not traced in this pass** — no GPL
  function reads it directly (not grepped exhaustively here, out of
  this item's narrow scope) — **UNVERIFIED** what `Multiplier` value
  controls at runtime beyond its presence correlating with `IncomeType`/
  `IncomeAmount`-bearing (revenue) buildings in the sample.

  **The real per-tier `Level` field lives in `Building_Data.dat` (the
  GPL-side `.dat`, not the XML), confirmed directly:**
  `SDK/OriginalQuests/GPL/Building_Data.dat`'s `[Palace1]`/`[Palace2]`
  blocks each set `(Level 1)`/`(Level 2)` inside their `{Palace ...}`
  prototype body — this is the actual numeric tier tracker the engine/
  GPL code uses, and it lives entirely on the `.dat` side (Section 3 of
  this doc's scope), matching each `.dat` block name (`Palace1`,
  `Palace2`) to the corresponding XML `Description` `Name`
  (`Palace1`/`Palace2`) by string, not by a shared numeric field. **This
  means a new multi-tier building needs BOTH a separate XML
  `Description` entry per tier (for Cost/stats/sprite-set wiring) AND a
  separate `.dat` block per tier with its own `Level` integer (for GPL-
  side tier tracking)** — the two layers are parallel, name-matched
  structures, neither one alone is sufficient, and neither one contains
  a construct that expresses "tiers" as a single multi-valued field.
- [x] `DialogID` — full explanation of what this field does and is
  required for (connects to the already-Ghidra-confirmed
  "building-to-panel mapping is hardcoded per building class" finding in
  `SMNUResearch/findings/exe_disassembly_results.md` — cite it, this is
  a DIRECT, confirmed blocker: a genuinely NEW building type cannot have
  a NEW research/service panel without an exe patch, per that finding.
  Make sure this shows up prominently as a hard requirement/limitation
  in the final checklist, not buried).

  **`DialogID` is a plain required XML string field, present on every
  sampled building (`Marketplace1/2/3`→`AP31`, `Guardhouse1/2`→`AP17`,
  `Rangers_Guild`→`AP47`, `Warriors_Guild`→`AP52`, `Palace1/2/3`→`AP39`),
  confirmed the value is IDENTICAL across all tiers of a multi-level
  building (Marketplace's 3 tiers all share `AP31`, Guardhouse's 2 tiers
  both share `AP17`, Palace's 3 tiers all share `AP39`)** — a tier
  upgrade changes `Cost`/`MaxHP`/etc. but does NOT change which panel
  the building opens; all tiers of one building family route to the
  same `DialogID`, confirmed directly from the XML, not assumed.

  **>>> HARD LIMITATION — PROMINENT, NOT BURIED <<<**

  **`DialogID` is the 4-character key the exe's building-panel class
  factory uses to select a hardcoded, compiled-in panel handler — this
  mapping is Ghidra-confirmed (real disassembly, not inference) and is
  NOT data-driven, NOT read from any XML/`.dat`/CAM file.** Quoting
  `SMNUResearch/findings/exe_disassembly_results.md` directly: "The
  mapping is HARDCODED in per-building-class virtual functions (vtable
  methods). Each building type has its own C++ class with a vtable...
  Each building's override function has the target panel name **burned
  in as a 4-byte constant**." The same file's "Implications for
  Modding" section states outright: "**BAD NEWS: Cannot add new
  building-to-panel mappings** — The panel name to open is a compiled
  constant in the exe. There is no data file to edit," and its
  dedicated "CANNOT DO" section confirms: "A completely new building
  type (new DialogID) that wants a Research button opening a custom
  panel **would need the exe patched to add a new vtable handler**."
  The factory function itself (`FUN_0051b150`, confirmed by address) is
  documented taking the 4-char `DialogID` packed as a `u32` and mapping
  it via a hardcoded table to one of a fixed set of constructor
  functions (e.g. `0x3230584d`/"MX02" → `FUN_004bc430` for Magic Bazaar,
  `0x31335041`/"AP31" → `FUN_004a56d0` for Marketplace) — the complete
  table of confirmed `DialogID`→constructor mappings is finite and
  enumerated in that file's "Verified Building Class Constructors"
  table; **a `DialogID` string not already in that compiled table falls
  through to the generic handler (`FUN_00497690`)**, which the same
  source confirms "does NOT open a new panel — it just configures the
  current panel's research button state," i.e. a genuinely new
  `DialogID` value on a new building gets **no dedicated
  research/service sub-panel at all**, only whatever the generic
  fallback renders inline.

  **Practical consequence for a new building type, stated plainly (per
  this item's own instruction to make this prominent, not buried): if a
  new building needs a Research/Purchase-style sub-panel the way
  Marketplace/Magic Bazaar/Library/Palace/Fairgrounds/Sorcerer's Abode
  do, that panel cannot be wired to a brand-new `DialogID` through XML/
  GPL/CAM alone — it requires an exe patch adding a new vtable handler
  to the factory, no other path exists per the current findings.** A
  new building CAN still validly set a `DialogID` value and function
  correctly for every purpose that doesn't need a dedicated sub-panel
  (HP bar, minimap, build-menu entry, GPL scripting, generic inline
  research-button state via the fallback handler) — the limitation is
  narrowly about **opening a genuinely new, distinct panel**, not about
  `DialogID` being unusable outright. Two documented workarounds exist,
  neither of which lifts this limitation, both cited directly from the
  same finding file rather than re-derived: (1) reuse an EXISTING
  building's already-mapped `DialogID` (inherits that building's panel,
  not a new one) — **UNVERIFIED** whether two unrelated building types
  sharing one `DialogID` causes any other cross-talk beyond the panel
  they open, not tested; (2) for a building that DOES already have a
  working hardcoded research panel, add secondary/paginated content by
  editing that panel's own SMNU/textdata.cam entries and navigating by
  panel INDEX (not `DialogID`) to an added "page 2" — this only extends
  an existing mapped panel, it does not create a new `DialogID`
  mapping. See `TODO-Ghidra.md` for the tracked follow-up on whether
  the factory table itself could be extended via binary patching.
- [x] Footprint/collision size — where is a building's ground footprint
  actually defined (XML field, derived from sprite dimensions, or
  something else)?

  **No dedicated footprint/collision-size field exists in
  `M_Buildings.xml` — confirmed by direct grep across the entire file
  for `Footprint`/`Radius`/`Size value`/`Width`/`Height value`/
  `Collision`: zero matches.** The only placement-relevant XML fields
  present are the boolean `Info` flags already covered in item 1
  (`BlockGround`, `BlockFlying`, `ModifyTerrainTextureOnPlacement`,
  `ModifyTerrainHeightOnPlacement`, `DontBlock` on the one placeholder
  entry) — these are pass/fail terrain-interaction flags, not
  dimensional footprint values (a flag can't express "this building is
  3 tiles by 2 tiles").

  **`CAM_MODDING_GUIDE.md`'s own documented DUNT key-field list (the
  binary-compiled form of `M_Buildings.xml`) also has no size/footprint
  field** — its "Key fields in a DUNT entry" list is `ImageIDBase`,
  `DefaultSound`, `MaxHP`/`Attack`/`Speed`/stats, `AllowedSpells`,
  `GPLFunction` — cited directly, not re-derived, and confirms the gap
  isn't just an XML-layer omission that reappears compiled — the
  compiled binary format's documented fields don't carry one either
  (though the DUNT binary format itself has NOT been byte-by-byte
  reverse engineered field-for-field the way IMAG/TILE have — this
  pass did not attempt that, so an undocumented binary-only field
  cannot be fully ruled out, only the currently-documented field list).

  **The `.kiro/steering/majesty-modding.md` RGS/`.q`-file research
  (already-completed prior work, cited not re-derived) states buildings
  have engine-enforced minimum spacing at map-generation time:** "The
  placement code will not allow objects to overlap, so a minimum
  spacing will be enforced if the placement would cause an overlap" —
  but that note's own wording only says spacing is enforced, it does
  NOT identify what data source the engine reads to know each
  building's size for that check. This pass did **not** find any
  further citation (GPL, XML, or `.dat`) resolving what that source
  is — the `Overlap_Prevention` term used in this project's own
  `quest-map-generator` spec docs is a paraphrase of the same
  RGSEditor-manual behavior description, not an independently
  Ghidra-confirmed or byte-level-confirmed mechanism.

  **Most likely candidate, but explicitly NOT confirmed in this pass:**
  Section 1's already-established finding that a building's only
  spatial data at the sprite layer is the per-frame `(x_off, y_off)`
  hotspot plus the frame's pixel width/height (both from the IMAG/TILE
  data, `CAM_MODDING_GUIDE.md`'s binary appendix) — it would be
  consistent for the engine to derive a placement/collision footprint
  from that same sprite bounding box at runtime rather than from any
  XML/`.dat` field, since no such field exists in either layer. **This
  is a plausible inference, not a confirmed mechanism — mark
  explicitly UNVERIFIED.** Resolving it definitively would require
  either a Ghidra trace of the building-placement/overlap-validation
  code path (the same class of engine-side gap as the "generic handler"
  vs. hardcoded-panel research already done for `DialogID` above) or an
  in-game/RGS-generation empirical test (e.g. two buildings with
  deliberately different sprite pixel dimensions but otherwise-identical
  XML, checking whether the game enforces different minimum spacing
  between them) — neither was performed here. Do not assume "derived
  from sprite dimensions" is settled fact; it is the only data that
  exists to derive from, which is suggestive but not proof the engine
  actually uses it this way.

### 3. `.dat` / Building_Data.dat Requirements (cross-reference
GPL_MODDING_GUIDE.md §2/§3/§5/§6 extensively — this section overlaps the
most with existing research, the job here is COMPLETING the picture for
"new building" specifically, not re-deriving what's already found)
- [x] Full required-field catalog for a NEW building's `.dat` block —
  cite GPL_MODDING_GUIDE.md's existing per-field findings
  (birthscript/birthScript2, upgradescript, Visited_Script,
  RevenueScript, Guard_Function, Lived_In_Script) but explicitly answer:
  which of these are MANDATORY for ANY new building vs. only relevant if
  the building needs that specific behavior? (e.g. RevenueScript is
  clearly optional — GuardHouse/Tower declare it but never set it, per
  existing research — but is there anything that's unconditionally
  required for EVERY building regardless of type?)

  **Method:** read `Building_Data.dat`/`mx_Building_Data.dat` in full
  (both base and expansion, every entry — not a sample) side by side with
  `prototype.gpl`/`mx_prototype.gpl`'s `building`/`Guild`/`GuardHouse`/
  `Palace`/`Library`/`Fairgrounds`/`Tower`/`Dwarven_Settlement`/
  `Lair`/`Outpost` prototype field declarations, plus the official SDK
  example mod `SDK/Adjust Guardhouse Mod/GPL/Guardhouse.dat` (a real,
  shipped, minimal single-building `.dat` override) as a cross-check for
  "what's the smallest real block that works."

  **`type`/`subtype`/`title` — present on every single entry checked in
  both `.dat` files, zero exceptions (confirmed by reading the full file,
  not a sample):** every one of the ~90 base-game entries and ~40
  expansion-only entries in `Building_Data.dat`/`mx_Building_Data.dat`
  opens with exactly these three fields, in this order, immediately
  inside the `{PrototypeName ...}` block. This matches the prototype
  declarations directly — `string type;`/`string subtype;`/`string
  title;` are the first three fields declared on literally every
  building-family prototype in `prototype.gpl`
  (`building`/`Library`/`Fairgrounds`/`Guild`/`Dwarven_Settlement`/
  `Palace`/`GuardHouse`/`Tower`/`Lair`), and every non-building prototype
  too (`hero`/`monster`/`Special_Item`/`Resource`/`RewardFlag`/
  `map_goodie`/`Spell`) — this is not a building-specific convention,
  it's the one universal pattern across the entire `.dat`/prototype
  system. **Treat `type`/`subtype`/`title` as unconditionally mandatory
  for any new building entry**, independent of which prototype block it
  uses.

  **`birthScript` (or a birthScript-equivalent) is the only
  *scripting*-side field that's unconditionally required for a new
  building to do anything at all — confirmed by tracing the engine call
  site, not by pattern-matching the `.dat`.** `LowLevel.gpl`'s
  `NewUnitInit` (the function GPL_MODDING_GUIDE.md's §1/§2 already
  identifies as engine-invoked on every new agent) does `if
  ($ValidFunction(NewAgent's "BirthScript")) $RunThread(newAgent's
  "birthScript", 1, newAgent);` — it's a conditional, not an assert, so a
  building **can** legally have no `birthScript` at all (the engine just
  silently skips the RunThread call, per `$ValidFunction`'s guard) and
  the game will not crash — but with no `birthScript`, a building has no
  self-registration path at all: `basic_birth`/`magical_birth`/
  `auto_Birth`/`built_or_auto_birth`/every other `birthScript` target
  found in the `.dat` are what wire a building into
  `buildings_waiting`/`RevenueScript` threads/its own `ActiveScript`
  etc. (`GPL_MODDING_GUIDE.md` §2). **Confirmed real exception in the
  shipped data:** `Palace3`, `Rogues_Guild2`... — actually every
  level-2/3 tier entry across every building family skips `birthScript`
  and jumps straight to setting `birthScript` to the *completion*
  function directly (e.g. `Marketplace2`/`3` set `(birthScript
  Building_Birth)` with no `basic_birth` step at all) — meaning
  `birthScript` itself is present on 100% of the ~130 total `.dat`
  entries checked (base + expansion), it is just pointed at a different
  target depending on whether the building starts under construction —
  **`birthScript` presence is universal, its target function is not.**
  `map_goodie`-typed decorative placeholder entries at the end of
  `Building_Data.dat` (`Stone_tablet`, `obelisk`, `sign_fancy_iron`,
  etc.) are the one genuine exception — those have only `type`/
  `subtype`/`title`, no `birthScript` at all — but those aren't
  buildings in the gameplay sense (no `{Building}`-family prototype, no
  HP/construction/menu presence), so they don't count against "every
  building has birthScript."

  **`IGdeathscript` is present on every single non-`map_goodie` entry in
  both `.dat` files, zero exceptions — confirmed unconditional, and
  confirmed WHY via the engine call site.** `Hero_Deaths.gpl`'s
  `Unit_Call_Deathscript` (`function Unit_Call_Deathscript(agent
  thisagent) ... if ($validfunction(thisagent's "IGDeathScript") ==
  TRUE) (thisagent's "IGDeathScript")(thisagent);`) is the shared,
  type-agnostic engine-invoked dispatcher for **every** agent type (its
  own comment: "called by the in-game code when a unit's HP are set to 0
  or less") — hero, monster, and building prototypes all declare
  `IGdeathScript`/`IGDeathScript` for exactly this reason (`prototype.gpl`
  literally comments it on the non-building prototypes too: "not used,
  but attribute must exist for `$Unit_Call_Deathscript()`" on
  `Generic_Object`/`Resource`/`Special_Item`/`RewardFlag`/`Spell`/
  `map_goodie`). A building missing `IGdeathscript` in its `.dat` block
  would compile (the field would just hold its default/null value) but
  `$validfunction(...)==TRUE` would be FALSE, so nothing runs on death —
  no `Become_Rubble` action, no cleanup, no `$deleteagent` — this pass's
  §1 sprite-item already confirmed `Become_Rubble`/`Crumble` art is a
  hard requirement reached exclusively through this path, so skipping
  `IGdeathscript` would silently leave a dead building's game piece
  never cleaned up. **Treat `IGdeathscript` as unconditionally required**
  for any new building that should die properly, though the engine
  itself does not enforce it at compile or run time (the same
  "conditional not assert" caveat as `birthScript` above) — the
  `map_goodie` decorative entries are again the sole confirmed exception,
  and again they aren't real buildings.

  **Confirmed genuinely optional, per GPL_MODDING_GUIDE.md — cited, not
  re-derived:** `birthScript2`/`upgradescript` (§2 — building-family-only,
  skipped by every level-2/3 tier and by any building with no
  under-construction-from-zero or upgrade path), `Visited_Script`/
  `Lived_In_Script` (§3/§4 — behavior-dependent; a building can have
  neither, either, or both simultaneously, e.g. `Rogues_Guild2` has
  both), `RevenueScript`/`Revenue_Amount`/`Revenue_Time` (§5 — exactly 6
  buildings in the base+expansion data set them; declared-but-unset on
  `GuardHouse`/`Tower` prototypes, absent entirely on `Guild`/`Palace`/
  `Library`-family prototypes), `Guard_Function`/`Guard_Spawn_Function`/
  `Max_Guards` (§6 — `GuardHouse`/`Palace`/`Outpost` only, see next
  checklist item for the deeper trace).

  **One field is set in the shipped `.dat` despite being commented out
  (undeclared) in the shipped `prototype.gpl` — a genuine
  inconsistency, flagged, not resolved.** `GuardHouse1`/`GuardHouse2` (and
  the official SDK `Adjust Guardhouse Mod/GPL/Guardhouse.dat` example)
  set `(Hero_Guarded False)`, but `prototype.gpl`'s `GuardHouse`
  declaration has that exact field commented out: `// boolean
  Hero_Guarded; //TRUE if the Guardhouse currently has a Hero Guard.
  FALSE if they don't.` (confirmed identical in base `GPL/prototype.gpl`
  line ~578 and expansion `GPLMx/mx_prototype.gpl`). The only two
  GPL-side references to `"Hero_Guarded"` anywhere in the workspace
  (`TaskModules/Characters/Garrison.gpl`'s
  `BackTarget's "Hero_Guarded" = False;`, twice) are **themselves also
  commented out** in the source. **UNVERIFIED, explicitly, not
  guessed at:** whether the real Gplbcc.exe compiler silently tolerates
  a `.dat` field with no matching prototype declaration (name-only,
  loosely-typed dynamic attribute) or whether this is only survivable
  because Building_Data.dat is compiled as a single unit alongside a
  prototype.gpl that — in some historical version — *did* declare
  `Hero_Guarded` before Cyberlore commented it out, leaving a stale
  `.dat` value nobody re-validated. This was **not resolved by actually
  invoking the compiler** — the task's stated method (read-only
  source investigation) does not permit running `Gplbcc.exe`, and no
  existing compile-log or error-message evidence was found in the
  workspace to settle it either way. **Practical implication for a new
  building: do not assume every `(FieldName value)` pair in a `.dat`
  block must have a corresponding prototype declaration — this one
  shipped example suggests it might not be strictly enforced — but do
  not rely on that either without an actual compile test**, which is
  outside this pass's read-only scope.

  **No HP/MaxHP field exists on any true building `.dat` entry — this is
  an XML-side field, not a `.dat`-side one, confirmed by its absence
  pattern.** Scanning both `.dat` files for `(HP `/`(MaxHP ` hits found
  matches **only** on 6 `Lair`-prototype entries (`Brashnards_Sphere`,
  `ElvenHideout`, `Hidden_Sword_Site`, `Hidden_Chalice_Site`,
  `Hidden_Ring_Site`, `Animal_Den`) — never on any `Building`/`Guild`/
  `GuardHouse`/`Palace`/`Tower`/`Library`/`Fairgrounds` entry. This is
  consistent with this doc's own §2 finding that ordinary buildings get
  `MaxHP` from `M_Buildings.xml`'s `<Game>` block instead — the `.dat`
  file's job is exclusively scripting-hook wiring (which functions fire
  when), not stats, for the building-family prototypes. A new building
  does **not** need an HP field in its `.dat` block; that's an XML
  concern (see Section 2).

  **Direct answer to the item's own question:** yes — `type`/`subtype`/
  `title` (structural, universal across every prototype in the entire
  `.dat` system, not just buildings) and `birthScript`/`IGdeathscript`
  (scripting hooks, universal across every *building-family* entry
  checked, though not compiler-enforced) are the fields with no observed
  exception among real buildings. Every other field named in this
  item's own list (`birthScript2`, `upgradescript`, `Visited_Script`,
  `RevenueScript`, `Guard_Function`, `Lived_In_Script`) is confirmed
  behavior-conditional, not universal — consistent with
  `GPL_MODDING_GUIDE.md`'s existing per-field research, not
  contradicting it.
- [x] `Max_Guards`/guard-family fields — confirmed by GPL_MODDING_GUIDE.md
  §6 to only matter for Guardhouse/Palace/Outpost — confirm this remains
  true for a hypothetical new defensive building type, or if there's a
  path to give a new building type its own guard-spawning without being
  one of those three prototypes.

  **Confirmed still true, and traced to the actual mechanism, not just
  re-confirmed by pattern.** `GPL_MODDING_GUIDE.md` §6 is cited directly,
  not re-derived, for the base finding (`Guard_Function`/
  `Guard_Spawn_Function` declared as a pair on exactly `GuardHouse`,
  `Palace`, and mx-only `Outpost`; `Tower` declares neither). This pass
  additionally read `Outpost`'s own prototype declaration in
  `GPLMx/mx_prototype.gpl` (lines 473-547) directly: it independently
  declares its own `Max_Guards`/`Num_Guards`/`Guard_Function`/
  `Guard_Spawn_Function`/`Waiting_Guards`/`Guards`/`Waiting_Guardhouses`
  fields (a near-verbatim copy of Palace's own block, not an inherited
  or shared struct — GPL prototypes don't inherit fields from each
  other, confirmed by `GPL_MODDING_GUIDE.md` §1's "Fields are declared
  independently per prototype, not inherited from one shared base") —
  Outpost is a genuinely separate 4th guard-capable prototype, not a
  Palace alias, though it uses the identical `Palace_Guard_Spawner`
  function as its `Guard_Spawn_Function` value (confirmed:
  `mx_Building_Data.dat`'s `[Outpost]` block sets
  `(Guard_Spawn_Function Palace_Guard_Spawner)`, same as `[Palace1/2/3]`
  and `[EvilPalace]` — no dedicated Outpost-only spawner function
  exists, matching §6's exact wording).

  **No path found for a `{Building}`-prototype (or `{Guild}`/`{Tower}`/
  `{Library}`/`{Fairgrounds}`-prototype) entry to get its own
  guard-spawning — confirmed by tracing the spawner functions' actual
  field reads, not just by their declaration list.** `City_Guard_Spawner`
  and `Palace_Guard_Spawner` (`TaskModules/Buildings/Building_Guard.gpl`,
  read in full) both do `thisagent's "num_guards"` and `thisagent's
  "max_guards"` as bare dynamic-attribute reads on whatever agent calls
  them — GPL's `agent's "fieldname"` syntax does not care which
  prototype declared the field at the language level, so nothing in the
  spawner functions THEMSELVES would refuse to run against a
  `{Building}`-typed agent that happened to have a `max_guards`/
  `num_guards` pair. **However, this does not create a real path**,
  because: (1) the `.dat` compiler validates fields against the
  compiling prototype's own declared field list (the `Hero_Guarded`
  anomaly noted in the previous checklist item shows this validation may
  be looser than expected, but that's a single UNVERIFIED counter-
  example, not a confirmed general bypass — no evidence a `{Building}`
  block can freely add `Max_Guards`/`Guard_Function`/
  `Guard_Spawn_Function` and have the compiler accept it, since
  `building`/`Guild`/`Tower`/`Library`/`Fairgrounds` prototypes don't
  declare any of those three fields at all, unlike the `Hero_Guarded`
  case where the field WAS declared, just commented out — a materially
  different situation); (2) even granting the field could somehow be set,
  nothing else in the engine or GPL source calls `Guard_Function`/
  `Guard_Spawn_Function` on a `{Building}`-typed agent — `NewUnitInit`
  only auto-starts `birthScript`, never `Guard_Function` (confirmed:
  no `$RunThread`/`$NewThread` call site for `Guard_Function` was found
  anywhere outside `Palace_Birth`/`GuardHouse_Birth`/`Outpost_Birth`'s
  own birth-script bodies) — a new building would have to manually
  `$NewThread($thisagent's "Guard_Function", #Normal_Cycle, thisagent)`
  from its OWN `birthScript2`/completion function to ever start the scan
  loop at all, which requires the field to exist and be settable in the
  first place. **Direct answer: the path does not exist through the
  `.dat`/prototype mechanism as shipped — the only confirmed way to get
  genuine `Guard_Function`-driven guard-spawning is to use one of the
  three prototypes (`GuardHouse`/`Palace`/`Outpost`) or to hand-write an
  entirely new prototype block (a 5th one) in a mod's own `prototype.gpl`
  replacement/addition that declares the same field shapes — see next
  checklist item for whether a mod can add wholly new prototype blocks
  at all.**

  **A materially different, and confirmed-working, alternative exists:
  build a custom guard-like mechanic from ordinary `$SpawnUnit`/
  `$NewThread` calls inside a ordinary `{Building}`-prototype's own
  `ActiveScript`, without touching `Guard_Function`/`Max_Guards` at
  all.** Nothing in `$SpawnUnit`'s call sites (`City_Guard_Spawner`/
  `Palace_Guard_Spawner`, both read above) requires the calling agent to
  be Guardhouse/Palace/Outpost-typed — they're ordinary GPL functions
  that happen to be wired to those 3 prototypes' fields in the shipped
  data, not engine-restricted to them. A new building could declare its
  own `ActiveScript`-driven spawn loop (the same mechanism
  `Trading_Post`/`Fairgrounds`/every guild's `spawn_1`/`spawn_2` already
  use per `GPL_MODDING_GUIDE.md` §2/§5) that calls `$SpawnUnit` with its
  own tracking fields (e.g. reusing `spawn_1`, already declared on
  `building`/`Guild`/`Dwarven_Settlement` prototypes) — this would be a
  **new, custom mechanic that behaves like guard-spawning**, not a
  reuse of the real `Guard_Function`/`City_Guard_Spawner`/
  `Palace_Guard_Spawner` machinery (no automatic Palace-guard-pool
  integration, no `Waiting_Guardhouses` list membership, no
  `RestartGuardSpawnThread` tie-in) — genuinely different from "get
  guard-spawning," more like "write your own spawner from scratch using
  already-available generic building fields." **UNVERIFIED** whether
  such a custom mechanic could integrate with the Palace's guard-pool
  bookkeeping (`Num_Guards`/`Max_Guards` counters, `Waiting_Guards`
  list) without also being one of the 3 real guard-prototype types —
  no source traced this far, out of this item's direct scope.
- [x] `subtype`/prototype selection — how does a `.dat` entry's `{Building
  ...}` block vs. `{Guild ...}` block vs. other prototype blocks actually
  get selected, and what does choosing the wrong prototype type break?
  (E.g. can a new building use `{Guild}` to get Lived_In_Script even if
  it's not a "guild" thematically?)

  **Mechanism, traced directly from the `.dat` file syntax itself:** each
  entry is `[EntryName] { PrototypeKeyword (field value) (field value)
  ... } [end]`. The `PrototypeKeyword` immediately after the opening `{`
  (e.g. `Building`, `GuardHouse`, `Guild`, `Palace`, `Tower`, `Library`,
  `Fairgrounds`, `Dwarven_Settlement`, `Lair`, `Outpost`, `Tower_Lair`,
  `map_goodie`, `Special_Item`, `Monster`) is a literal reference to a
  `prototype X() declare ... begin end` block compiled from the
  project's own `.gpl` sources (`prototype.gpl`/`mx_prototype.gpl`,
  confirmed by `path.gplproj`/`Path_Data.gplproj` compiling
  `source="prototype.gpl"` and `data="Building_Data.dat"` together as
  part of the same GPL project — the compiler needs the prototype
  declarations in scope to validate the `.dat` fields against). **This
  is a compile-time struct-template selection, not a runtime dispatch or
  inheritance mechanism** — confirmed by the fully independent,
  non-shared field lists across every building-family prototype in
  `prototype.gpl` (`GPL_MODDING_GUIDE.md` §1 already established
  "Fields are declared independently per prototype, not inherited from
  one shared base" for the hero/monster/building split; this pass
  confirms the same holds across the building-family prototypes
  themselves — `Guild`'s field list and `building`'s field list share
  almost no field names in common beyond `type`/`subtype`/`title`/
  `birthScript`/`birthScript2`/`IGdeathScript`/`deathScript`/
  `upgradescript`).

  **What choosing the wrong prototype type breaks — confirmed two
  distinct, independently-verified failure classes, not a single
  vague "breaks stuff":**
  1. **Compile-time field validation.** A `.dat` entry can only set
     fields the chosen prototype actually declares — e.g. `RevenueScript`
     is declared on `building`/`Fairgrounds`/`GuardHouse`/`Tower` but
     NOT on `Guild`/`Library`/`Palace`/`Dwarven_Settlement` (confirmed
     directly by reading every prototype's full field list in
     `prototype.gpl`) — so a `{Guild ...}` block setting
     `(RevenueScript Foo)` would reference an undeclared field. Whether
     this is a hard compile error or silently tolerated was **not
     empirically tested** in this pass (the task's read-only-source
     method does not permit invoking `Gplbcc.exe`; see the previous
     checklist item's `Hero_Guarded` finding, which shows at least one
     real shipped case of a `.dat`-set field with no live prototype
     declaration — so this is genuinely **UNVERIFIED**, not assumed to
     hard-fail, based on that one confirmed counterexample).
  2. **Runtime GPL function calls that read prototype-specific fields
     unconditionally.** This is the concretely-confirmed failure mode.
     `Building_Guard.gpl`'s `City_Guard_Spawner`/`Palace_Guard_Spawner`
     (read directly, previous item) do bare `thisagent's "num_guards"`/
     `thisagent's "max_guards"` reads with no type-check guard — if
     these were ever called on an agent from a prototype that never
     declared those fields, the call would reference a nonexistent
     dynamic attribute. Similarly, `Lived_In.gpl`'s functions and
     `use_building.gpl`'s `taskname == "go_home"` routing (both cited
     from `GPL_MODDING_GUIDE.md` §4) read/write `Lived_in_Script`/
     `Sleep_For`/`Occupants` — fields declared on `Guild`/
     `Dwarven_Settlement`/`Outpost` but not on plain `building`. Calling
     `$Go_home` → `use_building` → `target's "Lived_in_Script"` against
     a `{Building}`-typed target that never declared that field is the
     concrete "what breaks" — not a vague crash, a specific missing-
     field reference in a specific call chain §4 already traced in
     full.

  **Direct answer to the item's explicit example question: yes, a new
  building CAN use `{Guild}` to get `Lived_In_Script` even if it's not
  thematically a guild — confirmed by real shipped precedent, not
  hypothetical.** `Elven_Bungalow` (`{Guild ...}` block, `title
  Elven_Bungalow`) and `Gnome_Hovel` (`{Guild ...}` block) are both
  literally `{Guild}`-prototype entries despite being residential/
  "hovel"/"bungalow" housing, not adventurer's-guild buildings in the
  thematic sense a player would recognize — confirmed directly in
  `Building_Data.dat` (`[Elven_Bungalow] { Guild ... }`, `[Gnome_Hovel]
  { Guild ... }`). `Dwarven_Settlement` goes further and uses its OWN
  fully separate `{Dwarven_Settlement}` prototype (not `{Guild}` at all)
  despite functioning almost identically to a guild (has
  `Lived_In_Script`, `member_title`, `max_members`) — proving the engine
  cares about the **prototype's declared field shape**, not the
  in-game "is this a guild" concept; `{Guild}` is just the one Cyberlore
  happened to reuse for Elven_Bungalow/Gnome_Hovel because its field
  shape already matched what they needed, while `Dwarven_Settlement` got
  its own bespoke prototype instead of reusing `{Guild}` for reasons not
  explained in any comment (**UNVERIFIED** why Dwarven_Settlement didn't
  just reuse `{Guild}` like Elven_Bungalow/Gnome_Hovel did — no
  functional difference between the two paths was confirmed in this
  pass). **Practical implication, confirmed not hypothetical: a new
  building can freely pick whichever prototype block gives it the field
  set it needs (`{Guild}` for `Lived_In_Script`+guild-membership
  behavior, `{GuardHouse}`/`{Palace}`/`{Outpost}` for guard-spawning,
  `{Tower}`/`{Fairgrounds}`/`{building}` for `RevenueScript`), entirely
  independent of the building's thematic identity** — the `title`/
  `subtype` string fields (freely author-chosen strings, confirmed by
  the wide variety of `subtype` values seen — `xx`, `Shop`, `Guild`,
  `Entertainment`, `color`, `Palace`, `Outpost` — none of which map
  1:1 to the prototype keyword) carry the "what is this thing called"
  identity, while the `{PrototypeKeyword}` carries the "what fields/
  behavior hooks does this thing have" mechanism — these are two
  genuinely independent axes, confirmed by their frequent mismatch in
  real data (e.g. `Dwarven_Settlement`'s `subtype` is literally `Guild`
  even though its prototype keyword is `Dwarven_Settlement`, not
  `Guild`).

  **One real constraint on prototype choice, confirmed, not
  hypothetical:** the chosen prototype must still supply whatever fields
  the OTHER systems this building needs actually read — e.g. picking
  `{Guild}` for `Lived_In_Script` access also means giving up
  `RevenueScript`/`Guard_Function`/`birthScript2` unless the new
  building also custom-declares them via a brand-new prototype (not
  reusing `{Guild}` as-is, since `Guild` doesn't declare those fields at
  all per the full prototype-field read above). A new building can't
  get "all the fields from every prototype" by picking one — it's
  bounded to exactly the field set of whichever single prototype
  keyword it declares, confirming the tradeoff is real, not just
  theoretical.

### 4. Build Queue / Player-Facing Construction Integration (GENUINELY
UNRESEARCHED — this is likely the biggest gap, on par with hero
recruitment, trace it fully)
- [x] How does a building actually appear as a buildable option in the
  player's construction menu/panel? Trace the full chain: what makes a
  building "available to build" at all (tech tree/prerequisite gating,
  if any) vs. what makes it show up in the specific UI list.

  **Two genuinely separate gates found, confirmed from GPL/XML source —
  "on the build menu at all" (an enable/disable bit, engine-primitive-
  controlled) vs. "which menu tab it's filed under" (a plain XML field,
  §2's already-established `Menu` finding) are not the same mechanism,
  and neither is a `Researched_Item()`-style prerequisite check.**

  - **Enable/disable gate — real, confirmed, GPL-invoked, but the
    underlying storage/read mechanism is an opaque engine primitive.**
    `$DisableUnitType("TypeName")`/`$EnableUnitType("TypeName")` are
    real engine primitives (confirmed listed as compiler-recognized
    keywords in `SDK/Extras/GPL User Define[d] Language template for
    Notepad++.xml`'s `Keywords4` block — the same category as
    `$SpawnUnit`/`$CreateAgent`, i.e. built-in, not GPL-authored
    functions; grepped the entire `.gpl` corpus for a `Function
    Disableunittype`/`Function Enableunittype` definition and found
    zero — confirming it's engine-native, not something a GPL function
    body could be read to explain). They are used **extensively and
    unambiguously to gate what appears in the build menu specifically**
    — real base-game example: `GPL/Rules/Demo.gpl`'s `VAMPIRIC_REVENGE`
    quest-init function calls `$disableunittype("Palace3")`,
    `$disableunittype("Temple_Agrela1")` (×7 temples),
    `$disableunittype("Elven_bungalow")`/`Dwarven_settlement`/
    `Gnome_hovel`, `$disableunittype("Inn")`/`Trading_Post`/`Statue`/
    `Library1`, `$disableunittype("Fairgrounds")`/`Royal_Gardens`/
    `Ballista_Tower` — every single target is a real player-buildable
    unit title, called once at quest start, with no matching
    `$enableunittype` call anywhere else in that same file (confirmed
    by reading the full file) — i.e. these buildings are permanently
    unavailable to build for that quest's whole duration, which only
    makes sense if this actually removes them from the build UI
    itself, not some other gameplay system.
  - **Real prerequisite-style pattern found using the SAME primitive —
    confirmed via a genuine disable-then-later-enable pair, not
    inferred.** `GPL/Rules/epic_quest_scripts.gpl` (mx-identical in
    `mx_Epic_Quest_Scripts.gpl`) disables `"fairgrounds"` at quest init
    (line 48) and later — gated behind `AIRootAgent's "Quest_Flag_4" ==
    False` and a `$listobjects`/`$listtitles` check for a specific
    enemy Lair (`Dark_castle`) having been destroyed — calls
    `$enableunittype("fairgrounds")` (line 125, with an accompanying
    `$messageflag(palace,#message_barren_fairground)` "go build the
    fairgrounds" prompt) exactly once, when that condition first
    becomes true. A second, larger example in the same file (line
    866-880) disables `Warriors_guild`/`Rangers_guild`/`Wizards_guild1`/
    `Rogues_guild1`/all 7 temples/all 3 race-buildings at init, then
    re-enables the identical set once a `temple_fervus`-titled building
    is found among the player's own (`#MyPlayer`-implicit) building
    list — a genuine "destroy/build X to unlock the rest of the build
    menu" quest-scripted prerequisite gate. **This is functionally a
    prerequisite/tech-tree gate for buildings, but it is quest-authored
    GPL logic (a specific `Rules/*.gpl` quest-init/polling function
    choosing when to call the primitive), not an engine-enforced
    generic tech-tree system** — there is no equivalent of hero
    research's `Researched_Item()` (`GPL_MODDING_GUIDE.md` §3's
    already-confirmed hero-AI-purchase gate) for buildings; a new
    building has no default prerequisite of any kind unless a quest's
    own GPL explicitly calls `$disableunittype` on it and later
    `$enableunittype`s it under a condition the quest author writes.
    **CORRECTION (found later, via the Quest Rules deep dive — see
    `GPL_QUEST_RULES_REFERENCE.md` §16.1): the "no default prerequisite of any
    kind" claim above is too strong. A second, GPL-side, per-building
    placement prerequisite mechanism DOES exist and was simply not
    looked at in this pass: `GPL/Rules/construction_rules.gpl`'s
    `CanIBuildThisBuilding(agent thisBuilding, list dependencies)`.**
    It is an exe-invoked callback (zero GPL call sites anywhere —
    the engine calls it by name), returning 0 to allow the build and a
    non-zero `#chat_*` code to refuse it. Real shipped branches gate
    `wizards_tower` (must be within `#wiz_tower_range` 800 of a
    completed `wizards_tower`/`wizards_guild` — proximity-REQUIRED),
    `marketplace` and `trading_post` (must NOT be within
    500/1000-1700-2800 of a competing market/trading post —
    proximity-FORBIDDEN), plus an expansion-only `outpost` branch;
    everything else falls through to unconditionally buildable. **A
    modder can add a new per-title branch here with no XML and no exe
    change** — this is a genuine GPL-side prerequisite extension point
    the original pass missed. Two real constraints, both confirmed:
    failure-message codes are indices into the same enum as
    `#intent_*` (`defines.gpl`, 40-43 are the `#chat_*` codes sitting
    between `#intent_assemble`=39 and `#intent_defending_palace`=44),
    so a new failure message cannot be invented — only an existing
    slot reused (`#chat_too_close_market`=43 ships unused); and the
    `dependencies` parameter is **UNVERIFIED** (no live branch reads
    it, no XML field feeds it, only a commented-out design sketch
    describes its intent). **What still stands unchanged from the
    original claim:** there is genuinely no `Researched_Item()`-style
    attribute/tech-tree gate for buildings, and `CanIBuildThisBuilding`
    is proximity/title-based only — it never reads terrain data, so
    this doc's separate terrain-tile findings are unaffected, and the
    footprint/overlap-collision question remains fully open.
    **Confirmed absence, not an oversight** (this part of the original
    finding holds): grepped the entire corpus for any building-specific
    analog of `Researched_Item()` (a function checking an attribute
    before allowing a build) and found
    none — the closest thing, `$SetBuildingLimit`/`$RemoveBuildingLimit`/
    `$RemoveAllBuildingLimits`, are also engine primitives (same
    `Keywords4` list) with **zero GPL call sites found anywhere in the
    corpus** — real, engine-recognized, but **UNVERIFIED** whether any
    shipped quest actually uses them, and their exact semantics
    (limit count? limit by title? per-player?) are not documented in
    any GPL/XML source read in this pass — mark explicitly UNKNOWN.
  - **What actually makes a building's OWN entry exist in the menu at
    all (as opposed to being enabled/disabled) is the plain
    `CanUse value="HumanPlayer"` + `Menu value="N"` XML pair — already
    established in this doc's §2, cited not re-derived.** §2's `Menu`
    finding (`Menu="0"`=temple, `Menu="1"`=guild, `Menu="2"`=ordinary
    buildable, `Menu="3"`=`NotBuildable`-flagged non-menu buildings)
    determines which category tab a building's entry is filed under
    — this is a static, always-present XML declaration, not something
    `$DisableUnitType` touches (disabling a unit type does not require
    removing or changing its `Menu`/`CanUse` fields — the two
    mechanisms are independent layers: XML declares "this building
    belongs in the build menu, category N," the runtime enable/disable
    bit decides "is it currently selectable this game"). **This is the
    "vs. what makes it show up in the specific UI list" half of the
    item's own question, confirmed distinct from the enable/disable
    gate, not the same mechanism.**
  - **UNVERIFIED, explicitly:** the exact internal storage
    `$DisableUnitType`/`$EnableUnitType` write to (a per-player bitmask?
    a flag on the unit-type's compiled DUNT record read at UI-build
    time? something else?) — no GPL source can answer this since the
    primitive has no GPL-visible body, and no Ghidra trace of it exists
    in any reviewed research file (`exe_disassembly_results.md`,
    `TODO-Ghidra.md` do not mention it). This is the same class of gap
    as `$BuildingIsRecruiting` in the hero doc's §5 (a real, used,
    engine primitive whose internal implementation is opaque from
    GPL/XML alone) — flagging it explicitly rather than assuming a
    mechanism. A Ghidra trace of `$DisableUnitType`'s exe-side
    implementation would resolve this — **not yet a scoped
    `TODO-Ghidra.md` item; should be added** (see this section's item 2
    finding below for the closely related, definitively-answered
    question of whether the menu LIST itself is hardcoded vs.
    data-driven — that one did not require Ghidra to resolve, but the
    enable/disable bit's storage mechanism genuinely would).
- [x] Is the build-menu list hardcoded (same limitation class as the
  already-confirmed "building-to-panel mapping is hardcoded per building
  class" finding) or is it data-driven from the XML/`.dat` definitions?
  This is the single most important open question for "can I truly add
  a new building type" — confirm definitively, don't hedge.

  **Answered with real confidence, and it is NOT the same limitation
  class as the DialogID→panel mapping — the build-menu LIST itself is
  data-driven, confirmed by direct, positive evidence, not just an
  absence of a hardcoded-table citation.**

  - **Direct positive evidence: the expansion added entirely new
    buildings to the build menu (Magic Bazaar, Sorcerer's Abode,
    Outpost, Embassy, Mausoleum) without any exe recompilation** — this
    is the identical style of argument
    `SMNUResearch/findings/panel_resolution_analysis.md`'s own "Theory
    C: Hardcoded Table in Engine" section already uses to REJECT a
    hardcoded table for the sub-panel-name-resolution question ("Theory
    C... Unlikely because the expansion added new buildings with new
    panels... without recompiling the base game exe") — the same
    reasoning applies with equal force to "does the menu know about
    this building at all," and the evidence is even more direct here:
    every new expansion building (confirmed via this doc's own §2
    reading of `MX_Buildings.xml`'s `Menu`/`CanUse` fields on Magic
    Bazaar/Sorcerer's Abode/Outpost/Embassy/Mausoleum, all
    `CanUse="HumanPlayer"`, all with real `Menu` values) appears in the
    build menu in Expansion mode despite the base-game exe binary being
    unchanged between modes (base Data/ + DataMX/ overlay per
    `.kiro/steering/majesty-modding.md`'s "Expansion mode" note) — this
    would be impossible if the menu's building LIST were a compiled
    table of DialogIDs/titles the way the panel-open target names are.
  - **Confirms directly from this doc's own §2/§3 findings, not
    re-derived:** every buildable unit's presence is driven by the same
    XML `<Description type="Unit" subType="Building">` entry this whole
    doc already reads field-by-field — `CanUse="HumanPlayer"` +
    `Menu="N"` (§2) is a per-building, per-mod/quest-overridable XML
    declaration, and `Cost`/`Multiplier` (§2, also XML) supply the
    price the menu displays. There is no separate "menu registration"
    step distinct from writing the `M_Buildings.xml`/`MX_Buildings.xml`
    entry itself — the same XML file this whole document already
    treats as the building's primary definition IS the menu's data
    source.
  - **This is a genuinely DIFFERENT answer than the DialogID→panel-open
    mapping question, and the difference is principled, not
    arbitrary — worth stating plainly so the two are never conflated in
    the final guide:** the panel-open mapping
    (`exe_disassembly_results.md`'s Ghidra-confirmed finding) is
    hardcoded because it requires the exe to call a SPECIFIC COMPILED
    FUNCTION per building class (a vtable slot burned in at compile
    time — literally executable code, one 4-byte panel-name constant
    per building class) — there is no way for data alone to add a new
    function pointer to a vtable. The build-menu LIST, by contrast,
    only requires the engine to iterate "every unit-type definition
    flagged `CanUse=HumanPlayer` with a `Menu` value, not currently
    disabled via `$DisableUnitType`" and render a generic button per
    entry — a data-iteration loop, not a per-type dispatch table. These
    are different engineering problems and the expansion's own history
    (new buildings via new XML entries, zero exe changes, per
    `.kiro/steering/majesty-modding.md`'s Expansion Mode architecture)
    is real, positive, already-shipped proof the engine actually works
    this way for the menu specifically — this is not a hedge, this is
    the confirmed answer.
  - **Practical implication for "can I truly add a new building type,"
    stated directly per the item's own instruction not to hedge:** YES
    — a genuinely new building (new DialogID, new title, new XML
    entry with `CanUse="HumanPlayer"`/a `Menu` value) WILL appear as a
    build-menu option with no exe patch required, confirmed by the
    expansion precedent. **What it will NOT get for free** (already
    established, cited not re-derived) is a custom Research/Recruit
    SUB-PANEL of its own — that specific downstream capability remains
    blocked by the Ghidra-confirmed DialogID→panel-factory hardcoding
    (this section's earlier `DialogID` item, and
    `exe_disassembly_results.md`'s "CANNOT DO" section) — but merely
    EXISTING as a clickable, priced, placeable entry in the build menu
    is a wholly separate, confirmed-data-driven capability that does
    not depend on that limitation at all. Do not conflate "can't get a
    custom research panel" with "can't be built" — the building
    doc's own §2/§3 already establish everything a genuinely new
    building needs to function (XML `Description` block, `.dat`
    scripting hooks, sprite sets) independent of whether it also wants
    a bespoke sub-panel.
- [x] Placement/footprint validation — how does the engine decide where a
  building can be placed (terrain type restrictions, overlap checking)?

  **CORRECTION/ADDITION (found later via the Quest Rules deep dive —
  see `GPL_QUEST_RULES_REFERENCE.md` §16.1): this item's framing that placement
  validation is entirely exe-side is too strong. A real GPL-side
  placement gate exists — `construction_rules.gpl`'s
  `CanIBuildThisBuilding`, an exe-invoked callback that a modder CAN
  extend with new per-building-title rules (full detail in this doc's
  §4 build-menu item above, corrected there, and in
  `GPL_QUEST_RULES_REFERENCE.md` §16.1).** It performs *proximity* checks
  between agents only (`$ListObjects` distance/title filtering) — it
  never reads terrain-tile data and carries no footprint/size
  information — so the terrain-restriction and footprint/overlap
  findings below stand exactly as written, unaffected. What changes is
  only the "no GPL-side placement rules exist" implication: proximity-
  based placement prerequisites are genuinely moddable in GPL;
  terrain-type gating and footprint/overlap collision remain
  exe-side/unverified as described below.

  **Terrain-type restriction: confirmed XML-side, already established in
  this doc's §2, cited not re-derived — the `Info` flag set
  (`BlockGround`/`BlockFlying`/`ModifyTerrainTextureOnPlacement`/
  `ModifyTerrainHeightOnPlacement`) is the entirety of what a building's
  own definition declares about placement.** These are pass/fail
  boolean flags, not a terrain-type allowlist/denylist (e.g. no
  "buildable only on grass" or "not on water" field exists anywhere in
  `M_Buildings.xml` — confirmed by the same full-file grep §2 already
  ran for `Footprint`/`Radius`/`Size`/`Collision`, extended here to
  `Terrain`/`Water`/`Land`/`Ground`-type-restriction field names with
  zero additional matches beyond the already-documented `Info` flags).
  Whether the engine derives any ADDITIONAL terrain-type gating from
  something other than these flags (e.g. reading the map's tile data
  directly at cursor-hover time to reject water tiles for a
  `BlockGround` building) is **UNVERIFIED from GPL/XML source** — no
  GPL function anywhere reads terrain-tile data as part of a placement
  check (the only terrain-tile-reading GPL/data system found anywhere
  in this research is the wholly separate RGS `.q`/`.rgs`
  map-generation system, see below), so this would need a Ghidra trace
  of the exe's placement-cursor code, not a GPL/XML citation.

  **Overlap/footprint-size checking: this section's own question is a
  DIRECT continuation of §2's already-established footprint finding —
  cited, not re-derived, then extended with the RGS cross-reference the
  item explicitly asks for.** §2 already confirmed: (a) no dedicated
  footprint/collision-size field exists anywhere in `M_Buildings.xml`
  or in `CAM_MODDING_GUIDE.md`'s documented DUNT field list, and (b)
  the `.kiro/steering/majesty-modding.md` RGS `.q`-file research
  states buildings have engine-enforced minimum spacing ("The placement
  code will not allow objects to overlap, so a minimum spacing will be
  enforced if the placement would cause an overlap") without
  identifying what data source the engine reads for each building's
  size, leaving §2's own most-likely-candidate (derived from the
  sprite's IMAG hotspot+pixel-dimensions) explicitly marked
  **UNVERIFIED**, not confirmed.

  **This pass's specific contribution — the cross-reference the item
  asks for — is answering "is player-driven placement the same
  mechanism as RGS random placement, or different," and the honest
  answer is: NOT CONFIRMED EITHER WAY, and there is a real structural
  reason to suspect they might NOT be identical, not just an
  unexamined gap.** The RGS overlap-prevention note
  (`.kiro/steering/majesty-modding.md`'s "Overlap prevention" bullet,
  §2's own citation) describes a **map-generation-time** behavior — it
  operates on a `.q` file's Unit Pattern 5×5 grid entries (candidate
  cells picked from a `Resolution`-scaled grid, per the same steering
  doc's Q-file-format section: "a resolution of 3 means that each
  layout item is placed 96 pixels from its neighbor") BEFORE the map
  even exists in a playable state — it is resolving a discrete,
  finite candidate-cell list at load time, a fundamentally different
  computational problem than a live player dragging a placement cursor
  over arbitrary continuous pixel coordinates on an already-rendered
  map and getting real-time valid/invalid feedback. **No GPL, XML,
  `.dat`, or existing findings-file source confirms these two systems
  share code, share a footprint-size data source, or even run through
  the same engine subsystem** — the RGS note is exclusively about
  procedural map generation (confirmed scope: it appears in the
  `.kiro/steering/majesty-modding.md` "Q File Format" section
  discussing `.q`/RGSEditor mechanics, never in any building-XML or
  GPL placement context). It would be a plausible engineering choice
  for the same underlying footprint-size lookup to be shared by both
  systems (reusing one collision-check routine for both "does this RGS
  candidate cell overlap another RGS-placed unit" and "does this
  live cursor position overlap an existing building" is the kind of
  thing a real engine would do) — but that is exactly the same
  "plausible but not confirmed" caveat §2 already attached to the
  sprite-bounding-box footprint theory, one level removed. **Do not
  assume they're the same mechanism; do not assume they're different
  either — mark this explicitly UNKNOWN**, consistent with this doc's
  evidence standard. Resolving it would need either a Ghidra trace of
  the live placement-cursor validation code compared directly against
  the RGS generation-time overlap code (confirming or refuting shared
  routines), or an in-game empirical test analogous to the one §2
  already proposed (place two buildings with deliberately different
  sprite pixel dimensions but identical XML, and separately generate an
  RGS map with the same two building types adjacent, checking whether
  the enforced minimum spacing scales with sprite size identically in
  both contexts) — neither was performed here, and neither is currently
  a scoped `TODO-Ghidra.md` item; **should be added** (a new item
  distinct from the existing Priority 1/2/3.4 sub-panel-navigation
  items — this one is about the placement-validation code path
  specifically, not panel/action dispatch).
- [x] Connects directly to the hero-requirements doc's recruitment
  research — if this new building is meant to recruit a new hero type,
  what's the ACTUAL combined requirement? Don't research this in
  isolation from `TODO-New-Hero-Requirements.md` — cross-reference
  explicitly once both docs have initial findings, and flag any
  requirement that only exists BECAUSE the building recruits (vs. a
  building that's purely economic/decorative).

  **Full synthesis deferred to Section 7 ("The Combined Case") per this
  doc's own process notes — that section exists precisely to avoid
  duplicating the cross-reference in two places once both docs have
  full findings.** This item's own scope (per its wording) is to flag,
  not fully resolve, which requirements are recruitment-specific —
  done here in brief, expanded in §7:

  - **Confirmed recruitment-specific, cited from
    `TODO-New-Hero-Requirements.md` §5, not re-derived:** a
    recruiting building needs a `member_title`/`Produces` declaration
    (this doc's own §2 already found `Produces` is "behavior-dependent,
    not universal" — absent on Marketplace1, present on
    Rangers_Guild/Warriors_Guild/Guardhouse1/Palace1) AND — only if it
    wants its OWN new recruit panel rather than reusing an existing
    guild's `member_title` slot — runs directly into the identical
    Ghidra-confirmed `DialogID`→panel-factory hardcoding this section's
    item 2 above already cites, which the hero doc's §5 "Case B"
    finding independently confirms applies identically to guild recruit
    panels ("This applies identically to a brand-new GUILD's recruit
    panel, since guild panels use the exact same DialogID→panel-factory
    mechanism as research panels"). A purely economic/decorative
    building (Marketplace-style) never touches this limitation at all
    — it has no recruit button, no `member_title`, no exposure to the
    panel-factory hardcoding.
  - **Genuinely new finding from THIS section, not previously flagged
    in either doc:** the build-menu-list answer confirmed in this
    section's item 2 (data-driven, no exe patch needed for the building
    itself to appear as buildable) applies identically whether or not
    the building recruits — a recruiting building's mere EXISTENCE in
    the build menu is not blocked by anything recruitment-specific.
    The recruitment-specific blocker is narrower and downstream: only
    the recruit BUTTON's own sub-panel (if the building wants a bespoke
    one rather than reusing an existing guild's) is blocked, not the
    building's buildability itself. This distinction — buildable vs.
    has-a-working-custom-recruit-panel — did not exist as a stated
    finding in either doc before this pass and belongs in §7's combined
    checklist explicitly.

### 5. Sound Requirements
- [x] Ambient/construction/destruction sound requirements — mandatory vs.
  optional, confirmed against real building sound definitions.

  **Method:** read the full `<Description type="Sound" subType="Standard"
  ...>` blocks for `Marketplace` (`BP16`), `Rangers_Guild` (`BP20`),
  `Warriors_Guild` (`BP21`), `Guard_House` (`BP13`), and `Palace` (`PA01`)
  side by side in `SDK/OriginalQuests/Data/M_Sounds.xml`, cross-referenced
  against each building's `DefaultSound` value in `M_Buildings.xml`
  (`Marketplace1`/`Rangers_Guild`/`Warriors_Guild`/`Guardhouse1`/`Palace1`
  — the same 5 core buildings this doc's §2 already reads side by side).
  No `MX_Sounds.xml` cross-check was skipped — expansion's `Outpost`
  (`BP54`) and Magic Bazaar (`DialogID="MX02"`, `DefaultSound
  value="Magic_Bazaar"`) were checked too, confirming the pattern holds
  in expansion data, not just base.

  **Direct answer to this item's own explicit test ("is a building's
  Sound entry even mandatory, or can a building omit DefaultSound
  entirely — test against Marketplace1 directly"): `Marketplace1` does
  NOT omit `DefaultSound` — confirmed present, `value="Marketplace"`,
  matching the `BP16` Sound Description's `Name` attribute (name-match,
  not ID-match — identical wiring mechanism to the hero doc's §4
  `DefaultSound`↔`Sound Name` finding, confirmed independently for
  buildings here, not assumed from the hero doc's analogy).** Broadened
  to a full-file check: `grep`-counted every `<Description type="Unit"
  subType="Building"` entry against every `<DefaultSound value=` tag in
  `M_Buildings.xml` — **91 Description entries, 91 DefaultSound tags,
  zero exceptions.** This is a genuinely different result from §2's
  `Produces` finding (confirmed absent on `Marketplace1` and many others)
  — **the `<DefaultSound>` XML tag itself is unconditionally present on
  every real building entry in this file, unlike `Produces`/
  `RevenueScript`-family fields which are genuinely sometimes-omitted.**

  **However, the tag's presence is not the same as it pointing at a real
  sound — two confirmed real exceptions use a sentinel `value="0"`
  instead of a name:** `placeholder_building` (`ABA0`, the bare-minimum
  reference entry §2 already reads) and `BBs1` (a `Menu="12"` — the same
  transient-spell-effect Menu value the hero doc's §2 found for
  Character entries like `fire_strike`, confirming `Menu="12"` is a
  cross-entity-type "not a real placed object" signal, not
  Character-specific). Confirmed by grep: **zero** `Sound` Description
  anywhere in `M_Sounds.xml` has `Name="0"` — so `value="0"` cannot
  resolve to a real Sound block, it functions as an explicit "no sound"
  opt-out at the VALUE level, not an omission of the FIELD. **Net
  answer: a new building's `DefaultSound` tag should always be written
  (100% precedent), but it CAN legally point at the `"0"` sentinel to
  opt out of having any building-voice sound at all** — this is
  distinct from, and less permissive than, `Produces`'s true field-level
  omission.

  **Phase-vocabulary comparison, buildings vs. the hero doc's §4
  findings — genuinely DIFFERENT, non-overlapping systems, not a subset
  of the hero `Phase` catalog (verified independently against real
  building XML, not assumed from the hero doc's analogy per this task's
  evidence standard):** none of the 5 sampled building Sound blocks
  (`Marketplace`/`Rangers_Guild`/`Warriors_Guild`/`Guard_House`/`Palace`)
  contain a single `VFX_*`-prefixed `Phase ID` — confirmed by a
  workspace-wide grep for `Phase ID="VFX_` across the entire
  `M_Sounds.xml`: every hit resolves to a hero/monster-class-titled
  Sound block (`WD*`/`GE*`/`RE*`/`DF*`/`EF*`/`MK*`/`BN*`-prefixed Wave
  values — the hero doc's own `VFX_GO_COMBAT`/`VFX_FLEE_COMBAT`/
  `VFX_DECIDING`/etc. family) or an `Advisor`/message-style block
  (`VFX_ADVISOR`, a third, unrelated Phase namespace used by UI advisor
  chatter, not by heroes OR buildings) — **zero** `VFX_*` hits land on
  any `BP*`/`PA*`/`DC*`-prefixed (building) Sound ID. Buildings instead
  use a **wholly separate Phase vocabulary**, confirmed present with
  this exact shape on all 5 sampled buildings:
  - **`Select`** (mouse-click acknowledgment, `DistanceModifier
    value="10000.0"` on every sampled building) — present on all 5,
    zero exceptions.
  - **`GetHit`** (damage-taken cue, with `FrequencyVariation`) —
    present on all 5, zero exceptions. This is the ONE Phase ID name
    that's shared verbatim with the hero doc's §4 hero catalog — the
    only overlap between the two vocabularies found in this pass.
  - **`Ambient_Die1` through `Ambient_DieN`** (a *looped* ambient sound,
    `Flags value="Looped"`) — present on all 5, but **N varies: 6 for
    Marketplace/Rangers_Guild, 8 for Warriors_Guild/Guard_House/Palace**
    — not a fixed count, similar in shape to this doc's own §1 finding
    that populated `Build`-family setID counts vary per building.
    **Genuinely odd, flagged not glossed over:** every numbered
    `Ambient_Die` variant within a single building's block points at
    the exact identical `Wave` value (e.g. Marketplace's `Ambient_Die1`
    through `Ambient_Die6` all reference `AM14`; Palace's `Ambient_Die1`
    through `Ambient_Die8` all reference `AM01`) — the numbered slots
    carry no differentiated audio content in any of the 5 sampled
    buildings. **UNVERIFIED** why multiple identical-content numbered
    slots exist (a random-selection-among-duplicates engine mechanism?
    a leftover/unused authoring convention? something else) — no GPL/
    XML source explains it, and despite the field name's surface
    resemblance to "death," `Building_Collapse`/`Become_Rubble` (this
    doc's own §1 already-confirmed destruction path) references a
    **completely different** Sound Description (`BC01`, see below) —
    `Ambient_Die` is NOT the building-destruction sound, despite the
    name; do not conflate the two.
  - **`Ambient_Active1`** (a second looped ambient sound) — present on
    `Marketplace`/`Rangers_Guild`/`Warriors_Guild` (shop/guild-type
    buildings) but **absent on `Guard_House`/`Palace`** — class-
    dependent, not universal, the same "some phases are class-gated"
    shape the hero doc's §4 found for `VFX_CAST_SPELL1`.
  - **`Attack`** — present only on `Guard_House` (`WU27` wave) among the
    5 sampled — confirmed defensive-building-specific, consistent with
    `GPL_MODDING_GUIDE.md` §6's finding that only Guardhouse/Palace/
    Outpost have a `Guard_Function`/arrow-volley mechanic at all (this
    pass does not re-derive that GPL finding, only notes the sound-side
    correlation).
  - **Confirmed absent from every one of the 5 sampled buildings, zero
    exceptions:** `Death`, `Attack`(on the 4 non-Guard_House buildings),
    and the entire `VFX_*` family — buildings have no `Death`-phase
    equivalent inside their OWN `DefaultSound`-linked Sound block at
    all; see destruction-sound finding below for where that cue
    actually lives.

  **Construction/destruction sounds are NOT part of a building's own
  `DefaultSound` Sound block at all — they are separate, shared,
  building-type-agnostic Sound Descriptions wired through the Action
  XML layer, confirmed directly, cross-referencing this doc's own §1
  destruction-visual finding rather than re-deriving it:**
  - **Destruction: `Building_Collapse` (`BC01`)`, a single `Phase
    ID="Begin"` pointing at wave `BC02`.** §1 already confirmed
    `Become_Rubble` (`A009`) is unconditionally reached by every
    building's death path (`building_death`'s hardcoded
    `$performaction(thisagent,"Become_Rubble",thisagent)` call, no
    guard) — reading the action's XML directly here confirms it also
    carries `<Sound value="Building_Collapse"/><SoundPhase
    begin="Begin"/>` alongside the already-cited `<ImageSet
    value="Crumble"/>`. **This means a new building does NOT need to
    author its OWN destruction sound at all** — every building
    automatically gets the identical shared `Building_Collapse` cue for
    free via the same unconditional `Become_Rubble` call this doc's §1
    already established, the same way it automatically needs (and
    gets, if the `Crumble` art exists) the shared collapse animation.
    Destruction sound is **mandatory in effect, but supplied
    automatically — not a field a new building's own `.dat`/XML needs
    to set.**
  - **Construction/placement: `Place_Building` (`PB01`) exists** (single
    `Phase ID="Begin"`, wave `PB01`, `VolumeOverride`/`VolumeVariation`/
    `FrequencyVariation` all set — a deliberately-tuned one-shot cue,
    not a placeholder) **but its trigger wiring is UNVERIFIED — genuinely
    unresolved, not glossed over.** Grepped the entire workspace
    (GPL source + every Action/Building XML) for the literal string
    `Place_Building`: the only hits are the Sound Description itself and
    a `CAM_DEEP_DIVE.md` WAVE-section inventory table — **zero** `<Sound
    value="Place_Building"/>`-style Action XML reference anywhere,
    unlike `Building_Collapse`'s direct, confirmed `Become_Rubble` link.
    This means the construction-placement sound most likely fires from
    an exe-hardcoded call at the moment a building is placed on the map
    (mirroring this doc's own §4 finding that the live placement-cursor
    validation path is itself an opaque engine mechanism, not GPL/XML-
    driven) rather than through the Action/SoundPhase system every other
    sound in this section uses — **mark this explicitly UNKNOWN**, would
    need a Ghidra trace of the placement-confirm code path to resolve,
    consistent with this doc's evidence standard rather than assuming
    "probably also exe-triggered same as Become_Rubble" without a
    citation.

  **Direct summary answer to the item's own "mandatory vs. optional"
  framing:** `Select`/`GetHit`/`Ambient_Die`-family are mandatory-by-
  precedent for a new building's own Sound Description (present on
  100% of the 5 sampled real buildings); `Ambient_Active1` is optional/
  class-dependent (shop-and-guild-type only in this sample); `Attack` is
  optional/defensive-building-only; destruction sound (`Building_
  Collapse`) is mandatory in *effect* but supplied automatically via the
  shared `Become_Rubble` action, requiring **zero** new authoring by a
  new building; construction-placement sound (`Place_Building`) also
  appears to be automatic/exe-driven based on the total absence of any
  GPL/XML wiring reference, but this specific claim is **UNVERIFIED**,
  not confirmed the same way the destruction path is. **No building
  Sound Description anywhere in the 5-sample or the expansion cross-
  check (`Outpost`/Magic Bazaar) uses the hero doc's `VFX_*` Phase
  family** — buildings and heroes use genuinely disjoint Phase
  vocabularies sharing only the `GetHit` name, confirmed independently
  from real building XML rather than assumed from the hero doc's
  pattern, per this task's non-negotiable evidence standard.

### 6. GPL Requirements Beyond What's Already Documented
- [x] Cross-reference GPL_MODDING_GUIDE.md fully before adding anything
  here — the goal is filling gaps, not duplicating §2/§3/§5/§6. Likely
  gaps: does a genuinely NEW building family (not reusing an existing
  Visited_Script/birthScript2/etc.) need anything beyond writing new GPL
  functions and wiring them into the `.dat` the same way existing ones
  are? Or is there a compilation/dataset-registration step not yet
  covered (tie to the hero doc's identical open question about GPL
  bytecode compilation/dataset wiring — likely the SAME underlying
  mechanism for both hero and building GPL, worth resolving once and
  citing from both docs rather than duplicating the investigation).

  **Method:** read `GPL_MODDING_GUIDE.md` in full (all 10 numbered
  sections + Open Questions Catalog + Retracted Claims) before writing
  anything below — cross-checked every claim here against that guide's
  §1-§10 to avoid duplicating its already-confirmed findings on
  birthscript/birthScript2 (§2), Visited_Script (§3), Lived_In_Script
  (§4), RevenueScript (§5), Guard_Function (§6), or the intent system
  (§7). None of this section's findings restate those — they fill the
  two gaps the item explicitly names: (1) what a genuinely NEW building
  family needs beyond writing GPL functions + `.dat` wiring, and (2) the
  compilation/dataset-registration step.

  **Gap 2 (compilation/dataset wiring) resolved by direct verification,
  not by re-deriving — confirmed the SAME mechanism applies identically
  to buildings, per the item's own instruction to verify rather than
  assume:** `TODO-New-Hero-Requirements.md` §3's last bullet ("GPL
  bytecode compilation and dataset wiring") is the citation for the
  base mechanism — not re-derived here. That finding: `SDK/
  OriginalQuests/GPL/path.gplproj` lists every `.dat`/`.gpl` file
  compiled together into ONE `Bytecode.bcd` via `Gplbcc.exe`
  (`MakeGPL.bat`), and `Data/DataSets.xml` loads that single
  `Bytecode.bcd` under `<LoadGPL>` for all three release classifications
  (`MajestyCommonData`, `Rel0`, `Rel2`).

  **Verified directly (not assumed) that `Building_Data.dat` is listed
  in the exact same `path.gplproj`, alongside `Hero_Data.dat`:**
  ```
  data="Hero_Data.dat"
  data="Monster_Data.dat"
  data="Building_Data.dat"
  data="Misc_Data.dat"
  data="Spell_Data.dat"
  ```
  — these five `data=` lines are consecutive, unseparated entries in the
  same file, all feeding the same compile step. Every building GPL
  source file this doc's earlier sections cite (`Building_Births.gpl`,
  `Building_Deaths.gpl`, `TaskModules\Buildings\*.gpl` — `Lived_In.gpl`,
  `Building_Guard.gpl`, `Shop_Visited.gpl`, `Fairgrounds.gpl`, etc.) is
  likewise listed as an ordinary `source=` line in the identical file,
  interleaved with hero decision-tree/task-module `source=` lines, not
  segregated into a separate building-only project or compile pass.
  **Re-read `Data/DataSets.xml` directly here too** (not just cited from
  the hero doc) — confirmed all three `<LoadGPL>Bytecode.bcd</LoadGPL>`
  entries are identical to what the hero doc already found; no
  building-specific `<LoadGPL>` entry or separate dataset exists. **This
  fully confirms the item's own suspicion ("almost certainly does, since
  it's a shared compiler/dataset system") — verified by checking the
  actual file contents, not assumed by inference from the hero doc's
  finding.**

  **Gap 1 (does a NEW building family need anything beyond GPL functions
  + `.dat` wiring) — answered with a real worked example, the official
  shipped SDK mod, not a hypothetical:** `SDK/Adjust Guardhouse Mod/GPL/
  AdjustGuardhouse.gplproj` contains exactly one line —
  `data="Guardhouse.dat"` — no `source=` GPL file at all, because this
  particular mod only overrides an EXISTING building's `.dat` block
  (redeclaring `[GuardHouse2]` with different `Max_Guards`/`Strength`/
  etc., reusing `Building_Guard`/`City_Guard_Spawner`/
  `GuardHouse_Visited`/`basic_birth`/`GuardHouse_Birth`/
  `GuardHouse_death` — every function referenced is a base-game function,
  none newly authored). This confirms overriding an existing building
  family needs only a `.dat`-file-scoped `.gplproj` with zero new GPL
  source — but it does **not** by itself demonstrate the harder case (a
  genuinely NEW building family with NEW functions), so a second,
  real, in-workspace example was checked instead of stopping here.

  **`MyQuest/MyAI/GPL/MyAI.gplproj`/`Game/mx_Building_Data.dat` is a real,
  compiling, mod-scoped project that DOES add new building-side GPL —
  confirmed by reading both files together:** the `.gplproj` lists
  `data="Game\mx_Building_Data.dat"` alongside
  `source="Game\TaskModules\Buildings\mx_Building_Guard.gpl"` and
  `source="Game\TaskModules\Buildings\Mausoleum.gpl"` — ordinary
  `data=`/`source=` lines, structurally identical in shape to the base
  game's own `path.gplproj` entries, just scoped to the mod's own
  `Game\` subfolder. `mx_Building_Data.dat`'s own `[AI_Takeover]` block
  (`{Building (type building)(subtype xx)(title AI_Takeover)(cost 1)
  (Level 1)(birthscript playerOneAI)(IGdeathscript building_death)}`) is
  a genuinely new building TITLE not present in any base/expansion
  `.dat` — confirmed by grep, `AI_Takeover` appears nowhere in
  `Building_Data.dat`/`mx_Building_Data.dat` (the real shipped files) —
  and its `birthscript` points at `playerOneAI`, a function defined in
  this mod's own `custom_rules.gpl`, not a base-game function. **This is
  a real, direct confirmation that a NEW building family needs nothing
  beyond (a) a new `.dat` block using an existing `{Prototype}` keyword
  (here `{Building}` — this doc's own §3 already established prototype
  choice is bounded to one keyword's field set, cited not re-derived),
  (b) new GPL function(s) implementing whatever birthScript/
  IGdeathscript/Visited_Script/etc. hooks it needs, and (c) both the
  `.dat` and the new `.gpl` file(s) listed as ordinary `data=`/`source=`
  lines in a `.gplproj` that gets compiled — there is no additional
  registration step, no separate "building type registry," no
  building-specific compiler flag or dataset section found anywhere in
  this search.** This directly answers the item's own question: NO,
  there is nothing beyond writing new GPL functions and wiring them into
  the `.dat` the same way existing ones are — confirmed by a real
  compiling example already in this workspace, not asserted from
  absence of evidence.

  **One caveat surfaced by this same example, worth flagging rather than
  silently omitting (does not contradict the answer above, but bounds
  it):** `AI_Takeover`'s XML-side `M_Buildings.xml`/`MX_Buildings.xml`
  `<Description>` counterpart was **not found** — grepped both files for
  `AI_Takeover`, zero matches. This means the `.dat`/GPL layer alone is
  necessary but not sufficient for a building to be player-visible/
  placeable — it still needs the XML `Description` entry this doc's §2
  already covers in full (and which the build-menu-list research in §4
  already confirmed is separately data-driven, no exe patch required).
  `AI_Takeover` in this specific mod is apparently spawned directly via
  GPL (`$SpawnUnit`-style call, consistent with its very low `cost 1`
  and `xx` placeholder `subtype`) rather than being placed through the
  normal construction menu — **UNVERIFIED** whether a `.dat`-only
  building (no matching XML `Description`) would even successfully
  spawn via `$SpawnUnit`/`$CreateAgent` without a `.dat`↔XML name match,
  or whether the engine requires both by the time an actual instance is
  created — this specific mod's own GPL call site for `AI_Takeover`
  was not traced further in this pass (out of scope — this section's
  job is the compilation/wiring question, not tracing every consumer of
  a specific mod's cheat building). This is a genuinely new open
  question this pass surfaced, not one carried over from either doc's
  existing Known Gaps.

  **No other gap found beyond these two.** Re-scanned
  `GPL_MODDING_GUIDE.md`'s own "Open Questions Catalog" for anything
  framed as blocking "add a new building" specifically — none of its
  listed items (exe-side `$NewThread` semantics, `$building_upgraded`'s
  real caller, `#ATTRIB_isTaxed` setter, `GuardHouse_Birth`'s missing
  definition, research-button click dispatch, `cProc="8192"`,
  `Menu`-value validity for wrong-but-nonzero values) block a new
  building's basic existence/function — they're all either
  UNVERIFIED-but-non-blocking engine internals (consistent with this
  doc's own §1/§2/§4 UNVERIFIED items being narrowly scoped the same
  way) or already independently covered by this doc's own §2/§4
  (`DialogID`→panel hardcoding, build-menu data-drivenness). Nothing in
  that catalog constitutes an unaddressed "beyond GPL functions +
  `.dat` wiring" requirement.

### 7. The Combined Case: "A Building That Recruits a New Hero"
(This is the user's explicit example — treat it as a required final
synthesis step, not just background context.)
- [x] Once both the hero and building requirement lists have initial
  findings, produce an explicit combined checklist for this specific
  scenario: every requirement from both lists that applies, PLUS
  anything that's unique to the combination (e.g. does the recruit-button
  wiring itself impose requirements beyond "building exists" +
  "hero exists" independently?).

  **Method:** this is pure synthesis of this doc's §1-§6 and
  `TODO-New-Hero-Requirements.md`'s §5 (Recruitment) — both already have
  real findings, no new investigation performed here. Structured as: (A)
  the building's own independent requirements, (B) the hero's own
  independent requirements (cited, not re-derived), (C) requirements
  that exist ONLY because the building recruits, (D) the confirmed hard
  limitations that apply to this combination, (E) what's genuinely
  UNKNOWN for this specific combination.

  **(A) Building requirements — everything from this doc's §1-§3,
  unchanged by whether it recruits:** full sprite set per §1 (`Build`,
  `Die`+numbered variants, `Active`/`Inactive`, `Dead`, `Crumble`,
  `Hotspot`, `Interface` — no `Minimap` needed, that's Palace-specific);
  full XML `<Description type="Unit" subType="Building">` block per §2
  (`CanUse="HumanPlayer"`, `Menu` value, `ImageIDBase`, `DefaultSound`,
  `DialogID`, `MaxHP`, `SightRange`, `Flags value="HasHPBar"`, `HelpID`,
  plus `Cost`/`Multiplier` if it's meant to be player-purchasable rather
  than quest-spawned); `.dat` block per §3 with mandatory `type`/
  `subtype`/`title`, `birthScript`, `IGdeathscript`. None of this changes
  because the building happens to recruit — a recruiting building is a
  building first.

  **(B) Hero requirements — cited directly from
  `TODO-New-Hero-Requirements.md`, not re-derived:** the new hero class
  needs its own full sprite set, its own `M_Characters.xml`
  `<Description type="Unit" subType="Character">` block (`DialogID
  value="AP20"` — the shared hero-info panel, confirmed identical across
  every sampled hero, needs no new panel work of its own per that doc's
  §5 Case-analysis), its own `Cost`/`RecruitDelay`/stat fields, and its
  own `.dat`/GPL wiring (`hero_birth` path, `Generate_Character_
  Attributes` for stat bonuses — whose automatic-vs-manual invocation for
  a UI-recruited hero is itself unconfirmed, see (E) below). This is the
  entirety of `TODO-New-Hero-Requirements.md`'s own scope — not
  duplicated further here.

  **(C) Requirements that exist ONLY because the building recruits —
  the actual "combination-specific" layer, confirmed from both docs'
  existing findings, not newly investigated:**
  - **`member_title` field on the building's `.dat` block** — a plain
    string naming the hero title this building recruits (this doc's §3
    citation of `Building_Data.dat`'s Guild entries, e.g. `(member_title
    Rogue)`). This is the ONLY `.dat`-side field that ties a building to
    a specific hero class, and it's a bare string match against the
    hero's own `title` field — no ID-based linkage, no shared enum.
  - **`Produces` XML field with nested `<Unit ID="..."/>` entries** on
    the building's `<Game>` block (this doc's §2 finding: present on
    every recruiting/spawning building sampled — Rangers_Guild,
    Warriors_Guild, Guardhouse1, Palace1 — absent on non-producing
    Marketplace1). **UNVERIFIED, and flagged as a genuinely new
    open question by this synthesis, not previously stated in either
    doc:** whether `Produces`/`member_title` must name the SAME hero
    (i.e. are they two redundant declarations of one relationship, or
    does one drive UI display — e.g. "what shows in a tooltip" — while
    the other drives the actual `.dat`-side `check_strays`/`guild_birth`
    logic) was not traced in either doc. Building it wrong (mismatched
    `Produces` vs `member_title`) has an unknown failure mode — likely a
    cosmetic UI/tooltip mismatch rather than a crash, given `Produces`
    was never traced to a GPL consumer in this doc's §2 research, but
    this is inference, not confirmed.
  - **Capacity gating — `MaxGuildMembers`/`Flags value="IsGuild"` (XML,
    this doc's §2) and the corresponding `.dat`-side `max_members`
    field feeding `GuildHasOpenSlots`** (hero doc §5 item 2, cited not
    re-derived: one shared function, gated additionally on the opaque
    engine primitive `$BuildingIsRecruiting`). A building that recruits
    needs this pair even if it uses `{Building}` rather than `{Guild}`
    as its prototype keyword — this doc's §3 "subtype/prototype
    selection" finding already confirms prototype choice is bounded to
    field sets, so a non-`{Guild}` recruiting building would need
    `max_members`-equivalent fields custom-declared on whatever
    prototype it uses, since `{Building}` doesn't declare them at all.
  - **Birth-completion function choice depends on hero-type count, not
    just "does it recruit."** Cited from hero doc §5 item 2: a
    single-hero-type guild can point `birthScript2` at the generic
    `guild_birth` (which internally calls `check_strays` using the
    building's own `member_title`); a building recruiting MULTIPLE hero
    types (the `Warriors_Guild` pattern — Warrior/Paladin/Warrior_of_
    Discord from one building) needs its own dedicated completion
    function (`warriors_guild_birth`-style) with one `check_strays` call
    per hero type, since `guild_birth`'s generic form only handles one
    `member_title` string. **A brand-new building recruiting exactly ONE
    new hero type can use the generic `guild_birth` unmodified** — this
    is the simplest, most confirmed path for the user's stated example.
  - **The recruit button/panel itself is the SAME confirmed hard
    limitation as new-building `DialogID` generally, not a new,
    separate constraint layered on top — this is the single most
    important point of this synthesis, stated per hero doc §5 Case
    A/B/C, cited not re-derived:**
    - **Case A (recommended, fully unblocked):** the new hero recruits
      through an EXISTING guild's `member_title` slot (repoint an
      existing guild's `.dat` field, or give the new building a
      `DialogID` that's already in the exe's hardcoded panel-factory
      table — e.g. reusing an existing guild-type `DialogID` value).
      Zero exe-patch requirement. This is a `.dat`/XML edit only.
    - **Case B (blocked):** the new building wants its OWN never-
      before-seen `DialogID` with its OWN dedicated recruit panel.
      Blocked by the identical Ghidra-confirmed panel-factory hardcoding
      this doc's §2 `DialogID` item already documents in full
      (`FUN_0051b150`'s finite, compiled `DialogID`→constructor table;
      an unrecognized `DialogID` falls through to the generic handler,
      which per that citation "does NOT open a new panel"). Requires an
      exe patch, no GPL/XML/CAM path exists.
    - **Case C (unverified middle ground):** reusing the
      `Warriors_Guild`-style "multiple pre-defined SMNU buttons,
      exe toggles visibility" pattern on an EXISTING multi-slot guild
      panel, if such an unused slot exists. Confirmed real only for
      `Warriors_Guild` itself; not confirmed to exist on any other
      guild panel, and not confirmed to be extensible via SMNU editing
      alone without also patching whatever exe-side condition toggles
      button visibility.

  **(D) Confirmed hard limitations that govern this combination
  (restated together here per the item's own request for a combined
  checklist, cited from (C)/§2/hero-doc-§5, not new):** (1) a genuinely
  new hero class recruited via an EXISTING guild slot (Case A) is fully
  achievable with `.dat`/XML/GPL/sprite work alone, no exe patch, for
  BOTH the building side and the hero side — this is the confirmed
  "yes, doable today" answer for the user's literal example, provided
  the recruiting building itself also already exists or reuses an
  already-mapped `DialogID`; (2) a genuinely new hero recruited through
  a genuinely new, dedicated recruit panel (Case B, either because the
  building itself is new-`DialogID` or because the new hero specifically
  needs a panel distinct from an existing guild's) is blocked, requiring
  an exe patch to the panel-factory vtable — this is the same wall for
  both docs, not two separate walls that happen to look similar; (3) the
  building's mere existence as a buildable, placeable, HP-bar-having,
  properly-dying structure is NOT gated by any of this — per this doc's
  §4 finding, build-menu presence is confirmed data-driven, independent
  of whether the building recruits.

  **(E) Genuinely UNKNOWN for this specific combination (not carried
  over verbatim from either doc — these only arise from the combination
  itself):** whether `Produces` and `member_title` must name the same
  hero or serve different purposes (flagged in (C) above, newly
  surfaced by this synthesis); whether the recruit-click gold-check
  (hero doc §5 item 1's single biggest gap — no confirmed GPL/exe source
  for the literal click-to-spawn step for ordinary guilds) behaves any
  differently for a brand-new building vs. an existing one — no reason
  to assume it would, but not confirmed either; whether a brand-new
  `{Guild}`-prototype building can validly set `member_title` to a hero
  `title` string that has NO corresponding `M_Characters.xml` entry yet
  (i.e. does `.dat`/GPL compilation cross-validate `member_title`
  against real hero titles, or is it a loosely-typed string like
  `Hero_Guarded` — this doc's §3 already flags that exact class of
  compiler-validation question as unresolved for a different field, and
  it applies identically here, not independently re-verified).

### 8. Known Gaps After This Pass
(Fill in as research proceeds — list every UNVERIFIED item explicitly.)

**Consolidated from every UNVERIFIED/UNKNOWN item flagged across §1-§7 —
cited from where each was first raised, not re-derived here:**

- **Whether Palace's `Minimap` IMAGE set and lack of a `Build` set are
  enforced/required-by-engine, or coincidental to the one Palace example
  checked** — no second birthScript-less building type was checked to
  confirm either pattern generalizes (§1).
- **Whether the numbered `Build`-family setIDs (80-82) hold genuinely
  distinct construction-progress art or are aliased/placeholder slots**
  — only the first 6 tile indices of each set's slot 2 were compared,
  not full frame content; no GPL/XML selection logic ties construction
  %HP to a specific ImageSet (§1).
- **Whether omitting a `Crumble` ImageSet on a new building crashes
  `$performaction(...,"Become_Rubble",...)` outright or just renders
  nothing** — not tested in-game (§1).
- **What actually represents an ordinary (non-Palace) building on the
  minimap** — generic engine-computed dot, a downscaled existing
  ImageSet, or no per-building representation at all; not distinguished
  by any GPL/XML source read (§1).
- **What the XML `<Multiplier>` field's real engine consumer is** — no
  GPL function reads it directly; only its correlation with revenue-type
  buildings was confirmed, not its actual effect (§2).
- **Whether `Menu` value alone (vs. `Flags value="IsGuild"`) is what the
  engine actually keys off of for build-menu categorization**, and
  **why `Graveyard`/`Sewer` are the two Monster-`CanUse` exceptions still
  using `Menu="3"` instead of the otherwise-consistent `Menu="2"`**, and
  **whether setting an ordinary building to a "wrong" but valid nonzero
  `Menu` value misfiles it or breaks it outright** — none resolved
  without an exe trace (§2).
- **Whether two unrelated building types sharing one `DialogID` (Case A
  workaround) causes any cross-talk beyond the shared panel itself** —
  not tested (§2).
- **What data source the engine reads for building placement/overlap
  collision sizing** — no dedicated XML/`.dat`/documented-DUNT field
  exists; the sprite-bounding-box-derived theory is plausible but
  explicitly unconfirmed, and whether live player placement validation
  shares any code/data path with RGS map-generation-time overlap
  prevention is marked fully UNKNOWN, not assumed either way (§1/§4).
- **The internal storage mechanism `$DisableUnitType`/`$EnableUnitType`
  write to** — opaque engine primitive, no GPL-visible body, not
  addressed in any reviewed Ghidra research file (§4).
- **Whether `$SetBuildingLimit`/`$RemoveBuildingLimit`/
  `$RemoveAllBuildingLimits` are used by any shipped quest, and their
  exact semantics** — real engine primitives with zero found GPL call
  sites anywhere in the corpus (§4).
- **Why `Dwarven_Settlement` got its own bespoke prototype instead of
  reusing `{Guild}` the way `Elven_Bungalow`/`Gnome_Hovel` did** — no
  functional difference confirmed between the two paths (§3).
- **Whether the `Hero_Guarded`-style `.dat` field with no live prototype
  declaration is tolerated by the real compiler, or survives only by
  historical accident** — not tested, outside this research's read-only
  scope (§3).
- **Whether a `.dat`-only building with no matching XML `Description`
  entry can successfully spawn via `$SpawnUnit`/`$CreateAgent`** — the
  `AI_Takeover` example spawns via GPL with no traced XML counterpart,
  but the spawn call site itself wasn't traced further (§6).
- **Whether `Produces` and a recruiting building's `member_title` field
  must name the same hero, or serve genuinely different purposes** —
  newly surfaced by this pass's §7 synthesis, not previously flagged in
  either doc.
- **Whether a `.dat`/GPL compile step cross-validates a `{Guild}`
  building's `member_title` string against a real, existing hero
  `title`** — same open compiler-validation-strictness question as the
  `Hero_Guarded` case, not independently re-verified for this field
  (§7, citing §3).
- **The literal recruit-button click-to-spawn mechanism for ordinary
  (non-Embassy) guilds** — cited directly from
  `TODO-New-Hero-Requirements.md` §5/§6 as that doc's single biggest
  gap; equally unresolved whether it behaves any differently for a
  brand-new building vs. an existing one (§7).
- **Whether any guild besides `Warriors_Guild` has pre-defined-but-
  unused SMNU recruit button slots (Case C)** — only Warriors_Guild's
  panel was confirmed to have this pattern; cited from
  `TODO-New-Hero-Requirements.md` §5 (§7).
- **Building-unlocked player-castable "guild skill" abilities (Rage of
  Krolm/Temple of Krolm, Call to Arms/Warriors Guild, and — per the
  Petrify correction above — building-cast spells like Petrify/Temple to
  Dauros) — how a building grants/revokes this, and whether losing the
  building revokes the ability, is NOT covered anywhere in §1-§7 above.**
  Flagged by the user as a real gap after the Petrify research (§1's
  cross-reference into `GPL_MODDING_GUIDE.md` §11) surfaced that
  building-cast spells are a real, distinct mechanism this doc's
  sections never separately considered — every section above treats a
  building's outputs as either produced UNITS (`Produces`, §2/§7) or
  passive stats/revenue (§2/§3), never a player-triggerable ABILITY the
  building itself grants. **Researched — see `GPL_MODDING_GUIDE.md` §12
  and `TODO-GPL-Deepdive.md` item 13 for full findings, including a
  correction after user input.** Summary: Rage of Krolm/Call to Arms are
  confirmed (by the user) to be ordinary button clicks inside their own
  guild's panel — the same trigger CLASS as Petrify's AP05 button, not a
  separate mystery; what's still unconfirmed is only the exe-side
  click-dispatch code (no GPL/XML call site invokes `DoRageOfKrolm`/
  `DoAssembly`, consistent with an ordinary exe-hardcoded panel button).
  `Temple_Krolm`/`Warriors_Guild` are single-tier buildings with no
  `Skill`/`Ability` XML field, so the unlock mechanism structurally
  cannot be a Level-3-style tier gate the way Petrify's is. Whether
  destroying the building revokes the ability is explicitly UNVERIFIED
  from source, but the likely mundane explanation (losing the only copy
  of the building removes its panel/button along with it, not a
  separate revocation mechanic) is settleable in-game, no Ghidra needed.
  A modder CAN call these functions (or write new ones of the same
  shape) from custom GPL, confirmed via the Dwarfeh_AI mod's real
  (non-duplicate) call into `DoRageOfKrolm` — but making a NEW such
  ability player-triggerable from a building panel hits the same
  exe-hardcoded-panel wall Petrify's research found; no base-game
  "spell registry" exists to hook into instead.

**Overall assessment, stated plainly:** the confirmed-achievable path —
a new building recruiting exactly one new hero type, either through an
existing guild's `member_title` slot or a `DialogID` already present in
the exe's hardcoded panel table — requires no exe patch and is fully
supported by `.dat`/XML/GPL/sprite work alone (§7-D). The confirmed
blocker — a genuinely new, dedicated recruit/research panel tied to a
brand-new `DialogID` — requires an exe patch to the panel-factory
vtable, identically for buildings and for guild-hosted hero recruitment,
since both route through the same Ghidra-confirmed mechanism (§2, §7-D).
Everything in this Known Gaps list is either a cosmetic/UI-behavior
question or an engine-internal mechanism opaque to GPL/XML source —
none of it has been shown to block basic building or building+hero
functionality, only to leave some secondary behaviors (minimap
representation, construction-stage visual selection, exact recruit-cost
deduction mechanics) without a citation-backed explanation.

## Process Notes for Sub-Agent Dispatches (write in SMALL portions)

This has caused real problems before — a large single-edit research
pattern in `TODO-GPL-Deepdive.md` led to one dispatch crashing outright
mid-write and losing all its work before landing anything. Going forward:

- **Save after each numbered subsection (or even each checklist item),
  not once at the end of a whole coverage area.** Use `str_replace` to
  append a completed `- [x]`/`- [ ]` item immediately after finishing its
  investigation, then move to the next item — don't accumulate section
  1-8 in memory and write it all in one massive edit.
- **Re-read the file immediately before each small write** (other work
  may have landed concurrently on this file, and this avoids stale-content
  `str_replace` failures).
- Long citation-heavy findings per item are fine — the point is
  incremental commits per item/subsection, not shortening findings.
- Same tool-usage rules as `TODO-GPL-Deepdive.md`'s process notes:
  `grep_search`/`read_file`/`read_files` for investigation,
  `utility/test_decoder.py` (the one named trusted scratch script) if a
  script is genuinely needed, no ad hoc PowerShell.
- **This doc's §4 and §7 depend on `TODO-New-Hero-Requirements.md`'s
  recruitment findings (§5) being done first** — don't research the
  combined-case section in isolation before both individual docs have
  real content to cross-reference.
