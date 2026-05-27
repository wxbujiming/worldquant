import client from "./client";

export function getCacheStats() {
  return client.get("/cache/stats");
}

export function syncOperators() {
  return client.post("/cache/sync/operators");
}

export function syncDatasets(region = "usa", delay = 1, universe = "top3000") {
  return client.post("/cache/sync/datasets", null, {
    params: { region, delay, universe },
  });
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
