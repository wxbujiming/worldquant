import client from "./client";

export function searchOperators() {
  return client.get("/operators");
}
