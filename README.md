<div align="center">

# skill-telemetry

An Oh My Pi plugin that reports which skills the agent actually loads, and how often.

[![CI](https://img.shields.io/github/actions/workflow/status/sazlin/skill-telemetry/ci.yml?branch=master)](https://github.com/sazlin/skill-telemetry/actions/workflows/ci.yml)
[![Status: alpha](https://img.shields.io/badge/status-alpha-orange)](https://github.com/sazlin/skill-telemetry)

</div>

## Features

- **Named skill metrics.** omp already counts `read` tool calls. This plugin adds the skill name, load path, and a turn denominator.
- **Ride the host exporter.** Instruments use omp's MeterProvider. No second OTLP config.
- **Three load paths.** Model `skill://` reads, `/skill:` commands, and subagent autoload.
- **Fail open.** Handler errors are swallowed so telemetry cannot block a tool or the session.

## Installation

Requires [omp](https://github.com/can1357/oh-my-pi) and an OTLP metrics endpoint.

```bash
omp plugin install github:sazlin/skill-telemetry
```

Start a new omp session. Extensions load at session start, not via `/reload-plugins`.

If omp is already sending metrics, you are done. Otherwise set these before starting:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
export OTEL_TRACES_EXPORTER=none
export OTEL_LOGS_EXPORTER=none
```

Use a base URL. omp appends `/v1/metrics`. If you set `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` instead, include the full path (`…/v1/metrics`) or export fails silently.

<details>
<summary>Install from a local checkout</summary>

```bash
git clone https://github.com/sazlin/skill-telemetry.git
cd skill-telemetry
npm install
omp plugin install .
```

</details>

## Quick start

From a checkout, copy the probe skill and run one turn against this plugin:

```bash
mkdir -p ~/.omp/agent/skills/telemetry-probe
cp test/fixtures/telemetry-probe/SKILL.md ~/.omp/agent/skills/telemetry-probe/SKILL.md
omp --no-extensions -e "$PWD/src/main.ts" -p "read skill://telemetry-probe and follow it"
```

```
PROBE-OK
```

The probe skill asks the model to reply with exactly that string. Metrics go to whatever collector omp is already exporting to.

## Metrics

| Metric | Meaning |
| --- | --- |
| `omp.skill.skill_reads` | A skill body was loaded into context |
| `omp.skill.turns` | A turn where at least one skill was offered to the model |
| `omp.skill.discovered_on_session_start` | How many skills were discovered when the session started |

Series live under the instrumentation scope `omp.skill-telemetry`, separate from omp's own `@oh-my-pi/pi-coding-agent` metrics.

How often skill `x` is loaded, as a fraction of turns:

```promql
rate(omp_skill_skill_reads_total{omp_skill_name="x"}) / rate(omp_skill_turns_total)
```

`omp.skill.turns` is the denominator. It is not per skill.

A read is counted when the model does `read skill://<name>` (the skill body, not an asset), you invoke `/skill:<name>` in the TUI, or a subagent autoloads a skill. Each counted read also writes an info line to omp's file log (`~/.omp/logs/`) with the skill name, invocation kind, provider, model, repo, session, and whether it was a subagent. Failed reads and `skill://<name>/some-asset` are ignored.

On skill reads: `omp.skill.name`, `omp.skill.invocation_kind` (`model`, `user`, or `autoload`), `omp.skill.provider`. On both reads and turns: `omp.session.id`, `gen_ai.request.model`, `vcs.repository.name` (`none` when there is no git root), `omp.subagent`.

| Setting | Env | `~/.omp/agent/config.yml` | Default |
| --- | --- | --- | --- |
| Enabled | `SKILL_TELEMETRY_ENABLED` | `skillTelemetry.enabled` | `true` |
| Debug logs | `SKILL_TELEMETRY_DEBUG` | `skillTelemetry.debug` | `false` |

Env wins over the YAML block. Collector URL, protocol, headers, and export interval are omp's, via the usual `OTEL_*` variables. `SKILL_TELEMETRY_ENABLED=false` disables the plugin entirely.

```yaml
skillTelemetry:
  enabled: true
  debug: false
```

Notes:

- Restart omp after installing or changing this plugin.
- `/skill:…` metrics need the interactive UI (or RPC input). `omp -p` only sees model `skill://` reads.
- Counters reset every process. Repeated `omp -p` runs each export `1`; watch increments inside one session.
- omp does not set `service.instance.id`, so concurrent sessions can overwrite the same Prometheus series. Set `OTEL_RESOURCE_ATTRIBUTES=service.instance.id=<unique>` on the omp process if you need to tell them apart.
- A down collector must not break the session. If it does, that is an omp export issue, not this plugin.

## Documentation

- [Design spec](skill-telemetry-spec.md) for the metric contract and acceptance checks
- [Oh My Pi extension docs](https://github.com/can1357/oh-my-pi/blob/main/docs/extensions.md) for the host API this plugin rides
- [Manual verification transcript](test/manual-transcript.md) for what unit tests cover versus a live collector

## Contributing

Issues and pull requests are welcome at [github.com/sazlin/skill-telemetry](https://github.com/sazlin/skill-telemetry/issues). This repo is alpha; open an issue before large work.

Maintainer commands use [just](https://github.com/casey/just):

```bash
just install
just test
```

`just --list` shows plugin install, the probe fixture, and loadout sync recipes.

## License

This repository does not currently include a LICENSE file.
