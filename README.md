# skill-telemetry

An [Oh My Pi](https://github.com/can1357/oh-my-pi) (omp) plugin that reports which skills the agent actually loads — by name, how they were loaded, and how often that happens relative to turns where a skill could have been used.

Metrics go to whatever OTLP collector omp is already exporting to. You do not configure a second exporter.

## Install

You need [omp](https://github.com/can1357/oh-my-pi) and an OTLP metrics endpoint.

```bash
git clone https://github.com/sazlin/skill-telemetry.git
cd skill-telemetry
npm install
omp plugin install .
```

Start a new omp session (extensions load at session start, not via `/reload-plugins`).

If omp is already sending metrics, you are done. Otherwise point it at a collector before starting:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
export OTEL_TRACES_EXPORTER=none
export OTEL_LOGS_EXPORTER=none
```

Use a base URL. omp appends `/v1/metrics`. If you set `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` instead, include the full path (`…/v1/metrics`) or export fails silently.

From GitHub without cloning:

```bash
omp plugin install github:sazlin/skill-telemetry
```

To try a single run from a checkout without installing:

```bash
omp -e "$PWD/src/main.ts" -p "read skill://telemetry-probe and follow it"
```

## What you get

| Metric | Meaning |
| --- | --- |
| `omp.skill.skill_reads` | A skill body was loaded into context |
| `omp.skill.turns` | A turn where at least one skill was offered to the model |
| `omp.skill.discovered_on_session_start` | How many skills were discovered when the session started |

Series live under the instrumentation scope `omp.skill-telemetry`, separate from omp's own `@oh-my-pi/pi-coding-agent` metrics.

Useful query: how often skill `x` is loaded, as a fraction of turns:

```
rate(omp_skill_skill_reads_total{omp_skill_name="x"}) / rate(omp_skill_turns_total)
```

`omp.skill.turns` is the denominator. It is not per skill.

A read is counted when:

- the model does `read skill://<name>` (the skill body, not an asset file)
- you invoke `/skill:<name>` in the TUI
- a subagent autoloads a skill

Failed reads and `skill://<name>/some-asset` are ignored.

## Labels

On skill reads: `omp.skill.name`, `omp.skill.invocation_kind` (`model`, `user`, or `autoload`), `omp.skill.provider`.

On both reads and turns: `omp.session.id`, `gen_ai.request.model`, `vcs.repository.name` (`none` when there is no git root), `omp.subagent`.

## Plugin settings

| Setting | Env | `~/.omp/agent/config.yml` | Default |
| --- | --- | --- | --- |
| Enabled | `SKILL_TELEMETRY_ENABLED` | `skillTelemetry.enabled` | `true` |
| Debug logs | `SKILL_TELEMETRY_DEBUG` | `skillTelemetry.debug` | `false` |

Env wins over the YAML block. Collector URL, protocol, headers, and export interval are omp's, via the usual `OTEL_*` variables.

```yaml
skillTelemetry:
  enabled: true
  debug: false
```

`SKILL_TELEMETRY_ENABLED=false` disables the plugin entirely.

## Notes

- Restart omp after installing or changing this plugin.
- `/skill:…` metrics need the interactive UI (or RPC input). `omp -p` only sees model `skill://` reads.
- Counters reset every process. Repeated `omp -p` runs each export `1`; watch increments inside one session.
- omp does not set `service.instance.id`, so concurrent sessions can overwrite the same Prometheus series. Set `OTEL_RESOURCE_ATTRIBUTES=service.instance.id=<unique>` on the omp process if you need to tell them apart.
- A down collector must not break the session. If it does, that is an omp export issue, not this plugin.

```bash
npm test
```
