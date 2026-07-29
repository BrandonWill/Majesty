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
- [ ] Which animation/state sets are mandatory for a building
  specifically (buildings don't walk/attack like heroes — what states DO
  they need? Under-construction stages, idle, destroyed/collapsed,
  minimap icon — confirm against real building IMAG records, e.g.
  compare a single-level building like Inn against a multi-level one like
  Marketplace to see if level-tiers need separate full sprite sets or
  share one).
- [ ] Isometric art conventions — footprint/tile-size, ground-plane
  alignment, shadow handling. Is there a documented or inferable pixel
  grid buildings must align to (the existing `PG01`-style terrain prefix
  table implies a tile system — does building art need to match specific
  tile-multiples)?
- [ ] Construction-stage visuals — does the game render partial-HP
  construction progressively (scaffolding-style sprites) or is
  construction invisible until `birthscript2`/completion (per
  GPL_MODDING_GUIDE.md §2 — cite it, don't re-derive, but confirm what
  the VISUAL side of "under construction" actually shows, which that
  section doesn't cover).
- [ ] Destruction/collapse visuals — `Building_Collapse` action was
  noted in earlier research (GPL_MODDING_GUIDE.md §8's cProc mention) —
  is a collapse animation mandatory or optional for a new building?
- [ ] Minimap icon requirements.
- [ ] Palette constraints — same question as the hero doc: existing-only
  vs. quest-scoped-new-palette-allowed.

### 2. Unit XML Definition Requirements (M_Buildings.xml / MX_Buildings.xml)
- [ ] Full required-field catalog for `type="Unit" subType="Building"`
  with `CanUse value="HumanPlayer"` — read multiple real building
  definitions side by side (a shop-type, a guild-type, a defensive-type
  like Guardhouse, and a unique like Palace) to determine always-present
  vs. sometimes-omitted fields — don't generalize from one example.
- [ ] `Menu value="N"` for buildings — confirm what values are valid/what
  they control (existing docs note "2=building" generically — is there
  sub-categorization by building menu value that affects build-menu
  placement?).
- [ ] Cost/`costMultiplier`/`Level` fields — how multi-level buildings are
  declared as separate `Description` entries vs. one entry with tiers —
  confirm from real XML, this was asserted generically in earlier
  `.dat`-focused research but not confirmed at the XML layer.
- [ ] `DialogID` — full explanation of what this field does and is
  required for (connects to the already-Ghidra-confirmed
  "building-to-panel mapping is hardcoded per building class" finding in
  `SMNUResearch/findings/exe_disassembly_results.md` — cite it, this is
  a DIRECT, confirmed blocker: a genuinely NEW building type cannot have
  a NEW research/service panel without an exe patch, per that finding.
  Make sure this shows up prominently as a hard requirement/limitation
  in the final checklist, not buried).
- [ ] Footprint/collision size — where is a building's ground footprint
  actually defined (XML field, derived from sprite dimensions, or
  something else)?

### 3. `.dat` / Building_Data.dat Requirements (cross-reference
GPL_MODDING_GUIDE.md §2/§3/§5/§6 extensively — this section overlaps the
most with existing research, the job here is COMPLETING the picture for
"new building" specifically, not re-deriving what's already found)
- [ ] Full required-field catalog for a NEW building's `.dat` block —
  cite GPL_MODDING_GUIDE.md's existing per-field findings
  (birthscript/birthScript2, upgradescript, Visited_Script,
  RevenueScript, Guard_Function, Lived_In_Script) but explicitly answer:
  which of these are MANDATORY for ANY new building vs. only relevant if
  the building needs that specific behavior? (e.g. RevenueScript is
  clearly optional — GuardHouse/Tower declare it but never set it, per
  existing research — but is there anything that's unconditionally
  required for EVERY building regardless of type?)
- [ ] `Max_Guards`/guard-family fields — confirmed by GPL_MODDING_GUIDE.md
  §6 to only matter for Guardhouse/Palace/Outpost — confirm this remains
  true for a hypothetical new defensive building type, or if there's a
  path to give a new building type its own guard-spawning without being
  one of those three prototypes.
- [ ] `subtype`/prototype selection — how does a `.dat` entry's `{Building
  ...}` block vs. `{Guild ...}` block vs. other prototype blocks actually
  get selected, and what does choosing the wrong prototype type break?
  (E.g. can a new building use `{Guild}` to get Lived_In_Script even if
  it's not a "guild" thematically?)

### 4. Build Queue / Player-Facing Construction Integration (GENUINELY
UNRESEARCHED — this is likely the biggest gap, on par with hero
recruitment, trace it fully)
- [ ] How does a building actually appear as a buildable option in the
  player's construction menu/panel? Trace the full chain: what makes a
  building "available to build" at all (tech tree/prerequisite gating,
  if any) vs. what makes it show up in the specific UI list.
- [ ] Is the build-menu list hardcoded (same limitation class as the
  already-confirmed "building-to-panel mapping is hardcoded per building
  class" finding) or is it data-driven from the XML/`.dat` definitions?
  This is the single most important open question for "can I truly add
  a new building type" — confirm definitively, don't hedge.
- [ ] Placement/footprint validation — how does the engine decide where a
  building can be placed (terrain type restrictions, overlap checking)?
- [ ] Connects directly to the hero-requirements doc's recruitment
  research — if this new building is meant to recruit a new hero type,
  what's the ACTUAL combined requirement? Don't research this in
  isolation from `TODO-New-Hero-Requirements.md` — cross-reference
  explicitly once both docs have initial findings, and flag any
  requirement that only exists BECAUSE the building recruits (vs. a
  building that's purely economic/decorative).

### 5. Sound Requirements
- [ ] Ambient/construction/destruction sound requirements — mandatory vs.
  optional, confirmed against real building sound definitions.

### 6. GPL Requirements Beyond What's Already Documented
- [ ] Cross-reference GPL_MODDING_GUIDE.md fully before adding anything
  here — the goal is filling gaps, not duplicating §2/§3/§5/§6. Likely
  gaps: does a genuinely NEW building family (not reusing an existing
  Visited_Script/birthScript2/etc.) need anything beyond writing new GPL
  functions and wiring them into the `.dat` the same way existing ones
  are? Or is there a compilation/dataset-registration step not yet
  covered (tie to the hero doc's identical open question about GPL
  bytecode compilation/dataset wiring — likely the SAME underlying
  mechanism for both hero and building GPL, worth resolving once and
  citing from both docs rather than duplicating the investigation).

### 7. The Combined Case: "A Building That Recruits a New Hero"
(This is the user's explicit example — treat it as a required final
synthesis step, not just background context.)
- [ ] Once both the hero and building requirement lists have initial
  findings, produce an explicit combined checklist for this specific
  scenario: every requirement from both lists that applies, PLUS
  anything that's unique to the combination (e.g. does the recruit-button
  wiring itself impose requirements beyond "building exists" +
  "hero exists" independently?).

### 8. Known Gaps After This Pass
(Fill in as research proceeds — list every UNVERIFIED item explicitly.)
