# Spec: `skill-telemetry` plugin for OMP (Oh My Pi)

**Status:** ready to implement
**If blocked:** every unanswered item in section 10 has a stated fallback. Take the fallback, document it, and keep moving. Do not fork OMP, do not invent an event that is not in `hooks/types.ts`, and do not guess at a field name when a `TODO` in section 11 marks it unverified.
**Audience:** implementing sub-agent
**Target host:** `can1357/oh-my-pi` (omp), extensions loaded in-process in the Bun runtime

---

## 1. Objective

Emit OpenTelemetry **metrics** to an OTLP collector so the operator can answer:

- Which OMP skills get read into context?
- How often, when, and as a fraction of the turns where they could have been?
- By which path (model-invoked, user-invoked, autoloaded)?
- In which repo, session, and model context?

**Definition of "turn":** one user-prompt-to-assistant-settle cycle within a session. A session contains many turns. One `omp -p` run is a session containing one turn. This term is load-bearing for `omp.skill.turns`; see open question 9 for how to confirm the event boundary.

The plugin must work as a standard OMP extension loaded from user config. **Do not fork or patch OMP source.** If an objective cannot be met without a source change, record it in section 10 rather than editing the host.

## 1b. Verified baseline (measured, not assumed)

Everything in this section was confirmed on a live install against an OTLP collector. Treat it as ground truth and do not re-derive it.

**OMP ships zero skills out of the box.** A stock install with no other agent tooling on the machine reports `available skills: none`. Every skill provider is a discovery path over directories populated by the user or by another tool. Any test that names a skill must create it first.

**The fixture skill works at this exact path:**

```
~/.omp/agent/skills/telemetry-probe/SKILL.md
```

Not `~/.omp/skills/`. The `description` frontmatter field is mandatory for the native provider (`requireDescription: true`); without it the skill is silently undiscovered. Body used: `Reply with exactly: PROBE-OK`, which gives an unambiguous success signal.

**The host counter that already exists:**

```
pi_omp_agent_tool_calls_total{gen_ai_tool_name="read",job="oh-my-pi",
  otel_scope_name="@oh-my-pi/pi-coding-agent",
  pi_omp_agent_models_used_count="1",pi_omp_agent_providers_used_count="1",
  pi_omp_agent_tools_available_count="12",pi_omp_agent_tools_invoked_count="1",
  pi_omp_agent_tools_unused_count="11",pi_omp_tool_status="ok"} 2
```

Two skill reads in one interactive session produced the value 2. **No label carries the skill name.** This is the gap the plugin closes, and it is now demonstrated rather than inferred.

**Facts extracted from that series:**

- Instrumentation scope is `@oh-my-pi/pi-coding-agent`. The plugin must use a **different** scope name so its instruments stay separable from the host's.
- The tool-name label is the semconv key `gen_ai_tool_name`, not a custom key. Reuse it.
- The host prefixes its own non-semconv labels with `pi.omp.` (`pi_omp_tool_status`). The plugin should stay in the distinct `omp.skill.*` namespace so plugin-emitted series are trivially separable from host-emitted ones.
- Default `job` is `oh-my-pi`, so `OTEL_SERVICE_NAME` defaults to `oh-my-pi`, not `omp`.

**Counters accumulate per process, not across runs.** Each `omp -p` is a separate process with a fresh MeterProvider starting at zero. It exports 1, exits, and the next run exports 1 again; the Prometheus exporter reflects latest-value-per-series rather than summing across producers, so repeated headless runs sit at 1 forever. Two consequences:

1. Any test asserting increments must do the repeated invocations **inside a single session**.
2. The resource carries no instance-distinguishing attribute, so every run writes to the same series and clobbers the previous one. The plugin **must** set `service.instance.id` on its resource (or verify the host sets one) or cross-run aggregation is impossible. Real aggregation requires a backend that sums across instances; a bare collector plus Prometheus exporter cannot do it.

**Label-design anti-pattern to avoid.** `pi_omp_agent_tools_available_count` and its siblings are run-summary aggregates attached as labels to a per-call counter. Changing toolset forks a new time series: the run above produced two series differing only by `tools_available_count` 11 versus 12, one from a headless run and one from an interactive session. Summing then requires knowing which labels to ignore. The plugin's instruments must carry only stable, low-cardinality labels.

**Operational notes for whoever runs the verification:**

- Use the shared `OTEL_EXPORTER_OTLP_ENDPOINT` with a base URL. The SDK appends `/v1/metrics`. Signal-specific variables such as `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` require the **full path** including `/v1/metrics`, and getting this wrong produces silent 404s with no error surfaced.
- Set `OTEL_TRACES_EXPORTER=none` and `OTEL_LOGS_EXPORTER=none` to cut noise.
- Allow ~25s after a run for the periodic reader to flush before scraping.
- Collector-side filter processors fail closed. A misdrawn regex drops everything and looks identical to nothing being exported. Verify with an empty processor list before debugging the plugin.

## 1c. Build order (follow this sequence)

The spec is written as a set of requirements, not a plan. Implement in this order. **Stop at each gate** rather than working around it.

| Phase | Do | Gate before continuing |
| --- | --- | --- |
| 0 | Read the source files in section 3. Answer open questions 1, 2, 5, 9 by reading `hooks/types.ts`. Write the answers into the README. | You can name the real field for the read path and confirm `turn_end` exists |
| 1 | Scaffold the package (section 4), install it, register a `session_start` handler that logs once. | `omp` starts, your log line appears, nothing is broken |
| 2 | Implement `omp.skill.skill_reads` for the model path only. Ignore the other two paths. | Fixture skill read produces one increment with the correct name |
| 3 | Implement `omp.skill.turns` and `omp.skill.discovered_on_session_start`. | The ratio query in section 5 returns a sensible number |
| 4 | Implement the `/skill:` user path (open questions 1 and 6). | `invocation_kind="user"` appears, no double-count |
| 5 | Autoload path, or a documented decision not to cover it. | README states the outcome either way |
| 6 | Unit tests, README, manual transcript. | Every box in section 8 is ticked |

Phases 4 and 5 are allowed to fail. If the event surface does not exist, document it and ship phases 1 to 3. A working plugin covering the model path is worth more than a stalled one attempting all three.

## 2. Non-goals

- Tracing / spans. Metrics only. (If tracing is wanted later it is a separate plugin; see section 9 for prior art.)
- Instrumenting tools other than skill reads. (`omp.skill.turns` is in scope as the denominator, not as general tool instrumentation.)
- Measuring whether the model actually *followed* a skill. This plugin measures load events, not compliance.
- Shipping a collector. The operator supplies an OTLP endpoint.

## 3. Required background (verify in source before coding)

OMP has **no dedicated `skill` tool**. Skills reach the model through three distinct paths, and each needs separate instrumentation:

| Path | Mechanism | Observable via |
| --- | --- | --- |
| **Model-invoked** | `read` tool against a `skill://<name>` internal URL | `tool_call` / `tool_execution_end` extension events |
| **User-invoked** | `/skill:<name> [args]` slash command, registered when `skills.enableSkillCommands` is true. Reads the file from `filePath`, strips frontmatter, injects the body as a custom message, appends `Skill: <path>` metadata | `input` event (extension-only); dispatch goes through `#invokeSkillCommand` in `input-controller.ts` |
| **Autoloaded** | Subagents auto-inject skills declared in the `autoloadSkills` agent frontmatter; rendered with `autoload.md`, provenance-only | No tool call. Best available proxy is the session's skill list at `session_start` |

Source files the implementer should read first:

- `packages/coding-agent/src/extensibility/skills.ts` (`loadSkills`, `buildSkillPromptMessage`)
- `packages/coding-agent/src/internal-urls/skill-protocol.ts` (`skill://` resolution rules)
- `packages/coding-agent/src/extensibility/hooks/types.ts` (**authoritative** event payload shapes)
- `docs/extensions.md`, `docs/skills.md`, `docs/skills/authoring-hooks.md`

`skill://` resolution semantics that affect attribute extraction:

- `skill://<name>` resolves to `<baseDir>/SKILL.md`
- `skill://<name>/<relative-path>` resolves to an asset inside the skill directory
- Absolute paths and `..` traversal are rejected by the host

## 4. Package layout

```
skill-telemetry/
  package.json          # { "omp": { "extensions": ["./src/main.ts"] } }
  src/
    main.ts             # ExtensionAPI factory, default export
    otel.ts             # MeterProvider construction + shutdown
    skills.ts           # skill:// parsing, /skill: parsing, name normalization
    config.ts           # env + config resolution with defaults
  README.md
  test/
    skills.test.ts
```

Use `ExtensionAPI` (`@oh-my-pi/pi-coding-agent`), not the legacy `HookAPI`. The extension-only events this plugin needs (`input`, `tool_execution_end`) are unavailable on `HookAPI`.

### Concrete scaffolding

`package.json`:

```json
{
  "name": "skill-telemetry",
  "version": "0.1.0",
  "type": "module",
  "files": ["src"],
  "omp": { "extensions": ["./src/main.ts"] },
  "dependencies": { "@opentelemetry/api": "^1.9.0" },
  "devDependencies": {
    "@oh-my-pi/pi-coding-agent": "*",
    "@opentelemetry/sdk-metrics": "^1.30.0"
  }
}
```

**Dependency rule.** Under Design A the runtime dependency is `@opentelemetry/api` **only**. `@opentelemetry/sdk-metrics` is a dev dependency used by unit tests, and becomes a runtime dependency only under Design B. Shipping the SDK when you do not own a provider is how you end up accidentally registering a second one.

omp runs TypeScript directly, so no build step is needed. `omp.extensions` entries are relative to the package root; the older `pi.extensions` field still works but is not for new packages.

### Development loop

```bash
# register the package
echo "extensions:\n  - $PWD" >> ~/.omp/agent/config.yml   # verify YAML shape first
omp                                                       # restart to load
```

Changed skills, slash commands, and MCP servers pick up via `/reload-plugins`. **Tools, hooks, and extension modules require a new session**, so expect to restart `omp` on every code change to this plugin. If the extension fails to load, check `/extensions` for the error and confirm it was not disabled via `disabledExtensions` in config.

## 5. Metrics contract

Instrumentation scope: `omp.skill-telemetry`, version from `package.json`. This must differ from the host's scope, which is `@oh-my-pi/pi-coding-agent` (verified), so plugin series stay separable.

| Instrument | Type | Unit | Description |
| --- | --- | --- | --- |
| `omp.skill.skill_reads` | Counter (uint) | `{read}` | One increment per hydration of a skill body |
| `omp.skill.turns` | Counter (uint) | `{turn}` | One increment per turn in which skills were offered to the model |
| `omp.skill.discovered_on_session_start` | UpDownCounter | `{skill}` | Skills discovered when the session starts |

Asset reads and load errors are explicitly **out of scope**. Do not implement `omp.skill.asset_reads` or `omp.skill.load_errors`. A read of `skill://<name>/<path>` should be ignored entirely rather than counted under a separate instrument.

### Why `skill_reads` and not `invocations`

The name matches what is actually measured. Per section 3, the model does not "invoke" a skill through any dedicated mechanism; it emits a `read` against `skill://<name>` and the body comes back. The read **is** the hydration and **is** the decision. Naming the counter after the observable event keeps the metric honest about what it can and cannot tell you.

The `/skill:<name>` and autoload paths are not literally `read` calls, but they hydrate the same body, so they belong on the same counter and are distinguished by `omp.skill.invocation_kind`.

### `omp.skill.turns` semantics (read this before implementing)

This is the **denominator**. Every turn is an opportunity for the model to read a skill: the system prompt carries the name-and-description list, and the model either acts on it or does not. Counting turns gives you the base rate that `skill_reads` is measured against.

The useful quantity is a ratio computed at query time, not a metric:

```
rate(omp_skill_skill_reads_total{omp_skill_name="x"}) / rate(omp_skill_turns_total)
```

A skill read on 2 of 400 turns has a description that is not matching the work. That is the same signal the removed `considerations` counter was reaching for, obtained at N-times-lower volume: one increment per turn instead of one per skill per turn.

Rules for this instrument:

1. **`omp.skill.turns` carries no `omp.skill.name`.** It is not per skill. Attaching a skill name would make the denominator meaningless and multiply the series count by the skill count. This is the single most likely implementation error.
2. **Only count turns where skills were actually offered.** If `skills.enabled` is false, or discovery returned nothing, or the `read` tool is unavailable (in which case `system-prompt.ts` omits the skills list entirely), the model had no opportunity and the turn must not be counted. Otherwise the denominator is inflated by turns where a read was impossible.
3. **Emit once per turn at `turn_end`**, not per message or per tool call.
4. If turn boundaries are not cleanly observable, fall back to counting agent runs at `agent_end` and rename the instrument to match. Do not silently redefine "turn."

Carry `omp.skill.discovered_on_session_start` as a sibling so the denominator can be interpreted: 3 reads across 400 turns means something different with 2 skills installed than with 40.

**Attributes** on `omp.skill.skill_reads`:

| Key | Values | Notes |
| --- | --- | --- |
| `omp.skill.name` | string | **Required.** Normalized; lowercase; exact match against discovered name. This is the primary pivot |
| `omp.skill.invocation_kind` | `model` \| `user` \| `autoload` | Maps to the three paths in section 3 |
| `omp.skill.provider` | `native`, `omp-plugins`, `claude`, `agents`, `codex`, `opencode`, `github`, `omp-managed` | From discovery metadata; `unknown` if unresolvable |
| `omp.session.id` | string | From event context |
| `omp.agent.role` | `default`, `smol`, `slow`, `plan`, `task`, ... | Omit if unavailable |
| `gen_ai.request.model` | string | Active model for the turn, if exposed on context |
| `vcs.repository.name` | string | Git root basename; `"none"` when no repo root resolves. Always emit the key, so the attribute set stays identical across series and the ratio in `omp.skill.turns` does not break on repo-less sessions |
| `omp.subagent` | boolean | True when the event originates inside a `task` subagent |

**Attributes** on `omp.skill.turns`: everything in the table above **except** `omp.skill.name`, `omp.skill.invocation_kind`, and `omp.skill.provider`, which are per-skill concepts. Keeping `omp.session.id`, `omp.agent.role`, `gen_ai.request.model`, `vcs.repository.name`, and `omp.subagent` aligned across both instruments is what makes the ratio sliceable by model and repo.

Follow OpenTelemetry GenAI semantic conventions for any attribute that has an established key (`gen_ai.*`, `vcs.*`). Use the `omp.*` namespace only for concepts the conventions do not cover.

**No cardinality cap on `omp.skill.name`.** Expected scale is tens of skills. Emit the real name always; do not bucket into `__other__`. The cardinality risk here is `omp.session.id`, not the skill name, so drop the session attribute first if series count becomes a problem.

## 5b. Relationship to OMP's built-in OTEL export (important)

As of **v17.0.6**, OMP ships native OpenTelemetry export. When `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` (or the shared `OTEL_EXPORTER_OTLP_ENDPOINT`) is set, omp registers its own `MeterProvider` with a `PeriodicExportingMetricReader` and records GenAI-semconv `gen_ai.client.token.usage` plus `pi.omp.agent.*` counters and histograms covering runs, steps, chat and tool calls by name, status and finish reason, latencies, estimated cost, and errors. Each signal honors its own `OTEL_*_EXPORTER=none` kill switch and the global `OTEL_SDK_DISABLED`, and non-`http/protobuf` protocols are declined.

### Decide provider ownership FIRST (this governs sections 6 and 7)

Two mutually exclusive designs. Pick **A** unless phase 0 proves it impossible, and record the choice in the README.

**Design A, ride the host's provider (preferred).** Call `metrics.getMeter(...)` and nothing else. Your instruments export through the host's already-registered reader and exporter.

- You inherit endpoint, protocol, headers, interval, and every `OTEL_*` kill switch for free.
- You **cannot** set `service.instance.id`, own the flush, or configure an interval. Those belong to the host. Section 6's endpoint/protocol/headers/interval rows therefore **do not apply**, and section 7's flush requirement is the host's job, not yours.
- Open question 7 becomes a request to the host rather than plugin work: if the host sets no instance id, note the limitation in the README and move on. Do not stand up a second provider just to set it.
- The only config that applies is `SKILL_TELEMETRY_ENABLED` and `SKILL_TELEMETRY_DEBUG`.
- `otel.ts` and `config.ts` in section 4 collapse to a few lines. That is expected, not a sign you missed something.

**Design B, own a private provider (fallback only).** Use this only if phase 0 shows no global MeterProvider is registered when extensions load, or that the host's provider cannot be reached from an extension.

- All of section 6 applies, plus section 7's flush and the timer hazard below.
- Never call `metrics.setGlobalMeterProvider`; keep your provider local to the module so you cannot clobber the host's.

**How to tell which you are in:** at `session_start`, check whether `metrics.getMeterProvider()` returns something other than the no-op provider. Log it under `SKILL_TELEMETRY_DEBUG`. If instruments silently produce nothing, this is the first thing to check.

Consequences for this plugin:

1. **Do not duplicate what is already there.** Built-in export already counts tool calls by name. It does **not** attribute skill names, because a skill read is an ordinary `read` call and the skill identity lives in the argument. That gap is this plugin's entire reason to exist.
2. **A MeterProvider may already be registered globally.** Do not call `metrics.setGlobalMeterProvider`. Acquire a meter from the existing global provider via `metrics.getMeter(...)` so this plugin's instruments ride the host's configured reader and exporter, inheriting endpoint, headers, interval, and kill switches for free. Only stand up a private provider if the host's is absent, and gate that behind a config flag.
3. **Reuse the host's env contract.** Prefer `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` over a plugin-specific variable, and respect `OTEL_SDK_DISABLED`.

Also note the host only supports `http/protobuf`. Do not add a gRPC path.

### Timer hazard

v17.0.6 added managed `ctx.setInterval`, `ctx.setTimeout`, and `ctx.clearTimer` helpers on the extension context. Callbacks scheduled through them run inside handler-dispatch isolation, and every outstanding timer is unref'd and cleared on `session_shutdown`. An extension's **self-scheduled** `setInterval`/`setTimeout` callback that throws previously ran outside the try/catch and could surface as a process-fatal `uncaughtException`, tearing down the whole session.

This directly affects any private `PeriodicExportingMetricReader`, which schedules its own bare `setInterval`. If the plugin stands up its own provider, either drive export from a managed `ctx.setInterval` calling `forceFlush()`, or wrap the reader's callback so nothing can throw out of it. Riding the host's existing provider (option 2 above) sidesteps this entirely and is the preferred design.

## 6. Configuration

**Applies in full only under Design B.** Under Design A, only the last two rows apply; the rest are owned by the host.

Resolution order: env var, then `skillTelemetry` block in `~/.omp/agent/config.yml`, then default.

| Setting | Env | Default |
| --- | --- | --- |
| OTLP endpoint | `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4318` |
| Protocol | `OTEL_EXPORTER_OTLP_PROTOCOL` | `http/protobuf` |
| Headers | `OTEL_EXPORTER_OTLP_HEADERS` | none |
| Service name | `OTEL_SERVICE_NAME` | `oh-my-pi` (host default, observed as `job="oh-my-pi"`) |
| Export interval | `SKILL_TELEMETRY_INTERVAL_MS` | `15000` |
| Enabled | `SKILL_TELEMETRY_ENABLED` | `true` |
| Debug logging | `SKILL_TELEMETRY_DEBUG` | `false` |

Honor the standard `OTEL_*` variables so the plugin drops into an existing collector setup with no plugin-specific config.

## 7. Lifecycle requirements

1. **Factory phase.** Only registration is valid during the extension factory call. Runtime action methods are not initialized yet. Construct the MeterProvider lazily on first event, or in a `session_start` handler, not at module top level.
2. **Flush on exit (Design B only; skip entirely under Design A).** Short `omp -p` one-shot runs can exit before a periodic exporter fires. Call `meterProvider.forceFlush()` then `shutdown()` on `session_shutdown`, and also on `agent_end` if the run may terminate without a shutdown event. Bound the flush with a timeout (default 2000 ms) so a dead collector never hangs the CLI.
3. **Never block the agent.** Handlers must not return `{ block: true }`. A thrown error in a `tool_call` handler **blocks the tool, fail-closed**, so every handler body must be wrapped in try/catch that swallows and logs. This is the single highest-risk defect in this plugin.
4. **Zero user-visible output** unless debug is on. No `ctx.ui.notify` on the hot path.
5. **Subagents.** `task` fans out subagents. Verify empirically whether subagent sessions load extensions in the same process; if they do, deduplicate double-counting between parent and child, and set `omp.subagent=true` on child events.

## 8. Acceptance criteria

The implementation is done when all of the following hold. All criteria use the `telemetry-probe` fixture from section 1b; **no criterion may name a skill that is not created by the test itself**.

- [ ] `read skill://telemetry-probe` in a live session produces exactly one `omp.skill.skill_reads` increment with `invocation_kind="model"`, `omp.skill.name="telemetry-probe"`.
- [ ] `read skill://telemetry-probe/assets/example.txt` increments **nothing**. Asset reads are out of scope.
- [ ] A turn in which `telemetry-probe` is read increments `omp.skill.turns` by exactly 1 and `omp.skill.skill_reads{omp.skill.name="telemetry-probe"}` by exactly 1.
- [ ] A turn with no skill read increments `omp.skill.turns` by 1 and leaves `omp.skill.skill_reads` unchanged.
- [ ] `omp.skill.turns` carries **no** `omp.skill.name` attribute, and its series count does not grow when a second fixture skill is installed.
- [ ] With `skills.enabled: false`, `omp.skill.turns` does not increment at all, since no skill was offered.
- [ ] `omp.skill.discovered_on_session_start` reports 2 when two fixture skills are installed.
- [ ] `omp.skill.name` carries the real skill name on both counters, with no bucketing.
- [ ] `/skill:telemetry-probe some args` produces one increment with `invocation_kind="user"` and does not double-count if the same skill is then read via `skill://`.
- [ ] **Three reads in one interactive session** yield a counter value of 3. Per section 1b, repeated `omp -p` runs will each report 1 and prove nothing; this assertion must be made within a single process.
- [ ] The exported resource carries a `service.instance.id` (or an equivalent instance-distinguishing attribute) so concurrent and sequential sessions do not clobber one another's series.
- [ ] Plugin series are separable from host series by instrumentation scope alone, and the plugin's own labels do not fork series on run-scoped aggregates.
- [ ] A subagent with `autoloadSkills` produces `invocation_kind="autoload"` increments, or the limitation is documented in the README with the source-level reason.
- [ ] A nonexistent `skill://nope` read increments nothing on either counter. Load errors are out of scope; confirm the handler does not crash or block the tool when the read fails.
- [ ] With the collector unreachable, the session runs normally, no tool is blocked, and the CLI exits within the flush timeout.
- [ ] `omp -p "read skill://telemetry-probe and follow it"` prints `PROBE-OK` and exports before process exit.
- [ ] `SKILL_TELEMETRY_ENABLED=false` results in no network calls and no MeterProvider construction.
- [ ] Unit tests cover `skill://` parsing: bare name, name plus asset, URL-encoded path, rejected traversal, trailing slash, uppercase name.
- [ ] README documents install, config, the metric schema table, and the known limitations.

### How to test the counter logic without a collector

The parsing tests are easy; the counter logic is where a junior stalls waiting on a live collector. Do not. Structure `main.ts` so the emission logic is a pure function of (event, state) returning a list of `{instrument, value, attributes}` records, and have the handler apply them. Then unit-test the pure function directly.

For an integration test that still needs no network, use `@opentelemetry/sdk-metrics` in the test only:

```ts
import { MeterProvider, InMemoryMetricExporter, PeriodicExportingMetricReader,
         AggregationTemporality } from "@opentelemetry/sdk-metrics";

const exporter = new InMemoryMetricExporter(AggregationTemporality.CUMULATIVE);
const provider = new MeterProvider({
  readers: [new PeriodicExportingMetricReader({ exporter })],
});
// pass provider.getMeter(...) into your factory, then assert on
// exporter.getMetrics() after forcing a collection
```

This means **the factory must accept an injectable meter** rather than reaching for the global inside itself. Default it to `metrics.getMeter(...)` in production. Design for this from phase 2; retrofitting it later is painful.

### Verification harness

The fixture and a one-shot check, for the manual transcript:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://<collector>:4318 \
       OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf \
       OTEL_TRACES_EXPORTER=none OTEL_LOGS_EXPORTER=none
mkdir -p ~/.omp/agent/skills/telemetry-probe && printf -- '---\nname: telemetry-probe\ndescription: No-op fixture skill for telemetry checks.\n---\nReply with exactly: PROBE-OK\n' > ~/.omp/agent/skills/telemetry-probe/SKILL.md
omp -p "read skill://telemetry-probe and follow it"
sleep 25
curl -s <collector>:8889/metrics | grep -E 'omp_skill|pi_omp_agent_tool_calls'
```

Ship the fixture as `test/fixtures/telemetry-probe/` in the package and have the install step copy it into a scratch skills root.

## 9. Prior art to consult (do not duplicate blindly)

- **`pi-otel`** for upstream Pi exposes an event-bus escape hatch usable from any extension: `pi.events.emit("pi-otel:log", { eventName, severity, body, attributes })`, no import required, and a no-op when pi-otel is absent. If pi-otel or an OMP equivalent is present, consider emitting through it instead of standing up a second MeterProvider in the same process.
- **Arize AX / Phoenix coding-harness-tracing** hooks OMP lifecycle events and exports OpenInference spans with no application code changes. It forwards a whitelist of lifecycle events: `before_agent_start`, `turn_end`, `agent_end`, `session_shutdown`. Useful as a reference for lifecycle handling and for its debug-dump pattern (`ARIZE_TRACE_DEBUG` writes raw event payloads to disk for inspection).
- **`o11y-dev/opentelemetry-hooks`** covers other agents using GenAI semantic conventions. Borrow its attribute naming, not its architecture.

Check whether two MeterProviders in one Bun process conflict over the global `metrics` API. If the global is already set, register a scoped meter rather than calling `metrics.setGlobalMeterProvider`.

## 10. Open questions for the implementer to resolve in source

Record answers in the README as you go. Questions marked **[answered]** were resolved empirically; do not spend time re-deriving them.

1. Exact payload shape of the `input` event: does it carry the raw `/skill:<name>` text before dispatch, or a post-dispatch structured form?
2. Does `tool_call` expose the read path as `input.path`, `input.file_path`, or something else? The field name used in the sketch below is a guess.
3. Is session/model/role metadata reachable from the handler `ctx`, or does it require the open-sdk fork? Stock OMP does not expose internals such as settings and model registry through `ExtensionAPI.openSdk`; if a needed attribute is only available there, **drop the attribute** rather than requiring a fork.
4. Do subagent sessions load user extensions?
5. Is there a `session_start` surface that exposes the discovered skills list? Needed for `omp.skill.discovered_on_session_start`, and for gating `omp.skill.turns` on whether any skill was actually offered. Less critical than it was under the removed consideration design, since `turns` needs only a count and a non-empty check rather than the full name set.
9. Does a `turn_end` event exist on `ExtensionAPI`, and does its context expose the session and model metadata needed for attributes? The Arize integration forwards `before_agent_start`, `turn_end`, `agent_end`, and `session_shutdown`, so `turn_end` is very likely available, but confirm the payload. This is **blocking** for `omp.skill.turns`, which is meaningless without a reliable turn boundary. If turns are not cleanly observable, count agent runs at `agent_end` instead, rename the instrument accordingly, and document the change in meaning rather than quietly relabeling runs as turns.
6. **Highest priority.** Does `/skill:<name>` move `pi_omp_agent_tool_calls_total` at all? Expectation is **no**, because the slash command reads the skill file directly from `filePath` rather than going through the `read` tool. If confirmed, the user-invocation path is invisible to the host entirely and the `input` event is the plugin's only hook for it, which makes question 1 blocking. Verify in the TUI with a scrape before and after `/skill:telemetry-probe`.
7. Does the host set `service.instance.id` on its resource? The observed series carried only `job="oh-my-pi"` with nothing instance-distinguishing. If the host does not set one, the plugin must, or cross-session aggregation is impossible.
8. **[answered]** Skill file location, description requirement, host counter shape, scope name, per-process counter semantics. See section 1b.

## 11. Reference sketch

Illustrative only. Field names marked `TODO` are unverified guesses from section 10 and **must** be confirmed against `packages/coding-agent/src/extensibility/hooks/types.ts` before this compiles against reality.

```ts
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";
import { metrics, type Attributes } from "@opentelemetry/api";

// skill://<name>            -> hydration, count it
// skill://<name>/<asset>    -> asset read, out of scope, ignore
const SKILL_URL = /^skill:\/\/([^/?#]+)(\/[^?#]*)?$/i;

export default function (pi: ExtensionAPI) {
  const meter = metrics.getMeter("omp.skill-telemetry", "1.0.0");

  const skillReads = meter.createCounter("omp.skill.skill_reads", {
    unit: "{read}",
    description: "Hydrations of a skill body, by skill name and invocation kind",
  });
  const turns = meter.createCounter("omp.skill.turns", {
    unit: "{turn}",
    description: "Turns in which at least one skill was offered to the model",
  });
  const discovered = meter.createUpDownCounter(
    "omp.skill.discovered_on_session_start",
    { unit: "{skill}", description: "Skills discovered when the session started" },
  );

  // Offered set is resolved once: skills are discovered at startup and do not
  // change mid-session absent /reload-plugins.
  let skillsOffered = 0;

  /** Attributes shared by BOTH instruments. Never put a skill name in here. */
  function contextAttrs(ctx: unknown): Attributes {
    return {
      "omp.session.id": /* TODO ctx.sessionId */ "unknown",
      "gen_ai.request.model": /* TODO */ "unknown",
      // Always emit the key with a sentinel, never omit it: a missing key on one
      // instrument and not the other breaks the reads/turns ratio at query time.
      "vcs.repository.name": /* TODO */ "none",
      "omp.subagent": /* TODO */ false,
    };
  }

  pi.on("session_start", async (_event, ctx) => {
    try {
      const skills = /* TODO: discovered skills list, see open question 5 */ [] as unknown[];
      skillsOffered = skills.length;
      if (skillsOffered > 0) discovered.add(skillsOffered, contextAttrs(ctx));
    } catch {
      // telemetry must never break a session
    }
  });

  pi.on("tool_call", async (event, ctx) => {
    try {
      if (event.toolName !== "read") return;
      // TODO: confirm the argument key. input.path is a guess.
      const raw = String((event as any).input?.path ?? "");
      const match = SKILL_URL.exec(raw);
      if (!match) return;

      const [, name, asset] = match;
      if (asset) return; // asset read, explicitly out of scope

      skillReads.add(1, {
        ...contextAttrs(ctx),
        "omp.skill.name": name.toLowerCase(),
        "omp.skill.invocation_kind": "model",
      });
    } catch {
      // A throw here BLOCKS the tool, fail-closed. Swallow everything.
    }
  });

  pi.on("turn_end", async (_event, ctx) => {
    try {
      // Only count turns where a read was actually possible. A turn with no
      // skills offered is not an opportunity and would inflate the denominator.
      if (skillsOffered > 0) turns.add(1, contextAttrs(ctx));
    } catch {
      // swallow
    }
  });
}
```

Not shown, and still required:

- The `/skill:<name>` path via the `input` event, emitting `invocation_kind="user"` (open questions 1 and 6).
- The autoload path, emitting `invocation_kind="autoload"` (open question 4), or a documented decision not to cover it.
- `omp.skill.provider`, which needs discovery metadata the sketch does not have wired.
- Resolution of `contextAttrs`, every field of which is currently a placeholder.
- `service.instance.id` on the resource, per open question 7.

## 12. Deliverables

1. The package as laid out in section 4, installable by adding its path to `extensions:` in `~/.omp/agent/config.yml`.
2. README with install, config table, metric schema, limitations, and answers to section 10. It must explicitly state: which design (A or B) was chosen and why, which of the three invocation paths are covered and which are not, what "turn" resolved to in practice, and whether `service.instance.id` is present.
3. Unit tests for the parsing layer.
4. A manual verification transcript covering each acceptance criterion, run against a local collector.
