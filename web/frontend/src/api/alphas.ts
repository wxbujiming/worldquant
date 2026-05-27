import client from "./client";

export interface FilterAlphasParams {
  name?: string;
  status?: string;
  region?: string;
  delay?: number;
  universe?: string;
  instrument_type?: string;
  type?: string;
  language?: string;
  category?: string;
  color?: string;
  tag?: string;
  favorite?: boolean;
  hidden?: boolean;
  sharpe_min?: number;
  sharpe_max?: number;
  returns_min?: number;
  returns_max?: number;
  fitness_min?: number;
  fitness_max?: number;
  drawdown_min?: number;
  drawdown_max?: number;
  turnover_min?: number;
  turnover_max?: number;
  order?: string;
  limit?: number;
  offset?: number;
}

export interface PatchAlphaBody {
  name?: string;
  category?: string;
  color?: string;
  tags?: string[];
  favorite?: boolean;
  hidden?: boolean;
  regular_description?: string;
}

export function filterAlphas(params: FilterAlphasParams) {
  return client.get("/alphas", { params });
}

export function getAlpha(id: string) {
  return client.get(`/alphas/${id}`);
}

export function patchAlpha(id: string, body: PatchAlphaBody) {
  return client.patch(`/alphas/${id}`, body);
}

export function simulateAlpha(id: string) {
  return client.post(`/alphas/${id}/simulate`);
}

export function checkAlpha(id: string) {
  return client.post(`/alphas/${id}/check`);
}

export function submitAlpha(id: string) {
  return client.post(`/alphas/${id}/submit`);
}
