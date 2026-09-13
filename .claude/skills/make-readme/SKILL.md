---
name: make-readme
description: Use when the user asks to write, generate, improve, rewrite, review,
  fix, or score a README; when a repo has no README or a weak one; or when they invoke
  /make-readme.
license: MIT
metadata:
  loadout.managed: 'true'
  loadout.source: skills/make-readme/SKILL.md
  loadout.sha: 9180c3a
---

# make-readme

Produce a README that a stranger can evaluate in ten seconds and use in sixty.

The structure here is not taste. It comes from measuring the 40 most-starred OSS developer-tool
repositories on GitHub (September 2026), 114 curated "great README" write-ups, and six
mainstream guides. `references/evidence.md` carries the numbers and the method. When a decision
is contested, the corpus wins.

## Non-negotiable rules

1. **Never invent facts.** No benchmark numbers, no feature you have not seen in the code,
   no license you have not read in the LICENSE file, no Discord link you cannot verify. If a
   fact is missing, either omit the element or ask. An impressive lie in a README is a bug report.
2. **Never link a file that does not exist.** CONTRIBUTING.md, SECURITY.md, LICENSE, docs/,
   images: check each one on disk before linking it. Offer to create the missing file instead.
3. **Read the manifest for every version claim.** Runtime floors, package names, extras, and
   entry points come from `pyproject.toml`, `package.json`, `Cargo.toml`, or `go.mod`, never from
   memory or from the previous README. Version drift between README and manifest is the most
   common factual defect found in real repos.
4. **Verify commands.** Every install and quick-start command must be traceable to a manifest,
   a published package, or a script in the repo. Run them when the environment allows it. Mark
   anything you could not verify and tell the user in your summary.
5. **Cut before you add.** The median top-tier README is ~128 lines and ~10 sections. A section
   that exists because a template had it is worse than no section.
6. **Preserve what already works.** When improving an existing README, keep its working badges,
   real community links, hard-won troubleshooting notes, and its voice. You are editing, not
   replacing a person's work.

## Workflow

### Step 1: Establish mode and target

- `create`: no README, or the user wants a fresh one.
- `improve`: a README exists. Default to this whenever one is present.
- `review`: the user wants a critique or score only. Do Steps 2 and 6, skip the writing.

If the target is a remote repo, clone it shallowly first
(`git clone --depth 1 <url>`); if you cannot clone, fetch the raw README and work from the
user's answers alone, and say plainly that repo facts were unverified.

### Step 2: Gather facts from the repo, not from memory

```bash
python3 scripts/inspect_repo.py /path/to/repo
```

This prints identity, manifests, ecosystems, likely install commands, license detection, CI
workflows, docs dirs, media assets, community links, health files, and a GAPS list.
Then read enough of the actual code to describe it honestly: the entry point, the main
module or CLI definition, one real usage path. A README written from the manifest alone
reads like it was written from the manifest alone.

If a README already exists:

```bash
python3 scripts/score_readme.py /path/to/repo/README.md --repo /path/to/repo
```

Corpus calibration: the 40 top-starred repos score a median of 81 on this rubric
(p25 75, p75 89, range 59 to 98). Target 90+, and never ship with a CRITICAL failure.

### Step 3: Classify the project and pick the preset

Read `references/project-types.md` and choose one: CLI tool, library/SDK, web app or
self-hosted service, framework, AI agent/model tool, plugin/extension, monorepo,
research/dataset, internal repo, or template repo. The preset decides which optional
sections survive and what the hero visual should be.

### Step 4: Ask only what you cannot determine

Ask at most 3 to 5 questions, in one batch, only for facts the repo cannot answer. The usual
unknowns: who the audience is, whether a hosted version exists, which support channel is
actually monitored, whether a demo asset can be produced, and any license nuance. Include
your best guess with each question so the user can confirm rather than compose.

If the user is unavailable (unattended run), pick the most conservative reading, omit any
element that would require an unverified claim, and list every assumption at the top of
your final summary.

### Step 5: Write

Work from `README_TEMPLATE.md`. Its inline instruction blocks carry the per-section rules;
`references/section-playbook.md` carries the reasoning and the failure modes, and
`references/badges.md` has copy-paste badge URLs.

Canonical order (median positions from the corpus):

1. Header block: logo (optional), name, one-sentence tagline, 3 to 6 badges
2. Hero visual: GIF for a CLI, screenshot for an app, first code block for a library
3. Features: 3 to 6 bullets, bold benefit first, differentiators only
4. Installation: one primary command, prerequisites on one line, extras in `<details>`
5. Quick start: smallest runnable example plus its expected output
6. At most one domain section: integrations table, deployment, comparison, or architecture
7. Documentation: docs home plus up to 3 deep links
8. Community and support: routed by intent, 2 to 4 lines
9. Contributing: one sentence plus a link to CONTRIBUTING.md
10. License: one line, named explicitly, always last

Writing rules that the corpus and the guides agree on:

- Second person, present tense, active voice. "Install it with", not "It can be installed by".
- Lead every section with the thing itself, not with a preamble sentence.
- Language-tag every fence. No `$` prompts inside copyable blocks.
- Relative links for in-repo files; absolute only for external sites.
- Alt text on every image.
- Exactly one H1. No skipped heading levels.
- No emoji in heading text (10% of the corpus; it ages badly and breaks anchors).
- No table of contents under ~150 lines; GitHub generates an outline automatically.
- Tables only for genuinely tabular reference data, capped at ~12 rows.
- Do not describe unreleased work in the present tense.

In `improve` mode, work section by section against the score report: fix every CRITICAL,
then every IMPORTANT, then the MINORs that do not cost the author's voice. Keep a short list
of what you changed and why.

### Step 6: Verify before delivering

```bash
python3 scripts/score_readme.py README.md --repo /path/to/repo
grep -n "INSTRUCTIONS" README.md   # must return nothing
grep -n "{{" README.md             # must return nothing
```

Then check by hand what the linter cannot:

- [ ] The install command was actually run, or is traceable to a published package.
- [ ] The quick-start example was run and its output is what the README claims.
- [ ] Every badge URL resolves and its link target is correct.
- [ ] Every claim in Features is backed by code you read.
- [ ] The tagline matches the GitHub repo description and the package manifest description;
      if they differ, tell the user which ones to update.
- [ ] Nothing was silently dropped from the previous README that the author will miss.
- [ ] If the README doubles as a registry long description (pyproject `readme`, setup.py
      `long_description`), every image and in-repo link is an absolute URL. The linter checks this.
- [ ] Any limitation or caveat you carried over is still true in the newest CHANGELOG entry.
- [ ] Any list that duplicates a docs page names that page as the source of truth.

### Step 7: Deliver

Write `README.md` in the repo. Report back with: the score before and after, the sections
added, cut, and rewritten, every assumption you made, every command you could not verify,
and any missing health file (LICENSE, CONTRIBUTING.md, SECURITY.md, demo asset) that the
user should create next. Offer to draft those files.

## Anti-patterns to refuse

| Anti-pattern | Why | Do instead |
| --- | --- | --- |
| Badge wall (9+ badges) | Pushes the value proposition below the fold | 3 to 6, each answering a real question |
| "This project is a tool that..." | Wastes the highest-value line in the file | Lead with the category and the differentiator |
| Inlined full API or config reference | Goes stale, buries the quick start | Link the docs; keep the README a signpost |
| Manual TOC on a short README | Duplicates GitHub's outline, always rots | Delete it |
| Roadmap of unshipped features in Features | Reads as vaporware once dates slip | Link an issue or a Projects board |
| Copy-pasted CoC / contributing boilerplate | Nobody reads it in a README | CONTRIBUTING.md and CODE_OF_CONDUCT.md |
| Unverified benchmark claims | The fastest way to lose credibility | Cite a reproducible command, or cut it |
| Emoji headings and decorative dividers | Break anchors, age badly, cost scannability | Plain headings |
| A screenshot of code | Unsearchable, unreadable on mobile | A fenced code block |
| Install instructions for six package managers up top | Buries the 90% path | Primary command, rest in `<details>` |

## Files in this skill

| File | Use it for |
| --- | --- |
| `README_TEMPLATE.md` | The template itself, with per-section instructions inline |
| `references/evidence.md` | The data: frequencies, POPULAR/UNPOPULAR verdicts, method |
| `references/section-playbook.md` | Per-section best practices, rules, and failure modes |
| `references/badges.md` | Badge URLs by ecosystem, ordering, what to avoid |
| `references/project-types.md` | Ten presets: what to add and cut per project type |
| `scripts/inspect_repo.py` | Read-only repo fact sheet plus a gaps list |
| `scripts/score_readme.py` | Rubric linter, 0 to 100 score, exact fixes, `--strict` for CI |
| `scripts/corpus_analyzer.py` | Reproduce the evidence.md frequencies from the 40-repo corpus |
