import assert from "node:assert/strict";
import { describe, test } from "node:test";
import skillTelemetry, { createState, decide, skillReadLogLine, type CtxAttrs } from "../src/main.ts";

const attrs: CtxAttrs = {
  "omp.session.id": "s1",
  "gen_ai.request.model": "test-model",
  "vcs.repository.name": "skill-telemetry",
  "omp.subagent": false,
};

const providers = { "telemetry-probe": "native", "other-probe": "native" };

describe("decide", () => {
  test("session_start records discovered skills and not on subagent", () => {
    const parent = createState();
    assert.deepEqual(
      decide(parent, { type: "session_start", skillCount: 2, offered: true, providers, subagent: false }, attrs),
      [{ instrument: "omp.skill.discovered_on_session_start", value: 2, attributes: attrs }],
    );

    const child = createState();
    assert.deepEqual(
      decide(
        child,
        { type: "session_start", skillCount: 2, offered: true, providers, subagent: true },
        { ...attrs, "omp.subagent": true },
      ),
      [],
    );
  });

  test("turns increment once per offered turn and carry no skill name", () => {
    const state = createState();
    decide(state, { type: "session_start", skillCount: 2, offered: true, providers, subagent: false }, attrs);
    const rows = decide(state, { type: "turn_end" }, attrs);
    assert.equal(rows.length, 1);
    assert.equal(rows[0]?.instrument, "omp.skill.turns");
    assert.equal(rows[0]?.value, 1);
    assert.equal(rows[0]?.attributes["omp.skill.name"], undefined);
  });

  test("turns do not increment when no skill was offered", () => {
    const state = createState();
    decide(state, { type: "session_start", skillCount: 0, offered: false, providers: {}, subagent: false }, attrs);
    assert.deepEqual(decide(state, { type: "turn_end" }, attrs), []);
  });

  test("model body read increments; asset and error do not", () => {
    const state = createState();
    decide(state, { type: "session_start", skillCount: 1, offered: true, providers, subagent: false }, attrs);
    assert.deepEqual(decide(state, { type: "model_read", name: "telemetry-probe", asset: false, error: false }, attrs), [
      {
        instrument: "omp.skill.skill_reads",
        value: 1,
        attributes: {
          ...attrs,
          "omp.skill.name": "telemetry-probe",
          "omp.skill.invocation_kind": "model",
          "omp.skill.provider": "native",
        },
      },
    ]);
    assert.deepEqual(decide(state, { type: "model_read", name: "telemetry-probe", asset: true, error: false }, attrs), []);
    assert.deepEqual(decide(state, { type: "model_read", name: "nope", asset: false, error: true }, attrs), []);
  });

  test("three model reads in one session yield three increments", () => {
    const state = createState();
    decide(state, { type: "session_start", skillCount: 1, offered: true, providers, subagent: false }, attrs);
    let n = 0;
    for (let i = 0; i < 3; i++) {
      n += decide(state, { type: "model_read", name: "telemetry-probe", asset: false, error: false }, attrs).length;
    }
    assert.equal(n, 3);
  });

  test("user invocation is not double-counted with a following model read", () => {
    const state = createState();
    decide(state, { type: "session_start", skillCount: 1, offered: true, providers, subagent: false }, attrs);
    decide(state, { type: "turn_start" }, attrs);
    const user = decide(state, { type: "user_skill", name: "telemetry-probe" }, attrs);
    assert.equal(user[0]?.attributes["omp.skill.invocation_kind"], "user");
    assert.deepEqual(decide(state, { type: "model_read", name: "telemetry-probe", asset: false, error: false }, attrs), []);
  });

  test("autoload counts once per entry", () => {
    const state = createState();
    decide(state, { type: "session_start", skillCount: 1, offered: true, providers, subagent: false }, attrs);
    const first = decide(state, { type: "autoload_skill", id: "e1", name: "telemetry-probe" }, attrs);
    assert.equal(first[0]?.attributes["omp.skill.invocation_kind"], "autoload");
    assert.deepEqual(decide(state, { type: "autoload_skill", id: "e1", name: "telemetry-probe" }, attrs), []);
  });

  test("disabled factory registers no handlers", () => {
    const prev = process.env.SKILL_TELEMETRY_ENABLED;
    process.env.SKILL_TELEMETRY_ENABLED = "false";
    let n = 0;
    skillTelemetry({
      on() {
        n++;
      },
    } as never);
    if (prev === undefined) delete process.env.SKILL_TELEMETRY_ENABLED;
    else process.env.SKILL_TELEMETRY_ENABLED = prev;
    assert.equal(n, 0);
  });

  test("skillReadLogLine puts name and context in the message", () => {
    const line = skillReadLogLine({
      ...attrs,
      "omp.skill.name": "telemetry-probe",
      "omp.skill.invocation_kind": "model",
      "omp.skill.provider": "native",
    });
    assert.match(line, /skill read/);
    assert.match(line, /name=telemetry-probe/);
    assert.match(line, /invocation_kind=model/);
    assert.match(line, /provider=native/);
    assert.match(line, /model=test-model/);
    assert.match(line, /repo=skill-telemetry/);
    assert.match(line, /session=s1/);
    assert.match(line, /subagent=false/);
  });

  test("injectable meter records discovered on session_start", async () => {
    const prev = process.env.SKILL_TELEMETRY_ENABLED;
    process.env.SKILL_TELEMETRY_ENABLED = "true";
    const adds: Array<[number, unknown]> = [];
    const instrument = { add: (value: number, attributes?: unknown) => adds.push([value, attributes]) };
    const handlers = new Map<string, (event: unknown, ctx: unknown) => unknown>();
    skillTelemetry(
      {
        on(event: string, handler: (event: unknown, ctx: unknown) => unknown) {
          handlers.set(event, handler);
        },
        logger: { debug() {}, info() {} },
        getActiveTools: () => ["read"],
        getCommands: () => [],
        pi: {
          getActiveSkills: () => [{ name: "telemetry-probe", source: "native:user", _source: { provider: "native" } }],
        },
      } as never,
      {
        meter: {
          createCounter: () => instrument,
          createUpDownCounter: () => instrument,
        } as never,
      },
    );
    await handlers.get("session_start")?.(
      { type: "session_start" },
      {
        cwd: "/tmp",
        model: { id: "test-model" },
        models: { current: () => ({ id: "test-model" }) },
        getSystemPrompt: () => [],
        sessionManager: { getSessionId: () => "s1", getBranch: () => [] },
      },
    );
    if (prev === undefined) delete process.env.SKILL_TELEMETRY_ENABLED;
    else process.env.SKILL_TELEMETRY_ENABLED = prev;
    assert.equal(adds.length, 1);
    assert.equal(adds[0]?.[0], 1);
  });

  test("skill body read emits an info log; asset read does not", async () => {
    const prev = process.env.SKILL_TELEMETRY_ENABLED;
    process.env.SKILL_TELEMETRY_ENABLED = "true";
    const infos: Array<{ message: string; context: unknown }> = [];
    const handlers = new Map<string, (event: unknown, ctx: unknown) => unknown>();
    const ctx = {
      cwd: "/tmp",
      model: { id: "test-model" },
      models: { current: () => ({ id: "test-model" }) },
      getSystemPrompt: () => [],
      sessionManager: { getSessionId: () => "s1", getBranch: () => [] },
    };
    skillTelemetry(
      {
        on(event: string, handler: (event: unknown, ctx: unknown) => unknown) {
          handlers.set(event, handler);
        },
        logger: {
          debug() {},
          info(message: string, context?: unknown) {
            infos.push({ message, context });
          },
        },
        getActiveTools: () => ["read"],
        getCommands: () => [],
        pi: {
          getActiveSkills: () => [{ name: "telemetry-probe", source: "native:user", _source: { provider: "native" } }],
        },
      } as never,
      {
        meter: {
          createCounter: () => ({ add() {} }),
          createUpDownCounter: () => ({ add() {} }),
        } as never,
      },
    );
    await handlers.get("session_start")?.({ type: "session_start" }, ctx);
    await handlers.get("tool_result")?.(
      { toolName: "read", input: { path: "skill://telemetry-probe" }, isError: false },
      ctx,
    );
    await handlers.get("tool_result")?.(
      { toolName: "read", input: { path: "skill://telemetry-probe/assets/example.txt" }, isError: false },
      ctx,
    );
    if (prev === undefined) delete process.env.SKILL_TELEMETRY_ENABLED;
    else process.env.SKILL_TELEMETRY_ENABLED = prev;
    assert.equal(infos.length, 1);
    assert.match(infos[0]?.message ?? "", /name=telemetry-probe/);
    assert.match(infos[0]?.message ?? "", /invocation_kind=model/);
    assert.equal((infos[0]?.context as { "omp.skill.name"?: string })["omp.skill.name"], "telemetry-probe");
  });
});
