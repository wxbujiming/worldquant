import client from "./client";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthStatus {
  authenticated: boolean;
  email?: string;
  has_credentials?: boolean;
}

export function login(data: LoginRequest) {
  return client.post("/auth/login", data);
}

export function loginWithEnv() {
  return client.post("/auth/login/env");
}

export function logout() {
  return client.delete("/auth/logout");
}

export function getStatus() {
  return client.get<AuthStatus>("/auth/status");
}

export function getUserProfile() {
  return client.get("/auth/profile");
}

export function getSimulationQuota() {
  return client.get("/auth/simulation-quota");
}
