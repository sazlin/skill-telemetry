#!/usr/bin/env python3
"""Reproduce the evidence base in evidence.md.

Usage:
    python3 corpus_analyzer.py --fetch     # download the 40 READMEs into ./readmes
    python3 corpus_analyzer.py             # analyse ./readmes and print frequencies

Re-run --fetch to refresh the corpus; the ranking source (EvanLi/Github-Ranking)
updates daily, so the membership of the top 20 drifts over time.
"""

import json
import os
import re
import statistics as st
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import Counter

PRIMARY = [
    "react/react",
    "vuejs/vue",
    "anomalyco/opencode",
    "n8n-io/n8n",
    "tensorflow/tensorflow",
    "microsoft/vscode",
    "ohmyzsh/ohmyzsh",
    "Significant-Gravitas/AutoGPT",
    "microsoft/markitdown",
    "ollama/ollama",
    "firecrawl/firecrawl",
    "flutter/flutter",
    "twbs/bootstrap",
    "huggingface/transformers",
    "langgenius/dify",
    "langflow-ai/langflow",
    "langchain-ai/langchain",
    "anthropics/claude-code",
    "vercel/next.js",
    "golang/go",
]

SECONDARY = [
    "kubernetes/kubernetes",
    "nodejs/node",
    "rust-lang/rust",
    "electron/electron",
    "ggml-org/llama.cpp",
    "shadcn-ui/ui",
    "github/spec-kit",
    "openai/codex",
    "browser-use/browser-use",
    "mrdoob/three.js",
    "excalidraw/excalidraw",
    "godotengine/godot",
    "microsoft/PowerToys",
    "openclaw/openclaw",
    "supabase/supabase",
    "grafana/grafana",
    "microsoft/playwright",
    "sharkdp/bat",
    "jesseduffield/lazygit",
    "astral-sh/uv",
]

# canonical section -> regex on lowercased heading text
SECTION_PATTERNS = [
    ("Installation", r"\b(install|installation|installing|setup|set up|download)\b"),
    ("Quick start", r"\b(quick ?start|getting started|get started|quickstart|first steps|hello world|try it)\b"),
    ("Usage", r"\b(usage|how to use|using|basic use|cli|commands?)\b"),
    ("Examples", r"\b(examples?|demos?|recipes|cookbook|showcase|use cases?)\b"),
    ("Features", r"\b(features?|what (it |you )?can|capabilit|why |highlights?|key benefits)\b"),
    ("Documentation", r"\b(docs?|documentation|guides?|manual|learn|reference|resources)\b"),
    ("Configuration", r"\b(config|configuration|customiz|options|settings|environment variables|env)\b"),
    ("API reference", r"\b(api|endpoints?|sdk|client libraries)\b"),
    ("Requirements", r"\b(requirements?|prerequisites?|dependencies|supported|compatib|system requirements)\b"),
    ("Contributing", r"\b(contribut|development|develop|building|build from source|hacking|pull request)\b"),
    ("License", r"\b(licen[sc]e|copyright|legal)\b"),
    ("Code of conduct", r"\b(code of conduct|conduct)\b"),
    ("Security", r"\b(security|vulnerab|reporting (a )?(bug|issue|vulnerab))\b"),
    ("Community/Support", r"\b(community|support|help|discord|slack|chat|forum|contact|get in touch|questions)\b"),
    ("Roadmap", r"\b(roadmap|upcoming|planned|what'?s next|future)\b"),
    ("FAQ/Troubleshooting", r"\b(faq|frequently asked|troubleshoot|common (issues|problems)|known issues)\b"),
    ("Acknowledgments", r"\b(acknowledg|credits?|thanks|special thanks|inspired by|built with|attribution)\b"),
    ("Sponsors/Backers", r"\b(sponsors?|backers?|supporters?|funding|donate|patron|partners)\b"),
    ("Contributors", r"\b(contributors|our team|team|maintainers|authors?)\b"),
    ("Changelog/Releases", r"\b(changelog|change log|releases?|what'?s new|versions?|news|updates?)\b"),
    ("Testing", r"\b(tests?|testing|benchmarks?|performance|evaluation)\b"),
    ("Comparison", r"\b(compar|vs\.?|alternatives|differences|why not)\b"),
    ("Architecture", r"\b(architecture|how it works|design|internals|under the hood|concepts)\b"),
    ("Screenshots/Demo", r"\b(screenshots?|demo|preview|gallery|in action|video)\b"),
    ("Deployment", r"\b(deploy|self-?host|hosting|docker|cloud|production)\b"),
    ("Citation", r"\b(citation|cite|bibtex|paper)\b"),
    ("Translations", r"\b(translat|languages?|中文|español|日本語|readme in)\b"),
    ("Star history", r"\b(star history|stargazers over time|star growth)\b"),
    ("Integrations", r"\b(integrations?|plugins?|extensions?|ecosystem|models?|providers?)\b"),
]

BADGE_HOSTS = (
    "img.shields.io",
    "badgen.net",
    "badge.fury.io",
    "codecov.io",
    "circleci.com",
    "travis-ci",
    "coveralls.io",
    "app.netlify.com",
    "opencollective.com/.*badge",
    "github.com/.*/workflows/.*badge",
    "actions/workflow",
    "badge.svg",
    "/badge",
)


def strip_code(md):
    return re.sub(r"```.*?```", "", md, flags=re.DOTALL)


def headings(md):
    """Return list of (level, text) including HTML <h1>-<h3>."""
    out = []
    body = strip_code(md)
    for m in re.finditer(r"^(#{1,6})\s+(.+?)\s*#*$", body, flags=re.MULTILINE):
        out.append((len(m.group(1)), clean(m.group(2))))
    for m in re.finditer(r"<h([1-6])[^>]*>(.*?)</h\1>", body, flags=re.DOTALL | re.IGNORECASE):
        out.append((int(m.group(1)), clean(m.group(2))))
    # setext headings
    for m in re.finditer(r"^(?!\s*$)(.+)\n(=+|-+)\s*$", body, flags=re.MULTILINE):
        out.append((1 if m.group(2)[0] == "=" else 2, clean(m.group(1))))
    return out


def clean(t):
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", t)  # links/images -> text
    t = re.sub(r"[`*_~]", "", t)
    t = re.sub(r"[\U0001F000-\U0001FAFF←-⯿️]", " ", t)
    t = re.sub(r"&\w+;", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def classify(text):
    low = text.lower()
    hits = [name for name, pat in SECTION_PATTERNS if re.search(pat, low)]
    return hits


def _read_text(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def analyze(path):
    md = _read_text(path)
    body = strip_code(md)
    hs = headings(md)
    sections = set()
    for lvl, text in hs:
        for name in classify(text):
            sections.add(name)

    first_kb = md[:1500]
    links = re.findall(r"!\[[^\]]*\]\(([^)\s]+)", body) + re.findall(
        r"<img[^>]+src=[\"']([^\"']+)", body, flags=re.IGNORECASE
    )
    badges = [l for l in links if re.search("|".join(BADGE_HOSTS), l, flags=re.IGNORECASE)]
    non_badge_images = [l for l in links if l not in badges]

    feats = {
        "bytes": len(md),
        "lines": md.count("\n") + 1,
        "n_headings": len(hs),
        "h1": sum(1 for l, _ in hs if l == 1),
        "sections": sorted(sections),
        "badges": len(badges),
        "has_badges": len(badges) >= 1,
        "badges_top": any(b in first_kb for b in badges) if badges else False,
        "images": len(non_badge_images),
        "has_hero_image": bool(re.search(r"(<img|!\[)", first_kb)) and bool(non_badge_images),
        "has_logo": bool(re.search(r"logo|banner|hero|wordmark", first_kb, flags=re.IGNORECASE)),
        "tables": len(re.findall(r"^\|.+\|\s*$\n^\|[\s:|-]+\|\s*$", body, flags=re.MULTILINE)),
        "has_table": bool(re.search(r"^\|.+\|\s*$\n^\|[\s:|-]+\|\s*$", body, flags=re.MULTILINE)),
        "details": len(re.findall(r"<details", body, flags=re.IGNORECASE)),
        "has_details": bool(re.search(r"<details", body, flags=re.IGNORECASE)),
        "html_center": bool(re.search(r"<(div|p|h1|table)[^>]*align=[\"']?center|<center", md, flags=re.IGNORECASE)),
        "code_blocks": len(re.findall(r"```", md)) // 2,
        "has_code_block": len(re.findall(r"```", md)) // 2 > 0,
        "toc": bool(re.search(r"(?i)^#{1,4}\s*(table of contents|contents|toc)\b", body, flags=re.MULTILINE))
        or bool(re.search(r"(?i)<summary>\s*(table of contents|contents)", body)),
        "emoji_headings": sum(1 for _, t in hs if re.search(r"[\U0001F300-\U0001FAFF☀-➿]", t)),
        "gif_or_video": bool(
            re.search(r"\.(gif|mp4|webm)\b|youtube\.com|youtu\.be|asciinema|loom\.com", body, flags=re.IGNORECASE)
        ),
        "star_history": bool(re.search(r"star-history|stargazers over time", md, flags=re.IGNORECASE)),
        "contributors_grid": bool(
            re.search(r"contrib\.rocks|all-contributors|contributors-img", md, flags=re.IGNORECASE)
        ),
        "translation_links": bool(
            re.search(r"README[._-](zh|cn|es|fr|de|ja|ko|pt|ru|it|tr|hi)[^\s)\"']*\.md", md, flags=re.IGNORECASE)
        ),
        "install_cmd_in_first_2kb": bool(
            re.search(
                r"(?m)^\s*(npm i|npm install|pip install|brew install|curl -|cargo install|go install|docker run|uv |yarn add|pnpm add|apt|winget|npx )",
                md[:2500],
            )
        ),
        "h1_is_title": bool(hs and hs[0][0] == 1),
        "tagline_early": bool(re.search(r"^\s*(<p[^>]*>)?\s*[A-Z].{20,200}\.", md[:900], flags=re.MULTILINE)),
        "call_to_action_links": len(
            re.findall(
                r"\[(?:docs?|documentation|website|discord|slack|twitter|x\.com|community|blog)[^\]]*\]\(",
                md[:2500],
                flags=re.IGNORECASE,
            )
        ),
        # --- link-out behaviour (a section may be absent but linked) ---
        "links_contributing": bool(re.search(r"CONTRIBUTING(\.md|\.rst)?\b|/contributing", md, flags=re.IGNORECASE)),
        "links_license_file": bool(re.search(r"\bLICEN[SC]E(\.md|\.txt)?\b|/blob/[^)]*licen", md, flags=re.IGNORECASE)),
        "mentions_license_anywhere": bool(re.search(r"licen[sc]e", md, flags=re.IGNORECASE)),
        "links_coc": bool(re.search(r"CODE[_-]OF[_-]CONDUCT|code of conduct", md, flags=re.IGNORECASE)),
        "links_security": bool(
            re.search(r"SECURITY\.md|security polic|report.{0,20}vulnerab", md, flags=re.IGNORECASE)
        ),
        "links_docs_site": bool(re.search(r"https?://(docs?|www)\.[^)\s]+|\.dev/docs|/docs/", md, flags=re.IGNORECASE)),
        "links_chat": bool(
            re.search(
                r"discord\.(gg|com)|slack\.com|matrix\.to|t\.me|reddit\.com|/discussions", md, flags=re.IGNORECASE
            )
        ),
        "links_issues": bool(re.search(r"/issues", md, flags=re.IGNORECASE)),
        "install_cmd_anywhere": bool(
            re.search(
                r"(?m)^\s*\$?\s*(npm i |npm install|pip install|brew install|curl -[a-zA-Z]*S?[a-zA-Z]* http|cargo install|go install|docker run|docker compose|uv tool install|uvx |yarn add|pnpm add|apt-get install|winget install|npx |bun add|go get)",
                md,
            )
        ),
    }
    return feats


def run(names, label):
    rows = {}
    for repo in names:
        p = os.path.join("readmes", repo.replace("/", "_") + ".md")
        if not os.path.exists(p):
            print("MISSING", repo)
            continue
        rows[repo] = analyze(p)
    n = len(rows)
    sec = Counter()
    for r in rows.values():
        sec.update(r["sections"])
    boolfeats = [k for k, v in next(iter(rows.values())).items() if isinstance(v, bool)]
    bools = Counter()
    for r in rows.values():
        for k in boolfeats:
            if r.get(k):
                bools[k] += 1
    return {"label": label, "n": n, "sections": sec.most_common(), "bools": bools.most_common(), "rows": rows}


MAX_BODY = 1_048_576
MAX_CONSECUTIVE_FAILURES = 3


def fetch_corpus(outdir="readmes"):
    os.makedirs(outdir, exist_ok=True)
    consecutive_failures = 0
    for repo in PRIMARY + SECONDARY:
        try:
            ref = subprocess.run(
                ["git", "ls-remote", "--symref", f"https://github.com/{repo}.git", "HEAD"],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            ).stdout
            m = re.search(r"ref: refs/heads/(\S+)", ref)
            branch = m.group(1) if m else "main"
        except (OSError, subprocess.TimeoutExpired):
            branch = "main"
        for name in ("README.md", "readme.md", "README.markdown"):
            url = f"https://raw.githubusercontent.com/{repo}/{branch}/{name}"
            try:
                with urllib.request.urlopen(url, timeout=30) as response:
                    data = response.read(MAX_BODY)
            except (OSError, TimeoutError, urllib.error.URLError):
                data = b""
            if len(data) > 40:
                dest = os.path.join(outdir, repo.replace("/", "_") + ".md")
                with open(dest, "wb") as handle:
                    handle.write(data)
                print("OK  ", repo, branch, name, len(data))
                consecutive_failures = 0
                break
        else:
            print("FAIL", repo, branch)
            consecutive_failures += 1
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                print("Aborting fetch after 3 consecutive failures")
                return
            time.sleep(1)


if __name__ == "__main__":
    if "--fetch" in sys.argv:
        fetch_corpus()
        sys.exit(0)
    res = {}
    for names, label in ((PRIMARY, "primary20"), (SECONDARY, "secondary20")):
        r = run(names, label)
        res[label] = r
        print(f"\n===== {label} (n={r['n']}) =====")
        print("-- SECTIONS --")
        for name, c in r["sections"]:
            print(f"  {c:3d}/{r['n']}  {100 * c // r['n']:3d}%  {name}")
        print("-- FORMAT FEATURES --")
        for name, c in r["bools"]:
            print(f"  {c:3d}/{r['n']}  {100 * c // r['n']:3d}%  {name}")
        for metric in ("bytes", "lines", "n_headings", "badges", "tables", "code_blocks", "images", "details"):
            vals = sorted(x[metric] for x in r["rows"].values())
            print(
                f"  {metric:12s} median={st.median(vals):8.1f} mean={st.mean(vals):8.1f} min={vals[0]} max={vals[-1]}"
            )
    with open("analysis.json", "w", encoding="utf-8") as handle:
        json.dump(res, handle, indent=1)
