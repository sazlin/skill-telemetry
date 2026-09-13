import type { ExtensionAPI, ExtensionContext } from "@oh-my-pi/pi-coding-agent";
import type { Attributes, Meter } from "@opentelemetry/api";
import { loadConfig } from "./config.ts";
import { getMeter, isNoopMeterProvider, SCOPE } from "./otel.ts";
import { parseSkillCommand, parseSkillUrl, repoName, skillProvider } from "./skills.ts";

export type CtxAttrs = {
  "omp.session.id": string;
  "gen_ai.request.model": string;
  "vcs.repository.name": string;
  "omp.subagent": boolean;
};

export type Instrument =
  | "omp.skill.skill_reads"
  | "omp.skill.turns"
  | "omp.skill.discovered_on_session_start";

export type Emission = { instrument: Instrument; value: number; attributes: Attributes };

export type State = {
  offered: boolean;
  providers: Map<string, string>;
  userThisTurn: Set<string>;
  seenAutoload: Set<string>;
};

export type TelemetryEvent =
  | { type: "session_start"; skillCount: number; offered: boolean; providers: Record<string, string>; subagent: boolean }
  | { type: "turn_start" }
  | { type: "turn_end" }
  | { type: "user_skill"; name: string }
  | { type: "autoload_skill"; id: string; name: string }
  | { type: "model_read"; name: string; asset: boolean; error: boolean };

const SUBAGENT_MARK = "assigned to you by the main agent";

export function createState(): State {
  return { offered: false, providers: new Map(), userThisTurn: new Set(), seenAutoload: new Set() };
}

function reads(attrs: CtxAttrs, name: string, kind: "model" | "user" | "autoload", provider: string): Emission {
  return {
    instrument: "omp.skill.skill_reads",
    value: 1,
    attributes: {
      ...attrs,
      "omp.skill.name": name,
      "omp.skill.invocation_kind": kind,
      "omp.skill.provider": provider,
    },
  };
}

export function decide(state: State, event: TelemetryEvent, attrs: CtxAttrs): Emission[] {
  switch (event.type) {
    case "session_start": {
      state.offered = event.offered;
      state.providers = new Map(Object.entries(event.providers));
      state.userThisTurn.clear();
      state.seenAutoload.clear();
      if (event.skillCount > 0 && !event.subagent) {
        return [{ instrument: "omp.skill.discovered_on_session_start", value: event.skillCount, attributes: attrs }];
      }
      return [];
    }
    case "turn_start":
      state.userThisTurn.clear();
      return [];
    case "turn_end":
      return state.offered ? [{ instrument: "omp.skill.turns", value: 1, attributes: attrs }] : [];
    case "user_skill": {
      if (!state.providers.has(event.name)) return [];
      state.userThisTurn.add(event.name);
      return [reads(attrs, event.name, "user", state.providers.get(event.name) ?? "unknown")];
    }
    case "autoload_skill": {
      if (state.seenAutoload.has(event.id) || !state.providers.has(event.name)) return [];
      state.seenAutoload.add(event.id);
      return [reads(attrs, event.name, "autoload", state.providers.get(event.name) ?? "unknown")];
    }
    case "model_read": {
      if (event.asset || event.error || state.userThisTurn.has(event.name)) return [];
      return [reads(attrs, event.name, "model", state.providers.get(event.name) ?? "unknown")];
    }
    default: {
      const _never: never = event;
      return _never;
    }
  }
}

type SkillSnap = { name: string; hide?: boolean; source?: string; _source?: { provider?: string } };

function activeSkills(pi: ExtensionAPI): SkillSnap[] {
  const list = pi.pi.getActiveSkills();
  if (list.length > 0) return [...list];
  return pi
    .getCommands()
    .filter((cmd) => cmd.name.startsWith("skill:"))
    .map((cmd) => ({ name: cmd.name.slice("skill:".length) }));
}

function providersFrom(skills: SkillSnap[]): Record<string, string> {
  const providers: Record<string, string> = {};
  for (const skill of skills) providers[skill.name.toLowerCase()] = skillProvider(skill);
  return providers;
}

function isSubagent(ctx: ExtensionContext): boolean {
  return ctx.getSystemPrompt().some((line) => line.includes(SUBAGENT_MARK));
}

function attrs(ctx: ExtensionContext): CtxAttrs {
  return {
    "omp.session.id": ctx.sessionManager.getSessionId() || "unknown",
    "gen_ai.request.model": ctx.model?.id || ctx.models.current()?.id || "unknown",
    "vcs.repository.name": repoName(ctx.cwd),
    "omp.subagent": isSubagent(ctx),
  };
}

function autoloads(ctx: ExtensionContext): Array<{ id: string; name: string }> {
  const out: Array<{ id: string; name: string }> = [];
  for (const entry of ctx.sessionManager.getBranch()) {
    if (entry.type !== "custom_message" || entry.customType !== "skill-prompt") continue;
    if (entry.attribution === "user") continue;
    const details = entry.details;
    const name =
      details && typeof details === "object" && "name" in details && typeof details.name === "string"
        ? details.name.toLowerCase()
        : "";
    if (name) out.push({ id: entry.id, name });
  }
  return out;
}

/** Info-level file log for a counted skill-body hydration. */
export function skillReadLogLine(attributes: Attributes): string {
  const name = String(attributes["omp.skill.name"] ?? "unknown");
  const kind = String(attributes["omp.skill.invocation_kind"] ?? "unknown");
  const provider = String(attributes["omp.skill.provider"] ?? "unknown");
  const model = String(attributes["gen_ai.request.model"] ?? "unknown");
  const repo = String(attributes["vcs.repository.name"] ?? "none");
  const session = String(attributes["omp.session.id"] ?? "unknown");
  const subagent = attributes["omp.subagent"] === true;
  return `[${SCOPE}] skill read name=${name} invocation_kind=${kind} provider=${provider} model=${model} repo=${repo} session=${session} subagent=${subagent}`;
}

function apply(
  inst: {
    skill_reads: { add: (v: number, a?: Attributes) => void };
    turns: { add: (v: number, a?: Attributes) => void };
    discovered: { add: (v: number, a?: Attributes) => void };
  },
  rows: Emission[],
): void {
  for (const row of rows) {
    switch (row.instrument) {
      case "omp.skill.skill_reads":
        inst.skill_reads.add(row.value, row.attributes);
        break;
      case "omp.skill.turns":
        inst.turns.add(row.value, row.attributes);
        break;
      case "omp.skill.discovered_on_session_start":
        inst.discovered.add(row.value, row.attributes);
        break;
      default: {
        const _never: never = row.instrument;
        return _never;
      }
    }
  }
}

export type SkillTelemetryOptions = { meter?: Meter };

export default function skillTelemetry(pi: ExtensionAPI, options?: SkillTelemetryOptions): void {
  const cfg = loadConfig();
  if (!cfg.enabled && !options?.meter) return;

  let inst:
    | {
        skill_reads: { add: (v: number, a?: Attributes) => void };
        turns: { add: (v: number, a?: Attributes) => void };
        discovered: { add: (v: number, a?: Attributes) => void };
      }
    | undefined;
  const state = createState();

  const meters = () => {
    if (inst) return inst;
    const meter = options?.meter ?? getMeter();
    inst = {
      skill_reads: meter.createCounter("omp.skill.skill_reads", {
        unit: "{read}",
        description: "Hydrations of a skill body, by skill name and invocation kind",
      }),
      turns: meter.createCounter("omp.skill.turns", {
        unit: "{turn}",
        description: "Turns in which at least one skill was offered to the model",
      }),
      discovered: meter.createUpDownCounter("omp.skill.discovered_on_session_start", {
        unit: "{skill}",
        description: "Skills discovered when the session started",
      }),
    };
    return inst;
  };

  const run = (event: TelemetryEvent, ctx: ExtensionContext) => {
    const rows = decide(state, event, attrs(ctx));
    apply(meters(), rows);
    for (const row of rows) {
      if (row.instrument !== "omp.skill.skill_reads") continue;
      pi.logger.info(skillReadLogLine(row.attributes), { ...row.attributes });
    }
  };

  const swallow = (label: string, fn: () => void) => {
    try {
      fn();
    } catch (error) {
      if (cfg.debug) pi.logger.debug(`[${SCOPE}] ${label}`, { error });
    }
  };

  pi.on("session_start", async (_event, ctx) => {
    swallow("session_start", () => {
      if (cfg.debug) {
        pi.logger.debug(`[${SCOPE}] meter provider`, {
          scope: SCOPE,
          noop: isNoopMeterProvider(),
        });
      }
      const skills = activeSkills(pi);
      const read = pi.getActiveTools().includes("read");
      run(
        {
          type: "session_start",
          skillCount: skills.length,
          offered: read && skills.some((s) => s.hide !== true),
          providers: providersFrom(skills),
          subagent: isSubagent(ctx),
        },
        ctx,
      );
    });
  });

  pi.on("input", async (event, ctx) => {
    swallow("input", () => {
      const parsed = parseSkillCommand(event.text);
      if (parsed) run({ type: "user_skill", name: parsed.name }, ctx);
    });
  });

  pi.on("turn_start", async (_event, ctx) => {
    swallow("turn_start", () => {
      if (state.providers.size === 0) {
        const skills = activeSkills(pi);
        for (const [name, provider] of Object.entries(providersFrom(skills))) state.providers.set(name, provider);
        if (skills.length > 0) state.offered = pi.getActiveTools().includes("read") && skills.some((s) => s.hide !== true);
      }
      run({ type: "turn_start" }, ctx);
      for (const row of autoloads(ctx)) run({ type: "autoload_skill", id: row.id, name: row.name }, ctx);
    });
  });

  pi.on("turn_end", async (_event, ctx) => {
    swallow("turn_end", () => run({ type: "turn_end" }, ctx));
  });

  pi.on("tool_result", async (event, ctx) => {
    swallow("tool_result", () => {
      if (event.toolName !== "read") return;
      const raw = String((event.input as { path?: unknown }).path ?? "");
      const parsed = parseSkillUrl(raw);
      if (!parsed) return;
      run(
        { type: "model_read", name: parsed.name, asset: parsed.asset !== undefined, error: event.isError === true },
        ctx,
      );
    });
  });
}
