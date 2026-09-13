import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

export type Config = { enabled: boolean; debug: boolean };

function flag(raw: string | undefined): boolean | undefined {
  if (raw === undefined) return undefined;
  const v = raw.trim().toLowerCase();
  if (v === "1" || v === "true" || v === "yes" || v === "on") return true;
  if (v === "0" || v === "false" || v === "no" || v === "off") return false;
  return undefined;
}

function fileFlags(): Partial<Config> {
  try {
    const text = readFileSync(join(homedir(), ".omp/agent/config.yml"), "utf8");
    const block = /^skillTelemetry:\n((?:[ \t]+.+\n?)*)/m.exec(text)?.[1];
    if (!block) return {};
    const enabled = /^\s+enabled:\s*(true|false)\s*$/m.exec(block)?.[1];
    const debug = /^\s+debug:\s*(true|false)\s*$/m.exec(block)?.[1];
    return {
      ...(enabled ? { enabled: enabled === "true" } : {}),
      ...(debug ? { debug: debug === "true" } : {}),
    };
  } catch {
    return {};
  }
}

export function loadConfig(): Config {
  const file = fileFlags();
  return {
    enabled: flag(process.env.SKILL_TELEMETRY_ENABLED) ?? file.enabled ?? true,
    debug: flag(process.env.SKILL_TELEMETRY_DEBUG) ?? file.debug ?? false,
  };
}
