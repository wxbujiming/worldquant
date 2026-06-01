import client from "./client";

export interface GenConfig {
  region: string;
  delay: number;
  universe: string;
  instrument_type: string;
  neutralization?: string | null;
  truncation?: number | null;
  decay?: number | null;
  pasteurization?: string | null;
}

export interface Stage1Expression {
  id: string;
  formula: string;
  operator: string;
  field: string;
  category: string;
  params: Record<string, string>;
}

export interface Stage2Expression {
  id: string;
  formula: string;
  operator: string;
  category: string;
  composed_from: string[];
}

export interface Stage3Expression {
  id: string;
  formula: string;
  operator: string;
  category: string;
  composed_from: string[];
}

export function generateStage1(body: {
  config: GenConfig;
  dataset_ids: string[];
  count: number;
  seed?: number;
}) {
  return client.post("/generator/stage1", body);
}

export function generateStage2(body: {
  input_expressions: Stage1Expression[];
  count: number;
  seed?: number;
}) {
  return client.post("/generator/stage2", body);
}

export function generateStage3(body: {
  input_expressions: Stage2Expression[];
  count: number;
  seed?: number;
}) {
  return client.post("/generator/stage3", body);
}

export function simulateFormula(formula: string, config: GenConfig) {
  const alpha: Record<string, any> = {
    type: "REGULAR",
    settings: {
      instrumentType: config.instrument_type,
      region: config.region,
      universe: config.universe,
      delay: config.delay,
      neutralization: config.neutralization ?? "SUBINDUSTRY",
      unitHandling: "VERIFY",
      nanHandling: "ON",
      language: "FASTEXPR",
      visualization: false,
    },
    regular: formula,
  };
  if (config.decay != null) alpha.settings.decay = config.decay;
  if (config.truncation != null) alpha.settings.truncation = config.truncation;
  if (config.pasteurization != null) alpha.settings.pasteurization = config.pasteurization;
  return client.post("/simulate", { alpha });
}
