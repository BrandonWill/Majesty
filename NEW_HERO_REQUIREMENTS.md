# Adding a New Hero — Requirements Checklist

A literal, ordered checklist for adding a new playable hero class to
Majesty Gold HD. Every item below is backed by a citation in
`TODO-New-Hero-Requirements.md` — this file is the distilled checklist,
that file is the research/evidence behind it.

**Confidence key:**
- ✅ **Confirmed** — verified directly against shipped game data or GPL
  source.
- ⚠️ **Confirmed but has an open gap** — the core mechanism is verified,
  but a related detail is unconfirmed (noted inline).
- ❓ **Unverified** — genuinely unknown; noted so you don't assume either
  way.

---

## Step 1: Sprites (maindata.cam / quest CAM)

✅ **Mandatory animation sets** (present on every base-game hero, zero
exceptions): `Walk`, `Stand`, `Attack`, `Cast`, `Special`, `Die` (setID 96
only — heroes need exactly one Die variant, unlike buildings which use
setIDs 97-103 for multi-stage collapse), `Dead`, `Minimap` (setID 300),
`Hotspot`, `Interface`.

✅ **Optional, class-dependent:** `Carry` — only needed if your hero
picks up/carries items (item-interaction classes).

✅ **No fixed canvas size or hotspot** — every hero's frame dimensions are
self-contained per-direction data. Use whatever size your art needs (real
examples range 8×9 to 16×11).

✅ **8-directional requirement** — for Walk/Attack/Cast/Special, exactly 6
of 8 direction slots must be populated (slots 2-7; slots 0-1 always
empty).

✅ **Palette** — either reuse an existing base-game SPLT palette
(quantize your art to match), or ship a brand-new SPLT entry in your own
quest/mod CAM (confirmed valid via the WrathOfKrolm example).

❓ **What happens if a required frame is missing at runtime** — no source
describes the fallback (crash vs. silent skip vs. placeholder). Don't
assume; test if you need to know.

---

## Step 2: Character XML Definition (Characters.xml)

✅ **`<Engine>` block, always required:** `Info value="BlockGround"`,
`CanUse value="HumanPlayer"`, `Menu value="6"` (this is the value that
marks a playable hero — confirmed the one consistent signal separating
heroes from monsters/henchmen/spell-effects in the file), `ImageIDBase`,
`Attachment kind="Movement" type="Walk" ID="..."` (pick a ground-walk DMOV
class — heroes are never flyers in shipped data, though this isn't
proven to be enforced), `DefaultSound`.

✅ **`<Game>` block, always required:** `DialogID` (use `AP20` — the
shared hero info/status panel every hero uses; you do NOT need a new
panel for this), `Cost`, `Experience`, `MaxHP`, `SightRange`, `Speed`,
`AttackRange min/max`, `RecruitDelay`, `Flags value="Heals"`, `Flags
value="HasHPBar"`, `Flags value="CanHighlight"`, `HelpID`, `Vitality`,
`Artifice`, `WillPower`, `Intelligence`, `Strength`, `Attack`, `Parry`,
`Dodge`, `PrimaryStat`, `NameGenType`.

✅ **Conditionally required, based on your class design:**
`AllowedWeapon`/`AllowedArmor` (omit either to opt the class out of that
equipment category — confirmed valid, Priestess omits `AllowedArmor`
deliberately), `AllowedSpells` (grants spells via XML; also possible via
runtime `$LearnSpell` GPL calls independently), `WeaponBasicDamage`/
`ArmorBasicDamage` (only if you declared the matching `Allowed*`),
`MagicResistance`/`RangedAttack` (class-dependent, not universal).

⚠️ **`AllowedSpells` mechanism confirmed, failure mode not.** It's a pure
XML declaration list — no GPL function reads it directly. Spell learn-gating
uses `CharacterLevel` on the Action XML (separate from `AllowedSpells`) plus
an optional `ValidationScript` cast-time gate. ❓ What happens if
`AllowedSpells` names a spell with no matching Action XML entry is
unverified.

⚠️ **Equipment slots are XML-declarative on the surface, engine-side
underneath.** `AllowedWeapon`/`AllowedArmor` are never read by GPL —
GPL reads derived runtime attributes (`#ATTRIB_WeaponTypeIndex` etc.)
instead. ❓ The XML→attribute translation itself is exe-side and
unverified from source, but you don't need to know it to use the fields.

---

## Step 3: GPL — prototype, Hero_Data.dat, decision tree, compilation

✅ **You get the shared `hero` prototype's fields automatically** — no
action needed. Every hero class gets all `prototype.gpl` `hero()` fields
(ActiveScript/BackScript/TaskName, stats, death/birth script pointers,
etc.) whether or not your `Hero_Data.dat` entry sets them; unset fields
default to empty/0/FALSE/null.

✅ **`Hero_Data.dat` entry — required fields present on every playable
hero, zero exceptions:** `type hero`, `subtype hero`, `title`,
`original_type Hero`, `EnemyType`, `Idle_action`, `attack_action`,
`Cast_Action`, `PrimaryStat`, `Friend`, `attacktype`, `castingrange`,
`PercentageHPRetreat`, `enemy_estimation`, `self_estimation`, `Loyalty`,
`Greed`, `Luck`, `Upgrade_Armor_Chance`, `Upgrade_Weapon_Chance`,
`Poison_Weapon_Chance`, `evaluationScript`, `activeScript`, `basicscript`,
`StartingScript`, `birthScript` (use `hero_birth` — every playable class
does), `IGdeathscript`.

✅ **Death handling — use the shared `gravestone()` function.** No new
hero-specific death function needed; 14 of ~16 playable classes point
straight at it. Only deviate if you want self-revival logic like Healer's
(a conditional wrapper around `gravestone()`).

✅ **Decision tree — you can point at an EXISTING class's tree function**
(e.g. `warrior_tree`) instead of writing a new one. The wiring is a plain
function-pointer assignment in `Hero_Data.dat`'s
`activeScript`/`basicscript`/`StartingScript` fields, not filename-based.
⚠️ Confirmed no title-check exists in at least one sampled tree
(`Adept.gpl`) that would break under reuse, but not checked for every
tree function — if reusing a tree, spot-check it for hardcoded title
comparisons first.

✅ **Compilation and dataset wiring, for a mod/quest-scoped new hero (the
realistic path):**
1. Write your own `.gplproj` with `data="YourHero_Data.dat"` +
   `source="YourHeroTree.gpl"` (or reuse an existing tree, see above).
2. Compile via `cmd /c MakeGPL.bat` (wraps `Gplbcc.exe`) — never invoke
   the compiler directly.
3. Load the resulting `.bcd` via your mod's `.mmxml`/`.mqxml` — it loads
   additively alongside the base game's bytecode, same layered-dataset
   model `CAM_MODDING_GUIDE.md` documents for CAM files.

---

## Step 4: Sound

✅ **Create a `Sound` Description whose `Name` matches your hero's
`DefaultSound` value** (plain name match, not ID match).

✅ **Mandatory `Phase` entries** (present on every sampled hero, zero
exceptions): `VFX_GO_COMBAT`, `VFX_FLEE_COMBAT`, `VFX_DECIDING`,
`VFX_GO_REWARD`, `VFX_FIND_COOL`, `VFX_SPECIAL1`, `Death`,
`VFX_GAIN_LEVEL`, `VFX_SEE_HOSTILE`, `Attack`, `Easter_Egg`. Each must
point at a real `WAVE` entry in a loaded CAM.

✅ **Class-dependent:** `VFX_CAST_SPELL1` (casters only), `GetHit`
(non-universal — some classes reuse their `Attack` phase for hit
reactions instead).

❓ **What happens if you omit a "mandatory" phase** — crash vs. silent
no-sound vs. some exe fallback is unverified.

---

## Step 5: Getting Your Hero Recruitable

**This is the least-settled area — read the confidence markers
carefully, this is not a fully solved problem.**

### 5a. Simplest path: reuse an existing guild's recruit slot ✅ Confirmed, low-risk

If your new hero can be recruited from an **existing** guild (either
replacing what that guild recruits, or you're fine with it sharing a slot
conceptually), this is fully confirmed and requires no panel/exe work:

1. Point the guild's `.dat` entry's `member_title` field at your new hero
   title (plain data edit).
2. Nothing else needs to change — the guild's existing SMNU recruit
   button/action-code pairing doesn't reference the hero title at all,
   only the building's own action code.
3. This is exactly the "redefine an existing recruitable unit" pattern
   (reskin Warrior into something else via XML, per Step 2) — if you're
   doing that instead of adding a genuinely new title, you don't even
   need this step; recruitment already works unmodified.

### 5b. New hero needs its own new guild building ❌ Blocked without an exe patch

⚠️ **Confirmed blocked** by the same limitation documented in
`TODO-New-Building-Requirements.md`: a building's DialogID→panel mapping
is Ghidra-confirmed **hardcoded** per building class
(`exe_disassembly_results.md`). A brand-new guild building with its own
recruit panel needs the exe patched to add a new vtable handler. This is
not a "hasn't been tried" gap — it's an architecturally confirmed wall.

### 5c. Slotting into an existing multi-recruit guild (Warriors_Guild pattern) ❓ Possible, unconfirmed

Warriors_Guild already recruits 3 hero types (Warrior/Paladin/
Warrior_of_Discord) from ONE building, with all 3 buttons pre-defined in
SMNU and the exe toggling visibility by prerequisite. ❓ Whether
Warriors_Guild (or any other guild) has an unused pre-defined slot a new
hero type could occupy without an exe patch is unverified — not checked.

### 5d. What GPL mechanisms actually drive recruitment (background, for anyone extending behavior)

✅ **Two real, confirmed GPL mechanisms exist** — useful if you want to
change *how* recruitment behaves, not just *what* gets recruited:

- **`check_strays()`/`adopt()`** (`Building_Births.gpl`) — adopts an
  already-existing homeless hero (no `"home"` set) found on the map into
  a guild, gated by capacity and (for enemy heroes) a loyalty roll.
  Called automatically at guild birth.
- **`Hero_Generator`** (`Lair.gpl`) — spawns a brand-new hero directly at
  a guild (`$SpawnUnit(guild, guild's "Member_Title")`), gated only by
  member count vs. capacity. Confirmed wired as a guild's `SpecialScript`
  in several quests, but it's quest-specific opt-in, not automatic for
  every guild.

⚠️ **What is NOT confirmed:** the literal "player clicks Recruit → gold
deducted → `$SpawnUnit` called" step for an ordinary guild panel has no
confirmed GPL source anywhere. The general exe dispatch architecture
(handler code → per-building vtable method) IS Ghidra-confirmed, but the
*specific* handler for Recruit's code (`8009`) has never been
independently decompiled the way the research-panel-open handler (`8851`)
was. **You don't need this answered to complete 5a** — it only matters if
you're trying to change the click-time behavior itself (cost, spawn
conditions) rather than just what gets recruited.

❓ **Cost**: the hero's own `Cost` XML field has no confirmed GPL
consumer anywhere. The one confirmed AI-facing recruit-cost function uses
an unrelated hardcoded flat value (600), not the hero's `Cost`. Whether
the real UI click reads `Cost` from the XML-derived unit table directly
(exe-side) is unverified.

❓ **RecruitDelay**: universal per-hero XML field, plausible cooldown
timer, but no GPL function reads the suggestive
`#DelayRecruitCheckPeriod` constant either — likely exe-enforced, not
proven.

---

## Bottom Line

- **Adding a new hero that's fully art/stat/sound-complete and
  recruitable through an existing guild slot: fully achievable, every
  step confirmed (Steps 1-4, 5a).**
- **Adding a new hero with its own dedicated new guild/recruit panel:
  blocked by a confirmed exe-side limitation (5b)** — same class of wall
  as adding a new building type generally.
- **Changing how recruitment itself behaves (cost, timing, spawn
  conditions) beyond what `check_strays`/`Hero_Generator` already give
  you:** the exact click-time exe behavior is unconfirmed — real
  Ghidra work, not just source-reading, would be needed to close that
  gap (see `TODO-Ghidra.md`).

See `TODO-New-Hero-Requirements.md` for the full research, citations, and
`TODO-GPL-Deepdive.md`/`GPL_MODDING_GUIDE.md` for the underlying GPL
mechanics this checklist builds on.
