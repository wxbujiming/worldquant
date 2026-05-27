import axios from "axios";
import type { AxiosInstance } from "axios";

const client: AxiosInstance = axios.create({
  baseURL: "/api",
  timeout: 120000,
  headers: { "Content-Type": "application/json" },
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.location.hash = "#/login";
    }
    return Promise.reject(error);
  }
);

export default client;
