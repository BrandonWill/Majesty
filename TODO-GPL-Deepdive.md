# GPL / Gameplay Logic Deep Dive — TODO

**Status: First consolidation done.** All completed research (9 topics)
has been written up in `GPL_MODDING_GUIDE.md` — see that file for the
actual findings, organized by system. This TODO now tracks what's still
open: unresolved UNVERIFIED items, un-investigated topics, and the pass
structure for continuing the deep dive.

## Evidence Standard (non-negotiable — applies to all future work here)

Every claim in `GPL_MODDING_GUIDE.md` must cite the specific file/function/
line it was verified against. No claim based on naming conventions or
assumed symmetry between similar-looking systems. Unconfirmed behavior
must be labeled **UNVERIFIED**/**UNKNOWN**, not stated as fact. This
standard exists because two early claims in this research had to be
retracted after a closer read — see `GPL_MODDING_GUIDE.md`'s "Retracted
Claims" section for both, and don't repeat that failure mode (assuming a
similar-looking system behaves the same way without reading its actual
source).

## Completed (see GPL_MODDING_GUIDE.md for full findings)

1. ActiveScript/BackScript/TaskName state machine
2. birthscript vs birthScript2
3. upgradescript (basic_upgrade vs magical_upgrade)
4. Building revenue system (RevenueScript/Revenue_Amount/Revenue_Time)
5. Guard_Function/Guard_Spawn_Function
6. Lived_In_Script (guild buildings)
7. The Intent system (#intent_*)
8. Krypta/Agrela hero revival
9. Hero death and gravestone handling

## Open UNVERIFIED Items (carried over, need resolution)

See `GPL_MODDING_GUIDE.md`'s "Open Questions Catalog" for the full list
with section references. Highlights that would need Ghidra specifically
(coordinate with `TODO-Ghidra.md`):

- Engine-side `$NewThread`/`$RunThread`/`$ResumeThread`/`$KillThread`
  scheduler semantics
- Whether the exe truly calls `$building_upgraded`/`$DoMarketDay`/
  `$EndMarketDay` from real player actions
- Research-purchase-button click dispatch (control_id ranges) —
  `TODO-Ghidra.md` Priority 3.4
- What numeric `cProc="8192"` resolves to (hero death action callback)
- What renders the AITX intent/status string lookup and how

Highlights answerable from GPL/XML/`.dat` source alone (no Ghidra needed):

- What sets `#ATTRIB_isTaxed`/`#ATTRIB_QuickTax` on a building
- Where `GuardHouse_Birth` (referenced as a `birthScript2` value) is
  actually defined — not found in any `.gpl` file searched so far
- Whether every researchable item follows Magic Bazaar's confirmed
  gate-then-autonomous-purchase pattern, or some are AI-consumer-less
- Whether a Mausoleum-interred hero remains reachable by `"Dead"`-type
  list queries (affects whether Reanimate/Resurrection can still target
  them)
- Whether other building panels have the same per-panel-STRT-vs-GMTX text
  trap already confirmed for Marketplace/APa3
- What Hall of Champions' `HallOfChampions_Bounty_Cost`/`Period` functions
  actually do and what calls them (retracted claim — genuinely unknown)

## Not Yet Investigated

- **Re-verify `.kiro/steering/majesty-modding.md`'s Petrification System
  description** against actual GPL source — currently assumed correct
  because it's already written down, not because it was re-checked under
  this evidence standard.
- **Systematic orphaned-content sweep** (Zoo was found opportunistically,
  not systematically) — cross-reference every DialogID-shaped sprite
  prefix (`AB`, `BV`, `AV`, etc., see `CAM_DEEP_DIVE.md`'s prefix table)
  against every XML building/unit `ID=` attribute and every quest
  `.mqxml`/`.mmxml` reference. Worth scripting given the volume (~14+ IDs
  in the `AB` prefix alone) rather than doing by hand.
- **Building visit-system deep dive, full depth** — §3 of the guide has
  the dispatch table and the two misleading-`.dat`-value cases, but not a
  complete item-by-item/cost-by-cost writeup for every `Visited_Script`
  grouping (Library_Visited, Enchant_Equipment, GuardHouse_Visited,
  Inn_visited, Poison_Weapons, Gambling_Hall, Brothel, Gardens_visited are
  all still just named in the table, not individually traced the way
  Shop_Visited/Bazaar_Visited were).
- **Shared primitive catalog, remaining primitives** — `$control_monster`
  and `RewardFlag` got partial coverage as side effects of the Zoo/
  check_rewards findings; `$SpecifyIntent` got full coverage in §7. Still
  need: the effector system as its own topic (createeffector/checkeffector/
  duration semantics), and a deliberate (not opportunistic) sweep of any
  other primitive that shows up across 3+ unrelated systems.
- **Hero class decision tree pass** — no dedicated per-class writeup
  exists yet; classes have only been read incidentally while tracing
  `$Go_home`/`Hall_Champs_Check` call sites. Lower priority, mainly
  relevant to `MyAI` custom AI mod work.
- **Quest rules pass** (`Rules/Quests_1.gpl` etc.) — lowest priority, most
  quest-specific/least reusable knowledge.

## Prioritization Note

Don't start with "read all 306 files." Let real modding needs pull
sections into existence — the building visit-system deep dive (full
per-family item/cost writeups) is probably the next highest-value target
given it's directly relevant to "add research/purchase to an existing
building." Whatever gets pulled in must meet the evidence standard above.

## Process Notes for Future Sub-Agent Dispatches

- Use `general-task-execution` (full tool access), not `context-gatherer`
  (read-mostly — will ask the user to run commands manually instead of
  writing findings itself).
- For investigation, use `grep_search`/`read_file`/`read_files` directly —
  no shell needed. If a script is genuinely needed (e.g. extracting CAM/
  STRT data), overwrite `utility/test_decoder.py` (the project's one
  named, trusted scratch-script convention per `.kiro/steering/majesty-
  modding.md`) and run it via `python utility/test_decoder.py` — don't
  invent new scratch file names, don't reach for PowerShell for tasks the
  dedicated search/read tools already cover.
- Dispatch sequentially, not in parallel, when multiple agents write to
  the same file — concurrent `str_replace`s on one doc will clobber each
  other. Have each agent re-read the target file immediately before
  editing, since prior agents in the sequence may have appended sections
  since it was first read.
- One dispatch in this research thread failed outright with a tool-side
  error before writing anything — always verify via `git status`/`grep`
  that a dispatch's claimed edit actually landed before treating the topic
  as done.
