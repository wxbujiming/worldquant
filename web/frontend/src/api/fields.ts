import client from "./client";

export interface SearchFieldsParams {
  region: string;
  delay: number;
  universe: string;
  instrument_type?: string;
  dataset_id?: string;
  search?: string;
  category?: string;
  type?: string;
  coverage_min?: number;
  coverage_max?: number;
  order?: string;
  limit?: number;
  offset?: number;
}

export function searchFields(params: SearchFieldsParams) {
  return client.get("/fields", { params });
}

export function getField(id: string) {
  return client.get(`/fields/${id}`);
}
