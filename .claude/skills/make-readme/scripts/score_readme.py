#!/usr/bin/env python3
"""
score_readme.py: lint a README against the evidence-based rubric in
references/evidence.md (40 top-starred OSS dev-tool READMEs + guide consensus).

Usage:
    python3 score_readme.py README.md [--repo PATH] [--json] [--strict]

--repo PATH   also verify that relative links and images resolve on disk
--strict      exit 1 if any CRITICAL check fails (use in CI)

Prints a score out of 100, then every failed check with the specific fix.
Standard library only.
"""

import json
import os
import re
import signal
import sys
from dataclasses import dataclass
from itertools import pairwise

try:
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # tolerate `| head`
except (AttributeError, ValueError):
    pass

CRIT, IMPT, MINR = "CRITICAL", "IMPORTANT", "MINOR"
SEVERITY_WEIGHTS = {CRIT: 10, IMPT: 6, MINR: 3}
READ_LIMIT = 200_000
_BADGE_SRC = re.compile(r"shields\.io|badge|badgen", re.IGNORECASE)


def _read_text(path: str, limit: int = READ_LIMIT) -> str:
    with open(path, encoding="utf-8", errors="replace") as handle:
        text = handle.read(limit)
        truncated = bool(handle.read(1))
    if truncated:
        print(f"truncated {path} to {limit} bytes", file=sys.stderr)
    return text


def _manifest_is_long_description(repo, filename):
    path = os.path.join(repo, filename)
    if not os.path.exists(path):
        return False
    return bool(re.search(r'(?m)^\s*readme\s*=\s*["\']README|long_description', _read_text(path)))


def strip_code(md):
    return re.sub(r"```.*?```", "", md, flags=re.DOTALL)


@dataclass(frozen=True)
class _ReadmeSignals:
    body: str
    lines: int
    head: str
    h1s: list[str]
    html_title: re.Match[str] | None
    h2s: list[str]
    fences: list[str]
    opening: list[str]
    badges: list[str]
    nonbadge: list[tuple[str, str]]


def _readme_signals(md: str) -> _ReadmeSignals:
    body = strip_code(md)
    lines = md.count("\n") + 1
    head = md[:1800]
    h1s = re.findall(r"(?m)^# .+", body)
    html_title = re.search(r"<h1[^>]*>", md, re.IGNORECASE)
    h2s = re.findall(r"(?m)^## (.+)", body)
    fences = re.findall(r"```([a-zA-Z0-9+#-]*)", md)
    # Even indices are opening fences: the regex matches every ``` delimiter.
    opening = fences[0::2] if len(fences) > 1 else fences
    badges = re.findall(
        r"!\[[^\]]*\]\((https?://[^)]*(?:shields\.io|badge|badgen)[^)]*)\)", md, re.IGNORECASE
    ) + re.findall(r"<img[^>]+src=[\"\']([^\"\']*(?:shields\.io|badge|badgen)[^\"\']*)", md, re.IGNORECASE)
    return _ReadmeSignals(body, lines, head, h1s, html_title, h2s, fences, opening, badges, _nonbadge_images(md))


def _nonbadge_images(text: str) -> list[tuple[str, str]]:
    html_imgs = []
    for tag in re.findall(r"<img[^>]*>", text, re.IGNORECASE):
        alt_m = re.search(r'alt=["\']([^"\']*)', tag)
        src_m = re.search(r'src=["\']([^"\']*)', tag)
        html_imgs.append((alt_m.group(1) if alt_m else "", src_m.group(1) if src_m else ""))
    imgs = re.findall(r"!\[([^\]]*)\]\(([^)\s]+)", text) + html_imgs
    return [(a, s) for a, s in imgs if not _BADGE_SRC.search(s or "")]


def check(md: str, repo: str | None = None) -> tuple[list[dict], dict]:
    sig = _readme_signals(md)
    body = sig.body
    lines = sig.lines
    head = sig.head
    h1s = sig.h1s
    html_title = sig.html_title
    h2s = sig.h2s
    fences = sig.fences
    opening = sig.opening
    badges = sig.badges
    nonbadge = sig.nonbadge
    checks: list[dict] = []

    def add(ok, sev, cid, msg, fix=""):
        checks.append({"ok": bool(ok), "sev": sev, "id": cid, "msg": msg, "fix": fix})

    # ---- CRITICAL ----
    logo_title = bool(re.search(r"<img[^>]+alt=[\"\'][^\"\']+", md[:700], re.IGNORECASE)) and len(h1s) == 0
    add(
        len(h1s) == 1 or html_title or logo_title,
        CRIT,
        "title",
        "The project is identified at the very top (H1, <h1>, or a logo with alt text)",
        f"Found {len(h1s)} markdown H1s and no titled logo. Use exactly one title; extra or missing H1s break GitHub's outline.",
    )
    if logo_title:
        add(
            False,
            MINR,
            "text-title",
            "Project name appears as text, not only inside an image",
            "The title is an image only. Add an H1 with the project name so search, screen readers, "
            "and GitHub's outline can find it; keep the logo above it.",
        )
    elif len(h1s) > 1:
        add(False, IMPT, "single-h1", "Exactly one H1", f"{len(h1s)} H1s. Demote all but the first to H2.")
    tagline = next(
        (
            line.strip()
            for line in re.split(r"\n", re.sub(r"<[^>]+>", "", head))
            if 20 <= len(line.strip()) <= 200
            and not line.strip().startswith(("#", "!", "[", "<", "|", "-", "="))
            and not re.search(r"shields\.io", line)
        ),
        None,
    )
    add(
        tagline,
        CRIT,
        "tagline",
        "One-sentence description near the top",
        "No prose sentence found in the first ~1.8 KB. Add a <=120 character line saying what this is and for whom.",
    )
    if tagline:
        add(
            len(tagline) <= 140,
            MINR,
            "tagline-length",
            "Tagline is short enough to scan",
            f"Tagline is {len(tagline)} chars. Trim to <=120; move detail into Features.",
        )
    install_re = r"(?m)^\s*(npm i |npm install|pnpm add|yarn add|bun add|python3? -m pip|pip3 install|pip install|pipx install|uv (tool )?(add|install|pip)|brew install|cargo install|go install|go get|docker run|docker compose|apt(-get)? install|dnf install|winget install|scoop install|choco install|gem install|composer require|curl [^\n|]*\| ?(sh|bash)|git clone|npx |uvx |make install)"
    add(
        re.search(install_re, md),
        CRIT,
        "install",
        "An install or run command is present",
        "No recognizable install/run command found. Add one fenced ```bash block with the single most common install path.",
    )
    add(
        len(fences) // 2 >= 1,
        CRIT,
        "example",
        "At least one fenced code block (usage example)",
        "No fenced code block. Add a minimal runnable example, under ~15 lines, with its expected output.",
    )
    add(
        re.search(r"(?i)licen[sc]e", md),
        CRIT,
        "license",
        "License is stated",
        "No mention of a license. Add a final '## License' section naming the license and linking LICENSE.",
    )

    # ---- IMPORTANT ----
    add(
        re.search(r"(?im)^#{2,3}\s*(install|getting started|quick ?start|setup|usage)", body),
        IMPT,
        "install-heading",
        "Has an Installation or Quick start heading",
        "Add '## Installation' and/or '## Quick start'. 52% of top repos use each.",
    )
    add(
        1 <= len(badges) <= 8 or len(badges) == 0,
        IMPT,
        "badge-count",
        "Badge count is sane (0, or 1 to 8)",
        f"{len(badges)} badges. Cut to 3 to 6, ordered CI, version, license, downloads, chat.",
    )
    if len(badges) == 0:
        add(
            False,
            MINR,
            "badge-missing",
            "Has badges",
            "No badges. Add 3 to 6 (CI, version, license) if the project is published or CI-tested; skip if neither.",
        )
    visual_early = bool(_nonbadge_images(head))
    code_early = "```" in md[:2500]
    add(
        visual_early or code_early,
        IMPT,
        "hero",
        "Visual proof or a code example above the fold",
        "Nothing visual in the first screenful. Add a demo GIF/screenshot, or move the first code example up.",
    )
    add(
        re.search(r"(?i)\[[^\]]*\]\([^)]*(docs?|documentation|guide|wiki)[^)]*\)|https?://docs\.", md),
        IMPT,
        "docs-link",
        "Links to documentation",
        "No documentation link. 90% of top repos link a docs site or docs/ file. Add one.",
    )
    add(
        re.search(r"(?i)contributing", md),
        IMPT,
        "contributing",
        "Contributing is addressed (ideally as a link)",
        "No mention of contributing. Add one sentence plus a link to CONTRIBUTING.md.",
    )
    tagged = sum(1 for f in opening if f) if opening else 0
    add(
        not opening or tagged / max(1, len(opening)) >= 0.8,
        IMPT,
        "fence-lang",
        "Code fences are language-tagged",
        f"{len(opening) - tagged} of {len(opening)} fences lack a language tag. Use ```bash, ```python, ```ts.",
    )
    add(
        4 <= len(h2s) <= 14,
        IMPT,
        "section-count",
        "Between 4 and 14 top-level sections",
        f"{len(h2s)} H2 sections. Median top repo has ~10. Merge or move extras into docs/.",
    )
    add(
        50 <= lines <= 320,
        IMPT,
        "length",
        "Length is in the 50 to 320 line band",
        f"{lines} lines. Median top-tier README is ~128. Long ones belong in docs/; short ones are missing substance.",
    )
    placeholders = re.findall(r"\{\{[^}]+\}\}|INSTRUCTIONS|TODO|FIXME|Lorem ipsum|<!-- INSTRUCT", md)
    add(
        not placeholders,
        IMPT,
        "placeholders",
        "No template placeholders or TODOs left",
        f"Found: {sorted(set(placeholders))[:6]}. Remove every one before shipping.",
    )

    # ---- MINOR ----
    add(
        all(a.strip() for a, s in nonbadge) if nonbadge else True,
        MINR,
        "alt-text",
        "Every non-badge image has alt text",
        "One or more images have empty alt text. Describe what the image shows.",
    )
    github_blob_links = re.findall(r"\]\(https://github\.com/[^/]+/[^/]+/(?:blob|tree)/[^)]+\)", md)
    long_desc = bool(repo) and any(
        _manifest_is_long_description(repo, f) for f in ("pyproject.toml", "setup.cfg", "setup.py")
    )
    add(
        len(github_blob_links) <= 2 or long_desc,
        MINR,
        "relative-links",
        "In-repo files are linked relatively",
        f"{len(github_blob_links)} absolute github.com/blob links. Use relative links (LICENSE, docs/x.md); GitHub rewrites them per branch.",
    )
    toc = bool(re.search(r"(?im)^#{2,4}\s*(table of contents|contents)\b", body))
    add(
        not (toc and lines < 150),
        MINR,
        "toc",
        "No table of contents on a short README",
        "TOC on a README under 150 lines. GitHub auto-generates an outline; delete the manual TOC.",
    )
    if h2s:
        add(
            re.search(r"(?i)licen[sc]e", h2s[-1]) or not any(re.search(r"(?i)licen[sc]e", h) for h in h2s),
            MINR,
            "license-last",
            "License is the final section",
            f"Last section is '{h2s[-1]}'. In 100% of top repos that have one, License is last.",
        )
    levels = [len(m.group(1)) for m in re.finditer(r"(?m)^(#{1,6}) ", body)]
    skips = sum(1 for a, b in pairwise(levels) if b - a > 1)
    add(
        skips == 0,
        MINR,
        "heading-levels",
        "No skipped heading levels",
        f"{skips} level jumps (e.g. H2 straight to H4). Keep the hierarchy contiguous.",
    )
    add(
        re.search(r"(?i)/issues|/discussions|discord|slack|matrix\.to|mailing list|forum", md),
        MINR,
        "support",
        "Tells readers where to get help",
        "No support route. Add 2 to 4 lines: bugs to Issues, questions to Discussions/chat, security to SECURITY.md.",
    )
    add(
        len(fences) // 2 >= 2 or re.search(r"(?m)^(\$|>|#)?\s*(Output|=>|Result)", md),
        MINR,
        "expected-output",
        "Shows expected output for an example",
        "No output shown. Add the result of your example so a reader can self-check.",
    )
    add(
        not re.search(r"(?m)^\s*```\w*\s*\n\s*\$ ", md),
        MINR,
        "no-prompt-prefix",
        "Copyable commands have no '$' prompt prefix",
        "Remove '$' prefixes inside code blocks; they break copy-paste.",
    )
    bullets = re.findall(r"(?m)^\s*[-*+] ", md[:3500])
    add(
        len(bullets) <= 12,
        MINR,
        "bullet-restraint",
        "Feature list is 3 to 6 bullets, not a wall",
        f"{len(bullets)} bullets in the first 3.5 KB. Cut to the 3 to 6 that differentiate you.",
    )

    _add_packaging_checks(add, md, nonbadge, long_desc)
    if repo:
        _add_relative_path_checks(add, md, nonbadge, repo)
        _add_manifest_consistency(add, md, repo)

    return checks, {
        "lines": lines,
        "h2": len(h2s),
        "badges": len(badges),
        "code_blocks": len(fences) // 2,
        "images": len(nonbadge),
    }


def _add_packaging_checks(add, md: str, nonbadge: list[tuple[str, str]], long_desc: bool) -> None:
    if not long_desc:
        return
    rel_media = [s for a, s in nonbadge if s and not s.startswith(("http", "data:"))]
    add(
        not rel_media,
        IMPT,
        "pypi-media",
        "Images use absolute URLs (this README is the PyPI long description)",
        f"Relative image paths {rel_media[:3]} render on GitHub but break on the package page. "
        "Use https://raw.githubusercontent.com/OWNER/REPO/BRANCH/path URLs.",
    )
    rel_files = re.findall(r"\]\((?!https?://|#|mailto:)([^)\s]+\.(?:md|txt|MD))\)", md)
    add(
        not rel_files,
        MINR,
        "pypi-links",
        "In-repo file links are absolute (PyPI cannot resolve relative ones)",
        f"Relative links {rel_files[:3]} break on the package page; use full GitHub URLs "
        "when the README is also the long description.",
    )


def _confined_repo_path(repo_real: str, target: str) -> str | None:
    if os.path.isabs(target):
        return None
    candidate = os.path.realpath(os.path.join(repo_real, target))
    try:
        if os.path.commonpath([repo_real, candidate]) != repo_real:
            return None
    except ValueError:
        return None
    return candidate


def _relative_link_path(raw: str) -> str:
    return raw.strip("<>").split("#")[0].split("?")[0]


def _add_relative_path_checks(add, md: str, nonbadge: list[tuple[str, str]], repo: str) -> None:
    repo_real = os.path.realpath(repo)
    broken = []
    for m in re.finditer(r"\]\(([^)\s]+)\)", md):
        t = _relative_link_path(m.group(1))
        if re.match(r"https?://|mailto:|#|data:", t):
            continue
        if t:
            confined = _confined_repo_path(repo_real, t)
            if confined is None or not os.path.exists(confined):
                broken.append(t)
    for _alt, src in nonbadge:
        t = _relative_link_path(src)
        if t and not t.startswith(("http", "data:")):
            confined = _confined_repo_path(repo_real, t)
            if confined is None or not os.path.exists(confined):
                broken.append(t)
    add(
        not broken,
        IMPT,
        "broken-links",
        "All relative links and images resolve",
        f"Missing in repo: {sorted(set(broken))[:8]}",
    )


def _add_manifest_consistency(add, md: str, repo: str) -> None:
    pyproject_path = os.path.join(repo, "pyproject.toml")
    if os.path.exists(pyproject_path):
        pyproject_text = _read_text(pyproject_path)
        python_floor_match = re.search(r'requires-python\s*=\s*["\'][^0-9]*([0-9]+\.[0-9]+)', pyproject_text)
        if python_floor_match:
            floor = python_floor_match.group(1)
            stated = re.findall(
                r"(?i)python\s*(?:version\s*)?(?:>=?\s*|3\.x\s*)?([0-9]+\.[0-9]+)\s*(?:or (?:above|later|newer|higher)|\+)?",
                md,
            )
            bad = [
                v
                for v in stated
                if v.startswith("3.") and tuple(map(int, v.split("."))) < tuple(map(int, floor.split(".")))
            ]
            if stated:
                add(
                    not bad,
                    IMPT,
                    "manifest-consistency",
                    "Stated runtime versions match the manifest",
                    f"README states Python {bad[0]} but pyproject requires >= {floor}" if bad else "",
                )
    package_json_path = os.path.join(repo, "package.json")
    if os.path.exists(package_json_path):
        try:
            engines = json.loads(_read_text(package_json_path)).get("engines")
        except json.JSONDecodeError:
            engines = None
        node_engines = engines.get("node") if isinstance(engines, dict) else None
        if node_engines:
            node_major_match = re.search(r"(\d+)", str(node_engines))
            if node_major_match:
                stated = re.findall(r"(?i)node(?:\.js)?\s*(?:>=?\s*)?v?(\d+)", md)
                bad = [v for v in stated if int(v) < int(node_major_match.group(1))]
                if stated:
                    add(
                        not bad,
                        IMPT,
                        "manifest-consistency",
                        "Stated runtime versions match the manifest",
                        f"README states Node {bad[0]} but package.json engines requires {node_engines}" if bad else "",
                    )


def report(checks: list[dict], stats: dict, as_json: bool = False) -> tuple[int, list[dict]]:
    total = sum(SEVERITY_WEIGHTS[c["sev"]] for c in checks)
    got = sum(SEVERITY_WEIGHTS[c["sev"]] for c in checks if c["ok"])
    score = round(100 * got / total) if total else 0
    grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D" if score >= 60 else "F"
    if as_json:
        print(json.dumps({"score": score, "grade": grade, "stats": stats, "checks": checks}, indent=2))
        return score, checks
    print(f"README SCORE  {score}/100  (grade {grade})")
    print(
        f"  {stats['lines']} lines | {stats['h2']} sections | {stats['badges']} badges | "
        f"{stats['code_blocks']} code blocks | {stats['images']} images\n"
    )
    for sev in (CRIT, IMPT, MINR):
        bad = [c for c in checks if not c["ok"] and c["sev"] == sev]
        if bad:
            print(f"{sev} ({len(bad)})")
            for c in bad:
                print(f"  [{c['id']}] {c['msg']}")
                print(f"      FIX: {c['fix']}")
            print()
    passed = [c["id"] for c in checks if c["ok"]]
    print(f"PASSED ({len(passed)}): {', '.join(passed)}")
    return score, checks


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    path = args[0] if args else "README.md"
    repo = None
    if "--repo" in sys.argv:
        i = sys.argv.index("--repo")
        repo = sys.argv[i + 1] if i + 1 < len(sys.argv) else None
    checks, stats = check(_read_text(path), repo)
    score, checks = report(checks, stats, "--json" in sys.argv)
    if "--strict" in sys.argv and any(not c["ok"] and c["sev"] == CRIT for c in checks):
        sys.exit(1)
