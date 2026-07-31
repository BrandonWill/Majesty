# Majesty Modding Toolkit — Master TODO

See also:
- `TODO-Ghidra.md` — EXE patching / disassembly work (requires Ghidra
  machine). **For the Ghidra machine itself: start from `GHIDRA_TASK.md`
  instead** — minimal entry point so that session doesn't need to
  explore the repo.
- `TODO-GameTests.md` — In-game verification tests (requires loading the game)
- `TODO-GPL-Deepdive.md` — GPL/gameplay logic deep dive (now complete),
  the research record behind the two GPL reference docs below
- `GPL_MODDING_GUIDE.md` — gameplay-systems reference, **§1-§15**
- `GPL_QUEST_RULES_REFERENCE.md` — quest-scripting reference, **§16-§22**,
  split out of the guide (it was 76% of a 9,858-line file) and reorganised
  into mechanism chapters behind an "I want to …" task index.
  **A bare `§1`-`§15` means the guide, `§16`-`§22` means the quest
  reference** — subsection numbers were not renumbered by the split.
- `NEW_HERO_REQUIREMENTS.md` — **the actual checklist deliverable**: how
  to add a new hero, step by step, with confidence markers per item
- `TODO-New-Hero-Requirements.md` — the research/citations behind the
  checklist above (sprites, XML, GPL, sound, recruitment)
- `NEW_BUILDING_REQUIREMENTS.md` — **the actual checklist deliverable**:
  how to add a new building, step by step, with confidence markers per
  item (mirrors `NEW_HERO_REQUIREMENTS.md`'s format)
- `TODO-New-Building-Requirements.md` — the research/citations behind the
  checklist above — all 9 sections complete (§9 is the reconciliation
  pass against the quest-rules research)
- `IceSpell/TODO.md` — IceSpell mod-specific tasks
- `SMNUResearch/FUTURE_TODO.md` — Panel system research + tooling


---

## Active Work (this machine)

### New Hero / New Building Requirements Docs
- [x] **`NEW_HERO_REQUIREMENTS.md` deliverable created** — the actual
  literal checklist `TODO-New-Hero-Requirements.md` was always meant to
  produce (sprites → XML → GPL/compilation → sound → recruitment), with
  ✅/⚠️/❓ confidence markers per item. Bottom line: a new hero fully
  art/stat/sound-complete and recruited via an EXISTING guild slot is
  fully achievable today, no open gaps. A new hero needing its OWN new
  guild/recruit panel is blocked by the same confirmed exe DialogID→panel
  hardcoding wall as new buildings generally. Changing recruitment's
  click-time behavior itself (cost, spawn conditions) beyond the two
  confirmed GPL mechanisms (`check_strays`/`adopt`, `Hero_Generator`)
  still needs real Ghidra work, not just source-reading.
- `TODO-New-Hero-Requirements.md` (the underlying research/citations) had
  its recruitment section (§5) corrected twice after user pushback caught
  overreached conclusions — worth reading that doc's inline corrections
  as an example of how "ask the user who's actually modded this" resolved
  ambiguity that re-reading source alone couldn't.
- [x] `TODO-New-Building-Requirements.md` §7 AND §8 are now done — a
  prior session's dispatch had written a "§7 done" summary note into
  this very TODO.md file but crashed before the actual §7 content ever
  landed in the target doc (confirmed: re-read the file directly, §7/§8
  were still empty placeholders). Redone directly this pass — pure
  synthesis of that doc's own §1-§6 plus `TODO-New-Hero-Requirements.md`
  §5, no new investigation needed. Bottom line unchanged from the hero
  doc: recruiting through an EXISTING guild slot (Case A) is fully
  achievable with `.dat`/XML/GPL/sprite work alone; a genuinely new
  dedicated recruit panel (Case B) is blocked by the same exe
  `DialogID`→panel hardcoding wall, not a separate constraint. Two
  genuinely new open questions surfaced by the synthesis itself (not
  previously stated in either doc): whether a building's `Produces` XML
  field and its `.dat` `member_title` field must name the same hero or
  serve independent purposes (answerable from GPL/XML source alone, no
  Ghidra needed — nobody has traced `Produces` to a GPL consumer yet),
  and whether the recruit-click gold-check/`$SpawnUnit` step behaves
  differently for a brand-new building vs. an existing one (folds into
  the existing Ghidra item below). §8 consolidates every UNVERIFIED item
  raised across §1-§7 into one list with an overall assessment.
  **`TODO-New-Building-Requirements.md` research is now fully complete
  (all 8 sections)** — a `NEW_BUILDING_REQUIREMENTS.md` deliverable
  (mirroring `NEW_HERO_REQUIREMENTS.md`'s format) is the natural next
  step, not yet done.
- [x] Every UNVERIFIED item from both docs that needs Ghidra (not just
  source-reading) is now scoped into `TODO-Ghidra.md` as dedicated
  priorities — Priority 5 (building placement/collision footprint,
  `$DisableUnitType`/`$EnableUnitType`, building limit primitives, `Menu`
  value keying, construction-stage sprite selection, ordinary-building
  minimap representation) and Priority 6 (hero `Cost` field's real
  consumer, `RecruitDelay` enforcement, `$BuildingIsRecruiting`
  contract). See `TODO-Ghidra.md` for the full writeups.
- [x] **`NEW_BUILDING_REQUIREMENTS.md` deliverable created** — the
  literal checklist (958 lines), mirroring `NEW_HERO_REQUIREMENTS.md`'s
  ✅/⚠️/❓ format: Step 1 sprites, 2 XML, 3 `.dat`/prototype/compilation,
  4 sound, 5 construction menu + placement rules, 6 the `DialogID` panel
  wall, 7 a building that recruits a hero (Cases A/B/C), plus a Bottom
  Line. 75 ✅ / 15 ⚠️ / 27 ❓. Headline verdict: **a new building that
  reuses an existing `DialogID` is fully achievable today** — the
  build-menu list is data-driven (the expansion's own new buildings
  prove it, same exe) — while **a new building needing its own brand-new
  panel is blocked**, though §9.5's caveat means "not yet ruled out"
  rather than proven impossible. Carries §9.1's retraction (`Menu` is
  the build-menu categoriser; `Flags value="IsGuild"` is not — seven
  temples ship `IsGuild` + `Menu="0"`).
- [x] **Both internal contradictions in
  `TODO-New-Building-Requirements.md` resolved from source** (not just
  tidied — each was settled by going back to the shipped data, and both
  turned out to be real factual errors, not wording slips). Corrections
  are visible blocks with the original text left in place.
  1. **§1 `Build`-family count — the early claim was FALSE.** It said
     "only ONE `Build` set exists per building record ... no `Build-2`/
     `Build-3`-style numbered variant." Enumerating every ImageSet in
     all 7 sampled IMAG records (`cam_reader.read_cam()` +
     `sprite_extractor.parse_anim_set()`) confirms the later bullet
     instead: Inn 80/81, Marketplace1 80/81/82, Marketplace2 80/81,
     Marketplace3 80/81, Guardhouse1 80/81/82, Guardhouse2 80 only,
     Palace1 none — all at distinct `relOff`, so not aliases. **Root
     cause recorded:** the original pass matched the set *name* `Build`
     (only setID 80 carries it) instead of the setID *range* 80-83.
     Bonus finding: the `Die` family count isn't uniform either (Inn/
     both Guardhouses/Palace = 96-103, all Marketplace tiers = 96-101).
  2. **§2 `Graveyard`/`Sewer` — four factual errors, now censused.** A
     full `(CanUse, Menu)` grouping of all 91 base + 26 expansion
     building `Description`s found: there is **no** entry named `Sewer`
     and **none** whose ID is `BBN1` (the real entry is `ABN1`
     `Name="Sewers"`; `BBN1` is its `ImageIDBase` — so the doc's
     "surprising `BB` prefix on a HumanPlayer building" observation
     dissolves entirely); `Sewers` is `CanUse="HumanPlayer"`, not
     Monster; neither entry is `Menu="2"`, both are `Menu="3"`; and
     therefore **`BBJ1` `Graveyard` is the ONLY Monster-owned
     `Menu="3"` building in the base game — one exception, not two —
     with zero in the expansion.**
  3. **Third error found by the same census, not previously flagged:**
     §2's claim that buildings use `Menu` values "0/1/2/3, a genuinely
     different value range" from Characters' "4/5/6/7/12/13" is wrong —
     **`Menu="12"` is used by 15 building entries** (13 base Monster
     props, plus expansion `ABA1` `Siege_Marker` and `BBs7`
     `sign_fancy_iron`). The ranges overlap, so the disjoint-range
     argument for "`Menu` is interpreted per-`subType`" collapses; that
     conclusion is now marked UNVERIFIED pending different evidence.
     `Menu="12"` looks like the decorative-prop bucket.
  `NEW_BUILDING_REQUIREMENTS.md` Step 1 and Step 2 updated to match.
- [x] **Owner play-knowledge Q&A pass** — 6 open items answered from
  direct game experience, written up as `TODO-New-Building-Requirements.md`
  §10 (3 CLOSED, 1 NARROWED, 2 REFRAMED/REFUTED, 1 new open item). Both
  deliverables updated. Headlines: **the building price formula is
  confirmed** (`Cost` × `Multiplier`^owned × 0.95 with a Blacksmith,
  validated by the owner's own in-game logging tests — this also resolves
  the long-open "what does `<Multiplier>` do" gap); **Palace is never
  built**, which explains its missing `Build` art and missing
  `birthScript2` in one stroke; **`RecruitDelay` is a real per-class
  recruit cooldown**. Two corrections: the numbered `Die` slots are
  **damage-state art, not collapse stages** (no visible collapse at 0 HP,
  but art changes as HP drops), and **the build menu has no visible
  categories**, so `Menu` is not a category field — observed ordering
  matches XML document order filtered by availability.
- [x] **§10.3's upgrade mystery RESOLVED — the mechanism is
  `$UpgradeAgentAttributes`.** `upgradescript` targets (`basic_upgrade`,
  `magical_upgrade`, `palace_upgrade`/`2`) live in
  `GPL/Building_Births.gpl` + `mx_` twin. The human path is: click →
  `building_upgraded` → `upgradescript` → `basic_upgrade` queues onto
  `palace's "buildings_waiting"` → worker raises HP → at max HP
  `BuildingReachedMaxHP` calls `$UpgradeAgentAttributes`, which is where
  tier benefits land. That primitive has only 2 shipped call sites, and
  **no shipped code uses `$ChangeUnitType` for upgrades.** The owner had
  already found this for one building — his mod comments the call out on
  the Rogues' Guild branch citing the exact poison symptom. Why it felt
  unfixable: `$ChangeUnitType` leaves the agent inconsistent and
  `$UpgradeAgentAttributes` repairs it (his comment: game "will crash
  after a few seconds" without it), so that approach forces a choice
  between crashing and unlocking early. Confirmed negative: resetting
  `#ATTRIB_currentstagebuilt` does NOT re-gate content. Written up in
  `GPL_MODDING_GUIDE.md` §2.
- [ ] **Test the indicated upgrade fix in the `Dwarfeh_AI` mod** — drop
  `$ChangeUnitType`, call `$basic_upgrade(building)` instead, and let
  workers plus `BuildingReachedMaxHP` complete it. Follows from the
  shipped call graph but is UNTESTED; would also pick up the advisor
  sound, chat message and Guardhouse guard-thread restart for free.
- [ ] **NEW (from §10.5): render the numbered `Die`/damage slots to
  confirm they hold progressive damage art.** Extract setIDs 96-103 for
  Inn (`ABF1`, 8 slots) and a Marketplace tier (`ABH1`, 6 slots) as PNGs
  and compare visually. Doable on this machine with `sprite_extractor.py`;
  would upgrade §10.5's reframe from play observation to confirmed.
- [x] **§10.7 RESOLVED — Ballista Tower requires a completed Dwarven
  Settlement, and the whole exe-side tech tree is now captured** in
  `TODO-New-Building-Requirements.md` §10.8. The owner had already
  reverse-engineered it into his AI mod (`canBuild()` +the `build_*` flag
  block in `custom_rules.gpl`); his from-memory account and his code
  agree. Prerequisites: Gnome_Hovel = palace L1; Dwarven_Settlement =
  completed Blacksmith **L3** + palace L2; Elven_Bungalow = completed Inn
  + Marketplace + palace L2; Ballista_Tower = completed
  Dwarven_Settlement. Exclusivity groups (none of it data-driven): one
  race only; at palace L2 one deity group of Agrela+Dauros /
  Krypta+Fervus / Krolm; at palace L3 Helia **or** Lunord, and neither if
  Krolm was taken. Explains why source reading never found it and why
  shipped GPL keeps special-casing Dwarven_settlement alongside
  ballista_tower. **Owner correction applied on top:** deity exclusivity
  is a **mutual lockout, not a forced choice** — the engine happily lets
  you own conflicting temples (freestyle can even hand you two
  conflicting factions), but owning e.g. both Agrela and Fervus temples
  means you can build **no further buildings of either faction**. Both
  branches deadlock. Demolishing the conflicting temples is the way out,
  which is why the AI calls `$destroyBuildingsInList()` on the losers —
  purposeful un-deadlocking, not housekeeping.
- [ ] **In-game tests for the deity lockout** (from §10.8's correction):
  does the lockout key on the conflicting temple merely existing, or on
  it being completed/alive? Does a partially-built or `$disableunittype`d
  conflicting temple still deadlock? And is the palace-3
  Krolm-vs-Helia/Lunord rule the same lockout mechanism or a separate
  gate? Route to `TODO-GameTests.md`.
- [ ] **Ghidra (now well-specified): find the exe prerequisite table.**
  Target the rule gating `Ballista_Tower` on `Dwarven_Settlement` — the
  simplest single-dependency case in the tree — then check whether the
  table is data-addressable at all. If it is, new buildings could join
  the prerequisite system. Route to `TODO-Ghidra.md`.
- [x] **Minimap question RESOLVED for authoring purposes** (§10.10).
  Minimap markers are engine-drawn generically from faction/team colour,
  **not** from a per-unit `Minimap` ImageSet: only **28 of 380** IMAG
  records have setID 300 (18 heroes, 4 `MV*`, 3 `AR*`, and among buildings
  only the 3 Palace tiers), yet everything else still appears on the
  minimap, and the owner reports non-distinctive faction-coloured blips
  for heroes and buildings alike. Kills the "downscaled ImageSet"
  hypothesis. **A new building should author no minimap art.**
- [ ] **Open remainder of §10.10: what do the 28 `Minimap`-set records use
  it for?** Dumping the Palace's and several heroes' setID-300 descriptors
  was inconclusive — all report `width: 0, height: 0` with an implausible
  `frame_count`, but that was read with
  `parse_directional_frame_descriptor()` and `Minimap` is presumably
  non-directional, so **the parse is untrusted and must not be cited as
  evidence of empty art**. Needs a non-directional descriptor reader (this
  machine) or an in-game A/B check on the Palace marker.
- [ ] **Confirm GPL field-name case sensitivity.** The mod has a live
  example: it reads `palace's "build_Krolm"` while declaring
  `build_krolm`. The wider codebase implies case-insensitive matching
  (`$disableunittype`, `#CheckTitles`), but it is not actually confirmed
  and this is a cheap compile/runtime test.
- [ ] **Minor cleanup in `TODO-New-Building-Requirements.md` §3** — the
  `birthScript` passage has an unfinished self-correcting sentence that
  reads like a mid-edit artifact ("**Confirmed real exception in the
  shipped data:** `Palace3`, `Rogues_Guild2`… — actually every level-2/3
  tier entry…"). Its conclusion (presence universal, target varies) is
  clear and correct, so this is prose repair only, not a factual fix.

### GPL / Gameplay Logic Deep Dive
- [x] First consolidation done — `GPL_MODDING_GUIDE.md` created,
  companion to `CAM_MODDING_GUIDE.md` for gameplay mechanics (state
  machine, building lifecycle, visit/purchase systems, guild life,
  economy, guard spawning, intent system, death/gravestones, orphaned
  content). 9 topics fully cited with file/function/line references.
- [x] Topic 10 done — building visit-system deep dive, full depth: every
  remaining `Visited_Script` function (`Upgrade_Equipment`,
  `Enchant_Equipment`, `Library_Visited`, `GuardHouse_Visited`,
  `Inn_visited`, `Fairgrounds_Visited`, `Hall_Of_Champions_visited`,
  `Poison_Weapons`, `Gambling_Hall`, `Brothel`, `Gardens_visited`)
  individually traced in `GPL_MODDING_GUIDE.md` §3. Also confirmed the
  researchable-item gate-then-purchase pattern for Library/Blacksmith (in
  addition to Bazaar) — but NOT universal, several purchasable items have
  no unlock step at all. Hall of Champions' `HallOfChampions_Bounty_Cost`/
  `Period` were read in full but have zero GPL call sites — what
  exe-side code (if any) calls them is still open (see
  `TODO-Ghidra.md` Verification Tasks).
- [x] Topic 11 done — systematic orphaned-content sweep: every
  entity-shaped IMAG prefix (`AB`, `AV`, `BV`, `BB`) extracted from both
  `Data/maindata.cam` and `DataMX/mx_maindata.cam` and cross-checked
  against every `M_Buildings.xml`/`MX_Buildings.xml`/`M_Characters.xml`/
  `MX_Characters.xml` `ID=`. Result: Zoo remains the only genuine orphan
  (real sprites + real GPL logic + no XML wiring) — confirms rather than
  overturns the earlier opportunistic finding. Two unmatched `AV` IDs
  found (`AVn8`/`AVn9`) don't meet Zoo's bar (no GPL refs, same shape as
  already-wired selection-indicator sprites).
- [x] Topic 12 done — re-verified `.kiro/steering/majesty-modding.md`'s
  Petrification System description (a shipped doc that was previously
  assumed correct, not re-checked) against real GPL/XML source. 4 of 6
  claims confirmed exactly; 2 corrected — and one of those two corrections
  was itself corrected again after the fact (kept visible, not
  overwritten): the sub-agent flagged "UNVERIFIED how the base game
  invokes Petrify_Begin," but the user (an experienced modder) identified
  the real mechanism — base Petrify is cast directly from the Temple to
  Dauros building's own panel (`DialogID="AP05"`), unlocked at Temple
  Level 3, a "building-cast spell" pathway this project's docs hadn't
  previously distinguished from hero-`AllowedSpells`/monster-attack-spell
  casting, which is exactly why a source-only grep found nothing. The
  Level-3 unlock's own mechanism is still genuinely UNVERIFIED (no XML/
  GPL/`.dat` field found) — a correctly-scoped Ghidra candidate, tracked
  in `TODO-Ghidra.md`'s "Low Priority: Temple-to-Dauros Level-3 Petrify
  Unlock Mechanism" section. The "AI skips petrified units via IsFrozen" claim (the
  other correction) still has zero matching call sites in
  `DecisionTrees/`, unaffected by this update. All corrections visible in
  the steering doc and `GPL_MODDING_GUIDE.md` §11, none silently
  overwritten.
- [ ] Remaining work tracked in `TODO-GPL-Deepdive.md` — the investigation
  backlog is now empty (hero decision tree pass = Topic 15, quest rules
  pass = Topic 16, both done). What's left is the UNVERIFIED carry-over
  list, split by the tool each item needs: engine-side primitive
  semantics → `TODO-Ghidra.md` "Priority 7"; one-test-each language/data
  questions → `TODO-GameTests.md`; and a "writer found, reader not found"
  set that needs more source reading outside `Rules/` (in `TaskModules/`,
  `DecisionTrees/`, `*_Births`/`*_Deaths`).
- [x] Topic 13 done — building-unlocked "guild skill" castable abilities
  (Rage of Krolm / Call to Arms), both sub-questions resolved (see
  `GPL_MODDING_GUIDE.md` §12). **Correction after user input (kept
  visible, not overwritten):** the original framing treated "how is
  Rage of Krolm/Call to Arms triggered" as an open question of the same
  class as Petrify's genuinely-unresolved trigger gap — the user
  confirmed directly both are ordinary button clicks inside their own
  guild's building panel, the same trigger CLASS as Petrify's AP05
  button, not a separate mystery. **Q1 (unlock/lock):** with the trigger
  class confirmed, only the exe-side click-dispatch code remains open
  (same class of gap as `TODO-Ghidra.md` Priority 3.4's research-item
  click dispatch, not a new mechanism). Genuinely new finding:
  `Temple_Krolm`/`Warriors_Guild` are both single-tier (no `UpgradeTo`
  chain), so this can't be a Level-3-style tier gate the way Petrify's
  is — confirmed structurally different mechanisms, not the same gate
  reused. Destruction/revocation behavior no longer needs Ghidra first —
  moved to an in-game test (`TODO-GameTests.md`'s "Guild Skill Panel
  Persistence") since the likely mundane explanation (button lives on
  the building's own panel, so losing it just removes panel+button
  together) is directly testable without decompilation. **Q2
  (moddability):** confirmed `DoRageOfKrolm`/`DoAssembly` are plain
  callable GPL functions with no base-game "spell registry" anywhere
  (`Dwarfeh_AI_Spells.gpl`'s `canCast`/`castSpell` wrapper is a from-
  scratch mod invention, not a base-game pattern) — a modder can call or
  clone these with full confidence, but making a NEW one
  player-triggerable from a building panel hits the same
  exe-hardcoded-panel wall as Petrify. Cross-referenced, not duplicated,
  with `TODO-New-Building-Requirements.md`.
- [x] Topic 14 done — shared primitive catalog: the effector system as
  its own topic (`GPL_MODDING_GUIDE.md` §13) plus a deliberate sweep for
  any other primitive recurring across 3+ unrelated systems (§14 —
  `$ListObjects` flag vocabulary, `$AdjustAttribute` vs
  `$MagicalAdjustAttribute` as a cosmetic-only difference, `$PerformAction`,
  the random helpers, `$NewThread` vs `$RunThread`). Candidates with too
  little spread were discarded rather than padded in.
- [x] Topic 15 done — hero class decision tree pass: all 15 base-game
  classes read and compared (`GPL_MODDING_GUIDE.md` §15). Universal vs.
  class-specific module calls confirmed, the `chance` parameter's meaning
  pinned down from source, aggression/exploration spread tabulated, and
  the one real branching mechanism traced (`check_nearby`'s per-hero
  `"evaluationscript"` pointer). Which class maps to which
  `*_eval_nearby` implementation is still UNVERIFIED — no assignment site
  in the `.gpl` tree.
- [x] Topic 16 done — **quest rules pass COMPLETE (Batches A-G)**, which
  was the deep dive's last un-investigated area. All 15 files across
  `GPL/Rules/` and `GPLMx/Rules/` read; findings in
  `GPL_QUEST_RULES_REFERENCE.md` §16-§22 (construction/victory conditions,
  demo/random/special events, quest actives, the three expansion quest
  files, and the base epic-quest helper library). Each batch ends with a
  "recombination only" list so no file needs re-reading. Notable results:
  the special-event and victory-condition dropdowns turned out to be
  plain CAM `STRT` data (quest-distributable, no exe patch — superseding
  an earlier "needs an exe/UI change" verdict), the post-victory
  difficulty-tier system is base-only with no runtime difficulty input,
  and `epic_quest_scripts.gpl` yielded a 17-function reusable-helper
  catalogue the rest of the tree was already calling into blind. One
  shipped defect documented so nobody clones it
  (`Setup_High_Level_Members` writes `#ATTRIB_StartedwithThisUnit` to the
  guild building instead of the hero; harmless only because nothing reads
  that attribute).
- 10 confirmed findings with citations so far: building visit-script dispatch
  is per-building-family not unified (Shop_Visited vs Bazaar_Visited etc.),
  Mausoleum's `.dat` Visited_Script doesn't drive its real revival mechanic,
  Zoo is orphaned/unreachable content (now confirmed via a systematic sweep,
  not just opportunistically), `check_rewards()`'s hero-AI
  dispatch is a closed set (only "flag_attack"/"flag_explore" titles are
  ever scored), the `ActiveScript`/`BackScript`/`TaskName` mechanism is a
  GPL-side (not engine-builtin) cooperative timer/function-pointer relay,
  `birthscript`/`birthScript2` are a sequential birth→completion chain
  (only `birthscript` is engine-invoked from `NewUnitInit`; `birthScript2`
  is only ever reached through other GPL birth/completion functions), not
  two parallel setup scripts as originally guessed, the `upgradescript`
  split (`basic_upgrade` = hero/peasant-labor-driven, reuses the same
  construction queue as fresh builds; `magical_upgrade` = a genuinely
  different self-contained timer/tick mechanic, no labor involved) is
  confirmed real (not a false analogy), `Magical_build_rate` is a
  per-building-instance (expansion-only) tunable used by multiple
  buildings, not just Sorcerer's Abode, and the building revenue system
  (`RevenueScript`/`Revenue_Amount`/`Revenue_Time`) is a shared start
  mechanism (one `$NewThread` at building birth) but NOT a uniform
  mechanic — only 6 buildings ever set it (Marketplace 1-3, Fairgrounds,
  Inn, Royal_gardens; identical set in base and expansion), each with a
  structurally different payout function, `$Give_Gold` only fills a
  per-building gold pool that stays inert until a tax collector ferries
  it home, and Palace's own passive income is a fully separate
  `$AdjustPlayerData`-based mechanism with no call relationship to
  `RevenueScript` at all. Full detail + line-level citations in
  `TODO-GPL-Deepdive.md`.
- A running list of "Generated Research Questions" (the GPL-logic
  counterpart to every `CAM_MODDING_GUIDE.md` task recipe, e.g. what
  actually invokes a spell's `GPLFunction`, whether `AllowedSpells`
  mismatches fail silently) is tracked there — each must be answered with
  a citation or explicitly marked UNVERIFIED/UNKNOWN.
- Also tracked there: a "Candidate Topics" list of pattern-spotted but
  UNVERIFIED leads (e.g. guard spawning, guild Lived_In_Script, the Intent
  system, Krypta/Agrela revival) — none are exe/Ghidra work, all need
  citation-backed investigation before being promoted to confirmed
  findings. (The ActiveScript/BackScript/TaskName state machine, the
  birthscript/birthScript2 split, and the building revenue system have
  since moved from this list into the confirmed findings above.)

### SMNU Panel Compiler
- ✅ `smnu_format.py` — structured parser/writer, byte-perfect roundtrip on all
  169 real panels (base + expansion), 7 unit tests passing (SMNUResearch/)
- ✅ `smnu_compiler.py` — compiles Panel+strings to SMNU+STRT via str_tool.py,
  validates STRT string-index refs at compile time, byte-perfect on 168/169
  real panels (1 known data quirk — GDB4, see below)
- ✅ `cam_writer.build_cam_from_sections()` + `smnu_compiler.build_textdata_cam()`
  — packs compiled SMNU+STRT panels into a fresh quest CAM from scratch.
  Verified byte-perfect end-to-end (real panel -> compile -> pack -> read back).
  9 tests passing (SMNUResearch/test_smnu_compiler.py)
- Deferred: XML front-end for `smnu_compiler.py`. Only worth building if
  modders other than us are authoring panels directly (same rationale as
  gplbcc.exe existing for GPL). We drive the Panel/Widget/Property
  dataclasses from Python directly for now. See SMNUResearch/FUTURE_TODO.md.
- [ ] **Game machine: validate compiler output loads in-game** — the new
  smnu_format.py/smnu_compiler.py work is committed to Python-level
  byte-perfect verification only; nobody has confirmed the engine accepts
  a tooling-generated CAM at load time. See TODO-GameTests.md "SMNU Panel
  Override — Passthrough Test" for the concrete test.
- [ ] Ghidra: confirm GDB4's 2 out-of-range STRT refs are dead/unreachable code
  (see TODO-Ghidra.md Priority 3.5, SMNUResearch/FUTURE_TODO.md "Known Data Quirk")
- [ ] Ghidra: re-derive research item click dispatch mechanism (control_id
  registration/routing) via decompilation — currently only confirmed via an
  earlier binary-patch experiment, not disassembly. Determines whether a new
  research/purchase button (SMNUResearch/FUTURE_TODO.md Priority 3.6) needs
  an exe patch. **Bumped to next-up in the Ghidra queue** (ahead of its own
  numeric order) since it gates the most other open work — see
  TODO-Ghidra.md's "Work Order" note and Priority 3.4.
- ✅ Confirmed in `PanelTest_Quest`: widget insertion into an existing panel
  works end-to-end (5th widget on MX03 rendered/functioned), but forward
  sub-panel navigation is exe-patch-only — no data-only action code/target
  combo works except return-to-parent (8013). Blocks multi-page research
  panels until TODO-Ghidra.md Priority 1 lands — **in progress, paused
  when the Ghidra machine ran out of monthly tokens, resume first.**
  (see SMNUResearch/FUTURE_TODO.md "Building Sub-Panel Navigation")

### Landscape Objects (Trees/Rocks)
- [ ] Document which fractal refs (`xFel`, `xFer`, `xBBC`, etc.) produce which vegetation
- [ ] Consider adding "density" parameter to presets (bare, sparse, forested)

### tests/test_sprites.py — 12 Failing Tests (Stale After TILE v3 RLE Fix)
- ✅ Fixed. Root cause: PR merge `d9cb5e7` ("Fix TILE v3 RLE X as exclusive end")
  changed `sprite_extractor.py`/`sprite_injector.py`'s RLE X-position semantics
  (now exclusive-end, not relative/inclusive), but the merge did NOT update
  `tests/test_sprites.py`. Those tests were last touched in `04f0740` (before
  the fix) and still asserted the OLD encoding — that's why `TestDecodeTile`
  and `TestEncodeRow` (12 tests) failed while everything else (real-CAM
  roundtrip tests, `TestRealSprites`) passed. Not a regression in the actual
  encoder/decoder, purely stale test fixtures. Rebuilt the hand-crafted byte
  fixtures to use exclusive-end X values. All 147 tests across
  tests/QuestMapGenerator/SMNUResearch pass again.
- ✅ Added `.github/workflows/tests.yml` — runs the full `pytest` suite (all
  three testpaths, matrix on Python 3.10/3.12) on every PR targeting `main`
  and on push to `main`. Enable "Require status checks to pass" for the
  `test` job in GitHub branch protection settings for `main` so a merge like
  this can't land again without CI having run — currently branch protection
  is NOT configured, this needs to be turned on manually in repo settings
  (Settings → Branches → main → Require status checks to pass before merging).

---

## Lower Priority / Future

### Workshop Integration
- [ ] `--workshop` flag for quest_map_generator to create Workshop-ready packages
- [ ] Generate .mswproj files programmatically

### Ghidra: "Zoo" Building as a Possible EXE Expansion Point (low priority)
- [ ] Orphaned `ABn1/2/3` Zoo sprites + working GPL exist but are unreachable
  (no XML building definition references them). Investigate whether the exe
  still has dormant vtable/panel-factory plumbing for this DialogID family
  that could be repurposed as a "free" slot for other blocked exe patches
  (sub-panel nav, new building panel registration). (see TODO-Ghidra.md,
  "Low Priority: Investigate 'Zoo' Building")

---

## Completed

- ✅ Quest Map Generator: parse 37/37, roundtrip, create API, spawners, terrain, force layout, multi-kingdom, CLI
- ✅ GPL Knowledge Base: primitives, gotchas, patterns, debugging (in steering files)
- ✅ XML Schema: actions, overlays, buildings, research, particle systems (in CAM_MODDING_GUIDE + steering)
- ✅ MQXML/MMXML capabilities documented (steering file)
- ✅ TILE v3 RLE fix: exclusive-end X encoding (sprite_extractor + sprite_injector)
- ✅ CAM override mechanism: all resource types override via quest CAM (last-loaded wins)
- ✅ UUID generation: uuid.uuid4() is correct
- ✅ `<CAM>` tag works for sprites (IceSpell_Quest confirmed)
- ✅ Ice Barrage refactor: projectile + animated sprites + compact CAM (15KB)
- ✅ Expansion CAM support in sprite_extractor (3-section files)
