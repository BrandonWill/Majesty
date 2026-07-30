# Ghidra Machine — Start Here

**Purpose of this file:** everything the Ghidra-machine session needs to
begin work, in one place, so it doesn't have to explore the repo or ask
where things are. Read this file and the ones it points to — nothing
else in the repo should be needed to start.

## Do you need `Majesty_Files`?

**No, not for the work currently queued.** All of it targets
`MajestyHD.exe` disassembly/decompilation directly — none of it requires
reading the game's data files (`Data/`, `DataMX/`, `Quests/`, etc., which
live in the separate `Majesty_Files` repo). If a specific task step below
ever says otherwise, that step will say so explicitly. Don't open or
clone `Majesty_Files` by default.

## Required Reading, In Order

1. **This file** (you're here).
2. **`TODO-Ghidra.md`** (same folder as this file) — the actual task
   list. Read its "Work Order" section at the top first — it tells you
   exactly which Priority section to work on right now, out of numeric
   order if needed. Then jump straight to that section; you don't need
   to read the whole file top to bottom before starting.
3. **Whatever the current Work Order item's own "Record results in"
   line points to** — usually one of:
   - `SMNUResearch/findings/exe_disassembly_results.md`
   - `SMNUResearch/findings/action_codes_decoded.md`
   - `SMNUResearch/findings/smnu_parser_decompilation.md`
   - `SMNUResearch/findings/nav_button_pattern.md`
   - `SMNUResearch/FUTURE_TODO.md`

   Read the specific section named, not the whole file, unless the task
   step says to read more.

That's it. Don't read `CAM_MODDING_GUIDE.md`, `GPL_MODDING_GUIDE.md`,
`GPL_QUEST_RULES_REFERENCE.md`, the `TODO-New-Hero-Requirements.md`/
`TODO-New-Building-Requirements.md` research docs, or anything under
`.kiro/steering/` unless a specific task step below explicitly tells you
to — those exist for the local-machine research work, not exe patching,
and pulling them in wastes tokens on context you won't use.

**One exception, and it's write-only:** Priority 5, 6 and 7 in
`TODO-Ghidra.md` say to record results at a cited `§`-number. Those
numbers split across two files — **`§1`-`§15` are in
`GPL_MODDING_GUIDE.md`, `§16`-`§22` are in `GPL_QUEST_RULES_REFERENCE.md`**
(same folder). Open the one that owns the number, jump to that
subsection, append your finding there. You still don't need to read
either file end to end.

## Setup (confirm before starting any task)

- **Binary:** `MajestyHD.exe`
- **Ghidra project:** `MajestyRE` — confirm the project path on this
  machine (varies by machine; check your Ghidra install/recent-projects
  list if unsure, don't assume a specific path from an old note).
- **Tool:** Ghidra MCP — decompile functions, search strings, get xrefs,
  read disassembly.
- Known confirmed/unconfirmed function addresses are tracked in
  `TODO-Ghidra.md`'s "Known EXE Addresses" table at the bottom of that
  file — check there before re-deriving an address from scratch, and add
  any new one you confirm to that same table.

## Current Work Order (full detail lives in `TODO-Ghidra.md`)

1. **Priority 1 — Sub-Panel Navigation Action Code.** In progress
   already; continue from where the last session left off. Target: the
   building sub-panel click handler / code-8013 dispatcher /
   `OpenPanelByName` (`FUN_004b0ce0`, unconfirmed).
2. **Priority 3.4 — Research Item Click Dispatch.** Do this next, ahead
   of Priority 2/3 numerically — no dependency on Priority 1, and it
   unblocks the most other queued work (SMNU new-button task, hero
   recruit-cost gap, building combined-case gap). Target:
   `FUN_004a8510`/`FUN_004a83e0`/`FUN_004a94c0` (all unconfirmed
   addresses from an earlier binary-patch experiment, not yet
   decompiled).
3. After that, resume Priority 2, 3, 3.5, 4, 5, 6 in `TODO-Ghidra.md`'s
   existing numeric order, unless that file's Work Order note says
   otherwise by the time you get there.

## When You Finish a Task or Discover Something

Update the specific file `TODO-Ghidra.md`'s own table at the top says to
update for that kind of finding (new address → its own "Known EXE
Addresses" table; SMNU/panel format → `smnu_parser_decompilation.md`;
action codes → `action_codes_decoded.md`; etc.). Then mark the
corresponding checklist item done in `TODO-Ghidra.md` itself. Don't wait
until the end of a session to write things down — if a dispatch runs out
of budget mid-task, whatever's already been written to these files is
what survives; nothing held only in conversation does.

## If You Get Stuck / Think You Need Another File

Before opening something not listed above, check `TODO-Ghidra.md`'s
per-task "Background"/"Steps" text for the specific task you're on — it
usually already names the exact file/section to cross-reference. If it
genuinely doesn't and you need something else, that's a real gap in this
task file — note what you needed and why in your findings so it can be
added here for next time, rather than silently exploring the whole repo.
