# Evidence base: what real READMEs do (research, September 2026)

This file is the empirical backing for `SKILL.md` and `README_TEMPLATE.md`.
Every POPULAR / UNPOPULAR verdict below is derived from measured data, not opinion.

## Method

Three independent evidence streams were combined.

**Stream A: the top-starred OSS developer-tool corpus (n = 40).**
Ranking source: [EvanLi/Github-Ranking Top-100-stars](https://github.com/EvanLi/Github-Ranking/blob/master/Top100/Top-100-stars.md),
regenerated daily, snapshot of 2026-09-13. Inclusion rule: repositories whose primary
deliverable is software that developers install, run, or build with. Excluded: learning
resources, curated lists, prompt/skill collections, style guides, consumer media utilities,
OS kernels. The 20 highest-ranked qualifying repositories form the primary set; the next
20 form a validation set. Frequencies below are the combined 40 unless noted. Every README
was fetched from its default branch and parsed programmatically (headings normalized into
29 canonical sections, plus 35 formatting/link features).

Primary 20: react, vue, opencode, n8n, tensorflow, vscode, ohmyzsh, AutoGPT, markitdown,
ollama, firecrawl, flutter, bootstrap, transformers, dify, langflow, langchain, claude-code,
next.js, go.
Validation 20: kubernetes, node, rust, electron, llama.cpp, shadcn-ui, spec-kit, codex,
browser-use, three.js, excalidraw, godot, PowerToys, openclaw, supabase, grafana, playwright,
bat, lazygit, uv.

**Stream B: curated "great README" praise (n = 114).**
Every entry in [matiassingers/awesome-readme](https://github.com/matiassingers/awesome-readme)
carries a one-line rationale for why that README is admired. Those rationales were keyword-coded
to measure what reviewers actually praise, which is a different signal from what big repos ship.

**Stream C: guide consensus (n = 6 + 1 study).**
[makeareadme.com](https://www.makeareadme.com/), [GitHub's official About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes),
[standard-readme spec](https://github.com/RichardLitt/standard-readme),
[Best-README-Template](https://github.com/othneildrew/Best-README-Template),
[pushpen.dev 2026 guide](https://pushpen.dev/blog/github-readme-best-practices-2026),
[RepoClip 2026 guide](https://repoclip.io/blog/how-to-write-a-github-readme), plus the empirical study
[Categorizing the Content of GitHub README Files](https://arxiv.org/abs/1802.06997) (Prana et al.,
n = 4,226 sections): What 97.0%, How 88.5%, References 60.8%, Who 52.9%, Contribution 27.8%,
Why 25.7%, When 21.4%.

**Verdict rule (applied mechanically).**
POPULAR = present in >= 40% of Stream A **and** (required/recommended by >= 3 of Stream C **or** >= 30% of Stream B),
OR present in >= 70% of any single stream.
Everything else is UNPOPULAR. "UNPOPULAR" means *not a default*, not *never*: several
unpopular elements are correct in a narrow context, stated in the "use when" column.

## Corpus shape (calibration numbers)

| Metric | p25 | median | p75 | max |
| --- | --- | --- | --- | --- |
| Lines | 81 | **128** | 331 | 942 |
| Words | 448 | **616** | 1,594 | 5,128 |
| H2+ headings | - | **10** | - | 71 |
| Badges | - | **3** | - | 30 |
| Code blocks | - | **2** | - | 58 |
| Tables | - | **0** | - | 5 |
| Non-badge images | - | **2** | - | 655 |

Takeaway: the median top-tier README is ~130 lines and ~600 words, with about 10 sections,
3 badges, 2 code blocks, 2 images, and zero tables. Long READMEs exist but are the exception,
and they are almost always projects with no separate docs site.

## Group 1: Header block (everything above the first H2)

| Element | Stream A | Stream B | Stream C | Verdict |
| --- | --- | --- | --- | --- |
| Project name as the first thing (H1 or centered HTML title) | ~100% | - | required by 6/6 | **POPULAR** |
| Hero visual (logo, banner, screenshot) in first ~1.5 KB | 87% | 58% logo, 28% screenshot | 4/6 | **POPULAR** |
| One-sentence description under the name | 62% detected | 43% | required by 6/6 | **POPULAR** |
| Badge row, directly under the title | 77% have badges, 70% of those at top | 51% | 5/6 | **POPULAR** |
| Centered HTML header block (`<div align="center">`) | 70% | - | 0/6 explicit | **POPULAR** (corpus rule) |
| Bullet list within first 3 KB (features/why) | 55% | 33% | 4/6 | **POPULAR** |
| Animated demo (GIF / video / asciinema) | 17% | 45% | 5/6 | **POPULAR** (see note) |
| Row of 3+ nav links under the title (Docs / Discord / Blog) | 15% | 40% cite navigation | 1/6 | UNPOPULAR |
| Blockquote tagline (`> ...`) | 5% | - | banned by standard-readme | UNPOPULAR |
| Table of contents | 12% | 40% | required >100 lines by 1/6 | UNPOPULAR (see note) |
| Translation links (README.zh.md, ...) | 12% | - | 1/6 | UNPOPULAR, use when the project has real i18n demand |
| Emoji in heading text | 10% | 4% | 0/6 | UNPOPULAR |

Notes.
- **Demo GIF** is the clearest split between the two streams: only 17% of giant repos ship one
  (they have marketing sites instead), but 45% of *praised* READMEs do, and 5/6 guides demand
  visual proof. For a project without a docs site, this is the single highest-leverage element.
  Verdict POPULAR on the >=70%-of-one-stream clause via Stream B's visual cluster (GIF 45% +
  screenshots 28% + logo 58%, 84% of entries praise at least one visual).
- **TOC**: GitHub auto-generates an outline for every markdown file from the heading menu, which
  is why 88% of the top corpus omits one. Add a TOC only above ~150 lines.

## Group 2: Core body sections

| Section | Stream A (heading) | Stream A (linked/implied) | Stream B | Stream C | Verdict |
| --- | --- | --- | --- | --- | --- |
| Installation | 52% | install command present 52% | 30% | 6/6 | **POPULAR** |
| Quick start / getting started | 52% | - | 7% | 6/6 | **POPULAR** |
| Usage / examples with runnable code | 37% usage + 10% examples | fenced code block 77%, language-tagged 75% | 37% | 6/6 | **POPULAR** |
| Documentation links | 70% | links to a docs site 90% | 19% | 5/6 | **POPULAR** |
| Features / why | 30% | bullets near top 55% | 33% | 4/6 | **POPULAR** |
| Community / support | 55% | chat link 42%, issues link 45% | - | 5/6 | **POPULAR** |
| License | 47% | mentioned 82%, LICENSE linked 80% | 6% | 6/6 | **POPULAR** |
| Contributing | 22% | CONTRIBUTING linked 85% | 20% | 6/6 | **POPULAR as a link, UNPOPULAR as an inline section** |
| Integrations / ecosystem / supported models | 40% | - | - | 0/6 | UNPOPULAR by default, POPULAR for tools whose value *is* the matrix (n8n, ollama, langchain all ship it) |
| Deployment / self-hosting | 20% | - | - | 0/6 | UNPOPULAR, use when self-hosting is a primary path |
| Changelog / releases | 22% | - | - | 1/6 | UNPOPULAR, link to /releases instead |
| Contributors list or avatar grid | 22% heading, 12% grid image | - | 9% | 2/6 | UNPOPULAR |
| Security | 17% | SECURITY.md referenced 10% | - | 1/6 | UNPOPULAR inline, use SECURITY.md |
| Requirements / prerequisites (own section) | 15% | version stated anywhere 10% | - | 3/6 | UNPOPULAR as its own section, POPULAR as one line inside Installation |
| API reference | 15% | - | - | 2/6 | UNPOPULAR inline, link to docs |
| Sponsors / backers | 12% | - | 1/6 | UNPOPULAR, use when funding is live |
| Comparison / alternatives | 12% | - | 5% | 0/6 | UNPOPULAR, use when entering a crowded category |
| Configuration reference | 10% | - | - | 2/6 | UNPOPULAR inline, link to docs |
| Testing | 10% | - | - | 2/6 | UNPOPULAR, belongs in CONTRIBUTING.md |
| FAQ / troubleshooting | 10% | - | 4% | 1/6 | UNPOPULAR |
| Code of conduct | 7% | referenced 27% | - | 2/6 | UNPOPULAR inline, use CODE_OF_CONDUCT.md |
| Roadmap | 5% | - | 2% | 3/6 | UNPOPULAR, use when pre-1.0 and actively shaping scope |
| Architecture / how it works | 5% | 8% cite diagrams | - | 0/6 | UNPOPULAR, use for infra/protocol projects |
| Citation | 5% | - | 1/6 (GitHub CITATION.cff) | UNPOPULAR, use for research artifacts |
| Star history chart | 7% | - | 0/6 | UNPOPULAR |
| Acknowledgments / credits | 2% | - | 4/6 | UNPOPULAR despite guide enthusiasm; the corpus rejects it |

The strongest single finding: **big projects link out instead of inlining.**
85% link CONTRIBUTING, 80% link LICENSE, 90% link a docs site, yet only 22% write a
Contributing section and only 47% write a License section. README length is spent on
"what is this, why care, how do I run it in 60 seconds"; everything else is a hyperlink.
That is the same shape the Prana study found (What 97%, How 88.5%, References 60.8%,
Contribution 27.8%).

## Group 3: Formatting devices

| Device | Stream A | Stream B | Verdict |
| --- | --- | --- | --- |
| Fenced code block | 77% | 37% | **POPULAR** |
| Language tag on the fence (```bash) | 75% | - | **POPULAR** |
| Relative links to in-repo files | 72% | - | **POPULAR** (GitHub rewrites them per-branch; absolute links rot) |
| Exactly one H1 | 67% | - | **POPULAR** |
| Markdown table | 32% (median 0 per README) | 8% | UNPOPULAR as decoration, **POPULAR for reference data only** (options, platform support, comparisons) |
| `<details>` collapsible | 20% | 7% | UNPOPULAR, use for long optional blocks (per-OS install, full config) |
| "Back to top" links | 2% | - | UNPOPULAR |
| Contributor avatar grid (contrib.rocks) | 12% | - | UNPOPULAR |
| Star-history image | 7% | - | UNPOPULAR |

## Group 4: Badges, in detail

77% of the corpus ships badges; the median count is 3 and the p75 is 6. One repo ships 30,
which is the failure mode every guide names ("badge wall"). Both 2026 guides converge on the
same rule: **3 to 6 badges, each answering a question an evaluator actually asks**
(is it maintained, what version, does CI pass, what license, how big is the community).
Decorative badges (tech-stack logos, "made with love") appear in the corpus only on
lower-traffic projects and are praised by no guide.

## What this implies for a template

1. Default to ~120 to 200 lines. Longer only when there is no docs site.
2. Ten sections is the norm. A template with 20 mandatory sections contradicts every stream.
3. Above the fold: name, one-liner, badges, visual, and a runnable command. Nothing else.
4. Installation and a working example are the only two sections that are near-universal in
   substance; they must be copy-pasteable and verified.
5. Prefer a link over a section for: contributing, code of conduct, security, changelog,
   full API, full configuration, testing.
6. Tables earn their place only when the content is genuinely tabular.
