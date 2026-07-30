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

## Target Output — DONE, see `NEW_HERO_REQUIREMENTS.md`

The literal checklist this file exists to produce has been written:
`NEW_HERO_REQUIREMENTS.md` (workspace root). It's the actual deliverable —
read that file for the step-by-step "what to do" answer. This file
(`TODO-New-Hero-Requirements.md`) stays as the research/evidence backing
each checklist item, and as the place to record any further findings that
should update the checklist (e.g. if the recruitment gaps in §5 get
resolved via Ghidra work, update both this file's §5/§6 AND the
corresponding item in `NEW_HERO_REQUIREMENTS.md`'s Step 5).

**Still-open research that would update the checklist if resolved (see
§6 "Known Gaps" for full detail, and `TODO-Ghidra.md` for the Ghidra-scoped
items specifically):**
- The exe-side Recruit button handler (`8009` on `AP24`) has never been
  independently Ghidra-decompiled — only the general per-building vtable
  dispatch architecture is confirmed (via a different handler code,
  `8851`). Add as a scoped `TODO-Ghidra.md` item (see that file's Priority
  3.4 for the sibling research-button-click task this would extend).
  **If resolved, update:** `NEW_HERO_REQUIREMENTS.md` Step 5d.
- Whether `check_strays` ever re-fires after a guild's initial birth
  (only confirmed to run once, at birth) — determines whether a guild can
  passively adopt strays that appear on the map after construction, not
  just ones present at that exact moment. Answerable from GPL source
  alone (grep every `$NewThread`/`$RunThread` call site involving
  `check_strays`'s enclosing function), no Ghidra needed. **If resolved,
  update:** this file's §5 item 1/2, and `NEW_HERO_REQUIREMENTS.md`
  Step 5d.
- Whether `Hero_Generator` works correctly on an ordinary (non-quest-
  scripted) guild if manually wired as `SpecialScript` at birth — only
  confirmed wired via specific quest `Rules/*.gpl` files. Empirically
  testable in-game without Ghidra: set it on a plain mod guild and watch
  whether heroes spawn on the timer. **If resolved, update:** this file's
  §5 item 1, and `NEW_HERO_REQUIREMENTS.md` Step 5d.
- Whether any guild besides Warriors_Guild has pre-defined-but-unused
  recruit button slots in its SMNU (the "exe toggles visibility" pattern)
  — would need extracting and reading every guild panel's SMNU via
  `smnu_analysis.py`, no Ghidra needed. **If resolved, update:** this
  file's §5 item 3, and `NEW_HERO_REQUIREMENTS.md` Step 5c.
- The hero `Cost` XML field's real consumer, and whether `RecruitDelay`
  is GPL- or exe-enforced — both would need either a targeted in-game
  test (change `Cost` on a shipped hero, observe recruit price) or Ghidra.
  **If resolved, update:** this file's §5 item 4, and
  `NEW_HERO_REQUIREMENTS.md` Step 5d.

## Required Coverage Areas

### 1. Sprite/Art Requirements (cross-reference CAM_MODDING_GUIDE.md,
verify with real examples via cam_reader.py/sprite_extractor.py — don't
just restate the guide's existing IMAG/TILE section, confirm it against an
actual hero's real data)

**Method:** extracted real IMAG records for 15 shipped base-game heroes
(`AVA1` Adept, `AVB1` Barbarian, `AVC1` Cultist, `AVD1` Healer, `AVE1`
Monk, `AVF1` Paladin, `AVG1` Priestess, `AVH1` Ranger, `AVJ1` Rogue,
`AVK1` Solarus, `AVL1` Warrior, `AVM1` Warrior_of_Discord, `AVN1` Wizard,
`AVc1` Dwarf, `AVd1` Elf) directly from `Data/maindata.cam` via
`cam_reader.py`/`sprite_extractor.py`'s `parse_anim_set`/
`parse_directional_frame_descriptor`, using an exact-prefix record lookup
(see gotcha below). Full script preserved in git history of
`utility/test_decoder.py` for this pass.

**Gotcha found and fixed during this pass:** `sprite_extractor.py`'s
built-in `find_record()` does a **case-insensitive** prefix match. This
causes a false collision between `AVN1` (Wizard, uppercase N) and `AVn1`
(an unrelated `selection_ring` UI overlay, lowercase n) — two genuinely
different IMAG records. Any future investigation script must use an
exact-case prefix match, not `sprite_extractor.py`'s default, or hero
lookups by ID will silently resolve to the wrong record.

- [x] Which animation sets are MANDATORY vs optional for a hero
  specifically. **Confirmed by direct extraction across all 15 heroes:**
  `Walk`, `Stand`, `Attack`, `Cast`, `Special`, `Die` (setID 96 only —
  see 8-directional finding below), `Dead`, `Minimap`, `Hotspot`,
  `Interface` are present on **every single hero checked, zero
  exceptions** — treat these as mandatory. `Carry` is present on exactly
  3 of the 15 (`AVH1` Ranger, `AVJ1` Rogue) plus `Dwarf`'s `setID_145`
  entry — i.e. only classes that pick things up/carry items — treat
  `Carry` as **optional, class-dependent** (item-interaction heroes only).
  `Recoil`/`Damage`/`Sel-Underlay`/`Sel-Overlay` were **not found on any
  of the 15 heroes checked** — either genuinely unused by heroes or a
  gap in this pass's coverage; **UNVERIFIED** whether any hero anywhere
  uses them (not exhaustively checked against all 32 base-game
  `AV*`-prefixed records, only the 15 sampled).
- [x] Frame dimension/hotspot conventions — **no fixed canvas size.**
  Confirmed by extracting Walk-set width/height/hotspot for all 15
  heroes: sizes range from 8×9 (Healer/Elf) to 16×11 (Wizard), hotspots
  vary independently per hero (e.g. Adept `(-12,-12)`, Paladin
  `(-11,-18)`, Warrior_of_Discord `(-17,-18)`). Each hero's frame
  dimensions and hotspot are self-contained per-direction-block data —
  a new hero can use whatever canvas size its actual art needs.
- [x] 8-directional requirement — **confirmed for Walk/Attack/Cast/
  Special: exactly 6 of the 8 direction slots are ever populated (slots
  2–7; slots 0–1 are always empty)** across every hero and every one of
  those 4 animation-set families checked. This is a genuine finding, not
  an assumption — the frame-descriptor parser reports populated slot
  indices directly. **The "Die has more variants than 8" claim from
  earlier research is FALSE for heroes** — every one of the 15 heroes
  checked has **only setID 96 ("Die", the base/first Die variant)** with
  6 populated direction slots, identical in shape to Walk/Attack. A
  workspace-wide scan of every IMAG record in `maindata.cam` for setIDs
  97–103 (Die-2 through Die-8) found **zero hero (`AV*`) hits** — those
  setIDs are used exclusively by **buildings and monster lairs**
  (`ABB1` Ballista Tower, `ABC1-3` Blacksmith, `ABD1` Fairgrounds,
  `ABE1/2` Guardhouse, `ABJ1-3` Palace, all Temple tiers, `BBA1` Animal
  Den, `BBB1-4` Dark Castle, etc. — confirmed via full-CAM scan). The
  "more Die variants" note in earlier research was about **buildings**
  (multi-stage collapse animations), not heroes — a hero needs only the
  single `Die` (setID 96) set with 6 populated directions.
- [x] Palette constraints — **not re-derived, cited from existing docs.**
  `CAM_MODDING_GUIDE.md` and `.kiro/steering/majesty-modding.md` already
  confirm existing SPLT entries are read-only (modifying them crashes
  the game), but a quest/mod's own CAM file can ship **brand-new** SPLT
  entries of its own (`CAM_MODDING_GUIDE.md`'s "IMAG Writing Notes for
  Mod CAMs" — the WrathOfKrolm example ships 12 of its own SPLT entries
  in `MDL1_maindata.cam`). A new hero can therefore either reuse an
  existing base-game palette (no palette shipped, sprite quantized to
  match) or ship its own new palette entry inside its own quest/mod
  `maindata.cam` — both are valid, confirmed by the existing quest data.
- [x] Minimap icon requirements (setID 300) — **confirmed mandatory.**
  Every one of the 15 heroes checked has a `Minimap` (setID 300) entry
  with zero exceptions, consistent with the "always present" set above.
- [ ] What happens if a required animation frame is missing at runtime —
  **UNVERIFIED.** No GPL source, `.dat` comment, or engine-behavior note
  anywhere in the available SDK/GPL corpus describes the fallback
  behavior (silent skip, crash, placeholder frame). This would require
  either a Ghidra trace of the sprite-rendering code path or an in-game
  test with a deliberately-missing IMAG record — neither was done here.
  Do not assume "probably crashes" — mark explicitly unknown.

### 2. Unit XML Definition Requirements (M_Characters.xml / MX_Characters.xml)

**Method:** read the full `<Description type="Unit" subType="Character"
...>` blocks for all 15 heroes above plus `Cultist`/`Priestess`/
`Ranger`/`Rogue`/`Solarus` (`AVC1`/`AVG1`/`AVH1`/`AVJ1`/`AVK1`) directly
from `SDK/OriginalQuests/Data/M_Characters.xml`, side by side.

- [x] Full required-field catalog for `type="Unit" subType="Character"`
  with `CanUse value="HumanPlayer"`. **`<Engine>` block — present on
  every hero checked, zero exceptions:** `Info value="BlockGround"`,
  `CanUse value="HumanPlayer"`, `Menu value="6"`, `ImageIDBase`,
  `Attachment kind="Movement" type="Walk" ID="..."`, `DefaultSound`.
  **`<Game>` block — present on every hero checked:** `DialogID`
  (always `AP20` for playable heroes — see below), `Cost`, `Experience`,
  `MaxHP`, `SightRange`, `Speed`, `AttackRange min/max`, `RecruitDelay`,
  `Flags value="Heals"`, `Flags value="HasHPBar"`,
  `Flags value="CanHighlight"`, `HelpID`. **Sometimes omitted (real
  variation, not universal):** `AllowedWeapon`/`AllowedArmor` (present
  on melee/ranged classes with equipment slots; **absent** on Wizard,
  which uses `AllowedWeapon value="Staff"` actually — re-checked: only
  Priestess omits `AllowedArmor` entirely, being unarmored by design);
  `AllowedSpells` (absent on classes with zero spells — none of the 15
  sampled actually lack it entirely, every playable hero has at least
  one spell in this sample); `PrimaryStat`/`NameGenType` (present on all
  playable-hero entries, absent on non-recruitable Henchman-type
  `Character` entries like `AVb0` Veteran_City_Guard, which uses `Menu
  value="7"` instead — see Menu finding below). `WeaponBasicDamage`/
  `ArmorBasicDamage` appear only when the class actually has a weapon/
  armor slot (Priestess has `WeaponBasicDamage` but no
  `ArmorBasicDamage`, consistent with no `AllowedArmor`).
- [x] `Menu value="N"` — **confirmed via cross-referencing every `Menu`
  value in `M_Characters.xml` against the entity it's attached to:**
  `Menu="6"` = playable `HumanPlayer` hero (Adept through Elf/Dwarf/
  Gnome, all 16+ recruitable classes, zero exceptions). `Menu="5"` =
  `Monster`-CanUse creature (Evil_Oculus, Dragon, Skeleton, etc.).
  `Menu="7"` = player-side Henchman/utility unit (City_Guard,
  Veteran_City_Guard, Caravan — non-recruitable-via-guild units spawned
  by the Palace/buildings directly). `Menu="4"` = unique/boss monster
  (Black_Phantom, Url_Shekk, Dirgo). `Menu="12"` = transient spell-effect
  "unit" (fire_strike, farseeing, lightning_bolt — these are actually
  spell hit-effects modeled as Character entries, not player-visible
  heroes). `Menu="13"` = non-gameplay marker (event_beacon). **For a new
  player-recruitable hero, `Menu value="6"` is required** — it's the
  single consistent signal separating real heroes from every other
  Character-typed entity in the file. Whether other Menu values also
  "work" for a hero (i.e. don't crash, just misfile it in some UI list)
  is **UNVERIFIED** — no test was done setting a hero-shaped XML to
  `Menu="5"`; only the correlation from existing shipped data was
  checked, not exe behavior under a wrong value.
- [x] Stat fields — **full list observed across all 15+ heroes' complete
  `<Game>` blocks:** `DialogID`, `Cost`, `Experience`, `MaxHP`,
  `SightRange`, `Speed`, `AttackRange min/max`, `Vitality`, `Artifice`,
  `WillPower`, `Intelligence`, `Strength`, `MagicResistance` (sometimes
  omitted — absent on Adept/Barbarian/Healer/Monk in the sample, present
  on Paladin/Dwarf/Elf/Cultist etc. — appears to be class-dependent, not
  universal), `Attack`, `RangedAttack` (only on ranged/hybrid classes —
  Cultist, Ranger, Rogue, Dragon-type monsters), `Parry`, `Dodge`,
  `WeaponBasicDamage`, `ArmorBasicDamage` (see above — equipment-slot
  dependent), `RecruitDelay`, `PrimaryStat`, `NameGenType`, `Flags`
  (multiple), `HelpID`, `AllowedWeapon`, `AllowedArmor`, `AllowedSpells`.
  Not every field appears on every hero — `MagicResistance`,
  `RangedAttack`, `WeaponBasicDamage`/`ArmorBasicDamage` are
  class-dependent, the rest are universal across the sample.
- [x] `AllowedSpells` — **mechanism confirmed:** it is a pure XML-side
  declaration (`<AllowedSpells><Spell ID="N" Value="spell_name"/>...
  </AllowedSpells>`) — grepping the entire GPL corpus (base + expansion)
  for the literal string `AllowedSpells` returns **zero matches**; no
  GPL function reads it directly. Spells reach a hero through this XML
  grant list (engine-side, consumed at spawn/load to populate the
  hero's spell-cast options) **and independently** via runtime
  `$LearnSpell(agent, "spell_name")` GPL calls (confirmed in
  `Hero_Births.gpl`/`mx_Hero_Births.gpl` — e.g. the "Hooligan" quest
  hero gets `Power_Shock`/`Flame_Shield`/`Teleport`/`Resist_Magic` via
  `$LearnSpell`, not via `AllowedSpells`). These are two independent
  grant paths, not one funneling into the other. **`CharacterLevel`
  (on the Action XML, not the Character XML) is a separate, engine-
  enforced learn-gate** — confirmed real example: `teleport_short`
  (Adept's only spell) has `<CharacterLevel value="4"/>`; its GPL-side
  `ValidationScript` (`teleport_short_check`, in `Spells.gpl`/
  `mx_Spells.gpl`) is a **separate, additional** cast-time gate — the
  two are not the same mechanism. **UNVERIFIED:** the exact failure mode
  if `AllowedSpells` references a spell name with no matching Action XML
  entry, or if a hero's level never reaches a listed spell's
  `CharacterLevel` (silently never learns it vs. some other visible
  failure) — no source location describes this, would need an in-game
  test with a deliberately-broken `AllowedSpells` entry. This carries
  forward the same open question flagged in `TODO-GPL-Deepdive.md`
  (not independently resolved there either — confirmed by checking, that
  file contains no `AllowedSpells` mentions).
- [x] `Attachment kind="Movement"` — **DMOV classes catalogued from real
  hero XML, heroes vs. monsters compared directly:** heroes in this
  sample use only ground-walk classes: `Class 1` (Barbarian, Monk,
  Warrior, Warrior_of_Discord, Dwarf, Wizard), `Class 2` (Healer,
  Paladin, Rogue, Solarus), `Class 3` (Cultist, Ranger, Elf), `Class 5`
  (Adept — a caster-specific ground class).
  **No hero in the sample uses `Fly`/`Large Flyer`/`Small Flyer`** —
  those are confirmed monster-only in this data (Dragon uses `Fly` +
  `Large Flyer`; Roc/Giant_Eagle uses `Small Flyer`). This is consistent
  with heroes being ground units by design in this game, but
  **UNVERIFIED** whether a flying `Attachment` would actually be
  rejected for a `CanUse="HumanPlayer"` hero or would just work
  unexpectedly — no flying hero exists anywhere in shipped data to
  confirm either way, and no GPL/engine source states a restriction.
- [x] Inventory/equipment slot requirements — **confirmed XML-declarative
  at the surface, but the actual slot mechanics are engine-side, not
  GPL-side.** `AllowedWeapon`/`AllowedArmor` (the XML fields naming
  which equipment category a hero can use, e.g. `Staff`, `Longsword`,
  `Leather`, `Plate`) are **never read by any GPL function** — grepping
  the entire corpus for `AllowedWeapon`/`AllowedArmor` returns zero
  hits. GPL instead reads **derived runtime attributes** —
  `#ATTRIB_WeaponTypeIndex`, `#ATTRIB_ArmorTypeIndex` (gate whether a
  hero even considers upgrading, in `Purchase_Equipment.gpl`'s
  `Purchase_Equipment` function), `#ATTRIB_Weapon_Struct_Bonus`/
  `#ATTRIB_Armor_Struct_Bonus`/`#ATTRIB_Weapon_Magic_Bonus`/
  `#ATTRIB_Armor_Magic_Bonus` (current enchant/upgrade level, read/
  written by `BlackSmith_Check`/`WizGuild_Check` in the same file).
  **The XML→attribute derivation itself (how `AllowedWeapon
  value="Staff"` becomes a nonzero `#ATTRIB_WeaponTypeIndex` at
  runtime) is exe-side and UNVERIFIED from GPL/XML source alone** — no
  GPL code performs this translation, so it must happen in the engine's
  XML loader. A new hero needs `AllowedWeapon`/`AllowedArmor` declared
  if it should be able to equip/upgrade gear via Blacksmith/Wizard's
  Guild visits; omitting both (like Priestess omits `AllowedArmor`)
  appears to be a supported, deliberate way to opt a class out of that
  equipment category, not a required field with a bad default.

### 3. GPL Requirements (cross-reference GPL_MODDING_GUIDE.md's existing
findings — don't re-derive what's already confirmed there, but DO verify
anything that guide left as UNVERIFIED and is now blocking this checklist)
- [x] Decision tree file — **confirmed a decision tree is just an ordinary
  compiled GPL source file, and the wiring point is NOT filename-based —
  it's `Hero_Data.dat`'s function-pointer fields.** Read `path.gplproj`
  (base game) in full: it lists every decision tree file
  (`DecisionTrees\Adept.gpl`, `DecisionTrees\Warrior.gpl`, etc.) as
  ordinary `source=` entries compiled into the SAME single
  `Bytecode.bcd` as everything else (buildings, monsters, low-level
  helpers) — there is no special decision-tree-specific compilation
  step or naming convention the engine enforces. The actual connection
  from a hero title to its tree is `Hero_Data.dat`'s `activeScript`/
  `basicscript`/`StartingScript` fields, which point at a **function
  name**, e.g. Adept's entry sets all three to `adept_tree` (defined in
  `DecisionTrees/Adept.gpl`). **A new hero CAN structurally reuse an
  existing class's tree function** — just point a new `Hero_Data.dat`
  entry's `activeScript`/`basicscript`/`StartingScript` at e.g.
  `warrior_tree` instead of writing a new file — this follows directly
  from it being a plain function-pointer assignment with no per-class
  registration elsewhere found. **UNVERIFIED:** whether the engine or
  any GPL code has hidden assumptions tying a specific tree function to
  exactly one hero title (e.g. via `thisagent's "title"` checks inside
  that tree) that would misbehave under reuse — not tested in-game, and
  a quick read of `Adept.gpl`'s tree body shows no such title check, but
  this wasn't checked for every tree function.
- [x] `prototype hero()` fields — **full list read directly from
  `prototype.gpl`'s `hero()` block (lines ~103–150):** `type`, `subtype`,
  `title`, `Original_type` (strings); `percentageHPretreat` (integer),
  `Enemy_estimation`/`self_estimation` (float); `Greed`/`Loyalty`/`Luck`
  (integer); `critical_chance` (integer); `resist_critical`/
  `Immune_to_poison`/`rangeIncrease`/`criticalIncrease` (boolean);
  `leader` (agent); `Counter` (integer); `destination` (coordinate);
  `special_splat` (string); `target`/`BackTarget` (agent); `taskname`
  (string — see GPL_MODDING_GUIDE.md §1 for its dual-purpose usage);
  `hostiles` (list); `Friend` (string); `num_followers` (integer);
  `Reborn_Counter` (integer — Healer-specific, see below);
  `Task_Number` (integer); `StartingScript`/`basicscript`/`backscript`/
  `activescript`/`evaluationScript`/`birthScript`/`IGdeathScript`/
  `deathScript`/`teleportScript`/`QuestScript` (function pointers);
  `home`/`palace` (agent, engine-set on recruit per the field's own
  comment); `Raider_respond` (boolean); `castingrange`/`PrimaryStat`/
  `num_picked_goodies`/`Upgrade_Armor_Chance`/`Upgrade_Weapon_Chance`/
  `Poison_Weapon_Chance` (integer); `Special_Boolean` (boolean,
  quest-specific per its own comment); `Enemytype`/`attack_action`/
  `cast_action`/`Pickup_Action`/`Idle_Action` (string). All fields are
  declared once on the shared `hero` prototype — every hero class gets
  all of them regardless of whether that class's `Hero_Data.dat` entry
  actually sets a value (unset fields keep GPL type defaults: empty
  string/0/FALSE/null agent).
- [x] Birth wiring — **full required-field catalog from reading all ~19
  `Hero_Data.dat` entries side by side, not just the death-related
  ones.** Fields present on **every playable hero entry, zero
  exceptions:** `type hero`, `subtype hero`, `title`, `original_type
  Hero`, `EnemyType`, `Idle_action`, `attack_action`, `Cast_Action`,
  `PrimaryStat`, `Friend`, `attacktype`, `castingrange`,
  `PercentageHPRetreat`, `enemy_estimation`, `self_estimation`,
  `Loyalty`, `Greed`, `Luck`, `Upgrade_Armor_Chance`,
  `Upgrade_Weapon_Chance`, `Poison_Weapon_Chance`, `evaluationScript`,
  `activeScript`, `basicscript`, `StartingScript`, `birthScript`
  (always `hero_birth` for playable classes — see below),
  `IGdeathscript` (see death section). **Sometimes present, real
  per-class variation, not universal:** `Pickup_Action` (Cultist,
  Ranger, Rogue, Wizard — item-interaction classes only, absent on
  Adept/Barbarian/Dwarf/Elf/Gnome/Healer/Monk/Paladin/Priestess/Solarus/
  Warrior/Warrior_of_Discord in the sample);
  `Immune_to_poison` (Cultist, Dwarf, Warrior_of_Discord); `Num_Followers
  `/`Max_Followers` (Cultist, Priestess — controlled-monster-follower
  classes only); `criticalIncrease`/`critical_chance` (Barbarian,
  Warrior_of_Discord); `rangeincrease` (Ranger only);
  `Reborn_Counter` (Healer **only** — this is the field
  GPL_MODDING_GUIDE.md §8 references for self-resurrection eligibility).
- [x] Death handling — **cited from GPL_MODDING_GUIDE.md §8, not
  re-derived.** Confirmed against `Hero_Data.dat`: **the generic
  `gravestone()` function is genuinely the default for most classes**
  — 14 of the ~16 playable hero entries set `IGdeathscript gravestone`
  directly, confirming a new hero class does NOT need its own death
  function and can point straight at the shared `gravestone()`. The
  documented exception (`Healer` → `Healer_Death`, which
  conditionally routes to `gravestone()` only if its self-revival roll
  fails) is the only base-game deviation found in this pass, matching
  what §8 already documents — no new deviation discovered beyond what
  the guide already states.
- [x] GPL bytecode compilation and dataset wiring — **fully traced
  end-to-end for a NEW hero class specifically.** `SDK/OriginalQuests/
  GPL/path.gplproj` is the single project file listing every `data=`
  (`.dat`) and `source=` (`.gpl`) file that gets compiled together into
  ONE `Bytecode.bcd` via `Gplbcc.exe` (invoked by `MakeGPL.bat`,
  confirmed real command: `%GPLBCC% -in %1 -out %2 -stdout`).
  `Data/DataSets.xml` then loads exactly that one `Bytecode.bcd` under
  `<LoadGPL>` for every release classification (`MajestyCommonData`,
  `Rel0`, `Rel2`) — confirmed by reading the actual file, all three
  groups load the identical `Bytecode.bcd`. **For a new hero class added
  to the base game itself:** add `data="Hero_Data.dat"` entry (already
  present, just add the new `[HeroName] {Hero...} [end]` block inside
  it) and a new `source="DecisionTrees\NewHero.gpl"` line to
  `path.gplproj`, then recompile — this replaces the single shared
  `Bytecode.bcd`. **For a MOD/quest-scoped new hero (the realistic
  modder path, since base-game files aren't meant to be hand-edited):**
  the same mechanism applies at smaller scale — a mod's own `.gplproj`
  (e.g. `MyAI.gplproj`, confirmed pattern: `data="Game\mx_Hero_Data.dat"`
  + `source="custom_rules.gpl"`) compiles to the mod's own `.bcd`, loaded
  additively alongside the base game's `Bytecode.bcd` via the mod's
  `.mmxml`/`.mqxml` — this is the same "layered dataset" loading model
  `CAM_MODDING_GUIDE.md` documents for CAM files, just applied to
  compiled GPL bytecode instead. A mod's `Hero_Data.dat`-equivalent file
  can define entirely new hero titles this way without touching the
  base game's own `path.gplproj`/`Bytecode.bcd`.

### 4. Sound Requirements

**Method:** read the full `<Description type="Sound" subType="Standard"
...>` blocks for `Adept` (ID `AT01`), `Barbarian` (ID `BN01`), and
`Ranger` (ID `RR01`) side by side in `SDK/OriginalQuests/Data/
M_Sounds.xml`, and cross-referenced each hero's `DefaultSound` XML
attribute (in `M_Characters.xml`) against a matching `Sound`-typed
`Name=` entry.

- [x] What sound definitions/`Phase` entries are mandatory vs. optional.
  **Every hero's `Character` XML entry sets `DefaultSound value=
  "<HeroClassName>"`** (e.g. Adept → `DefaultSound value="Adept"`,
  confirmed matching a `Sound` Description with `Name="Adept"` — this is
  the wiring link between a hero and its sound set, a plain name-match,
  not an ID-match: the Character's `DefaultSound` string must equal the
  Sound Description's `Name` attribute, not its 4-char `ID`). **`Phase`
  IDs present on all 3 heroes checked, zero exceptions — treat as
  mandatory for a complete hero sound set:** `VFX_GO_COMBAT`,
  `VFX_FLEE_COMBAT`, `VFX_DECIDING`, `VFX_GO_REWARD`, `VFX_FIND_COOL`,
  `VFX_SPECIAL1`, `Death`, `VFX_GAIN_LEVEL`, `VFX_SEE_HOSTILE`,
  `Attack`, `Easter_Egg`. **Class-dependent, not universal:**
  `VFX_CAST_SPELL1` present on Adept (a caster) but **absent on
  Barbarian and Ranger** (both non-caster/limited-caster classes) —
  confirms this Phase is tied to whether the class actually casts
  spells, not a hard requirement for every hero. `GetHit` present on
  Adept and Ranger but **absent on Barbarian** — Barbarian's `Attack`
  phase reuses `HG13` directly as its hit-reaction cue instead of a
  separate `GetHit` phase (inferred from the `.dat`'s own structure,
  not from a GPL read — this specific substitution logic is exe-side
  and UNVERIFIED beyond "the field is simply missing"). `VFX_JIHAD`
  present as an empty/self-closing `<Phase ID="VFX_JIHAD"/>` on
  Barbarian with no `Wave` child at all — a valid-but-silent phase
  entry, distinct from omitting the phase entirely. `VFX_LEVEL_10` is
  present on all 3 but its exact trigger semantics were not traced into
  GPL — **UNVERIFIED** what specifically fires it beyond the field name
  suggesting a level-10 milestone voice line.
- [x] Combat/voice sound requirement for a genuinely NEW hero: **a new
  hero class needs its own `Sound` Description entry whose `Name`
  matches the hero's `DefaultSound` value**, with (at minimum, based on
  the "present on all 3 checked" set above) `VFX_GO_COMBAT`,
  `VFX_FLEE_COMBAT`, `VFX_DECIDING`, `VFX_GO_REWARD`, `VFX_FIND_COOL`,
  `VFX_SPECIAL1`, `Death`, `VFX_GAIN_LEVEL`, `VFX_SEE_HOSTILE`,
  `Attack`, and `Easter_Egg` phases, each pointing at a real `WAVE`
  entry name that must exist in a loaded CAM's `WAVE` section
  (`voices.cam`/`soundfx.cam` for base game, or a quest/mod's own CAM
  per `CAM_MODDING_GUIDE.md`'s CAM override rules). **UNVERIFIED:**
  whether omitting one of these "always present in the sample" phases
  causes a crash, a silent no-sound case, or some other exe-side
  fallback — no source describes missing-phase behavior, same caveat
  as the missing-sprite-frame question in §1.

### 5. Recruitment — How a Hero Actually Enters the Game (GENUINELY
UNRESEARCHED — this is the biggest gap, trace it fully, don't assume it's
"just like birth")

**CORRECTION (this section's original "recruit-click mechanism for
ordinary guilds has no GPL-side implementation at all" conclusion was
too strong — flagging per this doc's own evidence standard rather than
silently fixing it):** two real, confirmed, GPL-authored hero-generation
mechanisms exist that the original search missed entirely — but neither
is independently confirmed to be the literal "player clicks Recruit"
path, and the user's own experience does NOT confirm either one
specifically (see below), so don't overstate this correction either.

1. **`check_strays()`/`adopt()`** in `Building_Births.gpl` (base) /
   `mx_Building_Births.gpl` (expansion). `check_strays(thisagent,
   what_hero, player)` scans the map via `$ListObjects(thisagent, "hero",
   -1, strays, player, #insideOtherUnits)`, filters to the guild's
   `member_title` via `$listtitles`, keeps only heroes with no `"home"`
   set (`stray's "home" == $nullagent()`), and — while
   `GuildHasOpenSlots` allows it — calls `adopt(thisagent, stray)` on the
   closest one (player's own strays unconditionally; enemy-player strays
   gated by a `$randomnumber(100) > stray's "loyalty"` roll). `adopt()`
   pushes the hero onto `thisguild's "members"`, sets `stray's "home" =
   thisguild`, reparents the agent, resets `basicScript`, and sets the
   hero's player number to the guild's. Called unconditionally from
   `guild_birth` (`Building_Births.gpl` lines 415/419) and the dedicated
   `warriors_guild_birth`/`rogues_guild_birth` variants. **This mechanism
   ADOPTS an already-existing homeless hero found wandering the map — it
   does not itself create a new hero from nothing.**
2. **`Hero_Generator`** (`SDK/OriginalQuests/GPL/TaskModules/Buildings/
   Lair.gpl` lines 156-161, mx `mx_Lair.gpl` lines 182-189): a much
   simpler, direct-creation function — `If ($ListSize(ThisAgent's
   "Members") < ThisAgent's "Max_Members") $SpawnUnit(ThisAgent,
   ThisAgent's "Member_Title")` — spawns a brand-new hero of the guild's
   own `Member_Title` directly at the guild, gated only by member-count
   vs. capacity. Confirmed wired up as a guild's `SpecialScript` on a
   recurring `$NewThread` timer (30-90+ seconds, randomized) in several
   quest `Rules/*.gpl` files (`epic_quest_scripts.gpl`,
   `mx_Epic_Quest_Scripts.gpl`, `Quests_2.gpl`) — i.e. it's real,
   confirmed-wired GPL logic, but **quest-specific opt-in**, not
   something every guild runs by default (the base guild `prototype.gpl`
   comment explicitly frames `SpecialScript` as "quest-specific
   functionality... For instance, in Magic Ring, it runs
   Hero_Generator" — implying other quests could leave it unset).

**Neither mechanism is confirmed to be what the user actually did.**
Directly asked, the user clarified their Ratman-kingdom result came from
redefining the **Warrior** unit itself (sprites/stats/naming — the same
XML-redefinition approach this doc's §2 "Modify a unit's stats" already
documents) while leaving it recruited through the **existing, untouched**
Warriors_Guild pipeline. This means the user's result is actually
**consistent with, not contradictory to**, the original finding that the
literal panel-click gold-check-and-spawn step has no confirmed GPL
source — they never needed to touch or understand that step, because
they didn't change *how* recruitment works, only *what* gets recruited.
The corrected takeaway is narrower than first assumed: `check_strays`/
`adopt` and `Hero_Generator` are real, cited, confirmed-to-exist
mechanisms that add rigor to this section, but they should not be
presented as "the" recruit-click mechanism, and the original UNVERIFIED
gap (exactly what fires when a player clicks Recruit on an ordinary
guild panel) remains genuinely open. Retained below with this correction
prepended per the "don't silently drop retracted claims" standard used
elsewhere in this research (see `GPL_MODDING_GUIDE.md`'s "Retracted
Claims") — two corrections to the same claim, from two rounds of
follow-up, is itself worth leaving visible as an example of how
"asking the user directly" resolved an ambiguity re-reading source
couldn't.

- [x] How does clicking "Recruit" in a guild/temple panel actually create
  a new hero agent and add it to the player's roster? **Trace confirmed
  end-to-end on the GPL/data side. The exe-side click dispatch has a
  confirmed GENERAL ARCHITECTURE (Ghidra-verified for a different handler
  code) but no independently-confirmed disassembly for the Recruit
  handler code specifically — these are two different confidence levels,
  don't collapse them into one "UNCONFIRMED."**
  - **The general dispatch architecture IS Ghidra-confirmed** —
    `SMNUResearch/findings/exe_disassembly_results.md` shows actual
    disassembly (not just inference) proving that a widget's handler code
    triggers a call into a **per-building-class vtable method**, with
    each building's own compiled C++ handler containing the specific
    behavior (shown concretely for handler code `8851`/`0x2293`: `CMP
    EAX, 0x2293 / JZ open_panel`, per-building constants burned into each
    vtable slot). This is the confirmed System A action architecture
    (action ID + handler code → vtable dispatch) that
    `action_codes_decoded.md` catalogs entries for, including Recruit.
  - **What is NOT confirmed: the specific vtable handler for Recruit's
    handler code (8009) has never been independently Ghidra-decompiled.**
    `action_codes_decoded.md`'s decoded action table lists Action ID 75 /
    Handler Code 8009 = "Recruit" (found on `AP24`, Temple to Krolm) — a
    real, decoded-from-raw-SMNU-bytes catalog entry, not itself
    unconfirmed. But no one has traced what `AP24`'s specific `8009`
    vtable handler actually calls (a GPL function? `$SpawnUnit` directly?
    something else?) the way the `8851` handler was traced to
    `OpenPanelByName`. **It's a reasonable inference, not an independent
    confirmation, that Recruit follows the same architecture** — the same
    handler code `8009` is ALSO used for "Open spell list" (Action ID 83)
    and "Open visitors" (Action ID 69) elsewhere, meaning the
    Action-ID+Handler-Code PAIR (not the handler code alone) selects
    behavior, consistent with per-building-class dispatch — but this
    specific pairing's actual disassembly was not performed in any
    research reviewed here.
    `SMNUResearch/FUTURE_TODO.md`'s "Warriors Guild (AP52) Dynamic Panel
    Pattern" section separately confirms recruit buttons for multiple
    hero types (Warrior/Discord/Paladin) are **all pre-defined in SMNU
    simultaneously**, with the exe showing/hiding them at runtime based
    on which temples are built — i.e. the panel doesn't have one generic
    "recruit" button that changes its target hero type, it has one
    button per hero type, conditionally visible.
    `SMNUResearch/FUTURE_TODO.md`'s "Warriors Guild (AP52) Dynamic Panel
    Pattern" section separately confirms recruit buttons for multiple
    hero types (Warrior/Discord/Paladin) are **all pre-defined in SMNU
    simultaneously**, with the exe showing/hiding them at runtime based
    on which temples are built — i.e. the panel doesn't have one generic
    "recruit" button that changes its target hero type, it has one
    button per hero type, conditionally visible.
  - **Action code → GPL, confirmed via the closest real analog
    (Embassy, not a plain guild):** no base-game GPL function named
    literally "Recruit" exists anywhere in the corpus (grepped
    case-insensitively across all `.gpl` files, zero function
    definitions match). The clearest real, non-mod, engine-comment-
    verified example of a cost-gated hero-spawn triggered by a UI/timer
    event is `Embassy.gpl`'s `Embassy_Spawn` (`SDK/OriginalQuests/
    GPLMx/TaskModules/Buildings/Embassy.gpl`, expansion-only building):
    it reads a per-instance recruit cost off `#ATTRIB_EmbassyRecruitCost`
    (set by `Embassy_Init`, "When the ON button is pushed" per its own
    comment — i.e. genuinely UI-click-driven), checks
    `$GetPlayerData(Guild, "Gold") > heroCost`, deducts it via
    `$AdjustPlayerData(Guild, "gold", -heroCost, Type)`, then calls
    `$SpawnUnit(Guild, Type, $GetEntranceLoc(ThisAgent))`. This is a
    genuine "recruit" implementation, just not literally named that.
  - **For ordinary (non-Embassy) guilds, no comparable GPL-side
    cost-check function was found at all** — grepping the full corpus for
    a generic guild recruit-cost-check turned up nothing beyond
    `GuildHasOpenSlots` (a capacity check, not a cost check — see item 2).
    This strongly suggests plain guild recruitment's cost deduction and
    `$SpawnUnit` call happen **entirely exe-side** (the panel click
    handler itself does both the gold check/deduction and the spawn),
    with GPL only picking up the hero post-spawn via `hero_birth`/
    `Generate_Character_Attributes`. This is consistent with (but not
    proven by) the `Enemy_Guild_Spawn`/`Embassy_Spawn` AI functions'
    own comment "This is necessary for heroes that are not generated via
    an interface call" (`GPLMx/Rules/Quests_3.gpl` line 1502-1503,
    identically phrased in the workspace's own `MyAI/custom_rules.gpl`)
    — the comment's phrasing implies a real "interface call" recruit
    path exists elsewhere that these AI functions are explicitly
    replicating for the case where there's no UI click, but that real
    path's own GPL/exe implementation was not found as source in this
    pass. **UNVERIFIED**: the exact exe-side function that performs a
    plain (non-Embassy) guild recruit's cost check + `$SpawnUnit` call —
    no GPL-side call site exists to point at, and no Ghidra trace was
    done in this pass; would need the same disassembly work
    `TODO-Ghidra.md` Priority 3.4 already flags for research-button
    clicks, applied to the recruit button specifically.
  - **`$SpawnUnit` → hero attached to Palace/player, confirmed
    concretely:** `Hero_Births.gpl`'s `hero_birth` (called from
    `LowLevel.gpl`'s engine-invoked `NewUnitInit` per `birthScript`,
    same mechanism `GPL_MODDING_GUIDE.md` §1/§2 already establish for
    all units) is what actually wires the freshly spawned agent to its
    home guild and Palace: `palace = $getpalace(thisagent)` resolves the
    owning Palace; if `thisagent's "home"` is unset it defaults to
    `$parent(thisagent)` (the guild agent passed as the first arg to
    `$SpawnUnit`); if that "home" is a Palace it's nulled instead (no
    guild membership for Palace-spawned heroes — matches
    `GPL_MODDING_GUIDE.md` §4's "Palace-born heroes have no home" claim);
    otherwise `home's "members" << thisagent` — **this is the literal
    guild-membership-list append**, confirming the exact mechanism
    `GPL_MODDING_GUIDE.md` §4 references only abstractly. Separately,
    `palace's "Waiting_population"`/`"population_counter"` are
    incremented and can trigger auto-spawning `general_housing` — this
    is population/housing bookkeeping, not membership, and applies to
    every hero regardless of guild. **Confirmed the "hero attached to
    Palace" half is really "hero attached to its home guild's `members`
    list, and separately counted at the Palace level for housing"** —
    two different attachment mechanisms, not one.
  - **`Generate_Character_Attributes`** (`Hero_Births.gpl`,
    "called by the in-game code when a vehicle is generated" per its own
    comment — inconsistent with what it actually does, but the comment
    style matches other confirmed-engine-invoked functions per
    `GPL_MODDING_GUIDE.md`'s "same engine-entry-point comment style"
    pattern) applies the stat-randomization/building-bonus logic
    (library intelligence bonus, statue loyalty bonus, Krolm temple
    self-estimation bonus, etc.) that a UI-recruited hero apparently gets
    automatically, but that AI-spawned heroes must call explicitly — see
    `Enemy_Guild_Spawn`'s comment "This is necessary for heroes that are
    not generated via an interface call" quoted above. **UNVERIFIED**
    whether `Generate_Character_Attributes` is called by `hero_birth`
    itself, by `NewUnitInit`, or by some other engine-side step for a
    real UI-recruited hero — no GPL call site for it was found calling
    it unconditionally (only the AI-spawn functions call it explicitly,
    which is exactly the case the comment says needs the explicit call).
    This is a genuine gap, not an assumption either way.
- [x] Is recruitment building-specific (different mechanism per guild
  type) or does it funnel through one shared recruit function? **Mixed —
  more unified than `Visited_Script`, but not fully unified, and the
  "recruit" question and "birth completion" question turn out to be two
  separate mechanisms that must both be checked separately.**
  - **Capacity gating (`GuildHasOpenSlots`, `Building_Births.gpl` line
    978-994, byte-identical logic in `mx_Building_Births.gpl` line
    1198-1214 except reading `#ATTRIB_MaxGuildMembers` instead of the
    base game's `max_members` field — a real base/expansion divergence
    matching the one `GPL_MODDING_GUIDE.md` §4 already flags for the same
    field) IS a single shared function, called identically regardless of
    guild family** — confirmed by reading every call site
    (`Building_Births.gpl`/`mx_Building_Births.gpl` self-recruitment
    loops, `Building_Deaths.gpl`'s stray-member reassignment,
    `Embassy.gpl`/`Mausoleum.gpl`). This is genuinely unified, unlike
    `Visited_Script`.
  - **Birth-completion (`birthScript2`) is per-family, following the
    same pattern `GPL_MODDING_GUIDE.md` §2 already documents for
    buildings generally — guilds are not a special unified case here.**
    Confirmed by reading `Building_Data.dat`'s Guild-subtype entries
    directly: most guilds/temples (`Rangers_Guild`, `Temple_Dauros`,
    `Temple_Agrela`, `Temple_Krypta`, `Temple_Fervus`) point
    `birthScript2` at the generic `guild_birth` (`Building_Births.gpl`
    line 404-427 — starts the guild's own `ActiveScript` if it has one,
    seeds `check_strays` using `thisagent's "member_title"` generically,
    then delegates to `Building_Birth`). But **`Warriors_Guild`
    (`warriors_guild_birth`, line 430-454) and `Rogues_Guild1`
    (`rogues_guild_birth`, line 608-628) each have their own dedicated
    completion function**, not `guild_birth` — confirmed reading both in
    full: `warriors_guild_birth` hardcodes 6 explicit `$check_strays`
    calls (Warrior/Paladin/Warrior_of_Discord × myplayer/notmyplayer)
    instead of `guild_birth`'s generic single `member_title`-based call —
    a direct structural consequence of Warriors_Guild recruiting **3**
    hero types instead of 1 (see the Action Code 8009 "Warriors Guild
    dynamic panel" finding in item 1 above — this is the GPL-side half of
    that same multi-type-per-guild pattern). `rogues_guild_birth` instead
    layers a one-time gambling-hall-spawn side effect, then explicitly
    calls `$guild_birth(thisagent)` itself — so it's an *extension* of
    the shared function, not a full replacement, a third distinct shape.
    `Temple_Krolm`/`Temple_Helia`/`Temple_Lunord`/`Dwarven_Foundry`/
    `Elven_Bungalow`/`Gnome_Hovel` were not individually re-checked for
    their own `birthScript2` target in this pass — **UNVERIFIED** whether
    any of those also deviate from plain `guild_birth` the way
    Warriors/Rogues do.
  - **The actual gold-check-and-`$SpawnUnit` step for a UI recruit click
    has NO confirmed GPL-side function at all for ordinary guilds** (see
    item 1's finding above) — so the honest answer to "unified or
    per-building" for the part that matters most to a modder (what fires
    when you click Recruit) is **UNKNOWN**, not "unified" or
    "per-building," because no GPL source implements it either way for
    the common case. Only the Embassy (a real but non-guild, always-on
    building) and the two AI-facing functions (`Enemy_Guild_Spawn`,
    `Embassy_Spawn`) have confirmed source, and neither is the literal
    "player clicks Recruit in a Warriors_Guild panel" path.
  - **Net assessment:** recruitment is **more unified than
    `Visited_Script`** at the capacity-check layer (one shared
    `GuildHasOpenSlots`), **equally fragmented at the birth-completion
    layer** (per-family `birthScript2`, same pattern as every other
    building type per `GPL_MODDING_GUIDE.md` §2), and **entirely
    unconfirmed at the layer that actually matters for "what happens
    when Recruit is clicked."** This is a more nuanced answer than a
    single unified/fragmented verdict — don't collapse it to one or the
    other when writing the final guide.
- [x] What's the relationship between a NEW hero class and the EXISTING
  guild-recruitment UI (does a new class need a new recruit button/panel
  entry, or can it slot into an existing guild's roster)? **Depends
  entirely on whether the new class reuses an existing guild's
  `member_title` slot or needs a brand-new guild/panel — these are two
  very different cases, confirmed from both the XML and exe-mapping
  sides.**
  - **A new hero's own `DialogID` is NOT a recruit panel, and is already
    fully shared — confirmed by direct example.** Every playable hero
    checked in this doc's §2 findings uses `DialogID value="AP20"`
    (re-confirmed here directly: 15+ separate `<Description>` blocks in
    `SDK/OriginalQuests/Data/M_Characters.xml`, all identical
    `DialogID value="AP20"`). `AP20` is the shared hero-info/status panel
    (shows HP/level/inventory for whichever hero is currently selected on
    the map) — **not** where recruitment happens. This means a new hero
    class needs **zero new panel work for its own info display** — it
    automatically gets the existing shared `AP20` panel the same way
    every other hero does, confirmed by the field being identical across
    every sampled hero with no exceptions.
  - **The actual recruit button lives on the GUILD building's own panel,
    not the hero's.** Confirmed by item 1's citation:
    `SMNUResearch/findings/action_codes_decoded.md` places the Action
    75/Handler 8009 "Recruit" pairing on `AP24` (Temple to Krolm's own
    building panel), not on any hero DialogID. So the real question is
    whether the new hero's **guild** (existing or new) has a recruit
    button pointed at it — a building-panel question, not a
    hero-XML question.
  - **Case A — new hero reuses an EXISTING guild's single `member_title`
    slot (e.g. replacing what a guild recruits, or adding a class that
    behaves like an existing one): no new panel/button work needed at
    all.** Confirmed structurally: `Building_Data.dat`'s Guild entries
    (`Rangers_Guild`, `Wizards_Guild`, etc.) each declare exactly one
    `member_title` string field (plain data, e.g. `(member_title Rogue)`)
    — repointing it at a new hero title is a pure `.dat` edit, and the
    guild's existing SMNU recruit button/action-code pairing (already
    wired to that building's DialogID) needs no change, since it doesn't
    reference the hero title at all, only the building's own recruit
    action code.
  - **Case B — new hero needs its OWN new guild building (a new
    DialogID) to be recruited from: blocked by the same limitation
    `TODO-New-Building-Requirements.md` already documents, cite don't
    re-derive.** That doc's building-to-panel section cites
    `SMNUResearch/findings/exe_disassembly_results.md`'s Ghidra-confirmed
    finding that the building-panel class factory (`FUN_0051b150`) maps
    DialogIDs to panel handler classes via a **hardcoded** table — "A
    completely new building type (new DialogID) that wants a Research
    button opening a custom panel would need the exe patched to add a
    new vtable handler" (exact quote, `exe_disassembly_results.md` line
    119-122). This applies identically to a brand-new GUILD's recruit
    panel, since guild panels use the exact same DialogID→panel-factory
    mechanism as research panels — **confirmed the same constraint
    applies, not independently re-derived for guilds specifically.**
  - **Case C — new hero recruited via the Warriors_Guild-style
    "multiple pre-defined buttons, exe shows/hides by prerequisite"
    pattern:** per item 2's finding, `Warriors_Guild` already recruits 3
    hero types (Warrior/Paladin/Warrior_of_Discord) through one guild
    building, with all 3 recruit buttons **pre-defined in the existing
    SMNU** and the exe toggling visibility (`SMNUResearch/FUTURE_TODO.md`
    "Warriors Guild (AP52) Dynamic Panel Pattern"). A new hero type could
    in principle slot into an *already-reserved-but-currently-unused*
    button slot this way with no exe patch — but **UNVERIFIED** whether
    Warriors_Guild's SMNU has any such unused slot beyond its 3 known
    types, or whether every other multi-type guild panel in the game
    follows the same pre-defined-slots pattern — not checked for any
    guild besides Warriors_Guild in this pass.
  - **Cross-reference, not duplicated:** the SMNU panel/button dispatch
    mechanism itself (control_id ranges, click routing) is the same
    UNCONFIRMED area `SMNUResearch/findings/exe_disassembly_results.md`
    and `TODO-Ghidra.md` Priority 3.4 already flag — this item does not
    re-derive that, only traces what's confirmed on the GPL/data side
    around it (per the task's own instruction).
- [x] Cost/prerequisite gating for recruitment — where is this defined?
  **Split across three genuinely different mechanisms depending on which
  "cost" is meant — hero base cost, guild capacity, and recruit-timing —
  none of which share a single source.**
  - **Hero base cost (`Cost` XML field) — confirmed the authoritative,
    per-hero-class source, but its consumer is UNVERIFIED.** Every
    playable hero's `<Game>` block in `M_Characters.xml` sets a `Cost`
    value (re-confirmed directly: Adept `Cost value="500"`, and other
    sampled heroes range from `100` to `1000` per the raw file — e.g.
    lines 43, 148, 243, 339 etc. show `275`-`1000` range values). This is
    a plain XML-declared per-unit-type field, the same category as
    `MaxHP`/`Experience` next to it. **No GPL function anywhere in the
    corpus reads a hero's `Cost` field via `thisagent's "cost"` or an
    equivalent `#ATTRIB_*` accessor** — grepped the full corpus for any
    such read and found none (the only `'s "cost"` hits anywhere are the
    workspace's own `MyAI` mod code, which uses `enemy_hero's "cost"`
    AFTER an AI-driven `$SpawnUnit`, and `spell's "cost"` which is an
    unrelated spell-cost field, not hero recruitment). This means the
    `Cost` field's actual consumption — whether the exe reads it
    directly at recruit-click time from the XML-derived unit-type table,
    the same way `RecruitDelay` presumably is (see below) — is
    **UNVERIFIED** from GPL/XML source alone, consistent with item 1's
    finding that the whole recruit-click gold-check-and-spawn step has
    no confirmed GPL implementation for ordinary guilds.
  - **The one CONFIRMED real gold-gate for a hero spawn uses a
    hardcoded literal, not the `Cost` field, and only for an AI-facing
    path — do not conflate the two.** `Enemy_Guild_Spawn`
    (`GPLMx/Rules/Quests_3.gpl` line ~1479-1508, identically duplicated
    in the workspace's own `MyAI/custom_rules.gpl`) hardcodes
    `$AdjustPlayerData(Guild, "gold", -600)` — "Charge 600 per hero
    spawned" per its own comment — a single flat cost for **any** hero
    type recruited this way, completely independent of that hero's own
    `Cost` XML value. This is a real, confirmed mismatch between the
    per-class `Cost` field's apparent purpose and what this one
    AI-spawn path actually charges — **UNVERIFIED** whether this is a
    deliberate AI-balance simplification or evidence that the real
    UI-recruit path also doesn't use per-class `Cost` the way its name
    suggests. `Embassy_Spawn`'s cost (see item 1) is different again —
    a per-instance randomized value (`$RandomNumber(500) + 800`), not
    tied to hero `Cost` either. **Three different guild-adjacent
    hero-spawn code paths found in this research, and none of them
    reads the hero's own `Cost` XML field** — that field's real consumer
    remains unconfirmed.
  - **Guild capacity gating IS confirmed and cited from item 2 above —
    not re-derived here.** `GuildHasOpenSlots` (`max_members`/
    `#ATTRIB_MaxGuildMembers` vs. current `members` list size, gated
    additionally on `$BuildingIsRecruiting` — an engine primitive with
    no GPL definition, confirmed **UNVERIFIED** what it actually checks
    beyond its boolean return contract) is the one real, confirmed,
    shared prerequisite gate for whether a guild can produce a new hero
    at all, regardless of gold.
  - **Per-hero `RecruitDelay` (XML field, universal across every
    sampled hero — 4000ms Rogue-class-speed heroes up to 20000ms tank
    heroes per the raw values already catalogued in this doc's §2) is a
    plausible timing-gate candidate, but its GPL consumer is also
    UNVERIFIED.** `globals.gpl`/`mx_Globals.gpl`'s `#DelayRecruitCheckPeriod`
    (1000ms) has a suggestive comment — "period to check for recruiting
    a hero... will be recruited if individual recruitment delay is up"
    — but **no GPL function anywhere reads `#DelayRecruitCheckPeriod`
    as an actual `$NewThread`/`$SetThreadInterval` argument** (grepped
    for the literal expression name across every `.gpl` file, zero call
    sites beyond its own declaration). This strongly suggests
    `RecruitDelay`-based timing is implemented **entirely exe-side**
    (a per-guild recruit cooldown timer the UI/engine manages directly,
    reading the XML field without any GPL involvement) — consistent
    with, but not proof of, the pattern already established for the
    gold-check/spawn step in item 1. **UNVERIFIED**, explicitly, not
    assumed either way.
  - **No prerequisite/tech-tree gate (e.g. "guild must be a certain
    level," "player must have N other buildings") was found anywhere in
    GPL source for recruitment specifically** — contrast with the
    confirmed research-purchase prerequisite gates in `GPL_MODDING_GUIDE.md`
    §3 (`Researched_Item()`-style checks gating hero AI purchases). No
    equivalent `Recruit_Item()`-shaped function exists for recruitment.
    This is a real absence, not an oversight in this search — the
    closest thing found, `GuildHasOpenSlots`, is a capacity gate, not a
    prerequisite/tech gate.

### 6. Known Gaps After This Pass
(Fill in as research proceeds — list every UNVERIFIED item explicitly,
don't let them disappear into the writeup.)

**From the Section 5 (Recruitment) pass specifically — consolidated list
of every UNVERIFIED item raised above, so they don't get lost:**

- **The single biggest gap: no GPL/exe source was found anywhere for the
  literal "player clicks Recruit on an ordinary (non-Embassy) guild
  panel" gold-check-and-`$SpawnUnit` step.** Every real example found
  (`Embassy_Spawn`, `Enemy_Guild_Spawn`) is either a different building
  type (Embassy) or an AI-facing replication explicitly commented as
  filling in for the missing "interface call" path. This is the true
  blocker for confidently writing "how recruitment works" in the final
  guide — everything else in Section 5 is scaffolding around this
  central unconfirmed step. Needs a Ghidra trace of the recruit
  button's click handler specifically (same category of work as
  `TODO-Ghidra.md` Priority 3.4, but for the recruit action code, not
  research purchases).
- Whether `Generate_Character_Attributes` is called automatically for a
  real UI-recruited hero (by `hero_birth`, `NewUnitInit`, or some other
  engine step) or whether UI-recruited heroes simply never get the
  library/statue/temple stat bonuses that AI-spawned heroes must request
  explicitly — genuinely unknown either way (item 1).
- The exact exe-side function/control_id range for the Recruit button
  specifically — distinct from, but the same class of gap as, the
  research-button control_id ranges already flagged UNCONFIRMED in
  `SMNUResearch/findings/exe_disassembly_results.md` and
  `TODO-Ghidra.md` Priority 3.4 (items 1 and 3).
- Whether guild families besides `Warriors_Guild`/`Rogues_Guild1` (i.e.
  `Temple_Krolm`, `Temple_Helia`, `Temple_Lunord`, `Dwarven_Foundry`,
  `Elven_Bungalow`, `Gnome_Hovel`) also deviate from the generic
  `guild_birth` birth-completion function — not individually checked in
  this pass, only Warriors/Rogues were read in full (item 2).
- Whether any guild's SMNU panel has pre-defined-but-currently-unused
  recruit button slots (the `Warriors_Guild` "3 buttons, exe toggles
  visibility" pattern) that a new hero could occupy without an exe
  patch — only confirmed for Warriors_Guild itself, not checked against
  every other guild's panel data (item 3).
- The hero `Cost` XML field's actual consumer is unconfirmed — no GPL
  function reads it, and the one confirmed AI-facing gold-charge
  function (`Enemy_Guild_Spawn`) uses an unrelated hardcoded flat value
  (600) instead, a genuine unexplained mismatch (item 4).
- Whether `RecruitDelay` (universal per-hero XML field) is enforced
  exe-side, GPL-side, or not enforced as a real cooldown at all —
  `#DelayRecruitCheckPeriod`'s suggestive comment has no confirmed GPL
  call site anywhere in the corpus (item 4).
- What `$BuildingIsRecruiting` (an engine primitive with no GPL
  definition, consumed only inside `GuildHasOpenSlots`) actually checks
  — its boolean contract is used but never explained in GPL source
  (items 2 and 4).
- No prerequisite/tech-tree gate (guild level, building count, etc.) for
  recruitment was found anywhere in GPL source, unlike the confirmed
  research-purchase gate pattern in `GPL_MODDING_GUIDE.md` §3 — this
  reads as a genuine absence rather than a search gap, but it wasn't
  exhaustively ruled out against every guild's own birth/upgrade
  functions individually (item 4).

## Process Notes for Sub-Agent Dispatches (write in SMALL portions)

Sections 1-4 above were written as large, monolithic edits, and this has
caused real problems before (a similarly large single-edit pattern in
`TODO-GPL-Deepdive.md`'s research led to one dispatch crashing outright
mid-write and losing all its work before landing anything). Going
forward:

- **Save after each numbered subsection (or even each checklist item),
  not once at the end of the whole coverage area.** Use `str_replace` to
  append a completed `- [x]`/`- [ ]` item immediately after finishing its
  investigation, then move to the next item — don't accumulate an entire
  section (1-6) in memory and write it all in one massive edit.
- **Re-read the file immediately before each small write** (other work
  may have landed concurrently, and this avoids stale-content
  `str_replace` failures).
- If a single checklist item's investigation itself produces a lot of
  citation detail, that's fine — the point is committing incrementally
  per item/subsection, not artificially shortening findings.
- Follow the same tool-usage rules already established in
  `TODO-GPL-Deepdive.md`'s process notes: `grep_search`/`read_file`/
  `read_files` for investigation, `utility/test_decoder.py` (the one
  named trusted scratch script) if a script is genuinely needed, no
  ad hoc PowerShell.
