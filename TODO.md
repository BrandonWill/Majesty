# Majesty Modding Toolkit — Master TODO

See also:
- `TODO-Ghidra.md` — EXE patching / disassembly work (requires Ghidra machine)
- `TODO-GameTests.md` — In-game verification tests (requires loading the game)
- `TODO-GPL-Deepdive.md` — GPL/gameplay logic deep dive, building a
  `GPL_MODDING_GUIDE.md` companion to `CAM_MODDING_GUIDE.md`
- `IceSpell/TODO.md` — IceSpell mod-specific tasks
- `SMNUResearch/FUTURE_TODO.md` — Panel system research + tooling


---

## Active Work (this machine)

### GPL / Gameplay Logic Deep Dive
- [x] First consolidation done — `GPL_MODDING_GUIDE.md` created,
  companion to `CAM_MODDING_GUIDE.md` for gameplay mechanics (state
  machine, building lifecycle, visit/purchase systems, guild life,
  economy, guard spawning, intent system, death/gravestones, orphaned
  content). 9 topics fully cited with file/function/line references.
- [ ] Remaining work tracked in `TODO-GPL-Deepdive.md` — several
  UNVERIFIED items need Ghidra, several more are answerable from GPL/XML
  source alone but not yet done (full building visit-system depth,
  systematic orphaned-content sweep, hero decision tree pass).
- 9 confirmed findings with citations so far: building visit-script dispatch
  is per-building-family not unified (Shop_Visited vs Bazaar_Visited etc.),
  Mausoleum's `.dat` Visited_Script doesn't drive its real revival mechanic,
  Zoo is orphaned/unreachable content, `check_rewards()`'s hero-AI
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
  an exe patch. (see TODO-Ghidra.md Priority 3.4)
- ✅ Confirmed in `PanelTest_Quest`: widget insertion into an existing panel
  works end-to-end (5th widget on MX03 rendered/functioned), but forward
  sub-panel navigation is exe-patch-only — no data-only action code/target
  combo works except return-to-parent (8013). Blocks multi-page research
  panels until TODO-Ghidra.md Priority 1 lands.
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
