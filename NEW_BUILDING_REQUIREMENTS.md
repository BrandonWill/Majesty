# Adding a New Building — Requirements Checklist

A literal, ordered checklist for adding a new building type to Majesty
Gold HD. Every item below is backed by a citation in
`TODO-New-Building-Requirements.md` — this file is the distilled
checklist, that file is the research/evidence behind it.

**Confidence key:**
- ✅ **Confirmed** — verified directly against shipped game data or GPL
  source.
- ⚠️ **Confirmed but has an open gap** — the core mechanism is verified,
  but a related detail is unconfirmed (noted inline).
- ❓ **Unverified** — genuinely unknown; noted so you don't assume either
  way.

**Read this first:** the single most important distinction in this
document is between a new building that **reuses an existing `DialogID`
panel** (fully achievable today) and one that **needs its own new
panel** (walled off — see Step 6). Everything else on this list is
achievable with sprite/XML/`.dat`/GPL work alone.

---

## Step 1: Sprites (maindata.cam / quest CAM)

✅ **Mandatory animation sets** (present on every one of the 7 building
records extracted — Inn `ABF1`, Marketplace tiers `ABH1`/`ABH2`/`ABH3`,
Guardhouse tiers `ABE1`/`ABE2`, Palace `ABJ1` — zero exceptions):
`Build` (setID 80), `Die` (setID 96), `Active` (setID 192), `Inactive`
(setID 208), `Dead` (setID 224), `Crumble` (setID 240), `Hotspot`
(setID 400), `Interface` (setID 1000).

✅ **Buildings have NO `Stand` set (setID 8) at all** — confirmed absent
on all 7. Buildings use the `Active`/`Inactive` pair as their idle
state. This is a real building-vs-hero difference, not an extraction
gap; re-checked by dumping both sets' frame descriptors and confirming
real hotspot/size/tile-index data.

⚠️ **`Minimap` (setID 300) is NOT a general building requirement** — a
full scan of all 91 `AB*`/`BB*` IMAG records found it only on the three
Palace tiers (`ABJ1`/`ABJ2`/`ABJ3`). Every other building, guild,
temple, shop and lair has none, so **don't author one**. ❓ What actually
draws an ordinary building on the minimap is unresolved: an
engine-computed dot, or a downscaled existing ImageSet. What IS settled
is that ordinary buildings *do* appear — `Flags value="NotInMiniMap"` is
a real shipped opt-out flag whose entire population (11 in
`M_Buildings.xml`, 1 in `MX_Buildings.xml`) is decorative props, which
only makes sense if everything else appears by default.

⚠️ **Construction art is real and multi-slot — construction is NOT
invisible until completion.** The `Build` family occupies setIDs 80-83,
and sampled buildings populate several as genuinely separate frame
descriptors at distinct blob offsets (Marketplace1's setIDs 80/81/82 sit
at `relOff=0x25C`/`0x2C8`/`0x334`). **The count varies per building and
per tier** — Inn 2 slots, Marketplace1 and Guardhouse1 3 each,
Marketplace2/3 2, Guardhouse2 1. There is no "always exactly N stages"
rule.

❓ **How the engine picks among the populated `Build` slots, and whether
they hold distinct art at all.** The numbered variants checked report
identical width/height/hotspot and identical first-6 tile indices within
a given building, so they may not be progressive scaffolding frames at
all. No GPL, XML or `.dat` source ties construction %HP to an ImageSet
selection — `basic_birth`/`magical_birth`/`BuildingReachedMaxHP` only
reference `birthscript`/`birthscript2` function pointers, never an
ImageSet. Settling this is a sprite-extraction/rendering job, not a
source-reading one.

⚠️ **The numbered `Die` variants (setIDs 97-103, "Die-2" through
"Die-8") ARE present on buildings** — a broadened scan found 417 hits
across many `AB*` records (Ballista Tower, Blacksmith 1-3, Fairgrounds,
Guardhouse 1-2, Inn, Library 1-2, Marketplace). This is a building-only
feature: heroes have zero hits on 97-103 and use the single `Die`
setID 96. **The count is not uniform, so don't author to a fixed
number:** Inn, both Guardhouse tiers and Palace1 populate the full
96-103 (8 slots), while all three Marketplace tiers populate only 96-101
(6). ❓ Whether these numbered slots hold genuinely different
collapse-stage art or are reserved/placeholder slots was not verified —
only their presence in the setID table was.

✅ **`Crumble` (setID 240) is a hard requirement, not optional.** Every
building death path converges unconditionally on
`$performaction(thisagent, "Become_Rubble", thisagent)`, which reads the
`Crumble` ImageSet per `Become_Rubble`'s own XML (`A009`,
`<ImageSet value="Crumble"/>`). Confirmed four independent ways:
`Building_Deaths.gpl`'s shared `building_death` calls it with no guard;
every family-specific death function (`statue_death`, `gardens_death`,
`guild_destroyed_common`, `GuardHouse_Death`, the `Hidden_*_Death`
family, `lair_death`) ends by calling `$building_death`; `Palace_Death`,
which bypasses `building_death` entirely, still calls the identical
line; and `Siege_Palace_Death` (`GPLMx/Rules/Quests_3.gpl` 2236-2264), a
bespoke quest death script that hand-rolls the whole teardown from
scratch, still calls it too. Even authored-from-first-principles paths
treat rubble as non-optional.

❓ **What happens if you omit `Crumble`** — whether `$performaction`
crashes outright or renders nothing is untested, and re-checked against
the quest-rules material with nothing found. Don't omit it.

✅ **Each building level tier needs its own complete sprite set.**
`ABH1`/`ABH2`/`ABH3` are three separate IMAG records (6488/6472/6728
bytes) with their own `Active`/`Build`/`Crumble` tile indices —
Marketplace1's `Active` slot-2 indices start `[0, 256, …]` while tiers
2/3 start `[256, 0, …]`, and `Crumble` indices are tier-specific and
non-overlapping (1004/1018/1035). Guardhouse1 vs. Guardhouse2 shows the
same. Tiers do not share art.

⚠️ **Palace is the one building with no `Build` set** — `ABJ1` has no
setID 80 at all, matching its lack of a `birthscript`/`birthscript2`
two-stage chain. A building that skips the two-stage birth path
apparently needs no construction art. ❓ Whether that's engine-enforced
or just true of the one Palace example is unconfirmed; no second
birthScript-less building type was checked.

✅ **No fixed canvas size and no tile-multiple requirement.** Sampled
`Active` frames are Inn 69×101, Marketplace 105×116, Guardhouse 55×73 —
none a multiple of 32 or of any common value. The 32px terrain-tile unit
governs RGS map placement, a separate system; it does not constrain
sprite art.

✅ **Ground-plane alignment is the per-frame `(x_off, y_off)` hotspot,
the same mechanism heroes use** — Inn `(-65,-2)`, Marketplace
`(-96,-9)`, Guardhouse `(-57,-2)`. There is no separate footprint or
ground-plane field in the IMAG format.

✅ **Shadow/blend palette indices (248-255) are genuinely used by
buildings** — Inn, Marketplace1 and both Guardhouse tiles decode with
real values in the 248-250 range. Some individual frames have none,
which is per-sprite artist choice, not a rule.

✅ **Palette** — either reuse an existing base-game SPLT palette
(quantize your art to it) or ship brand-new SPLT entries in your own
quest/mod CAM. Existing SPLT entries are read-only; modifying them
crashes the game. Nothing here is building-specific — real building
tiles were observed using ordinary `palette_id` values (0, 37, 57).

---

## Step 2: Building XML Definition (M_Buildings.xml / your mod's Buildings.xml)

Your entry is a `<Description type="Unit" subType="Building" ID="…"
Name="…">` block. Field presence below was read side by side across
Marketplace1 (`ABH1`), Rangers_Guild (`ABW1`), Warriors_Guild (`ABV1`),
Guardhouse1 (`ABE1`) and Palace1 (`ABJ1`), then cross-checked against
additional buildings.

✅ **`<Engine>` block, always required** (all 5 sampled, zero
exceptions): `CanUse value="HumanPlayer"`, `Menu value="N"`,
`ImageIDBase`, `DefaultSound`.

✅ **`<Engine>` `Info` flags, partly optional:** `Info
value="BlockGround"`/`Info value="BlockFlying"` are on all 5 and on
nearly every other `AB*` building. `Info
value="ModifyTerrainTextureOnPlacement"` is genuinely per-building
optional — Rangers_Guild uniquely lacks it while the other 4 have it.
`Info value="ModifyTerrainHeightOnPlacement"` appears only on Palace1
among the 5, and elsewhere correlates with visually large/terrain-
reshaping structures (Fairgrounds, Dark_Castle, Sewer).

✅ **`<Game>` block, always required** (all 5 sampled, zero exceptions):
`DialogID`, `MaxHP`, `SightRange`, `Flags value="HasHPBar"`, `HelpID`.

✅ **`<Game>` fields that are conditional, confirmed by real omissions
rather than assumed:**
- `Cost`/`Multiplier`/`IncomeType`/`IncomeAmount` — present on
  Marketplace1, both guilds and Guardhouse1, but **all four absent on
  Palace1**, which uses `Flags value="NotBuildable"` instead. An
  `IncomeType="3"` (non-revenue service) building can validly omit
  `IncomeAmount` — Guardhouse1 does.
- `UpgradeTo` — tier-dependent. Present on Marketplace1/Guardhouse1/
  Palace1, absent on Rangers_Guild/Warriors_Guild, which have no further
  tiers.
- `MaxGuildMembers` + `Flags value="IsGuild"` — guild-only, and they
  always co-occur. Confirmed across Dwarven_Settlement, Elven_Bungalow,
  Gnome_Hovel, Rogues_Guild1, Wizards_Guild1 as well, zero exceptions.
- `Produces` (with nested `<Unit ID="…"/>`) — behavior-dependent.
  Present on both guilds, Guardhouse1 and Palace1; absent on
  Marketplace1, which produces nothing.
- `Flags value="NumberedName"` — for buildings the player can build
  several of (Marketplace1, Guardhouse1); absent on the guilds and
  Palace1.
- `Flags value="HasGoldToolTip"` — on Marketplace1/both guilds/Palace1
  but **absent on Guardhouse1**, consistent with its non-revenue role.

✅ **`Menu` is the field the engine keys build-menu categorisation on,
and `Flags value="IsGuild"` is NOT.** The two are orthogonal: `Menu`
(`<Engine>` block) carries the menu category; `IsGuild` (`<Game>` block)
means "this building houses/recruits heroes," which is why it always
travels with `MaxGuildMembers` and a `Produces` list.

> **Correction carried from the research doc's §9.1 — do not use the
> earlier version of this claim.** An earlier pass asserted that every
> building carrying `Flags value="IsGuild"` uses `Menu="1"` with zero
> exceptions. **That is retracted. There are seven exceptions: all seven
> base-game temples carry `Flags value="IsGuild"` *and* `Menu value="0"`
> simultaneously** — `Temple_Agrela1` (`ABO1`), `Temple_Dauros1`
> (`ABP1`), `Temple_Fervus1` (`ABQ1`), `Temple_Helia1` (`ABR1`),
> `Temple_Krolm` (`ABS1`), `Temple_Krypta1` (`ABT1`), `Temple_Lunord1`
> (`ABU1`), read directly from `M_Buildings.xml` lines 453-626. Because
> `IsGuild` takes the same value across two different `Menu`
> categories, it cannot be the categoriser — which is precisely what
> closed the question in `Menu`'s favour. The `IsGuild` ↔
> `MaxGuildMembers` pairing survives unchanged (the temples pair them
> too, so they are extra confirming cases).

✅ **Valid `Menu` values for buildings are 0, 1, 2, 3 and 12.** `Menu="0"` = temple
family (all 7 temples and their tiers). `Menu="1"` = guild/recruitment
family (Warriors_Guild, Rangers_Guild, Rogues_Guild1, Wizards_Guild1,
Dwarven_Settlement, Elven_Bungalow, Gnome_Hovel). `Menu="2"` = the
general bucket for ordinary economic/defensive buildings — **and also
most monster lairs**, so `Menu` alone does not distinguish
player-buildable from monster-only; `CanUse` carries that. `Menu="3"` =
buildings that appear through other mechanics rather than the
construction menu (`Brothel`, `Gambling_Hall`, `General_Housing`,
`Sewers` — all four also carry `Flags value="NotBuildable"` and no
`Cost`). `Menu="12"` = the decorative-prop bucket (banners, treasure
chests, goblin markers, signs, `Siege_Marker`).

Full base-game census, so you can see the shape rather than trust a
summary: HumanPlayer 0/1/2/3 = 17/10/23/4; Monster 2/3/12 = 23/1/13.

⚠️ **`Menu` is probably interpreted per-`subType` rather than as one
global enum, but the usual argument for that is wrong.** Buildings and
Characters do **not** occupy disjoint value ranges — `Menu="12"` is used
by both. ❓ So treat per-`subType` interpretation as unverified; it may
well be true, but range-disjointness is not evidence for it.

✅ **For a new player-buildable building in the normal construction
menu, use `Menu="2"`** (or `0`/`1` if you specifically want it filed as
a temple or guild).

⚠️ **For a new decorative prop, `Menu="12"` is the likely correct
value**, pairing with the prop flag set below. Inferred from the flag
correlation across all 15 `Menu="12"` entries, not from an engine trace.

❓ **Whether a wrong-but-nonzero `Menu` value simply misfiles a building
in the wrong tab or breaks/hides it outright** — untested, needs an exe
trace or an in-game test. ❓ Also unresolved: why `BBJ1` `Graveyard` is
the single Monster-`CanUse` building using `Menu="3"` instead of the
otherwise-universal `Menu="2"` (one exception in the base game, zero in
the expansion). Its `NotBuildable`/`NoFlaggable`/`NotSpellTarget` flags
and absent `Cost` make it structurally a non-constructed prop-like
building that happens to be Monster-owned, which is at least consistent
with `Menu="3"` meaning "not built from any menu, regardless of owner" —
but that is field correlation, not a confirmed mechanism.

✅ **Multi-tier buildings are separate, complete `<Description>` entries
— there is no single entry with a tier list.** `ABH1`/`ABH2`/`ABH3`,
`ABE1`/`ABE2`, `ABJ1`/`ABJ2`/`ABJ3` each have their own full `ID`/`Name`/
`<Engine>`/`<Game>` content. Tier 2/3 entries add `UpgradeFrom`
(pointing at the previous tier's `Name`) and `Flags value="NotBuildable"`
so they can only be reached by upgrade.

✅ **Tier 1's `Cost` is the build price; tier 2/3's `Cost` is the price
to UPGRADE into that tier.** Confirmed by the `Dwarfeh_AI` mod's parallel
`upgradeCost` field, whose value on tier N equals the XML `Cost` of tier
N+1 across every family (Blacksmith1 `upgradeCost 600` → Blacksmith2
`Cost 600`; Marketplace1 `upgradeCost 1000` → Marketplace2 `Cost 1000`;
Wizards_Guild1 `2500` → WG2 `2500`; Palace2 `3750` → Palace3 `3750`). So
Marketplace is 1500 to build then 1000 per upgrade — read that way it is
perfectly monotonic. Guardhouse genuinely inverts it (600 to build, 500
to upgrade), so cheaper-to-upgrade is real, not a data error.

⚠️ **The price a player actually sees is computed exe-side from at least
three inputs, so the XML `Cost` alone won't predict it.** The model the
`Dwarfeh_AI` mod uses to match player pricing is `Cost` × `Multiplier`
once per copy you already own, × 0.95 if you have a completed Blacksmith.
See §2's corroboration block in `TODO-New-Building-Requirements.md`.
❓ Whether that is exactly the exe's formula is unconfirmed — it is one
experienced modder's working reverse-engineering, not a trace.

✅ **`Cost` is a plain per-tier integer, not computed from a
multiplier — and it is not monotonic.** Marketplace1 is `Cost="1500"`
while Marketplace2 and Marketplace3 are both `Cost="1000"`. Don't assume
upgrades cost more.

✅ **`costMultiplier` and `Level` do not exist as XML attributes** —
zero matches for `Level=`/`Tier=` in the whole file. The XML's
`<Multiplier>` is an unrelated field, and the `costMultiplier` you may
see in `mx_prototype.gpl` is a fan-made AI script's own custom field,
not base-game data. **The real per-tier `Level` integer lives in
`Building_Data.dat`**, so a new multi-tier building needs both an XML
`Description` per tier *and* a `.dat` block per tier with its own
`(Level N)`. The two layers are parallel and name-matched by string.

❓ **What the XML `<Multiplier>` field actually drives** — no GPL
function reads it anywhere. One useful negative data point: across the
nine `IsGuild` buildings read in full, `Multiplier` varies independently
of both `Cost` and `IncomeAmount` (`1.5` occurs with `IncomeAmount` 50
and 40; `Temple_Krolm` and `Temple_Fervus1` share `Cost="900"` but
differ 1.5 vs 2.0), so it is not derived from either neighbour. Its
consumer is exe-side and unknown.

✅ **No footprint/collision-size field exists in the XML** — a full-file
grep for `Footprint`/`Radius`/`Size value`/`Width`/`Height value`/
`Collision` returns zero. The documented DUNT field list has none
either. See Step 5 for what this means in practice.

✅ **Don't set the prop-only flags on an ordinary building.** `Flags
value="NotInMiniMap"`, `Flags value="NoFlaggable"` and `Flags
value="NotSpellTarget"` are real, shipped, optional `<Game>` flags, but
their entire shipped population is decorative props that also carry
`NotBuildable` (e.g. `BBs1` `banner_wood`, `BBt1` `treasure_chest1`). A
new ordinary building should set none of them; a new decorative prop
should set all three plus `NotBuildable`, and per the `Menu` discussion
above should probably also use `Menu="12"` (that same prop population is
exactly the 15 `Menu="12"` entries).

`DialogID` is required here but is the one field with a real
architectural limitation attached — see Step 6.

---

## Step 3: `.dat` Block, Prototype Choice, GPL, and Compilation Wiring

Field presence below comes from reading `Building_Data.dat` and
`mx_Building_Data.dat` in full (~130 entries, not a sample) against every
building-family prototype declaration in `prototype.gpl`/
`mx_prototype.gpl`.

✅ **`type`/`subtype`/`title` are unconditionally mandatory**, in that
order, immediately inside the `{PrototypeName …}` block. Every entry in
both files opens with exactly these three, and every prototype in the
whole `.dat` system declares them first. This is the one universal
pattern across the entire system.

✅ **`birthScript` is present on 100% of non-`map_goodie` entries** — 84
named entries in base `Building_Data.dat` (the only 7 without it are all
`map_goodie`) and 110 in `mx_Building_Data.dat` (8 without, all
`map_goodie`). **Its target varies, and the pattern is per-FAMILY, not
per-tier.** Buildings that start under construction use a
`basic_birth` + `birthScript2` pair. Marketplace, Blacksmith,
Rogues_Guild, Wizards_Guild and the temples drop that pair at tier 2/3
and point `birthScript` straight at the completion function
(`Marketplace2`/`3` use `(birthScript Building_Birth)` with no
`birthScript2`) — but **`GuardHouse2` and `Library2` do not**: both keep
`basic_birth` + `birthScript2`, identical to their tier-1 entries. Don't
assume a tier-2 building collapses the chain; check the family.
`Palace` is a third shape again — all three tiers use `Palace_Birth`
with no `birthScript2` at any tier, so it never had a two-stage chain,
which is the `.dat`-side counterpart of Step 1's finding that Palace is
the one building with no `Build` ImageSet. The engine's call is
conditional, not an assert — `LowLevel.gpl`'s `NewUnitInit` does `if
($ValidFunction(NewAgent's "BirthScript")) $RunThread(…)` — so omitting
it won't crash, it just leaves the building with no self-registration
path into `buildings_waiting`/revenue threads/its own `ActiveScript`.
(The only genuine exceptions are the `map_goodie` decorative entries
like `Stone_tablet`/`obelisk`, which aren't buildings in the gameplay
sense.)

✅ **`IGdeathscript` is present on every non-`map_goodie` entry in both
files, zero exceptions.** `Hero_Deaths.gpl`'s `Unit_Call_Deathscript` is
the engine-invoked, type-agnostic dispatcher for every agent type.
Skipping it compiles, but `$validfunction(…)==TRUE` is then false and
nothing runs on death — no `Become_Rubble`, no `$release_occupants`, no
`$deleteagent`, so a dead building's game piece is never cleaned up.
Treat as required even though it isn't compiler-enforced.

✅ **Confirmed optional, behavior-dependent only:** `birthScript2`/
`upgradescript` (dropped by most level-2/3 tiers — though not
`GuardHouse2`/`Library2`, see above — and by any building with no
build-from-zero or upgrade path), `Visited_Script`/
`Lived_In_Script`, the `RevenueScript`/`Revenue_Amount`/`Revenue_Time`
trio (only 6 buildings across base + expansion set them), and the
`Guard_Function`/`Guard_Spawn_Function`/`Max_Guards` family.

✅ **No HP field belongs in the `.dat`.** Scanning both files for
`(HP `/`(MaxHP ` matched only 6 `Lair`-prototype entries and never a
`Building`/`Guild`/`GuardHouse`/`Palace`/`Tower`/`Library`/`Fairgrounds`
entry. For building-family prototypes the `.dat`'s job is exclusively
scripting-hook wiring; stats come from the XML (Step 2).

✅ **Prototype selection is compile-time struct-template selection, not
runtime dispatch and not inheritance.** The keyword after the opening
`{` (`Building`, `Guild`, `GuardHouse`, `Palace`, `Tower`, `Library`,
`Fairgrounds`, `Dwarven_Settlement`, `Lair`, `Outpost`, …) names a
`prototype X()` block compiled from the project's own GPL sources.
Field lists are declared independently per prototype and share almost
nothing beyond `type`/`subtype`/`title`/the birth/death/upgrade script
slots — **you are bounded to exactly one prototype's field set and
cannot mix and match.**

✅ **Pick your prototype by the field shape you need, not by theme.**
`Elven_Bungalow` and `Gnome_Hovel` are both literally `{Guild}` blocks
despite being residential housing, purely because `Guild`'s field shape
matched what they needed. `title`/`subtype` are freely author-chosen
strings (real shipped `subtype` values include `xx`, `Shop`, `Guild`,
`Entertainment`, `color`, `Palace`, `Outpost`) and don't map 1:1 to the
prototype keyword — `Dwarven_Settlement`'s `subtype` is literally
`Guild` while its prototype keyword isn't.

✅ **Choose `{Guild}` for a pure recruiter and the
`{Dwarven_Settlement}` shape if your building also fights.** This is a
structural difference, not a stylistic one: `prototype building()`
declares no guild-membership and no combat fields; `prototype Guild()`
adds the membership set (`members`, `member_title`,
`member_basicscript`, `max_members`) plus `SpecialScript`, still no
combat fields; `prototype Dwarven_Settlement()` adds, over and above
`Guild`, `agent Target`, `Strength`, `HtoH`, `Ranged`, `AttackType`,
`attack_action`, `EnemyType` and the `basicscript`/`backscript`/
`activescript` trio — the same family `prototype monster()` carries. The
shipped `[Dwarven_Settlement]` block populates exactly those combat
fields alongside ordinary guild ones, so they aren't vestigial. Copying
`{Guild}` and then adding `(Attack_Action …)`/`(EnemyType …)` would be
writing fields the prototype doesn't declare.

✅ **Two confirmed failure classes if you pick the wrong prototype:**
(1) compile-time field validation — you can only set fields the chosen
prototype declares, and e.g. `RevenueScript` exists on `building`/
`Fairgrounds`/`GuardHouse`/`Tower` but not on `Guild`/`Library`/`Palace`/
`Dwarven_Settlement`; (2) runtime GPL functions that read
prototype-specific fields with no type guard — `$Go_home` →
`use_building` → `target's "Lived_in_Script"` against a `{Building}`
target that never declared that field is a specific missing-field
reference in a specific traced call chain, not a vague crash.

⚠️ **Guard spawning: only `{GuardHouse}`/`{Palace}`/`{Outpost}` declare
the guard fields, but the guard bookkeeping itself is confirmed entirely
type-agnostic.** The full cycle was traced first-hand and contains no
type, title or prototype check anywhere: `City_Guard_Spawner` spawns
from the Palace and pushes itself onto `Palace's
"Waiting_Guardhouses"`; `City_Guard_Birth` (`Hero_Births.gpl` 407-437)
FIFO-pops that queue, sets the guard's `"Home"`, appends to `Home's
"Guards"`, increments `home's "num_guards"` and calls
`$RestartGuardSpawnThread`; `Guard_Death` (`Hero_Deaths.gpl` 140-163)
decrements and re-arms; `RestartGuardSpawnThread` is an ordinary GPL
function doing bare field reads. `Waiting_Guardhouses` lives on the
Palace, so you don't need to declare it. **So a custom building would
integrate with the real bookkeeping unchanged — provided it can hold the
fields.** ❓ That proviso is the whole remaining blocker: whether a
`{Building}`-prototype `.dat` block can declare/set `num_guards`/
`max_guards`/`Guards`/`Waiting_Guards`/`Guard_Spawn_Function` at all,
given `building` declares none of them. If the compiler refuses, the
route is a hand-written 5th prototype block of the same shape.

✅ **Two real gotchas for any guard-capable custom building.** (1)
`Building_Guard` and `Release_Guards` are partly title-gated — `If
(ThisAgent's "Title" == "Guardhouse")` wraps the arrow volley, the
1-in-100 wander behaviour and the `#ATTRIB_ResearchGoodGuard` guard-swap
(`Building_Guard.gpl` lines 46, 89, and 199 where the guard title-checks
its home). A custom building reusing these keeps the core release/scan
loop but silently loses all three Guardhouse-only behaviours. (2)
`Building_Guard`'s first statement is `if (thisagent's "enemytype" ==
"nothing") return;` — so you must set `EnemyType` in the `.dat` or the
scan loop no-ops on the first tick. Shipped precedent for `EnemyType` on
non-guard buildings exists (`[Wizards_Tower]`, `[Dwarven_Settlement]`).

❓ **Whether the compiler tolerates a `.dat` field with no live
prototype declaration.** `GuardHouse1`/`GuardHouse2` and the official
SDK `Adjust Guardhouse Mod` all set `(Hero_Guarded False)`, yet
`prototype.gpl` has that exact field **commented out**, and the only two
GPL references to it are also commented out. Whether the real
`Gplbcc.exe` silently accepts undeclared fields or this survives by
historical accident is unresolved — settling it needs a deliberate
compile, which the research was scoped not to run. Don't rely on it
either way. (Note: the two tempting near-misses about GPL expression
syntax the compiler accepted are a different compiler path and are
explicitly not treated as evidence here.)

✅ **Compilation and dataset wiring — same mechanism as heroes, verified
directly rather than assumed.** `Building_Data.dat` is listed in the
same `SDK/OriginalQuests/GPL/path.gplproj` as `Hero_Data.dat`, on
consecutive `data=` lines, feeding the same `Gplbcc.exe` compile into one
`Bytecode.bcd`; `Data/DataSets.xml` loads that single bytecode file under
`<LoadGPL>` for all three release classifications. Every building GPL
source (`Building_Births.gpl`, `Building_Deaths.gpl`,
`TaskModules\Buildings\*.gpl`) is an ordinary `source=` line in the same
file, interleaved with hero lines — no separate building project or
compile pass.

✅ **A genuinely new building family needs nothing beyond a `.dat` block,
new GPL functions, and `.gplproj` lines — there is no building-type
registry.** Confirmed by a real compiling in-workspace example:
`MyQuest/MyAI/GPL/MyAI.gplproj` lists `data="Game\mx_Building_Data.dat"`
alongside its own `source=` GPL files, and that `.dat`'s `[AI_Takeover]`
block is a genuinely new building title (absent from both shipped `.dat`
files) whose `birthscript` points at `playerOneAI`, a function defined in
the mod's own `custom_rules.gpl`. The simpler case is also confirmed: the
official `SDK/Adjust Guardhouse Mod` overrides an existing building with
a `.gplproj` containing exactly one `data="Guardhouse.dat"` line and no
new GPL at all.

✅ **Compile through `cmd /c MakeGPL.bat`**, never by invoking
`Gplbcc.exe` directly, and load the resulting `.bcd` via your mod's
`.mmxml`/`.mqxml`.

✅ **Your `.dat` block is necessary but not sufficient — you still need
the XML `Description` from Step 2.** `AI_Takeover` does have one, in the
mod's own overlay copy at `MyQuest/MyAI/Data/MX_Buildings.xml` line 2,
with a full field set (`CanUse="HumanPlayer"`, `Menu="2"`,
`ImageIDBase="ABr1"` reusing the Embassy's sprite record,
`DefaultSound="Embassy"`, `DialogID="MX22"`, `Cost="3000"`,
`MaxHP="300"`, `SightRange="200"`, `MaxGuildMembers="2"`, `Flags
value="IsGuild"`, `Flags value="HasHPBar"`, `HelpID="h167"`). That is a
real worked example of Step 2's mandatory-field catalog satisfied by a
fan-authored building. **A note on the research history: an earlier pass
claimed `AI_Takeover` had no XML counterpart; that was retracted — the
grep had only covered the two shipped SDK copies, not the mod's own
overlay.**

❓ **Whether a `.dat`-only building with no XML `Description` could
spawn at all** stays unverified, and there is now no known `.dat`-only
building anywhere in the workspace to reason from. Every building-type
string passed to `$SpawnUnit` in shipped GPL resolves to both an XML
`Description` and a `.dat` block. Settleable in-game only.

✅ **`$SpawnUnit` really does spawn buildings, and a `"MaxHP"` string
flag makes them arrive pre-completed.** Shipped examples:
`$spawnunit(palace,"general_housing",palace,"MaxHP")` ×5 in
`Housing_Boom` (`Random_Events.gpl` 364-368), `$spawnunit(palace,
"general_housing","maxhp")` in `Hero_Births.gpl` 203 (the base game
grows its own housing this way), `$SpawnUnit(Palace,"BrokenSewerMain",…,
"MaxHP")` in `Quests_1.gpl` 1673, and `Autospawn_Lair.gpl` 29, which
passes the agent's own `.dat` `title` as the type string.

---

## Step 4: Sound

Phase vocabulary below was read from the full `<Description type="Sound"
subType="Standard">` blocks for `Marketplace` (`BP16`), `Rangers_Guild`
(`BP20`), `Warriors_Guild` (`BP21`), `Guard_House` (`BP13`) and `Palace`
(`PA01`), cross-checked against the expansion's `Outpost` (`BP54`) and
Magic Bazaar.

✅ **`DefaultSound` is unconditionally present on every building entry** —
a full-file count found 91 `Description` entries and 91 `DefaultSound`
tags, zero exceptions. It matches the Sound Description's `Name`
attribute, not its ID. This is stricter than `Produces`/`RevenueScript`,
which really are sometimes omitted.

✅ **You may point `DefaultSound` at the `"0"` sentinel to opt out of a
building voice entirely** — `placeholder_building` (`ABA0`) and `BBs1`
both do, and no Sound Description anywhere has `Name="0"`, so it can't
resolve to a real block. This is a value-level opt-out, not a field-level
omission: **always write the tag.**

✅ **Buildings and heroes use genuinely disjoint Phase vocabularies.**
Not one of the 5 sampled building Sound blocks contains a single
`VFX_*`-prefixed `Phase ID`; a workspace-wide grep for `Phase ID="VFX_`
lands zero hits on any `BP*`/`PA*`/`DC*` (building) Sound ID — every hit
is a hero/monster block or the unrelated `VFX_ADVISOR` UI namespace.
**Do not copy the hero phase list.** The only name shared verbatim
between the two vocabularies is `GetHit`.

✅ **Mandatory by precedent (present on all 5 sampled, zero
exceptions):**
- `Select` — click acknowledgment, with `DistanceModifier
  value="10000.0"` on every sampled building.
- `GetHit` — damage cue, with `FrequencyVariation`.
- `Ambient_Die1` … `Ambient_DieN` — a *looped* ambient sound (`Flags
  value="Looped"`).

⚠️ **`Ambient_Die` is the building's looped ambient sound, NOT its
destruction sound — do not let the name mislead you.** The count varies
(6 for Marketplace/Rangers_Guild, 8 for Warriors_Guild/Guard_House/
Palace), and ❓ every numbered variant within a single building points at
the identical `Wave` value (Marketplace's `Ambient_Die1`-`6` all
reference `AM14`; Palace's `1`-`8` all reference `AM01`), so the numbered
slots carry no differentiated audio in any sampled building. Why the
duplicate slots exist — random selection among duplicates, or a leftover
authoring convention — is unexplained by any source.

✅ **Class-dependent, genuinely optional:** `Ambient_Active1` (a second
looped ambient) is present on the shop/guild-type buildings
(Marketplace/Rangers_Guild/Warriors_Guild) and absent on
Guard_House/Palace. `Attack` is present only on `Guard_House` (`WU27`)
among the 5, consistent with only Guardhouse/Palace/Outpost having a
guard/arrow-volley mechanic at all.

✅ **Confirmed absent from every sampled building:** `Death`, and the
whole `VFX_*` family. Buildings have no `Death` phase in their own
`DefaultSound`-linked block.

✅ **You do NOT author a destruction sound — you get it for free.** The
`Become_Rubble` action (`A009`) carries `<Sound
value="Building_Collapse"/>` and `<SoundPhase begin="Begin"/>` alongside
its `<ImageSet value="Crumble"/>`, and Step 1 already established that
every building death path reaches `Become_Rubble` unconditionally. The
collapse cue (`BC01`) is mandatory in effect but supplied automatically —
no field in your XML or `.dat` needs to set it.

❓ **The construction/placement sound's trigger is unknown.**
`Place_Building` (`PB01`) exists as a deliberately-tuned one-shot cue
(`VolumeOverride`/`VolumeVariation`/`FrequencyVariation` all set), but a
workspace-wide grep for the literal string `Place_Building` finds only
the Sound Description itself and a CAM inventory table — **zero**
`<Sound value="Place_Building"/>` Action XML reference anywhere, unlike
`Building_Collapse`'s confirmed `Become_Rubble` link. It most likely
fires from an exe-hardcoded call at placement time, mirroring the opaque
placement-cursor path in Step 5, but that is explicitly not confirmed.
Either way, it isn't something you author.

---

## Step 5: Getting the Building into the Construction Menu, and Placement Rules

**This step is good news, and it is the opposite of Step 6's answer.
Don't conflate the two.**

✅ **The build-menu LIST is data-driven, not hardcoded. A genuinely new
building type WILL appear as a buildable, priced, placeable entry with no
exe patch.** The direct positive evidence is the expansion itself: Magic
Bazaar, Sorcerer's Abode, Outpost, Embassy and Mausoleum are all new
buildings that appear in the build menu in Expansion mode, all
`CanUse="HumanPlayer"` with real `Menu` values, with the base-game exe
binary unchanged between modes. That would be impossible if the menu's
building list were a compiled table.

✅ **There is no separate "menu registration" step** — the XML
`Description` entry from Step 2 *is* the menu's data source. `CanUse` +
`Menu` put the entry in a category, `Cost` supplies the displayed price.

✅ **Why this differs from the panel limitation, stated so the two are
never conflated:** opening a panel requires the exe to call a specific
compiled function per building class (a vtable slot with a 4-byte panel
name burned in — data cannot add a function pointer to a vtable). The
build menu only requires the engine to iterate every unit-type definition
flagged `CanUse="HumanPlayer"` with a `Menu` value and not currently
disabled, then render a generic button per entry. Different engineering
problems, different answers.

✅ **Availability is gated at runtime by `$DisableUnitType` /
`$EnableUnitType`.** These are engine primitives (compiler-recognised
keywords, no GPL body anywhere) and they are used heavily — roughly 120
shipped call sites. The disable-at-init / enable-as-reward pair is the
base game's main mid-quest progression device, not a rare trick:
`epic_quest_scripts.gpl` re-enables 14 building types in one block at
`dark_forest_victory` (lines 867-880), re-enables `"fairgrounds"` alone
as a staged reward paired with a `$messageflag` prompt (line 125), and
re-enables `"Dwarven_Settlement"` conditionally at `Slay_Dragon_Victory`
(line 1463). Expect quests to gate your building.

✅ **The signature is exactly one type-name string at every shipped call
site** — no player or agent parameter, confirmed by grepping every
`.gpl` file in both repos.

✅ **The lookup key is the per-TIER XML `Name`, matched
case-insensitively — NOT the `.dat` `title` and NOT the 4-char `ID`.**
The decisive case is Marketplace: all three tiers share `(title
Marketplace)` in the `.dat`, yet shipped quests disable `"Marketplace3"`
alone (`Demo.gpl`) and `"Marketplace1"` alone
(`mx_Epic_Quest_Scripts.gpl` 461) to different effect, which a
`title`-keyed lookup could not do. Case-insensitivity is proven by
shipped spelling variance against the real `Name` attributes
(`"fairgrounds"` vs `Name="Fairgrounds"`, `"Magicbazaar"` vs
`Name="MagicBazaar"`, `"Temple_dauros1"` vs `Name="Temple_Dauros1"`, and
`Dwarven_Settlement` spelled three different ways in three files).

✅ **Your own building's `IGdeathscript` or `birthScript2` is a
confirmed-legal place to call `$EnableUnitType` from** if your building is
meant to unlock something.

⚠️ **The enable/disable effect is not scoped to the calling agent's
owner.** `Building_Deaths.gpl` line 696 (`Hidden_Sword_Death`) calls
`$Enableunittype("Dwarven_Settlement")` from the death script of a
`Hidden_sword_site`, a unit type that is `CanUse value="Monster"` — so a
Monster-owned agent unlocks a HumanPlayer build-menu entry in shipped,
playable content, under an authored comment saying exactly that. Honest
bound: this is authored intent plus a shipped comment, not an engine
trace. Strong narrowing, not proof.

❓ **Where the enable/disable bit is stored** — global per unit type, or
per-player with an implicit player — is unresolved, and so is whether the
name resolution indexes the compiled DUNT record's name or the `.dat`
block name (those two strings are identical in every checked case, so no
shipped data can separate them). Ghidra question.

⚠️ **`$SetBuildingLimit`/`$RemoveBuildingLimit`/
`$RemoveAllBuildingLimits` are real primitives that no shipped quest
uses.** That negative is now confirmed rather than merely unfound: all 15
`Rules/` files have been read in full, a case-insensitive grep for
`buildinglimit` across every `.gpl` file in both repos returns zero, and
across all of `SDK/` returns only the two Notepad++ keyword template
lists. ❓ Their argument shapes and semantics (limit count? by title? per
player? hide the menu entry or refuse the placement?) are therefore
unknowable from source — with zero call sites there is no usage example
anywhere to infer a signature from.

✅ **There is no `Researched_Item()`-style tech-tree gate for
buildings.** Grepped for any building-specific analog and found none. A
new building has no default prerequisite unless a quest's GPL explicitly
disables and later enables it.

✅ **But there IS a real GPL-side placement prerequisite you can extend:
`CanIBuildThisBuilding(agent thisBuilding, list dependencies)` in
`GPL/Rules/construction_rules.gpl`.** It's an exe-invoked callback (zero
GPL call sites — the engine calls it by name) returning 0 to allow and a
non-zero `#chat_*` code to refuse. Shipped branches gate `wizards_tower`
(must be within `#wiz_tower_range` 800 of a completed wizards
tower/guild — proximity *required*), `marketplace` and `trading_post`
(must NOT be within 500/1000-1700-2800 of a competitor — proximity
*forbidden*), plus an expansion-only `outpost` branch; everything else
falls through to unconditionally buildable. **You can add a new per-title
branch here with no XML change and no exe patch.**

✅ **`CanIBuildThisBuilding` branches on the `.dat` `title`, matched
case-insensitively, and is therefore per-building-FAMILY, not
per-tier.** Every branch opens `title = thisbuilding's "title";` then
compares against lowercase literals, while the shipped `.dat` values are
mixed case (`(title Wizards_Tower)`, `(title Marketplace)`). Because all
three Marketplace tiers share one `title`, the `marketplace` branch
applies to every tier at once — **you cannot get tier-specific placement
rules out of this function** unless you also give each tier a distinct
`.dat` `title`, which shipped data never does.

✅ **Watch which string you use — the two GPL-reachable build gates
address your building differently.** Quest-level enable/disable is
per-tier by XML `Name`; placement rules are per-family by `.dat` `title`.
Get one of the two wrong and the gate silently does nothing.

✅ **Two more confirmed constraints on `CanIBuildThisBuilding`:** the
failure-message codes are indices into the same enum as `#intent_*`
(`defines.gpl`, 40-43 sitting between `#intent_assemble`=39 and
`#intent_defending_palace`=44), so **you cannot invent a new refusal
message** — only reuse an existing slot, and `#chat_too_close_market`=43
ships unused. And every `$ListObjects` in the function passes
`#MyPlayer`, so the proximity checks are scoped to the building's own
player — the "competing marketplace" test does not see an opponent's
markets.

❓ **The `dependencies` parameter is unverified.** No live branch reads
it, no XML field feeds it, and its only appearances are a commented-out
`$DebugOut` and a commented-out design sketch referencing fields and
primitives that don't exist elsewhere.

✅ **Terrain restriction is entirely the `Info` flag set from Step 2** —
`BlockGround`/`BlockFlying`/`ModifyTerrainTextureOnPlacement`/
`ModifyTerrainHeightOnPlacement`. These are pass/fail booleans, not a
terrain allowlist: a grep extended to `Terrain`/`Water`/`Land`/`Ground`
field names found zero matches beyond those flags. `CanIBuildThisBuilding`
reads agent proximity only and never touches terrain data.

❓ **What data source the engine reads for a building's placement/overlap
collision size.** No dedicated field exists in the XML or the documented
DUNT field list. The only spatial data that exists at all is the sprite's
IMAG hotspot plus pixel dimensions, which makes a sprite-bounding-box
derivation the only candidate — **suggestive, not proof, and explicitly
not settled.** Don't treat it as fact.

❓ **Whether live player placement validation shares any code or data
path with RGS map-generation-time overlap prevention is unknown both
ways, and there's a structural reason not to assume they match.** The RGS
note describes resolving a discrete, finite candidate-cell list at map
build time; live placement is a player dragging a cursor over continuous
coordinates on an already-rendered map with real-time valid/invalid
feedback. No GPL, XML, `.dat` or findings-file source confirms shared
routines. Plausible engineering choice, unconfirmed mechanism.

---

## Step 6: The Panel (`DialogID`) — the One Real Wall

**This is the least-settled and most consequential area. Read the
markers carefully.**

✅ **`DialogID` is a required plain XML string, and it is identical
across every tier of a building family** — Marketplace's 3 tiers all use
`AP31`, Guardhouse's 2 both use `AP17`, Palace's 3 all use `AP39`. A tier
upgrade changes `Cost`/`MaxHP` but never which panel the building opens.

✅ **The `DialogID`→panel mapping is hardcoded in the exe, per building
class. This is real disassembly, not inference.** Each building type has
its own C++ class whose vtable override has the target panel name burned
in as a 4-byte constant. The factory (`FUN_0051b150`) takes the 4-char
`DialogID` packed as a `u32` and maps it through a finite compiled table
to one of a fixed set of constructor functions (`0x31335041`/"AP31" →
`FUN_004a56d0` for Marketplace, `0x3230584d`/"MX02" → `FUN_004bc430` for
Magic Bazaar). There is no data file to edit.

✅ **A `DialogID` not already in that compiled table falls through to the
generic handler (`FUN_00497690`), which does NOT open a new panel** — it
only configures the current panel's research-button state. So a
brand-new `DialogID` gets no dedicated research/service sub-panel at all.

⚠️ **Treat "a new panel requires an exe patch" as not yet ruled out
rather than proven — and follow the same practical advice either way.**
The verdict is not contradicted, but the word "confirmed" is doing more
work than the evidence supports, because this project has already had
one verdict of exactly this shape overturned: the Freestyle
special-event registry was concluded to need an exe/UI change, then
turned out to be CAM `STRT` data (`EVSC`/`ENTX`/`EDTX`), overridable from
a quest `<CAM>` tag with last-loaded-wins semantics. The panel case rests
on absence-of-GPL/XML-evidence plus a partial Ghidra map — the same
evidence shape that produced that error. **The mechanisms are genuinely
different and must not be conflated**: the event registry is a
string/function-name table, whereas a building panel is instantiated by
a `DialogID`→handler lookup located in real exe code. ❓ The narrow,
nameable open question is: **is the `DialogID`→handler association itself
table-driven from data the way the `EVSC` registry turned out to be, or
is it a compiled vtable?** That's a Ghidra question.

✅ **Practical guidance, unchanged by the above: reuse an existing
`DialogID`, don't invent one.** The project's own SMNU research still
states plainly that a patched exe is needed for sub-panel *navigation*
(new action code), and that a mod can override existing panels but cannot
navigate between sub-panels.

✅ **Your new building can still set a `DialogID` and work correctly for
everything that doesn't need a dedicated sub-panel** — HP bar, minimap,
build-menu entry, GPL scripting, generic inline research-button state via
the fallback handler. The limitation is narrowly about opening a
genuinely new, distinct panel; it is not about `DialogID` being unusable.

✅ **Workaround 1 — reuse an existing building's already-mapped
`DialogID`.** Your building inherits that building's panel. ❓ Whether two
unrelated building types sharing one `DialogID` causes any cross-talk
beyond the shared panel itself is untested, and nothing in the newer
research material discusses panel sharing.

✅ **Workaround 2 — extend an already-mapped panel.** For a building that
already has a working hardcoded panel, you can add secondary/paginated
content by editing that panel's own SMNU/`textdata.cam` entries and
navigating by panel INDEX rather than `DialogID`. This extends an
existing mapping; it does not create a new one.

✅ **Panel and `STRT` overrides from a quest CAM do work, last-loaded
wins** — confirmed by another modder replacing "Market Day" text, and an
earlier first-loaded-wins finding was retracted (the PanelTest crash was
a malformed custom SMNU binary, not a failed override).

❓ **Whether any guild panel has a spare, pre-defined-but-unused button
slot you could occupy.** Two things narrowed here without settling it.
(a) Dormant over-declared widget slots are a **real** pattern in shipped
panel binaries: `textdata.cam`'s `GDB4` panel has two type-0 button
widgets (widget[29]/[30], action codes 2016/2017) whose tag-7 references
point at STRT string indices 28 and 29 while that panel's STRT contains
only 28 strings. (b) The question is now answerable offline with tooling
that already exists and is validated — `smnu_format.py`/
`smnu_analysis.load_panels()`/`smnu_compiler.py` round-trip byte-perfect
on 168 of 169 real panels. **But `GDB4` is the GPL debugger's panel, not
a guild panel — it does not show that any guild panel has a spare recruit
slot**, and treating it as if it did would be exactly the
assumed-analogy move the research forbids. Nobody has dumped the other
guild panels' widget lists; the `DialogID`s are known (`AP52`
Warriors_Guild, `AP47` Rangers_Guild, and `AP01`/`AP05`/`AP10`/`AP19`/
`AP24`/`AP25`/`AP28` for the seven temples). Note the separate
unconfirmed gate: finding a spare slot would not by itself prove
anything can be wired to it, because click dispatch may gate it.

⚠️ **Building-granted player-castable abilities live behind this same
wall.** Rage of Krolm (Temple of Krolm), Call to Arms (Warriors Guild)
and Petrify (Temple to Dauros, `AP05`, unlocked at Level 3) are all
ordinary button clicks inside their own building's panel — the same
trigger class, not three separate mysteries. `Temple_Krolm` and
`Warriors_Guild` are single-tier buildings with no `Skill`/`Ability` XML
field, so their unlock structurally cannot be a Level-3-style tier gate.
✅ You **can** call these functions, or write new ones of the same shape,
from custom GPL — confirmed via the Dwarfeh_AI mod's real call into
`DoRageOfKrolm`. ⚠️ But making a NEW such ability player-triggerable from
a building panel hits the identical exe-hardcoded-panel wall, and there
is no base-game "spell registry" to hook into instead. ❓ Whether
destroying the building revokes the ability is unverified from source
(the mundane explanation — losing the building removes its panel and
button along with it — is settleable in-game, no Ghidra needed).

---

## Step 7: A Building That Recruits a Hero

Only do this step if your building recruits. A recruiting building is a
building first — everything in Steps 1-6 applies unchanged.

✅ **Nothing about recruiting affects your building's buildability.** The
data-driven build-menu answer from Step 5 holds whether or not the
building recruits. The recruitment-specific blocker is narrower and
downstream: only the recruit BUTTON's own sub-panel is affected, if you
insist on a bespoke one.

✅ **`member_title` on the `.dat` block is the field that ties a building
to a hero class** — a plain string matched against the hero's own `title`
field. No ID linkage, no shared enum.

✅ **`member_title` never appears alone — it needs `member_basicscript`
as a pair.** All ~28 shipped `.dat` entries that set one set the other on
the next line, zero exceptions (`(member_title warrior)
(member_basicscript warrior_tree)`, `(member_title Elf)
(member_basicscript elf_tree)`, …). So you need the recruited hero's
title *and* that hero's decision-tree function.

✅ **`member_title` is what actually spawns the hero**, confirmed at
three independent call sites: `Lair.gpl` line 157 (`Hero_Generator`:
`$SpawnUnit (ThisAgent, ThisAgent's "Member_Title")`), its expansion twin
`mx_Lair.gpl` 188-192, and `Quests_3.gpl` 1494-1500 (the AI kingdom's
recruit loop, which assigns the field into a local `string Type` first).

⚠️ **Base and expansion differ on which cap they check** — `Lair.gpl`
gates on the `.dat` `Max_Members` field while `mx_Lair.gpl` gates on
`$getattribute(thisagent, #ATTRIB_MaxGuildMembers)`. A real divergence,
confirmed by reading both.

✅ **The guild-member cap is convention, not enforcement — your GPL must
check it itself.** Both shipped sites do the `$ListSize < cap` comparison
by hand rather than relying on `$SpawnUnit` to refuse, consistent with
`$SpawnUnit` being a thin, unvalidating primitive.

✅ **`Produces` and `member_title` do NOT have to name the same hero, and
the base game ships them deliberately mismatched.** `Warriors_Guild`'s
XML lists three (`<Unit ID="Paladin"/><Unit ID="Warrior"/><Unit
ID="Warrior_of_Discord"/>`) while its `.dat` sets `(member_title
warrior)` — one string. They're structurally incapable of being the same
declaration twice. A second independent case: `Guardhouse1` and `Palace1`
have `Produces` lists (`City_Guard`; `Palace_Guard`/`Tax_Collector`/
`Peasant`) and no `member_title` at all.

✅ **`Produces` has zero GPL readers anywhere** — grepping every `.gpl`
file in both repos for `"Produces"` returns no matches. So a mismatch
cannot break any GPL logic. ❓ What `Produces` actually drives on the
engine side (build-menu tooltip? panel button roster? nothing?) is
unverified.

✅ **Capacity gating needs the XML pair `MaxGuildMembers` + `Flags
value="IsGuild"` plus a `.dat`-side `max_members`** feeding
`GuildHasOpenSlots`, which is additionally gated on the opaque engine
primitive `$BuildingIsRecruiting`. If you use `{Building}` rather than
`{Guild}` as your prototype, note that `{Building}` declares none of the
membership fields — see Step 3's bounded-field-set rule.

✅ **Recruiting exactly ONE new hero type is the simple path: point
`birthScript2` at the generic `guild_birth` unmodified.** It internally
calls `check_strays` using the building's own `member_title`. **Recruiting
MULTIPLE hero types needs a bespoke completion function** (the
`warriors_guild_birth` shape) with one `check_strays` call per hero type,
because `guild_birth`'s generic form only handles one `member_title`
string.

⚠️ **`member_title` validation is a runtime lookup, not a compile-time
cross-check — as far as source can show.** The field is read as a plain
string and handed straight to `$SpawnUnit`'s unit-type parameter, so
whatever validation exists lives inside `$SpawnUnit`'s unit-type-table
lookup, not in a `.dat`/GPL compile step against `M_Characters.xml`. ❓
Two things stay open: what `$SpawnUnit` does with a type string matching
no loaded unit type (returns null, no-ops, or crashes — no shipped call
site passes a bad string, so there's no worked example; this is a clean
in-game test), and whether the `.dat` loader *additionally* does a
load-time cross-check, which the runtime finding doesn't rule out.

### The three cases, in order of how much you'll like them

✅ **Case A — recommended, fully unblocked.** The new hero recruits
through an existing guild's `member_title` slot, or your new building
takes a `DialogID` that's already in the exe's compiled panel table.
Zero exe-patch requirement; this is `.dat`/XML/GPL/sprite work only, on
both the building side and the hero side. **This is the confirmed "yes,
doable today" answer.**

⚠️ **Case B — blocked.** Your new building wants its own never-before-seen
`DialogID` with its own dedicated recruit panel. This runs into exactly
the Step 6 wall — the same wall, not a second one that happens to look
similar, since guild recruit panels use the identical
`DialogID`→panel-factory mechanism as research panels. Per Step 6's
caveat, read this as *not yet ruled out* rather than *proven impossible*,
and plan around it regardless.

❓ **Case C — unverified middle ground.** Occupying a pre-defined-but-
unused SMNU recruit button slot on an existing multi-slot guild panel,
the `Warriors_Guild` pattern where the exe toggles button visibility by
prerequisite. Confirmed real only for `Warriors_Guild` itself, not
confirmed to exist on any other guild panel, and not confirmed to be
extensible by SMNU editing alone without also patching whatever exe-side
condition toggles visibility. See Step 6 for what the panel-dumping
tooling could settle offline.

❓ **The literal recruit-button click-to-spawn mechanism for ordinary
(non-Embassy) guilds has no confirmed source** — the gold check, the
deduction, the spawn call. This is the hero research's single biggest gap
too, and it's now a confirmed absence from a fully-read corpus rather
than a "not found yet." No reason to think it behaves differently for a
brand-new building than an existing one, but that isn't confirmed either.
**You don't need this answered to complete Case A.**

---

## Bottom Line

- **A new building that is art/stat/sound-complete, appears in the
  construction menu, obeys placement rules, dies properly, and reuses an
  existing `DialogID` panel: fully achievable today. Every step is
  confirmed (Steps 1-5, plus Step 6's Workaround 1).** The build-menu
  list is data-driven — the expansion's own new buildings prove it — so
  "can I truly add a new building type" is a yes, with no exe patch.
- **A new building with its own brand-new dedicated research/recruit
  panel: blocked (Step 6).** The `DialogID`→handler mapping is real exe
  code with the panel name burned in per building class. Read this as
  *not yet ruled out* rather than proven impossible — the one narrow
  question that would settle it is whether that mapping reads a data
  table or a compiled vtable — but the practical advice does not change:
  **reuse an existing `DialogID`.**
- **A new building that recruits exactly one new hero type through an
  existing guild slot or an already-mapped `DialogID`: achievable
  (Step 7, Case A).** Use the generic `guild_birth`, set
  `member_title` + `member_basicscript` as a pair, and don't worry about
  matching `Produces`.
- **Guard-spawning on a non-`{GuardHouse}`/`{Palace}`/`{Outpost}`
  building: the bookkeeping would integrate unchanged, but whether your
  prototype can hold the fields is unconfirmed** — the fallback is
  hand-writing a prototype block of the same shape.
- **What you will not get citation-backed answers for today:** how the
  engine picks among construction-stage art, what draws an ordinary
  building on the minimap, what the engine reads for placement footprint
  sizing, what `<Multiplier>` and `Produces` do engine-side, and the
  click-time recruit mechanism. None of these has been shown to block a
  working new building — they leave secondary behaviours unexplained, not
  broken.

See `TODO-New-Building-Requirements.md` for the full research and
citations (its §8 is the consolidated gap list and its §9 the
reconciliation pass), `TODO-New-Hero-Requirements.md` for the hero side
of Step 7, and `GPL_MODDING_GUIDE.md`/`GPL_QUEST_RULES_REFERENCE.md` for
the underlying GPL mechanics this checklist builds on.
