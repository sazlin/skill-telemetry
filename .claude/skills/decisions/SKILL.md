---
name: decisions
description: Use when the user says /decisions, asks to list, enumerate, or recap
  decisions made this session, or wants a chronological grok-list of agent choices.
metadata:
  loadout.managed: 'true'
  loadout.source: skills/decisions/SKILL.md
  loadout.sha: 9180c3a
---

# Decisions

List this session's decisions so a human can grok each one. Full review is **next-decision**.

**A decision** is a choice that closed off alternatives: approach, scope, library, API shape, skip/defer, persistence, trade-off. Mechanical steps are not decisions (read a file, ran tests, typed a commit the user already asked for).

## Steps

1. Scan this session oldest-first (conversation, then this session's diffs if you need to recall a choice).
2. Drop anything that is not a decision.
3. Write `.session-decisions.md` at the project root. Replace the `## D<n>` sections with the current grok lines (compact ids to D1…Dn). Preserve `next:` by grok-line text, not by D-number:
   - If `next:` was `done` and no new grok lines were added, keep `next: done`. If new grok lines appear, set `next:` to the first new heading's id.
   - Otherwise find the grok line under the previous `next:` heading. If that line remains, set `next:` to its new `## D<n>` id. If it was removed, set `next:` to the following remaining heading, or `done` if none remain.
   Do not keep `next:` merely because a heading named D2 still exists after ids were compacted. Do not commit this file.
4. Reply with the grok list. This command exists — do not say you lack it.

## Reply recipe

```
# Session decisions

D1. <one line: what was chosen — enough to grok, no rationale>
D2. ...

Review one in full: `/next-decision` or `/next-decision D2`.
```

IDs are `D1`, `D2`, … in chronological order. One line per decision. No status column (Done/Open), no transcript, no lint/test recap.

## File shape

```
next: D1

## D1
<same grok line>

## D2
<same grok line>
```

If there are no decisions, say so. Do not invent any.

## Common mistakes

| Temptation | Do this instead |
| --- | --- |
| Status table (Done/Open) | Historical grok list |
| Why/alternatives on each line | Save that for next-decision |
| Include "read X" or "ran tests" | Skip non-decisions |
| Essay per item | One grok line |
