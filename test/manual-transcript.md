# Manual verification transcript

Date: 2026-09-12. Host: omp 18.1.15. Plugin: skill-telemetry 0.1.0.

## Unit tests (no collector)

```
npm test
# 16 pass, 0 fail
```

Covered:

| Criterion | Result |
| --- | --- |
| `skill://` parsing: bare name, asset, URL-encoded, traversal, trailing slash, uppercase | pass (`test/skills.test.ts`) |
| `read skill://telemetry-probe` → one `skill_reads` with `invocation_kind=model` | pass (`decide` model body read) |
| `skill://telemetry-probe/assets/example.txt` increments nothing | pass |
| Turn with a read: turns +1 and skill_reads +1 | pass (separate turn_end + model_read cases) |
| Turn with no read: turns +1, skill_reads unchanged | pass |
| `omp.skill.turns` has no `omp.skill.name` | pass |
| `skills.enabled: false` / nothing offered: turns does not increment | pass |
| `discovered_on_session_start` is 2 for two fixtures | pass (`skillCount: 2`) |
| Real skill name, no bucketing | pass |
| `/skill:telemetry-probe` → `invocation_kind=user`, no double-count with following model read | pass |
| Three reads in one session → 3 | pass |
| Plugin series use scope `omp.skill-telemetry` (not host aggregates as labels) | pass (instruments created with that name; attributes are the spec set only) |
| `skill://nope` error increments nothing | pass |
| `SKILL_TELEMETRY_ENABLED=false` registers no handlers / does not construct instruments | pass |
| Autoload `invocation_kind=autoload`, once per entry | pass |
| Subagent does not re-add discovered | pass |

## Live collector

Not run. This environment has no OTLP collector and a live `omp -p` turn was not executed (would call the configured model).

Harness for a collector (from the spec):

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://<collector>:4318 \
       OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf \
       OTEL_TRACES_EXPORTER=none OTEL_LOGS_EXPORTER=none
mkdir -p ~/.omp/agent/skills/telemetry-probe
cp test/fixtures/telemetry-probe/SKILL.md ~/.omp/agent/skills/telemetry-probe/SKILL.md
omp --no-extensions -e "$PWD/src/main.ts" -p "read skill://telemetry-probe and follow it"
sleep 25
curl -s <collector>:8889/metrics | grep -E 'omp_skill|pi_omp_agent_tool_calls'
```

Expected live checks still outstanding: `PROBE-OK` print, scrape of `omp_skill_skill_reads_total{omp_skill_name="telemetry-probe",omp_skill_invocation_kind="model"}`, unreachable collector does not hang (Design A: host flush), `service.instance.id` absent unless `OTEL_RESOURCE_ATTRIBUTES` is set on the host, TUI `/skill:telemetry-probe` user path, subagent `autoloadSkills`.
