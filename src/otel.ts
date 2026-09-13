import { metrics, type Meter } from "@opentelemetry/api";
import pkg from "../package.json" with { type: "json" };

export const SCOPE = "omp.skill-telemetry";

export function isNoopMeterProvider(): boolean {
  return metrics.getMeterProvider().constructor.name === "NoopMeterProvider";
}

export function getMeter(): Meter {
  return metrics.getMeter(SCOPE, pkg.version);
}
