import { existsSync } from "node:fs";
import { basename, dirname, join, resolve } from "node:path";

const PROVIDERS = new Set([
  "native",
  "omp-plugins",
  "claude",
  "agents",
  "codex",
  "opencode",
  "github",
  "omp-managed",
]);

export type SkillUrl = { name: string; asset?: string };

/** Parse a `skill://` target. Returns undefined for non-skill URLs and rejected paths. */
export function parseSkillUrl(raw: string): SkillUrl | undefined {
  const trimmed = raw.trim();
  const prefix = /^skill:\/\//i.exec(trimmed);
  if (!prefix) return undefined;
  let rest = trimmed.slice(prefix[0].length).split(/[?#]/, 1)[0] ?? "";
  try {
    rest = decodeURIComponent(rest);
  } catch {
    return undefined;
  }
  if (rest.split(/[\\/]/).includes("..") || rest.startsWith("/") || rest.startsWith("\\")) return undefined;
  const slash = rest.search(/[\\/]/);
  const host = slash === -1 ? rest : rest.slice(0, slash);
  const name = host.toLowerCase();
  if (!name) return undefined;
  const after = slash === -1 ? "" : rest.slice(slash + 1).replace(/[\\/]+$/, "");
  return after ? { name, asset: after } : { name };
}

/** Parse a `/skill:<name>` invocation from submitted input text. */
export function parseSkillCommand(text: string): { name: string } | undefined {
  const trimmedStart = text.trimStart();
  if (trimmedStart.startsWith("/skill:")) {
    const space = trimmedStart.indexOf(" ");
    const name = (
      space === -1 ? trimmedStart.slice("/skill:".length) : trimmedStart.slice("/skill:".length, space)
    ).toLowerCase();
    return name && !name.includes("/") ? { name } : undefined;
  }
  if (trimmedStart.startsWith("/") || trimmedStart.startsWith("!")) return undefined;
  const match = /(^|\s)\/skill:([^\s/]+)(\s|$)/.exec(text);
  const name = match?.[2]?.toLowerCase();
  return name ? { name } : undefined;
}

export function skillProvider(skill: { source?: string; _source?: { provider?: string } }): string {
  const raw = skill._source?.provider ?? skill.source?.split(":")[0] ?? "unknown";
  return PROVIDERS.has(raw) ? raw : "unknown";
}

export function repoName(cwd: string): string {
  let dir = resolve(cwd);
  for (;;) {
    if (existsSync(join(dir, ".git"))) return basename(dir);
    const parent = dirname(dir);
    if (parent === dir) return "none";
    dir = parent;
  }
}
