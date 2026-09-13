#!/usr/bin/env python3
"""
inspect_repo.py: gather the facts a README needs, from the repo itself.

Usage:
    python3 inspect_repo.py [REPO_PATH] [--json]

Prints a fact sheet: identity, install commands, entry points, license, CI,
docs, assets, community links, and what the existing README is missing.
Read-only. Standard library only. Never guesses: unknown fields are reported
as null so the agent knows to ask instead of invent.
"""

import json
import os
import re
import subprocess
import sys
from urllib.parse import urlparse

SKIP_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "target",
    "vendor",
    ".venv",
    "venv",
    "__pycache__",
    ".next",
    ".cache",
    "site-packages",
    ".tox",
    "coverage",
    "htmlcov",
    ".gradle",
    "Pods",
    "data",
    "datasets",
}


def _run(cmd, cwd):
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=15, check=False).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _read_text(path, limit=200000):
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            return handle.read(limit)
    except OSError:
        return ""


def walk(root, max_files=6000):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS and name != ".git"]
        for filename in filenames:
            out.append(os.path.relpath(os.path.join(dirpath, filename), root))
            if len(out) >= max_files:
                return out
    return out


def toml_get(text, key):
    match = re.search(rf'(?m)^\s*{re.escape(key)}\s*=\s*["\']([^"\']+)["\']', text)
    return match.group(1) if match else None


_HTTP_URL = re.compile(r'https?://[^\s)\'"]+')
_SECRET_HINT = re.compile(r"token|key|secret|code|access_token", re.IGNORECASE)


def _redact_userinfo(url):
    parsed = urlparse(url)
    if "@" not in parsed.netloc:
        return url
    host = parsed.hostname or ""
    if parsed.port:
        host = f"{host}:{parsed.port}"
    return parsed._replace(netloc=host).geturl()


def _keep_community(url):
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    path = parsed.path or ""
    if "/api/webhooks" in path or "/api/" in path:
        return False
    if _SECRET_HINT.search(f"{parsed.username or ''} {parsed.password or ''} {parsed.query}"):
        return False
    if host in {"discord.gg", "join.slack.com", "matrix.to", "t.me"}:
        return True
    if host == "discord.com" and path.startswith(("/invite/", "/servers/")):
        return True
    return host == "reddit.com" or host.endswith(".reddit.com")


def _is_docs_url(url):
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    path = parsed.path or ""
    if host.startswith("docs.") or host == "readthedocs.io" or host.endswith(".readthedocs.io"):
        return True
    return "/docs/" in (path.rstrip("/") + "/")


def _git_identity(root, facts):
    remote = _run(["git", "remote", "get-url", "origin"], root)
    match = re.search(r"github\.com[:/]([^/]+)/([^/\s]+)", remote)
    facts["owner"] = match.group(1) if match else None
    if match:
        facts["repo"] = match.group(2).removesuffix(".git")
    else:
        facts["repo"] = os.path.basename(os.path.abspath(root))
    origin_head = _run(["git", "rev-parse", "--abbrev-ref", "origin/HEAD"], root)
    if origin_head.startswith("origin/"):
        origin_head = origin_head.removeprefix("origin/")
    # Failed rev-parse still prints origin/HEAD; that is not a branch name.
    if origin_head == "HEAD":
        origin_head = ""
    current_branch = _run(["git", "symbolic-ref", "--short", "HEAD"], root)
    facts["default_branch"] = origin_head or current_branch or None
    facts["last_commit"] = _run(["git", "log", "-1", "--format=%ci"], root) or None
    facts["commit_count"] = _run(["git", "rev-list", "--count", "HEAD"], root) or None
    facts["contributors"] = len([line for line in _run(["git", "shortlog", "-sn", "HEAD"], root).splitlines() if line])


def _manifest_facts(root, files, facts):
    lower = {path.lower(): path for path in files}
    top = [path for path in files if os.sep not in path]
    manifests = {}
    name = desc = version = None
    ecosystems, install, run_cmds, test_cmds = [], [], [], []

    if "package.json" in lower:
        try:
            pkg = json.loads(_read_text(os.path.join(root, lower["package.json"])))
        except json.JSONDecodeError:
            pkg = None
        if pkg is not None:
            manifests["package.json"] = {
                key: pkg.get(key)
                for key in ("name", "version", "description", "license", "bin", "private", "workspaces")
            }
            name = name or pkg.get("name")
            desc = desc or pkg.get("description")
            version = version or pkg.get("version")
            pkg_name = pkg.get("name")
            if not pkg.get("private"):
                ecosystems.append("npm")
                if isinstance(pkg_name, str) and pkg_name:
                    if pkg.get("bin"):
                        install.append(f"npm install -g {pkg_name}")
                    else:
                        install.append(f"npm install {pkg_name}")
            scripts = pkg.get("scripts") or {}
            for script in ("dev", "start", "build"):
                if script in scripts:
                    run_cmds.append(f"npm run {script}")
            for script in ("test", "test:unit"):
                if script in scripts:
                    test_cmds.append(f"npm run {script}")
            facts["node_engines"] = (pkg.get("engines") or {}).get("node")

    if "pyproject.toml" in lower:
        text = _read_text(os.path.join(root, lower["pyproject.toml"]))
        manifests["pyproject.toml"] = {
            "name": toml_get(text, "name"),
            "version": toml_get(text, "version"),
            "description": toml_get(text, "description"),
            "requires-python": toml_get(text, "requires-python"),
        }
        name = name or manifests["pyproject.toml"]["name"]
        desc = desc or manifests["pyproject.toml"]["description"]
        version = version or manifests["pyproject.toml"]["version"]
        ecosystems.append("pypi")
        if manifests["pyproject.toml"]["name"]:
            install.append(f"pip install {manifests['pyproject.toml']['name']}")
        if re.search(r"\[project\.scripts\]", text):
            facts["console_scripts"] = re.findall(
                r'(?m)^\s*([\w.-]+)\s*=\s*["\']', text.split("[project.scripts]", 1)[1][:500]
            )

    if "cargo.toml" in lower:
        text = _read_text(os.path.join(root, lower["cargo.toml"]))
        cargo_name = toml_get(text, "name")
        name = name or cargo_name
        desc = desc or toml_get(text, "description")
        version = version or toml_get(text, "version")
        ecosystems.append("crates.io")
        if isinstance(cargo_name, str) and cargo_name:
            install.append(f"cargo install {cargo_name}")
    if "go.mod" in lower:
        text = _read_text(os.path.join(root, lower["go.mod"]))
        module_match = re.search(r"(?m)^module\s+(\S+)", text)
        if module_match:
            manifests["go.mod"] = module_match.group(1)
            name = name or module_match.group(1).split("/")[-1]
            ecosystems.append("go")
            install.append(f"go install {module_match.group(1)}@latest")
        go_version_match = re.search(r"(?m)^go\s+([\d.]+)", text)
        facts["go_version"] = go_version_match.group(1) if go_version_match else None
    if "gemfile" in lower or any(path.endswith(".gemspec") for path in top):
        ecosystems.append("rubygems")
    if "composer.json" in lower:
        ecosystems.append("packagist")
    if any(path.lower() in ("pom.xml", "build.gradle", "build.gradle.kts") for path in top):
        ecosystems.append("maven/gradle")

    dockerfiles = [path for path in files if os.path.basename(path).lower().startswith("dockerfile")]
    composes = [path for path in files if re.match(r"(docker-)?compose\.ya?ml$", os.path.basename(path).lower())]
    if dockerfiles or composes:
        ecosystems.append("docker")
        if composes:
            run_cmds.append("docker compose up")
    if "makefile" in lower:
        makefile_text = _read_text(os.path.join(root, lower["makefile"]))
        facts["make_targets"] = re.findall(r"(?m)^([a-zA-Z][\w-]*):(?!=)", makefile_text)[:15]

    facts["manifests"] = manifests
    facts["name"] = name
    facts["description_from_manifest"] = desc
    facts["version"] = version
    facts["ecosystems"] = ecosystems
    facts["suggested_install_commands"] = install
    facts["suggested_run_commands"] = run_cmds
    facts["test_commands"] = test_cmds


def _language_mix(files, facts):
    counts = {}
    for path in files:
        suffix = os.path.splitext(path)[1].lower()
        if suffix in (
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
            ".go",
            ".rs",
            ".java",
            ".rb",
            ".php",
            ".c",
            ".cpp",
            ".cs",
            ".swift",
            ".kt",
            ".sh",
            ".lua",
            ".ex",
            ".scala",
        ):
            counts[suffix] = counts.get(suffix, 0) + 1
    facts["language_mix"] = sorted(counts.items(), key=lambda item: -item[1])[:5]
    facts["file_count"] = len(files)


def _health_files(root, files, facts):
    def find(*names):
        for name in names:
            for path in files:
                if os.path.basename(path).lower() == name and path.count(os.sep) <= 1:
                    return path
        return None

    health = {
        "readme": find("readme.md", "readme.rst", "readme.txt", "readme"),
        "license": find("license", "license.md", "license.txt", "licence", "copying"),
        "contributing": find("contributing.md", "contributing.rst"),
        "code_of_conduct": find("code_of_conduct.md"),
        "security": find("security.md"),
        "changelog": find("changelog.md", "changes.md", "history.md"),
        "citation": find("citation.cff"),
        "issue_templates": [path for path in files if "issue_template" in path.lower()][:5],
    }
    facts["health_files"] = health
    license_text = _read_text(os.path.join(root, health["license"]), 4000) if health["license"] else ""
    facts["license_guess"] = None
    for pattern, license_name in (
        (r"MIT License", "MIT"),
        (r"Apache License.*2\.0", "Apache-2.0"),
        (r"GNU AFFERO", "AGPL-3.0"),
        (r"GNU GENERAL PUBLIC LICENSE.*Version 3", "GPL-3.0"),
        (r"GNU LESSER", "LGPL"),
        (r"BSD 3-Clause", "BSD-3-Clause"),
        (r"BSD 2-Clause", "BSD-2-Clause"),
        (r"Mozilla Public License", "MPL-2.0"),
        (r"Business Source License", "BUSL-1.1"),
        (r"The Unlicense", "Unlicense"),
    ):
        if re.search(pattern, license_text, flags=re.IGNORECASE | re.DOTALL):
            facts["license_guess"] = license_name
            break


def _ci(files, facts):
    workflows = [path for path in files if path.startswith(os.path.join(".github", "workflows"))]
    facts["ci_workflows"] = workflows[:10]
    facts["ci_primary"] = next(
        (
            os.path.basename(workflow)
            for workflow in workflows
            if re.search(r"ci|test|build|main", os.path.basename(workflow), re.IGNORECASE)
        ),
        os.path.basename(workflows[0]) if workflows else None,
    )


def _docs_and_media(files, facts):
    facts["docs_dirs"] = sorted(
        {
            path.split(os.sep)[0]
            for path in files
            if path.split(os.sep)[0] in ("docs", "doc", "website", "documentation")
        }
    )
    facts["examples_dirs"] = sorted(
        {path.split(os.sep)[0] for path in files if path.split(os.sep)[0] in ("examples", "example", "samples", "demo")}
    )
    facts["images"] = [
        path
        for path in files
        if os.path.splitext(path)[1].lower() in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")
        and not path.startswith("node_modules")
    ][:20]
    facts["demo_media"] = [path for path in files if path.lower().endswith((".gif", ".webp", ".mp4", ".webm", ".cast"))]


def _readme_stats(root, facts):
    health = facts["health_files"]
    readme_text = _read_text(os.path.join(root, health["readme"])) if health["readme"] else ""
    urls = _HTTP_URL.findall(readme_text)
    facts["readme"] = {
        "exists": bool(readme_text),
        "bytes": len(readme_text),
        "lines": readme_text.count("\n") + 1 if readme_text else 0,
        "h1_count": len(re.findall(r"(?m)^# ", readme_text)),
        "headings": re.findall(r"(?m)^#{2,3}\s+(.+)$", readme_text)[:40],
        "badges": len(re.findall(r"img\.shields\.io|badge\.svg", readme_text)),
        "code_blocks": readme_text.count("```") // 2,
        "images": len(re.findall(r"!\[[^\]]*\]\(|<img ", readme_text)),
        "links_docs_site": any(_is_docs_url(url) for url in urls),
    }
    return urls


def _community_links(urls, facts):
    facts["community_links"] = sorted({_redact_userinfo(url) for url in urls if _keep_community(url)})[:5]
    facts["docs_links"] = sorted({url for url in urls if _is_docs_url(url)})[:5]


def _gaps(facts):
    health = facts["health_files"]
    gaps = []
    if not health["readme"]:
        gaps.append("No README at all.")
    if not health["license"]:
        gaps.append("No LICENSE file: add one before claiming a license in the README.")
    if not health["contributing"]:
        gaps.append("No CONTRIBUTING.md: either create it or do not link it.")
    if not facts["images"] and not facts["demo_media"]:
        gaps.append(
            "No images in repo: a demo GIF, screenshot, video, or asciinema cast must be created or the visual section cut."
        )
    if not facts["ci_workflows"]:
        gaps.append("No CI workflows: do not add a CI badge.")
    if not facts["ecosystems"]:
        gaps.append("No package manifest found: install instructions must be clone-and-run.")
    if not facts["docs_dirs"] and not facts["docs_links"]:
        gaps.append("No docs site or docs/ dir: Documentation section should link in-repo files or be cut.")
    facts["gaps"] = gaps


def inspect(root: str) -> dict:
    files = walk(root)
    facts = {"path": os.path.abspath(root)}
    _git_identity(root, facts)
    _manifest_facts(root, files, facts)
    _language_mix(files, facts)
    _health_files(root, files, facts)
    _ci(files, facts)
    _docs_and_media(files, facts)
    urls = _readme_stats(root, facts)
    _community_links(urls, facts)
    _gaps(facts)
    return facts


def human(facts: dict) -> str:
    lines: list[str] = []
    lines.append(
        f"REPO        {facts['owner'] or '?'}/{facts['repo']}   branch={facts['default_branch']}  commits={facts['commit_count']}  contributors={facts['contributors']}"
    )
    lines.append(f"NAME        {facts['name']}")
    lines.append(f"DESCRIPTION {facts['description_from_manifest']}")
    lines.append(f"VERSION     {facts['version']}    ECOSYSTEMS: {', '.join(facts['ecosystems']) or 'none'}")
    lines.append(f"LANGUAGES   {facts['language_mix']}   files={facts['file_count']}")
    lines.append(f"LICENSE     file={facts['health_files']['license']}  detected={facts['license_guess']}")
    lines.append(f"CI          {facts['ci_primary']}  ({len(facts['ci_workflows'])} workflows)")
    lines.append(f"DOCS        dirs={facts['docs_dirs']}  links={facts['docs_links']}")
    lines.append(f"EXAMPLES    {facts['examples_dirs']}")
    lines.append(f"MEDIA       demo={facts['demo_media'][:3]}  images={len(facts['images'])}")
    lines.append(f"COMMUNITY   {facts['community_links']}")
    lines.append(
        "HEALTH      "
        + ", ".join(
            f"{key}={'Y' if value else 'N'}" for key, value in facts["health_files"].items() if key != "issue_templates"
        )
    )
    lines.append(f"INSTALL?    {facts['suggested_install_commands']}")
    lines.append(f"RUN?        {facts['suggested_run_commands']}   TEST? {facts['test_commands']}")
    if facts["readme"]["exists"]:
        readme = facts["readme"]
        lines.append(
            f"README      {readme['lines']} lines, {readme['badges']} badges, {readme['code_blocks']} code blocks, {readme['images']} images, h1={readme['h1_count']}"
        )
        lines.append(f"  sections: {readme['headings']}")
    else:
        lines.append("README      none")
    if facts["gaps"]:
        lines.append("GAPS (resolve before writing; ask the user rather than inventing):")
        for gap in facts["gaps"]:
            lines.append(f"  - {gap}")
    return "\n".join(lines)


if __name__ == "__main__":
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    root = args[0] if args else "."
    facts = inspect(root)
    if "--json" in sys.argv:
        print(json.dumps(facts, indent=2))
    else:
        print(human(facts))
