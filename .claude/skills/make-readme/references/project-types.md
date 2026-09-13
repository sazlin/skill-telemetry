# Project-type presets

The template's section list is a default. Adjust it with the preset that matches the project.
Each preset lists sections *in addition to* the always-on core, plus what to cut.
Core (always): title, tagline, badges, visual-or-first-example, install, quick start,
docs links, community, contributing link, license.

---

## CLI tool
**Add:** a terminal GIF or asciinema cast as the hero; a short command table if there are
more than 3 subcommands; a one-line uninstall note when install writes outside the package dir.
**Cut:** API reference, architecture.
**Emphasis:** install command must cover the 3 platforms your users are actually on
(Homebrew/curl, apt/dnf, winget/scoop). Put the extras in `<details>`.
**Corpus exemplars:** bat, lazygit, uv, ohmyzsh.

---

## Library / SDK
**Add:** the minimal code example *is* the hero visual, placed immediately after the tagline;
a supported-versions line (language runtime, framework peer deps).
**Cut:** screenshots, deployment, roadmap.
**Emphasis:** first code block must be importable and runnable as written. Show the return
value. Keep the API surface in the docs site, not here.
**Corpus exemplars:** transformers, langchain, next.js.

---

## Web app / self-hosted service
**Add:** a screenshot above the fold; a one-command Docker/compose quick start; a
"Deploy" section with a hosted option and a self-host path; environment variable table only if
under ~10 vars, otherwise link it.
**Cut:** library-style API examples.
**Emphasis:** state explicitly whether there is a hosted/cloud version and how it differs from
self-hosted. Readers ask this first.
**Corpus exemplars:** n8n, dify, supabase, excalidraw.

---

## Framework
**Add:** "Getting started" via the official scaffolding command (`npm create ...`);
links to the ecosystem (plugins, templates, starter kits); a short philosophy/why paragraph.
**Cut:** exhaustive feature lists; the docs site carries those.
**Emphasis:** the README is a signpost, not a manual. Framework READMEs in the corpus are
among the shortest (react 5 KB, next.js 3 KB, go 1.5 KB).
**Corpus exemplars:** react, vue, flutter, bootstrap.

---

## AI agent / model tool
**Add:** a supported-models/providers table (this is the one place a matrix table earns its
keep, 40% of AI-adjacent repos in the corpus ship one); an API-key/setup prerequisite line;
a cost or rate-limit warning if the tool spends money.
**Cut:** benchmarks unless reproducible with a command in the repo.
**Emphasis:** be explicit about what runs locally vs what calls a remote API, and what data
leaves the machine. Say it in the header block.
**Corpus exemplars:** ollama, opencode, claude-code, browser-use.

---

## Plugin / extension / theme
**Add:** the host requirement in the tagline itself ("A VS Code extension for ...");
install via the host's marketplace first, manual install second; a compatibility table if it
spans host versions.
**Cut:** contributing depth, architecture.
**Emphasis:** a screenshot of the plugin inside the host application, not in isolation.

---

## Monorepo / meta-repo
**Add:** a package table (name, version badge, description, link to its own README);
a "repo layout" tree of 5 to 10 lines.
**Cut:** per-package usage examples; each package has its own README.
**Emphasis:** the root README's job is routing. Keep it under 120 lines.

---

## Research / dataset / paper code
**Add:** citation block (BibTeX) and `CITATION.cff`; a results table with the headline metric;
a link to the paper, and exact reproduction commands including seeds and hardware.
**Cut:** community/Discord if none exists; roadmap.
**Emphasis:** state the license of the *data* separately from the code license.

---

## Internal / private repo
**Add:** an owner line (team, on-call, Slack channel); runbook and dashboard links;
"how to get access" (credentials, VPN, roles).
**Cut:** badges, logo, contributing, license, community.
**Emphasis:** the reader is a colleague who was paged at 3 a.m. Optimize for "how do I run it
locally" and "who do I ask", not for adoption.

---

## Template / boilerplate repo
**Add:** a "Use this template" button link at the top; a checklist of what to rename or replace
after cloning; a one-command teardown of the demo content.
**Cut:** most badges, since they refer to the template rather than the user's project.
**Emphasis:** distinguish instructions *for the template user* from content they will keep.
