---
inclusion: manual
---

# Research Sub-Agent Dispatch Standards

Use this steering file (`#research-dispatch-standards`) whenever writing a
prompt to dispatch a sub-agent (or another Kiro session) to do citation-
backed research on any of this project's TODO/research docs
(`TODO-GPL-Deepdive.md`, `TODO-New-Hero-Requirements.md`,
`TODO-New-Building-Requirements.md`, or similar future docs). It exists
because two real failures already happened without it: a large
single-edit dispatch pattern crashed mid-write and lost all its work
before landing anything, and un-cited claims from assumed analogy between
similar-looking systems had to be retracted later. Every dispatch prompt
built from this file should include all five sections below, filled in
for the specific task — don't skip sections because they seem obvious for
a small task; the discipline is what prevents the two failure modes.

## 1. Evidence Standard (state this verbatim or equivalent)

> Every claim must cite a specific file/line/function (GPL), a real
> shipped XML attribute example, or a real extracted example (via
> `cam_reader.py`/`sprite_extractor.py`/direct file read) it was verified
> against. **No claim from assumed analogy** — similar-looking systems
> (e.g. two building types, a hero vs. a building, two guild families)
> must each be independently confirmed from their own source, not
> inferred from the other. If something can't be confirmed, mark it
> explicitly **UNVERIFIED**/**UNKNOWN** — do not guess, and do not soften
> an unconfirmed claim into confident-sounding prose.

## 2. Style/Rigor Template — point at a real prior example

Every dispatch prompt must name a specific already-completed section of
an existing doc as the style template, and instruct the sub-agent to
read it FIRST, before writing anything. Don't just say "match the
existing style" — name the file and section. Good examples to point at:
- `TODO-New-Hero-Requirements.md` §1 (sprite/animation-set research)
- `TODO-New-Building-Requirements.md` §1-§3 (sprite, XML, `.dat` research)
- `GPL_MODDING_GUIDE.md`'s "Retracted Claims" section — the canonical
  example of how to visibly correct an earlier claim rather than
  silently overwrite it

## 3. Exact Scope — quote or closely paraphrase the checklist items

List the exact checklist item(s)/section(s) to research, and tell the
sub-agent to re-read the target doc itself to get the current exact
wording rather than restating from memory (the doc may have changed
since the dispatch prompt was written). Explicitly state what NOT to
touch — sub-agents should only modify the section(s) they were asked to
research, never adjacent sections, even if they notice something worth
fixing there (flag it in their final summary instead).

## 4. Method — name the actual tools/scripts to use

- `grep_search`/`read_file`/`read_files` for all source investigation
  (GPL, XML, `.dat`, steering docs) — no shell needed for this.
- If CAM/sprite extraction is genuinely needed: write the extraction
  code into `utility/test_decoder.py` (via `fs_write`/`str_replace`,
  the same file-editing tools used for everything else) — the ONE
  named, trusted scratch script for this project (per
  `.kiro/steering/majesty-modding.md`) — then run it with
  `execute_pwsh` using EXACTLY `python utility/test_decoder.py` as the
  command, nothing else appended or piped.
- **Do not invent new scratch script names, do not run inline
  `python -c "..."`, and do not use any other PowerShell/shell
  command for investigation** — this project has already needed to
  stop and re-approve an ad hoc shell command mid-dispatch once; the
  whole point of the one-named-script convention is that
  `python utility/test_decoder.py` is pre-approved/low-friction and a
  novel shell invocation is not. **State this explicitly in every
  dispatch prompt** (don't assume it's implied from the general rule
  above) — e.g.: "The ONLY shell command you may run in this task is
  `python utility/test_decoder.py`, with no other arguments, flags,
  piping, or inline code. Write all extraction/investigation logic
  into that file first, then run it exactly that way. Do not run any
  other PowerShell, cmd, git, or python command — if you think you
  need one, stop and describe what you needed in your summary instead
  of running it."
- Suggest specific real candidate examples to extract/read when you
  already know good ones (e.g. "compare `ABF1` Inn against `ABH1/2/3`
  Marketplace tiers") — this saves the sub-agent time discovering them
  itself and steers it toward examples that will actually distinguish
  between competing hypotheses, not just confirm the first one found.

## 5. Write Discipline (the crash-prevention section — non-negotiable)

- **Re-read the target file immediately before each write.** Other work
  may have landed concurrently; this avoids stale-content `str_replace`
  failures.
- **Write incrementally, one checklist item at a time.** After finishing
  investigation for ONE item, immediately `str_replace` that item's
  `- [ ]` line into `- [x]` with findings, then move to the next item.
  **Do not accumulate multiple items in memory and write them in one
  giant edit at the end** — this is exactly the pattern that caused a
  real crash-mid-write data loss in this project's history.
- **If a claim is retracted/corrected within the same session, keep the
  correction visible** — prepend or append the correction, don't
  silently overwrite the original wrong claim. Matches this project's
  existing "Retracted Claims" convention.
- End by re-reading the file (or `grep_search`ing for the new content)
  to **confirm the edits actually landed** before reporting completion —
  don't just trust that the `str_replace` calls succeeded.

## Dispatch Prompt Checklist

Before sending a dispatch prompt, confirm it includes:
- [ ] The evidence standard (§1), stated explicitly, not just implied
- [ ] A named style-template file/section to read first (§2)
- [ ] The exact scope, with instruction to re-read the target doc for
  current wording, and an explicit "don't touch other sections" note (§3)
- [ ] Named tools/scripts, including the scratch-script rule, and
  optionally suggested real examples (§4)
- [ ] The explicit "only shell command allowed is
  `python utility/test_decoder.py`, exactly that, nothing else" line
  from §4 — spelled out, not left implied
- [ ] The full write-discipline block (§5), not a shortened paraphrase
- [ ] A final instruction to report back a short summary AND confirm the
  edits landed (re-read or grep)
