import assert from "node:assert/strict";
import { describe, test } from "node:test";
import { parseSkillCommand, parseSkillUrl } from "../src/skills.ts";

describe("parseSkillUrl", () => {
  test("bare name", () => {
    assert.deepEqual(parseSkillUrl("skill://telemetry-probe"), { name: "telemetry-probe" });
  });

  test("name plus asset", () => {
    assert.deepEqual(parseSkillUrl("skill://telemetry-probe/assets/example.txt"), {
      name: "telemetry-probe",
      asset: "assets/example.txt",
    });
  });

  test("URL-encoded path", () => {
    assert.deepEqual(parseSkillUrl("skill://telemetry-probe/foo%2Fbar.txt"), {
      name: "telemetry-probe",
      asset: "foo/bar.txt",
    });
  });

  test("rejected traversal", () => {
    assert.equal(parseSkillUrl("skill://telemetry-probe/../secret"), undefined);
    assert.equal(parseSkillUrl("skill://telemetry-probe/%2e%2e/secret"), undefined);
  });

  test("trailing slash is a body read", () => {
    assert.deepEqual(parseSkillUrl("skill://telemetry-probe/"), { name: "telemetry-probe" });
  });

  test("uppercase name", () => {
    assert.deepEqual(parseSkillUrl("skill://Telemetry-Probe"), { name: "telemetry-probe" });
  });
});

describe("parseSkillCommand", () => {
  test("leading slash command", () => {
    assert.deepEqual(parseSkillCommand("/skill:telemetry-probe some args"), { name: "telemetry-probe" });
  });
});
