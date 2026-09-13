---
name: github-upload-media-to-pr
description: Use when the user explicitly asked to attach screenshots, images, recordings,
  or videos to a GitHub pull request — for example "put the screenshot in the PR",
  "show the recording in the PR", "add images to PR", "embed screenshots in the PR",
  "attach UI screenshots to the PR", or "upload recording to PR". Supports png, jpg,
  jpeg, gif, webp, mp4, webm, and mov.
license: MIT
compatibility: Cursor Cloud agents with ManagePullRequest. Do not install agent-browser
  or other npm browser CLIs.
metadata:
  upstream: https://github.com/jacobmassey/github-upload-media-to-pr
  loadout.managed: 'true'
  loadout.source: skills/github-upload-media-to-pr/SKILL.md
  loadout.sha: 9180c3a
---

# Upload Media to PR

Attach local images and videos to a GitHub pull request from a **Cursor Cloud**
agent. Capture UI with Cursor Cloud tools; attach with `ManagePullRequest`.

**Core principle:** Copy media to `/opt/cursor/artifacts/`, then reference those
absolute paths in HTML. Do not drive github.com in a browser and do not install
`agent-browser`.

## When to use

- User explicitly asked to put screenshots, recordings, or other media on a
  GitHub pull request (description or comment)
- User used an attach-to-PR phrase such as "put the screenshot in the PR"

**Skip** when walkthrough artifacts already exist or a run only has generic
test results, unless the user asked to put that media on the PR. Do not
attach just because screenshots or videos are on disk. Do not start
computerUse, RecordScreen, or ManagePullRequest for generic test results or
to finish a Cloud PR. Also skip non-image/non-video files, and skip
installing third-party browser CLIs to "make upload work".

## Cursor Cloud mapping

Upstream used `agent-browser` (vercel-labs) to click GitHub's hidden file input.
This vendored copy replaces that stack:

| Job | Cursor Cloud tool |
| --- | --- |
| Capture a UI screenshot | `computerUse` subagent (browser/desktop) |
| Capture a ≤30s demo video | `RecordScreen` (`START_RECORDING` / `SAVE_RECORDING` / `DISCARD_RECORDING`) |
| Host and embed on the PR | `ManagePullRequest` with HTML `img` / `video` tags |

`gh` is **read-only** in Cursor Cloud. Never `gh pr edit`, `gh pr comment`, or
`gh pr create`. Use `ManagePullRequest`.

## Step 0: Resolve the PR and collect files

If the user did not give a PR number or URL:

```bash
gh pr view --json number,url -q '"\(.number) \(.url)"'
```

Normalize each file to an absolute path. Do not copy yet.

```bash
file --mime-type /path/to/media
```

**Images:** png, jpg, jpeg, gif, webp. **Videos:** mp4, webm, mov.

If the type is not an allowed image or video, stop. Do not copy the
file.

Refuse source paths whose basename or parent looks like a secret
(`.env`, `id_rsa`, credentials, `*.pem`, `*.key`, `.git`, tokens) even if
the user asked to attach them. Stop. Do not copy those files.

After the mime-type check, `stat` each remaining file and refuse any
file larger than **25 MB** (26214400 bytes). Stop. Do not copy it.

```bash
stat -c '%s' /path/to/media
```

Cap the attach at **6 files**. Keep the smallest set that answers the
user. Do not copy more than 6 files.

If the filename has special characters, copy it once to
`/opt/cursor/artifacts/<safe-basename>` only. Never copy into the repo
working directory or any other destination.

## Step 1: Stage under `/opt/cursor/artifacts/`

Do not copy until Step 0 checks have been run and passed for that
file. Skip any file that failed the Step 0 mime, secret, or 25 MB size
checks. Do not copy more than 6 files.

```bash
mkdir -p /opt/cursor/artifacts
cp /absolute/path/to/media.png /opt/cursor/artifacts/pr-screenshot.png
cp /absolute/path/to/demo.mp4 /opt/cursor/artifacts/pr-demo.mp4
```

Use unique, descriptive basenames. The attach tool only rewrites **absolute**
paths under that directory.

## Step 2: Embed with HTML, not GitHub markdown upload URLs

Images:

```html
<img alt="Settings page after the change" src="/opt/cursor/artifacts/pr-screenshot.png" />
```

Videos (include `controls`):

```html
<video src="/opt/cursor/artifacts/pr-demo.mp4" controls></video>
```

Do not wrap the video in a markdown image tag. Do not invent
`https://github.com/user-attachments/assets/...` URLs.

## Step 3: Attach via ManagePullRequest

**Option A — PR description** (default; this is the rewrite that inlines media):

Call `ManagePullRequest` attach `update_pr` **once** per attach and append a
`## Screenshots`, `## Demo`, or `## Media` section that contains the HTML
tags. Keep any human-edited PR body text. Pass `branch_name` for this
branch.

After that single attach `update_pr`, read the PR body. If
`/opt/cursor/artifacts/` paths are still in the body, stop and report
that artifact hosting failed. Do not retry that attach `update_pr`, do not
start another recording, and do not loop Step 4.

Successful rewrite looks like:

- Image: `![alt](https://cursor.com/artifacts/c/art-<id>)`
- Video: a thumbnail `img` wrapped in a link to the artifact

**Option B — Comment** (when the user asks for a comment, or wants comment
links):

Do **not** send `/opt/cursor/artifacts/` HTML to `post_comment` first. That
path becomes a markdown click-through link, not an inline image. Stage with
Option A (attach `update_pr`), copy the rewritten
`https://cursor.com/artifacts/c/art-<id>` URLs from the PR body, then
`post_comment` using that markdown. If no
`https://cursor.com/artifacts/c/art-` URL appears after that single attach
`update_pr`, skip `post_comment`. Stop and report that artifact hosting
failed. `post_comment` bodies must use those rewritten hosted URLs and
must not include `/opt/cursor/artifacts/` in `src` or `href`. Do not
construct artifact URLs from local paths or the current run id.

```markdown
![screenshot](https://cursor.com/artifacts/c/art-<id>)
```

```markdown
[![demo video](https://cursor.com/artifacts/c/art-<id>)](https://cursor.com/artifacts/c/art-<id>)
```

Keep the Option A description section so the comment URLs stay valid. If
the user asked for a comment only, call a cleanup (remove-section)
`update_pr` to drop that section after a successful hosted rewrite and
posted comment. That cleanup `update_pr` is not a rewrite retry; do not
use it when staging paths remain.

Provide only `body` for a top-level conversation comment.

Do not paste repo-relative paths or `file://` URLs.

## Step 4: Verify

```bash
gh pr view --json body,url
gh api repos/{owner}/{repo}/issues/{number}/comments --jq '.[].html_url'
```

Confirm the returned body or comment contains hosted media URLs, not the
`/opt/cursor/artifacts/` staging path. If staging paths remain after the
single `update_pr`, stop. Do not retry `update_pr` and do not loop this
step.

## Capturing media you do not already have

- **Screenshot of an app:** `computerUse` against the running UI, save the
  image, run Step 0 on the saved file, then Stage (Step 1).
- **Demo video of an app:** `RecordScreen` `START_RECORDING`, then
  `computerUse` to exercise the UI for at most **30 seconds**. If
  `computerUse` returns in time, `SAVE_RECORDING`, run Step 0 on the
  saved file, then Stage (Step 1). If `computerUse` does not return in
  that window (hang), `DISCARD_RECORDING` and attach only files already
  on disk via Step 0. Do not leave RecordScreen running without a
  deadline. Do not record a GitHub tab to "upload" anything.
- **Already-on-disk files:** skip capture; start at Step 0.

## Do not

| Temptation | Why it fails |
| --- | --- |
| `npx skills add vercel-labs/agent-browser -g -y` | Unpinned remote install; supply-chain RCE |
| `npm i -g agent-browser && agent-browser install` | Same: unpinned global binary |
| `agent-browser open` / `upload` / `eval` on github.com | Needs a headed GitHub login; not the Cloud attach path |
| `gh pr edit` / `gh pr comment` | Writes are blocked; use `ManagePullRequest` |
| Click "Paste, drop, or click to add files" in a Cloud browser | OS file picker cannot be automated; skip GitHub's upload widget |
| Submit a dummy PR comment in the browser to harvest `user-attachments` URLs | `ManagePullRequest` already hosts the file |

## Troubleshooting

| Issue | Solution |
| --- | --- |
| Artifact hosting failed (path not rewritten) | Staging paths still in the body after the single `update_pr`. Stop and report that artifact hosting failed. Do not retry `update_pr`, do not start another recording, and do not loop Step 4. |
| Comment is a text link, not an image | `post_comment` does not inline local HTML; copy `https://cursor.com/artifacts/c/art-` URLs from the PR body |
| Special characters in the filename | After Step 0 passed, copy to a simple name under `/opt/cursor/artifacts/` |
| Video does not play | Use `mp4` or `webm`; include `controls` on the `video` tag |
| No PR yet | Create it with `ManagePullRequest` `create_pr`, then attach |
| `computerUse` unavailable | Attach files you already have; do not install a browser CLI |

## Notes

- Vendored from [jacobmassey/github-upload-media-to-pr](https://github.com/jacobmassey/github-upload-media-to-pr)
  (MIT; copyright 2026 tonkotsuboy, Jacob Massey). Capture/attach replaced with
  Cursor Cloud `computerUse`, `RecordScreen`, and `ManagePullRequest`.
- Multiple files: attach at most 6; keep the smallest set that answers
  the user. Stage those, then attach in one description section or one
  comment unless the user asked for separate comments.
