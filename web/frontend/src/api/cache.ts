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

export function syncFields(dataset_id?: string) {
  return client.post("/cache/sync/fields", null, {
    params: { dataset_id },
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

export function getCachedDatasetKinds() {
  return client.get("/cache/dataset-kinds");
}

export function getCachedFields(dataset_id?: string) {
  return client.get("/cache/fields", { params: { dataset_id } });
}

export function updateOperatorRemarks(opId: string, remarks: string) {
  return client.patch(`/cache/operators/${encodeURIComponent(opId)}/remarks`, { remarks });
}

export function syncAlphas(sync_date_from?: string, sync_date_to?: string) {
  const params: Record<string, string> = {};
  if (sync_date_from) params.sync_date_from = sync_date_from;
  if (sync_date_to) params.sync_date_to = sync_date_to;
  return client.post("/cache/sync/alphas", null, { params });
}

export function getCachedAlphas() {
  return client.get("/cache/alphas");
}
