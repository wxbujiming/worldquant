import client from "./client";

export interface SearchDatasetsParams {
  region: string;
  delay: number;
  universe: string;
  instrument_type?: string;
  search?: string;
  category?: string;
  theme?: boolean;
  coverage_min?: number;
  coverage_max?: number;
  order?: string;
  limit?: number;
  offset?: number;
}

export function searchDatasets(params: SearchDatasetsParams) {
  return client.get("/datasets", { params });
}

export function getDataset(id: string) {
  return client.get(`/datasets/${id}`);
}
