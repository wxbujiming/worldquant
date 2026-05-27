import client from "./client";

export function getCacheStats() {
  return client.get("/cache/stats");
}

export function syncOperators() {
  return client.post("/cache/sync/operators");
}

export function syncDatasets() {
  return client.post("/cache/sync/datasets");
}

export function syncFields(
  region = "usa",
  delay = 1,
  universe = "top3000",
  dataset_id?: string
) {
  return client.post("/cache/sync/fields", null, {
    params: { region, delay, universe, dataset_id },
  });
}

export function getCachedOperators() {
  return client.get("/cache/operators");
}

export function getCachedDatasets(params?: {
  region?: string;
  delay?: number;
  universe?: string;
}) {
  return client.get("/cache/datasets", { params });
}

export function getCachedFields(dataset_id?: string) {
  return client.get("/cache/fields", { params: { dataset_id } });
}

export function updateOperatorRemarks(opId: string, remarks: string) {
  return client.patch(`/cache/operators/${encodeURIComponent(opId)}/remarks`, { remarks });
}

export function syncAlphas() {
  return client.post("/cache/sync/alphas");
}

export function getCachedAlphas() {
  return client.get("/cache/alphas");
}
